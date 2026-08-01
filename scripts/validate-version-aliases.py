#!/usr/bin/env python3
"""Validate version metadata and version aliases across registry JSON files.

Two layers have to agree, and this script is what makes them agree.

  The TREE matches. A versioned source has version-level nodes between its
  name node and its item nodes. `patterns` is an OR-list, so a version node's
  canonical string and its aliases are alternatives on one node:
      {"patterns": ["^1\\.1\\.0$", "^1\\.1$"], "children": [...]}
  patterns[0] is canonical.

  versions_available DESCRIBES. Release dates, status, notes and per-alias
  on_match cannot be derived from a regex, so they are hand-authored.

JSON Schema cannot enforce any of this: versions_available lives inside
match_nodes[].data, and data is additionalProperties:true by design, so a
$ref there is unreachable. The schema's $defs/VersionEntry and
$defs/VersionAlias are the documented shape; this script is the constraint.
Same split the $defs/Tags docstring already describes for data.tags.

Metadata rules, per source:
  1. every versions_available entry has a non-empty string `version`
  2. version strings are unique within the source
  3. every alias has a non-empty `label` and an `on_match` of resolve|redirect
  4. alias labels are unique within the source
  5. an alias label never equals a real version string in the same source

Binding rules, per source:
  6. every declared version has a version node whose patterns[0] equals it
  7. every version node's patterns[0] is a clean literal (no optional groups —
     otherwise there is nothing to canonicalize to)
  8. every version node has a versions_available entry
  9. every declared alias label appears as a pattern on its version node
 10. a source that declares aliases must have version-level tree nodes at all,
     since an alias with no node is documentation that never resolves

Rule 5 is the one that catches real mistakes: CSA's CCM 4.0 is a genuine
release that 4.0.13 supersedes, so aliasing 4.0 -> 4.0.13 would silently
repoint a real version.

Absent or null versions_available is valid — per the null-vs-absent
convention, absent means "not yet researched" and null means "researched,
found nothing".

Skips (matching scripts/validate-registry-schema.py):
  - files whose name starts with `_` (templates, _deferred entries)
  - top-level registry/<type>.json files (type descriptions, not namespaces)

Usage:
    python3 scripts/validate-version-aliases.py
    python3 scripts/validate-version-aliases.py --registry-root path/to/registry
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_ON_MATCH = ("resolve", "redirect")
_REGEX_META = set("[](){}*+?|.")


def pattern_literal(pattern: str) -> str | None:
    """Return the literal string a pattern matches, or None if it is a real regex.

    "^1\\.1\\.0$" -> "1.1.0";  "(?i)^aicm$" -> "aicm";  "^[A-Z]{2}$" -> None.
    Escaped characters are unescaped; any unescaped metacharacter disqualifies
    the pattern, which is what rejects CVSS-style "^2(\\.0)?$".
    """
    if not isinstance(pattern, str):
        return None
    core = pattern[4:] if pattern.startswith("(?i)") else pattern
    core = core[1:] if core.startswith("^") else core
    core = core[:-1] if core.endswith("$") else core
    out: list[str] = []
    i = 0
    while i < len(core):
        ch = core[i]
        if ch == "\\":
            if i + 1 >= len(core):
                return None
            out.append(core[i + 1])
            i += 2
            continue
        if ch in _REGEX_META:
            return None
        out.append(ch)
        i += 1
    return "".join(out) or None


def node_label(node: dict) -> str:
    """Best-effort readable source name from a match_node's first pattern."""
    patterns = node.get("patterns") or []
    if not patterns or not isinstance(patterns[0], str):
        return "<unnamed>"
    return pattern_literal(patterns[0]) or patterns[0]


def check_source_versions(versions_available, source_label: str) -> list[str]:
    """Metadata-internal rules 1-5. Returns a list of error strings."""
    if versions_available is None:
        return []
    if not isinstance(versions_available, list):
        return [f"{source_label}: versions_available must be an array or null"]

    errors: list[str] = []
    seen_versions: set[str] = set()

    for i, entry in enumerate(versions_available):
        where = f"{source_label}: versions_available[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be an object")
            continue
        version = entry.get("version")
        if not isinstance(version, str) or not version.strip():
            errors.append(f"{where}: missing required non-empty string 'version'")
            continue
        if version in seen_versions:
            errors.append(f"{where}: duplicate version {version!r}")
        seen_versions.add(version)

    # Second pass so rule 5 can see versions declared after the alias.
    seen_labels: dict[str, str] = {}
    for i, entry in enumerate(versions_available):
        if not isinstance(entry, dict):
            continue
        aliases = entry.get("aliases")
        if aliases is None:
            continue
        version = entry.get("version")
        prefix = f"{source_label}: versions_available[{i}] ({version})"
        if not isinstance(aliases, list):
            errors.append(f"{prefix}: aliases must be an array")
            continue
        for j, alias in enumerate(aliases):
            where = f"{prefix} aliases[{j}]"
            if not isinstance(alias, dict):
                errors.append(f"{where}: must be an object")
                continue
            label = alias.get("label")
            if not isinstance(label, str) or not label.strip():
                errors.append(f"{where}: missing required non-empty string 'label'")
                continue
            if alias.get("on_match") not in VALID_ON_MATCH:
                errors.append(
                    f"{where}: 'on_match' must be one of {VALID_ON_MATCH}, "
                    f"got {alias.get('on_match')!r}"
                )
            if label in seen_versions:
                errors.append(
                    f"{where}: alias label {label!r} is also a real version in this "
                    f"source — aliases must never shadow a real version"
                )
            if label in seen_labels:
                errors.append(
                    f"{where}: duplicate alias label {label!r} "
                    f"(already used by version {seen_labels[label]})"
                )
            else:
                seen_labels[label] = str(version)
    return errors


