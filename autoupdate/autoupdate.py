#!/usr/bin/env python3
"""
autoupdate.py — Detect changed Chainlink docs pages and regenerate skill reference descriptions.

Scans every docs.chain.link URL embedded in reference files across all skills,
fetches each page, checksums the stable content, and regenerates descriptions
for pages that changed since the last run.

Usage:
    python autoupdate/autoupdate.py [--force] [--dry-run] [--checksums-only] [--skill NAME] [--concurrency N]

Environment variables:
    OPENAI_API_KEY      Required for LLM regeneration (set to "ollama" for local)
    OPENAI_BASE_URL     API base URL (default: https://api.openai.com/v1)
    OPENAI_MODEL        Model name (default: gpt-4o-mini)

Exit code is always 0. Check `git diff` after running to detect changes.
"""

from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

import httpx
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from openai import AsyncOpenAI

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────────
REPO_ROOT = Path(__file__).resolve().parent.parent
AUTOUPDATE_DIR = Path(__file__).resolve().parent
STATE_FILE = AUTOUPDATE_DIR / "state.json"

# ── Settings ───────────────────────────────────────────────────────────────────
DOCS_DOMAIN = "https://docs.chain.link"
MAX_PAGE_CHARS = 14_000   # Characters of page content sent to LLM
FETCH_CONCURRENCY = 10
LLM_CONCURRENCY = 5
UA = "Mozilla/5.0 AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"


# ── State ──────────────────────────────────────────────────────────────────────

def load_state() -> dict:
    if STATE_FILE.exists():
        try:
            return json.loads(STATE_FILE.read_text())
        except Exception:
            pass
    return {"checksums": {}}


def save_state(state: dict) -> None:
    STATE_FILE.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")


# ── Skill + reference discovery ────────────────────────────────────────────────

def find_skills(skill_filter: Optional[str]) -> list[Path]:
    skills = sorted(
        d for d in REPO_ROOT.iterdir()
        if d.is_dir() and (d / "SKILL.md").exists()
    )
    if skill_filter:
        skills = [s for s in skills if s.name == skill_filter]
    return skills


def find_reference_files(skill_dir: Path) -> list[Path]:
    ref_dir = skill_dir / "references"
    return sorted(ref_dir.glob("*.md")) if ref_dir.exists() else []


# ── Entry parsing ──────────────────────────────────────────────────────────────
#
# Reference files use two entry styles:
#
#   1. Description entries (CRE, Data Feeds style) — URL + em-dash + description:
#        - [https://docs.chain.link/foo](https://docs.chain.link/foo) — Some description...
#        - https://docs.chain.link/foo — Some description...
#      These have `desc` set and are eligible for LLM regeneration when changed.
#
#   2. Reference-only entries (CCIP style) — URL inline, no description:
#        - `https://docs.chain.link/ccip`
#        - Overview: `https://docs.chain.link/ccip/concepts`
#      These have `desc=None`. Checksums are tracked but no file update is made.

EM = " \u2014 "   # em dash with surrounding spaces


def extract_entries(ref_file: Path) -> list[dict]:
    """Return all docs.chain.link entries found in a reference file."""
    entries = []
    seen: set[str] = set()

    for line in ref_file.read_text().splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue

        # Find the first docs.chain.link URL on this line (any format)
        match = re.search(r"https?://docs\.chain\.link[^\s\)\]`\"']*", stripped)
        if not match:
            continue

        url = match.group(0).rstrip(")")
        if url in seen:
            continue
        seen.add(url)

        desc: Optional[str] = stripped[stripped.index(EM) + len(EM):] if EM in stripped else None

        entries.append({"url": url, "desc": desc, "line": line, "file": ref_file})

    return entries


# ── Fetch + checksum ───────────────────────────────────────────────────────────

def normalize_html(html: str) -> str:
    """Strip dynamic HTML noise to produce stable, checksum-able text."""
    soup = BeautifulSoup(html, "html.parser")
    for tag in soup(["script", "style", "noscript", "nav", "footer", "header"]):
        tag.decompose()
    for tag in soup.find_all(True):
        for attr in list(tag.attrs):
            if attr.startswith("data-") or attr in ("onclick", "onload", "onerror"):
                del tag.attrs[attr]
    return soup.get_text(separator="\n", strip=True)


