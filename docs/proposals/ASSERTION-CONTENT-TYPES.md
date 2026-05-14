# Proposal: `assertion` and `content` Types (11th and 12th SecID Types)

Status: Research / proposal
Date: 2026-05-12
Author: Kurt Seifried, with AI-assisted design
Reviewers: open — please add review notes inline or as PR comments

## Summary

Add two new SecID types covering the education / training / credential ecosystem:

- **`assertion`** — an authority attests that an entity has demonstrated capability X. Covers professional credentials (CISSP, CCSK), org-level compliance attestations (SOC 2 Type II, FedRAMP authorization, ISO 27001 certification), auditor credentials (PCI QSA, ISO Lead Auditor), and microbadges.
- **`content`** — structured learning material with addressable internal organization. Covers bodies of knowledge (CISSP CBK, CCSK BoK) and courses (CCSK Foundation, SANS SEC401).

The two types are linked by registry-layer cross-reference fields. Together they close the largest remaining identity gap in SecID (the education ecosystem) using a 2-type carving that follows the existing `control`/`capability` pattern.

## The Problem

SecID has no identity space for things like CISSP, CCSK, SOC 2, FedRAMP, the CISSP CBK, the CCSK Foundation course, or auditor credentials like PCI QSA. These concepts:

- Get cited *constantly* in security knowledge (compliance frameworks, job postings, audit reports, training plans, resumes)
- Have no stable identifier scheme today — they're referred to with ad-hoc strings ("TSC CC6.1", "CISSP CBK Domain 3", "CCSK v5", "FedRAMP Moderate")
- Don't fit any existing SecID type cleanly

Without identities for these concepts, downstream AI agents and humans can't deterministically resolve a citation. "CISSP" might mean the credential, the exam, the body of knowledge, or the official training. Without disambiguation, mapping and enrichment become unreliable.

## Why Not Existing Types?

We considered each existing type as a home before proposing new ones:

| Existing type | Why it doesn't fit |
|---|---|
| `entity` | An entity *exists*. A credential is something an entity *holds*. Different semantics. |
| `control` | Controls are normative requirements an organization adopts. A credential is awarded *to* an entity by an authority — different shape. |
| `capability` | Capabilities are product features. Credentials and content aren't product features. |
| `methodology` | Methodologies produce outputs (CVSS → score, SSVC → decision). A credential isn't a process — it's an awarded status. |
| `reference` | The closest existing fit for `content`. References are atomic citation targets. Content has addressable internal structure (modules, lessons, domains) that justifies its own type. |
| `disclosure` | Vulnerability disclosure scope — unrelated. |
| `regulation` | Laws and legal requirements — unrelated. |
| `advisory`, `weakness`, `ttp` | Vulnerability/attack space — unrelated. |

## Dimensional Analysis

Before settling on the carving, we measured each concept in the space against six dimensions:

| Concept | Carrier | Authority | Validity | Proof | Citability | Existing-type fit |
|---|---|---|---|---|---|---|
| Professional credential (CISSP, CCSK) | individual | cert body | renewable (CPEs / re-exam) | exam | resumes, job specs, compliance | none |
| Vendor credential (AWS-SCS, SC-100) | individual | vendor | renewable | exam | resumes, vendor compliance | none |
| Org compliance attestation (SOC 2, ISO 27001 cert, FedRAMP) | org / system | audit firm + governing body | annual re-audit | audit | RFPs, security reviews | none |
| Auditor credential (PCI QSA, ISO Lead Auditor) | individual (in cert role) | framework body | renewable | exam + practicum | audit reports, RFPs | none |
| Course (CCSK Foundation, SANS SEC401) | (artifact) | training provider | versioned artifact | n/a (content) | training plans, audit evidence | `reference` (partial) |
| Body of knowledge (CISSP CBK, CCSK BoK) | (artifact) | cert issuer | versioned artifact | n/a (definitional) | curriculum, exam scope | `reference` (partial) |
| Exam version (SY0-701) | (artifact) | cert issuer | superseded over time | n/a (instrument) | candidate prep | none |
| Training completion event | individual (as evidence) | employer | one-time | participation | audit evidence | not registry data |

**Two clusters emerge:**

