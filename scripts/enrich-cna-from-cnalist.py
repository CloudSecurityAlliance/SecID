#!/usr/bin/env python3
"""Enrich disclosure entries with cnaID and disclosurePolicy from CNAsList.json.

Reads: ~/GitHub/cveproject/cve-website/src/assets/data/CNAsList.json
Updates: registry/disclosure/**/*.json

For each disclosure entry with a data.cve object:
  1. Match to CNAsList by assignerShortName (case-insensitive)
  2. Add data.cve.cna_id from CNAsList.cnaID
  3. Add data.disclosure_policy from CNAsList.disclosurePolicy

Run: python3 scripts/enrich-cna-from-cnalist.py [--dry-run]
"""

import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path

DRY_RUN = "--dry-run" in sys.argv
CNALIST_FILE = Path(os.path.expanduser(
    "~/GitHub/cveproject/cve-website/src/assets/data/CNAsList.json"
))
REGISTRY_DIR = Path("registry/disclosure")
TODAY = datetime.now(timezone.utc).strftime("%Y-%m-%d")


def main():
    if not CNALIST_FILE.exists():
        print(f"ERROR: CNAsList.json not found at {CNALIST_FILE}")
        sys.exit(1)

    cnas_list = json.load(open(CNALIST_FILE))
    print(f"CNAsList: {len(cnas_list)} entries")

    # Build lookup by shortName (case-insensitive)
    cna_by_short = {}
    for c in cnas_list:
        key = c.get("shortName", "").lower()
        if key:
            cna_by_short[key] = c

    files_modified = 0
    nodes_enriched = 0
    cna_id_added = 0
    policy_added = 0
    warnings = []

    for json_file in sorted(REGISTRY_DIR.rglob("*.json")):
        if "/_" in str(json_file):
            continue

        data = json.loads(json_file.read_text())
        modified = False

        for node in data.get("match_nodes", []):
            node_data = node.get("data", {})
            cve = node_data.get("cve")
            if not cve or not isinstance(cve, dict):
                continue

            short_name = cve.get("assignerShortName", "")
            if not short_name:
                continue

            cna_entry = cna_by_short.get(short_name.lower())
            if not cna_entry:
                warnings.append(f"{json_file}: No CNAsList match for '{short_name}'")
                continue

            enriched = False

            # Add cna_id if not present
            cna_id = cna_entry.get("cnaID")
            if cna_id and "cna_id" not in cve:
                cve["cna_id"] = cna_id
                cna_id_added += 1
                enriched = True

            # Add disclosure_policy if not present in node data
            if "disclosure_policy" not in node_data:
                dp_entries = cna_entry.get("disclosurePolicy", [])
                dp_urls = [p.get("url") for p in dp_entries if p.get("url")]
                if dp_urls:
                    node_data["disclosure_policy"] = {
                        "url": dp_urls[0],
                        "checked": TODAY,
                    }
                    policy_added += 1
                    enriched = True
                else:
                    # Researched, not found
                    node_data["disclosure_policy"] = None
                    enriched = True

            if enriched:
                nodes_enriched += 1
                modified = True

        if modified:
            files_modified += 1
            if not DRY_RUN:
                json_file.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")

    print(f"\n{'='*60}")
    print(f"Mode: {'DRY RUN' if DRY_RUN else 'LIVE'}")
    print(f"Files modified: {files_modified}")
    print(f"Nodes enriched: {nodes_enriched}")
    print(f"  cna_id added: {cna_id_added}")
    print(f"  disclosure_policy added: {policy_added}")

    if warnings:
        print(f"\nWarnings ({len(warnings)}):")
        for w in warnings[:20]:
            print(f"  {w}")
        if len(warnings) > 20:
            print(f"  ... and {len(warnings) - 20} more")


if __name__ == "__main__":
    main()
