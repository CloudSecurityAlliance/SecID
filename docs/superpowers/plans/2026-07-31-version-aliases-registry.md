# Version Aliases — Registry Plan (Plan 1 of 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make AICM's `@version` qualifier actually mean something, and give SecID a curated, validated way to express version aliases.

**Architecture:** Two layers bound by a validator. The **pattern tree** does the matching — a versioned source gets version-level nodes between its name node and its item nodes, with `patterns[0]` the canonical version string and aliases as further OR-alternatives. **`versions_available`** carries what a regex cannot: release dates, status, notes, and per-alias `on_match`. A new `scripts/validate-version-aliases.py` asserts the two agree, so the redundancy is a consistency guarantee rather than a drift risk.

**Tech Stack:** Python 3.12, `jsonschema` (pip), GitHub Actions. No build system; validation scripts are the test suite.

**Spec:** [`docs/superpowers/specs/2026-07-31-version-aliases-design.md`](../specs/2026-07-31-version-aliases-design.md). Decision IDs (D1–D10, R1–R4) below refer to it.

## Global Constraints

- **Python 3.12.** CI uses `actions/setup-python@v5` with `python-version: "3.12"`.
- **Validation scripts are hyphenated** (`validate-version-aliases.py`); tests are underscored (`test_validate_version_aliases.py`) and load the module via `importlib.util.spec_from_file_location`. Follow `scripts/test_validate_urls.py` exactly.
- **Tests are dual-runnable:** plain `assert` functions named `test_*`, plus an `if __name__ == "__main__":` block. Discoverable by pytest but must not require it.
- **Version enforcement needs version-level tree nodes AND a subpath in the query.** Established by live probe: `top10@9999#A01` → `not_found`; `top10@9999` → `found`; `cvss@9.9` → `found`; `aicm@9.9#LOG-15` → `found`. `version_required` does **not** gate it.
- **`patterns[0]` must be a clean literal** on every version node — no optional groups. `^2(\.0)?$` matches but leaves nothing to canonicalize to. Write `["^1\\.1\\.0$", "^1\\.1$"]`, never `^1\.1(\.0)?$`.
- **An alias only functions if its source has version tree nodes.** Declaring aliases without them produces documentation that silently never resolves — the validator rejects this.
- **Every declared version needs a tree node, and vice versa.** Do not declare a version SecID cannot resolve.
- **Never invent a URL.** Verify with `curl` before committing; CSA's site returns real 404s, so status codes are trustworthy.
- **`match_nodes[].data` stays `additionalProperties: true`.** Do not constrain it.
- **AICM renumbering count is 54**, not 55 — source of truth is the generated crosswalk CSV, not the DataSets prose.
- **Branch, never commit to `main`.** Work continues on `feat/version-aliases`.
- **JSON registry changes merged to `main` auto-deploy to the live resolver.** Every task must leave the registry valid.

---

### Task 1: Schema `$defs` for version entries and aliases

Documents the shape and the tree binding. Enforcement is Task 2 — this task changes no behavior, which is why it is separable.

**Files:**
- Modify: `schemas/registry-namespace.schema.json` (append inside `$defs`, after `Tags`)
- Modify: `docs/reference/REGISTRY-JSON-FORMAT.md` (the `versions_available` row, plus a new subsection)

**Interfaces:**
- Consumes: nothing
- Produces: `#/$defs/VersionEntry`, `#/$defs/VersionAlias` — referenced by Task 2's docstring and by REGISTRY-JSON-FORMAT.md

- [ ] **Step 1: Confirm the current `$defs`**

Run: `python3 -c "import json;print(list(json.load(open('schemas/registry-namespace.schema.json'))['\$defs']))"`
Expected: `['UrlObject', 'MatchNode', 'Tags']`

- [ ] **Step 2: Add the two `$defs`**

Inside `"$defs"`, after the `"Tags"` object's closing brace, add a comma then:

```json
    "VersionAlias": {
      "type": "object",
      "description": "An alternate label for the version entry this object is nested under. Publishers routinely label one release two ways: CSA stamps the AICM workbook 1.1.0 while branding the same release 'v1.1' on its download page, and does the reverse for CCM where 4.1 is canonical and 4.1.0 is the variant. Nesting encodes the target, so there is no pointer to dangle. IMPORTANT: this object is metadata only. Matching is done by the pattern tree — the alias label must also appear as an OR-pattern on the corresponding version node, or it will never resolve. scripts/validate-version-aliases.py enforces that binding.",
      "required": ["label", "on_match"],
      "properties": {
        "label": {
          "type": "string",
          "minLength": 1,
          "description": "The alias exactly as the publisher writes it. Never normalized — no case folding, no 'v' stripping, no semver inference. Must not equal a real version string in the same source."
        },
        "on_match": {
          "type": "string",
          "enum": ["resolve", "redirect"],
          "description": "What a resolver does when this label matches. 'resolve' returns full data inline with status 'found' and version_matched_alias set — for co-equal publisher labels. 'redirect' returns empty results with status 'corrected' and the canonical SecID in the message — for labels that should be retired. Reserved and deliberately unimplemented: 'track' (a moving pointer to the latest matching version). Resolvers must ignore alias entries whose on_match they do not recognize, so reserved values can ship later without breaking deployed resolvers."
        },
        "note": {
          "type": "string",
          "description": "Where this label appears, or why it exists."
        }
      },
      "additionalProperties": false
    },
    "VersionEntry": {
      "type": "object",
      "description": "One known version of a source, in a match_node's data.versions_available array. Each entry must correspond to a version-level node in that source's pattern tree whose patterns[0] is the canonical version string; the validator enforces this both ways. Not schema-enforced here, because versions_available lives inside match_nodes[].data and data is additionalProperties:true — see scripts/validate-version-aliases.py.",
      "required": ["version"],
      "properties": {
        "version": {
          "type": "string",
          "minLength": 1,
          "description": "The canonical version string, exactly as the artifact identifies itself. Where a publisher's download page and the artifact disagree, the artifact wins and the page's label becomes an alias."
        },
        "release_date": {
          "oneOf": [{ "type": "string" }, { "type": "null" }],
          "description": "ISO date, or null if researched and unknown."
        },
        "status": {
          "type": "string",
          "description": "Lifecycle state, e.g. 'current', 'superseded', 'draft'."
        },
        "note": {
          "type": "string",
          "description": "What a consumer needs to know about this specific version — item counts, mapping changes, ID-stability warnings, sourcing caveats."
        },
        "aliases": {
          "type": "array",
          "description": "Alternate labels for this version. Each must also appear as an OR-pattern on the corresponding version node in the tree.",
          "items": { "$ref": "#/$defs/VersionAlias" }
        }
      },
      "additionalProperties": true
    }
```

- [ ] **Step 3: Verify the schema is valid**

Run:
```bash
python3 -c "
import json, jsonschema
d = json.load(open('schemas/registry-namespace.schema.json'))
jsonschema.Draft202012Validator.check_schema(d)
print('defs:', list(d['\$defs']))
"
```
Expected: `defs: ['UrlObject', 'MatchNode', 'Tags', 'VersionAlias', 'VersionEntry']`, no exception.

- [ ] **Step 4: Verify the existing registry still validates**

Run: `python3 scripts/validate-registry-schema.py`
Expected: PASS — the new `$defs` are unreferenced from any enforced path.

- [ ] **Step 5: Document it**

In `docs/reference/REGISTRY-JSON-FORMAT.md`, replace the `versions_available` row of the Version Resolution Fields table with:

```markdown
| `versions_available` | array, optional | Known versions of this source. Each object has `version` (string, required), `release_date`, `status`, `note`, and `aliases`. Must correspond 1:1 with the source's version-level tree nodes — see `$defs/VersionEntry` and Version Aliases below. |
```

Then add, immediately after the Unversioned Behavior Values table:

```markdown
##### Version Aliases

Publishers routinely label one release two ways. CSA stamps `{"specification_version":"1.1.0"}` in cell A1 of the AICM workbook while branding the same release "v1.1" on its download page — and does the reverse for CCM, where `4.1` is canonical and `4.1.0` is the variant. Because the direction is inconsistent even within one publisher, aliases are curated data. They are never derived by prefix matching or `v`-stripping.

Aliases live in **two places with different jobs**:

**The tree matches.** A versioned source gets version-level nodes between its name node and its item nodes. `patterns` is an OR-list, so the canonical string and its aliases are alternatives on one node:

```json
{
  "patterns": ["^1\\.1\\.0$", "^1\\.1$", "^v1\\.1$"],
  "description": "AICM v1.1.0 — CSA brands this release v1.1",
  "children": [ /* this version's item patterns */ ]
}
```

`patterns[0]` is the canonical form. Write aliases as **separate patterns**, never as an optional group: `^2(\.0)?$` matches both `2` and `2.0` but leaves no literal to canonicalize to.

**`versions_available` describes.** Release dates, status, notes and `on_match` cannot be derived from a regex:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | yes | The alias exactly as the publisher writes it. Never normalized. |
| `on_match` | string | yes | `"resolve"` (data inline, status `found`) or `"redirect"` (empty results, status `corrected`, canonical SecID in the message). |
| `note` | string | no | Where the label appears, or why. |

**The validator binds them.** `scripts/validate-version-aliases.py` asserts every declared version has a tree node whose `patterns[0]` matches it, every alias label appears as a pattern on that node, and every version node has a metadata entry. An alias declared without tree nodes is rejected, because it would be documentation that never resolves.

**Rules.** An alias is immutable once published and is never re-pointed. Aliases never chain — one hop to a concrete version. An alias label must be unique within its source and must never equal a real version string there: CCM `4.0` is a genuine release that `4.0.13` supersedes, so `4.0` may not be an alias of `4.0.13`.

**When versions get enforced.** A version is validated only when the source has version-level tree nodes **and** the query carries a subpath — only a subpath forces the walk to traverse the version level. Adding version nodes to a source therefore also changes its unversioned behavior: `source#ITEM` with no version returns source-level data and drops the subpath. Do not add version nodes to a source whose item IDs are stable across releases and whose unversioned queries are useful.
```

- [ ] **Step 6: Commit**

```bash
git add schemas/registry-namespace.schema.json docs/reference/REGISTRY-JSON-FORMAT.md
git commit -m "Add VersionEntry/VersionAlias schema defs and document version aliases

