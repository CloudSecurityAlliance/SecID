# Version Aliases — Registry Plan (Plan 1 of 3) Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make version aliases expressible and enforced in SecID registry data, and correct the AICM/AI-CAIQ/CCM version records that are currently wrong.

**Architecture:** Aliases nest inside each `versions_available[]` entry in a `match_node`'s `data`, carrying a required `on_match` field (`resolve` or `redirect`). Because `match_nodes[].data` is `additionalProperties: true`, JSON Schema cannot reach inside it — so the schema gains `$defs` as documented shape while a new `scripts/validate-version-aliases.py` does the real enforcement, wired into the existing `Validate registry` workflow.

**Tech Stack:** Python 3.12, `jsonschema` (pip), GitHub Actions. No build system; validation scripts are the test suite.

**Spec:** [`docs/superpowers/specs/2026-07-31-version-aliases-design.md`](../specs/2026-07-31-version-aliases-design.md). Decision IDs (D1–D10) below refer to that document.

## Global Constraints

- **Python 3.12.** CI uses `actions/setup-python@v5` with `python-version: "3.12"`.
- **Validation scripts are hyphenated** (`validate-version-aliases.py`); their tests are underscored (`test_validate_version_aliases.py`) and load the module via `importlib.util.spec_from_file_location`. Follow `scripts/test_validate_urls.py` exactly.
- **Tests are dual-runnable:** plain `assert` functions named `test_*`, plus an `if __name__ == "__main__":` block that runs them all. Discoverable by pytest but must not require it.
- **`match_nodes[].data` stays `additionalProperties: true`.** Do not constrain it.
- **`on_match` values are exactly `"resolve"` and `"redirect"`.** Unrecognized values cause the alias entry to be ignored by resolvers, but are a hard validation error at PR time.
- **Absent vs null:** absent `versions_available` means "not researched"; `null` means "researched, none found". Both are valid and neither is an error.
- **AICM renumbering count is 54**, not 55. Source of truth is `crosswalks/aicm-1.0.3-to-1.1.0-crosswalk.csv` in the DataSets repo, not its prose docs.
- **Never lossily normalize** an alias label — store it exactly as the publisher writes it (PRINCIPLES #7).
- **Branch, never commit to `main`.** Work continues on `feat/version-aliases`.
- **JSON registry changes merged to `main` auto-deploy to the live resolver.** Every task that touches `registry/**/*.json` must leave the registry valid.

---

### Task 1: Schema `$defs` for version entries and aliases

Adds the documented shape. Enforcement comes in Task 2 — this task alone changes no behavior, which is why it is separable.

**Files:**
- Modify: `schemas/registry-namespace.schema.json:191-199` (append after the `Tags` `$def`)
- Modify: `docs/reference/REGISTRY-JSON-FORMAT.md:1288` (the `versions_available` row in the Version Resolution Fields table)

**Interfaces:**
- Consumes: nothing
- Produces: `#/$defs/VersionEntry` and `#/$defs/VersionAlias` — referenced by name in Task 2's validator docstring and by `REGISTRY-JSON-FORMAT.md`

- [ ] **Step 1: Confirm the current tail of the schema**

Run: `python3 -c "import json;d=json.load(open('schemas/registry-namespace.schema.json'));print(list(d['\$defs']))"`
Expected: `['UrlObject', 'MatchNode', 'Tags']`

- [ ] **Step 2: Add the two `$defs`**

In `schemas/registry-namespace.schema.json`, inside `"$defs"`, after the `"Tags"` object's closing brace, add a comma and then:

```json
    "VersionAlias": {
      "type": "object",
      "description": "An alternate label for the version this object is nested under. Aliases exist because publishers routinely label one release two ways — CSA stamps the AICM workbook 1.1.0 while branding the same release 'v1.1' on its download page. Nesting encodes the target: the alias means the version entry that contains it, so there is no pointer to dangle. Aliases are immutable once published and never chain. Not schema-enforced here (versions_available lives inside match_nodes[].data, which is additionalProperties:true) — see scripts/validate-version-aliases.py.",
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
          "description": "What a resolver does when this label is matched. 'resolve' returns full data inline with status 'found' and version_matched_alias set — for co-equal publisher labels. 'redirect' returns empty results with status 'corrected' and the canonical SecID in the message, forcing a second request — for labels that should be retired. Reserved for future use: 'track' (a moving pointer to the latest matching version) is deliberately unimplemented; resolvers must ignore alias entries whose on_match they do not recognize."
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
      "description": "One known version of a source, as used in a match_node's data.versions_available array. Not schema-enforced here (data is additionalProperties:true) — see scripts/validate-version-aliases.py.",
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
          "description": "Anything a consumer needs to know about this specific version — control counts, mapping changes, ID-stability warnings."
        },
        "aliases": {
          "type": "array",
          "description": "Alternate labels for this version.",
          "items": { "$ref": "#/$defs/VersionAlias" }
        }
      },
      "additionalProperties": true
    }
```

- [ ] **Step 3: Verify the schema is still valid JSON and a valid JSON Schema**

Run:
```bash
python3 -c "
import json, jsonschema
d = json.load(open('schemas/registry-namespace.schema.json'))
jsonschema.Draft202012Validator.check_schema(d)
print('defs:', list(d['\$defs']))
"
```
Expected: `defs: ['UrlObject', 'MatchNode', 'Tags', 'VersionAlias', 'VersionEntry']` and no exception.

- [ ] **Step 4: Verify the existing registry still validates**

Run: `python3 scripts/validate-registry-schema.py`
Expected: PASS. The new `$defs` are unreferenced from any enforced path, so nothing should change.

- [ ] **Step 5: Document the field in REGISTRY-JSON-FORMAT.md**

In `docs/reference/REGISTRY-JSON-FORMAT.md`, replace the `versions_available` row of the Version Resolution Fields table with:

```markdown
| `versions_available` | array, optional | Array of objects documenting known versions. Each object has: `version` (string, required), `release_date` (string, ISO date, optional), `status` (string: `"current"`, `"superseded"`, `"draft"`, optional), `note` (string, optional), `aliases` (array, optional). See `$defs/VersionEntry` in the JSON Schema. |
```

Then add this subsection immediately after the Unversioned Behavior Values table:

```markdown
##### Version Aliases

Publishers routinely label one release two ways. CSA stamps `{"specification_version":"1.1.0"}` in cell A1 of the AICM workbook while branding the same release "v1.1" on its download page — and does the reverse for CCM, where `4.1` is canonical and `4.1.0` is the variant. Because the direction is inconsistent even within one publisher, aliases are curated data and are never derived by prefix matching or `v`-stripping.

Each `versions_available[]` entry may carry an `aliases` array. Nesting encodes the target — an alias means the version entry containing it.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `label` | string | yes | The alias exactly as the publisher writes it. Never normalized. |
| `on_match` | string | yes | `"resolve"` (return data inline, status `found`) or `"redirect"` (return empty results, status `corrected`, canonical SecID in the message). |
| `note` | string | no | Where the label appears, or why. |

```json
{
  "version": "1.1.0",
  "release_date": "2026-06-22",
  "status": "current",
  "aliases": [
    { "label": "1.1",  "on_match": "resolve", "note": "CSA's download page brands this v1.1." },
    { "label": "v1.1", "on_match": "resolve" }
  ]
}
```

**Rules.** An alias is immutable once published and is never re-pointed. Aliases never chain — one hop to a concrete version. An alias label must be unique within its source and must never equal a real version string there: CCM `4.0` is a genuine release that `4.0.13` supersedes, so `4.0` may not be an alias of `4.0.13`. Resolvers must ignore alias entries whose `on_match` they do not recognize, so reserved values can ship later without breaking deployed resolvers.

These rules are enforced by `scripts/validate-version-aliases.py`, not by JSON Schema — `versions_available` lives inside `match_nodes[].data`, which is `additionalProperties: true` and therefore unreachable by `$ref`. The `$defs` are the documented shape; the script is the constraint.
```

- [ ] **Step 6: Commit**

```bash
git add schemas/registry-namespace.schema.json docs/reference/REGISTRY-JSON-FORMAT.md
git commit -m "Add VersionEntry/VersionAlias schema defs and document version aliases

Documents the shape only. versions_available lives inside
match_nodes[].data, which is additionalProperties:true, so a \$ref there
is unreachable by the schema validator — enforcement lands in
scripts/validate-version-aliases.py."
```

---

### Task 2: Validation script and tests

The enforcement layer. Written before any registry data changes so the new AICM/CCM data is validated as it is authored.

**Files:**
- Create: `scripts/validate-version-aliases.py`
- Create: `scripts/test_validate_version_aliases.py`

**Interfaces:**
- Consumes: `$defs/VersionEntry`, `$defs/VersionAlias` from Task 1 (as documented shape, referenced in the docstring)
- Produces:
  - `node_label(node: dict) -> str`
  - `collect_sources(doc: dict) -> list[tuple[str, object]]`
  - `check_source_versions(versions_available, source_label: str) -> list[str]`
  - `main() -> int` (exit code: 0 clean, 1 violations found)

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

# The script is hyphenated (validate-version-aliases.py), so load it explicitly.
_spec = importlib.util.spec_from_file_location(
    "validate_version_aliases",
    Path(__file__).resolve().parent / "validate-version-aliases.py",
)
_mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_mod)
check_source_versions = _mod.check_source_versions
collect_sources = _mod.collect_sources
node_label = _mod.node_label


