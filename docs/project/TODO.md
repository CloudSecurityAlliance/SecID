# TODO

Tracking exploratory work and rough notes. **Committed work lives in GitHub issues**, not here — see [open issues](https://github.com/CloudSecurityAlliance/SecID/issues). Updated 2026-05-21 (second sweep).

This file is for:
- Research/exploration not yet ready for an issue
- Items intentionally deferred until evidence appears
- Notes captured in passing during sessions

Anything with a clear definition-of-done belongs in an issue.

## Recently shipped (May 2026)

This block is a quick read-out of what landed in the most recent burst of work. For the canonical history, see git log + the GitHub issues/PRs.

- **Subtype framework** — [#46](https://github.com/CloudSecurityAlliance/SecID/pull/46) (TYPES-AND-SUBTYPES.md, 43 methodology entries tagged), [#47](https://github.com/CloudSecurityAlliance/SecID/pull/47) (README), [#49](https://github.com/CloudSecurityAlliance/SecID/pull/49) (CI validator)
- **GLOSSARY proposal accepted** — [#46](https://github.com/CloudSecurityAlliance/SecID/pull/46) — `subtype: ["glossary"]` + dataset-repo pointer (Phase 1). Phase 2 content population is open as [#62](https://github.com/CloudSecurityAlliance/SecID/issues/62)
- **CLAUDE.md visibility improvements** — [#44](https://github.com/CloudSecurityAlliance/SecID/pull/44) (plugins/, working-data/, schemas/ surfaced)
- **Cross-source bare-name search fix** — [SecID-Service #9](https://github.com/CloudSecurityAlliance/SecID-Service/pull/9) — `?secid=cwe`/`capec` now finds source-level matches
- **Subtype filter UI** — [SecID-Service #9](https://github.com/CloudSecurityAlliance/SecID-Service/pull/9) — `?subtype=X` filter + clickable homepage chips
- **Auto-deploy on push to main** — [SecID-Service #9](https://github.com/CloudSecurityAlliance/SecID-Service/pull/9) — no more manual `gh workflow run` needed
- **type-registry single source of truth** — [SecID-Service #8](https://github.com/CloudSecurityAlliance/SecID-Service/pull/8) — `/api/v1/types` endpoint, MCP describe + homepage + Resolver all import from one constant
- **DECISIONS.md ADR log** — [#69](https://github.com/CloudSecurityAlliance/SecID/pull/69) — 8 seed ADRs mirroring SecID-Service convention
- **CVSS reference versioned children** — [#77](https://github.com/CloudSecurityAlliance/SecID/pull/77) — `secid:reference/first.org/cvss@4.0` etc. now resolve to per-version spec docs
- **7 standards added as reference entries** — [#78](https://github.com/CloudSecurityAlliance/SecID/pull/78) — SARIF, CycloneDX, SPDX, VEX, OpenVEX, OSCAL, ROLIE (closed [#72](https://github.com/CloudSecurityAlliance/SecID/issues/72))

## Open follow-ups discovered during recent work

These have GitHub issues — see those for full context.

- **Overly-broad child patterns pollute search results** — [#52](https://github.com/CloudSecurityAlliance/SecID/issues/52). Patterns like `^.+$` in `control/ibm.com` create ~15 false-positives per common short query. Two strands: tighten the patterns (here) or de-weight at search time (SecID-Service).
- **Subtype tagging coverage audit** — [#53](https://github.com/CloudSecurityAlliance/SecID/issues/53). New methodology entries landed without tags ([#50](https://github.com/CloudSecurityAlliance/SecID/pull/50)); CI catches wrong values but not missing ones. Inventory pass needed.
- **Branch protection + CI/CD-automated registry merges** — *deferred from the 2026-06 security audit.* The audit added blocking CI gates on the registry contribution path (URL scheme/host gate `validate-urls.py`, and the ReDoS lint + publish-gate landing next), but **gates only matter once they're required**. To do, in order: (1) enable branch protection on `main` with the `validate` job (schema + URL gate + ReDoS lint) and the publish-gate as **required status checks**, and require a reviewer on `registry/**`, `schemas/**`, `scripts/`, `.github/workflows/`; (2) *only then* move to CI/CD-automated PR merges — the automated gates must be enforced **before** the human merge gate is removed (see THREAT_MODEL-SYSTEM T2 in the audit). Also: verify `https://www.planalto.gov.br` in a browser and drop it from `scripts/http-exception-allowlist.txt` if https works.

## Migrated to issues

Items previously tracked here that now have their own issues:

| Item | Issue |
|---|---|
| Entity-vs-Publication Cleanup | [#54](https://github.com/CloudSecurityAlliance/SecID/issues/54) |
| ISF SOGP / ENX ISA control gaps | [#55](https://github.com/CloudSecurityAlliance/SecID/issues/55) |
| Disclosure safe_harbor research | [#56](https://github.com/CloudSecurityAlliance/SecID/issues/56) |
| Disclosure bug_bounty research | [#57](https://github.com/CloudSecurityAlliance/SecID/issues/57) |
| Prowler checks as control entries | [#58](https://github.com/CloudSecurityAlliance/SecID/issues/58) |
| DISA STIGs as control entries | [#59](https://github.com/CloudSecurityAlliance/SecID/issues/59) |
| TIMESTAMP-FIELDS proposal triage | [#60](https://github.com/CloudSecurityAlliance/SecID/issues/60) |
| ASSERTION-CONTENT-TYPES revision | [#61](https://github.com/CloudSecurityAlliance/SecID/issues/61) |
| GLOSSARY Phase 2 dataset entries | [#62](https://github.com/CloudSecurityAlliance/SecID/issues/62) |
| CIS Benchmarks license check | [#63](https://github.com/CloudSecurityAlliance/SecID/issues/63) |
| V2 Data Repositories | [#64](https://github.com/CloudSecurityAlliance/SecID/issues/64) |
| Training course content | [#65](https://github.com/CloudSecurityAlliance/SecID/issues/65) |
| SecID-Service format metadata | [SecID-Service #10](https://github.com/CloudSecurityAlliance/SecID-Service/issues/10) |
| SecID-Server-API format metadata | [SecID-Server-API #3](https://github.com/CloudSecurityAlliance/SecID-Server-API/issues/3) |
| Sharper methodology-vs-reference test (ADR-009) | [#73](https://github.com/CloudSecurityAlliance/SecID/issues/73) |
| CCM/AICM multi-type modeling | [#71](https://github.com/CloudSecurityAlliance/SecID/issues/71) |
| Relationship Layer Design | [#75](https://github.com/CloudSecurityAlliance/SecID/issues/75) |
| Automate CNA listing refresh | [#76](https://github.com/CloudSecurityAlliance/SecID/issues/76) |

## Active — research and exploration

A handful of standards-coverage candidates remain where placement decisions haven't been made. Each is a small research task before promotion to an issue.

### Standards Registry Coverage — remaining candidates

The 9 standards from the prior list landed: 3 already existed (CSAF, STIX, TAXII), 1 had ambiguous placement and gained both a reference and methodology entry (CVSS, [#77](https://github.com/CloudSecurityAlliance/SecID/pull/77)), and 7 shipped as reference-only ([#78](https://github.com/CloudSecurityAlliance/SecID/pull/78)). One more standard remains in the original list as a research item:

- **OpenDXL** → likely `reference` (data-exchange spec from McAfee/Trellix). Confirm whether the project is still maintained and whether it has any methodology-shaped content beyond the format.

Other standards worth eventual placement decisions (no committed work; promote to issue when someone wants to land them):

- ASVS (OWASP Application Security Verification Standard) → likely `control`
- MASVS (Mobile Application Security Verification Standard) → likely `control`
- WSTG (Web Security Testing Guide) → likely `methodology` (security-testing subtype)
- SSDF (NIST 800-218) — already in `methodology/gov/nist.json` as 800-218? worth confirming
- VERIS already covered as `methodology` (incident-management subtype)

**Working rule** (now codified as ADR-009 candidate in [#73](https://github.com/CloudSecurityAlliance/SecID/issues/73)): a methodology provides standalone judgement guidance citable independent of any output format. A reference specifies how data should be formatted, with judgement-involved-incidental.

### AI-reported link rot and dead namespaces

A namespace that resolves to a dead URL is worse than one that does not exist: it returns an authoritative-looking
answer that is wrong. There are 2,130 namespaces of URLs, and programs end, organisations get acquired, and portals
move. Today the only systematic coverage is `working-data/cna/known-broken.json`, which handles CNA disclosure data
only — roughly a quarter of the registry, and nothing else is monitored.

Two halves:

1. **Track and test.** Periodic reachability checks across registry URLs, with results recorded rather than
   auto-applied — the same posture `audit-known-broken.py` already takes (report, do not reprobe-and-rewrite).
   Generalise the known-broken overlay beyond CNA data.
2. **Let AI report it.** An agent that resolves a SecID and finds a dead link, a moved portal, or a program that has
   plainly ended should be able to say so — filing an issue, or submitting through the existing `submit_feedback`
   MCP tool (which already carries a `correction` category and lands in `secid_FEEDBACK`).

The second half is the higher-yield one. Agents resolve SecIDs constantly and hit link rot in the course of real
work; they are a far denser sampling of the registry than any crawler we would run, and the report arrives with the
context of what the agent was actually trying to do. Feedback intake is MCP-only by design, so this fits the existing
AI-to-AI loop rather than needing a new channel.

Open: whether dead-link reports become issues, feedback entries, or both; what evidence an agent must supply for a
report to be actionable; and how a confirmed-dead namespace is represented — the `_broken: true` annotation pattern
from the CNA overlay is the obvious candidate.

### Search tiering — anonymous, gated, and local

Direction: search becomes **tiered** rather than removed.

| Tier | Gets |
|---|---|
| **Anonymous / hosted** | Direct resolution only, plus a downloadable master index (`type/namespace-domain/`) |
| **Authenticated / gated** | Better hosted search — likely CSA membership or token-scoped |
| **Local** | Whatever you want: SQLite FTS, vector search, custom enrichment, over your own synced copy |

This bounds hosted cost, gives membership a concrete benefit, and keeps the best experience available to anyone
willing to run their own resolver.

**Reuse CSA's existing audience model.** The CSA MCP server already implements exactly this shape: `anonymous` as a
recognised tier alongside authenticated tiers 1–4 and revoked tier 5, with capability gating by working-group /
chapter / staff membership, and a documented convention (ADR-027 §9) for how a gated capability announces itself —
structured errors carrying required-credential and how-to-resolve fields. SecID should adopt the same tiers and the
same error convention rather than inventing a parallel scheme, so a client that understands one CSA service
understands the other.

**The gate is on convenience, not access.** Because the registry and data are CC0 and syncable, anyone can obtain the
full corpus and run better search than the hosted service offers. Gating hosted search therefore cannot function as
lock-in even in principle — it is cost management plus a membership benefit. Worth stating openly, because it is what
keeps the tiering compatible with SecID's neutrality and openness claims.

**Consistent with principle 3, not a stretch of it.** *Helpful over correct* requires that a caller is never left
stuck — not that every query is served from CSA's infrastructure. A gated response that names the credential needed
and how to obtain it (ADR-027 §9) leaves the caller with a path, and so does "download the index and run it
yourself," because the corpus is CC0 and syncable. The capability is relocated, not withheld.

**An agent with sufficient privilege can stand up its own instance**, so the local fallback is immediate for agents
too, not only for humans — provided we make it trivial. That is a packaging problem, not a principles problem: see
*Distribution formats for the resolver* below. The gated response should carry the runnable instruction, not just
the suggestion.

**Precomputed facets remain worth doing** — common search dimensions like country, type, subtype and jurisdiction
served free means the queries agents make most often never reach the gate at all. Choose them from observed
behaviour; the `secid_FEEDBACK` miss log is the obvious input.

Two documented pieces of reasoning still need rewriting, because they assume unscoped cross-source search is
universally available:

- **The pattern-breadth gate's justification.** CLAUDE.md argues a catch-all is dangerous because *"cross-source search
  walks every namespace, so a single catch-all degrades every query in the system."* Once search is tiered, that
  argument holds only for callers who have search — but **the gate is still needed**, for a narrower reason: a
  namespace patterned `^.+$` will affirm *any* identifier presented to it directly, so
  `secid:control/ibm.com/anything` resolves to a fabricated answer. Blast radius shrinks; the defect does not.
- **`open_pattern`.** The JSON Schema defines it as "resolvers exclude such nodes from unscoped cross-source search."
  Its natural extended meaning is **exclusion from the master index** as well — an unbounded space cannot be
  enumerated, so it cannot be indexed.

**Open questions for the local tier.** Vector search needs embeddings, and embeddings are model-dependent derived
data. Does CSA generate and ship them (large, and pinned to whatever model produced them — the reproducibility
question from ADR-012 again), or does each local resolver generate its own (compute at the consumer's end, but no
model lock-in)? And is the shipped master index simply a SQLite file, which would make it a single artifact servable
from R2 and searchable with FTS5 out of the box?

Also revisit: [API-RESPONSE-FORMAT.md](../reference/API-RESPONSE-FORMAT.md) documents cross-source search as a
response mode available to all callers.

### Distribution formats for the resolver

Local-first only works if standing up a local instance is trivial. Every tier of the search design assumes a consumer
— human or agent — can go from "I need better search" to a running resolver without a project. That makes packaging
load-bearing rather than a convenience, and it means a gated response should carry a **runnable instruction**, not a
suggestion.

Formats to provide, roughly by who needs them:

| Format | For |
|---|---|
| **Docker image**, multi-arch (amd64 + arm64) | The universal "just run it" answer; what an agent reaches for first |
| **Local MCP server** — stdio, plus an MCPB bundle | The AI-first case. If the primary consumer is agents, a locally runnable MCP server *is* the distribution format |
| **Terraform module for Cloudflare** | Replicates CSA's own production topology; the reference deployment |
| **Single static binary** | No runtime dependencies; simplest thing to fetch and execute in a constrained environment |
| **Helm chart** | Enterprises already running Kubernetes |
| **docker-compose** | Resolver plus data volume plus index, as one unit |
| Terraform / Pulumi for AWS, Azure, GCP | Organizations standardised elsewhere |
| Homebrew, and OS packages | A CLI, for humans |

**Ship the supply-chain metadata we catalogue.** SecID registers Sigstore, SLSA, in-toto, CycloneDX and SPDX in its
own corpus. Distributing unsigned containers with no SBOM would be a poor look, and fixing it is cheap: sign images
with cosign, publish an SBOM per artifact, and reference our own releases by SecID. Dogfooding here is both
credibility and a working example of the corpus in use.

**Air-gapped installation deserves first-class treatment.** SecID's regulation and control coverage implies a
government, defence and critical-infrastructure audience, and those consumers frequently cannot reach the internet
from the environment where they need answers. A single tarball — image, data, index, checksums — that installs with
no network turns local-first from a cost measure into a genuine capability nobody else offers. It is also the extreme
case that validates the whole design: if the corpus cannot be handed over on a disk, it is not really portable.

**Open questions.** Which artifacts carry the data versus fetch it on first run (an image with the corpus baked in is
large but works offline immediately). Whether the master index ships as SQLite inside the image or alongside it.
Whether image builds should be reproducible in the ADR-012 sense — likely yes, for the same continuity reason. And
what the smallest useful deployment is, since "run the whole thing" and "run enough to resolve my jurisdiction"
are different products.

### Vocabulary survey — what do the schemas and ontologies actually enumerate?

STIX defines 18 domain objects and 2 relationship objects. Mapping them against SecID's types was
unexpectedly productive: it confirmed that ATT&CK groups/software/mitigations are already reachable
(`ttp/mitre.org/attack#G0007`, `#S0154`, `#M1036`), showed that STIX's two *relationship* objects land
exactly on SecID's Relationship and Data layers, and left only three objects with no home —
**Indicator** (a detection pattern), **Malware Analysis**, and **Opinion** (both recorded findings).

Do that survey properly, across every vocabulary of comparable weight. Two reasons it is worth the effort:

1. **It is the empirical basis for the v2 type decisions.** The "when to split" gate's fourth criterion is
   *volume justifies it*. Counting how many independent vocabularies define an object kind SecID cannot
   reach is far better evidence than intuition — and STIX already found the executable and evidential gaps
   from a direction we had reached independently.
2. **These vocabularies should themselves be in SecID.** Each object-type name is an enumerable, closed,
   citable set: `secid:reference/oasis-open.org/stix@2.1#attack-pattern`. `oasis-open.org` registers `stix`
   today with no children. Adding them is purely additive and needs no new vocabulary.

**Candidates**, grouped roughly. Not exhaustive — extending the list is part of the task:

| Domain | Vocabularies |
|---|---|
| Threat intel | STIX 2.1 (SDO/SRO/SCO), MISP object templates + taxonomies + galaxies, MAEC, OpenCTI data model, UCO/CASE, IODEF (RFC 7970), VERIS, CACAO, OpenC2 |
| Detection & telemetry | OCSF event classes, Elastic Common Schema, OSSEM, Sigma logsource taxonomy, MITRE CAR, D3FEND |
| Vulnerability | CVE JSON 5.x, OSV schema, CSAF + VEX profiles, OpenVEX, SARIF, CVSS/EPSS/SSVC, KEV schema, CWE view & category structure |
| Controls & assessment | OSCAL model set (catalog, profile, SSP, assessment-plan, assessment-results, POA&M), SCAP suite (XCCDF, OVAL, CCE, OCIL, ARF), CCM/AICM structure |
| Supply chain | SPDX elements, CycloneDX component types, in-toto attestation predicates, SLSA, OmniBOR/gitoid |
| Identity & crypto | PKIX/X.509 OID arcs, WebAuthn, SCIM, OpenID/OAuth registries, IANA protocol registries |
| AI | ATLAS, NIST AI RMF, Model Card / System Card schemas, MLCommons taxonomy, OWASP LLM Top 10 |

**Per vocabulary, capture:**

- The object/class/element types it defines, and whether that set is closed and enumerable
- What identifier each carries (UUID, numeric, structured string, name) and whether it is stable across producers
- Which SecID type each maps to — and where the publisher's *packaging* overrides the object's ontology
  (ATT&CK is the precedent: a group is really an organization, but it lives under `ttp` because ATT&CK
  ships it inside a TTP framework)
- What has no home, which is the actual finding

**Output:** a coverage map plus registry entries adding object-type subpaths to each vocabulary already
registered. Expect the map to settle the open type questions — the executable type (Sigma/Semgrep/Nuclei
/Atomic Red Team, and STIX Indicator) and the evidential one (certifications, malware analyses, opinions).

**Watch for:** vocabularies whose object types are deliberately *not* SecID material — STIX Observed Data,
Note, and Grouping are telemetry, annotation, and data-structuring rather than knowledge. Cataloguing what
is out of scope is as useful as cataloguing what is in.

### v2 — data lifecycle and publishing (open question)

v2 adds the data itself, not just pointers to it. The repo split is settled:
**the data repo holds all the data, including its acquisition metadata; the SecID
registry keeps holding exactly what it holds today** and refers out to the data
repo. Nothing new goes into a registry entry to support this.

What is deliberately *not* settled is the lifecycle: how data is versioned,
refreshed, superseded, archived, and published once it lives in the data repo.
Related threads, all unresolved:

- **Volatility is multi-dimensional.** Additions, updates, and removals happen at
  different rates for the same source. GDPR is near-frozen; CVE grows constantly.
  AICM 1.1.0 is the cautionary case — moderate *content* churn but high
  *identifier* churn (54 IDs designate a different control than in 1.0.3), so
  ID stability and content stability are separate axes.
- **Not every source needs stored data.** Where the publisher already hosts
  version-tagged authoritative data (CVE, ATT&CK STIX), pointing upstream is a
  complete answer, not a gap. The dataset repo already models this as
  `desired_end_state.reason: upstream-only`.
- **Reproducibility vs. AI extraction.** The goal is that a third party can run
  our extractor and get the same structured output. Deterministic pipelines can
  promise that; LLM extractors cannot. Unresolved whether AI is used to *build*
  deterministic extractors (reproducible) or to *do* the extraction (attestable
  but not reproducible).
- **Notes beyond SecID's scope.** Access constraints (geo-restricted sites needing
  an in-country VPN, SPAs needing a real browser) and semantic warnings (the AICM
  ID-reuse trap) are useful but sit outside "labeling and finding." Where they
  live and how they surface is open.
- **Caching for self-hosted resolvers.** Local servers need a cache layer for
  outage tolerance and speed; TTL policy likely derives from the volatility
  profile above.

Answer empirically — build v2 and see what the data demands, rather than
specifying the lifecycle up front.

## Deferred

Items intentionally not scheduled. Promote to an issue if/when a forcing function appears.

- **Resolver and Regex Test Fixture Strategy** — fixture extraction script, negative test fixtures, regex compile checks, overlap detection, deterministic ordering tests. Deferred until CI gates need this level of rigor.
- **Resolution Instructions for Non-Deterministic Systems** — search-based resolution for systems without stable URLs.
- **MCP Interaction Logging** — log every MCP interaction to KV with TTL for usage analytics.
- **Capability Freshness Monitoring** — monitor cloud provider release notes for new security features.
- **llms.txt for AI Discoverability** — implement llms.txt standard on the website.
- **Automated processing of the feedback backlog** — `secid_FEEDBACK` KV captures namespace-level misses + AI-submitted feedback (`miss:<type>/<namespace>` aggregates, plus MCP-submitted entries). Today it's read-only via raw `wrangler kv` (acceptable for now). Longer term: scheduled jobs read the backlog and process it with AI — rank demand, auto-research the most-requested missing sources, and draft registry entries / PRs for human review. Feedback intake is **MCP-only by design** (AI/MCP clients, not web forms), so the backlog is an AI-to-AI loop end to end.

## Done (v1.0)

See git history and merged PRs for the full list. Selected highlights:

- SecID-Server-API repo scaffolded (self-hosted Python/TypeScript resolver)
- Participation Model proposal ([docs/proposals/PARTICIPATION-MODEL.md](../proposals/PARTICIPATION-MODEL.md))
- Disclosure structured CNA fields populated across 486 entries ([docs/proposals/DISCLOSURE-TYPE-FIELDS.md](../proposals/DISCLOSURE-TYPE-FIELDS.md))
- JSON Schema for registry validation (`schemas/registry-namespace.schema.json`)
- OpenAPI spec for REST API (`schemas/openapi.yaml`)
- Capability type (9th → 10th type), 54 namespaces, 428 capabilities
- Disclosure type with 486 namespaces / 502 CVE Program partners
- URL normalization (data.source → urls[] arrays)
- Four slide decks published to `slides/` with CSA Marp theme
- MCP server enhancements (CNA workflow, feedback resource, capability descriptions)
- Standalone SecID Claude Code plugin (`/plugin install secid@csa-plugins-official`)
- CI/CD for slide generation (pre-commit hook auto-rebuilds HTML)
