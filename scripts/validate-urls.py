#!/usr/bin/env python3
"""Validate the scheme (and, for http, the host) of every URL in registry data.

The JSON Schema validator (validate-registry-schema.py) checks structure; it
does NOT check that URLs are https or that their scheme is safe. The registry
is the URL trust root for every resolver (the live Worker, the self-hosted
server, the client SDKs) — a poisoned `url` propagates to whatever a human or
AI agent ultimately navigates to. This pass closes that gap as a blocking CI
gate on the contribution path.

It walks every registry/**/*.json file, finds every URL-bearing value
(`url`, `url_template`, `*_url`, and `wikipedia[]`) anywhere in the tree —
including inside the open-ended `match_nodes[].data` blocks the schema leaves
unconstrained — and enforces:

  * scheme MUST be https, UNLESS the host is in scripts/http-exception-allowlist.txt
    (then http is tolerated for that host only); and
  * javascript:, data:, file:, blob:, vbscript: are ALWAYS rejected.

For values containing a {placeholder} template, only the literal scheme+host
prefix BEFORE the first `{` is validated — a placeholder may fill a path/query
segment but may not supply or move the scheme or host.

Usage:
  python3 scripts/validate-urls.py
  python3 scripts/validate-urls.py --registry-root path/to/registry
  python3 scripts/validate-urls.py --allowlist path/to/allowlist.txt
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from urllib.parse import urlsplit

REJECTED_SCHEMES = frozenset({"javascript", "data", "file", "blob", "vbscript"})
REQUIRED_SCHEME = "https"
URL_KEYS = frozenset({"url", "url_template", "wikipedia"})


def is_url_key(key: str) -> bool:
    return key in URL_KEYS or key.endswith("_url")


def load_allowlist(path: Path) -> set[str]:
    hosts: set[str] = set()
    if not path.is_file():
        return hosts  # absent == empty (https-only, no exceptions)
    for raw in path.read_text().splitlines():
        line = raw.split("#", 1)[0].strip()  # strip inline comments
        if line:
            hosts.add(line.lower())
    return hosts


def literal_prefix(value: str) -> str:
    """The literal portion of a (possibly templated) URL — up to the first '{'."""
    brace = value.find("{")
    return value if brace == -1 else value[:brace]


def check_url(value: str, allowlist: set[str]) -> str | None:
    """Return an error message if `value` is disallowed, else None."""
    parts = urlsplit(literal_prefix(value))
    scheme = parts.scheme.lower()
    if not scheme:
        return f"missing literal scheme (scheme may not be a placeholder): {value!r}"
    if scheme in REJECTED_SCHEMES:
        return f"disallowed scheme {scheme!r}: {value!r}"
    if scheme == REQUIRED_SCHEME:
        return None
    if scheme == "http":
        host = (parts.hostname or "").lower()
        if not host:
            return f"http with no literal host: {value!r}"
        if host in allowlist:
            return None
        return (f"http not allowed for host {host!r} "
                f"(add to http-exception-allowlist.txt only if it is a reviewed "
                f"legacy exception, or upgrade the entry to https): {value!r}")
    return f"scheme {scheme!r} is not https: {value!r}"


def walk(node: object, allowlist: set[str], path: str, out: list[tuple[str, str]]) -> None:
    if isinstance(node, dict):
        for key, val in node.items():
            child = f"{path}.{key}"
            if is_url_key(key):
                if isinstance(val, str):
                    err = check_url(val, allowlist)
                    if err:
                        out.append((child, err))
                elif isinstance(val, list):
                    for i, item in enumerate(val):
                        if isinstance(item, str):
                            err = check_url(item, allowlist)
                            if err:
                                out.append((f"{child}[{i}]", err))
            walk(val, allowlist, child, out)
    elif isinstance(node, list):
        for i, item in enumerate(node):
            walk(item, allowlist, f"{path}[{i}]", out)


def main() -> int:
    ap = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    ap.add_argument("--registry-root", default="registry")
    ap.add_argument("--allowlist", default="scripts/http-exception-allowlist.txt")
    args = ap.parse_args()

    root = Path(args.registry_root)
    if not root.is_dir():
        print(f"ERROR: registry root not found at {root}", file=sys.stderr)
        return 2

    allowlist = load_allowlist(Path(args.allowlist))
    failures: list[tuple[Path, str, str]] = []
    total = 0

    for path in sorted(root.rglob("*.json")):
        if path.stem.startswith("_"):
            continue
        if path.parent == root:  # skip top-level type-description files
            continue
        total += 1
        try:
            doc = json.loads(path.read_text())
        except json.JSONDecodeError:
            continue  # the schema validator owns malformed-JSON reporting
        errors: list[tuple[str, str]] = []
        walk(doc, allowlist, "", errors)
        for json_path, msg in errors:
            failures.append((path, json_path or "<root>", msg))

    if failures:
        print(f"FAIL: {len(failures)} URL policy violation(s) across {total} registry files\n")
        for path, json_path, msg in failures[:40]:
            print(f"  {path} ({json_path}): {msg}")
        if len(failures) > 40:
            print(f"  ... and {len(failures) - 40} more")
        print("\nPolicy: registry URLs must be https. http is allowed only for hosts in")
        print("scripts/http-exception-allowlist.txt. javascript:/data:/file:/blob: never.")
        return 1

    print(f"OK: all URLs in {total} registry files satisfy the scheme/host policy "
          f"({len(allowlist)} http exception host(s) allowlisted)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
