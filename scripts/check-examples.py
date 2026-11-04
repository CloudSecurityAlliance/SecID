#!/usr/bin/env python3
"""Validate child/grandchild examples and their expected URLs across registry/.

In SecID's registry, child and grandchild ``match_nodes`` carry ``data.examples``
that serve as executable test fixtures for both the grammar (``patterns``) and
URL resolution (``data.url`` templates with ``{id}``, ``{id_lower}``,
``{id_upper}``, ``variables`` regex extractors, ``lang``, or
``data.lookup_table`` maps).

Before this script, ``SecID-Service/test/resolver.test.ts`` tested ``ExampleObject``
entries only inside the service repository after a merge, and silently skipped any
``ExampleObject`` that omitted ``url`` (such as 5 article examples in
``registry/regulation/jp/go/ppc.json``). Running this validator in ``SecID`` CI
catches mismatches at PR time before registry changes ever merge.

Offline rules (default mode, wired into CI):
  1. Every child/grandchild example (string or ``ExampleObject``) must have a
     non-empty input string that matches at least one regex in its node's
     ``patterns``.
  2. On any child/grandchild node that carries ``data.url`` or
     ``data.lookup_table``, every ``ExampleObject`` must include a non-empty
     ``url`` string (so fixtures on resolvable nodes cannot silently skip URL
     assertion).
  3. On any ``ExampleObject`` that includes ``url``, the node must carry
     ``data.url`` or ``data.lookup_table``, and expanding the node's template or
     lookup table for ``input`` must produce ``example["url"]`` exactly.

Live mode (``--live``, opt-in network probe):
  Deduplicates ``example["url"]`` values across the target files, verifies each
  host and redirect target with ``_net_guard`` (SSRF protection), and issues an
  HTTP HEAD/GET probe to report dead or unreachable fixture URLs.

Usage:
    python3 scripts/check-examples.py                  # offline check across registry/
    python3 scripts/check-examples.py PATH ...         # offline check on specific files
    python3 scripts/check-examples.py --self-test      # run built-in unit tests
    python3 scripts/check-examples.py --live PATH ...  # live HTTP probe on specific files

Exit status: 0 clean, 1 violations found.
"""

from __future__ import annotations

import argparse
import concurrent.futures
import json
import re
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

REGISTRY = Path(__file__).resolve().parent.parent / "registry"

_JS_NAMED_GROUP_RE = re.compile(r"\(\?<([A-Za-z_][A-Za-z0-9_]*)>")
_JS_NAMED_BACKREF_RE = re.compile(r"\\k<([A-Za-z_][A-Za-z0-9_]*)>")

_UNSAFE_IN: dict[str, re.Pattern[str]] = {
    "path": re.compile(r"[?#%\\\s\x00-\x1f\x7f]"),
    "query": re.compile(r"[#&+%\\\s\x00-\x1f\x7f]"),
    "fragment": re.compile(r"[#%\\\s\x00-\x1f\x7f]"),
}
_DOT_SEGMENT_RE = re.compile(r"(^|/)\.{1,2}(/|$)")
_PLACEHOLDER_RE = re.compile(r"\{([^{}]*)\}")


def _compile_ecmascript_regex(pat: str) -> re.Pattern[str]:
    """Compile a registry pattern using SecID-Service's toRegExp + ECMAScript named-group syntax."""
    flags = 0
    if pat.startswith("(?i)"):
        flags |= re.IGNORECASE
        pat = pat[4:]
    pat = _JS_NAMED_GROUP_RE.sub(r"(?P<\1>", pat)
    pat = _JS_NAMED_BACKREF_RE.sub(r"(?P=\1)", pat)
    return re.compile(pat, flags)


def _encode_for_part(value: str, part: str) -> str:
    """Mirror SecID-Service encodeForPart(value, part)."""
    return _UNSAFE_IN[part].sub(
        lambda m: "".join(f"%{b:02X}" for b in m.group(0).encode("utf-8")),
        value,
    )


