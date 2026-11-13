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

(Correction, 2026-07-31: this originally claimed "CI verifies they don't drift." No such check exists — all three workflows trigger only on `registry/**/*.json` and nothing watches `.md`. The AICM entry proved it: `.md` read `versions: ["1.0"]` while `.json` read `1.0.3`, unflagged (both corrected in the same change that added ADR-009). Treat `.md` as legacy; JSON is the format that ships.)

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

## ADR-010: SecID 2.0 serves content; the registry is unchanged

**Date:** 2026-08-19
**Status:** Accepted
**Decision method:** Collaborative — worked through against measured registry and corpus data

**Goal:** Add the content itself to SecID (v2.0) — and later a local/private deployment story (v3.0) — without disturbing a frozen v1.0 registry format or the three-layer model.

**Context:** v1.0 returns URLs. The next thing consumers want is the content behind them — and CSA already holds most of it, scattered across roughly nineteen one-off dataset repositories, one of which already mirrors SecID's `type/namespace/name/version/` layout and carries license, lifecycle, and extraction-provenance metadata. The question was whether serving content requires the registry to grow: new fields for acquisition constraints, volatility, extractor pointers, cache policy.

**Decision:** It does not. **The registry keeps holding exactly what it holds today** — identity, resolution, disambiguation — and refers out to separate data repositories. All content, and all metadata about acquiring that content, lives on the data side. No new registry fields are introduced for v2.0.

**Rationale:** The registry's job is to answer "should I even try, and where do I look" for every namespace in a single pass, which is why it fits in KV and why unscoped cross-source search is possible at all. Extraction provenance is per-artifact and only matters once you have decided to fetch. Keeping the split on that functional line preserves both properties, and it keeps the v1.0 format frozen as promised. Serving content is still *labeling and finding* under PRINCIPLES.md §1 — what stays out is enrichment and relationships, exactly as before.

**Rejected alternatives:**
- **An `acquisition:` block on registry entries** — Puts access notes, volatility, and extractor pointers where cross-source search would carry their weight on every query; also reopens a frozen format
- **Split on function: cheap/stable facts in the registry, churny provenance with the data** — Defensible, and the split does fall on a real line, but it still means a v2.0 registry schema change and two places to look
- **Content in the registry repo itself** — Would put hundreds of megabytes of extracted text behind every registry clone and every deploy

