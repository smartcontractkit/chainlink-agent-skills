#!/usr/bin/env bash
set -uo pipefail

# Validate every http(s) URL referenced in skill markdown files.
#
# Usage:
#   .github/scripts/check-urls.sh                 # scan all *-skill/ dirs
#   .github/scripts/check-urls.sh chainlink-cre-skill
#   .github/scripts/check-urls.sh path/to/file.md another-dir
#
# Run from the repo root, in a normal shell with internet access. A full scan
# of all skills takes ~30-60s; scope to one skill (faster) while iterating.
#
# Env:
#   PARALLEL   number of concurrent checks (default 8)
#   TIMEOUT    per-request timeout in seconds (default 10)
#   GITHUB_ANNOTATIONS=1   emit ::error annotations (auto-on in CI)

# Keep concurrency moderate: bursting too many requests at docs.chain.link
# trips its rate limiter, which makes everything slower, not faster.
PARALLEL="${PARALLEL:-8}"
TIMEOUT="${TIMEOUT:-10}"
[ -n "${CI:-}" ] && GITHUB_ANNOTATIONS="${GITHUB_ANNOTATIONS:-1}"
GITHUB_ANNOTATIONS="${GITHUB_ANNOTATIONS:-0}"

# Reachability-only allowlist: API/RPC/WebSocket endpoints that don't serve a
# browseable page (a GET returns 404/403 even when the host is fine). For these
# we accept any HTTP response and only fail on a connection error (code 000).
script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
endpoints_file="$script_dir/../url-check-endpoints.txt"
ENDPOINT_PATTERNS=""
if [ -f "$endpoints_file" ]; then
  ENDPOINT_PATTERNS="$(grep -vE '^[[:space:]]*(#|$)' "$endpoints_file" || true)"
fi
export ENDPOINT_PATTERNS

# Colors (disabled when not a TTY)
if [ -t 1 ]; then
  BOLD=$'\033[1m'; RED=$'\033[31m'; GREEN=$'\033[32m'; YELLOW=$'\033[33m'
  DIM=$'\033[2m'; RESET=$'\033[0m'
else
  BOLD=""; RED=""; GREEN=""; YELLOW=""; DIM=""; RESET=""
fi