def _build_url(template: str, variables: dict[str, str]) -> str | None:
    """Mirror SecID-Service buildUrl(template, variables)."""
    try:
        tpl_parsed = urllib.parse.urlsplit(_PLACEHOLDER_RE.sub("x", template))
    except ValueError:
        return None
    if tpl_parsed.scheme not in ("https", "http") or not tpl_parsed.netloc:
        return None

    query_at = template.find("?")
    fragment_at = template.find("#")

    def part_at(offset: int) -> str:
        if fragment_at != -1 and offset > fragment_at:
            return "fragment"
        if query_at != -1 and offset > query_at and (fragment_at == -1 or query_at < fragment_at):
            return "query"
        return "path"

    unsafe = False

    def repl(m: re.Match[str]) -> str:
        nonlocal unsafe
        key = m.group(1)
        if key not in variables:
            return m.group(0)
        val = variables[key]
        part = part_at(m.start())
        if part == "path" and _DOT_SEGMENT_RE.search(val):
            unsafe = True
        return _encode_for_part(val, part)

    url = _PLACEHOLDER_RE.sub(repl, template)
    if unsafe:
        return None

    try:
        res_parsed = urllib.parse.urlsplit(url)
    except ValueError:
        return None
    if res_parsed.scheme != tpl_parsed.scheme or res_parsed.netloc != tpl_parsed.netloc:
        return None
    return url


def registry_files() -> list[Path]:
    """Return all namespace JSON files under registry/ (excluding _* and top-level type files)."""
    return sorted(
        p
        for p in REGISTRY.rglob("*.json")
        if p.parent != REGISTRY
        and not any(part.startswith("_") for part in p.relative_to(REGISTRY).parts)
    )


def _lookup_range_table(number: int, notes: str | None) -> str | None:
    """Mirror SecID-Service lookupRangeTable(number, notes)."""
    if not notes:
        return None
    pairs: list[tuple[str, int]] = []
    for m in re.finditer(r"(\d{4}):\s*(\d+)", notes):
        pairs.append((m.group(1), int(m.group(2))))
    if not pairs:
        return None
    pairs.sort(key=lambda item: item[1])
    result: str | None = None
    for year, start in pairs:
        if start <= number:
            result = year
        else:
            break
    return result


def _extract_lookup_url(val: object) -> str | None:
    if isinstance(val, str):
        return val
    if isinstance(val, dict) and isinstance(val.get("url"), str):
        return val["url"]
    return None


def expand_child_url(
    data: dict, inp: str, parent_notes: str | None = None
) -> tuple[str | None, str | None]:
    """Mirror SecID-Service resolveChildUrl(child, target, parentNode) for a single node's data.

    Returns ``(resolved_url, error_reason)``.
    """
    url_tpl = data.get("url")
    if isinstance(url_tpl, str) and url_tpl:
        if "{" not in url_tpl:
            return url_tpl, None

        resolved_vars: dict[str, str] = {}
        variables = data.get("variables")
        if isinstance(variables, dict):
            for var_name, var_def in variables.items():
                if not isinstance(var_def, dict):
                    continue
                extract_pat = var_def.get("extract")
                if not isinstance(extract_pat, str):
                    return None, f"variable {var_name!r} missing string 'extract' regex"
                try:
                    compiled_extract = _compile_ecmascript_regex(extract_pat)
                    m = compiled_extract.search(inp)
                except re.error as exc:
                    return None, f"variable {var_name!r} has invalid regex {extract_pat!r}: {exc}"
                if not m or m.lastindex is None or m.group(1) is None:
                    return (
                        None,
                        f"variable {var_name!r} extract regex {extract_pat!r} did not capture group(1) on {inp!r}",
                    )
                val = m.group(1)
                fmt = var_def.get("format")
                lookup_mode = var_def.get("lookup")
                if isinstance(fmt, str) and fmt:
                    val = fmt.replace("{1}", val)
                elif lookup_mode == "range_table":
                    try:
                        num = int(val, 10)
                    except ValueError:
                        return None, f"variable {var_name!r} range_table capture {val!r} is not an int"
                    looked_up = _lookup_range_table(num, parent_notes)
                    if looked_up is None:
                        return (
                            None,
                            f"variable {var_name!r} range_table lookup failed for {num} in parent notes",
                        )
                    val = looked_up
                resolved_vars[var_name] = val

        lang = data.get("lang")
        if isinstance(lang, dict) and isinstance(lang.get("default"), str):
            lang_code = lang["default"]
            if lang.get("url_transform") == "uppercase":
                lang_code = lang_code.upper()
            resolved_vars["lang"] = lang_code

        resolved_vars["id"] = inp
        resolved_vars["id_lower"] = inp.lower()
        resolved_vars["id_upper"] = inp.upper()

        built = _build_url(url_tpl, resolved_vars)
        if built is None:
            return None, f"buildUrl rejected template {url_tpl!r} for input {inp!r}"
        return built, None

    lookup = data.get("lookup_table")
    if isinstance(lookup, dict):
        if inp in lookup:
            u = _extract_lookup_url(lookup[inp])
            if u is not None:
                return u, None
        return None, f"input {inp!r} not found in data.lookup_table"

    return None, "node has neither data.url nor data.lookup_table"