Documents shape and the tree binding. versions_available lives inside
match_nodes[].data, which is additionalProperties:true, so a \$ref there is
unreachable — enforcement lands in scripts/validate-version-aliases.py."
```

---

### Task 2: Validation script and tests

The enforcement layer, including the tree ↔ metadata cross-check. Written before any data changes so the new AICM tree is validated as it is authored.

**Files:**
- Create: `scripts/validate-version-aliases.py`
- Create: `scripts/test_validate_version_aliases.py`

**Interfaces:**
- Consumes: `$defs/VersionEntry`, `$defs/VersionAlias` from Task 1 (as documented shape)
- Produces:
  - `pattern_literal(p: str) -> str | None`
  - `node_label(node: dict) -> str`
  - `check_source_versions(versions_available, source_label: str) -> list[str]`
  - `check_tree_binding(source_node: dict, source_label: str) -> list[str]`
  - `check_source(source_node: dict) -> list[str]`
  - `main() -> int` (0 clean, 1 violations)

- [ ] **Step 1: Write the failing tests**

Create `scripts/test_validate_version_aliases.py`:

```python
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
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 scripts/test_validate_version_aliases.py`
Expected: FAIL — `FileNotFoundError`, the module does not exist.

- [ ] **Step 3: Write the implementation**

Create `scripts/validate-version-aliases.py`:

```python
#!/usr/bin/env python3
"""Validate version metadata and version aliases across registry JSON files.

Two layers have to agree, and this script is what makes them agree.

  The TREE matches. A versioned source has version-level nodes between its
  name node and its item nodes. `patterns` is an OR-list, so a version node's
  canonical string and its aliases are alternatives on one node:
      {"patterns": ["^1\\.1\\.0$", "^1\\.1$"], "children": [...]}
  patterns[0] is canonical.

  versions_available DESCRIBES. Release dates, status, notes and per-alias
  on_match cannot be derived from a regex, so they are hand-authored.

JSON Schema cannot enforce any of this: versions_available lives inside
match_nodes[].data, and data is additionalProperties:true by design, so a
$ref there is unreachable. The schema's $defs/VersionEntry and
$defs/VersionAlias are the documented shape; this script is the constraint.
Same split the $defs/Tags docstring already describes for data.tags.

Metadata rules, per source:
  1. every versions_available entry has a non-empty string `version`
  2. version strings are unique within the source
  3. every alias has a non-empty `label` and an `on_match` of resolve|redirect
  4. alias labels are unique within the source
  5. an alias label never equals a real version string in the same source

Binding rules, per source:
  6. every declared version has a version node whose patterns[0] equals it
  7. every version node's patterns[0] is a clean literal (no optional groups —
     otherwise there is nothing to canonicalize to)
  8. every version node has a versions_available entry
  9. every declared alias label appears as a pattern on its version node
 10. a source that declares aliases must have version-level tree nodes at all,
     since an alias with no node is documentation that never resolves

Rule 5 is the one that catches real mistakes: CSA's CCM 4.0 is a genuine
release that 4.0.13 supersedes, so aliasing 4.0 -> 4.0.13 would silently
repoint a real version.

Absent or null versions_available is valid — per the null-vs-absent
convention, absent means "not yet researched" and null means "researched,
found nothing".

Skips (matching scripts/validate-registry-schema.py):
  - files whose name starts with `_` (templates, _deferred entries)
  - top-level registry/<type>.json files (type descriptions, not namespaces)

Usage:
    python3 scripts/validate-version-aliases.py
    python3 scripts/validate-version-aliases.py --registry-root path/to/registry
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

VALID_ON_MATCH = ("resolve", "redirect")
_REGEX_META = set("[](){}*+?|.")


def pattern_literal(pattern: str) -> str | None:
    """Return the literal string a pattern matches, or None if it is a real regex.

    "^1\\.1\\.0$" -> "1.1.0";  "(?i)^aicm$" -> "aicm";  "^[A-Z]{2}$" -> None.
    Escaped characters are unescaped; any unescaped metacharacter disqualifies
    the pattern, which is what rejects CVSS-style "^2(\\.0)?$".
    """
    if not isinstance(pattern, str):
        return None
    core = pattern[4:] if pattern.startswith("(?i)") else pattern
    core = core[1:] if core.startswith("^") else core
    core = core[:-1] if core.endswith("$") else core
    out: list[str] = []
    i = 0
    while i < len(core):
        ch = core[i]
        if ch == "\\":
            if i + 1 >= len(core):
                return None
            nxt = core[i + 1]
            # \d \w \s \b and backreferences are character classes, not literals.
            if nxt.isalnum():
                return None
            out.append(nxt)
            i += 2
            continue
        if ch in _REGEX_META:
            return None
        out.append(ch)
        i += 1
    return "".join(out) or None


def node_label(node: dict) -> str:
    """Best-effort readable source name from a match_node's first pattern."""
    patterns = node.get("patterns") or []
    if not patterns or not isinstance(patterns[0], str):
        return "<unnamed>"
    return pattern_literal(patterns[0]) or patterns[0]


def check_source_versions(versions_available, source_label: str) -> list[str]:
    """Metadata-internal rules 1-5. Returns a list of error strings."""
    if versions_available is None:
        return []
    if not isinstance(versions_available, list):
        return [f"{source_label}: versions_available must be an array or null"]

    errors: list[str] = []
    seen_versions: set[str] = set()

    for i, entry in enumerate(versions_available):
        where = f"{source_label}: versions_available[{i}]"
        if not isinstance(entry, dict):
            errors.append(f"{where}: must be an object")
            continue
        version = entry.get("version")
        if not isinstance(version, str) or not version.strip():
            errors.append(f"{where}: missing required non-empty string 'version'")
            continue
        if version in seen_versions:
            errors.append(f"{where}: duplicate version {version!r}")
        seen_versions.add(version)

    # Second pass so rule 5 can see versions declared after the alias.
    seen_labels: dict[str, str] = {}
    for i, entry in enumerate(versions_available):
        if not isinstance(entry, dict):
            continue
        aliases = entry.get("aliases")
        if aliases is None:
            continue
        version = entry.get("version")
        prefix = f"{source_label}: versions_available[{i}] ({version})"
        if not isinstance(aliases, list):
            errors.append(f"{prefix}: aliases must be an array")
            continue
        for j, alias in enumerate(aliases):
            where = f"{prefix} aliases[{j}]"
            if not isinstance(alias, dict):
                errors.append(f"{where}: must be an object")
                continue
            label = alias.get("label")
            if not isinstance(label, str) or not label.strip():
                errors.append(f"{where}: missing required non-empty string 'label'")
                continue
            if alias.get("on_match") not in VALID_ON_MATCH:
                errors.append(
                    f"{where}: 'on_match' must be one of {VALID_ON_MATCH}, "
                    f"got {alias.get('on_match')!r}"
                )
            if label in seen_versions:
                errors.append(
                    f"{where}: alias label {label!r} is also a real version in this "
                    f"source — aliases must never shadow a real version"
                )
            if label in seen_labels:
                errors.append(
                    f"{where}: duplicate alias label {label!r} "
                    f"(already used by version {seen_labels[label]})"
                )
            else:
                seen_labels[label] = str(version)
    return errors


def _pattern_matches(pattern: str, value: str) -> bool:
    """Does this regex match this exact string? Invalid regexes never match."""
    if not isinstance(pattern, str):
        return False
    try:
        return re.fullmatch(pattern, value) is not None
    except re.error:
        return False


def _looks_versionish(s: str) -> bool:
    """Heuristic, used only to report an undeclared version-shaped node."""
    core = s[1:] if s[:1] in "vV" else s
    return bool(core) and all(ch.isdigit() or ch == "." for ch in core)