def _pattern_matches(pattern: str, value: str) -> bool:
    """Does this regex match this exact string? Invalid regexes never match."""
    if not isinstance(pattern, str):
        return False
    try:
        return re.fullmatch(pattern, value) is not None
    except re.error:
        return False


def _looks_versionish(s: str) -> bool:
    """Heuristic, used only to report an undeclared version-shaped node."""
    core = s[1:] if s[:1] in "vV" else s
    return bool(core) and all(ch.isdigit() or ch == "." for ch in core)


def check_tree_binding(source_node: dict, source_label: str) -> list[str]:
    """Binding rules 6-10: the tree and versions_available must agree.

    Version nodes are identified by MATCHING, not by literal comparison: a child
    is the node for version V if any of its patterns matches V. That is what lets
    this bind a non-literal pattern such as CVSS's ^2(\\.0)?$ to its declared
    version "2" — and then correctly report that its patterns[0] is not a clean
    canonical literal.
    """
    data = source_node.get("data") or {}
    versions_available = data.get("versions_available")
    if not isinstance(versions_available, list) or not versions_available:
        return []

    declared: dict[str, dict] = {}
    for entry in versions_available:
        if isinstance(entry, dict) and isinstance(entry.get("version"), str):
            declared[entry["version"]] = entry

    children = [c for c in (source_node.get("children") or []) if isinstance(c, dict)]

    # A child is the node for version V only if its patterns[0] is the clean
    # literal V. Matching alone is NOT enough: CIS safeguard IDs (8.1) and PCI
    # requirement IDs (1.2) are item patterns that happen to match version
    # strings, and binding by match flags them as version nodes — 5 false
    # positives across cisecurity.org and pcisecuritystandards.org.
    version_nodes: dict[str, dict] = {}
    for child in children:
        pats = [p for p in (child.get("patterns") or []) if isinstance(p, str)]
        if not pats:
            continue
        lit = pattern_literal(pats[0])
        if lit is not None and lit in declared:
            version_nodes[lit] = child

    errors: list[str] = []
    any_aliases = any(e.get("aliases") for e in declared.values())

    if not version_nodes:
        if any_aliases:
            errors.append(
                f"{source_label}: declares version aliases but has no version-level tree "
                f"nodes — the aliases would never resolve. Add version nodes, or drop the "
                f"aliases until the tree is restructured."
            )
        # Metadata-only versions with no aliases are valid documentation.
        return errors

    for version, entry in declared.items():
        node = version_nodes.get(version)
        if node is None:
            errors.append(
                f"{source_label}: version {version!r} is declared in versions_available "
                f"but has no version node in the tree"
            )
            continue

        patterns = [p for p in (node.get("patterns") or []) if isinstance(p, str)]

        # Rule 7: patterns[0] must be the clean canonical literal.
        first = patterns[0] if patterns else None
        if first is None or pattern_literal(first) != version:
            errors.append(
                f"{source_label}: version node for {version!r} has patterns[0] {first!r}, "
                f"which is not the clean canonical literal — there is nothing to "
                f"canonicalize to. Write separate OR-patterns, not an optional group."
            )

        # Rule 9: every declared alias must actually match on this node.
        for alias in entry.get("aliases") or []:
            if not isinstance(alias, dict):
                continue
            label = alias.get("label")
            if not isinstance(label, str):
                continue
            if not any(_pattern_matches(p, label) for p in patterns):
                errors.append(
                    f"{source_label}: alias {label!r} on version {version!r} is not a "
                    f"pattern on that version node — it would never match"
                )

    # Rule 8, reverse direction: a version-shaped child bound to no declared version.
    bound = {id(n) for n in version_nodes.values()}
    for child in children:
        if id(child) in bound:
            continue
        patterns = [p for p in (child.get("patterns") or []) if isinstance(p, str)]
        if not patterns:
            continue
        lit = pattern_literal(patterns[0])
        if lit is None:
            continue  # a genuine item pattern such as ^[A-Z&]{2,3}-\d{2}$
        if _looks_versionish(lit):
            errors.append(
                f"{source_label}: version node {lit!r} is not declared in versions_available"
            )
    return errors


def check_source(source_node: dict) -> list[str]:
    """Run both layers for one source node."""
    label = node_label(source_node)
    data = source_node.get("data") or {}
    errs = check_source_versions(data.get("versions_available"), label)
    errs += check_tree_binding(source_node, label)
    return errs


def iter_namespace_files(registry_root: Path):
    for path in sorted(registry_root.rglob("*.json")):
        if path.name.startswith("_"):
            continue
        if path.parent == registry_root:
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--registry-root", default="registry")
    args = parser.parse_args()

    root = Path(args.registry_root)
    if not root.is_dir():
        print(f"ERROR: registry root not found: {root}", file=sys.stderr)
        return 2

    files = sources = 0
    failures: list[str] = []
    for path in iter_namespace_files(root):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(doc, dict) or "match_nodes" not in doc:
            continue
        files += 1
        for node in doc.get("match_nodes") or []:
            if not isinstance(node, dict):
                continue
            data = node.get("data") or {}
            if "versions_available" not in data:
                continue
            sources += 1
            for err in check_source(node):
                failures.append(f"{path}: {err}")

    print(f"Checked {files} namespace files, {sources} sources declaring versions_available.")
    if failures:
        print(f"\n{len(failures)} violation(s):\n")
        for f in failures[:30]:
            print(f"  {f}")
        if len(failures) > 30:
            print(f"  ... and {len(failures) - 30} more")
        return 1
    print("All version/alias entries valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
