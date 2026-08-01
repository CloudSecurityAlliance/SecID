#!/usr/bin/env python3
"""Offline unit tests for the version-alias gate (scripts/validate-version-aliases.py).

The live registry should always be clean, so it never exercises the rejection
paths. These assert the gate would actually catch a bad entry.
Run: python3 scripts/test_validate_version_aliases.py   (also discoverable by pytest)
"""

import importlib.util
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "validate_version_aliases",
    Path(__file__).resolve().parent / "validate-version-aliases.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
pattern_literal = _mod.pattern_literal
node_label = _mod.node_label
check_source_versions = _mod.check_source_versions
check_tree_binding = _mod.check_tree_binding
check_source = _mod.check_source


# ---------- pattern_literal ----------

def test_pattern_literal_extracts_clean_literals():
    assert pattern_literal("^1\\.1\\.0$") == "1.1.0"
    assert pattern_literal("(?i)^aicm$") == "aicm"
    assert pattern_literal("^2021$") == "2021"


def test_pattern_literal_rejects_real_regex():
    # A pattern with metacharacters has no single literal form.
    assert pattern_literal("^[A-Z&]{2,3}$") is None
    assert pattern_literal("^2(\\.0)?$") is None      # the CVSS optional-group case
    assert pattern_literal("^A0[1-9]$") is None


def test_pattern_literal_rejects_character_class_escapes():
    # \d is a character class, not a literal "d". Live example:
    # registry/control/org/aicpa.json has (?i)^A\d\.\d$ for SOC 2 criteria.
    assert pattern_literal("^\\d$") is None
    assert pattern_literal("^\\d\\d\\d\\d$") is None
    assert pattern_literal("^\\w+$") is None
    assert pattern_literal("^\\s$") is None
    assert pattern_literal("(?i)^A\\d\\.\\d$") is None
    # Escaped punctuation is still a literal.
    assert pattern_literal("^1\\.1$") == "1.1"
    assert pattern_literal("^a\\-b$") == "a-b"


def test_node_label_strips_regex_furniture():
    assert node_label({"patterns": ["(?i)^aicm$"]}) == "aicm"
    assert node_label({"patterns": []}) == "<unnamed>"


# ---------- check_source_versions (metadata-internal rules) ----------

def test_clean_metadata_passes():
    va = [
        {"version": "1.1.0", "aliases": [
            {"label": "1.1", "on_match": "resolve"},
            {"label": "v1.1", "on_match": "resolve"},
        ]},
        {"version": "1.0.3"},
    ]
    assert check_source_versions(va, "aicm") == []


def test_absent_and_null_are_valid():
    assert check_source_versions(None, "cve") == []


def test_missing_version_rejected():
    assert any("version" in e for e in check_source_versions([{"status": "current"}], "x"))


def test_duplicate_version_rejected():
    errs = check_source_versions([{"version": "1.0.3"}, {"version": "1.0.3"}], "x")
    assert any("duplicate version" in e for e in errs), errs


def test_alias_label_colliding_with_real_version_rejected():
    # The CCM trap: 4.0 is a genuine release that 4.0.13 supersedes.
    va = [
        {"version": "4.0.13", "aliases": [{"label": "4.0", "on_match": "resolve"}]},
        {"version": "4.0"},
    ]
    assert any("real version" in e for e in check_source_versions(va, "ccm"))


def test_duplicate_alias_label_rejected():
    va = [
        {"version": "1.1.0", "aliases": [{"label": "1.1", "on_match": "resolve"}]},
        {"version": "1.1.3", "aliases": [{"label": "1.1", "on_match": "resolve"}]},
    ]
    assert any("duplicate alias label" in e for e in check_source_versions(va, "x"))


def test_missing_or_unknown_on_match_rejected():
    assert any("on_match" in e for e in
               check_source_versions([{"version": "1.1.0", "aliases": [{"label": "1.1"}]}], "x"))
    assert any("on_match" in e for e in check_source_versions(
        [{"version": "1.1.0", "aliases": [{"label": "1.1", "on_match": "teleport"}]}], "x"))


