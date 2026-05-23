#!/usr/bin/env python3
"""
Generate entity stub entries from disclosure entries.

For each `registry/disclosure/<path>.json`, if no matching
`registry/entity/<path>.json` exists, generate a stub entity entry with
status `draft` using the disclosure entry's metadata.

Why this exists:
    SecID disclosure entries (mostly CNAs) cover ~486 vendors and government
    orgs, but the parallel `entity` type — which describes the organization
    itself, not just its vulnerability-reporting program — only covers a
    handful of the top vendors. This means most CNA vendors can be cited as
    "report a vulnerability here" but not as "this organization exists."

    The disclosure entries already contain the metadata needed for a basic
    entity record: official_name, common_name, alternate_names, website
    URL, sometimes wikidata/wikipedia. This script reads each disclosure
    JSON and emits an entity stub mirroring it.

    Stubs have empty `match_nodes` and `status: draft` because:
      (a) The disclosure data doesn't tell us what specific products or
          services the organization offers — that's what match_nodes are
          for, and it needs human research per vendor.
      (b) The metadata copied is good for "this org exists" but the broader
          characterization (alternate_names beyond CNA pages, accurate
          wikidata/wikipedia links, etc.) deserves human review.

Behaviors:
    - Skip if an entity file already exists at the mirrored path.
    - Skip if any entity file already covers this namespace (in case the
      entity entry was filed under a different path).
    - Preserve the disclosure file's directory structure under entity/.
    - Output is deterministic (sorted output where applicable, stable
      field ordering).

Usage:
    python3 scripts/generate-entity-stubs-from-disclosure.py [--dry-run]
"""

from __future__ import annotations

import argparse
import glob
import json
import sys
from pathlib import Path

# Resolve repo root from this script's location for portability.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent
DISCLOSURE_ROOT = REPO / "registry/disclosure"
ENTITY_ROOT = REPO / "registry/entity"


def disclosure_to_entity_stub(disc: dict) -> dict:
    """Convert a disclosure JSON to an entity stub.

    Preserves field ordering matching the existing entity registry files
    (schema_version, namespace, type, status, status_notes, then identity
    fields, then urls and match_nodes).
    """
    ns = disc["namespace"]
    # Pick out only the canonical website URL — disclosure entries often
    # also have CNA-specific URLs (security policy, vulnerability list)
    # that don't belong on the entity record. The website URL is the
    # natural primary URL for an organization.
    website_urls = []
    for u in disc.get("urls") or []:
        if isinstance(u, dict) and u.get("type") == "website" and u.get("url"):
            website_urls.append({"type": "website", "url": u["url"]})
    return {
        "schema_version": "1.0",
        "namespace": ns,
        "type": "entity",
        "status": "draft",
        "status_notes": (
            "Auto-generated stub from CVE CNA disclosure data. "
            "Identity metadata copied from the matching disclosure entry; "
            "match_nodes are empty pending human review to add product/service "
            "patterns. See companion secid:disclosure/" + ns + "/cna for the "
            "vulnerability-reporting program."
        ),
        "official_name": disc.get("official_name"),
        "common_name": disc.get("common_name"),
        "alternate_names": disc.get("alternate_names"),
        "notes": (
            "Organization with a CVE Numbering Authority (CNA) disclosure "
            f"program. See secid:disclosure/{ns}/cna for vulnerability-reporting "
            "channels and contacts. This entity entry was auto-generated to "
            "ensure each CNA-vendor has a parallel identity record; the "
            "match_nodes array is empty pending human research into the "
            "vendor's specific products and services."
        ),
        "wikidata": disc.get("wikidata"),
        "wikipedia": disc.get("wikipedia"),
        "urls": website_urls,
        "match_nodes": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing files",
    )
    args = parser.parse_args()

    # Inventory existing entity files by namespace, not just by path,
    # so we skip when an entity entry exists at any path.
    existing_entity_namespaces: set[str] = set()
    for path in glob.glob(str(ENTITY_ROOT / "**/*.json"), recursive=True):
        try:
            d = json.load(open(path))
        except Exception:
            continue
        ns = d.get("namespace")
        if ns:
            existing_entity_namespaces.add(ns)

    # Walk disclosure files.
    disclosure_paths = sorted(glob.glob(str(DISCLOSURE_ROOT / "**/*.json"), recursive=True))

    created = 0
    skipped_already_exists = 0
    skipped_unparseable = 0
    creations: list[tuple[Path, Path]] = []

    for disc_path_str in disclosure_paths:
        disc_path = Path(disc_path_str)
        try:
            disc = json.load(open(disc_path))
        except Exception as exc:
            print(f"SKIP (unparseable): {disc_path}: {exc}", file=sys.stderr)
            skipped_unparseable += 1
            continue

        ns = disc.get("namespace")
        if not ns:
            continue
        if ns in existing_entity_namespaces:
            skipped_already_exists += 1
            continue

        # Compute the entity-side mirror path from the disclosure-side path.
        rel = disc_path.relative_to(DISCLOSURE_ROOT)
        target = ENTITY_ROOT / rel
        if target.exists():
            # Defensive: shouldn't happen if existing_entity_namespaces was
            # built correctly, but guard against path-vs-namespace mismatches.
            skipped_already_exists += 1
            continue

        stub = disclosure_to_entity_stub(disc)
        creations.append((disc_path, target))
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w") as f:
                json.dump(stub, f, indent=2)
                f.write("\n")
        created += 1

    print(f"Created entity stubs: {created}")
    print(f"Skipped (entity already exists for namespace): {skipped_already_exists}")
    if skipped_unparseable:
        print(f"Skipped (disclosure unparseable): {skipped_unparseable}", file=sys.stderr)

    if args.dry_run:
        print("\n(dry run — no files written)")
        for disc_path, target in creations[:10]:
            print(f"  would create: {target.relative_to(REPO)}")
        if len(creations) > 10:
            print(f"  ... and {len(creations) - 10} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
