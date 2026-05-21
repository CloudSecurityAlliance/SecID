#!/usr/bin/env python3
"""
Validate that every `subtype:` value used in registry JSON data is declared
in SecID-Service's `src/type-registry.ts`.

Why this script exists:
    Adding a new SecID subtype is a deliberate design choice — it should
    require a code review on the SecID-Service side that adds the value
    to the type-registry constant. This script enforces that gate by
    failing the PR if any registry entry uses a subtype value that the
    Worker doesn't know about.

How it works:
    1. Fetches SecID-Service's `src/type-registry.ts` source from a configurable
       location (default: GitHub raw URL for main branch). Local-path fallback
       lets contributors test without network access.
    2. Extracts declared subtype values per type using regex (sufficient for
       the simple TypeScript object-literal structure we use).
    3. Scans all `registry/**/*.json` files. For every source-level match_node
       with a `data.subtype` array, checks each value is declared for the
       owning type.
    4. Reports drift and exits non-zero if any value is undeclared.

Usage:
    python3 scripts/validate-subtypes.py
        Fetch type-registry.ts from main branch (default URL).

    python3 scripts/validate-subtypes.py --type-registry-path /path/to/type-registry.ts
        Use a local copy (useful when SecID-Service is checked out locally).

    python3 scripts/validate-subtypes.py --type-registry-url <url>
        Custom raw URL (e.g., pointing at a feature branch during dev).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import urllib.request
from pathlib import Path

DEFAULT_TYPE_REGISTRY_URL = (
    "https://raw.githubusercontent.com/CloudSecurityAlliance/"
    "SecID-Service/main/src/type-registry.ts"
)

# Matches "type: \"name\"," (the start of a TypeDef object literal).
# Pairs with subtype-value extraction below.
TYPE_HEADER_RE = re.compile(r'type:\s*"([a-z][a-z0-9-]*)"\s*,')

# Matches "value: \"kebab-or-dotted-string\"," — a SubtypeDef value.
SUBTYPE_VALUE_RE = re.compile(r'value:\s*"([a-z0-9.\-]+)"\s*,')


def parse_type_registry(source: str) -> dict[str, set[str]]:
    """Extract {type_name: {subtype_value, ...}} from type-registry.ts source.

    Parses by walking the source linearly: each TYPE_HEADER opens a type
    section, and every SUBTYPE_VALUE encountered before the next TYPE_HEADER
    belongs to that type. This is robust to the readonly arrays, comments,
    and trailing-comma formatting we use.
    """
    declared: dict[str, set[str]] = {}
    current_type: str | None = None
    cursor = 0
    while cursor < len(source):
        next_type_match = TYPE_HEADER_RE.search(source, cursor)
        next_subtype_match = SUBTYPE_VALUE_RE.search(source, cursor)

        # Whichever pattern appears next at the current cursor wins.
        candidates = [m for m in (next_type_match, next_subtype_match) if m]
        if not candidates:
            break
        match = min(candidates, key=lambda m: m.start())

        if match is next_type_match:
            current_type = match.group(1)
            declared.setdefault(current_type, set())
        else:  # subtype value
            if current_type is None:
                # A subtype value appearing before any type header is malformed
                # input — bail loudly rather than silently miscategorize.
                raise ValueError(
                    f"Subtype value {match.group(1)!r} found before any type header"
                )
            declared[current_type].add(match.group(1))
        cursor = match.end()
    return declared


def fetch_type_registry(*, url: str | None, path: str | None) -> str:
    if path:
        return Path(path).read_text()
    target_url = url or DEFAULT_TYPE_REGISTRY_URL
    with urllib.request.urlopen(target_url, timeout=20) as resp:
        return resp.read().decode("utf-8")


def collect_used_subtypes(registry_root: Path) -> dict[tuple[str, str], list[tuple[Path, str]]]:
    """Scan registry JSON files for source-level subtype usages.

    Returns a mapping {(type, value): [(file_path, pattern_str), ...]} so
    error messages can point at the exact match_nodes that triggered a failure.
    """
    used: dict[tuple[str, str], list[tuple[Path, str]]] = {}
    for path in sorted(registry_root.rglob("*.json")):
        # Skip type-level description files (registry/<type>.json).
        # Those live in the parent of the per-namespace files.
        if path.parent == registry_root:
            continue
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError as exc:
            print(f"WARN: skipping unparseable {path}: {exc}", file=sys.stderr)
            continue
        type_name = doc.get("type")
        if not isinstance(type_name, str):
            continue
        for node in doc.get("match_nodes") or []:
            if not isinstance(node, dict):
                continue
            data = node.get("data") or {}
            if not isinstance(data, dict):
                continue
            subtypes = data.get("subtype")
            if subtypes is None:
                continue
            values: list[str] = []
            if isinstance(subtypes, list):
                values = [v for v in subtypes if isinstance(v, str)]
            elif isinstance(subtypes, str):
                # Tolerate single-string form even though convention is array.
                values = [subtypes]
            pattern_label = ",".join(node.get("patterns") or []) or "(no patterns)"
            for v in values:
                used.setdefault((type_name, v), []).append((path, pattern_label))
    return used


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
        "--registry-root",
        default="registry",
        help="Path to the SecID registry/ directory (default: ./registry)",
    )
    args = parser.parse_args()

    registry_root = Path(args.registry_root)
    if not registry_root.is_dir():
        print(f"ERROR: registry root not found at {registry_root}", file=sys.stderr)
        return 2

    try:
        source = fetch_type_registry(url=args.type_registry_url, path=args.type_registry_path)
    except Exception as exc:
        print(f"ERROR: could not fetch type-registry.ts: {exc}", file=sys.stderr)
        return 2

    declared = parse_type_registry(source)
    used = collect_used_subtypes(registry_root)

    failures: list[str] = []
    for (type_name, value), occurrences in sorted(used.items()):
        allowed = declared.get(type_name, set())
        if value not in allowed:
            count = len(occurrences)
            sample = occurrences[0]
            failures.append(
                f"  {type_name} + subtype: {value!r} used in {count} match_node(s); "
                f"first occurrence: {sample[0]} (patterns: {sample[1]})"
            )

    if failures:
        print("FAIL: registry data uses subtype values not declared in SecID-Service type-registry.ts")
        print()
        for line in failures:
            print(line)
        print()
        print("To fix:")
        print("  1. If the subtype is legitimate, add it to type-registry.ts in SecID-Service")
        print("     and merge that PR FIRST.")
        print("  2. Then update SecID's docs/reference/TYPES-AND-SUBTYPES.md to document the new value.")
        print("  3. Re-run this script — it should now pass.")
        return 1

    total_uses = sum(len(v) for v in used.values())
    print(
        f"OK: {total_uses} subtype usage(s) across {len(used)} distinct (type, value) pairs; "
        f"all declared in type-registry.ts"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