def test_clean_aliases_pass():
    va = [
        {"version": "1.1.0", "aliases": [
            {"label": "1.1", "on_match": "resolve"},
            {"label": "v1.1", "on_match": "resolve"},
        ]},
        {"version": "1.0.3"},
    ]
    assert check_source_versions(va, "aicm") == []


def test_absent_and_null_are_valid():
    # null means "researched, none found" — not an error.
    assert check_source_versions(None, "cve") == []


def test_missing_version_rejected():
    errs = check_source_versions([{"release_date": "2026-06-22"}], "x")
    assert any("version" in e for e in errs), errs


def test_duplicate_version_rejected():
    errs = check_source_versions([{"version": "1.0.3"}, {"version": "1.0.3"}], "x")
    assert any("duplicate version" in e for e in errs), errs


def test_alias_label_colliding_with_real_version_rejected():
    # The CCM trap: 4.0 is a genuine release that 4.0.13 supersedes.
    va = [
        {"version": "4.0.13", "aliases": [{"label": "4.0", "on_match": "resolve"}]},
        {"version": "4.0"},
    ]
    errs = check_source_versions(va, "ccm")
    assert any("real version" in e for e in errs), errs


def test_duplicate_alias_label_rejected():
    va = [
        {"version": "1.1.0", "aliases": [{"label": "1.1", "on_match": "resolve"}]},
        {"version": "1.1.3", "aliases": [{"label": "1.1", "on_match": "resolve"}]},
    ]
    errs = check_source_versions(va, "x")
    assert any("duplicate alias label" in e for e in errs), errs


def test_missing_on_match_rejected():
    errs = check_source_versions([{"version": "1.1.0", "aliases": [{"label": "1.1"}]}], "x")
    assert any("on_match" in e for e in errs), errs


def test_unknown_on_match_rejected():
    va = [{"version": "1.1.0", "aliases": [{"label": "1.1", "on_match": "teleport"}]}]
    errs = check_source_versions(va, "x")
    assert any("on_match" in e for e in errs), errs


def test_empty_label_rejected():
    va = [{"version": "1.1.0", "aliases": [{"label": "  ", "on_match": "resolve"}]}]
    assert check_source_versions(va, "x")


def test_wrong_types_rejected():
    assert check_source_versions("1.1.0", "x")
    assert check_source_versions([{"version": "1.1.0", "aliases": "1.1"}], "x")
    assert check_source_versions(["1.1.0"], "x")


def test_node_label_strips_regex_furniture():
    assert node_label({"patterns": ["(?i)^aicm$"]}) == "aicm"
    assert node_label({"patterns": []}) == "<unnamed>"


