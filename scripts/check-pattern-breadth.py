#!/usr/bin/env python3
"""Fail the build when a registry match_node pattern is overly broad.

A pattern is the registry's only mechanism for saying "no". A permissive regex
does not defer the claim that an identifier is valid — it asserts the opposite,
which removes the resolver's ability to answer not_found and lets one namespace
fabricate results for every query in the system. Searching "ismap" once returned
19 results, all of them invented by patterns like ^.+$ and ^[a-z]+(-[a-z]+)*$.

Two rules, both derived from that incident:

  1. NONSENSE — a pattern must not match a token no scheme would ever issue.
  2. CROSS-CLASS — a pattern must not match identifiers of more than
     `max_groups` unrelated shape classes.

Legitimate cross-source overlap is unaffected. Every CVE-shaped probe lives in
one group, so a CVE pattern scores 1 no matter how many namespaces publish CVE
data — which is exactly the cross-source resolution SecID exists to provide.

A node may be exempt in two ways:

  * `"open_pattern": true` on the node — the identifier space is genuinely
    unbounded (GitHub usernames, conference paper slugs) and this was reviewed.
  * `data.known_values` larger than MAX_ENUMERABLE AND an open pattern — the set
    is too big to inline (CSA's 1131 artifact slugs), so the resolver closes it
    instead. A SMALL enumeration earns no exemption at all: if the values can be
    listed, the pattern must be that list.

That second condition is narrower than it first appears, and deliberately so.
Blanket-exempting `known_values` left a gap — `^[A-Z&]{2,3}$` is loose enough to
admit FOO but not loose enough to count as open, so nothing enforced the 17
enumerated CCM domains and secid:control/FOO returned seven fabricated results
in production.

Usage:
    python3 scripts/check-pattern-breadth.py            # check the registry
    python3 scripts/check-pattern-breadth.py --json      # machine-readable
    python3 scripts/check-pattern-breadth.py --self-test # verify the detector
    python3 scripts/check-pattern-breadth.py --ref REV   # check a git revision

Exit code 0 when clean, 1 when any violation is found.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PROBES_PATH = Path(__file__).resolve().parent / "pattern-probes.json"
TODO_PATH = Path(__file__).resolve().parent / "pattern-breadth-todo.json"

# An enumeration at or below this size must be expressed IN the pattern, as an
# alternation. Only larger sets may lean on known_values plus an open pattern —
# CSA's 1131 artifact slugs are not going into a regex, but 17 CCM domains are.
# If you have the list, use the list: an enumerated pattern discriminates on its
# own and does not depend on a resolver honouring known_values.
MAX_ENUMERABLE = 50


def load_probes(path: Path = PROBES_PATH) -> tuple[dict[str, list[str]], set[str], int]:
    """Return (group -> probes, fatal group names, max_groups)."""
    spec = json.loads(path.read_text(encoding="utf-8"))
    groups: dict[str, list[str]] = {}
    fatal: set[str] = set()
    for name, body in spec["groups"].items():
        groups[name] = list(body["probes"])
        if body.get("fatal"):
            fatal.add(name)
    return groups, fatal, int(spec.get("max_groups", 2))


def compile_pattern(pat: str) -> re.Pattern | None:
    """Compile a registry pattern the way the resolver does.

    SecID-Service strips a leading (?i) into a JS 'i' flag and calls
    RegExp.test(), which is UNANCHORED. Mirroring both is what makes this check
    agree with production; using re.match here would silently miss patterns that
    match inside a longer string.
    """
    try:
        if pat.startswith("(?i)"):
            return re.compile(pat[4:], re.IGNORECASE)
        return re.compile(pat)
    except re.error:
        return None


def iter_nodes(nodes, path=()):
    """Yield (node, path-of-ancestor-descriptions) depth-first."""
    for node in nodes or []:
        label = (node.get("patterns") or ["?"])[0]
        yield node, path
        yield from iter_nodes(node.get("children"), path + (label,))


def is_open(patterns: list[str], groups: dict[str, list[str]], fatal: set[str]) -> bool:
    """Does this pattern set accept tokens no scheme would issue?

    This is the same test resolvers use to decide whether `known_values` closes a
    node, so the two must agree — see SecID-Service src/resolver.ts isOpenPattern.
    """
    tokens = [t for g in fatal for t in groups.get(g, [])]
    for pat in patterns:
        rx = compile_pattern(pat)
        if rx and any(rx.search(t) for t in tokens):
            return True
    return False


def is_exempt(node: dict, groups, fatal) -> str | None:
    """Return the exemption reason, or None if the node must satisfy the rules.

    `known_values` is NOT a blanket exemption. Resolvers treat an enumeration as
    a closed set only where the pattern is open, because a tight pattern is
    assumed to be doing real validation. That leaves a gap this check used to
    share: a pattern loose enough to admit garbage but not loose enough to count
    as open — nothing enforced the enumeration, and secid:control/FOO resolved to
    seven fabricated results while every one of those nodes was "exempt".

    So an enumeration excuses a pattern only when the resolver would actually
    enforce it. Otherwise the pattern must stand on its own, which for an
    enumerable set means being the enumeration.
    """
    if node.get("open_pattern") is True:
        return "open_pattern"
    known = (node.get("data") or {}).get("known_values")
    patterns = node.get("patterns") or []
    if known and len(known) > MAX_ENUMERABLE and is_open(patterns, groups, fatal):
        return "known_values+open"
    return None


def load_todo() -> list[dict]:
    """Known-broad patterns awaiting research. Debt, not permission."""
    if not TODO_PATH.exists():
        return []
    return json.loads(TODO_PATH.read_text(encoding="utf-8")).get("entries", [])


def todo_key(d: dict) -> tuple:
    return (d.get("type"), d.get("namespace"), d.get("pattern"))


def check_pattern(pat: str, groups, fatal, max_groups) -> dict | None:
    """Return a violation dict, or None if the pattern is acceptable."""
    rx = compile_pattern(pat)
    if rx is None:
        return {"kind": "invalid-regex", "pattern": pat, "matched": []}

    hit_groups: dict[str, list[str]] = {}
    for name, probes in groups.items():
        matched = [p for p in probes if rx.search(p)]
        if matched:
            hit_groups[name] = matched

    fatal_hits = sorted(set(hit_groups) & fatal)
    if fatal_hits:
        return {
            "kind": "nonsense",
            "pattern": pat,
            "groups": fatal_hits,
            "matched": sorted({m for g in fatal_hits for m in hit_groups[g]}),
        }

    if len(hit_groups) > max_groups:
        return {
            "kind": "cross-class",
            "pattern": pat,
            "groups": sorted(hit_groups),
            "matched": sorted({m for ms in hit_groups.values() for m in ms}),
        }
    return None


def registry_files(ref: str | None):
    """Yield (display_path, parsed_json) for every registry namespace file."""
    if ref:
        listing = subprocess.run(
            ["git", "ls-tree", "-r", "--name-only", ref, "registry/"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=True,
        ).stdout.split()
        for rel in listing:
            if not rel.endswith(".json") or Path(rel).name.startswith("_"):
                continue
            blob = subprocess.run(
                ["git", "show", f"{ref}:{rel}"],
                cwd=REPO_ROOT, capture_output=True, text=True, check=True,
            ).stdout
            try:
                yield rel, json.loads(blob)
            except json.JSONDecodeError:
                continue
    else:
        for path in sorted((REPO_ROOT / "registry").rglob("*.json")):
            if path.name.startswith("_"):
                continue
            try:
                yield str(path.relative_to(REPO_ROOT)), json.loads(
                    path.read_text(encoding="utf-8")
                )
            except json.JSONDecodeError:
                continue


def scan(ref: str | None = None):
    """Return (violations, tracked, stale_todo, patterns_checked, exempt_nodes)."""
    groups, fatal, max_groups = load_probes()
    violations: list[dict] = []
    checked = exempt = 0

    for rel, doc in registry_files(ref):
        if not isinstance(doc, dict) or "match_nodes" not in doc:
            continue
        ns, typ = doc.get("namespace"), doc.get("type")
        for node, ancestors in iter_nodes(doc.get("match_nodes")):
            reason = is_exempt(node, groups, fatal)
            if reason:
                exempt += 1
                continue
            for pat in node.get("patterns") or []:
                checked += 1
                bad = check_pattern(pat, groups, fatal, max_groups)
                if bad:
                    bad.update(
                        file=rel, namespace=ns, type=typ,
                        node=(node.get("description") or "")[:80],
                        parent="/".join(ancestors) or None,
                    )
                    violations.append(bad)

    todo = load_todo()
    allowed = {todo_key(t): t for t in todo}
    tracked, fatal_violations = [], []
    for v in violations:
        entry = allowed.get(todo_key(v))
        if entry:
            tracked.append({**v, "tracking": entry.get("tracking"),
                            "reason": entry.get("reason", "")})
        else:
            fatal_violations.append(v)

    # An entry matching nothing means the pattern was fixed but the excuse was
    # left behind. Fail, so the file cannot accumulate stale exemptions.
    seen = {todo_key(v) for v in violations}
    stale = [t for t in todo if todo_key(t) not in seen]

    return fatal_violations, tracked, stale, checked, exempt


# ── Self-test ──────────────────────────────────────────────────────────────

SELF_TEST_CASES = [
    # (pattern, should_be_flagged, why)
    (r"^.+$", True, "matches literally anything"),
    (r"^[a-z]+(-[a-z]+)*$", True, "the catch-all that fabricated the ismap results"),
    (r"^[a-z0-9-]+$", True, "open kebab slug"),
    (r"^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$", True, "open username space"),
    (r"^CVE-\d{4}-\d{4,}$", False, "canonical CVE — one shape class"),
    (r"(?i)^cve$", False, "source name literal"),
    (r"^CWE-\d+$", False, "canonical CWE"),
    (r"^T\d{4}(\.\d{3})?$", False, "ATT&CK technique"),
    (r"^[A-Z]{2}\.[A-Z]{2}-\d+$", False, "NIST CSF subcategory"),
    (r"^\d+(?:\.\d+){1,4}(?:\.(?:PB|P|B))?$", False, "ISMAP — dotted-numeric is one shape"),
    (r"^\d+$", False, "bare numeric IDs are legitimately broad"),
    (r"^RHSA-\d{4}:\d{4,}$", False, "Red Hat errata"),
    # the gap that let secid:control/FOO fabricate seven results: loose enough
    # to admit garbage, not loose enough for a resolver to enforce known_values
    (r"^[A-Z&]{2,3}$", True, "short uppercase wildcard — the CCM/AICM domain gap"),
    (r"^[A-Z]+$", True, "any uppercase run"),
    (r"^[A-Z]{1,3}$", True, "short uppercase wildcard"),
    (r"^(?:A&A|AIS|IAM|IVS)-\d{2}$", False, "enumerated CCM control"),
    (r"^(?:A&A|AIS|IAM|IVS)$", False, "enumerated CCM domain"),
]


def self_test() -> int:
    groups, fatal, max_groups = load_probes()
    failures = 0
    print("self-test: detector behaviour on known patterns\n")
    for pat, expect_flag, why in SELF_TEST_CASES:
        got = check_pattern(pat, groups, fatal, max_groups)
        ok = bool(got) == expect_flag
        mark = "ok  " if ok else "FAIL"
        detail = ""
        if got:
            detail = f"  [{got['kind']}: {', '.join(got.get('groups', []))}]"
        print(f"  {mark} {'flag' if expect_flag else 'pass'}  {pat:<48} {why}{detail}")
        if not ok:
            failures += 1
    print()
    if failures:
        print(f"self-test FAILED: {failures} case(s) behaved unexpectedly")
        return 1
    print(f"self-test passed: {len(SELF_TEST_CASES)} cases")
    return 0


# ── CLI ────────────────────────────────────────────────────────────────────

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--json", action="store_true", help="machine-readable output")
    ap.add_argument("--self-test", action="store_true", help="verify the detector itself")
    ap.add_argument("--ref", help="check a git revision instead of the working tree")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    violations, tracked, stale, checked, exempt = scan(args.ref)

    if args.json:
        print(json.dumps(
            {"checked": checked, "exempt_nodes": exempt,
             "violation_count": len(violations), "violations": violations,
             "tracked_count": len(tracked), "tracked": tracked,
             "stale_todo": stale},
            indent=2,
        ))
        return 1 if (violations or stale) else 0

    where = f"at {args.ref}" if args.ref else "in the working tree"
    print(f"Checked {checked} patterns {where} ({exempt} node(s) exempt).\n")

    if tracked:
        print(f"KNOWN-BROAD, pending research ({len(tracked)}) " + "-" * 34)
        for t in tracked:
            print(f"  {t['type']}/{t['namespace']}  {t['pattern']}")
            print(f"    {t['node']}")
            print(f"    tracking: {t.get('tracking')}")
        print()

    if stale:
        print(f"STALE todo entries ({len(stale)}) " + "-" * 40)
        print("  These match no current violation — the pattern was fixed but the")
        print("  excuse was left behind. Delete them from pattern-breadth-todo.json.")
        for t in stale:
            print(f"    {t.get('type')}/{t.get('namespace')}  {t.get('pattern')}")
        print()

    if violations:
        by_kind: dict[str, list[dict]] = {}
        for v in violations:
            by_kind.setdefault(v["kind"], []).append(v)
        for kind, items in sorted(by_kind.items()):
            print(f"-- {kind} ({len(items)}) " + "-" * 40)
            for v in items:
                print(f"  {v['type']}/{v['namespace']}")
                print(f"    pattern : {v['pattern']}")
                print(f"    node    : {v['node']}")
                if v.get("groups"):
                    print(f"    groups  : {', '.join(v['groups'])}")
                print(f"    matched : {', '.join(v['matched'][:8])}")
                print(f"    file    : {v['file']}")
                print()

    if violations or stale:
        n = len(violations)
        if n:
            print(f"FAIL - {n} overly broad pattern(s).")
            print("Fix by tightening the regex, adding data.known_values, or - if the")
            print('identifier space really is unbounded - setting "open_pattern": true')
            print("on the node with a note explaining why.")
        if stale:
            print(f"FAIL - {len(stale)} stale entry(ies) in pattern-breadth-todo.json.")
        return 1

    suffix = f" ({len(tracked)} tracked exception(s))" if tracked else ""
    print(f"PASS - no untracked overly broad patterns{suffix}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