def _matches_any_pattern(patterns: list[str], value: str) -> bool:
    for pat in patterns:
        if not isinstance(pat, str):
            continue
        try:
            if _compile_ecmascript_regex(pat).search(value) is not None:
                return True
        except re.error:
            continue
    return False


def violations(doc: dict) -> list[tuple[str, str]]:
    """Return a list of (node_trail, message) violations for a registry document."""
    found: list[tuple[str, str]] = []

    def walk(nodes: list | None, trail: list[str], parent_notes: str | None) -> None:
        for i, node in enumerate(nodes or []):
            if not isinstance(node, dict):
                continue
            pats = [p for p in (node.get("patterns") or []) if isinstance(p, str)]
            first_pat = pats[0] if pats else "?"
            here = trail + [f"{i}:{first_pat}"]
            where = " > ".join(here)
            data = node.get("data")
            if not isinstance(data, dict):
                data = {}

            if trail:
                has_resolver_target = bool(data.get("url") or data.get("lookup_table"))
                for j, ex in enumerate(data.get("examples") or []):
                    ex_where = f"{where} examples[{j}]"
                    if isinstance(ex, str):
                        if not ex:
                            found.append((ex_where, "empty string example"))
                            continue
                        if not _matches_any_pattern(pats, ex):
                            found.append(
                                (
                                    ex_where,
                                    f"example {ex!r} does not match any pattern in {pats!r}",
                                )
                            )
                    elif isinstance(ex, dict):
                        inp = ex.get("input")
                        if not isinstance(inp, str) or not inp:
                            found.append(
                                (ex_where, "ExampleObject missing non-empty string 'input'")
                            )
                            continue
                        if not _matches_any_pattern(pats, inp):
                            found.append(
                                (
                                    ex_where,
                                    f"ExampleObject input {inp!r} does not match any pattern in {pats!r}",
                                )
                            )
                        ex_url = ex.get("url")
                        if has_resolver_target and (not isinstance(ex_url, str) or not ex_url):
                            found.append(
                                (
                                    ex_where,
                                    f"ExampleObject for {inp!r} omits 'url' on a node with "
                                    f"data.url/data.lookup_table (causes resolver tests to skip it)",
                                )
                            )
                            continue
                        if isinstance(ex_url, str) and ex_url:
                            resolved_url, err = expand_child_url(data, inp, parent_notes)
                            if err is not None:
                                found.append(
                                    (
                                        ex_where,
                                        f"cannot resolve URL for {inp!r}: {err}",
                                    )
                                )
                            elif resolved_url != ex_url:
                                found.append(
                                    (
                                        ex_where,
                                        f"URL mismatch for {inp!r}: node resolves to "
                                        f"{resolved_url!r}, but example.url is {ex_url!r}",
                                    )
                                )
            node_notes = data.get("notes") if isinstance(data.get("notes"), str) else parent_notes
            walk(node.get("children"), here, node_notes)

    if isinstance(doc, dict):
        walk(doc.get("match_nodes"), [], None)
    return found


