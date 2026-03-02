# registry-research

**Status: Stub — not yet built.** Core documentation exists across multiple files. This skill will be built incrementally alongside SecID-Service (the API).

## Purpose

Skill for **researching security knowledge sources and creating registry entries**. This covers the full lifecycle from discovering a source through producing a validated .md registry file. Formalization to JSON and compliance testing are handled by separate skills.

## Audience

- AI agents creating or updating registry files (the primary near-term use case)
- Human contributors adding namespaces or sources
- Anyone researching a new security knowledge source for inclusion

## What This Skill Covers

### Research a Source

How to investigate a new security knowledge source end-to-end:

1. **Discover official resources** — Find the authoritative website, documentation, API endpoints, data downloads. Determine the organization behind it.
2. **Identify ID formats** — What identifiers does the source use? What's the pattern? Are there prefixes, version numbers, hierarchy levels?
3. **Find URL patterns** — Can individual items be linked directly? Is there a URL template, or do you need a lookup table? Test with real identifiers.
4. **Determine versioning** — Does the source have versions? Is version required to disambiguate? What happens when version is omitted?
5. **Record provenance** — Document where data came from, when it was verified, what method was used.

### Determine Type and Namespace

- Decision criteria for the 7 SecID types (advisory, weakness, ttp, control, regulation, entity, reference)
- Compute filesystem path using the reverse-DNS algorithm
- Check if namespace already exists (add source vs. create new file)
- Handle cross-type documentation (same source in multiple types)

### Create the Registry Entry (.md)

- Use `registry/<type>/_template.md` as starting point
- Fill in YAML frontmatter: namespace, type, status, urls, sources
- Write pattern nodes (match_nodes) with descriptions at each hierarchy level
- Include examples with real identifiers
- Handle versioning fields: `version_required`, `unversioned_behavior`, `version_disambiguation`
- Apply null vs. absent convention correctly

### Update Existing Entries

- Adding a new source to an existing namespace
- Updating URLs that have changed
- Adding versioning fields when a new edition releases
- Handling deprecation, acquisition, domain changes

### Decide Readiness

- When to use `draft` status vs. parking in `registry/_deferred/`
- Minimum viable entry: at least one working URL resolution path
- What "published" means (reviewed, not necessarily complete)

## Wraps These Guides

This skill consolidates and operationalizes the workflows documented in:

- [docs/guides/ADD-NAMESPACE.md](../../docs/guides/ADD-NAMESPACE.md) — Step-by-step walkthrough for new namespaces
- [docs/guides/UPDATE-NAMESPACE.md](../../docs/guides/UPDATE-NAMESPACE.md) — How to update existing entries
- [docs/guides/REGEX-WORKFLOW.md](../../docs/guides/REGEX-WORKFLOW.md) — How to write and test regex patterns for match_nodes

The guides provide the reference steps; this skill provides the judgment and workflow knowledge to execute them well.

## Current State of Knowledge

The information needed for this skill exists but is scattered:

| Knowledge Area | Current Location | Status |
|---------------|------------------|--------|
| Decision tree (type, namespace) | [docs/guides/REGISTRY-GUIDE.md](../../docs/guides/REGISTRY-GUIDE.md) | Good but could use worked examples |
| Filesystem path algorithm | [SPEC.md](../../SPEC.md), [CLAUDE.md](../../CLAUDE.md) | Duplicated, SPEC.md is canonical |
| YAML format (current) | [docs/reference/REGISTRY-FORMAT.md](../../docs/reference/REGISTRY-FORMAT.md) | Adequate |
| Source identifier preservation | [docs/guides/REGISTRY-GUIDE.md](../../docs/guides/REGISTRY-GUIDE.md) | Most practical treatment |
| Version resolution behavior | [docs/reference/REGISTRY-JSON-FORMAT.md](../../docs/reference/REGISTRY-JSON-FORMAT.md), [docs/guides/REGISTRY-GUIDE.md](../../docs/guides/REGISTRY-GUIDE.md) | Good coverage |
| Quality standards | [docs/guides/REGISTRY-GUIDE.md](../../docs/guides/REGISTRY-GUIDE.md) | Good (null vs absent, pattern anchoring, etc.) |
| Edge cases | [docs/reference/EDGE-CASES.md](../../docs/reference/EDGE-CASES.md) | Good for domains/internationalization |
| Real examples | `registry/weakness/org/owasp.json` | Excellent complex example |
| Template | `registry/advisory/_template.md` | Too minimal for complex cases |
| Research workflow | [docs/guides/ADD-NAMESPACE.md](../../docs/guides/ADD-NAMESPACE.md) | Stub — needs fleshing out |
| Regex workflow | [docs/guides/REGEX-WORKFLOW.md](../../docs/guides/REGEX-WORKFLOW.md) | Stub — needs fleshing out |

### Key Gaps to Fill

1. **Research workflow** — ADD-NAMESPACE.md stub exists but needs detailed guidance on how to investigate a source: where to look, how to discover ID formats, when to use lookup_table vs. URL template
2. **Provenance workflow** — How to record provenance while researching, not after the fact
3. **Worked examples** — At least 3: simple source (single pattern, predictable URLs), complex source (multiple sources, lookup_table, versioning), deferred source (insufficient info)
4. **Template expansion** — The current `_template.md` is too bare for complex cases; need a richer template or multiple templates for common patterns
5. **Validation checklist** — Systematic pre-submission checks beyond grep commands

## Dependencies

- [ ] Flesh out docs/guides/ADD-NAMESPACE.md with detailed research guidance
- [ ] Flesh out docs/guides/REGEX-WORKFLOW.md with testing procedures
- [ ] Create worked examples (simple, complex, deferred)
- [ ] Build or document a validation checklist

These will be built incrementally alongside SecID-Service development — each new namespace added during API work teaches us what the skill needs to cover.

## What This Skill Does NOT Cover

- **Converting .md to .json** — See [skills/registry-formalization/](../registry-formalization/)
- **JSON Schema validation** — See [skills/registry-formalization/](../registry-formalization/)
- **Testing resolver implementations** — See [skills/compliance-testing/](../compliance-testing/)
- **Consuming/using SecID as an end user** — See [skills/secid-user/](../secid-user/)

## Open Questions

- Should the skill include tooling (scripts for URL checking, pattern testing) or just knowledge?
- How to handle sources that require authentication or are behind paywalls?
- Should the skill be able to directly create PRs, or just produce files?