- Things that are *awarded/asserted* to a carrier (rows 1–4): individual or organizational, issued by an authority, renewable lifecycle, proof-by-test-or-audit.
- Things that are *content artifacts* (rows 5–7): no carrier, published by an authority, versioned, no proof concept.

Training completion (row 8) is an *event*, not an identity — relationship-layer territory, out of scope for registry.

## The Carving

Two new types, paralleling the `control`/`capability` carving:

- `control` = what you MUST do (normative requirements)
- `capability` = what you CAN do (descriptive features)
- `assertion` = what you've BEEN AWARDED / what's been ATTESTED to (awarded status)
- `content` = what's been PUBLISHED to teach / specify learning (instructional/normative content)

The pattern: each pair has a "from the authority's perspective" type (control, assertion) and a "what's available" type (capability, content).

### `assertion` Scope

Covers: any "authority attests that entity has demonstrated capability" identity.

**Includes:**
- Professional credentials held by individuals: CISSP, CCSK, CISSP, CISA, CISM, CRISC, Security+, AWS-SCS, SC-100, GCP-PCSE, OSCP, etc.
- Auditor credentials: PCI QSA, ISO 27001 Lead Auditor, FedRAMP 3PAO assessor
- Org compliance attestations: SOC 2 Type II, SOC 3, ISO 27001 certification, FedRAMP authorization (Low/Moderate/High), CMMC Level 1–3, StateRAMP, IRAP, ENS, C5
- Microbadges (Credly badges, vendor learning paths)

**Does NOT include:**
- Training completion events (relationship-layer)
- Academic degrees (not currently in scope; may revisit)
- "AWS is SOC 2 certified" — the *fact that* a specific entity holds an assertion is relationship-layer; the assertion itself is registry-layer

### `content` Scope

Covers: any structured learning material with addressable internal organization.

**Includes:**
- Bodies of knowledge: CISSP CBK, CCSK BoK, CISSP Outline, CISA Job Practice Areas
- Courses: CCSK Foundation, SANS SEC401, AWS Security Workshops, vendor learning paths
- Academic curricula (probably; deferred until first request)

**Does NOT include:**
- The credential the content teaches toward (`assertion` type)
- Atomic-cite documents like RFCs, arXiv papers (`reference` type — they have no addressable internal structure beyond section numbers)

### Why one type for BoK and course?

Both have the same structural shape:
- A title and version
- A publisher (entity)
- **Internal addressable structure**: top-level groups → sub-items (CISSP CBK: 8 domains → ~5 sub-objectives each; CCSK Foundation: modules → lessons)
- Optional alignment with a credential

Their differences are *data-level*, not *structural*:

| BoK has | Course has |
|---|---|
| Mapped exam coverage % per domain | Delivery format (self-paced, instructor-led, lab) |
| Definitional authority over exam scope (`is_normative: true`) | Length / duration / prerequisites |
| (No delivery format — it's a spec) | Learning objectives, hands-on labs |

These fit cleanly as attributes within an entry, not as separate types. Same registry-layer shape, different `data` fields.

## Cross-References

The two types form a graph via registry-layer SecID reference fields. These are *definitional* attributes (not enrichment), so they live in the registry — not the Relationship Data Layer.

### `assertion` cross-references

```
assertion (CISSP)
├── issuer: secid:entity/...isc2.org/isc2          [the awarding body]
├── tests_curriculum: secid:content/isc2.org/cissp-cbk   [knowledge-based assertions]
├── assesses_framework: (null)                            [audit-based assertions only]
├── examination: secid:assertion/isc2.org/cissp#exam      [self-reference to exam subpath]
└── alternate_names: ["CISSP"]

assertion (SOC 2 Type II)
├── issuer: secid:entity/...aicpa.org/aicpa
├── tests_curriculum: (null)                              [not knowledge-based]
├── assesses_framework: secid:control/aicpa.org/tsc       [the standard audited]
└── alternate_names: ["SOC 2 Type 2", "SOC2 Type II"]

assertion (FedRAMP Moderate)
├── issuer: secid:entity/.../fedramp-pmo
├── assesses_framework: secid:control/nist.gov/800-53@rev5
└── alternate_names: ["FR-Mod"]
```

### `content` cross-references

```
content (CISSP CBK)
├── publisher: secid:entity/...isc2.org/isc2
├── is_normative: true                                    [defines exam scope]
├── tested_by: secid:assertion/isc2.org/cissp             [back-reference, optional]
└── version: 2024

content (CCSK Foundation course)
├── publisher: secid:entity/.../cloudsecurityalliance
├── is_normative: false                                    [teaches; doesn't define exam]
├── teaches_curriculum: secid:content/cloudsecurityalliance.org/ccsk-bok
├── prepares_for: secid:assertion/cloudsecurityalliance.org/ccsk
└── version: v5
```

### Subpath structure

Both types have rich internal structure addressable via subpath:

| Citation | SecID |
|---|---|
| "personnel must hold CISSP" | `secid:assertion/isc2.org/cissp` |
| "CISSP CBK Domain 3: Security Architecture" | `secid:content/isc2.org/cissp-cbk#domain/d3` |
| "Security+ exam SY0-701" | `secid:assertion/comptia.org/security-plus#exam/sy0-701` |
| "ISC² Associate-level CISSP" | `secid:assertion/isc2.org/cissp#level/associate` |
| "CCSK Foundation Module 3 Lesson 4" | `secid:content/cloudsecurityalliance.org/ccsk-foundation#module/m3/lesson/l4` |
| "AWS has SOC 2 Type II" | The assertion: `secid:assertion/aicpa.org/soc-2-type-2`; "AWS has it" = relationship-layer |
| "PCI QSA-led assessment" | The QSA cred: `secid:assertion/pcisecuritystandards.org/qsa`; "led by X" = relationship-layer |
| "Annual security awareness training was completed" | Not registry — relationship-layer event |

## Worked Examples

Two fully-fleshed-out example entries to ground the proposal. These would land as registry/assertion/org/isc2.json and registry/content/org/isc2.json once the types are live.

### `assertion/org/isc2.json` (excerpt — CISSP only)

```json
{
  "schema_version": "1.0",
  "namespace": "isc2.org",
  "type": "assertion",
  "status": "draft",
  "official_name": "International Information System Security Certification Consortium",
  "common_name": "(ISC)²",
  "match_nodes": [
    {
      "patterns": ["(?i)^cissp$"],
      "description": "Certified Information Systems Security Professional",
      "weight": 100,
      "data": {
        "official_name": "Certified Information Systems Security Professional",
        "common_name": "CISSP",
        "carrier_type": "individual",
        "category": "professional-credential",
        "issuer": "secid:entity/org/isc2",
        "tests_curriculum": "secid:content/isc2.org/cissp-cbk",
        "renewal": {"cycle_years": 3, "mechanism": "CPE", "cpes_required": 120},
        "notes": "ISC²'s flagship credential; widely required in security leadership roles.",
        "versions_available": [
          {"version": "2024", "status": "current", "note": "Aligned with CBK 2024 effective April 2024"}
        ],
        "urls": [
          {"type": "website", "url": "https://www.isc2.org/certifications/cissp"}
        ],
        "examples": ["cissp", "cissp#exam/2024", "cissp#level/associate"]
      },
      "children": [
        {
          "patterns": ["^exam/.+$"],
          "description": "Specific exam version offered for this credential.",
          "data": {"type": "exam_version"}
        },
        {
          "patterns": ["^level/associate$"],
          "description": "Associate of (ISC)² — passed exam but does not yet meet experience requirement.",
          "data": {"type": "credential_level"}
        }
      ]
    }
  ]
}
```

### `content/org/isc2.json` (excerpt — CISSP CBK only)

```json
{
  "schema_version": "1.0",
  "namespace": "isc2.org",
  "type": "content",
  "status": "draft",
  "official_name": "(ISC)²",
  "match_nodes": [
    {
      "patterns": ["(?i)^cissp-cbk$"],
      "description": "CISSP Common Body of Knowledge — defines what the CISSP exam tests.",
      "weight": 100,
      "data": {
        "official_name": "CISSP Common Body of Knowledge",
        "common_name": "CISSP CBK",
        "publisher": "secid:entity/org/isc2",
        "is_normative": true,
        "tested_by": "secid:assertion/isc2.org/cissp",
        "structure_kind": "domains",
        "versions_available": [
          {"version": "2024", "status": "current", "note": "Effective April 2024; 8 domains, weighted exam coverage."}
        ],
        "urls": [
          {"type": "exam_outline", "url": "https://www.isc2.org/certifications/cissp/cissp-certification-exam-outline"}
        ],
        "examples": ["cissp-cbk", "cissp-cbk#domain/d3"]
      },
      "children": [
        {
          "patterns": ["^domain/d[1-8]$"],
          "description": "CISSP CBK domain (8 total).",
          "data": {
            "type": "domain",
            "known_values": {
              "d1": "Security and Risk Management",
              "d2": "Asset Security",
              "d3": "Security Architecture and Engineering",
              "d4": "Communication and Network Security",
              "d5": "Identity and Access Management (IAM)",
              "d6": "Security Assessment and Testing",
              "d7": "Security Operations",
              "d8": "Software Development Security"
            }
          }
        }
      ]
    }
  ]
}
```

## Edge Cases

### NICE Framework (NIST IR 8355)

NICE is a competency framework — work roles, tasks, knowledge areas, skills. It's BoK-shaped (structured, addressable, normative) but it's not a BoK *for any specific credential*. It defines a *vocabulary* for talking about cybersecurity work.

**Decision:** NICE Framework stays in `methodology` where it currently lives. The fact that it's curriculum-shaped doesn't override its actual function as a methodology for describing cybersecurity competencies.

### Academic credentials (BS Cybersecurity)

Universities issue them. Cited in job specs. Structurally identical to professional credentials.

**Decision:** Could fit `assertion` if needed, but deferred until concrete demand. The University → assertion namespace structure is workable (`assertion/edu/mit/bs-cs`) but introduces many low-value entries.

### Microbadges (Credly badges, etc.)

Credly issues badges on behalf of many authorities. The *badge* is the assertion; *Credly* is the platform.

**Decision:** Model the badge under its actual issuer's namespace, not under credly.com. E.g., AWS Certified Cloud Practitioner Foundational badge → `assertion/amazon.com/aws-ccp-foundational`. Credly is a delivery mechanism, not an authority.

### Auditor credentials with framework-tied issuers

PCI QSA is issued by the PCI SSC — the same organization that publishes PCI DSS. ISO 27001 Lead Auditor is certified by ISO/IEC and accreditation bodies.

**Decision:** Same shape as any other assertion. `assertion/pcisecuritystandards.org/qsa`. The fact that the issuer is also the framework owner doesn't change the type. The cross-reference `assesses_framework: secid:control/pcisecuritystandards.org/pci-dss` captures the relationship.

### Continuing-education requirements

CISSP requires 120 CPEs every 3 years. SOC 2 requires annual re-audit. The renewal cycle is *definitional* (set by the issuer, doesn't vary per holder).

**Decision:** Model in registry as a `renewal: {cycle_years, mechanism, cpes_required?}` block on the assertion entry. The fact that *a specific person* renewed in 2026 is relationship-layer.

### Vendor learning paths vs courses

AWS Skill Builder courses, Microsoft Learn paths, Google Cloud Skill Boost. These are courses, but they're often free, modular, and don't issue credentials directly.

**Decision:** They fit `content`. Whether they issue a microbadge at the end is captured by `prepares_for` linking to an `assertion` entry (or null if no credential).

## Multi-Repo Impact

Per CLAUDE.md: "adding a new type requires coordinated changes across multiple repos." Two new types means doing this twice (or coordinating both in one push). The impact:

### SecID (this repo)

- SPEC.md: add `assertion` and `content` to type list
- CLAUDE.md: update type table, registry structure section
- `registry/assertion/_template.md` and `registry/content/_template.md` — entry templates
- `registry/assertion.md` and `registry/content.md` — type descriptions
- INDEX.md: add new types
- README.md: regenerate counts (724 → 724+N after first entries)
- This proposal moves from `docs/proposals/` to `docs/explanation/` once implemented (per project convention for accepted proposals)

### SecID-Service

- `src/types.ts`: add `assertion` and `content` to `SECID_TYPES` array
- `src/mcp.ts`: add type descriptions for MCP `describe` tool
- Website / frontend: add type filtering, display logic
- Tests: extend type-coverage tests

### SecID-Server-API

- `python/resolver.py`: add to `SECID_TYPES` list
- TypeScript variant: same
- Tests: extend type-coverage tests

### SecID-Client-SDK

- Type definitions in: Python, npm, Go, Rust, Java, C#
- AI instructions documents that enumerate types
- README examples if applicable

### Estimated effort

This is comparable in scope to the `methodology` and `capability` rollouts — those were the most recent type additions. Estimate: ~1 day of coordinated work across the four repos for the spec/type-list changes, plus ongoing content population.

## Open Questions for Review

For an AI or human reviewer, the following design calls are open for challenge:

1. **One `content` type or split BoK and course?** The proposal unifies them. Alternative: separate types like `curriculum` (normative BoK) and `course` (instructional). Question: is the data-level distinction (`is_normative: true/false`) enough, or does it warrant a type split?

2. **`assesses_framework` vs `tests_curriculum`** — having both verbs on `assertion` reflects the two assertion kinds (audit-based vs knowledge-based). Could we unify under a single field? Pro: simpler schema. Con: loses the structural distinction between "knowledge tested by exam" and "compliance audited."

3. **Renewal cycle as registry data**: included as a `renewal` block on assertions. Alternative: defer to relationship-layer. Question: is "CISSP requires 120 CPEs every 3 years" definitional enough to be registry-layer, or does it belong with "Kurt holds CISSP since 2018"?

4. **Carrier type as a tagged field** (`carrier_type: "individual"` vs `"organization"` vs `"system"`): currently included. Question: necessary, or can consumers infer from context?

5. **Academic credentials**: deferred from initial scope. Question: defer until concrete request, or include from day one to avoid future refactor?

6. **Naming**: `assertion` covers credentials, attestations, authorizations, badges. Question: is this name clear enough, or is "credential" or "attestation" better? `content` is generic — overlaps semantically with `reference`. Better alternatives?

7. **Multi-repo cost timing**: do we ship spec-level changes (SPEC.md, type-list updates across repos) as one coordinated push, then iterate on registry entries? Or hold spec changes until we have a critical mass of entries ready?

## Validation Criteria

How would we know the design is wrong? Some checks:

- **An entry doesn't fit cleanly** — if the first real registry entries strain the proposed shape (e.g., we need to add 5 new top-level fields not anticipated here), the carving may be wrong.
- **Cross-reference verbs proliferate** — if `assertion` ends up needing >3 distinct cross-reference verbs to point at curriculum/framework/parent-credential, the model may be under-specified.
- **Consumer confusion** — if downstream consumers (resolver, MCP, client SDKs) need special-case logic that's not symmetric with how `control` and `capability` are handled, the carving may not be analogous enough.
- **Naming collisions** — if `content` produces resolver ambiguity with `reference`, naming needs revisiting.

## Decision Path

This proposal is in **research / proposal** state. The path forward:

1. **Review** — circulate this doc for AI and human review. Address open questions, refine carving if needed.
2. **Spec lock** — finalize type names, scope, cross-reference field names. Update SPEC.md.
3. **Multi-repo lift** — coordinated PRs across SecID, SecID-Service, SecID-Server-API, SecID-Client-SDK to add the two types to the type list.
4. **Initial registry entries** — populate first entries: CCSK (assertion) + CCSK BoK (content), CISSP (assertion) + CISSP CBK (content), SOC 2 Type II (assertion), one or two courses.
5. **Validate against real usage** — see if first entries strain the design; iterate if so.

## Related Documents

- `docs/proposals/CAPABILITY-TYPE.md` — the closest structural analog (control/capability split mirrors assertion/content)
- `docs/proposals/METHODOLOGY-TYPE.md` — prior new-type proposal
- `docs/reference/REGISTRY-JSON-FORMAT.md` — the schema entries must conform to
- `docs/explanation/DESIGN-DECISIONS.md` — broader SecID design principles
- `CLAUDE.md` (section: "WARNING: Adding a new type requires coordinated changes across multiple repos") — the multi-repo cost rationale
