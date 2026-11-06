# SecID Types and Subtypes

SecID has **10 official types** at the top level — the values that appear as the `type` field of a registry entry and immediately after `secid:` in an identifier string. They are frozen at v1.0; adding a new one is a multi-repo coordination event.

Within those 10 types, **subtypes** are named sub-classifications that live in a match_node's `data:` block. They let us model "kind-of-a-thing-inside-a-type" (e.g., a glossary is a kind of `reference`; an incident report is a kind of `advisory`) without inflating the official type list. Subtypes are a registry-data convention, not a spec-level change.

> **Vocabulary note:** "Subtype" is the canonical term for this concept. Earlier drafts and the 2026-05-17 revision of [GLOSSARY-DEFINITION-COMPARISON](../proposals/GLOSSARY-DEFINITION-COMPARISON.md) used `kind`; the 2026-05-20 acceptance renamed it to `subtype` for consistency. Don't be confused if you find `kind` in older proposal text — it's the same concept.

## The 10 official types

For full definitions, see [registry/`<type>`.md](../../registry/) (e.g., `registry/advisory.md`, `registry/control.md`).

| Type | Identifies |
|------|------------|
| `advisory` | Publications about vulnerabilities (CVE, GHSA, vendor advisories, incident reports) |
| `weakness` | Abstract flaw patterns (CWE, OWASP Top 10) |
| `ttp` | Adversary techniques (ATT&CK, ATLAS, CAPEC) |
| `control` | Security requirements (NIST CSF, ISO 27001, benchmarks) |
| `capability` | Product security features with configuration, audit, and remediation (AWS S3 encryption, CloudTrail) |
| `methodology` | Formal processes for producing security analysis, scores, mappings, decisions (CVSS, SSVC, IR 8477, STRIDE) |
| `disclosure` | Vulnerability disclosure programs, policies, reporting channels |
| `regulation` | Laws and legal requirements (GDPR, HIPAA) |
| `entity` | Organizations, products, services |
| `reference` | Documents, research, identifier systems (arXiv, DOI, ISBN, RFCs) |

Adding a new type requires coordinated changes across SecID, SecID-Service, SecID-Server-API, and SecID-Client-SDK (the type list is hardcoded in each). See [AGENTS.md](../../AGENTS.md) "WARNING: Adding a new type" for the full impact list, and *When to add a subtype vs. split into a new type* below for the decision gate.

## What a subtype is, mechanically

A subtype is an **array of strings** in the `subtype:` field of a match_node's `data:` block. It's normal registry data — no schema change needed (`data:` is `additionalProperties: true` in [registry-namespace.schema.json](../../schemas/registry-namespace.schema.json)).

`subtype` is an array because a single entry can legitimately fit more than one subtype at once — a glossary that's also a controlled vocabulary, a methodology that does both mapping and scoring, a regulation that contains both legal scaffolding and technical control content. Entries with a single subtype use a one-element array (`["glossary"]`); empty arrays and absent fields both mean "no subtype tag." Consumers filter on array membership.

Source-level example (`registry/reference/gov/nist.json`):

```json
{
  "namespace": "csrc.nist.gov",
  "type": "reference",
  "match_nodes": [
    {
      "patterns": ["(?i)^csrc-glossary$"],
      "description": "NIST CSRC Glossary",
      "data": {
        "subtype": ["glossary"],
        "data_repo": "secid:reference/cloudsecurityalliance.org/secid-glossaries#csrc-nist",
        "...": "..."
      }
    }
  ]
}
```

Consumers can filter for `"glossary" in subtype` to find all glossary-shaped reference entries across the registry, regardless of source. That's the cross-source-discovery affordance.

Subtypes are placed at the **source-level** match_node (the top-level entries in `match_nodes[]`), not on individual children. The subtype describes the whole namespace entry's character. Don't confuse subtypes with the existing child-level `data.type:` fields used for internal node typing — those describe what *kind of item* a specific child matches within a source's internal taxonomy (e.g., an ATT&CK child match_node with `type: "tactic"` vs. `type: "technique"`). Different level, different purpose.

