#!/usr/bin/env python3
"""Validate every registry/**/*.json file against the JSON Schema.

Catches structural errors in registry data before they ship — missing
required fields, wrong types, invalid enum values, malformed match_node
trees, etc. The schema (schemas/registry-namespace.schema.json) is the
spec-side source of truth for what a registry entry must look like.

Skips:
  - Files starting with `_` (templates, _deferred entries)
  - Top-level registry/<type>.json files (those are type descriptions,
    not namespace entries)

Usage:
    python3 scripts/validate-registry-schema.py
        Validate all registry JSON files. Exits 0 if all pass, 1 if any fail.

    python3 scripts/validate-registry-schema.py --registry-root path/to/registry
        Validate a different registry directory (for testing).

Output: human-readable summary on stdout. Failures listed first 30; full
error text for each (truncated to 200 chars per error).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--registry-root",
        default="registry",
        help="Path to the SecID registry/ directory (default: ./registry)",
    )
    parser.add_argument(
        "--schema-path",
        default="schemas/registry-namespace.schema.json",
        help="Path to the JSON Schema (default: ./schemas/registry-namespace.schema.json)",
    )
    args = parser.parse_args()

    registry_root = Path(args.registry_root)
    if not registry_root.is_dir():
        print(f"ERROR: registry root not found at {registry_root}", file=sys.stderr)
        return 2

    schema_path = Path(args.schema_path)
    if not schema_path.is_file():
        print(f"ERROR: schema not found at {schema_path}", file=sys.stderr)
        return 2

    schema = json.loads(schema_path.read_text())
    validator = jsonschema.Draft202012Validator(schema)

    failures: list[tuple[Path, str]] = []
    total = 0

    for path in sorted(registry_root.rglob("*.json")):
        # Skip templates, _deferred, and other underscore-prefixed files.
        if path.stem.startswith("_"):
            continue
        # Skip top-level type-description files like registry/advisory.json.
        # (Those don't follow the namespace schema.)
        if path.parent == registry_root:
            continue
        total += 1
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            failures.append((path, f"JSON parse error: {exc}"))
            continue
        errors = list(validator.iter_errors(doc))
        if errors:
            # Report only the first error per file to keep output manageable.
            failures.append((path, errors[0].message[:200]))

    if failures:
        print(f"FAIL: {len(failures)} of {total} registry files failed validation")
        print()
        for path, msg in failures[:30]:
            print(f"  {path}: {msg}")
        if len(failures) > 30:
            print(f"  ... and {len(failures) - 30} more")
        print()
        print("To debug a specific file:")
        print(f"  python3 -c \"import json,jsonschema; "
              f"jsonschema.Draft202012Validator(json.load(open('{schema_path}'))).validate("
              f"json.load(open('<path>')))\"")
        return 1

    print(f"OK: all {total} registry files validate against {schema_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