def test_collect_sources_only_returns_nodes_declaring_the_key():
    doc = {"match_nodes": [
        {"patterns": ["(?i)^aicm$"], "data": {"versions_available": [{"version": "1.1.0"}]}},
        {"patterns": ["(?i)^star$"], "data": {}},
        {"patterns": ["(?i)^cve$"], "data": {"versions_available": None}},
    ]}
    got = collect_sources(doc)
    assert got == [("aicm", [{"version": "1.1.0"}]), ("cve", None)], got


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
```

- [ ] **Step 2: Run the tests to verify they fail**

Run: `python3 scripts/test_validate_version_aliases.py`
Expected: FAIL — `FileNotFoundError` on `validate-version-aliases.py`, because the module does not exist yet.

- [ ] **Step 3: Write the implementation**

Create `scripts/validate-version-aliases.py`:

```python
#!/usr/bin/env python3
"""Validate versions_available and version aliases across registry JSON files.

Why a script and not JSON Schema: versions_available lives inside
match_nodes[].data, and data is additionalProperties:true by design, so a
$ref there is unreachable by the schema validator. The schema's
$defs/VersionEntry and $defs/VersionAlias are the documented shape; this
script is the actual constraint. Same split the $defs/Tags docstring
already describes for data.tags.

Rules enforced, per source (per match_node):
  1. every versions_available entry has a non-empty string `version`
  2. version strings are unique within the source
  3. every alias has a non-empty string `label` and an `on_match` of
     "resolve" or "redirect"
  4. alias labels are unique within the source
  5. an alias label never equals a real version string in the same source

Rule 5 is the one that catches real mistakes: CSA's CCM 4.0 is a genuine
release that 4.0.13 supersedes, so aliasing 4.0 -> 4.0.13 would silently
repoint a real version. Aliases must never shadow a real version.

Absent or null versions_available is valid. Per the null-vs-absent
convention, absent means "not yet researched" and null means "researched,
found nothing" — neither is an error.

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
import sys
from pathlib import Path

VALID_ON_MATCH = ("resolve", "redirect")


def node_label(node: dict) -> str:
    """Best-effort readable source name from a match_node's first pattern."""
    patterns = node.get("patterns") or []
    if not patterns or not isinstance(patterns[0], str):
        return "<unnamed>"
    return patterns[0].replace("(?i)", "").strip("^$")


def collect_sources(doc: dict) -> list[tuple[str, object]]:
    """Return (source_label, versions_available) for each node declaring the key.

    Nodes without the key are skipped: absent means "not yet researched",
    which is not something to validate.
    """
    out: list[tuple[str, object]] = []
    for node in doc.get("match_nodes") or []:
        if not isinstance(node, dict):
            continue
        data = node.get("data") or {}
        if isinstance(data, dict) and "versions_available" in data:
            out.append((node_label(node), data["versions_available"]))
    return out


def check_source_versions(versions_available, source_label: str) -> list[str]:
    """Validate one source's versions_available. Returns a list of error strings."""
    if versions_available is None:
        return []
    if not isinstance(versions_available, list):
        return [f"{source_label}: versions_available must be an array or null"]

    errors: list[str] = []
    seen_versions: set[str] = set()

    # Pass 1: collect and validate the real version strings.
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

    # Pass 2: aliases, after every real version is known, so rule 5 can see
    # versions declared later in the array than the alias referencing them.
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


def iter_namespace_files(registry_root: Path):
    """Yield namespace JSON files, skipping templates and type descriptions."""
    for path in sorted(registry_root.rglob("*.json")):
        if path.name.startswith("_"):
            continue
        if path.parent == registry_root:
            continue  # registry/<type>.json is a type description
        yield path


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument(
        "--registry-root",
        default="registry",
        help="Path to the SecID registry/ directory (default: ./registry)",
    )
    args = parser.parse_args()

    root = Path(args.registry_root)
    if not root.is_dir():
        print(f"ERROR: registry root not found: {root}", file=sys.stderr)
        return 2

    checked = 0
    sources = 0
    failures: list[str] = []
    for path in iter_namespace_files(root):
        try:
            doc = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            failures.append(f"{path}: invalid JSON: {exc}")
            continue
        if not isinstance(doc, dict):
            continue
        checked += 1
        for label, versions in collect_sources(doc):
            sources += 1
            for err in check_source_versions(versions, label):
                failures.append(f"{path}: {err}")

    print(f"Checked {checked} namespace files, {sources} sources declaring versions_available.")
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

- [ ] **Step 4: Run the tests to verify they pass**

Run: `python3 scripts/test_validate_version_aliases.py`
Expected: PASS — 12 lines of `ok  test_...`

Also run under pytest if available: `python3 -m pytest scripts/test_validate_version_aliases.py -q`
Expected: 12 passed.

- [ ] **Step 5: Run the validator against the live registry**

Run: `python3 scripts/validate-version-aliases.py`
Expected: `Checked 2130 namespace files, 380 sources declaring versions_available.` then `All version/alias entries valid.` (375 populated + 5 null.)

**If this reports violations, stop and report them.** They are pre-existing data defects, not caused by this change. Do not loosen the checks to make them pass — triage them as findings and decide per case.

- [ ] **Step 6: Commit**

```bash
git add scripts/validate-version-aliases.py scripts/test_validate_version_aliases.py
git commit -m "Add version/alias validator with offline tests

Enforces the alias rules JSON Schema cannot reach: versions_available
lives inside match_nodes[].data, which is additionalProperties:true.

The load-bearing check is rule 5 — an alias label may never equal a real
version string in the same source. CSA's CCM 4.0 is a genuine release
superseded by 4.0.13, so aliasing 4.0 -> 4.0.13 would silently repoint it."
```

---

### Task 3: Wire the validator into CI

**Files:**
- Modify: `.github/workflows/validate-registry.yml` (both `paths:` blocks, and the job steps)

**Interfaces:**
- Consumes: `scripts/validate-version-aliases.py`, `scripts/test_validate_version_aliases.py` from Task 2
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Add the script to both `paths:` filters**

`validate-registry.yml` has two `paths:` blocks (one under `push`, one under `pull_request`). Add these two lines to **both**, alongside the existing `scripts/validate-*.py` entries:

```yaml
      - "scripts/validate-version-aliases.py"
      - "scripts/test_validate_version_aliases.py"
```

- [ ] **Step 2: Add the validation steps**

After the existing `Validate type-list consistency with SecID-Service` step, add:

```yaml
      - name: Validate version aliases
        run: python3 scripts/validate-version-aliases.py
      - name: Unit-test the version-alias gate
        run: python3 scripts/test_validate_version_aliases.py
```

The unit-test step matters because the live registry is expected to be clean, so `validate-version-aliases.py` alone never exercises a rejection path. Without the unit tests, a regression that made the gate accept everything would pass CI silently.

- [ ] **Step 3: Verify the workflow file parses**

