#!/usr/bin/env python3
"""Fail on match_nodes whose URL template can never be resolved.

Resolvers build a subpath URL from exactly one field: a node's ``data.url``.
SecID-Service (src/resolver.ts, resolveChildUrl) and SecID-Server-API
(resolver.py) both read ``child.data.url`` and nothing else. A ``{id}``-style
template placed only in ``data.urls[]`` is therefore dead: the resolver reports
the identifier as found and returns no URL at all.

That is how 174 DISA STIG rule nodes (14,150 V-IDs) went live resolving to
nothing. The shape looks right to a reviewer -- ``urls[]`` is the correct field
at the *source* level -- so this check exists to catch it mechanically.

Rule: a subpath-level match_node (any node below the top level) whose
``data.urls[]`` contains a templated URL (one holding ``{``) must also carry
``data.url``. Either move the template to ``data.url`` (the fix almost every
time), or drop the placeholder from ``urls[]``.

Top-level (name-level) nodes are exempt. There, ``urls[]`` is source metadata:
a templated "lookup" entry documents the URL scheme while the node's children
carry the resolvable ``data.url`` (redhat errata, ubuntu usn, ...). The resolver
never builds a URL from a name-level node, so ``data.url`` there would not help.
Name-level nodes whose *pattern is itself the identifier* (arxiv, doi, pubmed)
have a related resolver-side gap -- the ``{id}`` is never substituted -- that no
registry edit can fix; it is tracked separately.

Usage:
    python3 scripts/check-url-templates.py            # check registry/
    python3 scripts/check-url-templates.py PATH ...   # check specific files
    python3 scripts/check-url-templates.py --self-test

Exit status: 0 clean, 1 violations found.
"""
import json
import sys
from pathlib import Path

REGISTRY = Path(__file__).resolve().parent.parent / "registry"


def violations(doc):
    """Yield (node_path, template_url) for every dead template in a registry doc."""
    def walk(nodes, trail):
        for i, node in enumerate(nodes or []):
            pats = node.get("patterns") or ["?"]
            here = trail + [f"{i}:{pats[0]}"]
            data = node.get("data") or {}
            if trail and not data.get("url"):
                for u in data.get("urls") or []:
                    url = u.get("url") if isinstance(u, dict) else u
                    if isinstance(url, str) and "{" in url:
                        yield " > ".join(here), url
                        break
            yield from walk(node.get("children"), here)
    yield from walk(doc.get("match_nodes"), [])


def registry_files():
    # Namespace files only: skip registry/<type>.json descriptions and _deferred/_template.
    return sorted(p for p in REGISTRY.rglob("*.json")
                  if p.parent != REGISTRY
                  and not any(part.startswith("_") for part in p.relative_to(REGISTRY).parts))


def self_test():
    bad = {"match_nodes": [{"patterns": ["(?i)^x$"], "data": {}, "children": [
        {"patterns": ["^V-1$"], "data": {"urls": [{"url": "https://e.test/{id}.json"}]}}]}]}
    good_url = {"match_nodes": [{"patterns": ["(?i)^x$"], "data": {}, "children": [
        {"patterns": ["^V-1$"], "data": {"url": "https://e.test/{id}.json",
                                          "urls": [{"url": "https://e.test/{id}.html"}]}}]}]}
    good_plain = {"match_nodes": [{"patterns": ["(?i)^x$"],
                                   "data": {"urls": [{"url": "https://e.test/"}]}}]}
    top_level = {"match_nodes": [{"patterns": ["(?i)^x$"],
                                  "data": {"urls": [{"url": "https://e.test/{id}"}]}}]}
    ok = (len(list(violations(bad))) == 1
          and not list(violations(good_url))
          and not list(violations(good_plain))
          and not list(violations(top_level)))
    print("self-test:", "PASS" if ok else "FAIL")
    return 0 if ok else 1


def main(argv):
    if "--self-test" in argv:
        return self_test()
    files = [Path(a) for a in argv] or registry_files()
    total = 0
    for f in files:
        try:
            doc = json.loads(f.read_text())
        except Exception as e:  # malformed JSON is the schema validator's job
            print(f"SKIP {f}: {e}")
            continue
        for where, url in violations(doc):
            total += 1
            print(f"FAIL {f}: {where}\n     template only in data.urls[] (no data.url): {url}")
    if total:
        print(f"\n{total} node(s) carry a URL template the resolver will never use. "
              f"Move it to data.url.")
        return 1
    print(f"OK: {len(files)} file(s); no templated URL is stranded in data.urls[].")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