def test_empty_label_and_wrong_types_rejected():
    assert check_source_versions([{"version": "1.1.0", "aliases": [{"label": "  ", "on_match": "resolve"}]}], "x")
    assert check_source_versions("1.1.0", "x")
    assert check_source_versions(["1.1.0"], "x")
    assert check_source_versions([{"version": "1.1.0", "aliases": "1.1"}], "x")


# ---------- check_tree_binding (the metadata <-> tree cross-check) ----------

def _source(versions_available, children):
    return {
        "patterns": ["(?i)^aicm$"],
        "data": {"versions_available": versions_available},
        "children": children,
    }


def test_binding_ok_when_tree_and_metadata_agree():
    node = _source(
        [{"version": "1.1.0", "aliases": [{"label": "1.1", "on_match": "resolve"}]},
         {"version": "1.0.3"}],
        [{"patterns": ["^1\\.1\\.0$", "^1\\.1$"]}, {"patterns": ["^1\\.0\\.3$"]}],
    )
    assert check_tree_binding(node, "aicm") == []


def test_binding_rejects_declared_version_with_no_tree_node():
    node = _source([{"version": "1.1.0"}, {"version": "1.0.3"}],
                   [{"patterns": ["^1\\.1\\.0$"]}])
    assert any("1.0.3" in e and "no version node" in e for e in check_tree_binding(node, "aicm"))


def test_binding_rejects_tree_node_with_no_metadata():
    node = _source([{"version": "1.1.0"}],
                   [{"patterns": ["^1\\.1\\.0$"]}, {"patterns": ["^0\\.9$"]}])
    assert any("0.9" in e and "not declared" in e for e in check_tree_binding(node, "aicm"))


def test_binding_rejects_alias_missing_from_tree():
    # Declared in metadata but absent from the node's patterns: would never resolve.
    node = _source([{"version": "1.1.0", "aliases": [{"label": "1.1", "on_match": "resolve"}]}],
                   [{"patterns": ["^1\\.1\\.0$"]}])
    assert any("1.1" in e and "not a pattern" in e for e in check_tree_binding(node, "aicm"))


def test_binding_rejects_aliases_when_source_has_no_version_nodes():
    # CCM's situation: metadata-only versions, no tree nodes. Aliases cannot work.
    node = _source([{"version": "4.1", "aliases": [{"label": "4.1.0", "on_match": "resolve"}]}],
                   [{"patterns": ["^[A-Z&]{2,3}-\\d{2}$"]}])
    assert any("no version-level tree nodes" in e for e in check_tree_binding(node, "aicm"))


def test_binding_allows_metadata_only_when_no_aliases_declared():
    # Documented versions without tree nodes are fine as long as no alias is claimed.
    node = _source([{"version": "4.1"}, {"version": "4.0"}],
                   [{"patterns": ["^[A-Z&]{2,3}-\\d{2}$"]}])
    assert check_tree_binding(node, "ccm") == []


def test_binding_reports_a_version_whose_node_is_not_canonically_literal():
    # ^2(\.0)?$ matches "2.0", but patterns[0] is not a clean literal so the node
    # cannot be bound and there is nothing to canonicalize to. This is the real
    # first.org/cvss situation.
    node = _source(
        [{"version": "3.1"}, {"version": "2.0"}],
        [{"patterns": ["^3\\.1$"]}, {"patterns": ["^2(\\.0)?$"]}],
    )
    errs = check_tree_binding(node, "cvss")
    assert any("2.0" in e and "no version node" in e for e in errs), errs


def test_binding_ignores_item_patterns_that_merely_look_like_versions():
    # CIS safeguard IDs (8.1) and PCI requirement IDs (1.2) match version-shaped
    # strings but are item patterns, not version nodes. Binding by regex match
    # instead of by literal flags these as false positives.
    node = _source(
        [{"version": "8.0"}, {"version": "7.1"}],
        [{"patterns": ["^\\d{1,2}$"]}, {"patterns": ["^\\d{1,2}\\.\\d{1,2}$"]}],
    )
    assert check_tree_binding(node, "cisecurity") == []


def test_check_source_combines_both_layers():
    node = _source([{"version": "1.1.0", "aliases": [{"label": "1.1"}]}],
                   [{"patterns": ["^1\\.1\\.0$"]}])
    errs = check_source(node)
    assert any("on_match" in e for e in errs)      # metadata layer
    assert any("not a pattern" in e for e in errs)  # binding layer


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