def collect_example_urls(doc: dict) -> list[tuple[str, str]]:
    """Return (where, url) pairs for all child/grandchild ExampleObjects in doc."""
    urls: list[tuple[str, str]] = []

    def walk(nodes: list | None, trail: list[str]) -> None:
        for i, node in enumerate(nodes or []):
            if not isinstance(node, dict):
                continue
            pats = node.get("patterns") or ["?"]
            here = trail + [f"{i}:{pats[0]}"]
            data = node.get("data") or {}
            if trail and isinstance(data, dict):
                for j, ex in enumerate(data.get("examples") or []):
                    if isinstance(ex, dict) and isinstance(ex.get("url"), str) and ex["url"]:
                        urls.append((" > ".join(here) + f" examples[{j}]", ex["url"]))
            walk(node.get("children"), here)

    if isinstance(doc, dict):
        walk(doc.get("match_nodes"), [])
    return urls


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    """Verify every redirect target via _net_guard.effective_url_is_safe."""

    def __init__(self, guard_fn):
        super().__init__()
        self._guard_fn = guard_fn

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        if not self._guard_fn(newurl):
            raise urllib.error.URLError(f"redirect target blocked by SSRF guard: {newurl}")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def probe_url(url: str, timeout: float = 10.0) -> tuple[bool, str]:
    """Probe a single URL using _net_guard SSRF protection. Returns (ok, detail)."""
    from _net_guard import effective_url_is_safe, is_safe_host

    if not url.startswith("https://") or not is_safe_host(url):
        return False, "blocked by SSRF guard (non-HTTPS or non-public host)"

    opener = urllib.request.build_opener(_SafeRedirectHandler(effective_url_is_safe))
    headers = {"User-Agent": "SecID-Example-Checker/1.0 (+https://secid.cloudsecurityalliance.org)"}

    for method in ("HEAD", "GET"):
        req = urllib.request.Request(url, headers=headers, method=method)
        try:
            with opener.open(req, timeout=timeout) as resp:
                status = getattr(resp, "status", 200)
                if 200 <= status < 400:
                    return True, f"HTTP {status}"
                if method == "HEAD" and status in (403, 405):
                    continue
                return False, f"HTTP {status}"
        except urllib.error.HTTPError as exc:
            if method == "HEAD" and exc.code in (403, 405, 501):
                continue
            return False, f"HTTP {exc.code}"
        except Exception as exc:
            if method == "HEAD":
                continue
            return False, str(exc)
    return False, "unreachable"


