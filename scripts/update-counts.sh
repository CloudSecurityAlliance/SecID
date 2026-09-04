#!/usr/bin/env bash
# Updates namespace counts in CLAUDE.md and README.md
# Run from repo root: ./scripts/update-counts.sh

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

TYPES="advisory weakness ttp control capability methodology disclosure regulation entity reference"

# Count JSON files per type, build table
total=0
TABLE="| Type | Count |
|------|-------|"

for type in $TYPES; do
  n=$(find "registry/$type" -name '*.json' -not -name '_*' 2>/dev/null | wc -l | tr -d ' ')
  total=$((total + n))
  # Capitalize first letter
  label="$(printf '%s' "$type" | cut -c1 | tr '[:lower:]' '[:upper:]')$(printf '%s' "$type" | cut -c2-)"
  TABLE="$TABLE
| $label | $n |"
done

TABLE="$TABLE
| **Total** | **$total** |"

# Update files with markers
for file in CLAUDE.md README.md; do
  if [ ! -f "$file" ]; then
    echo "Skipping $file (not found)"
    continue
  fi

  if ! grep -q '<!-- REGISTRY-COUNTS-START -->' "$file"; then
    echo "Skipping $file (no REGISTRY-COUNTS-START marker)"
    continue
  fi

  # Use awk to replace content between markers, injecting table via a temp file
  tmpdata=$(mktemp)
  printf '%s\n' "$TABLE" > "$tmpdata"

  awk -v datafile="$tmpdata" '
    /<!-- REGISTRY-COUNTS-START -->/ {
      print
      print ""
      while ((getline line < datafile) > 0) print line
      skip = 1
      next
    }
    /<!-- REGISTRY-COUNTS-END -->/ {
      skip = 0
      print ""
      print
      next
    }
    !skip { print }
  ' "$file" > "${file}.tmp"

  rm -f "$tmpdata"
  mv "${file}.tmp" "$file"

  # Also refresh prose counts that sit OUTSIDE the markers, e.g. "2,130 namespaces".
  # The marker block only covers the table, so without this the table and the
  # surrounding prose drift apart on every namespace batch.
  formatted=$(python3 -c "print(f'{$total:,}')")
  sed -i.bak -E "s/[0-9]{1,3}(,[0-9]{3})+ namespaces/${formatted} namespaces/g; s/[0-9]{4,} namespaces/${formatted} namespaces/g" "$file"
  rm -f "${file}.bak"

  echo "Updated $file: $total namespaces across 10 types (table + prose)"
done