Run:
```bash
python3 -c "
import json,sys
try:
    import yaml
except ImportError:
    print('SKIP: pyyaml not installed; check indentation by eye'); sys.exit(0)
d = yaml.safe_load(open('.github/workflows/validate-registry.yml'))
steps = [s.get('name') for s in d['jobs']['validate']['steps']]
print('steps:', steps)
assert 'Validate version aliases' in steps
assert 'Unit-test the version-alias gate' in steps
print('OK')
"
```
Expected: both step names present, `OK`.

- [ ] **Step 4: Commit**

```bash
git add .github/workflows/validate-registry.yml
git commit -m "Run version-alias validation and its unit tests in CI

The unit-test step is not redundant: a clean registry never exercises the
gate's rejection paths, so a regression that made it accept everything
would otherwise pass CI silently."
```

---

### Task 4: AICM and AI-CAIQ registry data

The substantive data fix. Adds 1.1.0, corrects the phantom `1.0`, and applies D10 — `version_required: true` with `unversioned_behavior: "all_with_guidance"`, so an unversioned control query stops silently answering with one version.

**Files:**
- Modify: `registry/control/org/cloudsecurityalliance.json` — the `(?i)^aicm$` node's `data` (currently lines 96-147) and the `(?i)^aicm-caiq$` node's `data` (currently lines 234-299)

**Interfaces:**
- Consumes: `check_source_versions` enforcement from Task 2
- Produces: registry data consumed by Plan 2's SecID-Service tests

- [ ] **Step 1: Write the assertion test first**

Create `scripts/test_csa_version_data.py`:

```python
#!/usr/bin/env python3
"""Assert the CSA control registry records AICM/AI-CAIQ/CCM versions correctly.

These are data assertions, not logic tests. They exist because the AICM
version record was wrong in a way no structural validator could catch: it
listed a version (1.0) that was never released, while omitting the two that
were (1.0.3, 1.1.0).

Run: python3 scripts/test_csa_version_data.py   (also discoverable by pytest)
"""

import json
from pathlib import Path

CSA = Path(__file__).resolve().parent.parent / "registry/control/org/cloudsecurityalliance.json"
DOC = json.loads(CSA.read_text(encoding="utf-8"))


def source(name: str) -> dict:
    for node in DOC["match_nodes"]:
        if node["patterns"][0].replace("(?i)", "").strip("^$") == name:
            return node["data"]
    raise AssertionError(f"source {name!r} not found")


def versions(name: str) -> dict[str, dict]:
    return {v["version"]: v for v in source(name)["versions_available"]}


def alias_labels(name: str, version: str) -> set[str]:
    entry = versions(name)[version]
    return {a["label"] for a in entry.get("aliases", [])}


def test_aicm_has_1_1_0_as_current():
    v = versions("aicm")
    assert "1.1.0" in v, sorted(v)
    assert v["1.1.0"]["status"] == "current"
    assert v["1.1.0"]["release_date"] == "2026-06-22"


def test_aicm_1_1_aliases_1_1_0():
    assert alias_labels("aicm", "1.1.0") == {"1.1", "v1.1"}


def test_aicm_has_no_phantom_1_0():
    # 1.0 was never released; the lineage is 0.0.2 -> 1.0.3 -> 1.1.0.
    assert "1.0" not in versions("aicm")
    assert "1.0" not in versions("aicm-caiq")


def test_aicm_1_0_3_superseded_with_date():
    v = versions("aicm")["1.0.3"]
    assert v["status"] == "superseded"
    assert v["release_date"] == "2025-11-10"


def test_aicm_requires_a_version():
    d = source("aicm")
    assert d["version_required"] is True
    assert d["unversioned_behavior"] == "all_with_guidance"


def test_aicm_disambiguation_states_the_renumbering():
    text = source("aicm")["version_disambiguation"]
    assert "54" in text, "the renumbering count must be 54, per the generated crosswalk"
    assert "55" not in text, "55 is the stale prose figure; use 54"
    assert "LOG-15" in text
    assert "string match" in text


def test_aicaiq_versions():
    v = versions("aicm-caiq")
    assert v["1.1.0"]["status"] == "current"
    assert "1.0.2" in v
    assert alias_labels("aicm-caiq", "1.1.0") == {"1.1", "v1.1"}


def test_aicaiq_requires_a_version():
    d = source("aicm-caiq")
    assert d["version_required"] is True
    assert d["unversioned_behavior"] == "all_with_guidance"


if __name__ == "__main__":
    fns = [v for k, v in sorted(globals().items()) if k.startswith("test_") and callable(v)]
    for fn in fns:
        fn()
        print(f"  ok  {fn.__name__}")
```

- [ ] **Step 2: Run it to verify it fails**

Run: `python3 scripts/test_csa_version_data.py`
Expected: FAIL on `test_aicm_has_1_1_0_as_current` — `AssertionError: ['1.0.3']`

- [ ] **Step 3: Replace the AICM node's version fields**

In `registry/control/org/cloudsecurityalliance.json`, in the `(?i)^aicm$` node's `data`, replace the existing `version_required`, `unversioned_behavior`, and `versions_available` fields with:

```json
        "version_required": true,
        "unversioned_behavior": "all_with_guidance",
        "version_disambiguation": "AICM control IDs are NOT stable across releases. Between 1.0.3 and 1.1.0, CSA renumbered controls in place: 54 of the 242 control IDs present in both releases designate a DIFFERENT control. LOG-15 was Output Monitoring in 1.0.3 and is Input Monitoring in 1.1.0; IAM-12 was Safeguard Logs Integrity and is Unique Identities; TVM-12 was Threat Analysis and Modelling and is Vulnerability Management Metrics. Only one ID (IAM-19) disappeared outright, so comparing ID sets between releases does NOT detect this. Always cite AICM controls with an explicit version. Never migrate a reference between versions by string match — CSA publishes no crosswalk, so the mapping has to be reconstructed by comparing specification text between the two releases.",
        "versions_available": [
          {
            "version": "1.1.0",
            "release_date": "2026-06-22",
            "status": "current",
            "note": "247 controls across 18 domains. Control IDs renumbered in place from 1.0.3 — see version_disambiguation. NIST AI 600-1:2024 mappings were withdrawn in this release; BSI AI C4, EU AI Act, and ISO/IEC 42001:2023 remain.",
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
            "release_date": "2025-11-10",
            "status": "superseded",
            "note": "243 controls. The last release carrying NIST AI 600-1:2024 mappings, so it remains the only source for those. Its control IDs are not interchangeable with 1.1.0."
          },
          {
            "version": "0.0.2",
            "release_date": null,
            "status": "draft",
            "note": "Early pre-release working draft."
          }
        ],
```

