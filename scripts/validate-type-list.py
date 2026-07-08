#!/usr/bin/env python3
"""Validate that the SecID type list is consistent across the spec repo and
SecID-Service's canonical type-registry.ts.

Why this script exists:
    Adding or removing a SecID type is a spec-level event that must touch:
      - schemas/registry-namespace.schema.json (the `type` field's enum)
      - SecID-Service/src/type-registry.ts (the canonical TYPE_REGISTRY)
      - SecID-Server-API and SecID-Client-SDK (documented in CLAUDE.md)

    This script enforces the first two — the most load-bearing pair — at PR
    time. If they drift, the resolver and the schema disagree about what
    types exist, and registry data may pass schema validation but fail the
    resolver, or vice versa.

How it works:
    1. Reads the `type` field's enum from the JSON Schema.
    2. Fetches SecID-Service's src/type-registry.ts (raw URL by default;
       local path for offline / pre-merge testing).
    3. Extracts type names from the TypeScript via regex (matches the
       approach validate-subtypes.py uses).
    4. Reports drift in either direction.

Usage:
    python3 scripts/validate-type-list.py
        Fetch type-registry.ts from main branch (default URL).

    python3 scripts/validate-type-list.py --type-registry-path /path/to/type-registry.ts
        Use a local copy (useful when testing changes to SecID-Service
        before merging).

    python3 scripts/validate-type-list.py --type-registry-url <url>
        Custom raw URL (e.g., pointing at a feature branch).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

# PINNED to a reviewed commit, not the moving `main` branch. Fetching `main`
# is a cross-repo TOCTOU: an unrelated SecID-Service merge silently changes the
# canonical type set that gates every SecID PR here. Pinning forces a reviewed
# bump in THIS repo. MAINTAINER ACTION: when SecID-Service's type-registry.ts
# changes, open a reviewed PR here bumping this SHA in BOTH validators
# (validate-type-list.py + validate-subtypes.py) in lockstep. Do NOT revert to
# `main`. (Override for local testing: --type-registry-url / -path.)
SECID_SERVICE_PINNED_SHA = "de7a87421d9ab02df39adb9a90551993fe4821f1"

DEFAULT_TYPE_REGISTRY_URL = (
    "https://raw.githubusercontent.com/CloudSecurityAlliance/"
    f"SecID-Service/{SECID_SERVICE_PINNED_SHA}/src/type-registry.ts"
)

# Matches `type: "name",` (the start of a TypeDef object literal).
# Same regex as validate-subtypes.py uses — keep them aligned if either changes.
TYPE_HEADER_RE = re.compile(r'type:\s*"([a-z][a-z0-9-]*)"\s*,')


def extract_canonical_types(source: str) -> set[str]:
    """Pull type names from type-registry.ts source."""
    return set(TYPE_HEADER_RE.findall(source))


def extract_schema_types(schema_path: Path) -> set[str]:
    """Pull the `type` field's enum from registry-namespace.schema.json."""
    schema = json.loads(schema_path.read_text())
    try:
        type_enum = schema["properties"]["type"]["enum"]
    except (KeyError, TypeError) as exc:
        raise ValueError(
            f"Could not find properties.type.enum in {schema_path}: {exc}"
        ) from exc
    if not isinstance(type_enum, list):
        raise ValueError(f"properties.type.enum is not a list in {schema_path}")
    return set(type_enum)


def fetch_type_registry(*, url: str | None, path: str | None) -> str:
    if path:
        return Path(path).read_text()
    if url is None and SECID_SERVICE_PINNED_SHA == "<PIN_ME_TO_A_REVIEWED_SHA>":
        raise RuntimeError(
            "type-registry.ts fetch is not pinned: set SECID_SERVICE_PINNED_SHA to a "
            "reviewed SecID-Service commit (or pass --type-registry-path / "
            "--type-registry-url). Refusing to fetch from an unpinned source."
        )
    target_url = url or DEFAULT_TYPE_REGISTRY_URL
    with urllib.request.urlopen(target_url, timeout=20) as resp:
        return resp.read().decode("utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--type-registry-url",
        help="Raw URL to SecID-Service's type-registry.ts (default: main branch)",
    )
    parser.add_argument(
        "--type-registry-path",
        help="Local path to type-registry.ts (overrides URL)",
    )
    parser.add_argument(
        "--schema-path",
        default="schemas/registry-namespace.schema.json",
        help="Path to the registry-namespace JSON Schema",
    )
    args = parser.parse_args()

    schema_path = Path(args.schema_path)
    if not schema_path.is_file():
        print(f"ERROR: schema not found at {schema_path}", file=sys.stderr)
        return 2

    try:
        source = fetch_type_registry(url=args.type_registry_url, path=args.type_registry_path)
    except Exception as exc:
        print(f"ERROR: could not fetch type-registry.ts: {exc}", file=sys.stderr)
        return 2

    canonical = extract_canonical_types(source)
    in_schema = extract_schema_types(schema_path)

    if canonical == in_schema:
        print(
            f"OK: {len(canonical)} types match between {schema_path} and "
            f"SecID-Service type-registry.ts"
        )
        return 0

    print("FAIL: type list drift between schema and SecID-Service type-registry.ts")
    print()
    only_in_canonical = canonical - in_schema
    only_in_schema = in_schema - canonical
    if only_in_canonical:
        print(f"  In type-registry.ts but missing from schema enum:")
        for t in sorted(only_in_canonical):
            print(f"    - {t}")
    if only_in_schema:
        print(f"  In schema enum but missing from type-registry.ts:")
        for t in sorted(only_in_schema):
            print(f"    - {t}")
    print()
    print("To fix:")
    print("  1. Decide which side is correct (usually type-registry.ts — it's canonical)")
    print("  2. Update the other side to match")
    print("  3. Re-run this script")
    return 1


if __name__ == "__main__":
    sys.exit(main())