def check_tree_binding(source_node: dict, source_label: str) -> list[str]:
    """Binding rules 6-10: the tree and versions_available must agree.

    Version nodes are identified by LITERAL: a child is the node for version V
    only when pattern_literal(patterns[0]) == V. Binding by regex match instead
    would capture item patterns that merely look like versions -- CIS safeguard
    IDs (8.1) and PCI requirement IDs (1.2) -- producing false positives.
    """
    data = source_node.get("data")
    if not isinstance(data, dict):
        data = {}
    versions_available = data.get("versions_available")
    if not isinstance(versions_available, list) or not versions_available:
        return []

    declared: dict[str, dict] = {}
    for entry in versions_available:
        if isinstance(entry, dict) and isinstance(entry.get("version"), str):
            declared[entry["version"]] = entry

    children = [c for c in (source_node.get("children") or []) if isinstance(c, dict)]

    # A child is the node for version V only if its patterns[0] is the clean
    # literal V. Matching alone is NOT enough: CIS safeguard IDs (8.1) and PCI
    # requirement IDs (1.2) are item patterns that happen to match version
    # strings, and binding by match flags them as version nodes — 5 false
    # positives across cisecurity.org and pcisecuritystandards.org.
    version_nodes: dict[str, dict] = {}
    for child in children:
        pats = [p for p in (child.get("patterns") or []) if isinstance(p, str)]
        if not pats:
            continue
        lit = pattern_literal(pats[0])
        if lit is not None and lit in declared:
            version_nodes[lit] = child

    errors: list[str] = []
    any_aliases = any(e.get("aliases") for e in declared.values())

    if not version_nodes:
        if any_aliases:
            errors.append(
                f"{source_label}: declares version aliases but has no version-level tree "
                f"nodes — the aliases would never resolve. Add version nodes, or drop the "
                f"aliases until the tree is restructured."
            )
        # Metadata-only versions with no aliases are valid documentation.
        return errors

    for version, entry in declared.items():
        node = version_nodes.get(version)
        if node is None:
            errors.append(
                f"{source_label}: version {version!r} is declared in versions_available "
                f"but has no version node in the tree"
            )
            continue

        patterns = [p for p in (node.get("patterns") or []) if isinstance(p, str)]

        # Rule 7: patterns[0] must be the clean canonical literal.
        first = patterns[0] if patterns else None
        if first is None or pattern_literal(first) != version:
            errors.append(
                f"{source_label}: version node for {version!r} has patterns[0] {first!r}, "
                f"which is not the clean canonical literal — there is nothing to "
                f"canonicalize to. Write separate OR-patterns, not an optional group."
            )

        # Rule 9: every declared alias must actually match on this node.
        for alias in entry.get("aliases") or []:
            if not isinstance(alias, dict):
                continue
            label = alias.get("label")
            if not isinstance(label, str):
                continue
            if not any(_pattern_matches(p, label) for p in patterns):
                errors.append(
                    f"{source_label}: alias {label!r} on version {version!r} is not a "
                    f"pattern on that version node — it would never match"
                )

    # Rule 8, reverse direction: a version-shaped child bound to no declared version.
    bound = {id(n) for n in version_nodes.values()}
    for child in children:
        if id(child) in bound:
            continue
        patterns = [p for p in (child.get("patterns") or []) if isinstance(p, str)]
        if not patterns:
            continue
        lit = pattern_literal(patterns[0])
        if lit is None:
            continue  # a genuine item pattern such as ^[A-Z&]{2,3}-\d{2}$
        if _looks_versionish(lit):
            errors.append(
                f"{source_label}: version node {lit!r} is not declared in versions_available"
            )
    return errors


def check_source(source_node: dict) -> list[str]:
    """Run both layers for one source node."""
    label = node_label(source_node)
    data = source_node.get("data")
    if not isinstance(data, dict):
        data = {}
    errs = check_source_versions(data.get("versions_available"), label)
    errs += check_tree_binding(source_node, label)
    return errs


