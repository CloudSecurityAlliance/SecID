#!/usr/bin/env python3
"""Offline unit tests for the URL scheme/host gate (scripts/validate-urls.py).

The live registry is all-clean, so it never exercises the rejection paths.
These assert the gate would actually catch a bad entry.
Run: python3 scripts/test_validate_urls.py   (also discoverable by pytest)
"""

import importlib.util
from pathlib import Path

# The script is hyphenated (validate-urls.py), so load it explicitly.
_spec = importlib.util.spec_from_file_location(
    "validate_urls", Path(__file__).resolve().parent / "validate-urls.py"
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
check_url, is_url_key = _mod.check_url, _mod.is_url_key

ALLOW = {"veriscommunity.net", "www.pentest-standard.org"}


def test_https_ok():
    assert check_url("https://www.cve.org/CVERecord?id=CVE-2021-44228", set()) is None


def test_http_rejected_unless_allowlisted():
    assert check_url("http://example.com/x", set()) is not None
    assert check_url("http://veriscommunity.net/robots.txt", ALLOW) is None
    assert check_url("http://evil.example/x", ALLOW) is not None


def test_dangerous_schemes_always_rejected():
    for bad in ("javascript:alert(1)", "data:text/html,<script>1</script>",
                "file:///etc/passwd", "blob:abc", "vbscript:msgbox(1)"):
        assert check_url(bad, ALLOW) is not None, f"{bad} must be rejected"


def test_other_schemes_rejected():
    assert check_url("ftp://host/x", set()) is not None


def test_template_validates_literal_prefix():
    # placeholder in path position — literal prefix is https://host -> ok
    assert check_url("https://host.example/{id}", set()) is None
    # scheme/host is itself a placeholder -> no literal scheme -> rejected
    assert check_url("{base}/path", set()) is not None


def test_url_key_detection():
    assert is_url_key("url") and is_url_key("url_template") and is_url_key("wikipedia")
    assert is_url_key("source_url") and is_url_key("cna_partner_url")
    assert not is_url_key("description")


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"PASS — {len(fns)} tests")
