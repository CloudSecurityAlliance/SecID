#!/usr/bin/env python3
"""Rank every registry pattern by how much of the registry's own example corpus
it swallows. Report only — this never fails a build.

The companion gate, scripts/check-pattern-breadth.py, answers a yes/no question
against a curated probe set. This answers a different one: given every real
identifier the registry already documents in its `examples` fields, which
patterns are the widest nets? That is the worklist for tightening, not a list of
defects — several patterns are legitimately broad. Red Hat Bugzilla IDs really
are bare integers, so `^\\d+$` matching every numeric example is correct.

Read the output as "these deserve a look", never as "these are wrong".

Usage:
    python3 scripts/audit-pattern-breadth.py             # top 25
    python3 scripts/audit-pattern-breadth.py --top 60
    python3 scripts/audit-pattern-breadth.py --json
    python3 scripts/audit-pattern-breadth.py --min-hits 20
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def compile_pattern(pat: str):
    try:
        return re.compile(pat[4:], re.IGNORECASE) if pat.startswith("(?i)") else re.compile(pat)
    except re.error:
        return None


def collect():
    """Return (corpus, patterns) harvested from every registry namespace file."""
    corpus: dict[str, str] = {}          # identifier -> owning namespace
    patterns: list[dict] = []
    for path in sorted((REPO_ROOT / "registry").rglob("*.json")):
        if path.name.startswith("_"):
            continue
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not isinstance(doc, dict) or "match_nodes" not in doc:
            continue
        ns, typ = doc.get("namespace"), doc.get("type")
        rel = str(path.relative_to(REPO_ROOT))

        def walk(nodes):
            for node in nodes or []:
                data = node.get("data") or {}
                for pat in node.get("patterns") or []:
                    patterns.append({
                        "pattern": pat, "namespace": ns, "type": typ, "file": rel,
                        "description": (node.get("description") or "")[:70],
                        "open_pattern": node.get("open_pattern") is True,
                        "known_values": len(data.get("known_values") or {}) or None,
                    })
                for ex in data.get("examples") or []:
                    val = ex.get("input") if isinstance(ex, dict) else ex
                    if isinstance(val, str) and val.strip():
                        corpus.setdefault(val, ns)
                walk(node.get("children"))

        walk(doc.get("match_nodes"))
    return corpus, patterns


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--top", type=int, default=25, help="rows to show (default 25)")
    ap.add_argument("--min-hits", type=int, default=0, help="only show patterns above this")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    corpus, patterns = collect()
    ids = list(corpus)

    rows = []
    for p in patterns:
        rx = compile_pattern(p["pattern"])
        if rx is None:
            continue
        # count identifiers owned by OTHER namespaces — matching your own
        # examples is the point; matching everyone else's is the signal.
        foreign = [i for i in ids if corpus[i] != p["namespace"] and rx.search(i)]
        rows.append({**p, "foreign_hits": len(foreign),
                     "share": round(len(foreign) / len(ids), 4),
                     "sample": sorted(foreign)[:6]})
    rows.sort(key=lambda r: -r["foreign_hits"])
    rows = [r for r in rows if r["foreign_hits"] >= args.min_hits]

    if args.json:
        print(json.dumps({"corpus_size": len(ids), "patterns": len(patterns),
                          "rows": rows[: args.top]}, indent=2))
        return 0

    print(f"Corpus: {len(ids)} unique identifiers harvested from registry examples.")
    print(f"Patterns examined: {len(patterns)}.\n")
    print("Ranked by how many identifiers belonging to OTHER namespaces a pattern")
    print("matches. Legitimately broad patterns appear here too — this is a")
    print("worklist, not a defect list.\n")
    print(f"{'hits':>5} {'share':>7}  {'flags':<12} namespace / pattern")
    print("-" * 100)
    for r in rows[: args.top]:
        flags = []
        if r["open_pattern"]:
            flags.append("open")
        if r["known_values"]:
            flags.append(f"kv:{r['known_values']}")
        print(f"{r['foreign_hits']:>5} {r['share']:>7.1%}  {','.join(flags) or '-':<12} "
              f"{(r['type'] or '?')+'/'+(r['namespace'] or '?')}")
        print(f"{'':>27}{r['pattern'][:70]}")
        if r["sample"]:
            print(f"{'':>27}e.g. {', '.join(r['sample'])}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
