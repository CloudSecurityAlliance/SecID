# Documentation Gap Analysis

This document tracks gaps identified in SecID project documentation and their resolution status.

---

## Status Summary

### Resolved ✅

| Gap | Resolution | Where Documented |
|-----|------------|------------------|
| Undefined BDFL | Kurt Seifried named as BDFL | `STRATEGY.md` |
| PURL governance constraint | Documented as intentional constraint that inherits PURL decisions | `STRATEGY.md` |
| Deprecation/archival process | Case-by-case approach; old identifiers forever; retired standards are enrichment data | `DESIGN-DECISIONS.md` |
| Data validation strategy | AI-assisted validation workflow | `ROADMAP.md` |
| API/distribution model | REST API + libraries in priority order; self-hostable design | `ROADMAP.md` |

### Intentionally Deferred ⏸️

| Gap | Rationale | Trigger to Address |
|-----|-----------|-------------------|
| Working group charter | Premature governance complexity kills projects | When community interest warrants formal input |
| Formal dispute resolution | BDFL decides for now | When disputes actually arise that need process |
| SLOs for PR review | Early stage, small team | When contributor volume requires predictability |
| Path to community curation | Need core team experience first | When registry is stable and patterns are clear |
| Future layers design (relationships, overlays) | Intentionally deferred to learn from usage | When v1.0 has real adoption and concrete use cases |

### Still Open 🔴

| Gap | Priority | What's Needed |
|-----|----------|---------------|
| Compliance test suite | High | Canonical test cases before libraries ship to prevent implementation drift |
| Registry file validation requirement | Medium | SPEC.md or CONTRIBUTING.md should require `id_pattern` in all registry files |
| Central discovery hub | Low | "awesome-secid" list or similar for community tools |
| URL rot mitigation details | Low | Content caching strategy (addressed conceptually by v1.x raw content phase) |
| Markdown⇄JSON lifecycle | Medium | Document when exploratory Markdown entries graduate to JSON mirrors and how to keep them synchronized |
| Regex authoring workflow | Medium | Consolidated how-to plus compatibility checks for building and testing resolver regex trees |
| Task-focused contributor guides | Medium | Step-by-step docs for common tasks (e.g., new registry entry, regex testing) alongside the reference material |

---

## Detailed Analysis

### 1. Governance

#### Current State
- **BDFL**: Kurt Seifried (documented in `STRATEGY.md`)
- **Stewardship**: Cloud Security Alliance
- **Philosophy**: "Guidelines, not rules" for agility
- **PURL Constraint**: We inherit PURL's decisions on identifier syntax, focusing governance energy on security-specific questions

#### Resolved
- ✅ BDFL named explicitly
- ✅ PURL compatibility framed as governance mechanism

#### Deferred (Acceptable)
- ⏸️ Working group charter - establish when needed
- ⏸️ Formal dispute resolution - BDFL decides for now
- ⏸️ Change control process for SPEC.md - BDFL approves, formal RFC when community grows

---

### 2. Registry Maintenance

#### Current State
- Contribution via GitHub PRs (`CONTRIBUTING.md`)
- Seeding strategy documented (`ROADMAP.md`)
- AI-assisted validation workflow defined

#### Resolved
- ✅ Deprecation/archival: "Namespace Transitions: Case by Case" in `DESIGN-DECISIONS.md`
  - Old identifiers are forever
  - Retired standards = enrichment data, not namespace changes
  - Handle transitions when they happen with real information
- ✅ Validation strategy: AI-assisted workflow in `ROADMAP.md`

#### Deferred (Acceptable)
- ⏸️ Path to community curation - define when community grows
- ⏸️ SLOs for PR review - best-effort at early stage

---

### 3. Tooling Ecosystem

#### Current State
- Library roadmap defined: Python → npm → REST API → Go → Rust → Java → C#/.NET
- PURL library adaptation possible (lowers barrier)

#### Still Open
- 🔴 **Compliance test suite** (HIGH PRIORITY)
  - Without canonical test cases, implementations may handle edge cases differently
  - Needed before v1.0 libraries ship
  - Should cover: percent-encoding, subpath parsing, version handling, qualifier parsing

- 🔴 **Central discovery hub** (LOW PRIORITY)
  - No "awesome-secid" list planned
  - Would help adopters find community tools
  - Can add when there are tools to list

---

