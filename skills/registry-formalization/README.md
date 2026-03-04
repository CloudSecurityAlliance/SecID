# registry-formalization

**Status: Stub — not yet built.** Will be built incrementally alongside SecID-Service as the JSON format stabilizes.

## Purpose

Skill for **converting registry .md files to production .json format**, validating against the JSON Schema, and ensuring cross-format consistency. This is the bridge between exploratory research (done in Markdown) and production-ready data (consumed by the API).

## Audience

- AI agents performing YAML-to-JSON conversion
- Contributors promoting registry entries from draft .md to production .json
- Reviewers checking JSON output quality and schema compliance

## What This Skill Covers

### YAML-to-JSON Field Migration

Convert YAML frontmatter fields to their JSON equivalents:

- Map `sources:` entries to JSON `sources` objects with full field definitions
- Translate `urls:` block to `resolution` object with `url_template` and `lookup_table`
- Convert flat `id_pattern` lists to nested `match_nodes` tree structure
- Handle `description`, `notes`, `known_values`, and provenance fields
- Preserve null vs. absent semantics across formats

### match_nodes Tree Construction

Build the nested pattern tree from flat or partially structured patterns:

- Identify hierarchy levels in the source's ID system
- Create parent nodes with children for hierarchical IDs (e.g., RHSA/RHBA/RHEA under errata)
- Write regex patterns that are anchored, PCRE2-safe, and backtracking-resistant
- Add `description` and `url_template` at each node level
- Test patterns against declared examples

### JSON Schema Validation

Validate converted files against the canonical JSON Schema:

- Required fields present for declared `status`
- Field types match schema definitions
- `match_nodes` patterns compile in target runtimes (JS, Python, Go, Rust)
- Version resolution fields internally consistent (`version_required`, `unversioned_behavior`, `version_disambiguation`)
- No layer violations (relationship/enrichment data in registry)

**Note:** The JSON Schema will be built during SecID-Service API development.

### Cross-Format Consistency

Ensure .md and .json files for the same namespace stay in sync:

- All sources in .md are present in .json (and vice versa)
- URL templates match between formats
- Pattern definitions are equivalent
- Examples in .md are valid against .json patterns
- Status values correspond (`active` in YAML ↔ `published` in JSON)

### Re-sync Workflow

When the .md file changes after .json already exists:

- Identify what changed in .md (new source, updated URLs, new patterns)
- Apply changes to .json without losing JSON-only fields
- Re-validate the updated .json
- Document the sync in commit message

## Wraps This Guide

- [docs/guides/YAML-TO-JSON.md](../../docs/guides/YAML-TO-JSON.md) — Step-by-step conversion walkthrough

## Resources

- [docs/reference/REGISTRY-JSON-FORMAT.md](../../docs/reference/REGISTRY-JSON-FORMAT.md) — Target JSON schema specification
- [registry/CONVERSION-REVIEW-PROMPT.md](../../registry/CONVERSION-REVIEW-PROMPT.md) — AI-assisted review prompt for conversions
- 121 existing .json files covering all registry namespaces (see CLAUDE.md "JSON Registry Files" for full list). Key reference files:
  - `registry/advisory/org/mitre.json` — Simple advisory with variable extraction (cvelistV5 bucket)
  - `registry/advisory/com/redhat.json` — Complex nested match_nodes (RHSA/RHBA/RHEA)
  - `registry/advisory/org/debian.json` — Range-table year lookup (DSA/DLA)
  - `registry/control/org/cloudsecurityalliance.json` — Control framework with versioning
  - `registry/weakness/org/owasp.json` — `version_required`, `version_disambiguation`, and structured ExampleObject test fixtures

## Dependencies

- [ ] JSON Schema formalized (built during SecID-Service API development)
- [ ] YAML-TO-JSON.md guide fleshed out with detailed procedures
- [ ] Validation tooling or checklist for schema compliance
- [ ] Status value mapping between YAML and JSON formats finalized

These will be built incrementally alongside SecID-Service — the API needs the JSON format, so the schema and validation emerge naturally during API development.

## What This Skill Does NOT Cover

- **Researching new sources** — See [skills/registry-research/](../registry-research/)
- **Testing resolver implementations** — See [skills/compliance-testing/](../compliance-testing/)
- **Consuming/using SecID as an end user** — See [skills/secid-user/](../secid-user/)

## Design Rationale

**Why separate from research?** Research is exploratory — you're discovering what a source looks like and capturing it in human-readable Markdown. Formalization is mechanical — you're converting known-good data to a machine-readable format. Different skills, different failure modes, different expertise.

**Why keep both .md and .json?** Markdown is the authoring format (human-readable, easy to review, good for exploration). JSON is the production format (machine-parseable, schema-validated, consumed by the API). The .md file remains authoritative for narrative content; the .json file is authoritative for resolution data.

## Open Questions

- Should conversion be fully automated (script) or AI-assisted (skill provides judgment)?
- How to handle fields that exist in JSON but have no Markdown equivalent?
- Should the skill detect when .md and .json are out of sync, or only convert on demand?