### Exhaustive-partition vs. specialization subtypes

SecID's declared subtypes follow two distinct structural models, enforced differently by `scripts/validate-subtypes.py` ([#53](https://github.com/CloudSecurityAlliance/SecID/issues/53)):

1. **Exhaustive-partition subtypes (`methodology`):** Every source-level `match_node` in `registry/methodology/` belongs to at least one of the 11 declared methodology categories (`mapping`, `scoring`, `risk-management`, `vulnerability-management`, `threat-modeling`, `security-testing`, `digital-forensics`, `incident-management`, `supply-chain`, `audit-certification`, `classification`). `scripts/validate-subtypes.py` includes `"methodology"` in `ENFORCED_COMPLETE_TYPES`, so CI fails if any new `methodology` source-level `match_node` omits `data.subtype`.
2. **Specialization (carve-out) subtypes (`advisory`, `disclosure`, `entity`, `reference`):** The declared subtypes in these four types identify specialized subsets that differ in character from the type's default baseline items:
   - `advisory`: `"incident"` carves out harm/incident reports (`AIID`, `AIAAIC`, `FDA MAUDE`, `NHTSA SGO`, `CA DMV AV reports`) from standard vulnerability advisories (CVE, GHSA, vendor security bulletins), which remain untagged.
   - `disclosure`: `"coordinator"` and `"psirt"` carve out neutral CVD coordinators and dedicated vendor PSIRTs from standard CNA-only disclosure records (whose CVE roles live in structured `data.cve.role` per [DISCLOSURE-TYPE-FIELDS](../proposals/DISCLOSURE-TYPE-FIELDS.md)).
   - `entity`: `"consortium"` carves out multi-organization alliances/foundations from standard single-company or government-agency entities.
   - `reference`: `"glossary"` (166 nodes) and `"strategy"` (240 nodes) carve out terminology glossaries and national/organizational strategy documents from general reference publications, RFCs, academic preprints, identifier systems, and data schemas, which remain untagged until additional document-kind subtypes are promoted.

Because baseline nodes in specialization-subtype types intentionally omit `data.subtype`, `scripts/validate-subtypes.py` validates that every present `data.subtype` value is declared in `SecID-Service/src/type-registry.ts` and appears only at the source level, without requiring 100% of `advisory`, `disclosure`, `entity`, or `reference` nodes to carry a subtype.

## Named subtypes in use today

Five types currently carry named `subtype:` tags on entries: `reference` (for glossaries and strategies), `methodology` (the full 11-category set tagged on all ~40 entries), `advisory` (for incident reports), `entity` (for multi-organization consortia), and `disclosure` (for coordinators and PSIRTs). Other named subtypes are either anticipated (assertion-content revision direction), pattern-match candidates (regulation, and the entity organization/product/service split), or implicit overloads that predate the convention.

### `reference`

