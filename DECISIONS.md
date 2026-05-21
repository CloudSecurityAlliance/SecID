# Architecture Decision Records

Sequential log of architecture decisions for the SecID specification and registry.

This file complements [docs/proposals/](docs/proposals/) (per-proposal rationale, often with extensive analysis) and [docs/explanation/DESIGN-DECISIONS.md](docs/explanation/DESIGN-DECISIONS.md) (broader explanatory content): proposals capture *why a specific question got answered the way it did*; this file captures *the architectural choices that shape SecID*, in chronological order, with rejected alternatives. The format mirrors [SecID-Service's DECISIONS.md](https://github.com/CloudSecurityAlliance/SecID-Service/blob/main/DECISIONS.md).

New ADRs are appended (never renumbered). When a decision is reversed, add a new ADR superseding the old one rather than editing the old entry.

---

## ADR-001: PURL grammar with `secid:` scheme

**Date:** 2025-08 (approximate, from SPEC.md v0.1)
**Status:** Accepted
**Decision method:** Founder choice

**Goal:** Establish an identifier grammar for security knowledge that's machine-parseable, human-legible, and familiar to developers.

**Context:** Security knowledge lives in dozens of databases (CVE, CWE, ATT&CK, NIST, ISO, etc.), each with its own identifier format. A unified grammar makes citation and resolution tractable. The need was for grammar that supports type + namespace + name + version + qualifier semantics.

**Decision:** Adopt Package URL (PURL) grammar with `secid:` as the scheme. The full form is `secid:type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]`.

**Rationale:** PURL is already battle-tested in software supply chain tooling (SPDX, CycloneDX, OSV) and has solved the same shape of problem. Developers already know PURL. The grammar fits all 10 SecID types we currently use, and the percent-encoding rules transfer directly. The subpath addition (after `#`) is an extension PURL doesn't define but doesn't conflict with — it lets us address sub-items within a database (e.g., a specific CVE within the CVE source).

**Rejected alternatives:**
- **Ad-hoc grammar designed for security** — More effort, less interoperability, no library ecosystem
- **URI fragments only (`https://...#CVE-2021-44228`)** — Forces an HTTP context; doesn't compose for cross-source citations
- **Opaque tokens** — Defeats the human-legibility goal

See [docs/explanation/RATIONALE.md](docs/explanation/RATIONALE.md) for the longer-form treatment.

---

## ADR-002: Domain-name namespaces

**Date:** 2025-08 (approximate)
**Status:** Accepted
**Decision method:** Founder choice

**Goal:** Make namespace registration globally unique without inventing a naming authority.

**Context:** SecID needs to identify which organization publishes each set of identifiers (`mitre.org/cve`, `nist.gov/csf`, etc.). A central registrar would be a single point of failure and political bottleneck.

**Decision:** Namespaces are DNS domain names (with optional `/`-separated sub-namespace path segments for platform sub-spaces like `github.com/advisories`). DNS already provides globally unique names with an established ownership-proof story.

**Rationale:** Domain ownership can be verified independently (DNS TXT records, ACME challenges) when self-registration ships. No central authority needs to bless namespaces; the existing DNS system does that work. Filesystem-safe by construction (with reverse-DNS layout — see ADR-003). Unicode-friendly for internationalization.

**Rejected alternatives:**
- **Numeric IDs assigned by a registrar** — Single point of failure; political bottleneck for adding sources
- **Opaque slugs with collision detection** — No proof-of-ownership story
- **Vendor-prefixed schemes (`secid:mitre:cve:...`)** — Less consistent than DNS, no global uniqueness mechanism

---

## ADR-003: Reverse-DNS filesystem layout for registry entries

**Date:** 2025-08 (approximate)
**Status:** Accepted
**Decision method:** Founder choice

**Goal:** Organize registry files on disk so collisions are impossible and lookups are predictable.

**Context:** With ~1,150 namespaces today (and more anticipated), a flat directory is unwieldy. A hash-prefixed layout would defeat human readability. A naive `<domain>.md` layout has collisions across types (mitre.org appears as advisory, weakness, ttp, and entity).

**Decision:** Registry files live at `registry/<type>/<tld>/<domain>.json` (and `.md`), where the domain is reversed component-by-component. So `cve.org` becomes `registry/<type>/org/cve.json`. Sub-namespace paths append after the reversed domain: `github.com/advisories` becomes `registry/<type>/com/github/advisories.json`.

**Rationale:** Reverse-DNS layout groups files by TLD (alphabetical browsing works), allows a domain to appear under multiple types without collision, and matches conventions familiar from Java package naming. The algorithm is described in CLAUDE.md "Namespace-to-Filesystem Algorithm" and validated by CI to catch path-mismatches against SPEC §4.0.

**Rejected alternatives:**
- **Flat `<domain>-<type>.json`** — Harder to browse, fewer affordances for tab-completion
- **Hash-prefixed sharding (`registry/ab/cdef.../...`)** — Defeats human readability
- **Type-only nesting (no reverse DNS)** — Collisions when domains repeat (which they do constantly)

---

## ADR-004: Three-layer model — Registry / Relationship / Data

**Date:** 2026-01 (approximate, formalized when explanation docs were written)
**Status:** Accepted
**Decision method:** Project-shaping principle

**Goal:** Keep the SecID spec focused on identifier resolution without scope-creep into enrichment, relationships, or general security knowledge representation.

**Context:** SecID could grow indefinitely. "Identify the CVE" tempts adding "and link to the CWEs it maps to" then "and the controls that prevent it" then "and the AI risk it represents." Each addition makes the spec heavier, harder to implement, and harder to reason about.

**Decision:** Adopt a three-layer model with strict separation:
- **Registry layer** (this repo) — identity, resolution, disambiguation
- **Relationship layer** (future) — equivalence, succession, cross-type mappings
- **Data layer** (future, partially via V2 dataset repos) — enrichment, full content, metadata

Each layer can be implemented and version independently. The registry layer is the only one frozen at v1.0.

**Rationale:** Clear boundaries make the spec implementable in a weekend. The relationship layer is the right place for "CVE → CWE → ATT&CK" mappings — those are observations *about* identities, not identities themselves. The data layer is the right place for "full CWE definition text" — that's bulk content, not identity. Co-mingling them would make every implementation carry the weight of all three.

See [CLAUDE.md "Three Layers"](CLAUDE.md) and [docs/explanation/RATIONALE.md](docs/explanation/RATIONALE.md).

**Rejected alternatives:**
- **Monolithic spec (everything together)** — Implementation burden; spec churn affects all consumers
- **Two-layer (registry + data, no relationship layer)** — Forces all cross-type observations into registry data, polluting identity records
- **Four-layer (split data into static + dynamic)** — Premature; one data layer with sub-conventions is sufficient

---

## ADR-005: Types are intentionally overloaded; split via four-criteria gate

**Date:** 2026-04 (formalized in DESIGN-DECISIONS.md after `disclosure` split)
**Status:** Accepted (reconfirmed 2026-05-17 via GLOSSARY + ENTITY-REGULATION-CONTROL-SPLIT proposals)
**Decision method:** Project-shaping principle, validated by three proposals

**Goal:** Decide when a registry concept gets a new top-level SecID type vs. a tag/subtype within an existing type.

**Context:** Adding a new type is expensive — coordinated changes across SecID, SecID-Service, SecID-Server-API, and SecID-Client-SDK (the type list is hardcoded in each). Splitting too eagerly creates churn; splitting too late creates muddled types.

**Decision:** The default is to put related concepts into the closest existing type, with a `subtype:` tag (see ADR-009) for differentiation. Promote to a new type only when all four criteria are met:

1. **Resolution patterns diverge** — different URL structures, different APIs, different metadata
2. **Consumers diverge** — different tools need to filter them separately
3. **Semantics drift** — the "question answered" becomes meaningfully different
4. **Volume justifies it** — enough examples exist to define clear boundaries

**Rationale:** Validated by lived experience. `disclosure` passed all four (split from `entity` in 2026); so did `capability` and `methodology`. Recent decisions to *not* split — glossary (→ `reference + subtype`), regulation/control split (declined), assertion/content (revision toward `control` + `reference`) — each failed at least one criterion. The four-criteria gate is doing real work in design discussions.

**Rejected alternatives:**
- **Never overload (always split)** — Multi-repo cost would compound; spec evolution slows to a crawl
- **Always overload (never split)** — Already-split types like `disclosure` were correctly split; consumer experience would degrade
- **Discretionary case-by-case** — Easy to abuse in either direction; explicit gate keeps the bar high

See [docs/explanation/DESIGN-DECISIONS.md "When to Split"](docs/explanation/DESIGN-DECISIONS.md).

---

## ADR-006: YAML+Markdown contributions, JSON authoritative

**Date:** 2026-03 (approximate, from format-transition history)
**Status:** Accepted
**Decision method:** Pragmatic dual-format choice

**Goal:** Reconcile two competing needs: human contributors want a forgiving editable format; resolvers and tools want a strict machine-parseable format.

**Context:** Early registry was YAML frontmatter + Markdown body (Obsidian-friendly, easy to edit by hand). Resolvers, validators, and the live service need JSON for strict schema validation and fast parsing. Maintaining both by hand is error-prone.

**Decision:** JSON is the authoritative format for v1.0+. YAML+Markdown contributions remain accepted (and the templates and human docs still use that format), but the JSON file is what the resolver reads, what the JSON Schema validates, and what gets uploaded to KV. The two formats coexist on disk; CI verifies they don't drift.

**Rationale:** Letting contributors author in YAML lowers the barrier to participation. Letting the resolver consume JSON lets us use JSON Schema (Draft 2020-12) for validation and standard JSON tooling everywhere. Conversion is mechanical (see [`docs/guides/YAML-TO-JSON.md`](docs/guides/YAML-TO-JSON.md)).

**Rejected alternatives:**
- **JSON only, no YAML** — Higher barrier for casual contributors; loses Obsidian compatibility
- **YAML only** — JSON Schema ecosystem is richer; resolver performance would suffer; the type ecosystem (jq, JSON Path, openapi-validators) is JSON-native
- **TOML or Cue** — Niche; loses the existing YAML→JSON tooling

---

## ADR-007: GLOSSARY two-phase rollout (tag-now, copy-into-registry later)

**Date:** 2026-05-20
**Status:** Accepted
**Decision method:** Proposal acceptance via [docs/proposals/GLOSSARY-DEFINITION-COMPARISON.md](docs/proposals/GLOSSARY-DEFINITION-COMPARISON.md)

**Goal:** Make glossary documents (NIST CSRC, CSA, AWS, OWASP) resolvable at the term level via SecID without committing to V2 dataset infrastructure that doesn't exist yet.

**Context:** A glossary has thousands of term-level definitions. Embedding everything in a registry file scales badly (NIST alone is 3-5 MB). A pure relationship-layer approach (registry returns identity only; consumer fetches definitions elsewhere) leaves users with a bare identity, not a useful lookup.

**Decision:** Two-phase rollout:
- **Phase 1 (now):** Tag glossary `reference` entries with `subtype: ["glossary"]`. Term content lives in a separate glossary dataset repository. The registry entry carries a `data_repo:` SecID pointer.
- **Phase 2 (future):** Copy term-level data into the SecID registry alongside identity data, so the resolver API serves definitions directly via `GET /api/v1/resolve`.

**Rationale:** Phase 1 lands operational value immediately (discoverability via the subtype tag, term-level identity via subpaths) with zero infrastructure dependency. Phase 2 is a developer-experience upgrade gated on V2 dataset pattern maturity. This sequencing addresses the "hybrid has no operational landing if V2 slips" risk the proposal originally flagged.

**Rejected alternatives:**
- **Pure relationship-layer** (original proposal) — Bare identity isn't a useful lookup
- **Embed everything in the registry file** — NIST CSRC alone would be 100× the size of typical registry files; deploy chain becomes the wrong tool for weekly content updates
- **One-phase rollout** — Phase 2 depends on V2 infra that's not built; blocking on it would defer all glossary value indefinitely

---

## ADR-008: Subtypes as code-bundled constant in SecID-Service, not as freely-addable registry data

**Date:** 2026-05-21
**Status:** Accepted
**Decision method:** Project-shaping principle, codified after the subtype framework shipped

**Goal:** Treat subtype additions as a deliberate design choice (like adding a new type), not as a casual registry-data edit.

**Context:** Subtypes (`subtype: ["glossary"]`, `subtype: ["scoring"]`, etc.) were introduced as a registry-data convention. The first instinct was to make adding a new subtype as easy as adding the value to a JSON file. But unconstrained subtype additions would dilute the vocabulary, fragment consumer filtering, and undermine the "try a subtype first" gate from ADR-005.

**Decision:** The authoritative list of subtypes lives in SecID-Service's `src/type-registry.ts` as a TypeScript constant. Adding or removing a subtype requires a code edit + PR review in that repo. SecID's CI ([`scripts/validate-subtypes.py`](scripts/validate-subtypes.py)) gates registry-data PRs by fetching the SecID-Service type-registry and validating that every `subtype:` value used in registry data is declared there. The Worker serves the type list from the in-memory constant for zero-latency reads; KV holds a synchronized mirror for non-code consumers.

**Rationale:** Forcing the change through SecID-Service code review puts a meaningful gate in place. The constant is also the single source of truth that the API endpoint, MCP describe tool, homepage, and Resolver component all import from — eliminating drift between four places that previously hardcoded type/subtype info. Performance benefit is a bonus (no KV hit for the most-common query).

**Rejected alternatives:**
- **Compute from registry data at deploy time** — Trivially easy to add a new subtype; defeats the discipline goal
- **JSON file in SecID repo, uploaded to KV** — Drifts unless CI compares to actual usage; same effective bar as TypeScript constant but with worse tooling
- **MCP-only, no REST endpoint** — Skips the website's own consumption; homepage would still need to hardcode

See [SecID-Service ADR-equivalent in their type-registry.ts header comment](https://github.com/CloudSecurityAlliance/SecID-Service/blob/main/src/type-registry.ts) for the SecID-Service-side framing, and [docs/reference/TYPES-AND-SUBTYPES.md](docs/reference/TYPES-AND-SUBTYPES.md) for the conceptual model.

---
