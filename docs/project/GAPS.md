# Documentation Gap Analysis

This document tracks gaps identified in SecID project documentation and their resolution status.

---

## Status Summary

### Resolved

| Gap | Resolution | Where Documented |
|-----|------------|------------------|
| Undefined BDFL | Kurt Seifried named as BDFL | `STRATEGY.md` |
| PURL governance constraint | Documented as intentional constraint that inherits PURL decisions | `STRATEGY.md` |
| Deprecation/archival process | Case-by-case approach; old identifiers forever; retired standards are enrichment data | `DESIGN-DECISIONS.md` |
| Data validation strategy | AI-assisted validation workflow | `ROADMAP.md` |
| API/distribution model | REST API + libraries in priority order; self-hostable design | `ROADMAP.md` |

### Intentionally Deferred

| Gap | Rationale | Trigger to Address |
|-----|-----------|-------------------|
| Working group charter | Premature governance complexity kills projects | When community interest warrants formal input |
| Formal dispute resolution | BDFL decides for now | When disputes actually arise that need process |
| SLOs for PR review | Early stage, small team | When contributor volume requires predictability |
| Path to community curation | Need core team experience first | When registry is stable and patterns are clear |
| Future layers design (relationships, overlays) | Intentionally deferred to learn from usage | When v1.0 has real adoption and concrete use cases |

### Re-scoped (Addressed or In Progress)

| Gap | Status | Resolution |
|-----|--------|------------|
| Compliance test suite | Re-scoped | Built incrementally during SecID-Service API development; doubles as conformance spec for third-party implementations. No longer a standalone pre-v1.0 blocker. See [skills/compliance-testing/](../../skills/compliance-testing/). |
| Task-focused contributor guides | Partially addressed | Four stub guides created: [ADD-NAMESPACE.md](../guides/ADD-NAMESPACE.md), [UPDATE-NAMESPACE.md](../guides/UPDATE-NAMESPACE.md), [YAML-TO-JSON.md](../guides/YAML-TO-JSON.md), [REGEX-WORKFLOW.md](../guides/REGEX-WORKFLOW.md). Stubs need fleshing out during registry buildout. |
| Regex authoring workflow | Partially addressed | [REGEX-WORKFLOW.md](../guides/REGEX-WORKFLOW.md) stub exists. Needs detailed procedures and cross-runtime compatibility testing. Will be fleshed out during API development. |
| Markdown⇄JSON lifecycle | Addressed | [YAML-TO-JSON.md](../guides/YAML-TO-JSON.md) stub documents the conversion workflow. Dual format is intentional: .md for exploratory authoring, .json for production. See [skills/registry-formalization/](../../skills/registry-formalization/). |

### Still Open

| Gap | Priority | What's Needed |
|-----|----------|---------------|
| Registry file validation requirement | Medium | SPEC.md or CONTRIBUTING.md should require `match_nodes` in all registry files |
| Central discovery hub | Low | "awesome-secid" list or similar for community tools |
| URL rot mitigation details | Low | Content caching strategy (addressed conceptually by v1.x raw content phase) |

---

## Detailed Analysis

### 1. Governance

#### Current State
- **BDFL**: Kurt Seifried (documented in `STRATEGY.md`)
- **Stewardship**: Cloud Security Alliance
- **Philosophy**: "Guidelines, not rules" for agility
- **PURL Constraint**: We inherit PURL's decisions on identifier syntax, focusing governance energy on security-specific questions

#### Resolved
- [x]BDFL named explicitly
- [x]PURL compatibility framed as governance mechanism

#### Deferred (Acceptable)
- [ ]Working group charter - establish when needed
- [ ]Formal dispute resolution - BDFL decides for now
- [ ]Change control process for SPEC.md - BDFL approves, formal RFC when community grows

---

### 2. Registry Maintenance

#### Current State
- Contribution via GitHub PRs (`CONTRIBUTING.md`)
- Seeding strategy documented (`ROADMAP.md`)
- AI-assisted validation workflow defined

#### Resolved
- [x]Deprecation/archival: "Namespace Transitions: Case by Case" in `DESIGN-DECISIONS.md`
  - Old identifiers are forever
  - Retired standards = enrichment data, not namespace changes
  - Handle transitions when they happen with real information
- [x]Validation strategy: AI-assisted workflow in `ROADMAP.md`