| `subtype:` value | What it means | Where to find it | Defined by |
|------------------|---------------|------------------|------------|
| `"glossary"` | A glossary document with addressable term-level subpaths. Entry is identity-only; term data lives in a separate dataset repo (Phase 1) and will be copied into the registry for direct API serving in Phase 2. | `registry/reference/<path>.json` entries carrying `subtype: ["glossary"]` | [GLOSSARY-DEFINITION-COMPARISON](../proposals/GLOSSARY-DEFINITION-COMPARISON.md) (Accepted 2026-05-20) |
| `"strategy"` | Strategy documents, multi-year action and implementation plans, and strategic reviews or evaluations — including national security and cybersecurity strategies, agency strategic plans, and corporate or organizational security strategies. | `registry/reference/<path>.json` source-level match_nodes carrying `subtype: ["strategy"]` | Declared in SecID-Service `type-registry.ts` ([SecID-Service#58](https://github.com/CloudSecurityAlliance/SecID-Service/pull/58)) and [ADR-016](../../DECISIONS.md#adr-016-registry-conventions-for-multi-edition-national-strategies-215-and-proposedenacted-legislation-208) |

### `advisory`

| `subtype:` value | What it means | Where to find it | Defined by |
|------------------|---------------|------------------|------------|
| `"incident"` | Publication documenting that an AI, automated, or computing system caused harm or behaved badly. Distinct from a vulnerability advisory in *what happened* (an incident has occurred, vs. a vulnerability was disclosed) but identical in resolution shape (publication with ID + URL). Sources include AIID, AIAAIC, NHTSA SGO, CA DMV autonomous-vehicle reports. | `registry/advisory/<path>.json` source-level match_nodes carrying `subtype: ["incident"]` | Declared in SecID-Service `type-registry.ts` 2026-05-27 (promoted from "Implicit overloads") |

Tag at the source-level match_node, not the file level — many advisory files contain a mix (e.g., `nhtsa.json` has SGO incident reports alongside recall/defect-investigation match_nodes that are NOT incidents and stay untagged). Per-node granularity lets one namespace carry both incident and non-incident sources.

### `methodology`

The methodology type's match_nodes are tagged with one of eleven categories. Ten come from [METHODOLOGY-ARCHITECTURE.md](../proposals/METHODOLOGY-ARCHITECTURE.md)'s category table; an eleventh (`"classification"`) was added on 2026-05-20 to accommodate TLP (information-sharing classification), which didn't fit any of the original ten cleanly.

| `subtype:` value | What it means | Example entries |
|------------------|---------------|-----------------|
| `"mapping"` | Methodologies that produce a mapping/crosswalk from one framework to another | NIST IR 8477, CISA ATT&CK mapping, CSA CCM mapping methodology, CTID framework/platform mapping |
| `"scoring"` | Methodologies that produce a score, prioritization decision, or rating | CVSS, EPSS, SSVC, BitSight rating, SecurityScorecard, UpGuard, CyberCube |
| `"risk-management"` | Methodologies for identifying, analyzing, evaluating, and treating risk | NIST RMF (800-37), NIST 800-30, ISO 27005, ISO 31000, Open FAIR |
| `"vulnerability-management"` | Methodologies for receiving, handling, and disclosing vulnerabilities | ISO 29147, ISO 30111 |
| `"threat-modeling"` | Methodologies for systematically identifying threats against a system | STRIDE, PASTA, VAST |
| `"security-testing"` | Methodologies for conducting security tests and assessments | NIST 800-115, PTES, OWASP Testing Guide, OSSTMM |
| `"digital-forensics"` | Methodologies for digital evidence collection, preservation, analysis | ISO 27037, 27041, 27042, 27043, RFC 3227 |
| `"incident-management"` | Methodologies for detecting, handling, and analyzing security incidents | ISO 27035, VERIS, NIST 800-61 |
| `"supply-chain"` | Methodologies for software supply chain security | NIST 800-161, SLSA |
| `"audit-certification"` | Methodologies for conformity assessment and certification | ISO 27006, 27007, 17021, Common Criteria CEM |
| `"classification"` | Methodologies for classifying/labeling information for handling | TLP (Traffic Light Protocol) |

Multi-subtype methodologies are permitted but rare in practice. The tagging sweep on 2026-05-20 assigned single-element arrays to all 43 match_nodes; future entries should add a second value only when the methodology genuinely produces more than one output kind (e.g., a methodology that's both a mapping and a scoring framework).

Note: METHODOLOGY-ARCHITECTURE.md's table placed NIST 800-61 under "Vulnerability Management." The actual document is the NIST Incident Handling Guide; the tagged data corrects this to `"incident-management"`.

### `entity`

| `subtype:` value | What it means | Where to find it | Defined by |
|------------------|---------------|------------------|------------|
| `"consortium"` | A multi-organization collaborative body — consortium, coalition, alliance, or foundation formed by multiple member organizations (CoSAI, Akrites, MOSAIC, ORCA, OpenSSF). Refines the organization form; composes with a future organization/product/service axis. | `registry/entity/<path>.json` source-level match_nodes carrying `subtype: ["consortium"]` | [CONSORTIUM-AND-COORDINATOR-SUBTYPES](../proposals/CONSORTIUM-AND-COORDINATOR-SUBTYPES.md) |

### `disclosure`

| `subtype:` value | What it means | Where to find it | Defined by |
|------------------|---------------|------------------|------------|
| `"coordinator"` | A neutral coordinated-vulnerability-disclosure body that routes reports between finders and affected vendors — CERT/CC, national CSIRTs, shared SIRTs (FIRST, JPCERT/CC, Akrites). Composes with the structured `cve.role` field. | `registry/disclosure/<path>.json` source-level match_nodes carrying `subtype: ["coordinator"]` | [CONSORTIUM-AND-COORDINATOR-SUBTYPES](../proposals/CONSORTIUM-AND-COORDINATOR-SUBTYPES.md) |
| `"psirt"` | A vendor's own Product Security Incident Response Team program (its own products) — distinct from a neutral coordinator and from a CNA. | `registry/disclosure/<path>.json` source-level match_nodes carrying `subtype: ["psirt"]` | [CONSORTIUM-AND-COORDINATOR-SUBTYPES](../proposals/CONSORTIUM-AND-COORDINATOR-SUBTYPES.md) |

**Subtypes vs. structured fields.** CNA status (`cve.role`), bug bounty programs (`bug_bounty[]`), and security.txt (`security_txt`) were once floated as disclosure subtypes but are instead carried by explicit first-class fields ([DISCLOSURE-TYPE-FIELDS](../proposals/DISCLOSURE-TYPE-FIELDS.md)). The governing rule: **subtypes name provisional, still-emergent groupings we want to identify but aren't set in stone; a fact important enough to earn explicit first-class support graduates into a structured field** — and must not then be duplicated as a subtype (one source of truth).

## Anticipated subtypes (accepted direction, tagged on demand)

### `control` and `reference` (from ASSERTION-CONTENT-TYPES decision)

The [ASSERTION-CONTENT-TYPES](../proposals/ASSERTION-CONTENT-TYPES.md) proposal was resolved on 2026-11-06 ([#61](https://github.com/CloudSecurityAlliance/SecID/issues/61)) with **0 new top-level types**, collapsing its domain into existing `control` and `reference` types with subtype tags plus the Relationship Layer:

| Type | `subtype:` value (accepted direction) | What it means | Example entries |
|------|--------------------------------|---------------|-----------------|
| `control` | `"body-of-knowledge"` | Normative curricula that define what a credential tests for | CISSP CBK, CCSK BoK, CISA Job Practice Areas |
| `reference` | `"course"` | Instructional content with addressable internal structure | CCSK Foundation, SANS SEC401, AWS Security Workshops |

These values will be registered in `SecID-Service/src/type-registry.ts` and moved to "Named subtypes in use today" when the first dedicated BoK or course match_node is tagged. Organizational compliance attestations (SOC 2 holder, FedRAMP authorization for org X) belong in the Relationship Layer, while conformity-assessment methodologies live in `methodology` with `subtype: ["audit-certification"]` (e.g., `methodology/enx.com/tisax`, `methodology/cloudsecurityalliance.org/ccm-auditing-guidelines`).

## Candidate subtypes (pattern-match, not formally proposed)

These patterns exist in the registry but have not been formally proposed as named subtypes. Listed here so future contributors recognize the patterns and pick a consistent name if/when they're tagged.

### `disclosure`

Resolved by [CONSORTIUM-AND-COORDINATOR-SUBTYPES](../proposals/CONSORTIUM-AND-COORDINATOR-SUBTYPES.md): `coordinator` and `psirt` are now named subtypes (see *Named subtypes in use today* above). The other values once floated here — `cna`, `bug-bounty`, `security.txt` — are **deliberately not** subtypes: those facts are carried by the structured `cve.role`, `bug_bounty[]`, and `security_txt` fields from [DISCLOSURE-TYPE-FIELDS](../proposals/DISCLOSURE-TYPE-FIELDS.md), and duplicating them as subtypes would create two sources of truth.

### `regulation`

EU directives, national transpositions, and US/national laws all currently sit in `regulation/` without a discriminator. The cross-type documentation pattern in [AGENTS.md](../../AGENTS.md) already distinguishes these informally.

| `subtype:` value (candidate) | What it would identify |
|------------------------------|------------------------|
| `"law"` | Acts of legislature (US Congress, UK Parliament, etc.) |
| `"directive"` | EU directives requiring national transposition (PSD2, NIS2, eIDAS) |
| `"administrative-rule"` | Administrative/executive rules (US federal regulations, etc.) |
| `"transposition"` | National implementation of an EU directive |

### `entity`

The `consortium` subtype is now in use (see *Named subtypes in use today* above). The organization/product/service split below remains a candidate. The `entity` type mixes organizations (Microsoft, NIST, ISO) with their products (Office 365, AWS S3) and services. The ENTITY-REGULATION-CONTROL-SPLIT proposal's "What's still worth doing" section flagged this as a known pain point with high consumer value (separating "show me all the orgs" from "show me all the products"). `consortium` composes with these if/when they land (an entry can be `["organization", "consortium"]`).

| `subtype:` value (candidate) | What it would identify |
|------------------------------|------------------------|
| `"organization"` | Legal/operational orgs (Microsoft, NIST, ISO, CSA) |
| `"product"` | Products from an org (Office 365, AWS S3, Chrome browser) |
| `"service"` | Service offerings (AWS, Azure, GCP as overall services) |

### `reference` — document kinds (SecID 2.0 corpus expansion)

SecID 2.0 sets out to capture the material practitioners and researchers actually reach for — papers, blogs, reports,
talks, datasets, vendor documentation. All of it is already `reference` ("Documents, research, identifier systems"), so
none of it needs a new type. What it needs is a discriminator, because "show me the academic papers" and "show me the
vendor blogs" are different questions.

| `subtype:` value (candidate) | What it would identify |
|------------------------------|------------------------|
| `"paper"` | Academic papers and preprints (arXiv, DOI, IEEE, ACM, SSRN, USENIX) |
| `"blog"` | Vendor and researcher blog posts (Project Zero, Unit 42, Talos) |
| `"report"` | Industry and threat reports (Verizon DBIR, M-Trends, ENISA Threat Landscape, CSA reports) |
| `"presentation"` | Conference talks and slide decks (Black Hat, DEF CON, RSA, FIRST) |
| `"dataset"` | Evaluation sets and benchmarks (HarmBench, WMDP) — currently sitting implicitly under `control` |
| `"documentation"` | Vendor product and API documentation |
| `"format-spec"` | Data and exchange formats (SARIF, CycloneDX, SPDX, OSCAL, STIX) — already `reference`, untagged |

**Identifier-space warning.** Several of these have genuinely unbounded identifier spaces — a blog post's ID is a URL
slug, and new ones appear daily. Those nodes must declare `open_pattern: true`, which keeps namespace-scoped resolution
working while excluding them from unscoped cross-source search. Bounded sets must *not*: a publisher issues one DBIR a
year, so an enumerated pattern discriminates and stays searchable. See the pattern-breadth rules in
[AGENTS.md](../../AGENTS.md#pattern-breadth-the-one-rule-that-protects-every-query).

### `control` and `entity` — scope of obligation

A standard published by a single company binds only those who do business with it; one published by a consortium binds
its members. Both differ from a public standard anyone may adopt, and the distinction answers a question consumers
genuinely have: *can I just implement this, or do I need a relationship first?* Roughly 72 company- and
consortium-published entries currently sit in `control/` and `methodology/` untagged — SWIFT CSP, the card-brand
programs, EMVCo, ENX/TISAX, the ISACs, and the market-infrastructure operators among them.

| `subtype:` value (candidate) | What it would identify |
|------------------------------|------------------------|
| `"corporate"` | One company's requirements, binding on those who transact with it (SWIFT CSP, Visa, Microsoft SDL) |
| `"consortium"` | A member body's requirements, binding on members (EMVCo, ENX/TISAX, the ISACs) — composes with the existing `entity: consortium` |

### `regulation` — enforcement

Statutes say what the law requires; enforcement actions say what it has actually meant in practice, which is a
different research question. Fines, consent decrees, and regulator decisions (GDPR penalties, FTC actions, ICO
enforcement) sit alongside the `law` / `directive` / `transposition` candidates above.

| `subtype:` value (candidate) | What it would identify |
|------------------------------|------------------------|
| `"enforcement"` | Regulatory enforcement actions, fines, and consent decrees |

## Implicit overloads (subtypes-in-spirit, not yet tagged)

Patterns that predate the `subtype:` convention and are documented in [DESIGN-DECISIONS.md §"Current Overloading"](../explanation/DESIGN-DECISIONS.md). They behave like subtypes — distinct sub-categories within a type — but they don't currently carry a `subtype:` tag in registry data. They're identified by *which namespace* they live in, not by a discriminator field.

| Type | Implicit sub-category | What it covers | Example sources | Anticipated `subtype:` value (if backfilled) |
|------|----------------------|----------------|-----------------|---------------------------------------------|
| `control` | Prescriptive benchmarks | "Test for these behaviors" eval suites that function as requirements | HarmBench, WMDP | `["benchmark"]` |
| `control` | Documentation standards | Templates for describing a model/system, treated as a normative format requirement | Model Cards | `["documentation-standard"]` |
| `control` | Executable check catalogs | Automated posture/compliance check catalogs whose check IDs are cited as concrete security requirements in findings and crosswalks ([#186](https://github.com/CloudSecurityAlliance/SecID/issues/186), [#58](https://github.com/CloudSecurityAlliance/SecID/issues/58)) | Prowler (`control/prowler.com/checks`), DISA STIGs (`control/disa.mil/stig`) | `["check-catalog"]` |

We are not doing a backfill sweep of these implicit overloads. New entries that match these patterns should carry the `subtype:` value from day one, and existing entries pick it up opportunistically when they're touched for other reasons. Over time the implicit overloads become explicit.

The `advisory + incident` pattern was promoted out of this table on 2026-05-27 — see the `### advisory` section above for the now-explicit subtype.

## When to add a subtype vs. split into a new type

The default — and a load-bearing project principle — is **use the existing type plus a `subtype:` tag**. Splitting into a new type is the exception path, gated by the four criteria documented in [DESIGN-DECISIONS.md §"When to Split"](../explanation/DESIGN-DECISIONS.md):

1. **Resolution patterns diverge.** Different URL structures, different APIs, different metadata shapes.
2. **Consumers diverge.** Different tools need to filter them separately, with materially different workflows.
3. **Semantics drift.** The "question answered" becomes meaningfully different.
4. **Volume justifies it.** Enough examples exist to define clear boundaries.

The `disclosure` type passed all four. So did `capability` and `methodology`. Recent decisions to *not* split (glossary → `reference + subtype`, regulation/control split → declined, assertion/content → revision direction is to use existing `control` + `reference` with subtypes) failed at least one criterion — usually #1 (resolution patterns can fit within the parent type's shape) or #2 (consumers don't actually need the filtering distinction).

The cost gradient:

- **Subtype tag** — change one field in a registry file, document the value here, ship. Reversible.
- **New type** — coordinate changes across 4 repos, update parser/resolver/MCP/client logic, migrate existing entries, update all documentation. Hard to reverse.

So the practical rule: **try a subtype first**. If lived experience shows the four split criteria are genuinely met, promote to a new type. If a subtype works fine, leave it as a subtype.

## Decision history

### Proposals that landed as subtypes (existing-type path)

| Proposal | Decision | Mechanism | Status |
|----------|----------|-----------|--------|
| [GLOSSARY-DEFINITION-COMPARISON](../proposals/GLOSSARY-DEFINITION-COMPARISON.md) | Glossaries stay in `reference` | `subtype: ["glossary"]` + `data_repo:` pointer (Phase 1); copy into registry (Phase 2) | Accepted 2026-05-20 |
| [METHODOLOGY-ARCHITECTURE](../proposals/METHODOLOGY-ARCHITECTURE.md) | The category structure for methodology entries (10 categories + 11th "classification" added on tagging sweep) | 11 `subtype:` values applied to all 43 source-level methodology match_nodes on 2026-05-20 | Implemented (categorization landed; arch doc is "Research / design") |
| [ASSERTION-CONTENT-TYPES](../proposals/ASSERTION-CONTENT-TYPES.md) | Declined 2-type split (`assertion`, `content`); collapsed into existing `control` (BoKs as normative knowledge specs), `reference` (courses as instructional artifacts), `methodology` (`audit-certification`), and Relationship Layer (org compliance attestations) | `subtype: ["body-of-knowledge"]` on control, `subtype: ["course"]` on reference | Decided 2026-11-06 ([#61](https://github.com/CloudSecurityAlliance/SecID/issues/61)) |
| [ENTITY-REGULATION-CONTROL-SPLIT](../proposals/ENTITY-REGULATION-CONTROL-SPLIT.md) | Regulations stay in `control/`; small entity-cleanup may still extract clearly-org-not-control entries into `entity/` | Cross-reference fields (`publishedBy:`, `authorizedBy:`) instead of type split | Declined (with rationale) 2026-05-17 |
| [CONSORTIUM-AND-COORDINATOR-SUBTYPES](../proposals/CONSORTIUM-AND-COORDINATOR-SUBTYPES.md) | First `entity` + `disclosure` subtypes; declines `cna`/`bug-bounty`/`security.txt` (kept as structured fields) | `subtype: ["consortium"]` (entity); `subtype: ["coordinator"]` / `["psirt"]` (disclosure) | Draft 2026-07-08 |

### Proposals that became new types (split path)

For the contrast, see [CAPABILITY-TYPE](../proposals/CAPABILITY-TYPE.md) and [METHODOLOGY-TYPE](../proposals/METHODOLOGY-TYPE.md), and [DESIGN-DECISIONS.md §"Case Study: The `disclosure` Split"](../explanation/DESIGN-DECISIONS.md) for the four-criteria gate as actually applied.

## Adding a new subtype

To propose a new named subtype:

1. **Check whether it really needs a name.** A subtype is worth defining when (a) multiple registry entries will share it, and (b) consumers will want to filter or behave differently based on it. A one-off classification with no consumer affordance doesn't justify a named subtype.
2. **Pick a kebab-case string value** — `"glossary"`, `"incident-report"`, `"benchmark"`. Match the conceptual name a practitioner would use. Filenames (`"security.txt"`) and other domain-canonical strings keep their literal form.
3. **Add a row to the "Named subtypes in use today" table** above, under the relevant type, with the value, meaning, where to find entries, and the proposal/decision document.
4. **Tag entries from day one**; don't backfill in a sweep — pick up existing matches opportunistically as they're touched for other reasons. The exception is a small bounded set like methodology (~40 entries), where a one-time sweep is tractable.
5. **If consumer behavior depends on the subtype**, document that behavior wherever the consumer lives (resolver, MCP server, client SDK).

A subtype proposal lives at the same level as a feature decision — a short proposal doc in [docs/proposals/](../proposals/) is appropriate if the subtype changes API behavior or introduces cross-repo coordination; otherwise a PR adding the row to this doc is sufficient.
