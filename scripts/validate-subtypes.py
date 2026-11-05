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
       location (default: GitHub raw URL at the pinned SecID-Service commit). Local-path fallback
       lets contributors test without network access.
    2. Extracts declared subtype values per type using regex (sufficient for
       the simple TypeScript object-literal structure we use).
    3. Scans all `registry/**/*.json` files:
       - Fails if any non-root (child/grandchild) match_node carries `data.subtype`
         (subtype is a source-level-only property per docs/reference/TYPES-AND-SUBTYPES.md).
       - For every source-level match_node with a `data.subtype` array, checks each
         value is declared for the owning type.
       - Optionally (`--completeness warn|fail`) checks that every source-level
         match_node in a type with declared subtypes carries a non-empty `data.subtype`.
    4. Reports drift and exits non-zero if any value is undeclared, misplaced on a
       child node, or (under `--completeness fail`) missing.

Usage:
    python3 scripts/validate-subtypes.py
        Fetch type-registry.ts at the pinned SecID-Service commit (default URL).

    python3 scripts/validate-subtypes.py --completeness warn
        Also warn on source-level match_nodes missing `data.subtype` in types that
        have declared subtypes.

    python3 scripts/validate-subtypes.py --self-test
        Run offline unit tests for subtype validation rules.

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

# PINNED to a reviewed commit, not the moving `main` branch. Fetching `main`
# is a cross-repo TOCTOU: an unrelated SecID-Service merge silently changes the
# canonical type/subtype set that gates every SecID PR here. Pinning forces a
# reviewed bump in THIS repo. MAINTAINER ACTION: when SecID-Service's
# type-registry.ts changes, open a reviewed PR here bumping this SHA in BOTH
# validators (validate-subtypes.py + validate-type-list.py) in lockstep. Do NOT
# revert to `main`. (Override for local testing: --type-registry-url / -path.)
SECID_SERVICE_PINNED_SHA = "203b80268367f306eab4018e1f1e91205656a8ac"

DEFAULT_TYPE_REGISTRY_URL = (
    "https://raw.githubusercontent.com/CloudSecurityAlliance/"
    f"SecID-Service/{SECID_SERVICE_PINNED_SHA}/src/type-registry.ts"
)

# Matches "type: \"name\"," (the start of a TypeDef object literal).
# Pairs with subtype-value extraction below.
TYPE_HEADER_RE = re.compile(r'type:\s*"([a-z][a-z0-9-]*)"\s*,')

# Matches "value: \"kebab-or-dotted-string\"," — a SubtypeDef value.
SUBTYPE_VALUE_RE = re.compile(r'value:\s*"([a-z0-9.\-]+)"\s*,')

# Types that have been 100% subtype-tagged and must never regress (#101).
ENFORCED_COMPLETE_TYPES = {"methodology"}


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
    if url is None and SECID_SERVICE_PINNED_SHA == "<PIN_ME_TO_A_REVIEWED_SHA>":
        raise RuntimeError(
            "type-registry.ts fetch is not pinned: set SECID_SERVICE_PINNED_SHA to a "
            "reviewed SecID-Service commit (or pass --type-registry-path / "
            "--type-registry-url). Refusing to fetch from an unpinned source."
        )
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


def iter_child_subtypes(nodes: list | None, trail: list[str] | None = None):
    """Yield (node_trail, subtype_value) for any non-root match_node carrying data.subtype."""
    current_trail = trail or []
    for i, node in enumerate(nodes or []):
        if not isinstance(node, dict):
            continue
        pats = node.get("patterns") or []
        first_pat = pats[0] if pats and isinstance(pats[0], str) else "(no patterns)"
        here = current_trail + [f"{i}:{first_pat}"]
        if current_trail:
            data = node.get("data")
            if isinstance(data, dict) and "subtype" in data and data["subtype"] is not None:
                yield " > ".join(here), data["subtype"]
        children = node.get("children")
        if isinstance(children, list):
            yield from iter_child_subtypes(children, here)


def collect_child_subtype_violations(registry_root: Path) -> list[tuple[Path, str, object]]:
    """Scan registry JSON files for forbidden child/grandchild data.subtype fields."""
    violations: list[tuple[Path, str, object]] = []
    for path in sorted(registry_root.rglob("*.json")):
        if path.parent == registry_root:
            continue
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        for where, raw_subtype in iter_child_subtypes(doc.get("match_nodes")):
            violations.append((path, where, raw_subtype))
    return violations


def collect_missing_subtypes(
    registry_root: Path, declared: dict[str, set[str]]
) -> list[tuple[Path, str, str]]:
    """Return (path, type_name, pattern_label) for source-level match_nodes that lack
    a non-empty data.subtype in types that have declared subtypes in type-registry.ts.
    """
    missing: list[tuple[Path, str, str]] = []
    for path in sorted(registry_root.rglob("*.json")):
        if path.parent == registry_root:
            continue
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue
        type_name = doc.get("type")
        if not isinstance(type_name, str) or not declared.get(type_name):
            continue
        for node in doc.get("match_nodes") or []:
            if not isinstance(node, dict):
                continue
            data = node.get("data") or {}
            if not isinstance(data, dict):
                data = {}
            subtypes = data.get("subtype")
            has_subtype = False
            if isinstance(subtypes, list):
                has_subtype = any(isinstance(v, str) and v.strip() for v in subtypes)
            elif isinstance(subtypes, str):
                has_subtype = bool(subtypes.strip())
            if not has_subtype:
                pattern_label = ",".join(node.get("patterns") or []) or "(no patterns)"
                missing.append((path, type_name, pattern_label))
    return missing


