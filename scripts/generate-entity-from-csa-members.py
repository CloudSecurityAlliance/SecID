#!/usr/bin/env python3
"""
Generate entity stub entries from the CSA public member list.

For each (entity_name, domain) row in the CSA website members CSV, if no
matching `registry/entity/<path>.json` exists for that namespace, generate a
stub entity entry with status `draft`.

Why this exists:
    SecID's entity type is its "noun" type — the organizations, products, and
    services every other type points at. Today's ~690 entity files come from
    two sources: 475 auto-mined CNA/disclosure stubs and ~215 hand-curated
    entries. Neither is driven by CSA membership, so coverage of real
    security/AI vendors is incidental — present only when a vendor happens to
    be a CVE Numbering Authority. Notable members (Anthropic, Fortinet, and
    most of the ~250 below) have no entity record at all.

    The CSA public member list is a high-quality, curated roster of
    security-relevant organizations — overwhelmingly commercial vendors. It
    fills exactly the gaps the CNA-derived stubs miss. The CSV carries only
    entity_name + domain, but that is sufficient for the entity schema's five
    required fields (schema_version, namespace, type, status, official_name),
    producing records at identical fidelity to the existing CNA stubs.

    Stubs have empty `match_nodes` and `status: draft` because the member list
    doesn't tell us what specific products or services the org offers — that's
    what match_nodes are for, and it needs human research per vendor.

    NOTE: These stubs are intentionally generated WITHOUT a `subtype:` tag, to
    match the current (untagged) state of the rest of the entity registry. The
    entity subtype catalog (organization/product/service/model/dataset plus
    org-nature tags like company/government) is still being designed; once it
    lands, these member-derived records are prime candidates for
    `subtype: ["organization", "company"]` in a tagging sweep.

    Membership itself ("X is a CSA member") is deliberately NOT encoded here.
    That is a relationship-layer fact (an open-ended, changing edge), not an
    intrinsic property of the entity. The registry says what each node IS; the
    future Relationship layer (SPEC §6) says how nodes connect.

Behaviors:
    - Skip if any entity file already covers this namespace (never overwrite;
      the 44 members already present — some hand-curated — are left untouched).
    - Clean domains: strip www., zero-width chars, trailing junk after
      whitespace ("huaweicloud.com http:" -> "huaweicloud.com"), lowercase,
      and take only the host portion before any path separator.
    - Report (and skip) rows with a blank/unusable domain — these have no
      resolvable namespace and need a domain hand-filled first.
    - Reverse-DNS filesystem layout matching the rest of registry/entity/.
    - Output is deterministic (sorted processing, stable field ordering).

Usage:
    python3 scripts/generate-entity-from-csa-members.py [--csv PATH] [--dry-run]
"""

from __future__ import annotations

import argparse
import csv
import glob
import json
import sys
from pathlib import Path

# Resolve repo root from this script's location for portability.
SCRIPT_DIR = Path(__file__).resolve().parent
REPO = SCRIPT_DIR.parent
ENTITY_ROOT = REPO / "registry/entity"

DEFAULT_CSV = (
    "/Volumes/MacMiniData/Users/kurt/GitHub/CloudSecurityAlliance-Internal/"
    "CINO-CSA-Data-Inventory/working-data/csa-website-members-2026-06-08.csv"
)

# Zero-width / invisible characters seen in scraped domains.
_ZERO_WIDTH = "".join(["​", "‌", "‍", "﻿", " "])


def clean_domain(raw: str) -> str | None:
    """Normalize a scraped domain into a bare host, or None if unusable.

    Handles the specific messiness in the CSA scrape: trailing protocol
    fragments ("huaweicloud.com http:"), zero-width characters, www.
    prefixes, stray paths, and casing.
    """
    if not raw:
        return None
    d = raw.strip()
    # Drop anything after whitespace ("huaweicloud.com http:" -> "huaweicloud.com").
    d = d.split()[0] if d.split() else ""
    # Strip zero-width / invisible chars anywhere in the string.
    d = d.translate({ord(c): None for c in _ZERO_WIDTH})
    # Strip a scheme if one slipped in.
    for scheme in ("https://", "http://"):
        if d.lower().startswith(scheme):
            d = d[len(scheme):]
    # Keep only the host portion (before any path).
    d = d.split("/")[0]
    d = d.strip(".").lower()
    if d.startswith("www."):
        d = d[4:]
    # Must look like a domain: at least one dot and no spaces.
    if "." not in d or " " in d or not d:
        return None
    return d


def entity_path_for(domain: str) -> Path:
    """Compute the reverse-DNS entity filesystem path for a bare domain.

    e.g. "a-lign.com" -> registry/entity/com/a-lign.json
         "4science.it" -> registry/entity/it/4science.json
    Multi-label domains keep the non-TLD labels joined by dots, matching the
    existing registry layout (e.g. "csrc.nist.gov" -> gov/csrc.nist.json).
    """
    parts = domain.split(".")
    tld = parts[-1]
    rest = ".".join(parts[:-1])
    return ENTITY_ROOT / tld / f"{rest}.json"


