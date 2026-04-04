#!/usr/bin/env bash
# Downloads all CVE CNA partner detail pages into working-data/cna/pages/
# Run from repo root: ./scripts/fetch-cna-pages.sh
#
# Uses curl with rate limiting (0.5s between requests) to be polite.
# Pages are saved as HTML files named by partner slug.

set -euo pipefail
cd "$(git rev-parse --show-toplevel)"

SLUGFILE="working-data/cna/partner-slugs.txt"
OUTDIR="working-data/cna/pages"
BASE_URL="https://www.cve.org/PartnerInformation/ListofPartners/partner"

if [ ! -f "$SLUGFILE" ]; then
  echo "Error: $SLUGFILE not found. Run the scraper first to generate it."
  exit 1
fi

mkdir -p "$OUTDIR"

total=$(wc -l < "$SLUGFILE" | tr -d ' ')
count=0
skipped=0
failed=0

echo "Fetching $total CNA partner pages..."
echo "Output: $OUTDIR/"
echo ""

while IFS= read -r slug; do
  count=$((count + 1))
  outfile="$OUTDIR/${slug}.html"

  # Skip if already downloaded
  if [ -f "$outfile" ] && [ -s "$outfile" ]; then
    skipped=$((skipped + 1))
    continue
  fi

  printf "[%d/%d] %s ... " "$count" "$total" "$slug"

  if curl -sS -f -o "$outfile" \
    -H "User-Agent: SecID-Registry-Research/1.0 (https://github.com/CloudSecurityAlliance/SecID)" \
    "${BASE_URL}/${slug}" 2>/dev/null; then
    size=$(wc -c < "$outfile" | tr -d ' ')
    printf "OK (%s bytes)\n" "$size"
  else
    printf "FAILED\n"
    rm -f "$outfile"
    failed=$((failed + 1))
  fi

  # Rate limit: 0.5s between requests
  sleep 0.5

done < "$SLUGFILE"

downloaded=$((count - skipped - failed))
echo ""
echo "Done: $downloaded downloaded, $skipped skipped (already existed), $failed failed out of $total"
