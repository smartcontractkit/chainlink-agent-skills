# Autoupdate

Weekly automation that detects changed Chainlink documentation pages and regenerates
affected reference file descriptions using an LLM.

## How it works

1. **Discovers** every `docs.chain.link` URL embedded in `references/*.md` files across all skills
2. **Fetches** each page and computes a checksum of its normalized text content
3. **Compares** checksums to the last known state (`state.json`)
4. **Regenerates** descriptions for pages that changed, using the existing description as a style guide
5. **Saves** updated checksums to `state.json`

The GitHub Action runs weekly, commits any changes to a branch, and opens a PR for human review.

## GitHub Action

Runs automatically every Monday at 07:00 UTC via `.github/workflows/autoupdate.yml`.

**Manual dispatch inputs:**
- `force` — Regenerate all descriptions regardless of checksums
- `skill` — Limit to one skill (e.g. `chainlink-cre-skill`)
- `dry_run` — Detect and print changes without writing files

**Required secrets:**
- `OPENAI_API_KEY` — API key for the LLM (GPT-4o-mini by default)
- `OPENAI_BASE_URL` — Optional; override for Ollama or other OpenAI-compatible endpoints

**Optional variable:**
- `AUTOUPDATE_MODEL` — Model name (default: `gpt-4o-mini`). Set as a repository variable.

## Running locally

```bash
cd chainlink-agent-skills

# Install deps
pip install -r autoupdate/requirements.txt

# Detect changes (no writes)
OPENAI_API_KEY=your-key python autoupdate/autoupdate.py --dry-run

# Update one skill
OPENAI_API_KEY=your-key python autoupdate/autoupdate.py --skill chainlink-cre-skill

# Force-regenerate everything
OPENAI_API_KEY=your-key python autoupdate/autoupdate.py --force

# Use Ollama locally (no API key cost)
OPENAI_API_KEY=ollama OPENAI_BASE_URL=http://localhost:11434/v1 OPENAI_MODEL=llama3.2 \
    python autoupdate/autoupdate.py
```

## State file

`state.json` tracks the URL → checksum mapping. It is committed to the repo as part of each
autoupdate PR so the next weekly run inherits the latest checksums after merging.

If `state.json` is empty (fresh install), the first run will re-check all pages and
regenerate all descriptions. This is expected and correct; subsequent runs are incremental.

## Migrating checksums from the generator repo

To avoid regenerating all descriptions on the first run, import existing checksums
from `chainlink-skills-generator/`:

```python
# Run once from repo root
import json
from pathlib import Path

state = {"checksums": {}}

for cache_file in [
    Path("/Users/thomas/chainlink-skills-generator/cre-checksums.json"),
    Path("/Users/thomas/chainlink-skills-generator/data-feeds-checksums.json"),
]:
    if cache_file.exists():
        data = json.loads(cache_file.read_text())
        for url, entry in data.items():
            if "checksum" in entry:
                state["checksums"][url] = entry["checksum"]

Path("autoupdate/state.json").write_text(json.dumps(state, indent=2, sort_keys=True) + "\n")
print(f"Imported {len(state['checksums'])} checksums")
```

## Which skills are supported

Autoupdate works with reference files that follow the `- [URL](URL) — description` format
used by the CRE and Data Feeds skills. Skills with a different reference format (e.g. CCIP's
plain URL lists) are automatically skipped — no configuration needed.

New skills added to the repo are picked up automatically on the next weekly run.