def member_to_entity_stub(name: str, domain: str, domain_hand_filled: bool = False) -> dict:
    """Convert a CSA member (name, cleaned domain) into an entity stub.

    Field ordering matches the existing entity registry files. When
    `domain_hand_filled` is True, the provenance note records that the
    domain was supplied by hand (the public member list left it blank)
    rather than carried in the source CSV — keeping provenance honest.
    """
    if domain_hand_filled:
        provenance = (
            "Auto-generated stub from the CSA public member list "
            "(csa-website-members-2026-06-08). The member's name is from that "
            "list; the public list had no domain for this member, so the "
            "domain was hand-filled from public knowledge. match_nodes are "
            "empty pending human review to add product/service patterns. CSA "
            "membership itself is a relationship-layer fact and is "
            "intentionally not encoded on this record."
        )
    else:
        provenance = (
            "Auto-generated stub from the CSA public member list "
            "(csa-website-members-2026-06-08). Identity is the member's name "
            "and primary domain; match_nodes are empty pending human review to "
            "add product/service patterns. CSA membership itself is a "
            "relationship-layer fact and is intentionally not encoded on this "
            "record."
        )
    return {
        "schema_version": "1.0",
        "namespace": domain,
        "type": "entity",
        "status": "draft",
        "status_notes": provenance,
        "official_name": name,
        "common_name": None,
        "alternate_names": None,
        "notes": (
            "Organization sourced from the Cloud Security Alliance public "
            "member roster. This entity entry was auto-generated to give each "
            "member a parallel identity record; the match_nodes array is empty "
            "pending human research into the organization's specific products "
            "and services."
        ),
        "wikidata": None,
        "wikipedia": None,
        "urls": [{"type": "website", "url": f"https://{domain}"}],
        "match_nodes": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--csv", default=DEFAULT_CSV, help="Path to the CSA members CSV")
    parser.add_argument(
        "--domains-hand-filled",
        action="store_true",
        help=(
            "Mark generated records' provenance as hand-filled domains. Use for "
            "a supplemental CSV of members whose public-list domain was blank "
            "and supplied by hand."
        ),
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be created without writing files",
    )
    args = parser.parse_args()

    csv_path = Path(args.csv)
    if not csv_path.exists():
        print(f"ERROR: CSV not found: {csv_path}", file=sys.stderr)
        return 1

    # Inventory existing entity files by namespace so we never overwrite —
    # including the 44 members already present (some hand-curated).
    existing_entity_namespaces: set[str] = set()
    for path in glob.glob(str(ENTITY_ROOT / "**/*.json"), recursive=True):
        try:
            d = json.load(open(path))
        except Exception:
            continue
        ns = d.get("namespace")
        if ns:
            existing_entity_namespaces.add(ns)

    rows = list(csv.DictReader(open(csv_path)))

    created = 0
    skipped_already_exists = 0
    skipped_no_domain: list[str] = []
    skipped_dup_in_csv = 0
    creations: list[Path] = []
    seen_ns: set[str] = set()

    # Sort by name for deterministic processing order.
    for row in sorted(rows, key=lambda r: (r.get("entity_name") or "").lower()):
        name = (row.get("entity_name") or "").strip()
        domain = clean_domain(row.get("domain") or "")
        if not name:
            continue
        if not domain:
            skipped_no_domain.append(name)
            continue
        if domain in seen_ns:
            # Same domain appeared twice in the CSV; only emit once.
            skipped_dup_in_csv += 1
            continue
        seen_ns.add(domain)
        if domain in existing_entity_namespaces:
            skipped_already_exists += 1
            continue

        target = entity_path_for(domain)
        if target.exists():
            skipped_already_exists += 1
            continue

        stub = member_to_entity_stub(name, domain, domain_hand_filled=args.domains_hand_filled)
        creations.append(target)
        if not args.dry_run:
            target.parent.mkdir(parents=True, exist_ok=True)
            with open(target, "w") as f:
                json.dump(stub, f, indent=2)
                f.write("\n")
        created += 1

    print(f"Created entity stubs: {created}")
    print(f"Skipped (entity already exists for namespace): {skipped_already_exists}")
    if skipped_dup_in_csv:
        print(f"Skipped (duplicate domain within CSV): {skipped_dup_in_csv}")
    if skipped_no_domain:
        print(f"Skipped (blank/unusable domain — need hand-fill): {len(skipped_no_domain)}")
        for n in sorted(skipped_no_domain):
            print(f"    - {n}")

    if args.dry_run:
        print("\n(dry run — no files written)")
        for target in creations[:10]:
            print(f"  would create: {target.relative_to(REPO)}")
        if len(creations) > 10:
            print(f"  ... and {len(creations) - 10} more")

    return 0


if __name__ == "__main__":
    sys.exit(main())