# Resolve scan targets: args, or every *-skill directory at repo root.
targets=("$@")
if [ ${#targets[@]} -eq 0 ]; then
  while IFS= read -r d; do targets+=("$d"); done < <(find . -maxdepth 1 -type d -name '*-skill' | sort)
fi

if [ ${#targets[@]} -eq 0 ]; then
  echo "No skill directories found and no paths given." >&2
  exit 1
fi

# Collect markdown files.
md_files=()
for t in "${targets[@]}"; do
  if [ -f "$t" ]; then
    md_files+=("$t")
  elif [ -d "$t" ]; then
    # Skip vendored/third-party trees — we only validate our own docs.
    while IFS= read -r f; do md_files+=("$f"); done < <(
      find "$t" \( -name node_modules -o -name .git \) -prune -o -type f -name '*.md' -print
    )
  else
    echo "${YELLOW}warning:${RESET} skipping '$t' (not a file or directory)" >&2
  fi
done

if [ ${#md_files[@]} -eq 0 ]; then
  echo "No markdown files to scan." >&2
  exit 0
fi

work_dir="$(mktemp -d)"
trap 'rm -rf "$work_dir"' EXIT
locations="$work_dir/locations"   # url<TAB>file:line
: > "$locations"

# Extract URLs with file:line. Strip trailing markdown/punctuation noise and
# skip obvious non-checkable placeholders.
for f in "${md_files[@]}"; do
  grep -noE 'https?://[^][:space:]()<>"`'"'"'\\]+' "$f" 2>/dev/null \
  | while IFS=: read -r lineno url; do
      # Trim trailing punctuation that commonly clings to URLs in prose.
      url="${url%%[.,;:]}"
      case "$url" in
        *localhost*|*127.0.0.1*|*example.com*|*YOUR_*|*'{'*|*'$'*) continue ;;
      esac
      printf '%s\t%s:%s\n' "$url" "$f" "$lineno" >> "$locations"
    done
done

# Unique URL list.
urls=()
while IFS= read -r u; do urls+=("$u"); done < <(cut -f1 "$locations" | sort -u)
total=${#urls[@]}

if [ "$total" -eq 0 ]; then
  echo "No checkable URLs found."
  exit 0
fi

echo "${BOLD}Checking $total unique URL(s) across ${#md_files[@]} file(s)...${RESET}"
echo

# Check one URL: print "<status>\t<http_code>\t<url>".
# status = OK (2xx/3xx) | WARN (exists but auth/method/rate-limited) | BROKEN.
check_url() {
  local url="$1" code
  code=$(curl -A "url-checker (chainlink-agent-skills)" \
              -sS -o /dev/null -L --max-time "$TIMEOUT" --retry 1 \
              -w '%{http_code}' "$url" 2>/dev/null)
  code="${code:-000}"

  # Reachability-only endpoints: the server answering at all (any non-000 code)
  # proves the host is alive; only a connection failure is a real break.
  if [ -n "${ENDPOINT_PATTERNS:-}" ]; then
    while IFS= read -r pat; do
      [ -z "$pat" ] && continue
      case "$url" in
        *"$pat"*)
          if [ "$code" = "000" ]; then
            printf 'BROKEN\t%s\t%s\n' "$code" "$url"
          else
            printf 'OK\t%s\t%s\n' "$code" "$url"
          fi
          return ;;
      esac
    done <<< "$ENDPOINT_PATTERNS"
  fi

  if [ "$code" -ge 200 ] 2>/dev/null && [ "$code" -lt 400 ]; then
    printf 'OK\t%s\t%s\n' "$code" "$url"
  else
    case "$code" in
      # Resource exists but the request was refused (needs POST/auth, or
      # we got rate-limited). Not a dead link — surface as a warning.
      401|403|405|429) printf 'WARN\t%s\t%s\n' "$code" "$url" ;;
      *)               printf 'BROKEN\t%s\t%s\n' "$code" "$url" ;;
    esac
  fi
}
export -f check_url
export TIMEOUT

results="$work_dir/results"
# Stream results as each check finishes so we can show live progress. The
# counter lives in this piped subshell; results land in the file regardless.
printf '%s\n' "${urls[@]}" \
  | xargs -P "$PARALLEL" -I {} bash -c 'check_url "$@"' _ {} \
  | { done=0
      while IFS= read -r line; do
        printf '%s\n' "$line" >> "$results"
        done=$((done + 1))
        printf '\r  checked %d/%d ...' "$done" "$total" >&2
      done
      printf '\r%*s\r' 40 "" >&2; }   # clear the progress line

ok_count=$(grep -c '^OK' "$results" || true)
warn_count=$(grep -c '^WARN' "$results" || true)
broken_count=$(grep -c '^BROKEN' "$results" || true)

echo "${GREEN}✓ $ok_count OK${RESET}    ${YELLOW}! $warn_count warn${RESET}    ${RED}✗ $broken_count broken${RESET}"

# List the locations for a given URL, indented, with optional CI annotations.
print_locations() {
  local url="$1" code="$2" level="$3" label="$4"
  grep -F "$(printf '%s\t' "$url")" "$locations" | cut -f2 | sort -u | while IFS= read -r loc; do
    echo "      ${DIM}↳ $loc${RESET}"
    [ "$GITHUB_ANNOTATIONS" = "1" ] && {
      file="${loc%%:*}"; line="${loc##*:}"
      echo "::${level} file=$file,line=$line::${label} URL ($code): $url"
    }
  done
}

if [ "$warn_count" -gt 0 ]; then
  echo
  echo "${BOLD}${YELLOW}Reachable but refused (auth/method/rate-limit — review, not necessarily broken):${RESET}"
  grep '^WARN' "$results" | sort -t$'\t' -k3 | while IFS=$'\t' read -r _ code url; do
    echo "  ${YELLOW}!${RESET} ${BOLD}$url${RESET} ${DIM}(HTTP ${code})${RESET}"
    print_locations "$url" "$code" "warning" "Refused"
  done
fi

if [ "$broken_count" -gt 0 ]; then
  echo
  echo "${BOLD}${RED}Broken URLs:${RESET}"
  grep '^BROKEN' "$results" | sort -t$'\t' -k3 | while IFS=$'\t' read -r _ code url; do
    echo "  ${RED}✗${RESET} ${BOLD}$url${RESET} ${DIM}(HTTP ${code})${RESET}"
    print_locations "$url" "$code" "error" "Broken"
  done
  echo
  echo "${RED}URL check failed.${RESET}"
  exit 1
fi

echo
echo "${GREEN}All URLs reachable.${RESET}"