- [ ] **Step 4: Replace the AI-CAIQ node's version fields**

In the `(?i)^aicm-caiq$` node's `data`, replace `version_required`, `unversioned_behavior`, and `versions_available` with:

```json
        "version_required": true,
        "unversioned_behavior": "all_with_guidance",
        "version_disambiguation": "AI-CAIQ question IDs are derived from AICM control IDs (XXX-NN.M), so they inherit AICM's renumbering. Between 1.0.2 and 1.1.0 the underlying control IDs moved and the question IDs moved with them — LOG-15.1 in 1.0.2 and LOG-15.1 in 1.1.0 are questions about different controls. Always cite AI-CAIQ questions with an explicit version, and never migrate references by string match — the mapping has to be derived from the underlying AICM control changes, since CSA publishes no crosswalk for either artifact.",
        "versions_available": [
          {
            "version": "1.1.0",
            "release_date": "2026-06-22",
            "status": "current",
            "note": "320 questions. Ships in the AICM v1.1 bundle as a standalone workbook. Pairs with AICM 1.1.0.",
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
            "note": "Paired with AICM 1.0.3."
          }
        ],
```

- [ ] **Step 5: Run all three checks**

Run:
```bash
python3 -c "import json; json.load(open('registry/control/org/cloudsecurityalliance.json')); print('valid JSON')"
python3 scripts/test_csa_version_data.py
python3 scripts/validate-version-aliases.py
python3 scripts/validate-registry-schema.py
```
Expected: `valid JSON`; the 8 AICM/AI-CAIQ assertions pass (`test_aicaiq_*` and `test_aicm_*`); alias validation clean; schema validation clean.

- [ ] **Step 6: Commit**

```bash
git add registry/control/org/cloudsecurityalliance.json scripts/test_csa_version_data.py
git commit -m "Correct AICM and AI-CAIQ version records; require explicit versions

AICM listed 1.0, which was never released, and omitted both releases that
were (1.0.3, 1.1.0). Adds 1.1.0 as current with 1.1/v1.1 aliases, dates
1.0.3, and adds the 0.0.2 draft.

Sets version_required: true and unversioned_behavior: all_with_guidance
because 54 of the 242 control IDs shared between 1.0.3 and 1.1.0 designate
a different control. An unversioned control query previously returned one
version silently, so the same query gave different answers over time."
```

---

### Task 5: CCM registry data

A different defect from AICM's: SecID lists `4.0`, a real release with no published extraction, and omits `4.0.13`, which has one. Also records the `4.1.0` variant label.

**Files:**
- Modify: `registry/control/org/cloudsecurityalliance.json` — the `(?i)^ccm$` node's `data.versions_available` (currently starting line 39)
- Modify: `scripts/test_csa_version_data.py` (add CCM assertions)

**Interfaces:**
- Consumes: `source()`, `versions()`, `alias_labels()` helpers from Task 4's test module
- Produces: nothing consumed by later tasks

- [ ] **Step 1: Add the failing CCM assertions**

Append to `scripts/test_csa_version_data.py`, before the `if __name__` block:

```python
def test_ccm_has_4_0_13():
    assert "4.0.13" in versions("ccm"), sorted(versions("ccm"))


def test_ccm_4_1_0_is_an_alias_of_4_1():
    # Opposite direction from AICM: here the 2-part form is canonical.
    assert "4.1.0" in alias_labels("ccm", "4.1")


def test_ccm_4_0_is_a_real_version_not_an_alias():
    # 4.0.13 supersedes "CCM 4.0 through 4.0.12", so 4.0 is a distinct
    # release. Aliasing it to 4.0.13 would silently repoint a real version.
    v = versions("ccm")
    assert "4.0" in v
    for entry in v.values():
        for alias in entry.get("aliases", []):
            assert alias["label"] != "4.0", "4.0 must never be an alias"
```

- [ ] **Step 2: Run to verify failure**

Run: `python3 scripts/test_csa_version_data.py`
Expected: FAIL on `test_ccm_has_4_0_13`.

- [ ] **Step 3: Update the CCM `versions_available`**

Replace the `(?i)^ccm$` node's `data.versions_available` with:

```json
        "versions_available": [
          {
            "version": "4.1",
            "release_date": "2024-01-01",
            "status": "current",
            "note": "207 controls, 283 CAIQ questions. Incremental update from 4.0.x.",
            "aliases": [
              {
                "label": "4.1.0",
                "on_match": "resolve",
                "note": "Three-part form of the same release. Note this is the opposite direction from AICM, where the three-part 1.1.0 is canonical and 1.1 is the alias — the canonicalization direction is per-source and is never derived."
              },
              {
                "label": "v4.1",
                "on_match": "resolve"
              }
            ]
          },
          {
            "version": "4.0.13",
            "release_date": null,
            "status": "superseded",
            "note": "Supersedes CCM 4.0 through 4.0.12. Distinct from 4.0 — not an alias of it."
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

**Deliberately not added:** an alias mapping `3` or `v3` to `3.0.1`. The v3 line is closed, so a track alias would collapse to a fixed one — but `3.0` was itself a real release that `3.0.1` supersedes, so which string may safely alias `3.0.1` needs a judgment call rather than a guess. Recorded as a follow-up in Task 8.

- [ ] **Step 4: Run all checks**

Run:
```bash
python3 -c "import json; json.load(open('registry/control/org/cloudsecurityalliance.json')); print('valid JSON')"
python3 scripts/test_csa_version_data.py
python3 scripts/validate-version-aliases.py
python3 scripts/validate-registry-schema.py
```
Expected: all pass, 11 `ok` lines from the data test.

- [ ] **Step 5: Commit**

```bash
git add registry/control/org/cloudsecurityalliance.json scripts/test_csa_version_data.py
git commit -m "Add CCM 4.0.13 and record the 4.1.0 variant label

CCM listed 4.0, a real release with no published extraction, and omitted
4.0.13, which has one. Adds 4.0.13 as a distinct superseded release.