def self_test() -> int:
    """Offline unit tests for subtype validation rules (#100, #101)."""
    import tempfile

    fake_ts = '''
    export const TYPE_REGISTRY = [
      {
        type: "methodology",
        subtypes: [
          { value: "risk-analysis", label: "Risk Analysis" },
          { value: "scoring", label: "Scoring" },
        ],
      },
      {
        type: "control",
        subtypes: [],
      },
    ];
    '''
    declared = parse_type_registry(fake_ts)
    assert declared == {
        "methodology": {"risk-analysis", "scoring"},
        "control": set(),
    }, f"unexpected parse_type_registry result: {declared}"

    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "methodology.json").write_text('{"type": "methodology"}')
        ns_dir = root / "methodology" / "org"
        ns_dir.mkdir(parents=True)

        doc = {
            "type": "methodology",
            "match_nodes": [
                {
                    "patterns": ["(?i)^good-source$"],
                    "data": {"subtype": ["scoring"]},
                    "children": [
                        {
                            "patterns": ["^v1$"],
                            "data": {"subtype": ["scoring"]},
                        }
                    ],
                },
                {
                    "patterns": ["(?i)^untagged-source$"],
                    "data": {"official_name": "Untagged"},
                },
                {
                    "patterns": ["(?i)^bad-value-source$"],
                    "data": {"subtype": ["not-a-real-subtype"]},
                },
            ],
        }
        (ns_dir / "example.json").write_text(json.dumps(doc))

        used = collect_used_subtypes(root)
        child_violations = collect_child_subtype_violations(root)
        missing = collect_missing_subtypes(root, declared)

        checks = [
            ("declared_value_collected", ("methodology", "scoring") in used),
            ("undeclared_value_collected", ("methodology", "not-a-real-subtype") in used),
            (
                "child_subtype_flagged",
                len(child_violations) == 1
                and "0:(?i)^good-source$ > 0:^v1$" in child_violations[0][1],
            ),
            (
                "missing_subtype_flagged",
                len(missing) == 1 and missing[0][2] == "(?i)^untagged-source$",
            ),
        ]
        failed = [name for name, ok in checks if not ok]
        for name, ok in checks:
            print(f"  {'ok' if ok else 'FAIL'}  {name}")
        print("self-test:", "PASS" if not failed else f"FAIL ({', '.join(failed)})")
        return 0 if not failed else 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument(
        "--type-registry-url",
        help="Raw URL to SecID-Service's type-registry.ts (default: pinned SecID-Service commit, SECID_SERVICE_PINNED_SHA)",
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
    parser.add_argument(
        "--completeness",
        choices=("off", "warn", "fail"),
        default="off",
        help="Check source-level match_nodes in types with declared subtypes for missing data.subtype (default: off)",
    )
    parser.add_argument(
        "--self-test",
        action="store_true",
        help="Run built-in unit tests and exit",
    )
    args = parser.parse_args()

    if args.self_test:
        return self_test()

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
    child_violations = collect_child_subtype_violations(registry_root)

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

    if child_violations:
        print("FAIL: child/grandchild match_nodes must not carry data.subtype (source-level only)")
        print()
        for path, where, raw_subtype in child_violations:
            print(f"  {path}: {where} has data.subtype={raw_subtype!r}")
        print()
        print("Move data.subtype to the source-level match_node in match_nodes[].")
        return 1

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

    missing_all = collect_missing_subtypes(registry_root, declared)
    enforced_missing = [
        item for item in missing_all if item[1] in ENFORCED_COMPLETE_TYPES
    ]
    if enforced_missing:
        print(
            f"FAIL: {len(enforced_missing)} source-level match_node(s) in enforced-complete "
            f"type(s) {sorted(ENFORCED_COMPLETE_TYPES)} are missing data.subtype:"
        )
        for path, type_name, pattern_label in enforced_missing:
            print(f"  [{type_name}] {path} (patterns: {pattern_label})")
        return 1

    if args.completeness != "off" and missing_all:
        level = "FAIL" if args.completeness == "fail" else "WARN"
        by_type: dict[str, list[tuple[Path, str]]] = {}
        for path, type_name, pattern_label in missing_all:
            by_type.setdefault(type_name, []).append((path, pattern_label))
        summary = ", ".join(f"{t}={len(items)}" for t, items in sorted(by_type.items()))
        print(
            f"{level}: {len(missing_all)} source-level match_node(s) in types with declared "
            f"subtypes have no data.subtype ({summary})"
        )
        for type_name, items in sorted(by_type.items()):
            if args.completeness == "fail" or len(items) <= 25:
                for path, pattern_label in items:
                    print(f"  [{type_name}] {path} (patterns: {pattern_label})")
        if args.completeness == "fail":
            return 1

    total_uses = sum(len(v) for v in used.values())
    print(
        f"OK: {total_uses} subtype usage(s) across {len(used)} distinct (type, value) pairs; "
        f"all declared in type-registry.ts and no child-level subtype violations"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
