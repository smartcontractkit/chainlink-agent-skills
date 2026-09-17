#!/usr/bin/env bash
set -euo pipefail

BASE_SHA="${BASE_SHA:?BASE_SHA is required}"
HEAD_SHA="${HEAD_SHA:-HEAD}"

extract_version() {
  git show "$1:$2" 2>/dev/null \
    | grep -m1 -oE '^[[:space:]]+version:[[:space:]]*"?[0-9]+\.[0-9]+\.[0-9]+"?' \
    | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' \
    || true
}

extract_cursor_plugin_version() {
  git show "$1:$2" 2>/dev/null \
    | grep -m1 -oE '^[[:space:]]+"version":[[:space:]]*"?[0-9]+\.[0-9]+\.[0-9]+"?' \
    | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' \
    || true
}

file_exists_at() {
  git cat-file -e "$1:$2" 2>/dev/null
}

# A path is dot-only when any component under the skill root starts with "."
# (e.g. .cursor-plugin/plugin.json or .gitignore). Such changes do not require
# a metadata.version bump.
file_is_dot_only() {
  local skill="$1"
  local file="$2"
  local rel="${file#"$skill/"}"
  local part
  IFS='/' read -ra parts <<<"$rel"
  for part in "${parts[@]}"; do
    if [[ "$part" == .* ]]; then
      return 0
    fi
  done
  return 1
}

skill_has_substantive_changes() {
  local skill="$1"
  local file
  while IFS= read -r file; do
    [ -z "$file" ] && continue
    if ! file_is_dot_only "$skill" "$file"; then
      return 0
    fi
  done < <(git diff --name-only "$BASE_SHA" "$HEAD_SHA" -- "$skill/")
  return 1
}

touched_skills=()
changed_skills=()
while IFS= read -r skill; do
  [ -z "$skill" ] && continue
  touched_skills+=("$skill")
  if skill_has_substantive_changes "$skill"; then
    changed_skills+=("$skill")
  else
    echo "$skill: only dot-path changes (e.g. .cursor-plugin); skipping metadata.version bump check."
  fi
done < <(
  git diff --name-only "$BASE_SHA" "$HEAD_SHA" \
    | awk -F/ '/^[a-z][a-z0-9-]*-skill\// { print $1 }' \
    | sort -u
)

if [ ${#touched_skills[@]} -eq 0 ]; then
  echo "No skill directories changed; nothing to check."
  exit 0
fi

echo "Checking Cursor plugin versions for: ${touched_skills[*]}"
echo

failed=0

for skill in "${touched_skills[@]}"; do
  skill_md="$skill/SKILL.md"
  cursor_plugin_json="$skill/.cursor-plugin/plugin.json"

  if ! file_exists_at "$HEAD_SHA" "$skill_md"; then
    echo "$skill: SKILL.md not present at HEAD; treating as deleted skill. Skipping Cursor plugin version check."
    continue
  fi

  skill_version="$(extract_version "$HEAD_SHA" "$skill_md")"
  if [ -z "$skill_version" ]; then
    echo "::error file=$skill_md::$skill: could not parse metadata.version (expected X.Y.Z) at HEAD."
    failed=1
    continue
  fi

  if ! file_exists_at "$HEAD_SHA" "$cursor_plugin_json"; then
    echo "::error file=$cursor_plugin_json::$skill: Cursor plugin manifest is missing at HEAD."
    failed=1
    continue
  fi

  cursor_plugin_version="$(extract_cursor_plugin_version "$HEAD_SHA" "$cursor_plugin_json")"
  if [ -z "$cursor_plugin_version" ]; then
    echo "::error file=$cursor_plugin_json::$skill: could not parse Cursor plugin version (expected X.Y.Z) at HEAD."
    failed=1
    continue
  fi

  if [ "$cursor_plugin_version" != "$skill_version" ]; then
    echo "::error file=$cursor_plugin_json::$skill: Cursor plugin version is $cursor_plugin_version, but SKILL.md metadata.version is $skill_version."
    failed=1
    continue
  fi

  echo "$skill: Cursor plugin version $cursor_plugin_version matches SKILL.md. OK."
done

echo

if [ ${#changed_skills[@]} -eq 0 ]; then
  echo "Skill directories changed, but only dot-path files; no metadata.version bump required."
  echo
  if [ "$failed" -ne 0 ]; then
    echo "Skill version check failed."
  else
    echo "All touched skills have matching Cursor plugin and SKILL.md versions."
  fi
  exit "$failed"
fi

echo "Checking version bumps for: ${changed_skills[*]}"
echo

for skill in "${changed_skills[@]}"; do
  skill_md="$skill/SKILL.md"

  if ! file_exists_at "$HEAD_SHA" "$skill_md"; then
    echo "$skill: SKILL.md not present at HEAD; treating as deleted skill. Skipping."
    continue
  fi

  head_version="$(extract_version "$HEAD_SHA" "$skill_md")"
  if [ -z "$head_version" ]; then
    echo "::error file=$skill_md::$skill: could not parse metadata.version (expected X.Y.Z) at HEAD."
    failed=1
    continue
  fi

  if ! file_exists_at "$BASE_SHA" "$skill_md"; then
    echo "$skill: new skill at $head_version. OK."
    continue
  fi

  base_version="$(extract_version "$BASE_SHA" "$skill_md")"
  if [ -z "$base_version" ]; then
    echo "$skill: base SKILL.md has no parseable version; treating HEAD ($head_version) as a bump. OK."
    continue
  fi

  IFS='.' read -r M m p <<<"$base_version"
  next_patch="$M.$m.$((p + 1))"
  next_minor="$M.$((m + 1)).0"
  next_major="$((M + 1)).0.0"

  if [ "$head_version" = "$base_version" ]; then
    echo "::error file=$skill_md::$skill: files changed but metadata.version is still $head_version. Bump it to $next_patch (or $next_minor / $next_major)."
    failed=1
    continue
  fi

  case "$head_version" in
    "$next_patch"|"$next_minor"|"$next_major")
      echo "$skill: $base_version -> $head_version. OK."
      ;;
    *)
      echo "::error file=$skill_md::$skill: $base_version -> $head_version is not a single-step bump. Use $next_patch, $next_minor, or $next_major."
      failed=1
      ;;
  esac
done

echo
if [ "$failed" -ne 0 ]; then
  echo "Skill version check failed."
else
  echo "All changed skills have a bumped metadata.version and matching Cursor plugin versions."
fi

exit "$failed"