#### Deferred (Acceptable)
- [ ]Path to community curation - define when community grows
- [ ]SLOs for PR review - best-effort at early stage

---

### 3. Tooling Ecosystem

#### Current State
- Library roadmap defined: Python → npm → REST API → Go → Rust → Java → C#/.NET
- PURL library adaptation possible (lowers barrier)

#### Re-scoped
- [~]**Compliance test suite** (re-scoped from HIGH to INCREMENTAL)
  - Built incrementally during SecID-Service API development
  - Test cases accumulate as edge cases are discovered during implementation
  - Doubles as conformance specification for third-party resolver implementations
  - See [skills/compliance-testing/](../../skills/compliance-testing/) for full scope

#### Still Open
- [ ]**Central discovery hub** (LOW PRIORITY)
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
- [ ]Entire relationship layer design
- [ ]Entire overlay layer design
- [ ]Trigger criteria for starting design

This is the correct approach. Designing these layers before v1.0 adoption would be guessing.

---

### 5. Technical Gaps

#### Resolved
- [x]**Data validation**: AI-assisted workflow documented
- [x]**API distribution**: REST API + self-hostable in roadmap

#### Still Open
- [ ]**Registry file validation requirement** (MEDIUM PRIORITY)
  - Registry files should be required to include `match_nodes` for subpath validation
  - Should be added to SPEC.md or CONTRIBUTING.md

- [ ]**URL rot mitigation** (LOW PRIORITY)
  - Conceptually addressed by v1.x raw content caching
  - Detailed strategy not yet documented
  - Will become clearer as content ingestion begins

#### Accepted Trade-offs
- Percent-encoding complexity (necessary evil)
- Filesystem path length limits (future database solves)
- Database indexing (not a concern at current scale)

---

### 6. Documentation & Workflow Gaps

#### Markdown⇄JSON Lifecycle (ADDRESSED)
- **Status:** In progress.Addressed by [docs/guides/YAML-TO-JSON.md](../guides/YAML-TO-JSON.md) and [skills/registry-formalization/](../../skills/registry-formalization/).
- **Resolution:** Dual format is intentional — .md is the authoring/exploratory format, .json is the production format consumed by the API. The YAML-TO-JSON.md guide documents the conversion workflow. The registry-formalization skill (stub) will provide judgment and automation for keeping formats in sync.
- **Remaining work:** YAML-TO-JSON.md stub needs fleshing out with detailed procedures during API development.

#### Regex Authoring Workflow & Compatibility Testing (PARTIALLY ADDRESSED)
- **Status:** In progress.Partially addressed by [docs/guides/REGEX-WORKFLOW.md](../guides/REGEX-WORKFLOW.md).
- **Resolution:** REGEX-WORKFLOW.md stub exists as a task-oriented guide placeholder. The [registry-research skill](../../skills/registry-research/) will wrap this workflow.
- **Remaining work:** Flesh out the guide with concrete procedures, cross-runtime testing steps, and ReDoS prevention guidance. Will happen during API development as patterns are tested against real runtimes.

#### Task-Focused Contributor Guides (PARTIALLY ADDRESSED)
- **Status:** In progress.Partially addressed by four stub guides in `docs/guides/`.
- **Resolution:** Created [ADD-NAMESPACE.md](../guides/ADD-NAMESPACE.md), [UPDATE-NAMESPACE.md](../guides/UPDATE-NAMESPACE.md), [YAML-TO-JSON.md](../guides/YAML-TO-JSON.md), [REGEX-WORKFLOW.md](../guides/REGEX-WORKFLOW.md). These will be wrapped by the three skills ([registry-research](../../skills/registry-research/), [registry-formalization](../../skills/registry-formalization/), [compliance-testing](../../skills/compliance-testing/)).
- **Remaining work:** All four guides are stubs that need fleshing out. This happens incrementally during registry buildout and API development.

---

## Next Actions

1. **During API development**: Compliance test suite accumulates incrementally (see [skills/compliance-testing/](../../skills/compliance-testing/))
2. **During registry buildout**: Ensure all registry files include `match_nodes`; flesh out stub guides in docs/guides/
3. **When community grows**: Establish working group, formalize processes
4. **When v1.0 has adoption**: Begin relationship/overlay layer design with real use cases