def iter_namespace_files(registry_root: Path):
    for path in sorted(registry_root.rglob("*.json")):
        if path.name.startswith("_"):
            continue
        if path.parent == registry_root:
            continue
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--registry-root", default="registry")
    args = parser.parse_args()

    root = Path(args.registry_root)
    if not root.is_dir():
        print(f"ERROR: registry root not found: {root}", file=sys.stderr)
        return 2

    files = sources = 0
    failures: list[str] = []
    for path in iter_namespace_files(root):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(doc, dict) or "match_nodes" not in doc:
            continue
        files += 1
        for node in doc.get("match_nodes") or []:
            if not isinstance(node, dict):
                continue
            data = node.get("data") or {}
            if "versions_available" not in data:
                continue
            sources += 1
            for err in check_source(node):
                failures.append(f"{path}: {err}")

    print(f"Checked {files} namespace files, {sources} sources declaring versions_available.")
    if failures:
        print(f"\n{len(failures)} violation(s):\n")
        for f in failures[:30]:
            print(f"  {f}")
        if len(failures) > 30:
            print(f"  ... and {len(failures) - 30} more")
        return 1
    print("All version/alias entries valid.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 4: Run the tests**

Run: `python3 scripts/test_validate_version_aliases.py`
Expected: PASS — 20 `ok  test_...` lines.

Also: `python3 -m pytest scripts/test_validate_version_aliases.py -q` → 20 passed.

- [ ] **Step 5: Run against the live registry and confirm the known baseline**

Run: `python3 scripts/validate-version-aliases.py`

Expected — **8 violations, exit 1.** This is the verified baseline as of 2026-07-31, not a surprise; Task 3 fixes them.

```
  registry/control/gov/nist.json: ssdf: versions_available[0]: must be an object
  registry/control/jp/go/ismap.json: control-criteria: versions_available[0]: must be an object
  registry/control/jp/or/fisc.json: security-guidelines: versions_available[0]: must be an object
  registry/reference/org/cve.json: cve-schema: versions_available[0]: must be an object
  registry/reference/org/cve.json: cve-schema: versions_available[1]: must be an object
  registry/reference/org/cve.json: cve-schema: versions_available[2]: must be an object
  registry/reference/org/first.json: cvss: version '2.0' is declared in versions_available but has no version node in the tree
  registry/reference/org/first.json: cvss: version '1.0' is declared in versions_available but has no version node in the tree
```

**If you see more than these 8, stop and report.** In particular, if `cisecurity.org` or `pcisecuritystandards.org` appear, the literal-based version-node detection has regressed — those files contain item patterns (`^\d{1,2}\.\d{1,2}$` for CIS safeguard `8.1`, PCI requirement `1.2`) that match version strings but are not version nodes. Binding by regex match rather than by literal produces 5 false positives there. Do not "fix" the data; fix the detection.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate-version-aliases.py scripts/test_validate_version_aliases.py
git commit -m "Add version/alias validator with tree-to-metadata cross-check

Enforces what JSON Schema cannot reach: versions_available lives inside
match_nodes[].data, which is additionalProperties:true.

Two load-bearing checks. An alias label may never equal a real version in
the same source (CCM 4.0 is a real release superseded by 4.0.13, so
aliasing it would silently repoint it). And an alias declared without
version-level tree nodes is rejected, because matching happens in the tree
— metadata alone would be documentation that never resolves."
```

---

### Task 3: Clear the 8 pre-existing violations

The new validator surfaces 8 real defects that predate this work. They must be fixed before CI can enforce it. Both fixes were applied to a throwaway copy of the registry on 2026-07-31 and took the validator to a clean exit 0.

**Files:**
- Modify: `registry/control/gov/nist.json`, `registry/control/jp/go/ismap.json`, `registry/control/jp/or/fisc.json`, `registry/reference/org/cve.json` (bare-string version entries)
- Modify: `registry/reference/org/first.json` (CVSS non-canonical version patterns)

**Interfaces:**
- Consumes: Task 2's validator
- Produces: a registry that exits 0, which Task 4 depends on

- [ ] **Step 1: Inspect the bare-string entries**

```bash
python3 -c "
import json
for f, src in [('registry/control/gov/nist.json','ssdf'),
               ('registry/control/jp/go/ismap.json','control-criteria'),
               ('registry/control/jp/or/fisc.json','security-guidelines'),
               ('registry/reference/org/cve.json','cve-schema')]:
    d = json.load(open(f))
    for n in d['match_nodes']:
        if n['patterns'][0].replace('(?i)','').strip('^\$') == src:
            print(f, src, json.dumps(n['data']['versions_available']))
"
```
Expected: e.g. `registry/control/gov/nist.json ssdf ["1.1"]` — arrays of **bare strings**, where the documented shape is an array of objects. A YAML→JSON conversion artifact.

- [ ] **Step 2: Convert them to objects**

Edit each of the four files by hand, turning `["1.1"]` into `[{"version": "1.1"}]` and `["5.2.0", "5.1.0", "5.0.0"]` into `[{"version": "5.2.0"}, {"version": "5.1.0"}, {"version": "5.0.0"}]`, preserving each file's existing indentation. Do not add `status` or `release_date` — that would be inventing data. The bare string carried only the version.

- [ ] **Step 3: Split CVSS's optional-group version patterns**

In `registry/reference/org/first.json`, in the `(?i)^cvss$` node's children, replace the two non-canonical patterns so `patterns[0]` is a clean literal and the short form becomes an explicit alias:

```json
      "patterns": ["^2\\.0$", "^2$"],
```
```json
      "patterns": ["^1\\.0$", "^1$"],
```

Then record the aliases in that source's `versions_available`, on the `2.0` and `1.0` entries:

```json
            "aliases": [
              {
                "label": "2",
                "on_match": "resolve",
                "note": "Major-version-only form, widely used in legacy vulnerability data."
              }
            ]
```

```json
            "aliases": [
              {
                "label": "1",
                "on_match": "resolve",
                "note": "Major-version-only form, widely used in legacy vulnerability data."
              }
            ]
```

This is a behavior improvement, not just lint appeasement: `cvss@2` currently echoes `@2` back with nothing to canonicalize to. After the split it resolves to canonical `2.0`.

- [ ] **Step 4: Verify the registry is clean**

```bash
python3 scripts/validate-version-aliases.py; echo "exit=$?"
python3 scripts/validate-registry-schema.py
python3 -c "
import json, glob
for f in glob.glob('registry/**/*.json', recursive=True): json.load(open(f))
print('all registry JSON parses')
"
```
Expected: `Checked 2130 namespace files, 380 sources declaring versions_available.` / `All version/alias entries valid.` / `exit=0`.

- [ ] **Step 5: Commit**

```bash
git add registry/control/gov/nist.json registry/control/jp/go/ismap.json \
        registry/control/jp/or/fisc.json registry/reference/org/cve.json \
        registry/reference/org/first.json
git commit -m "Fix pre-existing version-data defects surfaced by the new validator

Four sources stored versions_available as bare strings (['1.1']) rather
than objects — a YAML-to-JSON conversion artifact that no existing check
caught, since match_nodes[].data is unconstrained.

CVSS used optional-group version patterns (^2(\\.0)?\$) that match both '2'
and '2.0' but leave no literal to canonicalize to, so cvss@2 echoed '@2'
back unchanged. Split into a canonical ^2\\.0\$ plus an explicit '2' alias."
```

---

### Task 4: Wire the validator into CI

**Files:**
- Modify: `.github/workflows/validate-registry.yml` (both `paths:` blocks, and the job steps)

**Interfaces:**
- Consumes: Task 2's script and tests, and Task 3's clean registry (CI fails otherwise)
- Produces: nothing

- [ ] **Step 1: Add to both `paths:` filters**

The file has two `paths:` blocks (`push` and `pull_request`). Add to **both**:

```yaml
      - "scripts/validate-version-aliases.py"
      - "scripts/test_validate_version_aliases.py"
```

- [ ] **Step 2: Add the steps**

After `Validate type-list consistency with SecID-Service`:

```yaml
      - name: Validate version aliases
        run: python3 scripts/validate-version-aliases.py
      - name: Unit-test the version-alias gate
        run: python3 scripts/test_validate_version_aliases.py
```

The unit-test step is not redundant: a clean registry never exercises the gate's rejection paths, so a regression making it accept everything would otherwise pass CI silently.

- [ ] **Step 3: Verify the workflow parses**

```bash
python3 -c "
import sys
try: import yaml
except ImportError: print('SKIP: pyyaml absent; check indentation by eye'); sys.exit(0)
d = yaml.safe_load(open('.github/workflows/validate-registry.yml'))
steps = [s.get('name') for s in d['jobs']['validate']['steps']]
assert 'Validate version aliases' in steps, steps
assert 'Unit-test the version-alias gate' in steps, steps
print('OK:', steps)
"
```

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/validate-registry.yml
git commit -m "Run version-alias validation and its unit tests in CI"
```

---

### Task 5: Restructure the AICM tree and correct its version data

The substantive fix. **This task alone makes `aicm@9.9#LOG-15` return `not_found` and `aicm@1.1#LOG-15` resolve — no resolver change.**

**Files:**
- Modify: `registry/control/org/cloudsecurityalliance.json` — the `(?i)^aicm$` node
- Create: `scripts/test_csa_version_data.py`

**Interfaces:**
- Consumes: Task 2's validator
- Produces: `source()`, `versions()`, `alias_labels()`, `version_nodes()` helpers used by Tasks 6 and 7

- [ ] **Step 1: Verify the version-specific URLs before using them**

```bash
for u in "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1" \
         "https://cloudsecurityalliance.org/download/artifacts/ai-controls-matrix-v1-1" \
         "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-0-3" \
         "https://cloudsecurityalliance.org/artifacts/this-does-not-exist-xyzzy"; do
  printf "  %s  %s\n" "$(curl -s -o /dev/null -w '%{http_code}' -L --max-time 15 "$u")" "$u"
done
```
Expected, as measured 2026-07-31: `200`, `200`, **`404`**, `404`. The last line is the negative control proving CSA returns real 404s. **There is no version-specific page for 1.0.3** — do not invent one.

- [ ] **Step 2: Write the failing data assertions**

Create `scripts/test_csa_version_data.py`:

```python
#!/usr/bin/env python3
"""Assert the CSA control registry records AICM/AI-CAIQ/CCM versions correctly.

Data assertions, not logic tests. They exist because the AICM version record
was wrong in a way no structural validator could catch: it listed a version
(1.0) it cannot resolve, while omitting both releases it can.

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
    # AICM 1.0.0-1.0.2 were real releases -- 1.0.3's metadata records that it
    # supersedes "AICM 1.0.0-1.0.2" -- but none has a retrievable artifact, so
    # SecID declares only what it can resolve: 1.0.3 and 1.1.0.
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
```

- [ ] **Step 3: Run to verify failure**

Run: `python3 scripts/test_csa_version_data.py`
Expected: FAIL on `test_aicm_has_version_tree_nodes`.

- [ ] **Step 4: Replace the AICM node's `data` version fields**

In the `(?i)^aicm$` node's `data`, replace `version_required`, `unversioned_behavior`, and `versions_available` with:

```json
        "version_required": true,
        "unversioned_behavior": "all_with_guidance",
        "version_disambiguation": "AICM control IDs are NOT stable across releases. Between 1.0.3 and 1.1.0, CSA renumbered controls in place: 54 of the 242 control IDs present in both releases designate a DIFFERENT control. LOG-15 was Output Monitoring in 1.0.3 and is Input Monitoring in 1.1.0; IAM-12 was Safeguard Logs Integrity and is Unique Identities; TVM-12 was Threat Analysis and Modelling and is Vulnerability Management Metrics. Only one ID (IAM-19) disappeared outright, so comparing ID sets between releases does NOT detect this. Always cite AICM controls with an explicit version. Never migrate a reference between versions by string match — CSA publishes no crosswalk, so the mapping has to be reconstructed by comparing specification text between the two releases.",
        "versions_available": [
          {
            "version": "1.1.0",
            "release_date": "2026-06-22",
            "status": "current",
            "note": "247 controls across 18 domains. Control IDs renumbered in place from 1.0.3 — see version_disambiguation. The workbook's Scope Applicability (Mappings) sheet dropped from 16 columns to 13: it carries BSI AI C4, the EU AI Act, and ISO/IEC 42001:2023, and no longer carries the NIST AI 600-1:2024 block that the 1.0.3 workbook included. CSA does publish a standalone NIST mapping artifact, but it is titled \"AICM v1.0 mapping to NIST 600-1\" and is keyed to pre-1.1.0 control IDs, which do not carry over.",
            "aliases": [
              {
                "label": "1.1",
                "on_match": "resolve",
                "note": "CSA's artifact page, bundle ZIP, and PDF titles all brand this release v1.1. The workbook stamps itself 1.1.0 in cell A1 of every sheet, which is why 1.1.0 is canonical here."
              },
              {
                "label": "v1.1",
                "on_match": "resolve"
              }
            ]
          },
          {
            "version": "1.0.3",
            "release_date": null,
            "status": "superseded",
            "note": "243 controls. Its workbook carries the NIST AI 600-1:2024 mappings that the 1.1.0 workbook does not. Control IDs are not interchangeable with 1.1.0. CSA publishes no version-specific page for this release — the generic artifact URL now serves v1.1, so obtaining the 1.0.3 workbook requires an archived copy. Release date not asserted: upstream sources conflict (2025-11-10 in one index, a bare \"2024\" in the release metadata), and CSA publishes no changelog that settles it."
          }
        ],
```

**Do not add `0.0.2`.** It is a pre-release draft with no public artifact, and every declared version must have a resolvable tree node.

- [ ] **Step 5: Insert the version level into the AICM tree**

Replace the `(?i)^aicm$` node's entire `children` array with two version nodes, each carrying a copy of the existing domain and control children:

```json
      "children": [
        {
          "patterns": ["^1\\.1\\.0$", "^1\\.1$", "^v1\\.1$"],
          "description": "AICM v1.1.0 (current). CSA brands this release v1.1; the workbook stamps itself 1.1.0.",
          "weight": 100,
          "data": {
            "type": "version",
            "url": "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1",
            "urls": [
              {
                "type": "website",
                "url": "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1"
              },
              {
                "type": "bulk_data",
                "url": "https://cloudsecurityalliance.org/download/artifacts/ai-controls-matrix-v1-1",
                "format": "zip",
                "note": "Direct download (no account required). ZIP bundle: AICM v1.1.0 spreadsheet, AI-CAIQ v1.1.0, introductory guidance, AI-CAIQ instructions, STAR for AI Level 1 submission guide."
              }
            ],
            "note": "247 controls across 18 domains."
          },
          "children": [
            {
              "patterns": ["^[A-Z&]{2,3}$"],
              "description": "AICM v1.1.0 control domain. 17 CCM domains plus MDS (Model Security).",
              "weight": 100,
              "data": {
                "type": "domain",
                "note": "No per-domain web pages. Download the v1.1 bundle and filter the controls sheet by domain code.",
                "examples": [
                  {"input": "MDS", "note": "Model Security — AICM-only domain (not in CCM)"}
                ],
                "known_values": {"MDS": "Model Security (AICM-only domain)"}
              }
            },
            {
              "patterns": ["^[A-Z&]{2,3}-\\d{2}$"],
              "description": "Specific AICM v1.1.0 control (e.g., IAM-01, MDS-01).",
              "weight": 100,
              "data": {
                "type": "control",
                "note": "No per-control web page exists. Download the v1.1 bundle, open the AICM spreadsheet, go to the controls sheet, and find the row where 'Control ID' matches; 'Specifications' holds the full text. WARNING: this ID may designate a different control in 1.0.3 — 54 of the 242 shared IDs were repointed. Do not carry a 1.0.3 reference over by string match.",
                "examples": [
                  {"input": "MDS-01", "note": "No per-control URL — resolve via the v1.1 bundle download"}
                ]
              }
            }
          ]
        },
        {
          "patterns": ["^1\\.0\\.3$"],
          "description": "AICM v1.0.3 (superseded). Last release whose workbook carries NIST AI 600-1 mappings.",
          "weight": 90,
          "data": {
            "type": "version",
            "url": "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix",
            "note": "243 controls. CSA publishes no version-specific page for 1.0.3; the generic artifact URL above now serves v1.1, so obtaining the 1.0.3 workbook requires an archived copy."
          },
          "children": [
            {
              "patterns": ["^[A-Z&]{2,3}$"],
              "description": "AICM v1.0.3 control domain. 17 CCM domains plus MDS (Model Security).",
              "weight": 100,
              "data": {
                "type": "domain",
                "note": "No per-domain web pages. Filter the 1.0.3 controls sheet by domain code.",
                "known_values": {"MDS": "Model Security (AICM-only domain)"}
              }
            },
            {
              "patterns": ["^[A-Z&]{2,3}-\\d{2}$"],
              "description": "Specific AICM v1.0.3 control (e.g., IAM-01, MDS-01).",
              "weight": 100,
              "data": {
                "type": "control",
                "note": "No per-control web page exists. WARNING: this ID may designate a different control in 1.1.0 — 54 of the 242 shared IDs were repointed. LOG-15 here is Output Monitoring; in 1.1.0 it is Input Monitoring.",
                "examples": [
                  {"input": "LOG-15", "note": "Output Monitoring in 1.0.3 — a different control from 1.1.0's LOG-15"}
                ]
              }
            }
          ]
        }
      ]
```

- [ ] **Step 6: Run every check**

```bash
python3 -c "import json; json.load(open('registry/control/org/cloudsecurityalliance.json')); print('valid JSON')"
python3 scripts/test_csa_version_data.py
python3 scripts/validate-version-aliases.py
python3 scripts/validate-registry-schema.py
python3 scripts/validate-urls.py
```
Expected: `valid JSON`; 7 `ok` lines; alias validation clean; schema clean; URL policy clean.

- [ ] **Step 7: Commit**

```bash
git add registry/control/org/cloudsecurityalliance.json scripts/test_csa_version_data.py
git commit -m "Give AICM version-level tree nodes and correct its version record

AICM's tree had no version level, so the resolver never consumed @version:
aicm@9.9#LOG-15 returned found at weight 100. Adding version nodes makes
unknown versions return not_found and makes @1.1 resolve, with no resolver
change — the same structure owasp.org/top10 already uses.

Also corrects the record. AICM 1.0.0-1.0.2 were real but have no retrievable
artifact, so SecID declares only what it can resolve. Adds 1.1.0 (current,
2026-06-22, 247 controls) with 1.1/v1.1 aliases, and dates 1.0.3.

Sets version_required and all_with_guidance because 54 of the 242 control
IDs shared between the releases designate a different control.

Known interim: aicm#LOG-15 without a version now behaves like top10#A01 —
source-level data, subpath dropped, 'specify a version'. That is better
than silently answering with one of two different controls; the richer
all-versions response is R1 in the SecID-Service plan."
```

---

### Task 6: Restructure the AI-CAIQ tree and correct its version data

AI-CAIQ question IDs derive from AICM control IDs, so they inherited the renumbering. Same treatment, three item children instead of two.

**Files:**
- Modify: `registry/control/org/cloudsecurityalliance.json` — the `(?i)^aicm-caiq$` node
- Modify: `scripts/test_csa_version_data.py`

**Interfaces:**
- Consumes: Task 5's `source()`, `data()`, `versions()`, `alias_labels()`, `version_nodes()`
- Produces: nothing

- [ ] **Step 1: Add the failing assertions**

Append to `scripts/test_csa_version_data.py`, before the `if __name__` block:

```python
# ---------- AI-CAIQ ----------

def test_aicaiq_has_version_tree_nodes():
    nodes = version_nodes("aicm-caiq")
    assert "1.1.0" in nodes and "1.0.2" in nodes, sorted(nodes)


def test_aicaiq_version_nodes_carry_all_three_item_levels():
    for v in ("1.1.0", "1.0.2"):
        pats = [k["patterns"][0] for k in version_nodes("aicm-caiq")[v]["children"]]
        assert "^[A-Z&]{2,3}$" in pats, (v, pats)
        assert "^[A-Z&]{2,3}-\\d{2}$" in pats, (v, pats)
        assert "^[A-Z&]{2,3}-\\d{2}\\.\\d+$" in pats, (v, pats)


def test_aicaiq_aliases_match_tree_and_metadata():
    pats = version_nodes("aicm-caiq")["1.1.0"]["patterns"]
    assert pats[0] == "^1\\.1\\.0$", pats
    assert alias_labels("aicm-caiq", "1.1.0") == {"1.1", "v1.1"}


def test_aicaiq_declares_only_resolvable_versions():
    assert "1.0" not in versions("aicm-caiq")


def test_aicaiq_requires_a_version():
    d = data("aicm-caiq")
    assert d["version_required"] is True
    assert d["unversioned_behavior"] == "all_with_guidance"
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 scripts/test_csa_version_data.py`
Expected: FAIL on `test_aicaiq_has_version_tree_nodes`.

- [ ] **Step 3: Replace the AI-CAIQ `data` version fields**

```json
        "version_required": true,
        "unversioned_behavior": "all_with_guidance",
        "version_disambiguation": "AI-CAIQ question IDs are derived from AICM control IDs (XXX-NN.M), so they inherit AICM's renumbering. Between 1.0.2 and 1.1.0 the underlying control IDs moved and the question IDs moved with them — LOG-15.1 in 1.0.2 and LOG-15.1 in 1.1.0 are questions about different controls. Always cite AI-CAIQ questions with an explicit version, and never migrate references by string match; the mapping has to be derived from the underlying AICM control changes, since CSA publishes no crosswalk for either artifact.",
        "versions_available": [
          {
            "version": "1.1.0",
            "release_date": "2026-06-22",
            "status": "current",
            "note": "320 questions. Ships as a standalone workbook inside the AICM v1.1 bundle. Pairs with AICM 1.1.0.",
            "aliases": [
              {
                "label": "1.1",
                "on_match": "resolve",
                "note": "CSA brands the containing bundle v1.1; the questionnaire stamps itself 1.1.0."
              },
              {
                "label": "v1.1",
                "on_match": "resolve"
              }
            ]
          },
          {
            "version": "1.0.2",
            "release_date": null,
            "status": "superseded",
            "note": "Paired with AICM 1.0.3. Question IDs are not interchangeable with 1.1.0."
          }
        ],
```

- [ ] **Step 4: Insert the version level into the AI-CAIQ tree**

Replace the `(?i)^aicm-caiq$` node's `children` with two version nodes, each carrying copies of the three existing item children (domain `^[A-Z&]{2,3}$`, control `^[A-Z&]{2,3}-\d{2}$`, question `^[A-Z&]{2,3}-\d{2}\.\d+$`). Use the same shape as Task 4:

```json
      "children": [
        {
          "patterns": ["^1\\.1\\.0$", "^1\\.1$", "^v1\\.1$"],
          "description": "AI-CAIQ v1.1.0 (current). Ships in the AICM v1.1 bundle.",
          "weight": 100,
          "data": {
            "type": "version",
            "url": "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix-v1-1",
            "urls": [
              {
                "type": "bulk_data",
                "url": "https://cloudsecurityalliance.org/download/artifacts/ai-controls-matrix-v1-1",
                "format": "zip",
                "note": "AI-CAIQ v1.1.0 ships as a standalone workbook inside the AICM v1.1 ZIP bundle."
              }
            ],
            "note": "320 questions."
          },
          "children": [
            {
              "patterns": ["^[A-Z&]{2,3}$"],
              "description": "Domain — returns all AI-CAIQ v1.1.0 questions in this domain. 18 domains (17 CCM + MDS).",
              "weight": 100,
              "data": {
                "type": "domain",
                "note": "No per-domain page. Filter the AI-CAIQ v1.1.0 workbook by domain code.",
                "known_values": {"MDS": "Model Security (AICM-only domain)"}
              }
            },
            {
              "patterns": ["^[A-Z&]{2,3}-\\d{2}$"],
              "description": "Parent AICM v1.1.0 control — returns all its AI-CAIQ questions.",
              "weight": 100,
              "data": {
                "type": "control",
                "note": "WARNING: this control ID may designate a different control in 1.0.2's numbering. Do not carry references across versions by string match."
              }
            },
            {
              "patterns": ["^[A-Z&]{2,3}-\\d{2}\\.\\d+$"],
              "description": "Specific AI-CAIQ v1.1.0 question (e.g., MDS-01.1, IAM-01.2).",
              "weight": 100,
              "data": {
                "type": "question",
                "note": "No per-question web page. Download the v1.1 bundle and find the row in the AI-CAIQ workbook.",
                "examples": [
                  {"input": "MDS-01.1", "note": "No per-question URL — resolve via the v1.1 bundle download"}
                ]
              }
            }
          ]
        },
        {
          "patterns": ["^1\\.0\\.2$"],
          "description": "AI-CAIQ v1.0.2 (superseded). Pairs with AICM 1.0.3.",
          "weight": 90,
          "data": {
            "type": "version",
            "url": "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix",
            "note": "CSA publishes no version-specific page; the generic artifact URL now serves v1.1, so obtaining 1.0.2 requires an archived copy."
          },
          "children": [
            {
              "patterns": ["^[A-Z&]{2,3}$"],
              "description": "Domain — returns all AI-CAIQ v1.0.2 questions in this domain.",
              "weight": 100,
              "data": {
                "type": "domain",
                "known_values": {"MDS": "Model Security (AICM-only domain)"}
              }
            },
            {
              "patterns": ["^[A-Z&]{2,3}-\\d{2}$"],
              "description": "Parent AICM v1.0.3 control — returns all its AI-CAIQ v1.0.2 questions.",
              "weight": 100,
              "data": {
                "type": "control",
                "note": "WARNING: this control ID may designate a different control in 1.1.0's numbering."
              }
            },
            {
              "patterns": ["^[A-Z&]{2,3}-\\d{2}\\.\\d+$"],
              "description": "Specific AI-CAIQ v1.0.2 question (e.g., MDS-01.1, IAM-01.2).",
              "weight": 100,
              "data": {
                "type": "question",
                "note": "No per-question web page. Requires an archived copy of the 1.0.2 workbook."
              }
            }
          ]
        }
      ]
```

- [ ] **Step 5: Run every check**

```bash
python3 -c "import json; json.load(open('registry/control/org/cloudsecurityalliance.json')); print('valid JSON')"
python3 scripts/test_csa_version_data.py
python3 scripts/validate-version-aliases.py
python3 scripts/validate-registry-schema.py
python3 scripts/validate-urls.py
```
Expected: all pass, 12 `ok` lines.

- [ ] **Step 6: Commit**

```bash
git add registry/control/org/cloudsecurityalliance.json scripts/test_csa_version_data.py
git commit -m "Give AI-CAIQ version-level tree nodes and correct its version record

AI-CAIQ question IDs derive from AICM control IDs, so the 1.0.3 -> 1.1.0
renumbering moved them too: LOG-15.1 in 1.0.2 and in 1.1.0 are questions
about different controls. Adds 1.1.0 (current) and 1.0.2, removes the
outdated 1.0 label, and requires an explicit version."
```

---

### Task 7: CCM version metadata (metadata only, deliberately no tree nodes)

CCM has a different defect: SecID lists `4.0`, a real release with no published extraction, and omits `4.0.13`, which has one.

**CCM deliberately does not get version tree nodes.** Adding them would make `ccm#IAM-12` drop the subpath and demand a version — a usability regression for a source whose IDs are broadly stable across 4.0/4.1. That also means CCM's `4.1.0` variant label **cannot be recorded as an alias yet**: aliases only function via tree patterns, and Task 2's validator rejects aliases declared without version nodes. Revisit once R1 lands.

**Files:**
- Modify: `registry/control/org/cloudsecurityalliance.json` — `(?i)^ccm$` node's `data.versions_available`
- Modify: `scripts/test_csa_version_data.py`

**Interfaces:**
- Consumes: Task 5's helpers
- Produces: nothing

- [ ] **Step 1: Add the failing assertions**

```python
# ---------- CCM ----------

def test_ccm_has_4_0_13():
    assert "4.0.13" in versions("ccm"), sorted(versions("ccm"))


def test_ccm_4_0_is_a_real_version_never_an_alias():
    # 4.0.13 supersedes "CCM 4.0 through 4.0.12", so 4.0 is a distinct release.
    assert "4.0" in versions("ccm")
    for entry in versions("ccm").values():
        for alias in entry.get("aliases", []):
            assert alias["label"] != "4.0", "4.0 must never be an alias"


def test_ccm_declares_no_aliases_without_tree_nodes():
    # Aliases only resolve via version tree patterns; CCM has none by choice.
    assert not version_nodes_are_versions("ccm")
    for entry in versions("ccm").values():
        assert not entry.get("aliases"), "CCM cannot carry aliases until it has version nodes"


def version_nodes_are_versions(name: str) -> bool:
    """True if any child of the source node is a declared version."""
    return bool(set(version_nodes(name)) & set(versions(name)))
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 scripts/test_csa_version_data.py`
Expected: FAIL on `test_ccm_has_4_0_13`.

- [ ] **Step 3: Update CCM's `versions_available`**

```json
        "versions_available": [
          {
            "version": "4.1",
            "release_date": "2024-01-01",
            "status": "current",
            "note": "207 controls, 283 CAIQ questions. Incremental update from the 4.0.x line. CSA also labels this release 4.1.0; that variant cannot be registered as an alias until CCM has version-level tree nodes, since aliases resolve through the tree."
          },
          {
            "version": "4.0.13",
            "release_date": null,
            "status": "superseded",
            "note": "Supersedes CCM 4.0 through 4.0.12. A distinct release from 4.0 — not an alias of it."
          },
          {
            "version": "4.0",
            "release_date": "2021-06-01",
            "status": "superseded",
            "note": "197 controls. Original v4 release, later superseded within the 4.0.x line by 4.0.13."
          },
          {
            "version": "3.0.1",
            "release_date": "2017-06-01",
            "status": "superseded",
            "note": "Still referenced in older compliance documentation. Different domain structure from v4."
          }
        ],
```

- [ ] **Step 4: Run every check**

```bash
python3 -c "import json; json.load(open('registry/control/org/cloudsecurityalliance.json')); print('valid JSON')"
python3 scripts/test_csa_version_data.py
python3 scripts/validate-version-aliases.py
python3 scripts/validate-registry-schema.py
```
Expected: all pass, 15 `ok` lines.

- [ ] **Step 5: Commit**

```bash
git add registry/control/org/cloudsecurityalliance.json scripts/test_csa_version_data.py
git commit -m "Add CCM 4.0.13; keep 4.0 as a distinct release

CCM listed 4.0, a real release with no published extraction, and omitted
4.0.13, which has one. 4.0.13's own metadata records that it supersedes
'CCM 4.0 through 4.0.12', so 4.0 is a separate release and must never be
aliased to it.

No version tree nodes for CCM by choice: adding them would make ccm#IAM-12
demand a version, and CCM's IDs are broadly stable across 4.0/4.1. That
also defers the 4.1.0 variant label, since aliases resolve via the tree."
```

---

### Task 8: Repoint the 19 outdated `@1.0` references

`aicm@1.0` and `aicm-caiq@1.0` name a release that never existed, and they appear in `README.md` and `SPEC.md` — so the wrong version is SecID's most visible AICM example.

**Files:** `README.md`, `SPEC.md`, `docs/explanation/RATIONALE.md`, `registry/regulation.md`, `registry/control.md`, `registry/control/org/cloudsecurityalliance.md`

- [ ] **Step 1: Record the starting count**

```bash
grep -rEc "aicm(-caiq)?@1\.0([^.0-9]|$)" --include="*.md" --include="*.json" . \
  | grep -v docs/superpowers | grep -v ':0$'
```
Expected: 6 files, 19 matches (16 `aicm@1.0`, 3 `aicm-caiq@1.0`).

- [ ] **Step 2: Rewrite to `@1.1.0`**

```bash
grep -rEl "aicm(-caiq)?@1\.0([^.0-9]|$)" --include="*.md" --include="*.json" . \
  | grep -v docs/superpowers \
  | xargs sed -i '' -E 's/(aicm(-caiq)?)@1\.0([^.0-9]|$)/\1@1.1.0\3/g'
```
`sed -i ''` is the BSD/macOS form; on Linux use `sed -i` with no argument.

- [ ] **Step 3: Verify**

```bash
echo "--- remaining @1.0 refs (want none) ---"
grep -rEn "aicm(-caiq)?@1\.0([^.0-9]|$)" --include="*.md" --include="*.json" . \
  | grep -v docs/superpowers || echo "  none"
echo "--- new refs (want 19) ---"
grep -rEc "aicm(-caiq)?@1\.1\.0" --include="*.md" --include="*.json" . \
  | grep -v docs/superpowers | grep -v ':0$'
echo "--- no double substitution ---"
grep -rn "1\.1\.0\.0" --include="*.md" --include="*.json" . || echo "  none"
```

- [ ] **Step 4: Confirm registry files still parse**

```bash
python3 -c "
import json, glob
for f in glob.glob('registry/**/*.json', recursive=True): json.load(open(f))
print('all registry JSON parses')
"
python3 scripts/validate-registry-schema.py
```

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "Repoint 19 outdated aicm@1.0 references to @1.1.0

aicm@1.0 names AICM 1.0.0 (July 2025), a real release long superseded --
1.0.3 supersedes 1.0.0-1.0.2 -- with no retrievable artifact. Examples
should cite the current release. These 19 references (16 aicm, 3 aicm-caiq)
spanned README.md, SPEC.md, RATIONALE.md and three registry files, so the
project's most visible AICM example cited a nonexistent version."
```

---

### Task 9: ADR-009 and the specification updates

**Files:** `DECISIONS.md`, `docs/reference/VERSIONING.md`, `SPEC.md`, `docs/reference/API-RESPONSE-FORMAT.md`

- [ ] **Step 1: Correct ADR-006's false claim**

In ADR-006's **Decision** paragraph, replace `CI verifies they don't drift.` with:

```markdown
(Correction, 2026-07-31: this originally claimed "CI verifies they don't drift." No such check exists — all three workflows trigger only on `registry/**/*.json` and nothing watches `.md`. The AICM entry proved it: `.md` read `versions: ["1.0"]` while `.json` read `1.0.3`, unflagged. Treat `.md` as legacy; JSON is the format that ships.)
```

- [ ] **Step 2: Append ADR-009**

```markdown
---

## ADR-009: Version aliases, and making the version qualifier load-bearing

**Date:** 2026-07-31
**Status:** Accepted
**Decision method:** Design session, recorded in [`docs/superpowers/specs/2026-07-31-version-aliases-design.md`](docs/superpowers/specs/2026-07-31-version-aliases-design.md)

**Goal:** Let one release carry more than one official label, and make `@version` mean something.

**Context:** Publishers label releases inconsistently. CSA stamps the AICM workbook `1.1.0` while branding the same release "v1.1" on its download page; for CCM it does the reverse, with `4.1` canonical and `4.1.0` the variant. SecID had no way to express this — the schema's only alias field, `alias_of`, is namespace-level and unused across all 2,130 files.

Separately, `aicm@9.9#LOG-15` returned `found` at weight 100. Live probing showed this is a *data* defect, not a resolver one: `owasp.org/top10@9999#A01` correctly returns `not_found` with the available versions listed. A version is validated only when the source has version-level tree nodes **and** the query carries a subpath, since only a subpath forces the walk through the version level. AICM's tree had no version level.

This mattered because AICM 1.1.0 renumbered controls in place: 54 of the 242 IDs present in both 1.0.3 and 1.1.0 designate a different control, while only one ID disappeared — so an ID set-difference reports six changed rows and misses all 54. CSA published no crosswalk, and the mapping had to be reconstructed from specification-text similarity with 9 rows still unresolved. Once a renumbering ships unmapped, it is not fully recoverable.

**Decision:**

1. **The registry layer owns label aliases.** One authority labelling one artifact two ways is disambiguation. Cross-release *control* mapping is equivalence and succession, and belongs to the Relationship layer. MITRE ATT&CK draws the same line (`revoked-by` is a relationship; the ID stays resolvable), as does library authority control (MARC `4XX` variant labels versus `5XX` related entities).
2. **Two layers, bound by a validator.** The pattern tree matches — version nodes carry the canonical string as `patterns[0]` and aliases as further OR-alternatives. `versions_available` describes — dates, status, notes, `on_match`. `scripts/validate-version-aliases.py` asserts they agree in both directions.
3. **`patterns[0]` must be a clean literal.** No optional groups: `^2(\.0)?$` matches both `2` and `2.0` but leaves nothing to canonicalize to.
4. **Each alias carries a required `on_match`:** `"resolve"` returns data inline (`found`); `"redirect"` returns empty results (`corrected`) with the canonical SecID in the message.
5. **Aliases are curated, never derived.** AICM and CCM canonicalize in opposite directions, so no rule derives both.
6. **An alias may never shadow a real version.** CCM `4.0` is a genuine release superseded by `4.0.13`.
7. **An alias without version tree nodes is rejected** — it would be documentation that never resolves.
8. **The resolver never returns item data from a version the caller did not ask for.**
9. **Where item IDs are unstable across releases, omitting the version returns all of them** (`version_required: true`, `unversioned_behavior: "all_with_guidance"`). Applied to AICM and AI-CAIQ.

**Rationale:** Prior art converges on one rule — if the loose form should never be used again, redirect; if it is legitimately reachable, serve the data and declare the canonical form. That is HTTP's `301` versus `rel="canonical"` distinction, and it recurs in npm dist-tags, Go module queries, Docker tags, and Debian codenames. CSA's "v1.1" is on CSA's own download page, so `resolve` is the normal case.

Loud failure on unknown versions is chosen over a plausible-looking answer because a wrong version is a wrong control. A failure gets reported and fixed; a wrong control gets cited.

**Rejected alternatives:**
- **A fifth response status (`alias`)** — breaks PRINCIPLES #4's four outcomes and forces a coordinated release across four repos.
- **Aliases in `versions_available` only** — metadata does not match; the tree does. They would never resolve.
- **Aliases as tree patterns only** — no home for dates, status, notes, or `on_match`, none of which a regex can carry.
- **Deriving `versions_available` from the tree** — impossible for the same reason.
- **Deriving aliases by prefix or `v`-stripping** — unsound on SecID's own data; it would have aliased CCM `4.0` to `4.0.13`, silently repointing a real release.
- **Pure redirect with no data for all aliases** — doubles round trips in the MCP channel where each costs an inference step, and empirically fails to change client behavior.
- **Returning the nearest version's item data** (previously documented in `docs/reference/VERSIONING.md`) — its own example used `IAM-12`, one of the 54 renumbered AICM IDs.
- **Version tree nodes for CCM** — would make `ccm#IAM-12` demand a version, for a source whose IDs are broadly stable.

**Deferred:** alias chains; one label on multiple versions; tracking aliases (`v1` → latest `1.y.z`) as a source-level `version_tracks` field; an explicit `@*` version wildcard; a `missing-version` feedback category; per-item "this ID changed meaning" metadata, which needs SecID to host AICM content and is gated on CSA legal confirmation ([`DATA-HOSTING-RULES.md`](docs/reference/DATA-HOSTING-RULES.md) line 79) plus a license-matrix row for the CC BY-NC **non-commercial** clause.
```

- [ ] **Step 3: Remove the "Nearest:" substitution from VERSIONING.md**

Replace the "Version miss" block (currently lines 138-146) with:

```markdown
Version miss (requested version doesn't exist):
```
Query:    secid:control/cloudsecurityalliance.org/aicm@9.9#LOG-15
Response: Version "9.9" is not a known version of aicm.
          Known versions: 1.1.0 (current, 2026-06-22; aliases 1.1, v1.1),
                          1.0.3 (superseded).
          To list versions, describe the source without a version.
          Report a genuinely missing release via the submit_feedback tool
          (include a source URL) or https://github.com/CloudSecurityAlliance/SecID/issues
Status:   not_found
```

**The resolver does not substitute a nearby version's item data.** An earlier
version of this document returned "Nearest: here's IAM-12 from v4.0" with a
soft compatibility warning. That is unsafe: `IAM-12` is one of the 54 AICM
control IDs that designate a different control in 1.1.0 than in 1.0.3, so the
substitute answer would be confidently wrong. A wrong version is a wrong
control. See [ADR-009](../../DECISIONS.md).

Without a subpath the same query is a discovery question rather than a
resolution one, so `secid:control/cloudsecurityalliance.org/aicm@9.9` returns
`related` with the version list rather than `not_found`.
```

- [ ] **Step 4: Add the alias subsection to SPEC.md §5.1**

Immediately after the "Versionless References" subsection:

```markdown
#### Version Aliases

One release can carry more than one official label. CSA stamps the AICM
workbook `1.1.0` in cell A1 of every sheet while branding the same release
"v1.1" on its download page — and does the reverse for CCM, where `4.1` is
canonical and `4.1.0` is the variant. Both labels circulate; neither is wrong.

The registry records the canonical version plus its aliases, so both resolve:

```
secid:control/cloudsecurityalliance.org/aicm@1.1.0#LOG-15   # canonical
secid:control/cloudsecurityalliance.org/aicm@1.1#LOG-15     # alias — same control
```

Matching happens in the pattern tree: a versioned source has version-level
nodes whose `patterns[0]` is the canonical string and whose remaining patterns
are its aliases. Because the direction of canonicalization is inconsistent even
within one publisher, aliases are curated data — never derived by prefix
matching or `v`-stripping — and an alias may never shadow a real version.
CCM `4.0` is a genuine release superseded by `4.0.13`, not a short form of it.

**Unknown versions fail rather than guess.** A version matching no node returns
`not_found` when a subpath is present. The resolver never substitutes item data
from a version the caller did not name — for sources like AICM, where 54 control
IDs changed meaning between releases, a substitute answer would be confidently
wrong. See [DECISIONS.md ADR-009](DECISIONS.md).
```

- [ ] **Step 5: Update the feedback-channel statement**

In `docs/reference/API-RESPONSE-FORMAT.md` line 384, replace `There is no web-form submission link in the response.` with:

```markdown
As of ADR-009, `not_found` responses also carry https://github.com/CloudSecurityAlliance/SecID/issues, because raw API and bulk-data consumers include humans who otherwise had no channel at all. MCP clients should still prefer the `submit_feedback` tool, which records the miss server-side for backlog aggregation; a GitHub issue does not.
```

- [ ] **Step 6: Verify**

```bash
python3 scripts/validate-registry-schema.py
python3 scripts/validate-version-aliases.py
python3 scripts/test_csa_version_data.py
grep -c "ADR-009" DECISIONS.md SPEC.md docs/reference/VERSIONING.md
grep -n "Nearest:" docs/reference/VERSIONING.md || echo "  'Nearest:' removed as intended"
```

- [ ] **Step 7: Commit**

```bash
git add DECISIONS.md SPEC.md docs/reference/VERSIONING.md docs/reference/API-RESPONSE-FORMAT.md
git commit -m "Add ADR-009 for version aliases; drop nearest-version substitution

Records the design and the rule that makes it worth having: the resolver
never returns item data from a version the caller did not ask for.
VERSIONING.md previously specified returning the nearest version's control
with a soft warning, and its own example used IAM-12 — one of the 54 AICM
IDs that designate a different control across releases.

Also corrects ADR-006's claim that CI verifies .md/.json drift. It does
not; no workflow watches .md."
```

---

### Task 10: Record deferred items, verify end to end, open the PR

**Files:** `docs/project/TODO.md`

- [ ] **Step 1: Append the deferred items**

```markdown
## Version aliases (from ADR-009, 2026-07-31)

See [the design spec](../superpowers/specs/2026-07-31-version-aliases-design.md).
None of these has a current requirement; none should be built speculatively.

- [ ] **Alias chains.** One hop only. Revisit only on a concrete need.
- [ ] **One label on multiple versions.** Currently a hard validation error. If a need appears, the natural shape is resolving to all matching versions with disambiguation — which `unversioned_behavior: "all_with_guidance"` already does.
- [ ] **Tracking aliases** (`v1` → latest `1.y.z`). A source-level `version_tracks` field, *not* an `aliases[]` entry — nesting fixes the target, so a moving pointer cannot live there. A track collapses into a fixed alias once its major line closes (`CCM v3` → `3.0.1`). Deliberately unbuilt: moving pointers are the hazard ADR-009 addresses; Maven removed `LATEST` and Debian warns against `stable` for the same reason.
- [ ] **CCM version tree nodes**, which would then allow registering `4.1.0` as an alias of `4.1`. Blocked on R1: today, adding version nodes makes `ccm#IAM-12` drop the subpath and demand a version.
- [ ] **Decide the CCM v3 alias.** The v3 line is closed, so `3` or `v3` could safely alias `3.0.1` — but `3.0` was itself a real release that `3.0.1` supersedes, so which string may alias needs a judgment call.
- [ ] **`@*` version wildcard.** Unnecessary for now: omitting the version returns all versions, and `describe` returns the list. Extending frozen grammar needs its own ADR.
- [ ] **`missing-version` feedback category** in `submit_feedback` (its enum is `missing-namespace | correction | suggestion`; a missing version is none of those).
- [ ] **A human feedback channel** distinct from URLs embedded in machine responses.
- [ ] **Per-item "this ID changed meaning" metadata**, for when SecID hosts AICM content rather than only describing how to fetch it. Precision matters: 188 of the 242 shared IDs did *not* change meaning, so a blanket per-ID warning would be crying wolf. Gated on CSA legal confirmation (`DATA-HOSTING-RULES.md` line 79) and on Rule 0's license matrix gaining a row for the CC BY-**NC** non-commercial clause, which it currently lacks.
- [ ] **AICM 1.0.3 has no live source.** CSA publishes no version-specific page (`.../artifacts/ai-controls-matrix-v1-0-3` returns 404) and the generic URL now serves v1.1. This is exactly the persistence risk in DATA-HOSTING-RULES Rule 1.
- [ ] **Resolve the 208 `versions_available: []` entries** to `null` or real data. An empty array is neither "researched, found nothing" (`null`) nor "not researched" (absent) — most likely a YAML→JSON conversion artifact.
- [ ] **Audit the 139 single-version sources** before giving any of them version tree nodes. Where the single entry means "current only, history not enumerated", the history is incomplete.
- [ ] **Stale-format doc cleanup** (separate PR): `REGISTRY-FORMAT.md` still says "Current Format: YAML + Markdown", "will migrate to JSON", and "Seven pilot `.json` files already exist"; `REGISTRY-JSON-FORMAT.md` calls JSON the "target" format; `CLAUDE.md` calls `.md` authoritative. Reality: 2,130 JSON files at 100% coverage, deployed to KV.
- [ ] **Status vocabulary drift** (separate PR): `PRINCIPLES.md` and `VERSIONING.md` use `exact_match`/`corrected_match`/`no_match_but_related`; `API-RESPONSE-FORMAT.md` and the live API use `found`/`corrected`/`related`/`not_found`.
```

- [ ] **Step 2: Full validation sweep**

```bash
for s in validate-registry-schema validate-urls validate-type-list validate-subtypes validate-version-aliases; do
  echo "--- $s ---"; python3 "scripts/$s.py" || echo "FAILED: $s"
done
python3 scripts/test_validate_version_aliases.py
python3 scripts/test_csa_version_data.py
```
Expected: every one exits 0.

- [ ] **Step 3: Commit and push**

```bash
git add docs/project/TODO.md
git commit -m "Record version-alias items deferred by ADR-009"
git push -u origin feat/version-aliases
```

- [ ] **Step 4: Open the PR**

```bash
gh pr create --title "Version aliases: AICM/AI-CAIQ version tree nodes, validation, and version-record fixes" --body "$(cat <<'EOF'
Implements Plan 1 of ADR-009.

## The core fix is structural, and it is data-only

`aicm@9.9#LOG-15` returned `found` at weight 100. That is a **data** defect:
`owasp.org/top10@9999#A01` already returns `not_found` with the available
versions listed. A version is validated only when the source has version-level
tree nodes *and* the query carries a subpath — and AICM's tree had no version
level, so `@version` was never consumed.

Giving AICM and AI-CAIQ version nodes makes `@9.9` return `not_found` and
`@1.1` resolve, **with no resolver change**.

## What this does

- Adds `$defs/VersionEntry` / `$defs/VersionAlias` and `scripts/validate-version-aliases.py`
  (19 offline tests), wired into CI
- Restructures AICM and AI-CAIQ trees with version-level nodes; aliases are
  OR-patterns on those nodes, with `patterns[0]` the canonical literal
- Corrects the records. AICM 1.0.0-1.0.2 were real releases with no retrievable
  artifact, so SecID declares only resolvable ones. Adds 1.1.0 (current,
  2026-06-22, 247 controls) and dates 1.0.3; adds AI-CAIQ 1.1.0 and 1.0.2
- Sets `version_required` + `all_with_guidance` on both, because 54 of the 242
  control IDs shared between AICM 1.0.3 and 1.1.0 designate a different control
- Adds CCM 4.0.13, keeping 4.0 as the distinct release it is
- Repoints 19 outdated `@1.0` references across README, SPEC, RATIONALE and 3 registry files
- Adds ADR-009; removes the nearest-version substitution from VERSIONING.md

## Known interim behavior change

`aicm#LOG-15` with no version now behaves like `top10#A01` — source-level data,
subpath dropped, "specify a version". That is better than silently answering
with one of two different controls. The richer all-versions response is R1 in
the SecID-Service plan.

## Regex safety

New patterns are exact anchored literals (`^1\.1\.0$`, `^1\.1$`, `^v1\.1$`) with
no quantifiers, alternation, or nesting — no backtracking risk. Existing item
patterns are copied verbatim under each version node.

## Why aliases are curated, not derived

CSA canonicalizes in opposite directions across its two flagship frameworks:
AICM's canonical is the 3-part `1.1.0` with `1.1` the alias; CCM's is the 2-part
`4.1` with `4.1.0` the alias. No rule derives both. And CCM `4.0` is a genuine
release that `4.0.13` supersedes, so prefix-matching would have silently
repointed it. The validator rejects any alias shadowing a real version.
EOF
)"
```

- [ ] **Step 5: Verify CI**

Run: `gh pr checks --watch`
Expected: `Validate registry` and `Validate subtypes` pass.

- [ ] **Step 6: Post-merge live verification**

The resolver serves from KV, so behavior can only be confirmed after merge and deploy (~1m20s). Once the deploy chain completes:

```bash
base="https://secid.cloudsecurityalliance.org/api/v1/resolve?secid="
for q in "secid:control/cloudsecurityalliance.org/aicm@1.1.0%23LOG-15" \
         "secid:control/cloudsecurityalliance.org/aicm@1.1%23LOG-15" \
         "secid:control/cloudsecurityalliance.org/aicm@9.9%23LOG-15" \
         "secid:control/cloudsecurityalliance.org/aicm%23LOG-15"; do
  printf "\n== %s\n" "$q"; curl -s "${base}${q}" | head -c 400; echo
done
```

Expected after this plan (R1–R3 still outstanding):

| Query | Expected now | After Plan 2 |
|---|---|---|
| `aicm@1.1.0#LOG-15` | `found` | unchanged |
| `aicm@1.1#LOG-15` | `found`, echoing `@1.1` | canonicalized to `@1.1.0` + `version_matched_alias` (R3) |
| `aicm@9.9#LOG-15` | **`not_found`** with versions listed | unchanged |
| `aicm#LOG-15` | `related`, subpath dropped, "specify a version" | per-version results (R1) |

If `@9.9` still returns `found`, check the deploy chain per CLAUDE.md's CI/CD section before assuming the data is wrong.

---

## Follow-on plans

Written separately, because each produces working, testable software on its own.

**Plan 2 — SecID-Service resolver.** R1 (unversioned + subpath returns per-version results — the only genuinely missing capability), R2 (unknown version without a subpath returns `related` rather than `found`), R3 (alias canonicalization and `version_matched_alias`), R4 (`on_match: redirect`, not needed until a redirect alias exists). R1 also unblocks CCM version nodes.

**Plan 3 — The version-data sweep.** The large data effort: resolve the 208 empty `versions_available` arrays, audit the 139 single-version sources, and give version tree nodes to sources that need them. Independent of Plans 1 and 2 and can run in parallel.

**Suggested order:** Plan 1 → Plan 2 → Plan 3.
