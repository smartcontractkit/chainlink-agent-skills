#!/usr/bin/env python3
"""Grade description-only skill routing.

The discovery prompt comes from `skills-ref to-prompt`. It may contain
name, description, and location only. This script does not parse SKILL.md
frontmatter itself.
"""

from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
CASES_PATH = Path(__file__).resolve().parent / "cases.yaml"
FIXTURES = Path(__file__).resolve().parent / "fixtures"
MIN_BODY_LINE = 48

# Hand-off names that must sit in the first 300 characters.
HANDOFFS = {
    "chainlink-cre-skill": [
        "chainlink-cre-connect-skill",
        "chainlink-confidential-ai-attester-skill",
    ],
    "chainlink-cre-connect-skill": ["chainlink-cre-skill"],
    "chainlink-confidential-ai-attester-skill": ["chainlink-cre-skill"],
    "chainlink-nop-skill": ["chainlink-ccip-skill", "chainlink-cre-skill"],
    "chainlink-ccip-skill": ["chainlink-nop-skill", "chainlink-ace-skill"],
    "chainlink-data-feeds-skill": ["chainlink-data-streams-skill"],
    "chainlink-data-streams-skill": ["chainlink-data-feeds-skill"],
    "chainlink-ace-skill": ["chainlink-ccip-skill"],
}

FORBIDDEN = {
    "chainlink-cre-skill": ["automation with Chainlink"],
    "chainlink-data-feeds-skill": ["oracle data"],
}


def skill_dirs() -> list[Path]:
    dirs = sorted(path for path in REPO.glob("chainlink-*-skill") if path.is_dir())
    if len(dirs) != 9:
        raise SystemExit(f"expected 9 skill directories, found {len(dirs)}")
    return dirs


def parse_cases(text: str) -> list[dict]:
    cases: list[dict] = []
    current: dict | None = None
    mode: str | None = None
    for raw in text.splitlines():
        line = raw.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if line.startswith("- id:"):
            current = {
                "id": line.split(":", 1)[1].strip(),
                "prompt": "",
                "expect": [],
                "reject": [],
            }
            cases.append(current)
            mode = None
            continue
        if current is None:
            raise SystemExit(f"cases.yaml has content before the first case: {line}")
        if line.startswith("  prompt:"):
            value = line.split(":", 1)[1].strip()
            if len(value) >= 2 and value[0] == value[-1] and value[0] in "\"'":
                value = value[1:-1]
            current["prompt"] = value
            mode = None
            continue
        if line.startswith("  expect:"):
            mode = "expect"
            continue
        if line.startswith("  reject:"):
            mode = "reject"
            tail = line.split(":", 1)[1].strip()
            if tail == "[]":
                mode = None
            continue
        if line.strip().startswith("- ") and mode in {"expect", "reject"}:
            current[mode].append(line.strip()[2:].strip())
            continue
        raise SystemExit(f"cannot read cases.yaml line: {line}")
    if len(cases) != 10:
        raise SystemExit(f"expected 10 cases, found {len(cases)}")
    return cases


def load_cases() -> list[dict]:
    return parse_cases(CASES_PATH.read_text())


def discovery_prompt() -> str:
    command = ["skills-ref", "to-prompt", *map(str, skill_dirs())]
    try:
        result = subprocess.run(command, check=False, capture_output=True, text=True)
    except FileNotFoundError:
        raise SystemExit(
            "skills-ref is not on PATH. Install it with:\n"
            "python3 -m venv /tmp/skills-ref-venv\n"
            '/tmp/skills-ref-venv/bin/pip install "skills-ref @ git+https://github.com/agentskills/agentskills.git#subdirectory=skills-ref"\n'
            'PATH="/tmp/skills-ref-venv/bin:$PATH" python3 evals/skill-routing/check.py self-test'
        )
    if result.returncode != 0:
        raise SystemExit(result.stderr.strip() or "skills-ref to-prompt failed")
    return result.stdout


def frontmatter_and_body(text: str) -> str:
    if not text.startswith("---"):
        raise SystemExit("SKILL.md is missing frontmatter")
    parts = text.split("---", 2)
    if len(parts) < 3:
        raise SystemExit("SKILL.md frontmatter is not closed")
    return parts[2]