def self_test() -> int:
    """Run unit tests for offline example validation."""
    good_doc = {
        "match_nodes": [
            {
                "patterns": ["(?i)^test-source$"],
                "data": {"notes": "Year ranges: 2023: 5000, 2024: 5600"},
                "children": [
                    {
                        "patterns": ["^CVE-\\d{4}-\\d+$"],
                        "data": {
                            "url": "https://example.org/cve/{year}/{prefix}/{id}",
                            "variables": {
                                "year": {"extract": "^CVE-(\\d{4})-"},
                                "prefix": {"extract": "^CVE-\\d{4}-(\\d)\\d{3}$", "format": "{1}xxx"},
                            },
                            "examples": [
                                {"input": "CVE-2023-4487", "url": "https://example.org/cve/2023/4xxx/CVE-2023-4487"}
                            ],
                        },
                    },
                    {
                        "patterns": ["^DSA-\\d+-\\d+$"],
                        "data": {
                            "url": "https://example.org/dsa/{year}/dsa-{num}",
                            "variables": {
                                "num": {"extract": "^DSA-(\\d+)-"},
                                "year": {"extract": "^DSA-(\\d+)-", "lookup": "range_table"},
                            },
                            "examples": [
                                {"input": "DSA-5678-1", "url": "https://example.org/dsa/2024/dsa-5678"}
                            ],
                        },
                    },
                    {
                        "patterns": ["^art-(?<num>\\d+)$"],
                        "data": {
                            "url": "https://example.org/{lang}/art-{num}",
                            "lang": {"default": "en", "url_transform": "uppercase"},
                            "variables": {
                                "num": {"extract": "^art-(\\d+)$"}
                            },
                            "examples": [
                                {"input": "art-5", "url": "https://example.org/EN/art-5"}
                            ],
                        },
                    },
                    {
                        "patterns": ["^A&A-\\d+$"],
                        "data": {
                            "url": "https://example.org/path/{id}?q={id}",
                            "examples": [
                                {"input": "A&A-01", "url": "https://example.org/path/A&A-01?q=A%26A-01"}
                            ],
                        },
                    },
                    {
                        "patterns": ["^(a1|b2)$"],
                        "data": {
                            "lookup_table": {
                                "a1": "https://example.org/items/first",
                                "b2": {"url": "https://example.org/items/second"},
                            },
                            "examples": [
                                {"input": "a1", "url": "https://example.org/items/first"},
                                {"input": "b2", "url": "https://example.org/items/second"},
                            ],
                        },
                    },
                ],
            }
        ]
    }

    bad_pattern_doc = {
        "match_nodes": [
            {
                "patterns": ["(?i)^x$"],
                "children": [
                    {
                        "patterns": ["^art-\\d+$"],
                        "data": {
                            "url": "https://example.org/{id}",
                            "examples": [{"input": "sec-1", "url": "https://example.org/sec-1"}],
                        },
                    }
                ],
            }
        ]
    }

    bad_missing_url_doc = {
        "match_nodes": [
            {
                "patterns": ["(?i)^x$"],
                "children": [
                    {
                        "patterns": ["^art-\\d+$"],
                        "data": {
                            "url": "https://example.org/{id}",
                            "examples": [{"input": "art-1", "note": "missing url"}],
                        },
                    }
                ],
            }
        ]
    }

    bad_mismatch_url_doc = {
        "match_nodes": [
            {
                "patterns": ["(?i)^x$"],
                "children": [
                    {
                        "patterns": ["^art-\\d+$"],
                        "data": {
                            "url": "https://example.org/{id}",
                            "examples": [{"input": "art-1", "url": "https://example.org/art-2"}],
                        },
                    }
                ],
            }
        ]
    }

    bad_lookup_missing_doc = {
        "match_nodes": [
            {
                "patterns": ["(?i)^x$"],
                "children": [
                    {
                        "patterns": ["(?i)^a1$"],
                        "data": {
                            "lookup_table": {"a1": "https://example.org/1"},
                            "examples": [{"input": "A1", "url": "https://example.org/1"}],
                        },
                    }
                ],
            }
        ]
    }

    bad_case_extractor_doc = {
        "match_nodes": [
            {
                "patterns": ["(?i)^x$"],
                "children": [
                    {
                        "patterns": ["^ART-\\d+$"],
                        "data": {
                            "url": "https://example.org/art-{num}",
                            "variables": {"num": {"extract": "^art-(\\d+)$"}},
                            "examples": [{"input": "ART-5", "url": "https://example.org/art-5"}],
                        },
                    }
                ],
            }
        ]
    }

    bad_query_encoding_doc = {
        "match_nodes": [
            {
                "patterns": ["(?i)^x$"],
                "children": [
                    {
                        "patterns": ["^A&A-01$"],
                        "data": {
                            "url": "https://example.org/?id={id}",
                            "examples": [{"input": "A&A-01", "url": "https://example.org/?id=A&A-01"}],
                        },
                    }
                ],
            }
        ]
    }

    checks = [
        ("good_doc", violations(good_doc) == []),
        (
            "bad_pattern_doc",
            len(violations(bad_pattern_doc)) == 1
            and "does not match any pattern" in violations(bad_pattern_doc)[0][1],
        ),
        (
            "bad_missing_url_doc",
            len(violations(bad_missing_url_doc)) == 1
            and "omits 'url'" in violations(bad_missing_url_doc)[0][1],
        ),
        (
            "bad_mismatch_url_doc",
            len(violations(bad_mismatch_url_doc)) == 1
            and "URL mismatch" in violations(bad_mismatch_url_doc)[0][1],
        ),
        (
            "bad_lookup_missing_doc",
            len(violations(bad_lookup_missing_doc)) == 1
            and "not found in data.lookup_table" in violations(bad_lookup_missing_doc)[0][1],
        ),
        (
            "bad_case_extractor_doc",
            len(violations(bad_case_extractor_doc)) == 1
            and "did not capture group(1)" in violations(bad_case_extractor_doc)[0][1],
        ),
        (
            "bad_query_encoding_doc",
            len(violations(bad_query_encoding_doc)) == 1
            and "URL mismatch" in violations(bad_query_encoding_doc)[0][1],
        ),
    ]
    failed = [name for name, ok in checks if not ok]
    for name, ok in checks:
        print(f"  {'ok' if ok else 'FAIL'}  {name}")
    print("self-test:", "PASS" if not failed else f"FAIL ({', '.join(failed)})")
    return 0 if not failed else 1