def compute_checksum(text: str) -> str:
    normalized = " ".join(text.lower().split())
    return hashlib.sha256(normalized.encode()).hexdigest()


async def fetch_page(
    client: httpx.AsyncClient,
    sem: asyncio.Semaphore,
    url: str,
) -> Optional[tuple[str, str]]:
    """Fetch URL and return (page_text, checksum), or None on failure."""
    async with sem:
        try:
            resp = await client.get(url, timeout=30, follow_redirects=True)
            resp.raise_for_status()
            text = normalize_html(resp.text)[:MAX_PAGE_CHARS]
            return text, compute_checksum(text)
        except Exception as exc:
            print(f"  [warn] fetch failed: {url} — {exc}", file=sys.stderr)
            return None


# ── LLM re-summarization ───────────────────────────────────────────────────────

SYSTEM_PROMPT = """\
You update reference entries for Chainlink developer skill documentation.
Each entry is a single-line description of a docs.chain.link page, written so an LLM agent \
can quickly decide whether to fetch that page.

Style rules (follow exactly):
- Single paragraph, no line breaks or markdown formatting
- Opens with a concise high-level sentence describing what the page covers
- Covers integration patterns, interfaces, key methods, parameters, return types, configuration
- Calls out caveats, deprecations, and production warnings
- Ends with "Key details:" followed by semicolon-separated technical facts
- Target 120-250 words. Dense but no padding.\
"""

REGEN_PROMPT = """\
The documentation page at {url} has changed. Regenerate its reference entry description.

Current description (match this style and level of detail):
{current}

Updated page content:
{content}

Write only the new description — no URL, no leading dash, no markdown.\
"""


async def regenerate_description(
    sem: asyncio.Semaphore,
    client: AsyncOpenAI,
    model: str,
    url: str,
    current_desc: str,
    page_text: str,
) -> Optional[str]:
    async with sem:
        try:
            resp = await client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": REGEN_PROMPT.format(
                        url=url,
                        current=current_desc,
                        content=page_text[:8_000],
                    )},
                ],
                temperature=0.2,
                max_tokens=600,
            )
            return resp.choices[0].message.content.strip()
        except Exception as exc:
            print(f"  [warn] LLM failed: {url} — {exc}", file=sys.stderr)
            return None


# ── Reference file update ──────────────────────────────────────────────────────

def update_entry(ref_file: Path, old_line: str, new_desc: str) -> bool:
    """Replace a reference entry's description in-place. Returns True if changed."""
    content = ref_file.read_text()
    if EM not in old_line:
        return False
    prefix = old_line[:old_line.index(EM)]
    new_line = f"{prefix}{EM}{new_desc}"
    if new_line == old_line:
        return False
    new_content = content.replace(old_line, new_line, 1)
    if new_content == content:
        return False
    ref_file.write_text(new_content)
    return True


# ── Orchestration ──────────────────────────────────────────────────────────────

