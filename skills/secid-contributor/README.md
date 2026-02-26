# secid-contributor

**Status: Stub — not yet built.** Core documentation exists across multiple files but needs consolidation into an operational playbook before packaging as a skill.

## Purpose

Single skill for anyone who wants to **work on the SecID project** — creating registry entries, updating existing ones, validating data, contributing to the spec, or helping with project infrastructure. If you're making SecID better, this is your skill.

## Audience

- AI agents creating or updating registry files (the primary near-term use case)
- Human contributors adding namespaces or sources
- Reviewers validating registry entries
- Anyone proposing spec changes, documentation improvements, or tooling

## What This Skill Will Cover

### Registry Creation (highest priority)

End-to-end workflow for creating a new registry entry:

1. **Research a source** — Where to look, how to find official URLs, ID formats, versioning, API endpoints. How to validate that URLs resolve. How to test pattern nodes against real identifiers.
2. **Determine type and namespace** — Decision criteria for the 7 types. Compute filesystem path using reverse-DNS algorithm. Check if namespace already exists (add source vs. create new file).
3. **Create the entry** — Both .md (current format) and .json (target format). Fill in all fields with correct semantics (description vs. notes, null vs. absent, known_values vs. lookup_table).
4. **Handle versioning** — When to set version_required, unversioned_behavior, version_disambiguation, versions_available. The three resolution behaviors and when each applies.
5. **Record provenance** — How to document where data came from, when it was verified, what method was used. Essential for lookup_tables with non-computable URLs.
6. **Validate** — Check patterns match examples, URLs are well-formed, .md and .json are consistent, required fields present for declared status, no layer violations.
7. **Decide readiness** — draft vs. _deferred. When you have enough info vs. when to park it.

### Registry Update

- Adding a new source to an existing namespace
- Updating URLs that have changed
- Adding versioning fields when a new edition of a source releases
- Promoting status (proposed → draft → pending → published)
- Handling deprecation, acquisition, domain changes

### Registry Validation

- Schema validation for both YAML frontmatter and JSON
- Pattern testing (do match_nodes patterns match the declared examples?)
- URL validation (well-formed, resolvable)
- Cross-format consistency (.md ↔ .json)
- Status-appropriate field completeness
- Layer violation detection (relationship/enrichment data in registry)

### Bulk Seeding

- Creating many entries from a CSV or list of sources
- Triage workflow: sufficient info → draft, insufficient → _deferred
- Prioritization guidance (core security infrastructure first per ROADMAP.md)

### Contribution Process

- PR conventions and review criteria
- What reviewers look for (from CONTRIBUTING.md + docs/guides/REGISTRY-GUIDE.md quality standards)
- How to propose spec changes vs. registry additions
- Documentation standards

## Current State of Knowledge

The information needed for this skill **exists but is scattered** across multiple documents:

| Knowledge Area | Current Location(s) | Status |
|---------------|---------------------|--------|
| Decision tree (type, namespace) | docs/guides/REGISTRY-GUIDE.md | Good but could use worked examples |
| Filesystem path algorithm | SPEC.md, CLAUDE.md, docs/guides/REGISTRY-GUIDE.md | Duplicated 3x, SPEC.md is canonical |
| JSON schema / field reference | docs/reference/REGISTRY-JSON-FORMAT.md | Comprehensive |
| YAML format (current) | docs/reference/REGISTRY-FORMAT.md | Adequate |
| Source identifier preservation | SPEC.md, docs/guides/REGISTRY-GUIDE.md, CLAUDE.md | Duplicated, REGISTRY-GUIDE.md is most practical |
| Version resolution behavior | docs/reference/REGISTRY-JSON-FORMAT.md, docs/guides/REGISTRY-GUIDE.md, docs/explanation/DESIGN-DECISIONS.md | Good coverage after recent additions |
| Quality standards | docs/guides/REGISTRY-GUIDE.md | Good (null vs absent, id_pattern anchoring, etc.) |
| Provenance workflow | docs/reference/REGISTRY-JSON-FORMAT.md (field def only) | Gap — field exists but "how to do it" isn't documented |
| Research workflow | Nowhere | Major gap — no guidance on how to research a new source |
| Validation workflow | CLAUDE.md (grep commands only) | Major gap — manual grep, no systematic validation |
| Edge cases | docs/reference/EDGE-CASES.md | Good for domains/internationalization |
| Real examples | registry/weakness/org/owasp.json | Excellent complex example |
| Template | registry/advisory/_template.md | Too minimal for complex cases |

### Key Gaps to Fill Before Building

1. **Research workflow** — Step-by-step guide for investigating a new source: where to look for official documentation, how to discover ID formats, how to find URL patterns, when to use lookup_table vs. url template
2. **Provenance workflow** — How to record provenance while researching, not after the fact
3. **Worked examples** — At least 3: a simple source (single id_pattern, predictable URLs), a complex source (multiple sources, lookup_table, versioning), and a deferred source (insufficient info)
4. **Validation checklist** — Systematic, not just grep commands
5. **Template expansion** — The current _template.md is too bare; need a richer template or multiple templates for common patterns

## Dependencies Before Building

- [ ] Consolidate scattered documentation into a single operational reference (or at minimum, clear "read this section of that file" pointers)
- [ ] Write the research workflow guide
- [ ] Write the provenance workflow guide
- [ ] Create worked examples (simple, complex, deferred)
- [ ] Build or document a validation checklist
- [ ] Decide: does this skill work against the repo directly (files), or through an API?

## Resources This Skill Will Bundle

- Complete field reference (consolidated from docs/reference/REGISTRY-JSON-FORMAT.md)
- Decision tree for type selection
- Filesystem path algorithm
- Research workflow guide (to be written)
- Provenance recording guide (to be written)
- Validation checklist (to be written)
- Quality standards reference
- Worked examples (to be created)
- Template files for common patterns
- The three version resolution behaviors and when to use each

## Open Questions

- Should the skill include tooling (scripts for validation, URL checking) or just knowledge?
- How to handle the YAML → JSON format transition? Create both formats? Only JSON?
- Should the skill have access to the full registry for deduplication checks?
- How to handle sources that require authentication or are behind paywalls?
- Should the skill be able to directly create PRs, or just produce files?