def _resolve_input_files(paths: list[str]) -> list[Path]:
    if not paths:
        return registry_files()
    out: list[Path] = []
    for raw in paths:
        p = Path(raw)
        if p.is_dir():
            out.extend(
                sorted(
                    sub
                    for sub in p.rglob("*.json")
                    if not any(part.startswith("_") for part in sub.relative_to(p).parts)
                )
            )
        else:
            out.append(p)
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("paths", nargs="*", help="Optional registry JSON files to check")
    parser.add_argument("--self-test", action="store_true", help="Run built-in unit tests")
    parser.add_argument(
        "--live",
        action="store_true",
        help="Probe example URLs over HTTPS (uses _net_guard SSRF protection)",
    )
    parser.add_argument(
        "--timeout", type=float, default=10.0, help="HTTP timeout in seconds for --live"
    )
    parser.add_argument(
        "--workers", type=int, default=8, help="Concurrent workers for --live"
    )
    args = parser.parse_args(argv)

    if args.self_test:
        return self_test()

    files = _resolve_input_files(args.paths)
    total_violations = 0
    total_examples = 0
    live_targets: dict[str, list[str]] = {}

    for f in files:
        try:
            doc = json.loads(f.read_text(encoding="utf-8"))
        except Exception as exc:
            print(f"SKIP {f}: {exc}")
            continue

        for where, url in collect_example_urls(doc):
            total_examples += 1
            live_targets.setdefault(url, []).append(f"{f}: {where}")

        for where, msg in violations(doc):
            total_violations += 1
            print(f"FAIL {f}: {where}\n     {msg}")

    if total_violations:
        print(f"\n{total_violations} example violation(s) across {len(files)} file(s).")
        return 1

    print(
        f"OK: {len(files)} file(s), {total_examples} structured example URL(s); "
        f"all child/grandchild examples match patterns and URL templates."
    )

    if not args.live:
        return 0

    print(f"\nProbing {len(live_targets)} unique example URL(s) (--live)...")
    dead = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        future_map = {
            pool.submit(probe_url, url, args.timeout): url for url in sorted(live_targets)
        }
        for fut in concurrent.futures.as_completed(future_map):
            url = future_map[fut]
            ok, detail = fut.result()
            if not ok:
                dead += 1
                locs = ", ".join(live_targets[url][:3])
                print(f"DEAD [{detail}] {url}\n     at {locs}")
    if dead:
        print(f"\n{dead}/{len(live_targets)} unique example URL(s) failed live probe.")
        return 1
    print(f"LIVE OK: all {len(live_targets)} unique example URL(s) reachable.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
