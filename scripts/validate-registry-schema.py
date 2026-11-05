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
import re
import sys
from pathlib import Path

try:
    import jsonschema
except ImportError:
    print("ERROR: jsonschema not installed. Run: pip install jsonschema", file=sys.stderr)
    sys.exit(2)


_JS_NAMED_GROUP_RE = re.compile(r"\(\?<([A-Za-z_][A-Za-z0-9_]*)>")
_JS_NAMED_BACKREF_RE = re.compile(r"\\k<([A-Za-z_][A-Za-z0-9_]*)>")


def _compile_node_pattern(pat: str) -> re.Pattern[str] | None:
    """Compile a registry pattern using ECMAScript-compatible semantics.

    Strips a leading (?i) flag (matching SecID-Service's toRegExp) and translates
    ECMAScript named capture groups (?<name>...) / backreferences \\k<name> into
    Python's (?P<name>...) / (?P=name) syntax.
    """
    flags = 0
    if pat.startswith("(?i)"):
        flags |= re.IGNORECASE
        pat = pat[4:]
    pat = _JS_NAMED_GROUP_RE.sub(r"(?P<\1>", pat)
    pat = _JS_NAMED_BACKREF_RE.sub(r"(?P=\1)", pat)
    try:
        return re.compile(pat, flags)
    except re.error:
        return None


def check_lowercase_namespace_and_path(path: Path, doc: dict) -> list[str]:
    """Ensure namespace and filename stem are lowercase (preserving Unicode IDNs per SPEC.md §4.2).

    SecID-Service indexes registry files by verbatim `doc["namespace"]` and normalizes
    incoming queries to lowercase, so any uppercase character (ASCII or Unicode) in
    `namespace` makes the entry unreachable at runtime.
    """
    errs: list[str] = []
    ns = doc.get("namespace")
    if isinstance(ns, str) and ns != ns.lower():
        errs.append(f"namespace {ns!r} must be lowercase ({ns.lower()!r})")
    if path.stem != path.stem.lower():
        errs.append(f"filename stem {path.stem!r} must be lowercase ({path.stem.lower()!r})")
    return errs


def check_child_examples(doc: dict) -> list[str]:
    """Ensure every child/grandchild ExampleObject.input matches its node's patterns[].

    SecID-Service's test/resolver.test.ts builds a fixture query for every
    structured ExampleObject ({input, url}) on child/grandchild nodes as:
        secid:<type>/<ns>/<name>[@<version>]#<ex.input>
    If ex.input includes a '<name>#' prefix or otherwise fails to match the
    child node's patterns[], the resolver returns status='related' instead of
    'found' and blocks KV deployment.
    """
    errs: list[str] = []

    def walk(nodes: list[dict] | None, depth: int = 0, trail: tuple[str, ...] = ()) -> None:
        for node in nodes or []:
            pats = node.get("patterns") or ["?"]
            here = trail + (pats[0],)
            if depth > 0:
                examples = [
                    ex
                    for ex in ((node.get("data") or {}).get("examples") or [])
                    if isinstance(ex, dict) and isinstance(ex.get("input"), str)
                ]
                if examples:
                    compiled = [c for p in (node.get("patterns") or []) if (c := _compile_node_pattern(p)) is not None]
                    for ex in examples:
                        inp = ex["input"]
                        if not any(r.search(inp) for r in compiled):
                            loc = " > ".join(here)
                            errs.append(
                                f"{loc}: child example input {inp!r} does not match node patterns {pats}"
                            )
            walk(node.get("children"), depth + 1, here)

    walk(doc.get("match_nodes"))
    return errs


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
            continue
        case_errors = check_lowercase_namespace_and_path(path, doc)
        if case_errors:
            failures.append((path, case_errors[0][:200]))
            continue
        child_ex_errors = check_child_examples(doc)
        if child_ex_errors:
            failures.append((path, child_ex_errors[0][:200]))

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