Records 4.1.0 as an alias of 4.1 — the opposite direction from AICM,
where 1.1.0 is canonical. Two frameworks from one publisher canonicalize
oppositely, which is why aliases are curated rather than derived."
```

---

### Task 6: Replace the 19 phantom `@1.0` references

`aicm@1.0` and `aicm-caiq@1.0` name a release that never existed, and they appear in `README.md` and `SPEC.md` — so the wrong version is currently SecID's most visible AICM example.

**Files:**
- Modify: `README.md:171,270`
- Modify: `SPEC.md:115,376,483,693,972`
- Modify: `docs/explanation/RATIONALE.md:216`
- Modify: `registry/regulation.md:120`
- Modify: `registry/control.md:28,115,124`
- Modify: `registry/control/org/cloudsecurityalliance.md:36,37,38,65,66,151,233`

**Interfaces:**
- Consumes: nothing
- Produces: nothing

- [ ] **Step 1: Record the starting count**

Run:
```bash
grep -rEc "aicm(-caiq)?@1\.0([^.0-9]|$)" --include="*.md" --include="*.json" . \
  | grep -v docs/superpowers | grep -v ':0$'
```
Expected: 6 files listed, 19 matches total (16 `aicm@1.0`, 3 `aicm-caiq@1.0`).

- [ ] **Step 2: Rewrite them all to `@1.1.0`**

Run:
```bash
grep -rEl "aicm(-caiq)?@1\.0([^.0-9]|$)" --include="*.md" --include="*.json" . \
  | grep -v docs/superpowers \
  | xargs sed -i '' -E 's/(aicm(-caiq)?)@1\.0([^.0-9]|$)/\1@1.1.0\3/g'
```

Note: `sed -i ''` is the BSD/macOS form. On Linux use `sed -i` with no argument.

- [ ] **Step 3: Verify none remain and the replacements are well-formed**

Run:
```bash
echo "--- remaining phantoms (want none) ---"
grep -rEn "aicm(-caiq)?@1\.0([^.0-9]|$)" --include="*.md" --include="*.json" . \
  | grep -v docs/superpowers || echo "  none"
echo "--- new references (want 19) ---"
grep -rEc "aicm(-caiq)?@1\.1\.0" --include="*.md" --include="*.json" . \
  | grep -v docs/superpowers | grep -v ':0$'
echo "--- no double-substitution artifacts ---"
grep -rn "1\.1\.0\.0\|@1\.1\.0\.0" --include="*.md" --include="*.json" . || echo "  none"
```
Expected: no phantoms remain; 19 new references across the same 6 files; no `1.1.0.0` artifacts.

- [ ] **Step 4: Verify the touched registry `.md`/`.json` files are still well-formed**

Run:
```bash
python3 -c "
import json, glob
for f in glob.glob('registry/**/*.json', recursive=True):
    json.load(open(f))
print('all registry JSON still parses')
"
python3 scripts/validate-registry-schema.py
```
Expected: both pass.

- [ ] **Step 5: Commit**

```bash
git add -u
git commit -m "Replace 19 phantom aicm@1.0 references with @1.1.0

AICM 1.0 was never released — the lineage is 0.0.2, 1.0.3, 1.1.0. These
19 references (16 aicm, 3 aicm-caiq) spanned README.md, SPEC.md,
RATIONALE.md and three registry files, so the most visible AICM example
in the project cited a nonexistent version."
```

---

### Task 7: ADR-009 and the specification updates

Records the decision and removes the documented behavior this design supersedes.

**Files:**
- Modify: `DECISIONS.md` (append ADR-009 after ADR-008; correct ADR-006's drift-check claim)
- Modify: `docs/reference/VERSIONING.md:138-146` (remove the "Nearest:" substitution)
- Modify: `SPEC.md` §5.1 "Versionless References" (add the alias subsection)
- Modify: `docs/reference/API-RESPONSE-FORMAT.md:384` (the feedback-channel reversal)

**Interfaces:**
- Consumes: all prior tasks (the ADR describes what they implemented)
- Produces: nothing

- [ ] **Step 1: Correct ADR-006's false claim**

In `DECISIONS.md`, in ADR-006's **Decision** paragraph, replace `CI verifies they don't drift.` with:

```markdown
(Correction, 2026-07-31: this originally claimed "CI verifies they don't drift." No such check exists — all three workflows trigger only on `registry/**/*.json` and nothing watches `.md`. The AICM entry proved it: `.md` read `versions: ["1.0"]` while `.json` read `1.0.3`, unflagged. Treat `.md` as legacy; JSON is the format that ships.)
```

- [ ] **Step 2: Append ADR-009**

Add to the end of `DECISIONS.md`:

```markdown
---

## ADR-009: Version aliases in registry data; the version qualifier is load-bearing

**Date:** 2026-07-31
**Status:** Accepted
**Decision method:** Design session, recorded in [`docs/superpowers/specs/2026-07-31-version-aliases-design.md`](docs/superpowers/specs/2026-07-31-version-aliases-design.md)

**Goal:** Let one release carry more than one official label, and make `@version` mean something.

**Context:** Publishers label releases inconsistently. CSA stamps the AICM workbook `1.1.0` while branding the same release "v1.1" on its download page; for CCM it does the reverse, with `4.1` canonical and `4.1.0` the variant. SecID had no way to express this — the schema's only alias field, `alias_of`, is namespace-level and unused in all 2,130 files.

Worse, the resolver did not validate `@version` at all. `aicm@1.1#LOG-15`, `aicm@1.0.3#LOG-15`, and `aicm@9.9#LOG-15` all returned `found` at weight 100 with identical payloads, so pinning a version bought nothing.

This mattered because AICM 1.1.0 renumbered controls in place: 54 of the 242 control IDs present in both 1.0.3 and 1.1.0 designate a different control, while only one ID disappeared — so an ID set-difference reports six changed rows and misses all 54. CSA published no crosswalk, and the mapping had to be reconstructed from specification-text similarity with 9 rows still unresolved. Once a renumbering ships unmapped, it is not fully recoverable.

**Decision:**