async def run(
    force: bool,
    dry_run: bool,
    checksums_only: bool,
    skill_filter: Optional[str],
    concurrency: int,
) -> dict:
    """Run the autoupdate loop. Returns a summary dict."""
    state = load_state()
    stored_checksums = state.get("checksums", {})

    skills = find_skills(skill_filter)
    if not skills:
        print("No skills found.", file=sys.stderr)
        return {"scanned": 0, "changed": 0, "updated": 0}

    # Collect all docs.chain.link URLs across all skills
    # url -> list of entry dicts (same URL can appear in multiple skills/files)
    url_entries: dict[str, list[dict]] = {}
    for skill in skills:
        skill_count = 0
        for ref_file in find_reference_files(skill):
            for entry in extract_entries(ref_file):
                url_entries.setdefault(entry["url"], []).append(entry)
                skill_count += 1
        if skill_count:
            print(f"  {skill.name}: {skill_count} URL(s)")
        else:
            print(f"  {skill.name}: 0 URLs (no docs.chain.link entries found)")

    all_urls = list(url_entries)
    print(f"Total: {len(all_urls)} docs.chain.link URL(s) across {len(skills)} skill(s) checked.")

    # Fetch all pages concurrently
    fetch_sem = asyncio.Semaphore(min(concurrency, FETCH_CONCURRENCY))
    async with httpx.AsyncClient(headers={"User-Agent": UA}) as http:
        tasks = [fetch_page(http, fetch_sem, url) for url in all_urls]
        raw_results = await asyncio.gather(*tasks)

    fetched: dict[str, tuple[str, str]] = {
        url: result
        for url, result in zip(all_urls, raw_results)
        if result is not None
    }

    # --checksums-only: snapshot current state without touching any markdown files
    if checksums_only:
        for url, (_, cs) in fetched.items():
            stored_checksums[url] = cs
        state["checksums"] = stored_checksums
        state["last_run"] = datetime.now(timezone.utc).isoformat()
        save_state(state)
        print(f"Saved {len(fetched)} checksum(s) to state.json. No files updated.")
        return {"scanned": len(all_urls), "changed": 0, "updated": 0}

    # Determine which pages changed
    changed_urls = [
        url for url in fetched
        if force or stored_checksums.get(url) != fetched[url][1]
    ]
    print(f"{len(changed_urls)} page(s) changed (of {len(fetched)} successfully fetched).")

    if not changed_urls:
        return {"scanned": len(all_urls), "changed": 0, "updated": 0}

    if dry_run:
        print("\nChanged pages (dry-run, no files written):")
        for url in changed_urls:
            entries = url_entries[url]
            has_desc = any(e["desc"] is not None for e in entries)
            tag = "" if has_desc else " [checksum-only, no description to update]"
            for entry in entries:
                rel = entry["file"].relative_to(REPO_ROOT)
                print(f"  {url}{tag}\n    -> {rel}")
        return {"scanned": len(all_urls), "changed": len(changed_urls), "updated": 0}

    # Set up LLM client
    api_key = os.environ.get("OPENAI_API_KEY", "")
    if not api_key:
        print("OPENAI_API_KEY not set — skipping LLM regeneration.", file=sys.stderr)
        return {"scanned": len(all_urls), "changed": len(changed_urls), "updated": 0}

    base_url = os.environ.get("OPENAI_BASE_URL", "https://api.openai.com/v1")
    model = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
    llm = AsyncOpenAI(api_key=api_key, base_url=base_url)
    llm_sem = asyncio.Semaphore(LLM_CONCURRENCY)

    # Regenerate descriptions for changed pages
    updated_files: list[str] = []
    for url in changed_urls:
        entries = url_entries[url]
        page_text, new_checksum = fetched[url]

        # Entries with desc=None have no description to update — just track the checksum
        updatable = [e for e in entries if e["desc"] is not None]
        if not updatable:
            print(f"  Checksum updated (no description): {url}")
            stored_checksums[url] = new_checksum
            continue

        print(f"\n  Updating: {url}")
        new_desc = await regenerate_description(
            llm_sem, llm, model, url, updatable[0]["desc"], page_text
        )
        if not new_desc:
            print(f"    [skip] LLM returned empty result")
            continue

        for entry in updatable:
            if update_entry(entry["file"], entry["line"], new_desc):
                rel = str(entry["file"].relative_to(REPO_ROOT))
                print(f"    -> {rel}")
                updated_files.append(rel)

        # Only persist checksum after a successful update
        stored_checksums[url] = new_checksum

    # Save updated state
    state["checksums"] = stored_checksums
    state["last_run"] = datetime.now(timezone.utc).isoformat()
    save_state(state)

    return {
        "scanned": len(all_urls),
        "changed": len(changed_urls),
        "updated": len(updated_files),
        "files": sorted(set(updated_files)),
    }


def main() -> None:
    ap = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    ap.add_argument("--force", action="store_true",
                    help="Regenerate all descriptions, ignoring stored checksums")
    ap.add_argument("--dry-run", action="store_true",
                    help="Detect changes and print them, but write nothing")
    ap.add_argument("--checksums-only", action="store_true",
                    help="Fetch all pages, save checksums to state.json, skip LLM and file updates")
    ap.add_argument("--skill", metavar="NAME",
                    help="Limit to one skill (e.g. chainlink-data-feeds-skill)")
    ap.add_argument("--concurrency", type=int, default=10, metavar="N",
                    help="Max concurrent page fetches (default: 10)")
    args = ap.parse_args()

    summary = asyncio.run(run(args.force, args.dry_run, args.checksums_only, args.skill, args.concurrency))

    prefix = "[dry-run] " if args.dry_run else ""
    print(f"\n{prefix}Done: {summary['updated']} reference(s) updated "
          f"({summary['changed']} page(s) changed, {summary['scanned']} scanned).")


if __name__ == "__main__":
    main()