**Implementation:** Not yet started. Lifecycle and publishing model deliberately left open — see [docs/project/TODO.md](docs/project/TODO.md) and [ROADMAP.md](ROADMAP.md#secid-20-content-and-the-tools-that-produce-it).

---

## ADR-011: Data repositories shard by region, keyed by the authority behind the material

**Date:** 2026-08-19
**Status:** Accepted
**Decision method:** Collaborative — several partition schemes modelled against registry and corpus measurements before choosing

**Goal:** Choose a partition for the data repositories that survives reclassification, supports delegated ownership, and lets consumers sync only what they need.

**Context:** Several schemes were measured. Sharding by publisher domain concentrates badly — one publisher is roughly half the corpus. Sharding by country leaves ~80% of namespaces with no country signal at all, since most sit on `.com` or `.org`. Sharding by type is unstable, because an item's type can be reclassified — is this a control, a disclosure, or both? — and reclassification would move bytes between repositories.

**Decision:** Data shards into region repositories — `International`, `North-America`, `Latin-America`, `Europe`, `Asia`, `Middle-East`, `Africa`, `Oceania` — plus `Staging` for material acquired but not yet classified. Placement follows **the authority behind the instrument**: if a state or sub-state body owns it, it belongs to that state's region regardless of who adopts it; if the body is constituted across states, it is International regardless of where its office is. In practice the region derives from the namespace's country tag where present and from the TLD otherwise. Private counterparts live under `CloudSecurityAlliance-Internal` with identical names, so visibility is an organization property rather than a naming convention.

**Capability data is exempt, and shards by vendor.** The region axis serves *jurisdictional relevance*, which product capabilities lack — AWS S3 encryption is identical everywhere. Sharding them geographically would place AWS, Azure and GCP together in `North-America` (their publishers are US companies), where a projected 10,000–20,000 entries would outweigh every standards body in that repository. They live in `SecID-Data-Vendor` instead, promoting to `SecID-Data-<domain>` at a published, mechanical size threshold. The generalised rule: **data that is not jurisdictional does not shard jurisdictionally.**

**Rationale:** The publishing domain never changes when an item is reclassified, so the shard key is stable by construction. Authority resolves the cases that address and reach get wrong in opposite directions — a Japanese government standard is Asian even when globally adopted; SWIFT is International despite being Belgian. Regions map onto structures that already exist (CSA chapters, national bodies), giving delegated ownership a natural home, and they let a consumer sync one jurisdiction plus the global bodies instead of the world. `Staging` is named for transience deliberately: an entry sitting in a bucket called "Other" is unremarkable, whereas one sitting in "Staging" is visibly overdue.

**Rejected alternatives:**
- **Per-publisher-domain repositories** — Power-law distribution; a handful of whales and hundreds of near-empty repositories
- **Per-country repositories** — 80% of namespaces have no country signal; would produce dozens of shards holding fewer than five entries each
- **Per-type repositories (`SecID-{type}`)** — Reclassification moves bytes, which is the specific failure the shard key must avoid
- **A single repository with CODEOWNERS paths** — Delegates review but cannot delegate read access, and forces every consumer to sync everything
- **An `Other` catch-all** — Would silently accumulate misfiled material; a residual bucket that is allowed to have contents cannot also serve as an alarm
- **Sharding capability data by region alongside everything else** — Correct by the letter of the rule and wrong in effect: it would make `North-America` roughly 90% AWS configuration data
- **A repository per vendor from the start** — Premature; a repo explosion ahead of the evidence. `SecID-Data-Vendor` first, promotion on a threshold
- **An editorial list of which vendors get repositories** — Not vendor-neutral. A mechanical threshold means a vendor earns a repository by arithmetic, and any vendor can earn one

**Implementation:** Not yet started.

---

## ADR-012: Extraction equivalence is tiered; extractions are reproduced or attested

**Date:** 2026-08-19
**Status:** Accepted
**Decision method:** Collaborative — resolved a tension between reproducible builds and AI-assisted extraction

**Goal:** Let CSA accept extracted content from contributors without either trusting them blindly or redoing their work.

**Context:** Contributors will submit extractors alongside extracted data, and CSA needs to confirm the two agree. Byte-identical reproduction is achievable for deterministic pipelines but impossible where an LLM is in the extraction path — and AI extraction is exactly what makes large-scale ingestion affordable. Treating this as binary would either bar AI extraction entirely or reduce every verification claim to "trust us."

**Decision:** Equivalence is **tiered**. Identifiers, hierarchical structure, and normative text must match exactly; formatting, line wrapping, and extraction incidentals need not match at all. Extractions are labelled by grade: **reproduced** where a deterministic pipeline can be re-run and compared, **attested** where AI was in the path and the output is instead checked against invariants and its provenance recorded. Both grades are legitimate and both are stated to consumers.

**Rationale:** The strictness follows what is load-bearing. A dropped article number or mangled control ID is a wrong answer delivered silently, whereas a rewrapped paragraph harms nobody — so binding the check to the semantic layers makes it both meaningful and achievable across tool versions. Grading rather than gating keeps AI extraction available while remaining honest, which is PRINCIPLES.md §5 applied to content. The preferred pattern that falls out is to use AI to *build* a deterministic extractor and then ship the extractor, paying the expensive step once and earning the stronger grade. Reproducibility is also a continuity property: a corpus intended to outlive its authors must be re-derivable by people who were not there.

**Rejected alternatives:**
- **Byte-identical reproduction required** — Bars AI extraction, and fails on ordinary tool-version drift
- **Trust contributor assertions** — No defence against error or malice in an open contribution model
- **Human review only** — Does not scale, and reviewers do not reliably notice a single missing identifier in a long document

**Implementation:** Not yet started. Note that running contributor-supplied extractors is untrusted code execution and will need isolation designed in from the start.

---
## ADR-013: A single-source corpus promotes out of its region repository at a size threshold

**Date:** 2026-09-04
**Status:** Accepted
**Decision method:** Empirical — six quarterly ingests were built and measured before deciding

**Goal:** Keep the region repositories legible when one publisher's corpus is an order of magnitude larger than everything else in its region.

**Context:** ADR-011 shards data by region, keyed by the authority behind the instrument, and exempts capability data because it is not jurisdictional. DISA STIGs fit neither case cleanly. They are unambiguously US instruments, so the letter of ADR-011 places them in `North-America` — but the measured corpus is 174 documents and ~14,150 rules per release, retained across releases. Six quarters produce 511 document-release pairs and 53,674 rule records. That is the same magnitude ADR-011 refused for capability data, where "a projected 10,000-20,000 entries would outweigh every standards body in that repository". Placing STIGs in `North-America` would make it predominantly DISA, drowning NIST, FedRAMP and CISA.

Size alone is not the sharpest argument, because storage is cheap. **Cadence** is. STIGs refresh quarterly as one synchronised batch of ~175 documents; statutes, regulations and agency guidance change irregularly and one item at a time. Mixed in one repository, each damages the other: the quarterly bulk-replace drowns the commit history, and "did a US regulation change this week" becomes unanswerable by inspection.

**Decision:** A single publisher's corpus **promotes out of its region repository** into `SecID-Data-<domain>` when it exceeds a published, mechanical threshold. The repository is named for the authority's DNS domain — `SecID-Data-disa.mil` — matching the identifier used everywhere else in SecID, so promotion requires no naming debate. This is the same promotion mechanism ADR-011 already defines for `SecID-Data-Vendor`, applied in the opposite direction.

Promotion does not change how anything resolves. The registry namespace stays `disa.mil`, the SecID string is unchanged, and the data path is identical to what it would have been inside the region repository (ADR-014). Only the repository boundary moves.

**Rationale:** Measurement settled the storage question that motivated the alternatives. Six quarters of STIG data — 54,185 files, 245 MB checked out — pack to **18 MiB**, because git deduplicates identical rule records across release directories and stores every blob as a delta. Extrapolated at the measured ~2 MiB per quarter, a decade lands near 100 MiB: about 10% of GitHub's soft warning threshold. A single repository is therefore not merely acceptable but comfortable, and the reasons to split are legibility and delegated ownership rather than capacity.

Naming by domain keeps promotion mechanical rather than editorial, which is the property ADR-011 insisted on when it rejected "an editorial list of which vendors get repositories".

**Rejected alternatives:**
- **Leave STIGs in `SecID-Data-North-America`** — Correct by the letter of ADR-011 and wrong in effect, the same way sharding capability data by region was: one publisher would dominate the region
- **A repository per quarterly compilation** (`SecID-Data-disa.mil-2026-07`) — Measured and rejected. Deduplication and delta compression only operate within a single packfile, so six repositories store six copies of every unchanged rule: roughly 150 MiB against 18 MiB, growing by four repositories a year. It also destroys `git diff v2026.04 v2026.07`, the single most useful query over this corpus. Immutability, the property this was reaching for, is delivered by tags and per-quarter Releases at no cost
- **Retain only the current release** — Rejected on evidence. SCAP Compliance Checker ships SCAP content one release behind the manual STIG (RHEL 9 manual V2R9 against SCAP V2R8), so latest-1 is not history, it is what practitioners' scanners are running today
- **A size threshold expressed in bytes** — Storage compresses unpredictably; 245 MB of files became 18 MiB. Record and document counts are the stable signal
- **Exempting STIGs by declaring them "not jurisdictional"** — They plainly are. Stretching ADR-011's existing exemption to cover this would have been motivated reasoning, and would have made the rule mean nothing

**Implementation:** `SecID-Data-disa.mil` created 2026-09-04 with six quarterly ingests tagged `v2025.04` through `v2026.07`.

---

## ADR-014: Every SecID-Data-* repository uses one layout, mirroring the registry

**Date:** 2026-09-04
**Status:** Accepted
**Decision method:** Collaborative — settled while creating the first data repository, before it was published

**Goal:** Let one path-derivation algorithm read every data repository, so a resolver needs no per-source knowledge.

**Context:** The first data repository was built with `stigs/` and `srgs/` at the top level, following the publisher's own vocabulary. Two problems surfaced immediately. It does not generalise — `SecID-Data-Europe` holds nothing called a STIG. And it is wrong by SecID's own model: STIGs and SRGs both resolve as `secid:control/...`, so the split encoded a distinction the identifier does not make.

**Decision:** Every `SecID-Data-*` repository uses:

```
data/         extracted content, addressed by SecID
schemas/      JSON Schema for the record formats
scripts/      acquisition and extraction tooling
indexes/      generated cross-references, never hand-edited
docs/         how it works, source quirks, provenance
```

Content under `data/` is keyed on the **SecID type**, then the publisher domain in **reverse-DNS**, exactly as `registry/<type>/<tld>/<domain>` already does:

```
secid:control/disa.mil/rhel-9@V2R9#V-257505
  -> data/control/mil/disa/rhel-9/V2R9/rules/V-257505.json
```

The domain appears even in a single-domain repository, where it is redundant, so that the derivation is identical in regional repositories that hold many.

**Rationale:** Path derivation from the identifier is what makes a local resolver a filesystem lookup rather than an index scan, which is the 3.0 goal. The moment a layout encodes publisher vocabulary, every consumer needs a per-source lookup table. Keying on type rather than source vocabulary also survives the publisher reorganising: DISA could rename SRGs tomorrow without moving a byte.

Mirroring the registry's existing reverse-DNS convention means contributors moving between repositories already know the furniture, and one documented algorithm covers both.

**Rejected alternatives:**
- **Publisher vocabulary at top level** (`stigs/`, `srgs/`) — Does not generalise, and encodes a distinction the SecID type does not make. `kind` survives as a field
- **Omitting the domain in single-domain repositories** — Shorter, but regional repositories must carry it, producing two path shapes and a rule about which applies where
- **Flat content at the repository root** — No room for tooling, schemas or documentation without colliding with data
- **A top-level `research/`** — Provisional material belongs at `docs/research/`, where it reads as provisional; SecID's own documentation sweep flagged a stray top-level equivalent for archiving

**Implementation:** Applied to `SecID-Data-disa.mil` before publication, so the layout is correct from its first commit.

---

## ADR-015: Version aliases, and making the version qualifier load-bearing

**Date:** 2026-07-31
**Status:** Accepted
**Decision method:** Design session (originally proposed in PR #134 as ADR-009; renumbered because ADR-009 is reserved for the methodology-vs-reference test, #73)

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
6. **An alias may never shadow a real version.** CCM `4.0` is CSA's published label; `4.0.13` is an internal patch stamp with no addressable version of its own.
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
- **Deriving aliases by prefix or `v`-stripping** — unsound on SecID's own data; it would have aliased CCM's published label `4.0` to the internal patch stamp `4.0.13`, inverting the relationship.
- **Pure redirect with no data for all aliases** — doubles round trips in the MCP channel where each costs an inference step, and empirically fails to change client behavior.
- **Returning the nearest version's item data** (previously documented in `docs/reference/VERSIONING.md`) — its own example used `IAM-12`, one of the 54 renumbered AICM IDs.
- **Version tree nodes for CCM** — would make `ccm#IAM-12` demand a version, for a source whose IDs are broadly stable.

**Amendment (2026-09-25): AICM 1.1.1, and `1.1` as a series label.** CSA shipped AICM 1.1.1: the same 247 control IDs, titles, and 18 domains as 1.1.0, adding NIST AI RMF / NIST AI 600-1 and AIUC-1 cross-framework mappings to every control and correcting a handful of guidance texts (per CSA's csa-mcp dataset). The AI-CAIQ stays at 1.1.0; CSA issued no AI-CAIQ 1.1.1. Decision: register 1.1.1 as the current AICM version and point the aliases `1.1` and `v1.1` at it instead of at 1.1.0. 1.1.0 stays addressable as `@1.1.0`. AI-CAIQ's `1.1` / `v1.1` still point at AI-CAIQ 1.1.0.

*Why:* CSA's own tooling defines the label. The csa-mcp server treats `1.1` as a series label that resolves to the newest ingested 1.1.x — `aicm 1.1 → 1.1.1`, `aicm-caiq 1.1 → 1.1.0` — so a SecID `@1.1` pointing at 1.1.0 would name a different release than the publisher's own server does for the same string. PRINCIPLES #6 (follow the source) decides it. The re-point is safe for citations: 1.1.1 did not renumber, so `aicm@1.1#LOG-15` names the same control under either target.

*Acknowledged cost:* this is a two-part alias pointing at a patch release, and it makes `1.1` a moving pointer — the hazard this ADR's rule 5 and the deferred `version_tracks` item warn about, and an exception to "an alias is never re-pointed". It is accepted as a single, manually maintained case; if CSA ships a 1.1.2, the alias moves by hand. A second case should build `version_tracks` rather than repeat the exception.

*Rejected:* keeping `1.1 → 1.1.0` (disagrees with CSA's own server for the same label); making `1.1` a `redirect` (still names the wrong release); declaring `1.1` on both 1.1.0 and 1.1.1 (one label on multiple versions is a validation error, and AICM's `all_with_guidance` already covers the "give me every version" case when the version is omitted).

**Second amendment (2026-10-22): CCM version nodes, and `4.1` as a series label.** CSA shipped CCM 4.1.1 inside its unchanged "v4.1" bundle: the workbook's Change Log dates it 2026-10-01, while the artifact page still reads "Released: 01/27/2026", and the patch level shows only in the workbook filename and its cell A1 stamp. 4.1.1 keeps 4.1.0's 207 control IDs and titles, adds the first CCM v4.1 cross-framework mappings (NIST SP 800-171 rev2, MITRE ATT&CK v17.1) and a DORA reverse mapping, and rewords 101 control specifications and 26 CAIQ questions. Decision (Kurt): register 4.1.1 and 4.1.0 as versions, give CCM version tree nodes, and point `4.1` / `v4.1` at 4.1.1 — repeating the AICM exception above rather than building `version_tracks`. `4.0.13`, the stamp on the workbook CSA serves as v4.0, becomes a fixed alias of `4.0`, so references that cite it now resolve. (Before this amendment, `ccm@4.0.13` and `ccm@v4.1` were `not_found`, as an unlisted version is; `ccm@4.1` resolved.)

*Why:* "4.1" now names two different datasets, and only the version tree can tell them apart. The tree also fixes a resolution bug: CCM's single set of item patterns enumerated 4.0's `IVS`, so `ccm@4.1#I&S-01` never matched — 4.1 renamed IVS to I&S. Each version node now enumerates its own release's domain codes.

*This reverses* the rejected alternative above, "version tree nodes for CCM". SecID-Service resolves version nodes only for `version_required` sources, so CCM now sets `version_required: true` with `all_with_guidance`, and an unversioned `ccm#IAM-12` returns the versions with guidance instead of the current control.

*Acknowledged cost:* a second moving pointer, against the first amendment's "a second case should build `version_tracks`". Unlike AICM, the publisher's own tooling does not yet agree: as of 2026-10-22, CSA's csa-mcp server still labels its 4.1.0 data "4.1", so SecID's `ccm@4.1` and csa-mcp's `ccm 4.1` name different releases until csa-mcp loads 4.1.1. If CSA ships a 4.1.2, the alias moves by hand. Unversioned CCM queries, which previously resolved straight to the current control, now need a version. Bare-ID cross-source search also stops finding CCM: SecID-Service's namespace- and type-scoped search tests only a source's direct children, which for CCM are now version nodes, so `secid:control/cloudsecurityalliance.org/IAM-01` returns `ccm-caiq#IAM-01` but no longer `ccm#IAM-01`, and a version literal such as `.../4.1.1` comes back as a malformed `ccm#4.1.1`. AICM already behaves this way. SecID-Service's test of the unversioned `ccm#A&A-01` case is pinned to `@4.0` (SecID-Service#45), which must merge first or registry deploys fail.

**Third amendment (2026-11-02): Multi-artifact version nodes and immutable `.0` semver aliases on format schemas.**
**Decision method:** AI decision (Gemini), reviewed by Codex ([PR #214](https://github.com/CloudSecurityAlliance/SecID/pull/214), closing [#204](https://github.com/CloudSecurityAlliance/SecID/issues/204)).

*Context:* Format and schema `reference` entries (`cve.org/cve-schema`, `mitre.org/cwe-schema`, `cyclonedx.org/cyclonedx`, `spdx.dev/spdx`, `ossf.github.io/osv-schema`) frequently publish multiple resolution artifacts per version at different weights — for example, a normative XSD or JSON Schema at weight 100 alongside HTML documentation or a GitHub web view at weight 50, or CVE JSON 4.0's three state-specific JSON Schemas (`public`, `reject`, `reserved`) plus its Markdown draft specification. Previously, `scripts/validate-version-aliases.py` required `len(matched) == 1` per version in `versions_available`, rejecting sibling child nodes for the same version.

*Decision:*
1. **Multi-artifact sibling version nodes:** `scripts/validate-version-aliases.py` permits multiple sibling child nodes to match the same version in `versions_available`, provided every sibling node for that version declares the exact same canonical `patterns[0]` literal and the exact same set of alias literals (`patterns[1:]`).
2. **Immutable `.0` semver aliases on format schemas:** On schema `reference` sources where publishers or consumers use two-part (`X.Y`) and three-part (`X.Y.0`) version strings interchangeably (`cve-schema`, `spdx`, `osv-schema`), two-part/three-part aliases always bind to the fixed `.0` release (`5.1 → 5.1.0`, `3.0.0 → 3.0`, `1.9 → 1.9.0`, `1.3 → 1.3.0`) rather than moving to subsequent patch releases (`5.1.1`, `1.9.2`, `1.3.1`). Unlike AICM `1.1` and CCM `4.1` above, format schema `.0` aliases are static semver equivalences and never move when a patch release ships.

*Rejected alternatives:*
- **Collapsing each schema version to a single URL** — loses secondary representations (HTML specification pages alongside XSD/JSON schemas, or CVE 4.0's `reject` and `reserved` schemas) that Issue #204 explicitly requires preserving.
- **Pointing two-part schema aliases (`1.9`, `1.3`) at the latest patch release (`1.9.2`, `1.3.1`)** — creates moving pointers without `version_tracks`, violating rule 5 above and causing "validate against X.Y" to silently change meaning when X.Y.Z ships.

**Deferred:** alias chains; one label on multiple versions; tracking aliases (`v1` → latest `1.y.z`) as a source-level `version_tracks` field (AICM `1.1` and CCM `4.1` are manual stopgaps for exactly this — see the amendments above); an explicit `@*` version wildcard; a `missing-version` feedback category; per-item "this ID changed meaning" metadata, which needs SecID to host AICM content and is gated on CSA legal confirmation ([`DATA-HOSTING-RULES.md`](docs/reference/DATA-HOSTING-RULES.md) line 79) plus a license-matrix row for the CC BY-NC **non-commercial** clause.

---

## ADR-016: Registry conventions for multi-edition national strategies (#215) and proposed/enacted legislation (#208)

**Date:** 2026-11-03
**Status:** Accepted
**Decision method:** AI decision (Gemini), reviewed by Codex (closing [#208](https://github.com/CloudSecurityAlliance/SecID/issues/208) and [#215](https://github.com/CloudSecurityAlliance/SecID/issues/215))

**Goal:** Establish consistent registry patterns for multi-edition national security/cybersecurity strategies, implementation plans, and review documents (`#215`), as well as proposed bills, enacted statutes, and enforceable regulatory industry codes (`#208`).

**Context:**
1. National security and cybersecurity strategies evolve across multiple editions (e.g., Canada's National Cyber Security Strategy 2010/2018/2025, US National Security Strategy 2010/2015/2017/2022/2025, UK National Security Strategy 2010/2015/2025 and Integrated Review 2021/2023) and are accompanied by implementation action plans, progress reports, mid-term reviews, and statutory oversight acts. Previously, multi-edition `reference` entries that listed `versions_available` without per-version URLs or version child nodes returned only the latest edition's URL even when a caller explicitly requested a historical edition (e.g., `@2018` or `@2010`).
2. Laws and bills regulating AI chatbots and AI companions span pending bills, newly enacted statutes, implementing decrees, and legally enforceable regulatory codes across multiple jurisdictions. Five design questions in `#208` needed explicit answers: how to record bill lifecycle status without breaking the schema, how to handle Bill-to-Act transitions without breaking citations, how to namespace bills versus enacted statutes, how to classify legally binding industry codes registered by a statutory regulator (Australia's eSafety Phase 2 Industry Codes), and whether to add topical tags or use curated inventories/relationships.

**Decision:**

1. **Edition-resolvable version nodes on multi-edition `reference` strategies:** When a `reference` entry declares multiple editions in `versions_available` with distinct primary-source URLs, each edition is given:
   - its edition URL on the `versions_available[]` entry (so source-level `@<version>` queries expose per-edition URLs in `versions_available`),
   - a labelled entry in the parent `match_node.data.urls` array (current edition first), and
   - a child version node (`^<version>$`) carrying `"url"` (so `#<version>` and `@<version>#<version>` subpath queries resolve directly to that edition's document URL as a `ResolutionResult`), `"urls"`, and a structured `ExampleObject` fixture (`[{"input": "<version>", "url": "...", "note": "..."}]`).
2. **Separate `match_node` entries for distinct follow-up reports and distinct strategy series, tagged with `subtype: ["strategy"]`:** Progress audits or implementation reports are not versions of the strategy they evaluate (e.g., Canada's 2005 *Securing an Open Society: One Year Later* is `secid:reference/canada.ca/national-security-policy-progress-report`, distinct from `national-security-policy@2004`). Similarly, distinct strategy series with different official titles (such as the UK's *National Security Strategy* series vs the 2021/2023 *Integrated Review* series) are registered as separate `match_node` entries with cross-references in `notes`. All strategy documents, multi-year action/implementation plans, and strategic reviews or evaluations carry `"subtype": ["strategy"]` on their source-level `match_node.data` (declared under `type: "reference"` in `SecID-Service` `src/type-registry.ts`, [SecID-Service#58](https://github.com/CloudSecurityAlliance/SecID-Service/pull/58)), enabling discovery via `secid:reference?subtype=strategy` across national security/cybersecurity strategies, agency strategic plans, and corporate/organizational strategies, alongside normalized unscoped lookup aliases (`^national-security-strategy$`, `^national-cybersecurity-strategy$`, `^national-cyber-security-strategy$`, `^national-cyber-strategy$`).
3. **Consolidated jurisdiction namespaces and non-breaking Bill-to-Act transitions (`regulation`):**
   - Bills and enacted statutes share a single jurisdiction namespace (`congress.gov`, `parl.ca`, `gov.uk`, `ca.gov`, `ny.gov`, etc.) so a bill's namespace never changes upon enactment.
   - When a bill is enacted under a short title or codified citation, both the Act slug and the bill/Public Act number remain in `patterns` on the same `match_node` (with the primary citation as `patterns[0]`) so pre-enactment and post-enactment SecIDs resolve to the same entry.
   - Separate legal instruments with distinct official texts (such as Brazil's *Lei nº 15.211/2025* and its implementing *Decreto nº 12.880/2026*) are registered as separate `match_node` entries.
   - Legislative status and verification date are recorded consistently at the start of `data.notes` (`Status: <Proposed | Enacted | In force | ...> (...; verified as of YYYY-MM-DD).`), and pre-legislative consultations without a published legislative text (such as the EU Digital Fairness Act as of 2026-11-03) are not given speculative placeholder SecIDs.
4. **Enforceable statutory industry codes belong in `regulation`:** Industry codes registered under statutory authority where registration makes compliance legally binding and enforceable via civil penalties or injunctions (such as Australia's eSafety Phase 2 Industry Codes for Class 1C and Class 2 material under Part 9 of the *Online Safety Act 2021*) are classified under `regulation` (`secid:regulation/esafety.gov.au/phase-2-industry-codes`).
5. **Clean lowercase regex patterns without PCRE `(?i)` prefixes:** In `SecID-Service`, `toRegExp` strips a leading `(?i)` prefix to set the `'i'` flag (leaving unprefixed patterns case-sensitive unless matched against canonical lowercase slugs), whereas raw ECMAScript `new RegExp(pattern)` rejects PCRE inline flags (`(?i)`) with `SyntaxError`. New registry patterns use lowercase canonical slug patterns without `(?i)`.

**Rejected alternatives:**
- **Listing historical strategy editions in `versions_available` without per-edition URLs and version child nodes** — leaves `#<version>` subpath resolution unable to return historical edition URLs and omits per-edition URLs from `versions_available`.
- **Splitting bills and enacted statutes into separate legislative vs statute-consolidator namespaces** — forces every bill's SecID namespace to break when enacted.
- **Adding ad-hoc topical tags (`topic: ["ai-chatbot"]`) to namespace files** — `tags` are namespace-level (`country`, `region`) and cannot scope individual `match_node` entries within a general legislature namespace like `congress.gov` or `ca.gov`; cross-jurisdiction thematic sets belong in research inventories and the Relationship Layer.

**Amendment (2026-11-04): Enforce child/grandchild `ExampleObject.input` pattern matching in `scripts/validate-registry-schema.py`.**
**Decision method:** AI decision (Gemini), reviewed by Codex ([PR #231](https://github.com/CloudSecurityAlliance/SecID/pull/231), closing [#230](https://github.com/CloudSecurityAlliance/SecID/issues/230)).

*Context:* `SecID-Service`'s `test/resolver.test.ts` turns every structured `ExampleObject` (`{"input": "...", "url": "..."}`) on child and grandchild `match_nodes` into an automated resolver test (`secid:<type>/<ns>/<name>[@<version>]#<ex.input>`). When 178 child examples in [#229](https://github.com/CloudSecurityAlliance/SecID/pull/229) carried a duplicate `<name>#<subpath>` prefix in `ex.input` instead of just `<subpath>`, `SecID`'s schema validator passed (because `MatchNode.data` is open-ended in JSON Schema), and the defect was only caught downstream by `SecID-Service`'s pre-deploy test gate during `Upload registry to KV`.

*Decision:* Extend `scripts/validate-registry-schema.py` with `check_child_examples(doc)` so the required `validate-schema` CI gate verifies that every structured `ExampleObject.input` on child/grandchild `match_nodes` matches at least one regex in that node's `patterns[]` (evaluated with ECMAScript-compatible `(?i)` and named-capture semantics).

*Rejected alternatives:*
- **Relying solely on `SecID-Service`'s post-merge `Upload registry to KV` test gate** — catches the mismatch only after a PR has already merged to `SecID` `main`, halting the KV sync rather than blocking the offending PR before merge.
- **Validating `ExampleObject.input` with static JSON Schema pattern rules** — JSON Schema cannot cross-reference a sibling `patterns[]` array dynamically at runtime.

**Second amendment (2026-11-04): Regulation status snapshot semantics ([#228](https://github.com/CloudSecurityAlliance/SecID/issues/228)) and UK/EU statutory subpath patterns ([#133](https://github.com/CloudSecurityAlliance/SecID/issues/133), [#228](https://github.com/CloudSecurityAlliance/SecID/issues/228)).**
**Decision method:** AI decision (Gemini), reviewed by Codex (closing [#133](https://github.com/CloudSecurityAlliance/SecID/issues/133), [#219](https://github.com/CloudSecurityAlliance/SecID/issues/219), and [#228](https://github.com/CloudSecurityAlliance/SecID/issues/228)).

*Context:*
1. On 2026-11-03, `secid:regulation/parl.ca/bill-c-34` (45th Parliament, 1st Session *Safe Social Media Act*) was added with `Status: Proposed (First Reading June 10, 2026 ...; verified as of 2026-11-03)`, synthesized from secondary summaries rather than the live LEGISinfo JSON endpoint (`https://www.parl.ca/legisinfo/en/bill/45-1/c-34/json`), which showed the bill had already passed second reading on `2026-10-29` and been referred to the Standing Committee on Canadian Heritage (`CHPC`). In addition, Canada resets bill numbers every parliamentary session (44th Parliament Bill C-34 was the *National Security Review of Investments Modernization Act*, S.C. 2024, c. 4).
2. UK 2026 statutes (`gov.uk/crime-and-policing-act-2026`, `gov.uk/childrens-wellbeing-and-schools-act-2026`, and `gov.uk/osa`) lacked child `match_nodes` for section-level resolution (`#s-248`, `#s-70`, `#s-1`), and EU regulations/directives (`europa.eu/ai-act`, `gdpr`, `nis2`, `dora`) only accepted top-level article integers (`^art-\d+$`) and bare Roman-numeral annexes (`^annex-[IVX]+$`), failing to resolve paragraph/point citations (`#art-32.1.a`, `#art-17.1.a`, `#annex-IV.2.f`) or recitals/chapters (`#recital-81`, `#chapter-2`).

*Decision:*
1. **Three rules for regulation status snapshots (`scripts/check-regulation-status.py`):**
   - `Status: <Proposed | Enacted | In force | Died on the Order Paper> (...; verified as of YYYY-MM-DD)` in `data.notes` is a **dated snapshot** for finding and sorting. Every `Status:` note in `registry/regulation/` is validated in CI by `scripts/check-regulation-status.py` to require a valid ISO `verified as of YYYY-MM-DD` date and status category.
   - **The snapshot is never a substitute for the live primary source:** any agent, paper, or tool stating a bill's or statute's current legal state must re-check the live primary source URL (such as Parliament of Canada's LEGISinfo `/json` endpoint) before citing it, and update the snapshot via PR if it has moved.
   - **Terminal states are not exempt from re-verification:** `Proposed` snapshots have a 90-day re-verification threshold and terminal snapshots (`Enacted`, `In force`, `Died on the Order Paper`) have a 180-day threshold in `scripts/check-regulation-status.py`, because bills get reintroduced across sessions and enacted statutes commence in phases or get amended/enjoined.
   - Where a legislature reuses bill numbers across parliamentary sessions (such as `parl.ca`), `data.notes` records the session number and cross-references notable prior-session homonyms.
2. **Statutory and regulatory subpath patterns:**
   - UK Acts in `registry/regulation/uk/gov.json` (`osa`, `crime-and-policing-act-2026`, `childrens-wellbeing-and-schools-act-2026`) expose `^s-\d+[A-Z]?$` child nodes resolving to `https://www.legislation.gov.uk/ukpga/<year>/<chapter>/section/{num}` (with legislative history such as Commons amendment `NC120` recorded in `notes`).
   - EU acts in `registry/regulation/eu/europa.json` (`gdpr`, `ai-act`, `nis2`, `dora`) expose bounded article/paragraph/point patterns (`^art-<bounded-range>(\.\d+)*(\.[a-z])*$`), bounded annex/section/point patterns (`^annex-(?:I|...|XIII)(\.\d+)*(\.[a-z])*$`), and bounded chapter and recital patterns (`^chapter-<bounded-range>$`, `^recital-<bounded-range>$`) matching each instrument's actual provision range.

*Rejected alternatives:*
- **Removing status notes from `registry/regulation/` entirely** — removes context that helps practitioners distinguish an active bill from an enacted statute during discovery.
- **Exempting `Enacted`, `In force`, or `Died on the Order Paper` from re-verification** — misses phased commencement, judicial stays, repealing acts, and reintroduction of dead bills in subsequent legislative sessions.

---

## 2026-11-05: Resolver semantics (`#177`, `#181`, `#190`) and CI validation gates (`#100`, `#101`, lowercase namespaces)

**Decision:** Align the `SecID` validator suite and CI gates with `SecID-Service` ([#65](https://github.com/CloudSecurityAlliance/SecID-Service/pull/65)) and `SecID-Server-API` ([#34](https://github.com/CloudSecurityAlliance/SecID-Server-API/pull/34)) across five rules:
1. **`lookup_table` precedence over `url` ([#177](https://github.com/CloudSecurityAlliance/SecID/issues/177)):** When a child `match_node` declares both `data.lookup_table` and `data.url`, resolvers and `scripts/check-examples.py` try `lookup_table` first (exact key match, then case-insensitive fallback) and fall back to the `data.url` template when the subpath is not in `lookup_table`, matching `docs/reference/REGISTRY-JSON-FORMAT.md`.
2. **Preserve literal `.` in canonical source names ([#181](https://github.com/CloudSecurityAlliance/SecID/issues/181)):** Unescape `\.` before testing literalness in `extractNameSlug` (`SecID-Service` / `SecID-Server-API`) and `scripts/check-canonical-names.py` (`^[A-Za-z0-9._-]+$`), so dotted source names (`x.1060`, `sp800-53r5.1.1`, `tls1.3`, `cvss3.1`) resolve to their literal identifier instead of falling back to slugifying `node.description`.
3. **`data.known_values` closes a pattern in unscoped search ([#190](https://github.com/CloudSecurityAlliance/SecID/issues/190)):** A node with a non-empty `data.known_values` array is closed by enumeration (unless `open_pattern: true` is explicitly set): during unscoped cross-source search, resolvers check membership in `data.known_values` (case-insensitively when the pattern carries `(?i)`), while namespace-scoped resolution continues to accept `open_pattern: true` nodes at any depth.
4. **Subtype placement and completeness validation ([#100](https://github.com/CloudSecurityAlliance/SecID/issues/100), [#101](https://github.com/CloudSecurityAlliance/SecID/issues/101)):** `scripts/validate-subtypes.py` fails when `data.subtype` appears on a depth > 0 child/grandchild `match_node` (enforcing the source-level-only rule in `SUBTYPES.md`), supports `--completeness off|warn|fail` (wired in `.github/workflows/registry-ci.yml` as `--completeness warn` across partially tagged types), and enforces 100% source-level subtype completeness on fully tagged types (`ENFORCED_COMPLETE_TYPES = {"methodology"}`).
5. **Lowercase namespace and filename stem validation (Unicode IDN-safe):** `schemas/registry-namespace.schema.json` rejects ASCII uppercase and whitespace in `namespace` (`^[^A-Z\s]+$`) while preserving Unicode IDNs per `SPEC.md §4.2`, and `scripts/validate-registry-schema.py` enforces `ns == ns.lower()` and `path.stem == path.stem.lower()` (with `.lower()` normalization added to `scripts/generate-cna-disclosure.py` and `scripts/generate-entity-stubs-from-disclosure.py`) so mixed-case CNA imports can never produce unreachable registry keys.

**Decision method:** AI decision (Gemini), reviewed by Codex (closing [#100](https://github.com/CloudSecurityAlliance/SecID/issues/100), [#101](https://github.com/CloudSecurityAlliance/SecID/issues/101), [#177](https://github.com/CloudSecurityAlliance/SecID/issues/177), [#181](https://github.com/CloudSecurityAlliance/SecID/issues/181), [#190](https://github.com/CloudSecurityAlliance/SecID/issues/190)).

**Rejected alternatives:**
- **Restricting `namespace` in JSON Schema to ASCII `^[a-z0-9.-]+(/[a-z0-9._-]+)*$`** — breaks Unicode IDN namespaces permitted by `SPEC.md §4.2`.
- **Setting `--completeness fail` globally across all types immediately** — `advisory`, `disclosure`, `entity`, and `reference` still have 935 untagged legacy source nodes; enforcing `ENFORCED_COMPLETE_TYPES = {"methodology"}` locks in completed types immediately without breaking CI on legacy backlog.

---

## 2026-11-05: Zero pattern-breadth debt (`#158`, `#159`, `#52`), CWE 5.0 REST API (`SecID-Internal-Research#17`), and classification/timestamp decisions (`#60`, `#73`, `#102`)

**Decision:**
1. **Eliminate all remaining `scripts/pattern-breadth-todo.json` exemptions (`#158`, `#159`, `#52`):**
   - **`control/bsi.bund.de/c5`, `ai-c4`, and `a5` ([#158](https://github.com/CloudSecurityAlliance/SecID/issues/158)):** Enumerate all 20 BSI C5 domain and General Conditions codes across C5:2020 and C5:2026 (`AM`, `BC`, `BCM`, `COM`, `COS`, `CRY`, `DEV`, `GC`, `HR`, `IAM`, `IDM`, `INQ`, `OIS`, `OPS`, `PI`, `PS`, `PSS`, `SIM`, `SP`, `SSO`) in `patterns[0]` and `data.known_values` (verified against BSI's official C5:2020 and C5:2026 workbooks), and tighten the C5 criterion, C5:2026 sub-criterion, AIC4 criterion, and A5 subgroup/control patterns to use their explicit domain/group alternations.
   - **`control/owasp.org/ai-exchange` and `weakness/owasp.org/ai-exchange` ([#159](https://github.com/CloudSecurityAlliance/SecID/issues/159), [#52](https://github.com/CloudSecurityAlliance/SecID/issues/52)):** Enumerate all 65 OWASP AI Exchange control, control-group, and redirect-alias IDs from `OWASP/www-project-ai-security-and-privacy-guide` (`content/ai_exchange/content/docs/*.md` and `content/ai_exchange/firebase.json`) in `patterns[0]` and `data.known_values`, and switch `data.url` to `https://owaspai.org/goto/{id_lower}/` across both `control` and `weakness` (because `owaspai.org`'s Firebase Hosting `/go/<slug>` redirect table is lowercase-only and returns HTTP 404 on uppercase `/goto/{id}/`). Also tighten `weakness/owasp.org/agentic-top10` from `^ASI\d{2}$` to `^ASI(?:0[1-9]|10)$` and point its `data.url` to the live resource page (`https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/`). Empty `scripts/pattern-breadth-todo.json` (`"entries": []`).
2. **CWE 5.0 (Schema 8.0), CWE 4.21 (Schema 7.4), and CWE REST API resolution ([`SecID-Internal-Research#17`](https://github.com/CloudSecurityAlliance-Internal/SecID-Internal-Research/issues/17)):**
   - Update `weakness/mitre.org/cwe` with CWE `5.0` (`current`, XSD 8.0, 2026-10-28), `4.21` (`superseded`, parallel Schema 7.4 transition release, 2026-10-28), and `4.20` (`superseded`, XSD 7.3, 2026-04-30), and add type-partitioned sibling child `match_nodes` for the official MITRE CWE REST API JSON endpoints (`https://cwe-api.mitre.org/api/v1/cwe/weakness/{num}` across all 984 weakness IDs, `/api/v1/cwe/category/{num}` across all 431 grouping/category IDs, and `/api/v1/cwe/view/{num}` across all 62 view IDs at weight 50, plus universal entry-type lookup `https://cwe-api.mitre.org/api/v1/cwe/{num}` at weight 40, `content_type: "application/json"`, `parsability: "structured"`).
   - Update `reference/mitre.org/cwe-schema` with XSD `8.0` (`current`) and `7.4` (`superseded`) version metadata and child version nodes (`^8\.0$`, `^7\.4$`).
3. **Sharper `methodology` vs `reference` boundary test ([#73](https://github.com/CloudSecurityAlliance/SecID/issues/73)):** Codify the **Format-Stripping Test** and **Provenance-Field Test** in `registry/methodology.md` and `docs/explanation/DESIGN-DECISIONS.md` to distinguish methodologies with an output syntax (CVSS, TLP, SP 800-53A) from data-format schemas where slot assignment is left to external processes (OpenVEX, CSAF, SARIF, OSCAL).
4. **Timestamp metadata fields ([#60](https://github.com/CloudSecurityAlliance/SecID/issues/60)):** Record in `docs/proposals/TIMESTAMP-FIELDS.md` that optional `checked`/`updated`/`note` fields on namespace roots and `UrlObject` entries (already in `schemas/registry-namespace.schema.json`) plus dated `Status: ... (verified as of YYYY-MM-DD)` snapshots in `registry/regulation/` (`scripts/check-regulation-status.py`) are accepted, while per-scalar `field_checked`/`field_updated`/`field_note` sibling suffixes are declined.
5. **Minimal-diff and counting conventions ([#102](https://github.com/CloudSecurityAlliance/SecID/issues/102)):** Document in `CONTRIBUTING.md` that contributors and agents must not re-serialize entire registry JSON files when editing single nodes and must distinguish namespace-file counts, source-level `match_node` counts (`scripts/update-counts.sh`), and total recursive `match_node` counts.

**Decision method:** AI decision (Gemini), reviewed by Codex (closing [#52](https://github.com/CloudSecurityAlliance/SecID/issues/52), [#60](https://github.com/CloudSecurityAlliance/SecID/issues/60), [#73](https://github.com/CloudSecurityAlliance/SecID/issues/73), [#102](https://github.com/CloudSecurityAlliance/SecID/issues/102), [#158](https://github.com/CloudSecurityAlliance/SecID/issues/158), [#159](https://github.com/CloudSecurityAlliance/SecID/issues/159), [#193](https://github.com/CloudSecurityAlliance/SecID/issues/193), and [`SecID-Internal-Research#17`](https://github.com/CloudSecurityAlliance-Internal/SecID-Internal-Research/issues/17)).

**Rejected alternatives:**
- **Keeping `control/owasp.org/ai-exchange` as `^[A-Z]+$` with `known_values` and `open_pattern: true`** — all 65 OWASP AI Exchange control IDs are finite and known from `OWASP/www-project-ai-security-and-privacy-guide`, so expressing the exact alternation in `patterns[0]` validates both scoped and unscoped queries in every resolver without needing an open-pattern exemption.
- **Adding `field_checked` / `field_updated` / `field_note` sibling properties for every scalar field in `match_nodes[].data`** — multiplies property counts by 4x across 2,262 files when `UrlObject.checked`/`updated` and CI example probes (`scripts/check-examples.py`) already cover URL freshness cleanly.

---

## 2026-11-06: Registry hygiene & architecture batch (`#53`, `#54`, `#55`, `#56`, `#57`, `#58`, `#61`, `#63`, `#71`, `#76`, `#186`)

**Decision:**
1. **Subtype tagging completion and partition-vs-specialization model ([#53](https://github.com/CloudSecurityAlliance/SecID/issues/53)):**
   - Backfill `"subtype": ["glossary"]` onto all 164 untagged glossary `match_nodes` in `registry/reference/` (bringing tagged glossaries to 166), `"subtype": ["strategy"]` onto the 3 untagged strategy/plan nodes in `registry/reference/ca/canada.json` and `registry/reference/ca/gc/publicsafety.json` (bringing tagged strategies to 240), and `"subtype": ["incident"]` onto `registry/advisory/gov/fda.json#maude` (FDA medical device adverse event reports, bringing tagged incident nodes to 7).
   - Codify in `docs/reference/TYPES-AND-SUBTYPES.md` the architectural distinction between **exhaustive-partition subtypes** (`methodology`, where every source-level `match_node` belongs to at least one of the 11 categories and CI enforces 100% completeness via `ENFORCED_COMPLETE_TYPES = {"methodology"}` in `scripts/validate-subtypes.py`) and **specialization (carve-out) subtypes** (`advisory: incident`, `disclosure: coordinator|psirt`, `entity: consortium`, `reference: glossary|strategy`), where baseline items of the type intentionally omit `data.subtype`.
2. **100% publisher `entity/` coverage for `control/` and `methodology/` ([#54](https://github.com/CloudSecurityAlliance/SecID/issues/54)):**
   - Generate the 33 remaining publisher `registry/entity/` files for every `registry/control/` (20 files) and `registry/methodology/` (13 files, including cyber-rating providers `bitsight.com`, `securityscorecard.com`, `upguard.com`, and `cybercube.com`) namespace that lacked an `entity/` counterpart, achieving 100% 1:1 `entity/` publisher coverage across `control/` and `methodology/`.
3. **ENX ISA v6.0, TISAX methodology, and ISF SOGP ([#55](https://github.com/CloudSecurityAlliance/SecID/issues/55)):**
   - Add `registry/methodology/com/enx.json` (`tisax`, `subtype: ["audit-certification"]`, cross-referencing `secid:control/enx.com/isa`), and add `versions_available` metadata (`6.0` current / `5.1` superseded on `control/enx.com/isa`; `2024` current / `2023` / `2022` superseded on `control/securityforum.org/sogp`).
4. **Structured disclosure fields documentation, top-20 vendor `safe_harbor` & `bug_bounty`, and 100% CNA shortName mapping ([#56](https://github.com/CloudSecurityAlliance/SecID/issues/56), [#57](https://github.com/CloudSecurityAlliance/SecID/issues/57)):**
   - Document the 5 reserved disclosure `data` fields (`cve`, `safe_harbor`, `bug_bounty`, `security_txt`, `disclosure_policy`) in `docs/reference/REGISTRY-JSON-FORMAT.md`.
   - Populate verified `data.safe_harbor` and `data.bug_bounty` across the top-20 vendor disclosure files (`microsoft.com`, `google.com`, `apple.com`, `redhat.com`, `cisco.com`, `amazon.com`, `oracle.com`, `ibm.com`, `adobe.com`, `mozilla.org`, `salesforce.com`, `github.com`, `atlassian.com`, `cloudflare.com`, `broadcom.com` (VMware), `citrix.com`, `fortiguard.com` (Fortinet), `paloaltonetworks.com`, `sap.com`, `dell.com`).
   - Enrich the 23 previously unmapped CNA nodes in `registry/disclosure/` from `CNAsList.json` and `cvelistV5`, bringing unmapped CNA nodes from 23 to `0`.
5. **Decline `assertion` and `content` top-level types ([#61](https://github.com/CloudSecurityAlliance/SecID/issues/61)):**
   - Record in `docs/proposals/ASSERTION-CONTENT-TYPES.md` and `docs/reference/TYPES-AND-SUBTYPES.md` that `0` new top-level types are added: organizational compliance attestations belong in the Relationship Layer (backed by existing `control` frameworks and `methodology` `audit-certification` entries), normative Bodies of Knowledge belong in `control` (`subtype: ["body-of-knowledge"]`), and instructional courses belong in `reference` (`subtype: ["course"]`).
6. **CIS Benchmarks license posture and cloud foundation benchmarks ([#63](https://github.com/CloudSecurityAlliance/SecID/issues/63)):**
   - Record that CIS Benchmarks are **registry-only metadata/IDs** under `control/cisecurity.org` per `DATA-HOSTING-RULES.md` (no redistribution of copyrighted per-recommendation prose in public dataset repositories without explicit CIS permission), and add versioned `match_nodes` and recommendation ID patterns (`^\d{1,2}\.\d{1,2}(?:\.\d{1,2})?$`) for `aws-foundations-benchmark`, `azure-foundations-benchmark`, `gcp-foundations-benchmark`, and `kubernetes-benchmark` in `registry/control/org/cisecurity.json`.
7. **Modeling CSA CCM and AICM implementation and audit guidelines ([#71](https://github.com/CloudSecurityAlliance/SecID/issues/71)):**
   - Per-control implementation guidelines and auditing guidelines share the exact 1:1 `XXX-NN` control identifier space of CCM and AICM and are therefore bundled facets of `secid:control/cloudsecurityalliance.org/ccm` and `secid:control/cloudsecurityalliance.org/aicm` (paralleling NIST SP 800-53 Supplemental Guidance), unlike `ccm-caiq` and `aicm-caiq` which define a distinct `XXX-NN.M` question identifier hierarchy.
   - For citations targeting the standalone audit methodologies as documents/processes, add `ccm-auditing-guidelines` and `aicm-auditing-guidelines` (`subtype: ["audit-certification"]`) in `registry/methodology/org/cloudsecurityalliance.json`, cross-referencing `secid:control/cloudsecurityalliance.org/ccm` and `aicm` and the artifact slugs in `secid:reference/cloudsecurityalliance.org/artifacts`.
8. **Executable check catalogs (`#186`) and Prowler check catalog ([#58](https://github.com/CloudSecurityAlliance/SecID/issues/58), [#186](https://github.com/CloudSecurityAlliance/SecID/issues/186)):**
   - Automated security check catalogs whose individual check IDs are cited in posture findings, remediation tickets, and compliance crosswalks as normative security checks (e.g., Prowler checks, DISA STIGs) belong in **`control/`** (with candidate `subtype: ["check-catalog"]` documented in `TYPES-AND-SUBTYPES.md`), whereas scanner tools themselves belong in `entity/` and exchange/signature formats (OVAL, SARIF) belong in `reference/`.
   - Add `registry/control/com/prowler.json` (`checks` / `prowler`, resolving snake_case check IDs to `https://hub.prowler.com/check/{id_lower}` with `open_pattern: true`) and `registry/entity/com/prowler.json`.
9. **Scheduled/manual CNA refresh and `known-broken.json` audit workflow ([#76](https://github.com/CloudSecurityAlliance/SecID/issues/76)):**
   - Add `.github/workflows/cna-refresh.yml` (weekly cron + `workflow_dispatch`) to fetch upstream `CNAsList.json`, run `scripts/audit-known-broken.py`, report any unmapped or newly added upstream CNAs, and verify `scripts/apply-known-broken.py --dry-run` without overwriting `working-data/cna/known-broken.json`.

**Decision method:** AI decision (Gemini), reviewed by Codex (closing [#53](https://github.com/CloudSecurityAlliance/SecID/issues/53), [#54](https://github.com/CloudSecurityAlliance/SecID/issues/54), [#55](https://github.com/CloudSecurityAlliance/SecID/issues/55), [#56](https://github.com/CloudSecurityAlliance/SecID/issues/56), [#57](https://github.com/CloudSecurityAlliance/SecID/issues/57), [#58](https://github.com/CloudSecurityAlliance/SecID/issues/58), [#61](https://github.com/CloudSecurityAlliance/SecID/issues/61), [#63](https://github.com/CloudSecurityAlliance/SecID/issues/63), [#71](https://github.com/CloudSecurityAlliance/SecID/issues/71), [#76](https://github.com/CloudSecurityAlliance/SecID/issues/76), and [#186](https://github.com/CloudSecurityAlliance/SecID/issues/186)).

**Rejected alternatives:**
- **Adding `assertion` and `content` as 11th and 12th top-level SecID types (`#61`)** — requires a 4-repo breaking type-list expansion when existing `control` (`body-of-knowledge`), `reference` (`course`), `methodology` (`audit-certification`), and the Relationship Layer represent every concept cleanly.
- **Adding a new top-level `check` or `rule` type for executable security checks (`#186`)** — check IDs in Prowler, DISA STIGs, and CIS Benchmarks are cited identically to controls in compliance crosswalks and findings; keeping them in `control/` preserves uniform resolution and crosswalk mapping.
- **Auto-committing upstream `CNAsList.json` overwrites in CI (`#76`)** — blindly re-running CNA generation without auditing `working-data/cna/known-broken.json` would clobber curated fixes or miss upstream URL replacements that require manual verification.

---

## 2026-11-06: Zero-egress GitHub data serving, domain-first exhaustive local extraction, and `SecID-Data*` sharding (amending ADR-010, ADR-011, ADR-013; closing `#64`)

**Date:** 2026-11-06
**Status:** Accepted
**Decision method:** Kurt directive (2026-11-06), recorded by Gemini and reviewed by Codex (closing [#64](https://github.com/CloudSecurityAlliance/SecID/issues/64))

**Context:**
1. `CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards` predates SecID and currently holds 645 MB of tracked files (256 MB `.git` packfile), of which 135.9 MB are PDF-extracted `.jpeg`/`.png` images that do not delta-compress in Git, and 67% is concentrated in a handful of large domains (`nist.gov` 217.7 MB, `cloudsecurityalliance.org` 94.1 MB, `pcisecuritystandards.org` 51.5 MB, `mitre.org` 39.8 MB, `fedramp.gov` 31.9 MB).
2. In Git, committing large datasets into a general repository and later running `git rm` to split them out **does not reclaim space in `.git/objects/pack`** without rewriting history (`git filter-repo` + force-push).
3. Similarly, wiring `SecID` registry nodes to `dataset-public-laws-regulations-standards` now and re-pointing them later when data moves to `SecID-Data*` would cause unnecessary URL churn across the registry.

**Decision (Kurt, 2026-11-06):**
1. **Zero-egress data serving via `raw.githubusercontent.com` (shelve R2 for now):**
   - Serve SecID 2.0 public structured content directly from GitHub (`raw.githubusercontent.com/CloudSecurityAlliance/SecID-Data.../main/data/<type>/<reverse-dns>/...`) via standard `match_node` `data.url` / `data.urls[]` entries (`format: "json"`, `parsability: "structured"`).
   - Shelve Cloudflare R2 direct serving for now so storage/transfer costs remain `$0` and datasets remain git-versioned and one-command `git clone`-able.
2. **Domain-first exhaustive local extraction & measurement before committing to Git:**
   - *"basically for any given domain (mitre.org, etc.) we agressively find and extract every possible secid thing locally, and then decide what to do. also for some like .gov or nist.gov or cisa.gov or europa.eu we'll just assume we need to do it from the start."* — Kurt, 2026-11-06.
   - *"we should probably agressively try to get everything from a domain/country/etc and see how big it is.... we can put it in, but removing it doesn't really save space."* — Kurt, 2026-11-06.
   - Before committing a domain or country to a `SecID-Data*` repository, aggressively discover and extract its complete SecID-resolvable corpus locally into the ADR-014 layout (`data/<type>/<reverse-dns>/<name>/<version>/...`), strip binary files (`.pdf`, `.xlsx`, `.jpeg`, `.png`), and measure both unpacked size and packed `.git` size.
3. **Pragmatic `SecID-Data*` sharding (~50–100 MB threshold + anchor authorities, superseding ADR-011's 8-region grid):**
   - *"also it seems like nist.gov, cisa.gov, fedramp.gov, they are important enough to simply have their own repo like disa.mil. what happens if we break it up more? it seems like... anything over 50-100 megs should probably be it's own repo?"* — Kurt, 2026-11-06.
   - Major anchor authorities and domains/TLDs that exceed (or are projected to exceed) ~50–100 MB get dedicated `CloudSecurityAlliance/SecID-Data-<domain/tld>` repositories from the start (e.g., `SecID-Data-disa.mil`, `SecID-Data-nist.gov`, `SecID-Data-cisa.gov`, `SecID-Data-fedramp.gov`, `SecID-Data-cloudsecurityalliance.org`, `SecID-Data-europa.eu`, `SecID-Data-gov`, `SecID-Data-ca`), while smaller domains share `CloudSecurityAlliance/SecID-Data`.
4. **Point Once & Phase Out `dataset-public-laws-regulations-standards`:**
   - Gradually migrate public content out of `dataset-public-laws-regulations-standards` into `SecID-Data*` (moving proprietary content like PCI DSS/HITRUST to `dataset-private-laws-regulations-standards` and relying on upstream APIs/repos where authoritative per-item JSON already exists, such as MITRE's CWE REST API and `attack-stix-data`).
   - Only add `raw.githubusercontent.com` links to `CloudSecurityAlliance/SecID` registry nodes **after** a domain's content is in its permanent `SecID-Data*` repository, so pointers are written once and never churned.
5. **Pre-extraction upstream catalog discovery, jurisdiction & umbrella domain grouping, sector metadata, and defensive upstream mirror insurance (2026-11-06–2026-11-09, [`#238`](https://github.com/CloudSecurityAlliance/SecID/issues/238)–[`#272`](https://github.com/CloudSecurityAlliance/SecID/issues/272); canonical list in [`DATA-HOSTING-RULES.md` §3](docs/reference/DATA-HOSTING-RULES.md#3-canonical-list-of-separate-secid-data--repositories)):**
   - **Upstream catalog & publishing architecture discovery before extraction ([`#244`](https://github.com/CloudSecurityAlliance/SecID/issues/244)):** Before extracting a jurisdiction or standards authority, map its complete publishing architecture (e.g., the 5 official US federal legal/regulatory portals: `congress.gov` bills, `govinfo.gov` Public Laws, `uscode.house.gov` U.S. Code, `ecfr.gov` Code of Federal Regulations, and `federalregister.gov`/`whitehouse.gov` daily rules & directives; Canada `parl.ca` & `laws-lois.justice.gc.ca`; UK `legislation.gov.uk`; EU `eur-lex.europa.eu`; Japan `laws.e-gov.go.jp`; Germany `gesetze-im-internet.de`) and enumerate full control/clause ID catalogs in `SecID/registry/` even for paywalled `Rule 0` SDOs (`iso.org`+`iec.ch`, `isaca.org`, `isc2.org`, `cisecurity.org`, `pcisecuritystandards.org`, `aicpa.org`, `etsi.org`+`cen.eu`, [`#255`](https://github.com/CloudSecurityAlliance/SecID/issues/255)).
   - **Jurisdiction-first repository sharding with sector as metadata ([`#242`](https://github.com/CloudSecurityAlliance/SecID/issues/242), [`#247`](https://github.com/CloudSecurityAlliance/SecID/issues/247)–[`#252`](https://github.com/CloudSecurityAlliance/SecID/issues/252), [`#256`](https://github.com/CloudSecurityAlliance/SecID/issues/256), [`#258`](https://github.com/CloudSecurityAlliance/SecID/issues/258)–[`#261`](https://github.com/CloudSecurityAlliance/SecID/issues/261)):** Major national/supranational jurisdictions (`SecID-Data-gov`, `SecID-Data-europa.eu`, `SecID-Data-ca`, `SecID-Data-jp`, `SecID-Data-uk`, `SecID-Data-de`, `SecID-Data-au`, `SecID-Data-sg`, `SecID-Data-in`, `SecID-Data-cn`) get dedicated repositories so practitioners can clone 100% of their jurisdiction's laws, controls, and sector guidelines, while industry sectors (`financial`, `healthcare`, `transportation`, `energy`, `telecom`, `government`, `cross-sector`) are modeled via the existing `tags.sector` / `match_nodes[].data.tags.sector` metadata field + cross-repo index manifests rather than competing sector Git repositories.
   - **Umbrella domain grouping (`cve.org` → `SecID-Data-mitre.org`, `cyclonedx.org`+`owaspai.org` → `SecID-Data-owasp.org`, etc., [`#245`](https://github.com/CloudSecurityAlliance/SecID/issues/245), [`#253`](https://github.com/CloudSecurityAlliance/SecID/issues/253), [`#254`](https://github.com/CloudSecurityAlliance/SecID/issues/254), [`#262`](https://github.com/CloudSecurityAlliance/SecID/issues/262)):** Sibling/operated domains roll into their parent authority or jurisdiction repository (`cve.org` → `SecID-Data-mitre.org`; `csrc.nist.gov`/`nvd.nist.gov` → `SecID-Data-nist.gov`; `niccs.cisa.gov` → `SecID-Data-cisa.gov`; `cyber.mil` → `SecID-Data-disa.mil`; `ico.org.uk`/`fca.org.uk` → `SecID-Data-uk`; `gesetze-im-internet.de`/`bafin.de` → `SecID-Data-de`; `cert-in.org.in`/`rbi.org.in` → `SecID-Data-in`; `tc260.org.cn` → `SecID-Data-cn`; `cyclonedx.org`/`owaspai.org` → `SecID-Data-owasp.org`; `spdx.dev`/`openvex.dev`/`slsa.dev` → OpenSSF/LF in `SecID-Data`) while keeping their canonical `data/<type>/<tld>/<domain>/<name>/<version>/...` internal `ADR-014` directory paths. Pinned format schemas (`#203`) and per-domain glossaries (`#62`) fold directly into these `SecID-Data*` repositories rather than requiring separate special-purpose repos.
   - **Defensive upstream dataset forks / mirror insurance ([`#246`](https://github.com/CloudSecurityAlliance/SecID/issues/246), [`#263`](https://github.com/CloudSecurityAlliance/SecID/issues/263)–[`#272`](https://github.com/CloudSecurityAlliance/SecID/issues/272)):** For massive upstream per-item repositories (`CVEProject/cvelistV5` `3.25 GB`, `github/advisory-database` `3.50 GB`, `cisagov/vulnrichment` `375.7 MB`, `mitre-attack/attack-stix-data` `134.3 MB`, `CVEProject/cve-schema` `482.8 MB`, `ossf/osv-schema` `0.9 MB`, `cisagov/CSAF` `59.0 MB`, `golang/vulndb` `53.8 MB`, `rustsec/advisory-db` `44.5 MB`, `pypa/advisory-database` `21.9 MB`), maintain gated-sync GitHub forks (`SecID-Data-cvelistV5`, `SecID-Data-advisory-database`, `SecID-Data-vulnrichment`, `SecID-Data-attack-stix-data`, `SecID-Data-cve-schema`, `SecID-Data-osv-schema`, `SecID-Data-CSAF`, `SecID-Data-vulndb`, `SecID-Data-rustsec-advisory-db`, `SecID-Data-pypa-advisory-database`, which share GitHub's parent object store at `$0` quota) so SecID can fail over via a one-line prefix swap if upstream ever breaks its layout or force-pushes bad data.

**Rejected alternatives:**
- **Serving content from Cloudflare R2 now** — incurs storage/operation setup and loses git-tag history and `git clone` simplicity when `raw.githubusercontent.com` serves per-item JSON at `$0` egress.
- **Committing everything into a single `SecID-Data` repo first and running `git rm` later when a domain grows large** — `git rm` leaves deleted blobs in `.git/objects/pack` forever unless history is rewritten.
- **Adding interim `raw.githubusercontent.com` links to `dataset-public-laws-regulations-standards` before migrating to `SecID-Data*`** — causes avoidable registry diff churn and breaks cached URLs when migrated.

---

## 2026-11-09: Four-tier public/private data-hosting rule, 100% public hosting for National Security, Defense, Cybersecurity & AI Strategies, strategy version-node `"type": "version"` standardization, and extracted section/pillar subpath `match_nodes` (`#274`)

**Date:** 2026-11-09
**Status:** Accepted
**Decision method:** Kurt directives (2026-11-09), recorded by Gemini and reviewed by Codex (closing [#274](https://github.com/CloudSecurityAlliance/SecID/issues/274), [`dataset-public-laws-regulations-standards#141`](https://github.com/CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards/issues/141), and [`dataset-private-laws-regulations-standards#11`](https://github.com/CloudSecurityAlliance-DataSets/dataset-private-laws-regulations-standards/issues/11))

**Context:**
1. During Track 2 Wave 1 and Wave 2 extraction of the 404 National Security, Defense, Cybersecurity, and AI Strategy editions (`240` `subtype: ["strategy"]` sources across `139` `registry/reference/` files), 46 editions across 20 government and intergovernmental portals (`au.int`, `cncs.gob.do`, `csa.gov.sg`, `cyber.gov.il`, `defence.gov.au`, `dsn.gob.es`, `hcpn.gouvernement.lu`, `homeaffairs.gov.au`, `itu.int`, `mcit.gov.qa`, `meity.gov.in`, `micitt.go.cr`, `mnd.gov.tw`, `mset.gov.jm`, `nacsa.gov.my`, `ncsa.gov.qa`, `oas.org`, `puc.bz`, `smartnation.gov.sg`, `u.ae`) — as well as 39 open-web no-login glossaries (`bsi.bund.de/glossary`, `apple.com`, `barracuda.com`, `beyondtrust.com`, `bitsight.com`, `checkmk.com`, `cisco.com`, `cloudflare.com`, `cyberark.com`, `forescout.com`, `microsoft.com`, `paloaltonetworks.com`, `vulncheck.com`) and 36 public-government / open-web `control/` stubs — had been conservatively placed in `dataset-private-laws-regulations-standards` because their portal terms of use or website footers contained generic copyright or non-commercial boilerplate.
2. On 2026-11-09, Kurt reviewed the split placement of national security strategies and established both the immediate strategy migration directive and the general 4-tier data-hosting policy:
   - *"ok pause. the national security strategies are gov docs and public release, they are freely available. I can comfortable violating the license on them, so lets move all the stuff from dataset-private-laws-regulations-standards  to the public. and then also update SecID."*
   - *"so in general anything we get from a public gov website, goes into the public dataset repo regardless of license. in general if it's on the web, and there's no login, we treat it as if we can mirror it. if there is a free login, ask me, and if it' a paid login, or paid access like iso.org, we do NOT mirror it publicly ever unless there is a specific exception granted, and it would have to be explicit and well documented and have solid reasons for it."*
3. Separately, Kurt directed on 2026-11-09 (*"lets first extract and structure ALL the data, and then add all the items with subopaths/etc to secid, so basically two batches of work"*) that the extracted section/chapter/pillar subpaths from the 207 full-text extracted strategy editions and 4 extracted Canadian national security statutes (`ccspa`, `national-security-act-2017`, `nsira-act`, `nsicop-act`) be wired into `CloudSecurityAlliance/SecID` without adding interim `raw.githubusercontent.com` URLs before the permanent `SecID-Data*` domain split.

**Decision:**
1. **Four-Tier Public vs. Private Data-Hosting Rule ([`DATA-HOSTING-RULES.md` §Rule 0](docs/reference/DATA-HOSTING-RULES.md#rule-0-the-four-tier-access--license-rule-2026-11-09)):**
   - **Tier 1 (Public government / intergovernmental websites):** Anything fetched from a public government or intergovernmental website goes into the public dataset repository (`SecID-Data*` / `dataset-public-laws-regulations-standards`) **regardless of license** (preserving attribution and upstream license fields in `-metadata.json` with `publicly_redistributable: true`).
   - **Tier 2 (Public web, no login required):** Anything publicly available on the web without a login (including open standards and public vendor glossaries/documentation) is treated as publicly mirrorable and placed in the public dataset repository with attribution and source terms preserved in `-metadata.json`.
   - **Tier 3 (Free login required, e.g., CIS Benchmarks PDF download, Open Group TOGAF / Open FAIR, NFPA):** Ask Kurt first (`needs-kurt` governance issue) before mirroring publicly.
   - **Tier 4 (Paid login, paid purchase, or members-only access, e.g., `iso.org`, `iec.ch`, `bsigroup.com`, `cen.eu`, `isaca.org`, `hitrustalliance.net`, `swift.com`):** Never mirror publicly unless a specific, explicit, well-documented exception with solid reasons is granted by Kurt. Keep extracted reference copies strictly in `dataset-private-laws-regulations-standards`, and register only uncopyrighted identifiers, titles, and URLs in `SecID/registry/`.
2. **100% public hosting for government & intergovernmental public-release strategies (`DATA-HOSTING-RULES.md`):**
   - All `404` registered strategy editions (`subtype: ["strategy"]` in `registry/reference/`) are hosted in the **public** dataset repositories (`207` full-text extracted + `197` `metadata-only` stubs; migrated in [`dataset-public-laws-regulations-standards#142`](https://github.com/CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards/pull/142) and [`dataset-private-laws-regulations-standards#12`](https://github.com/CloudSecurityAlliance-DataSets/dataset-private-laws-regulations-standards/pull/12)).
   - Each migrated `-metadata.json` file sets `license.publicly_redistributable: true` while preserving its underlying `Grouping`, `redistribution`, and `derivatives` source fields and documenting the 2026-11-09 hosting policy in `license.note` and `license.notes`.
3. **Standardize `"type": "version"` on all strategy version child nodes:**
   - Add `"type": "version"` to all `178` strategy version child `match_nodes` across `registry/reference/` that previously omitted `data.type`, ensuring uniform version-node typing across the entire strategy corpus.
4. **Add extracted section/chapter/pillar subpath child `match_nodes` (`#274`):**
   - Add `155` edition-scoped section/chapter/pillar child `match_nodes` (`patterns: ["^(?:...)$"]`, `data.type: "section"`, `data.known_values`, `data.examples`) across `101` files in `registry/reference/` from the extracted `-sections.json` corpus (`66` multi-version strategy sources scoped per edition under their version child nodes with `version_required: true`, plus `42` single-version strategy sources), preserving published section/chapter/pillar casing and spacing (`CHAPTER 1`, `Part 1`, `Pillar 1`, `Pillar (i) Section (1)`, `Shield 1`, etc.), scoping local per-chapter/per-initiative sub-numbering to its parent (`Chapter 4 A`..`Chapter 6 C`, `1.1`..`20.5`), and filtering out TOC dot-leader double-prefixes and PDF page/chart/indicator-table artifacts.
   - Add statutory section child `match_nodes` (`data.type: "section"`, `data.known_values`, `data.examples`) to the 4 extracted Canadian national security statutes in `registry/regulation/ca/parl.json`: `ccspa` (`154` CCSPA sections `Preamble`, `1`–`148` plus `19` enclosing Bill C-8 clauses/schedules), `national-security-act-2017` (`181` sections/schedules), `nsira-act` (`58` sections), and `nsicop-act` (`51` sections/schedules).
   - Per the **Point Once** rule (`2026-11-06` decision), these section child nodes intentionally omit `raw.githubusercontent.com` URLs until each domain is migrated into its permanent `SecID-Data*` repository.

**Rejected alternatives:**
- **Keeping the 46 government/IGO strategy editions in `dataset-private-laws-regulations-standards`** — splits publicly released government national security strategies across two repositories over boilerplate website terms when the documents themselves are freely published for public consumption.
- **Overwriting `Grouping`, `redistribution`, and `derivatives` in `-metadata.json` when setting `publicly_redistributable: true`** — erases provenance about the upstream portal's stated terms (`CC-BY-NC-ND-3.0-IGO`, etc.); keeping the source fields intact while setting `publicly_redistributable: true` and recording the hosting exception note preserves full license metadata fidelity.
- **Adding `raw.githubusercontent.com/CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards/...` URLs to the 107 strategy section nodes now** — violates the `Point Once` rule (`2026-11-06`) and would require touching all 101 registry files a second time when those domains move to `SecID-Data*`.

---

## ADR-017: Public S3 binary mirror with Account-Regional Namespaces and Requester-Pays for public government and open legal standards

**Date:** 2026-11-12
**Status:** Accepted
**Decision method:** Kurt Seifried's direction (2026-11-12), designed with Gemini, which built the bucket and opened #281. Gemini stopped on its usage quota before review; Claude took over as governing agent on 2026-11-13 and completed it. Review: Claude (own review) and OpenAI Codex (`gpt-6-astra`, cross-vendor, fresh context) on 2026-11-13. Codex's findings (1 P1, 5 P2, 2 P3) are dispositioned in PR #281: seven fixed; one (public access to old versions) declined, with the reason recorded below. Owner pinning was then added to meet CINO-Engineering DEC-035. Where goals conflicted, the AI decided by the CINO goal order (safety and privacy first).

**Context:**
1. SecID references public security knowledge, laws, regulations, and standards. Publisher documents often originate as binaries (`.pdf`, `.docx`, `.xlsx`, `.zip`) from official government portals (`govinfo.gov`, `congress.gov`, `parl.ca`, `eur-lex.europa.eu`, `nist.gov`).
2. Per ADR-014 and the 2026-11-06 data architecture directives, Git repositories (`SecID-Data-*`) are restricted to clean, lightweight, line-oriented text (`.json`, `.csv`, `.md`). Storing binary files (especially PDFs hundreds of megabytes in size) in Git inflates `.git/objects/pack` permanently and makes cloning painful for practitioners.
3. However, a reliable, versioned archive of the publisher binaries we extract from is needed for provenance, verification, and re-checking extractions.
4. On 2026-11-12, Kurt directed:
   - *"first lets talk S3 bucket, we mirror 'Safe' stuff like gov docs, public docs, not corp stuff, e.g. no csa, etc. does that make sense? also we can make an S3 bucket, using cino-prod aws cli profile, and lets create it using terraform, and the s3 bucket names needs to be compatible with https://aws.amazon.com/blogs/aws/introducing-account-regional-namespaces-for-amazon-s3-general-purpose-buckets/ and lets make it public, requestor pays from the start, can we do that? it would basically be called SecID-Data plus whatever account name stuff is needed, and the dir structure would be the same as we did in the github repo, remind me what that format is?"*
   - *"yeah, are we sure it's safe to include this, no sensitive data right?"* -> *"go for it"* -> *"yes"*.
5. Earlier the same day, answering where binary originals should live, Kurt wrote: *"an s3 bucket, we can do a private bucket for now, with plans to make it public with requestor pays."* His later *"lets make it public, requestor pays from the start"* (above) supersedes the private-first step.
6. On 2026-11-13, on keeping Terraform state local: *"the terraform state is ok, because this is a permanent s3 bucket"*.

**Decision:**
1. **Public S3 Binary Mirror Bucket:**
   - One permanent S3 bucket managed by Terraform (`infrastructure/terraform/s3-data-mirror/`) under the `cino-prod` AWS profile, with `prevent_destroy` so Terraform cannot delete or replace it.
   - Named per AWS Account Regional Namespaces: `secid-data-{account-id}-{region}-an`, here `secid-data-502869771730-us-west-2-an`. Creating an `-an` bucket requires the `x-amz-bucket-namespace: account-regional` header, which the `hashicorp/aws` provider sends via `bucket_namespace` from 6.37.0 (5.100 rejects the argument). The provider is pinned `~> 6.73` and the lock file is committed.
   - Bucket configuration:
     - `payer = "Requester"` from day zero. S3 rejects anonymous requests to a Requester Pays bucket, so every request is signed and the signing account pays for it and its transfer (normally the reader; for a presigned URL, whoever presigned it). CSA still pays for storage including retained versions, for its own operations, and for the requests AWS bills to the owner (such as denied requests from within CSA's account or organization). External readers cannot run up CSA's transfer bill.
     - Bucket policy allowing `s3:GetObject` and `s3:ListBucket` to `Principal = "*"`, applied only after Requester Pays is in force (`depends_on`). Combined with Requester Pays, that means any AWS account willing to pay, not anonymous users. Turning Requester Pays off alone would make the bucket anonymous-public with CSA paying egress, so the two change together or not at all.
     - A deny on every request without TLS (`aws:SecureTransport = false`).
     - Public access block: `block_public_acls = true`, `ignore_public_acls = true`, `block_public_policy = false`, `restrict_public_buckets = false` (ACLs off, policy-based access on).
     - Object versioning enabled: an overwrite or delete keeps the earlier copy, readable by maintainers only. This is a recoverable archive, not an immutable one.
     - A lifecycle rule that aborts incomplete multipart uploads after 7 days and never expires objects or versions.
     - Object ownership `BucketOwnerEnforced` (ACLs disabled).
   - Follows CINO-Engineering DEC-035 (rule B14, Kurt 2026-11-12) for S3: account regional namespace; owner pinned through the provider's `allowed_account_ids` and `expected_bucket_owner` on every resource that accepts it; never deleted (`prevent_destroy`; a retired bucket becomes an emptied tombstone).
   - Terraform state stays local to the maintainer's machine (gitignored), per Kurt (context 6). The module README documents rebuilding state with `terraform import` if the file is lost.
2. **Scope: public government publications and open standards only.**
   - US public laws, NIST SPs, White House directives, EUR-Lex texts, Canadian bills and the like.
   - Narrower than the Tier 1 + Tier 2 rule for the public text repositories: no CSA documents, and no corporate or vendor material even when it is on the open web. No Tier 3 (free login) and no Tier 4 paid standards (ISO/IEC).
3. **Object layout (ADR-014):**
   - `data/<type>/<tld>/<domain>/<name>[/<version>]/<publisher-filename>`, derived mechanically from the SecID, e.g. `secid:control/nist.gov/800-53@rev5` -> `data/control/gov/nist/800-53/rev5/NIST.SP.800-53r5.pdf`.
   - The `<version>` level appears only when the SecID has a version (ADR-014 does not cover unversioned sources). Unversioned statutes sit directly under `<name>/`, e.g. `data/regulation/gov/govinfo/hipaa/`, and S3 object versioning keeps earlier fetches for maintainers. The file keeps the publisher's original name, for provenance.

**Rejected alternatives:**
- **Storing PDFs in GitHub repositories** — Bloats `.git/objects/pack` permanently; Git is unsuitable for multi-gigabyte binary archives.
- **Hosting binaries on standard public S3 with CSA-paid egress** — Risks unpredictable and potentially massive AWS egress billing spikes if automated web scrapers or AI agents download large PDF corpora. Requester Pays moves external download costs to the reader; CSA keeps the bounded costs listed above.
- **Public read access to old versions (`s3:GetObjectVersion`, `s3:ListBucketVersions`)** — Suggested by the Codex review for auditors who want an earlier copy. Declined on safety grounds (CINO goal order: safety and privacy before correctness). If something is uploaded by mistake, deleting it must take it out of public view; with public version access it would stay readable by `versionId` until someone noticed and purged every version. Maintainers can still retrieve history.
- **S3 Object Lock for immutability** — Would stop maintainers from purging a mistaken upload, the same safety problem; and nothing yet requires legal-grade retention.
- **Global S3 bucket namespace (`secid-data`)** — Subject to global naming collisions and lacks account-regional namespace security/governance integration.
- **Remote Terraform state backend (S3 + lock)** — Raised in review on 2026-11-13; Kurt kept local state because the bucket is permanent and rarely changed (context 6). Losing the state file is recoverable by `terraform import`.
- **A `<version>` folder for every object, using the retrieval date for unversioned sources** — Would break mechanical derivation from the SecID (the path would hold something the identifier does not), and S3 object versioning already keeps the history.


---
