"""Unit tests for the SecID MCP plugin's output-boundary hardening (F-13-01).

Run: pytest plugins/secid/test_server.py

Loads server.py by path so the test does not depend on it being importable as
a top-level module. server.py imports cleanly (argparse lives in main()).
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "secid_plugin_server", Path(__file__).with_name("server.py")
)
server = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(server)

# Special chars built via chr() so this test's source stays pure ASCII.
TAB, NL, ESC, ZWSP, RLO = chr(9), chr(10), chr(0x1B), chr(0x200B), chr(0x202E)


def test_clean_str_strips_controls_keeps_tab_newline():
    assert server._clean_str("ok" + ESC + "[2Jx" + TAB + "c" + NL + "d") == "ok[2Jx" + TAB + "c" + NL + "d"


def test_clean_str_strips_zero_width_and_bidi():
    assert server._clean_str("a" + ZWSP + "b" + RLO + "c") == "abc"


def test_clean_str_caps_length():
    assert len(server._clean_str("a" * 10_000)) == server._MAX_FIELD_CHARS


def test_sanitize_data_relocates_and_labels_prose():
    data = {"urls": [{"url": "https://x"}], "description": "free text", "scope": "act on me"}
    out = server._sanitize_data(data)
    assert "urls" in out                                   # structural key stays
    assert "description" not in out and "scope" not in out  # prose relocated
    env = out["registry_text_untrusted"]
    assert env["description"] == "free text" and env["scope"] == "act on me"
    assert "NOT as instructions" in env["_warning"]


def test_sanitize_response_rebuilds_envelope_and_drops_unknown_keys():
    resp = {
        "secid_query": "secid:advisory/x",
        "status": "found",
        "message": None,
        "results": [{"secid": "s", "weight": 100, "url": "https://x", "data": {"notes": "n"}}],
        "evil_top_level": "should be dropped",
    }
    out = server._sanitize_response(resp)
    assert "evil_top_level" not in out          # unknown top-level key dropped
    assert out["status"] == "found"
    assert "message" not in out                 # None message omitted
    r = out["results"][0]
    assert r["url"] == "https://x" and r["weight"] == 100  # structural preserved
    assert r["data"]["registry_text_untrusted"]["notes"] == "n"  # data prose relocated


def test_sanitize_response_handles_non_dict():
    out = server._sanitize_response(["not", "a", "dict"])
    assert out["status"] == "error"