1. **The registry layer owns label aliases.** One authority labelling one artifact two ways is disambiguation. Cross-release *control* mapping is equivalence and succession, and belongs to the Relationship layer. MITRE ATT&CK draws the same line (`revoked-by` is a relationship, the ID stays resolvable), as does library authority control (MARC `4XX` variant labels versus `5XX` related entities).
2. **Aliases nest inside `versions_available[]` entries**, so nesting encodes the target and cannot drift from it.
3. **Each alias carries a required `on_match`:** `"resolve"` returns data inline with status `found`; `"redirect"` returns empty results with status `corrected` and the canonical SecID in the message.
4. **Aliases are curated, never derived.** No prefix matching, no `v`-stripping. AICM and CCM canonicalize in opposite directions, so no rule derives both.
5. **An alias may never shadow a real version.** CCM `4.0` is a genuine release superseded by `4.0.13`, so `4.0` must not alias `4.0.13`. Enforced by `scripts/validate-version-aliases.py`.
6. **The resolver never returns item data from a version the caller did not ask for.** Unknown version plus a subpath is `not_found` with guidance; unknown version without a subpath is `related` with the version list.
7. **Where item IDs are unstable across releases, omitting the version returns all of them** (`version_required: true`, `unversioned_behavior: "all_with_guidance"`). Applied to AICM and AI-CAIQ.

**Rationale:** Prior art converges on one rule — if the loose form should never be used again, redirect; if it is legitimately reachable, serve the data and declare the canonical form. That is HTTP's `301` versus `rel="canonical"` distinction, and it generalizes across npm dist-tags, Go module queries, Docker tags, and Debian codenames. CSA's "v1.1" is on CSA's own download page, so it is legitimately reachable — hence `resolve` as the normal case.

Loud failure on unknown versions is chosen over a plausible-looking answer because a wrong version is a wrong control. A failure gets reported and fixed; a wrong control gets cited.

**Rejected alternatives:**
- **A fifth response status (`alias`)** — breaks PRINCIPLES #4's four outcomes and forces a coordinated release across four repos.
- **Silent transparent resolution with no signal** — makes alias resolution invisible, so callers keep storing the loose form.
- **Pure redirect with no data for all aliases** — doubles round trips in SecID's primary (MCP) channel, where each one costs an inference step, and empirically fails to change client behavior: HTTP redirects are auto-followed and the web never updated its links.
- **Deriving aliases by prefix or `v`-stripping** — unsound on SecID's own data, and would have aliased CCM `4.0` to `4.0.13`, silently repointing a real release.
- **Returning the nearest version's item data** (the behavior previously documented in `docs/reference/VERSIONING.md`) — its own example used `IAM-12`, one of the 54 renumbered AICM IDs.
- **`unversioned_behavior: "all_with_guidance"` everywhere** — most sources have stable IDs across versions and do not need it.

