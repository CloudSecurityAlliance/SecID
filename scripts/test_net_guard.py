#!/usr/bin/env python3
"""Offline unit tests for the SSRF guard (scripts/_net_guard.py).

Uses literal IPs so getaddrinfo resolves them locally — no DNS / no network.
Run: python3 scripts/test_net_guard.py   (also discoverable by pytest)
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _net_guard import is_safe_host, effective_url_is_safe, _host_from


def test_blocks_internal_addresses():
    for bad in ("127.0.0.1", "10.0.0.1", "192.168.1.1", "172.16.0.1",
                "169.254.169.254", "::1", "0.0.0.0"):
        assert is_safe_host(bad) is False, f"{bad} should be blocked"


def test_allows_public_literal():
    assert is_safe_host("8.8.8.8") is True
    assert is_safe_host("1.1.1.1") is True


def test_empty_and_garbage_fail_closed():
    assert is_safe_host("") is False
    assert is_safe_host("not a host at all") is False


def test_host_extraction():
    assert _host_from("https://Example.COM:443/path") == "example.com"
    assert _host_from("cisco.com") == "cisco.com"
    assert _host_from("cisco.com/foo") == "cisco.com"


def test_effective_url_requires_https_and_public():
    assert effective_url_is_safe("https://8.8.8.8/x") is True
    assert effective_url_is_safe("http://8.8.8.8/x") is False   # not https
    assert effective_url_is_safe("https://127.0.0.1/x") is False  # internal


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
    print(f"PASS — {len(fns)} tests")
