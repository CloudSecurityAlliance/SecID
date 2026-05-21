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

Adding a new type requires coordinated changes across SecID, SecID-Service, SecID-Server-API, and SecID-Client-SDK (the type list is hardcoded in each). See [CLAUDE.md](../../CLAUDE.md) "WARNING: Adding a new type" for the full impact list, and *When to add a subtype vs. split into a new type* below for the decision gate.

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

## Named subtypes in use today

Two types currently carry named `subtype:` tags on entries: `reference` (for glossaries) and `methodology` (the full 11-category set tagged on all ~40 entries). Other named subtypes are either anticipated (assertion-content revision direction), pattern-match candidates (disclosure, regulation, entity), or implicit overloads that predate the convention.

### `reference`

| `subtype:` value | What it means | Where to find it | Defined by |
|------------------|---------------|------------------|------------|
| `"glossary"` | A glossary document with addressable term-level subpaths. Entry is identity-only; term data lives in a separate dataset repo (Phase 1) and will be copied into the registry for direct API serving in Phase 2. | `registry/reference/<path>.json` entries carrying `subtype: ["glossary"]` | [GLOSSARY-DEFINITION-COMPARISON](../proposals/GLOSSARY-DEFINITION-COMPARISON.md) (Accepted 2026-05-20) |

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

## Anticipated subtypes (pending proposal)

### `control` and `reference` (from ASSERTION-CONTENT-TYPES revision direction)

The [ASSERTION-CONTENT-TYPES](../proposals/ASSERTION-CONTENT-TYPES.md) proposal is "Under revision" and is expected to collapse toward fewer new types, using existing `control` and `reference` with subtype tags. Concrete subtypes flagged in the revision direction:

| Type | `subtype:` value (anticipated) | What it means | Example entries |
|------|--------------------------------|---------------|-----------------|
| `control` | `"body-of-knowledge"` | Normative curricula that define what a credential tests for | CISSP CBK, CCSK BoK, CISA Job Practice Areas |
| `reference` | `"course"` | Instructional content with addressable internal structure | CCSK Foundation, SANS SEC401, AWS Security Workshops |

These will be added to "Named subtypes in use today" when the ASSERTION-CONTENT-TYPES revision lands as Accepted. Org-level compliance attestations (SOC 2 holder, FedRAMP authorization for org X) are anticipated to go to the relationship layer, not the registry; professional credentials (CISSP, CCSK) may still need their own home, which is part of why the proposal is still under revision.

## Candidate subtypes (pattern-match, not formally proposed)

These patterns exist in the registry but have not been formally proposed as named subtypes. Listed here so future contributors recognize the patterns and pick a consistent name if/when they're tagged.

### `disclosure`

The disclosure type has 486 entries dominated by CVE Numbering Authorities (CNAs). Substructure already exists via the `cve:` / `bug_bounty:` / `safe_harbor:` / `security_txt:` / `disclosure_policy:` fields proposed in [DISCLOSURE-TYPE-FIELDS](../proposals/DISCLOSURE-TYPE-FIELDS.md), but no `subtype:` tags yet.

| `subtype:` value (candidate) | What it would identify |
|------------------------------|------------------------|
| `"cna"` | CVE Numbering Authority entries (dominant subset — 486 today) |
| `"bug-bounty"` | Programs hosted on HackerOne / Bugcrowd / Intigriti |
| `"psirt"` | Vendor Product Security Incident Response Team programs without a bug bounty |
| `"security.txt"` | Entries primarily sourced from an RFC 9116 `security.txt` file |

### `regulation`

EU directives, national transpositions, and US/national laws all currently sit in `regulation/` without a discriminator. The cross-type documentation pattern in [CLAUDE.md](../../CLAUDE.md) already distinguishes these informally.

| `subtype:` value (candidate) | What it would identify |
|------------------------------|------------------------|
| `"law"` | Acts of legislature (US Congress, UK Parliament, etc.) |
| `"directive"` | EU directives requiring national transposition (PSD2, NIS2, eIDAS) |
| `"administrative-rule"` | Administrative/executive rules (US federal regulations, etc.) |
| `"transposition"` | National implementation of an EU directive |

### `entity`

The `entity` type mixes organizations (Microsoft, NIST, ISO) with their products (Office 365, AWS S3) and services. The ENTITY-REGULATION-CONTROL-SPLIT proposal's "What's still worth doing" section flagged this as a known pain point with high consumer value (separating "show me all the orgs" from "show me all the products").

| `subtype:` value (candidate) | What it would identify |
|------------------------------|------------------------|
| `"organization"` | Legal/operational orgs (Microsoft, NIST, ISO, CSA) |
| `"product"` | Products from an org (Office 365, AWS S3, Chrome browser) |
| `"service"` | Service offerings (AWS, Azure, GCP as overall services) |

## Implicit overloads (subtypes-in-spirit, not yet tagged)

Two patterns predate the `subtype:` convention and are documented in [DESIGN-DECISIONS.md §"Current Overloading"](../explanation/DESIGN-DECISIONS.md). They behave like subtypes — distinct sub-categories within a type — but they don't currently carry a `subtype:` tag in registry data. They're identified by *which namespace* they live in, not by a discriminator field.

| Type | Implicit sub-category | What it covers | Example sources | Anticipated `subtype:` value (if backfilled) |
|------|----------------------|----------------|-----------------|---------------------------------------------|
| `advisory` | Incident reports | "This AI system caused harm" / "this device failed" publications | AIID, NHTSA, FDA adverse events | `["incident-report"]` |
| `control` | Prescriptive benchmarks | "Test for these behaviors" eval suites that function as requirements | HarmBench, WMDP | `["benchmark"]` |
| `control` | Documentation standards | Templates for describing a model/system, treated as a normative format requirement | Model Cards | `["documentation-standard"]` |

We are not doing a backfill sweep of these implicit overloads. New entries that match these patterns should carry the `subtype:` value from day one, and existing entries pick it up opportunistically when they're touched for other reasons. Over time the implicit overloads become explicit.

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
| [ASSERTION-CONTENT-TYPES](../proposals/ASSERTION-CONTENT-TYPES.md) | Originally proposed two new types (`assertion`, `content`); revision direction collapses toward existing `control` (BoKs as normative knowledge specs) + `reference` (courses as content artifacts) + relationship-layer (org compliance attestations) | Anticipated: `subtype: ["body-of-knowledge"]` on control, `subtype: ["course"]` on reference | Under revision |
| [ENTITY-REGULATION-CONTROL-SPLIT](../proposals/ENTITY-REGULATION-CONTROL-SPLIT.md) | Regulations stay in `control/`; small entity-cleanup may still extract clearly-org-not-control entries into `entity/` | Cross-reference fields (`publishedBy:`, `authorizedBy:`) instead of type split | Declined (with rationale) 2026-05-17 |

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