def description_of(skill_dir: Path) -> str:
    # Read the description from the skills-ref prompt, not a second parser.
    prompt = discovery_prompt()
    name = skill_dir.name
    match = re.search(
        rf"<name>\s*{re.escape(name)}\s*</name>\s*<description>\s*(.*?)\s*</description>",
        prompt,
        re.DOTALL,
    )
    if not match:
        raise SystemExit(f"discovery prompt has no description for {name}")
    return match.group(1)


def leak_errors(prompt: str) -> list[str]:
    errors = []
    # The location element always names SKILL.md. A heading is a markdown line.
    for skill_dir in skill_dirs():
        body = frontmatter_and_body((skill_dir / "SKILL.md").read_text())
        for raw in body.splitlines():
            line = raw.strip()
            if not line:
                continue
            if line.startswith("#") or len(line) >= MIN_BODY_LINE:
                if line in prompt:
                    errors.append(f"{skill_dir.name} body line is in the prompt: {line[:80]}")
        for path in skill_dir.rglob("*.md"):
            if path.name == "SKILL.md":
                continue
            for raw in path.read_text(errors="replace").splitlines():
                line = raw.strip()
                if line.startswith("#") and line in prompt:
                    errors.append(f"{path.relative_to(REPO)} heading is in the prompt: {line}")
    return errors


def handoff_errors() -> list[str]:
    errors = []
    for skill_dir in skill_dirs():
        if skill_dir.name not in HANDOFFS and skill_dir.name not in FORBIDDEN:
            continue
        description = description_of(skill_dir)
        if len(description) > 1024:
            errors.append(f"{skill_dir.name} description is {len(description)} characters")
        head = description[:300]
        for name in HANDOFFS.get(skill_dir.name, []):
            if name not in head:
                errors.append(f"{skill_dir.name} hand-off {name} is outside the first 300 characters")
        for phrase in FORBIDDEN.get(skill_dir.name, []):
            if phrase in description:
                errors.append(f"{skill_dir.name} still contains {phrase!r}")
    return errors


def mentioned(reply: str, name: str) -> bool:
    return re.search(rf"(?<![A-Za-z0-9-]){re.escape(name)}(?![A-Za-z0-9-])", reply) is not None


def grade(case: dict, reply: str) -> list[str]:
    errors = []
    for name in case["expect"]:
        if not mentioned(reply, name):
            errors.append(f"missing {name}")
    for name in case["reject"]:
        if mentioned(reply, name):
            errors.append(f"rejected name present: {name}")
    return errors


def require_case(cases: list[dict], case_id: str) -> dict:
    for case in cases:
        if case["id"] == case_id:
            return case
    raise SystemExit(f"unknown case {case_id}")


def self_test() -> int:
    prompt = discovery_prompt()
    errors = leak_errors(prompt)
    errors.extend(handoff_errors())
    cases = load_cases()
    fixture_pairs = [
        ("cre-enclave-no-document", True),
        ("cre-enclave-no-document", False),
        ("ace-on-ccip-pool", True),
        ("ace-on-ccip-pool", False),
    ]
    for case_id, should_pass in fixture_pairs:
        kind = "accept" if should_pass else "reject"
        reply = (FIXTURES / kind / f"{case_id}.txt").read_text()
        found = grade(require_case(cases, case_id), reply)
        if should_pass and found:
            errors.append(f"accept fixture {case_id} failed: {', '.join(found)}")
        if not should_pass and not found:
            errors.append(f"reject fixture {case_id} was accepted")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("self-test passed")
    print("discovery prompt has name, description, and location only")
    print("accept fixtures passed and reject fixtures failed")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("self-test")
    sub.add_parser("prompt")
    grade_parser = sub.add_parser("grade")
    grade_parser.add_argument("--case", required=True)
    grade_parser.add_argument("--reply-file", required=True, type=Path)
    args = parser.parse_args()

    if args.command == "self-test":
        return self_test()
    if args.command == "prompt":
        prompt = discovery_prompt()
        errors = leak_errors(prompt)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        sys.stdout.write(prompt)
        if not prompt.endswith("\n"):
            sys.stdout.write("\n")
        return 0
    case = require_case(load_cases(), args.case)
    reply = args.reply_file.read_text()
    errors = grade(case, reply)
    if errors:
        print(f"{case['id']} failed: {', '.join(errors)}", file=sys.stderr)
        return 1
    print(f"{case['id']} passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
