#!/usr/bin/env python3
"""Assert the CSA control registry records AICM/AI-CAIQ/CCM versions correctly.

Data assertions, not logic tests. They exist because the AICM version record
was wrong in a way no structural validator could catch: it declared `1.0`,
which it cannot resolve, while omitting both releases it can.

Run: python3 scripts/test_csa_version_data.py   (also discoverable by pytest)
"""

import json
from pathlib import Path

CSA = Path(__file__).resolve().parent.parent / "registry/control/org/cloudsecurityalliance.json"
DOC = json.loads(CSA.read_text(encoding="utf-8"))


def source(name: str) -> dict:
    for node in DOC["match_nodes"]:
        if node["patterns"][0].replace("(?i)", "").strip("^$") == name:
            return node
    raise AssertionError(f"source {name!r} not found")


def data(name: str) -> dict:
    return source(name)["data"]


def versions(name: str) -> dict[str, dict]:
    return {v["version"]: v for v in data(name)["versions_available"]}


def alias_labels(name: str, version: str) -> set[str]:
    return {a["label"] for a in versions(name)[version].get("aliases", [])}


def version_nodes(name: str) -> dict[str, dict]:
    """Children of the source node keyed by their canonical patterns[0] literal."""
    out = {}
    for child in source(name).get("children") or []:
        p0 = child["patterns"][0]
        lit = p0.replace("(?i)", "").strip("^$").replace("\\", "")
        out[lit] = child
    return out


# ---------- AICM ----------

def test_aicm_has_version_tree_nodes():
    # The whole point: without these, @9.9 resolves.
    nodes = version_nodes("aicm")
    assert "1.1.0" in nodes, sorted(nodes)
    assert "1.0.3" in nodes, sorted(nodes)


def test_aicm_version_nodes_carry_the_control_children():
    for v in ("1.1.0", "1.0.3"):
        kids = version_nodes("aicm")[v].get("children") or []
        pats = [k["patterns"][0] for k in kids]
        assert "^[A-Z&]{2,3}-\\d{2}$" in pats, (v, pats)


def test_aicm_1_1_is_an_alias_pattern_on_the_tree_node():
    pats = version_nodes("aicm")["1.1.0"]["patterns"]
    assert pats[0] == "^1\\.1\\.0$", pats          # canonical first
    assert "^1\\.1$" in pats and "^v1\\.1$" in pats, pats


def test_aicm_metadata_matches_the_tree():
    assert alias_labels("aicm", "1.1.0") == {"1.1", "v1.1"}
    v = versions("aicm")
    assert v["1.1.0"]["status"] == "current"
    assert v["1.1.0"]["release_date"] == "2026-06-22"
    assert v["1.0.3"]["status"] == "superseded"
    assert v["1.0.3"]["release_date"] is None


def test_aicm_declares_only_resolvable_versions():
    # AICM 1.0.0-1.0.2 were real releases -- 1.0.3's upstream metadata records
    # that it supersedes "AICM 1.0.0-1.0.2" -- but none has a retrievable
    # artifact, so SecID declares only what it can resolve: 1.0.3 and 1.1.0.
    assert "1.0" not in versions("aicm")
    assert "1.0" not in version_nodes("aicm")


def test_aicm_requires_a_version():
    d = data("aicm")
    assert d["version_required"] is True
    assert d["unversioned_behavior"] == "all_with_guidance"


def test_aicm_disambiguation_states_the_renumbering():
    text = data("aicm")["version_disambiguation"]
    assert "54" in text, "the renumbering count must be 54, per the generated crosswalk"
    assert "55" not in text, "55 is the stale prose figure"
    assert "LOG-15" in text and "string match" in text


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