**Deferred:** alias chains; one label on multiple versions; tracking aliases (`v1` → latest `1.y.z`) as a source-level `version_tracks` field; an explicit `@*` version wildcard; a `missing-version` feedback category.
```

- [ ] **Step 3: Remove the "Nearest:" substitution from VERSIONING.md**

In `docs/reference/VERSIONING.md`, replace the "Version miss" example block (currently lines 138-146) with:

```markdown
Version miss (requested version doesn't exist):
```
Query:    secid:control/cloudsecurityalliance.org/aicm@9.9#LOG-15
Response: Version "9.9" is not a known version of aicm.
          Known versions: 1.1.0 (current, 2026-06-22; aliases 1.1, v1.1),
                          1.0.3 (superseded, 2025-11-10), 0.0.2 (draft).
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

Without a subpath the same query is merely a discovery question, so
`secid:control/cloudsecurityalliance.org/aicm@9.9` returns `related` with the
version list rather than `not_found`.
```

- [ ] **Step 4: Add the alias subsection to SPEC.md §5.1**

In `SPEC.md`, immediately after the "Versionless References" subsection (which ends with the `unversioned_behavior` sentence around line 849), add:

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

An alias resolves to full data in one request; the response carries the
canonical form in the result's `secid` and the matched label in
`version_matched_alias`, so nothing is silently normalized. An alias whose
`on_match` is `"redirect"` instead returns no results and the canonical SecID,
requiring a second request — reserved for labels that should be retired.

Because the direction of canonicalization is inconsistent even within one
publisher, aliases are curated registry data. They are never derived by prefix
matching or `v`-stripping, and an alias may never shadow a real version:
CCM `4.0` is a genuine release superseded by `4.0.13`, not a short form of it.

**Unknown versions fail rather than guess.** A version that is not a known
version or alias returns `not_found` when a subpath is present. The resolver
never substitutes item data from a version the caller did not name — for
sources like AICM, where 54 control IDs changed meaning between releases, a
substitute answer would be confidently wrong. See
[DECISIONS.md ADR-009](DECISIONS.md).
```

- [ ] **Step 5: Update the feedback-channel statement**

In `docs/reference/API-RESPONSE-FORMAT.md`, in the paragraph at line 384, replace the sentence `There is no web-form submission link in the response.` with:

```markdown
As of ADR-009, `not_found` responses also carry https://github.com/CloudSecurityAlliance/SecID/issues, because raw API and bulk-data consumers include humans who otherwise had no channel at all. MCP clients should still prefer the `submit_feedback` tool, which records the miss server-side for backlog aggregation; a GitHub issue does not.
```

- [ ] **Step 6: Verify nothing broke and cross-references resolve**

Run:
```bash
python3 scripts/validate-registry-schema.py
python3 scripts/validate-version-aliases.py
python3 scripts/test_csa_version_data.py
grep -c "ADR-009" DECISIONS.md SPEC.md docs/reference/VERSIONING.md
grep -n "Nearest:" docs/reference/VERSIONING.md || echo "  'Nearest:' removed as intended"
```
Expected: validators pass; ADR-009 referenced in all three files; no `Nearest:` remains.

- [ ] **Step 7: Commit**

```bash
git add DECISIONS.md SPEC.md docs/reference/VERSIONING.md docs/reference/API-RESPONSE-FORMAT.md
git commit -m "Add ADR-009 for version aliases; drop nearest-version substitution

Records the alias design and the rule that makes it worth having: the
resolver never returns item data from a version the caller did not ask
for. VERSIONING.md previously specified returning the nearest version's
control with a soft warning, and its own example used IAM-12 — one of the
54 AICM IDs that designate a different control across releases.

Also corrects ADR-006's claim that CI verifies .md/.json drift. It does
not; no workflow watches .md."
```

---

### Task 8: Record deferred items and open the PR

**Files:**
- Modify: `docs/project/TODO.md`

**Interfaces:**
- Consumes: all prior tasks
- Produces: nothing

- [ ] **Step 1: Append the deferred items**

Add to `docs/project/TODO.md`:

```markdown
## Version aliases (from ADR-009, 2026-07-31)

Deferred deliberately — none has a current requirement. See
[the design spec](../superpowers/specs/2026-07-31-version-aliases-design.md).

- [ ] **Alias chains.** One hop only today; a resolver never follows an alias to another alias. Revisit only on a concrete need.
- [ ] **One label on multiple versions.** Currently a hard validation error. If a need appears, the natural shape is resolving to all matching versions with disambiguation — which `unversioned_behavior: "all_with_guidance"` already does.
- [ ] **Tracking aliases** (`v1` → latest `1.y.z`). Would be a source-level `version_tracks` field, *not* an `aliases[]` entry — nesting fixes the target, so a moving pointer cannot live there. Note that a track collapses into a fixed alias once its major line closes. Deliberately unbuilt: moving pointers are the hazard ADR-009 exists to address; Maven removed `LATEST` and Debian warns against `stable` for the same reason.
- [ ] **Decide the CCM v3 alias.** The v3 line is closed, so `3` or `v3` could safely alias `3.0.1` — but `3.0` was itself a real release that `3.0.1` supersedes, so which string may alias needs a judgment call, not a guess.
- [ ] **Crosswalk and changelog as citable `reference` entries.** The design calls for giving the AICM 1.0.3→1.1.0 crosswalk and `aicm-1.1.0-changelog.json` SecID identities so `version_disambiguation` can cite them. **Blocked:** these currently exist only as local files in the DataSets working tree, which is not a git repository, and the only distribution path named in its README is an `s3://` URI. A `reference` entry needs a resolvable URL, so this needs the artifacts published (or an agreed canonical location) first. Until then the registry text states that no crosswalk is published, which is accurate rather than pointing at something unreachable.
- [ ] **`@*` version wildcard.** Unnecessary for now: omitting the version returns all versions, and `describe` returns the version list. Extending frozen grammar needs its own ADR.
- [ ] **`missing-version` feedback category** in SecID-Service's `submit_feedback` (its enum is `missing-namespace | correction | suggestion`; a missing version is none of those).
- [ ] **A human feedback channel** distinct from URLs embedded in machine responses.
- [ ] **Stale-format doc cleanup** (separate PR): `docs/reference/REGISTRY-FORMAT.md` still says "Current Format: YAML + Markdown", "will migrate to JSON", and "Seven pilot `.json` files already exist"; `REGISTRY-JSON-FORMAT.md` calls JSON the "target" format; `CLAUDE.md` calls `.md` authoritative. Reality: 2,130 JSON files at 100% coverage, deployed to KV.
- [ ] **Status vocabulary drift** (separate PR): `PRINCIPLES.md` and `docs/reference/VERSIONING.md` use `exact_match`/`corrected_match`/`no_match_but_related`; `API-RESPONSE-FORMAT.md` and the live API use `found`/`corrected`/`related`/`not_found`.
```

- [ ] **Step 2: Full validation sweep**

Run:
```bash
python3 scripts/validate-registry-schema.py
python3 scripts/validate-urls.py
python3 scripts/validate-type-list.py
python3 scripts/validate-subtypes.py
python3 scripts/validate-version-aliases.py
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
gh pr create --title "Version aliases: schema, validation, and AICM/AI-CAIQ/CCM version fixes" --body "$(cat <<'EOF'
Implements Plan 1 of the ADR-009 design. Registry side only — **the live
resolver's behavior does not change until the SecID-Service PR lands**,
because nothing gates on `versions_available` today.

## What this does

- Adds `$defs/VersionEntry` and `$defs/VersionAlias` to the registry schema
- Adds `scripts/validate-version-aliases.py` plus offline unit tests, wired into CI
- Corrects AICM: adds 1.1.0 (current, 2026-06-22, 247 controls) with `1.1`/`v1.1`
  aliases, dates 1.0.3, adds the 0.0.2 draft, removes the phantom 1.0
- Same for AI-CAIQ: adds 1.1.0 and 1.0.2
- Sets `version_required: true` + `unversioned_behavior: all_with_guidance` on both,
  because 54 of the 242 control IDs shared between AICM 1.0.3 and 1.1.0 designate a
  different control
- Adds CCM 4.0.13 and records `4.1.0` as an alias of `4.1`
- Replaces 19 phantom `@1.0` references across README, SPEC, RATIONALE and 3 registry files
- Adds ADR-009; removes the nearest-version substitution from VERSIONING.md

## Regex safety

No regex patterns were added or modified. The `on_match` check is an exact
membership test against a two-element tuple, not a pattern match.

## Why aliases are curated rather than derived

CSA canonicalizes in opposite directions across its two flagship frameworks —
AICM's canonical is the 3-part `1.1.0` with `1.1` as the alias; CCM's is the
2-part `4.1` with `4.1.0` as the alias. No rule derives both. And CCM `4.0` is a
genuine release that `4.0.13` supersedes, so prefix-matching would have silently
repointed a real version. The validator rejects any alias that shadows a real
version.
EOF
)"
```

- [ ] **Step 5: Verify CI passes**

Run: `gh pr checks --watch`
Expected: `Validate registry`, `Validate subtypes` both pass.

---

## Follow-on plans

This plan is deliberately scoped to the SecID repo. Two further plans are needed, and each should be written separately because each produces working, testable software on its own:

**Plan 2 — SecID-Service resolver** (`CloudSecurityAlliance/SecID-Service`, TypeScript/Cloudflare Worker). Implements alias matching, `on_match` dispatch, unknown-version `not_found`/`related`, `version_matched_alias`, and `did_you_mean`. **This is the plan that actually fixes the three broken queries** — Plan 1 changes data only. Depends on Plan 1's data shape being merged. Test cases are enumerated in the spec's Testing section.

**Plan 3 — The version-data sweep.** The large data effort: 375 source nodes have populated `versions_available`, of which **347 list exactly one version**. Where that single entry means "current release only, history not enumerated" rather than "this is the only release", version enforcement converts working historical queries into `not_found`. This plan audits those 347, populates real version histories, and only then is enforcement safe to enable broadly. Independent of Plans 1 and 2 and can run in parallel; it does not gate the mechanism, only its blast radius.

**Suggested order:** Plan 1 → Plan 2 (with enforcement initially limited to AICM/AI-CAIQ) → Plan 3 → widen enforcement.
