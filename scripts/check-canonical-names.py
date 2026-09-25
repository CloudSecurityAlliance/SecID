#!/usr/bin/env python3
"""Fail on top-level match_nodes whose patterns[0] is not a clean literal.

A resolver has to print a canonical SecID for whatever it matched, and the
registry holds no separate "canonical name" field: SecID-Service derives it from
the first pattern of the name-level node (``extractNameSlug`` in
src/resolver.ts). It strips a leading ``(?i)``, one ``^`` and one ``$``,
unescapes ``\\x`` to ``x``, and accepts the result only if it matches
``^[\\w-]+$``. Anything else falls back to *slugifying the description*, so

    secid:control/iso.org/27006

came back as

    secid:control/iso.org/iso/iec-27006-—-requirements-for-isms-certification-bodies

-- a string that is not a valid SecID and does not resolve. Every variant
spelling a source uses can still be matched; it just has to come *after* a
clean literal that names the thing the way the source does.

Rule (checked on top-level nodes only; children name subpaths, not names):
patterns[0] must be ``^literal$`` or ``(?i)^literal$`` where the literal, after
unescaping, is ASCII letters, digits, ``_`` and ``-``.

Some nodes cannot honestly get a literal: a numbered family matched by one
node (GLI-11, GLI-19), a name that is itself an open identifier (arXiv IDs,
DOIs), or a source name containing '.', which the resolver rejects (ITU-T
X.805). Those are tracked in scripts/canonical-names-todo.json, each needing a
resolver change rather than a registry edit. Tracked nodes are reported but do
not fail; a *stale* entry (node fixed, renamed or removed) fails, so a fix must
delete its entry -- the same contract as pattern-breadth-todo.json.

Usage:
    python3 scripts/check-canonical-names.py             # check registry/
    python3 scripts/check-canonical-names.py PATH ...    # check specific files (todo not applied)
    python3 scripts/check-canonical-names.py --list      # every violation incl. tracked, TSV
    python3 scripts/check-canonical-names.py --self-test

Exit status: 0 clean, 1 untracked violations or stale todo entries.
"""
import json
import re
import sys
from pathlib import Path

REGISTRY = Path(__file__).resolve().parent.parent / "registry"

# Mirrors SecID-Service extractNameSlug(). Keep the two in step.
_LITERAL = re.compile(r"^[A-Za-z0-9_-]+$")
_ANCHORED = re.compile(r"^(?:\(\?i\))?\^(.*)\$$")

TODO = Path(__file__).resolve().parent / "canonical-names-todo.json"


def load_todo():
    doc = json.loads(TODO.read_text())
    return {(e["file"], e["pattern"]): e["category"] for e in doc["entries"]}


def clean_literal(pattern):
    """Return the canonical name SecID-Service would derive, or None if it would
    fall back to slugifying the description."""
    m = _ANCHORED.match(pattern or "")
    if not m:
        return None
    body = re.sub(r"\\(.)", r"\1", m.group(1))
    return body.lower() if _LITERAL.match(body) else None


def violations(doc):
    for i, node in enumerate(doc.get("match_nodes") or []):
        pats = node.get("patterns") or [""]
        if clean_literal(pats[0]) is None:
            yield i, pats[0], node.get("description", "")


def registry_files():
    return sorted(p for p in REGISTRY.rglob("*.json")
                  if p.parent != REGISTRY
                  and not any(part.startswith("_") for part in p.relative_to(REGISTRY).parts))


def self_test():
    cases = [
        ("(?i)^27006$", "27006"),
        ("(?i)^cna\\-tlr$", "cna-tlr"),
        ("^CVE$", "cve"),
        ("(?i)^gb-t-22239$", "gb-t-22239"),
        ("(?i)^(27006|iso-27006)$", None),
        ("(?i)^iso[/ ]?iec[- ]?27006$", None),
        ("(?i)^sp-800\\.53$", None),       # a dot survives unescaping; not \w
        ("27006", None),                    # unanchored
        ("^\\d{4}\\.\\d{4,5}$", None),
    ]
    bad = [(p, want, clean_literal(p)) for p, want in cases if clean_literal(p) != want]
    for p, want, got in bad:
        print(f"  FAIL {p!r}: want {want!r}, got {got!r}")
    print("self-test:", "FAIL" if bad else f"PASS ({len(cases)} cases)")
    return 1 if bad else 0


def main(argv):
    if "--self-test" in argv:
        return self_test()
    as_list = "--list" in argv
    args = [a for a in argv if not a.startswith("--")]
    files = [Path(a) for a in args] or registry_files()
    # The todo only applies to a whole-registry run; staleness is undecidable otherwise.
    todo = {} if (args or as_list) else load_todo()
    seen = set()
    tracked = {}
    total = 0
    for f in files:
        try:
            doc = json.loads(f.read_text())
        except Exception as e:
            print(f"SKIP {f}: {e}")
            continue
        try:
            rel = str(f.resolve().relative_to(REGISTRY.parent))
        except ValueError:
            rel = str(f)
        for i, pat, desc in violations(doc):
            if (rel, pat) in todo:
                seen.add((rel, pat))
                tracked[todo[(rel, pat)]] = tracked.get(todo[(rel, pat)], 0) + 1
                continue
            total += 1
            if as_list:
                print(f"{rel}\t{i}\t{pat}\t{desc}")
            else:
                print(f"FAIL {rel}: match_nodes[{i}] patterns[0] = {pat!r}\n"
                      f"     not a clean literal; canonical name would be slugified from: {desc[:80]!r}")
    if as_list:
        return 1 if total else 0
    stale = sorted(set(todo) - seen)
    for f, pat in stale:
        print(f"STALE {f}: {pat!r} is no longer a violation (fixed, renamed or removed); "
              f"delete its entry from {TODO.name}")
    if tracked:
        summary = ", ".join(f"{n} {c}" for c, n in sorted(tracked.items()))
        print(f"tracked in {TODO.name} (need resolver changes, not failing): {summary}")
    if total or stale:
        if total:
            print(f"\n{total} top-level node(s) lack a clean-literal patterns[0]. "
                  f"Insert the source's own short name first, e.g. \"(?i)^27006$\", "
                  f"and keep the variant regexes after it.")
        return 1
    print(f"OK: {len(files)} file(s); every untracked top-level patterns[0] is a clean literal.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