### 4. Future Layers (Relationships & Overlays)

#### Current State
- Explicitly deferred - documented in `RELATIONSHIPS.md`, `OVERLAYS.md`, `DESIGN-DECISIONS.md`
- Exploratory ideas captured but not committed
- Rationale: avoid premature complexity, let usage inform design

#### Deferred (Intentional)
- ⏸️ Entire relationship layer design
- ⏸️ Entire overlay layer design
- ⏸️ Trigger criteria for starting design

This is the correct approach. Designing these layers before v1.0 adoption would be guessing.

---

### 5. Technical Gaps

#### Resolved
- ✅ **Data validation**: AI-assisted workflow documented
- ✅ **API distribution**: REST API + self-hostable in roadmap

#### Still Open
- 🔴 **Registry file validation requirement** (MEDIUM PRIORITY)
  - Registry files should be required to include `id_pattern` for subpath validation
  - Should be added to SPEC.md or CONTRIBUTING.md

- 🔴 **URL rot mitigation** (LOW PRIORITY)
  - Conceptually addressed by v1.x raw content caching
  - Detailed strategy not yet documented
  - Will become clearer as content ingestion begins

#### Accepted Trade-offs
- Percent-encoding complexity (necessary evil)
- Filesystem path length limits (future database solves)
- Database indexing (not a concern at current scale)

---

### 6. Documentation & Workflow Gaps

#### Markdown⇄JSON Lifecycle (MEDIUM PRIORITY)
- **Where it's mentioned:** `AGENTS.md:3-4` tells contributors that Markdown registry files and JSON mirrors must match, while `REGISTRY-FORMAT.md:5-16` only notes that JSON is a “future direction.” Neither source explains when exploratory Markdown files should remain narrative-only, when to generate JSON mirrors, or how to keep Markdown authoritative once JSON exists.
- **Impact:** Contributors may promote research-stage content into JSON too early (hurting API stability) or forget to sync JSON after Markdown edits (leading to resolver regressions).
- **Needed fix:** Document the lifecycle explicitly: draft in Markdown → validate SecIDs/regexes → mark “ready” → generate JSON mirror → keep Markdown as the narrative/authoritative text and describe how to re-sync JSON when Markdown changes. A short checklist in `REGISTRY-FORMAT.md` (linked from `AGENTS.md`) would prevent ambiguity.

#### Regex Authoring Workflow & Compatibility Testing (MEDIUM PRIORITY)
- **Where info lives now:** `SPEC.md:14-18` and `README.md:153-160` explain that registry patterns drive parsing, `DESIGN-DECISIONS.md:2072-2089` describes the unified pattern tree, and `REGISTRY-JSON-FORMAT.md:456-515` plus `REGISTRY-GUIDE.md:369-375` list schema expectations. There is no single workflow or automated validation.
- **Impact:** Contributors must hop across multiple reference docs and manually trust that their regexes compile everywhere. There is also no lint/test harness to enforce the “PCRE2-safe, no backtracking” constraints, so incompatibilities will only surface at runtime.
- **Needed fix:** Publish a task-oriented guide (e.g., `REGEX-WORKFLOW.md`) walking through deriving patterns, encoding them in Markdown/JSON, validating with `rg`/Python, and testing SecID examples. Pair it with a script/CI job that loads every `patterns[]` entry and compiles it using the target runtimes (JS/Python/Go/Rust) with timeout guards to catch ReDoS-prone expressions.

#### Task-Focused Contributor Guides (MEDIUM PRIORITY)
- **Current state:** `AGENTS.md:21-22` merely suggests keeping the reference docs handy; contributors must infer how to perform common workflows.
- **Impact:** Important tasks—creating a namespace, promoting Markdown to JSON, testing regexes, or validating SecID examples—lack concise procedures, slowing onboarding and creating review churn.
- **Needed fix:** Add short runbooks or checklists (either within `AGENTS.md` or as separate `WORKFLOW` docs) that enumerate steps, commands, and success criteria for frequent tasks. Link each step back to the authoritative reference but provide an ordered, actionable path another AI can execute.

---

## Next Actions

1. **Before v1.0 libraries ship**: Create compliance test suite with canonical test cases
2. **During registry buildout**: Ensure all registry files include `id_pattern`
3. **When community grows**: Establish working group, formalize processes
4. **When v1.0 has adoption**: Begin relationship/overlay layer design with real use cases
