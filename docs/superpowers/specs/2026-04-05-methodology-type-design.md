# Design: `methodology` as 10th SecID Type

Status: Approved design
Date: 2026-04-05

## Summary

Add `methodology` as a tenth SecID type — identifying formal processes with defined inputs, steps, and outputs used to produce security analysis, scores, mappings, decisions, classifications, and reports.

## The Problem

SecID can identify and resolve CVEs, CWEs, ATT&CK TTPs, NIST controls, regulations, capabilities, and organizational entities. What it cannot do is identify the **process used to produce a relationship between two of those things**.

When a practitioner writes "CCM control IAM-01 maps to NIST CSF PR.AC-1," there is no machine-readable way to express how that mapping was established, why that methodology was chosen over alternatives, or who requires it. The mapping floats without process provenance.

This matters because the methodology chosen changes the meaning and defensibility of the output. CVSS and SSVC both produce vulnerability priorities but are not interchangeable. STRM and a simple crosswalk both produce control mappings but carry different evidentiary weight.

## Classification: The Duck Test

> **"If someone hands you this document and asks 'what do I DO with it?' — what is the primary answer?"**

| Primary answer | SecID type |
|----------------|-----------|
| "Follow this process to produce an output" | `methodology` |
| "Implement these requirements" / "Check compliance against these" | `control` or `regulation` |
| "Understand this knowledge base" | `reference` or existing type |

"Does it contain some methodology?" is explicitly NOT the test — everything contains some methodology. The question is whether process is the **primary purpose**.

### Applied Examples

| Thing | Duck test answer | Type |
|-------|-----------------|------|
| NIST IR 8477 | Follow this to produce a defensible mapping | `methodology` |
| CVSS v4.0 | Follow this to produce a vulnerability score | `methodology` |
| SSVC | Follow this decision tree to produce a priority | `methodology` |
| CCM | Implement these cloud security controls | `control` |
| CCM Implementation Guidelines | Follow this to implement/audit CCM | `methodology` |
| NIST 800-53 | Implement these controls | `control` |
| NIST RMF (800-37) | Follow this to authorize a system | `methodology` |
| ISO 27001 clauses 4-10 | Implement these ISMS requirements | `regulation` |
| ISO 27005 | Follow this to perform risk assessment | `methodology` |
| STRIDE | Follow this to enumerate threats | `methodology` |
| ATT&CK matrix | Understand adversary behavior | `ttp` |
| SOC 2 Trust Services Criteria | Comply with these audit criteria | `regulation` |
| SOC 2 examination process | Follow this to conduct an examination | `methodology` |

### Embedded Methodology: Leave It Alone

ISO 27001 contains an ISMS management process within a primarily-requirements document. Do not extract it. Create a `methodology` record that cites ISO 27001 as its normative reference. Separate records that cross-reference, not absorbing control documents into methodology entries.

## Why Not Use Existing Types?

### Why not `reference`?

Both resolve to documents. But `reference` is SecID's catch-all bucket — "documents that don't fit elsewhere." Leaving methodologies in `reference` makes the type less navigable and hides the semantic signal that this is a **process**, not a document to read.

When you see `secid:methodology/first.org/cvss@4.0`, you immediately know it's a process that produces outputs from inputs — something you *follow*, not something you *read about*. That semantic clarity in the type field is worth the cost of a 10th type.

Consumer divergence is real: a GRC analyst asking "which methodology should I use for control mapping?" is a different workflow from "give me this document."

### Why not `control`?

Controls define requirements. Methodologies define processes. A methodology may contain normative language (SHALL, MUST) but its primary purpose is procedural, not prescriptive. The duck test distinguishes them cleanly.

## Distinction Table

| | Control | Methodology | Reference |
|--|---------|-------------|-----------|
| **Duck test answer** | "Implement these requirements" | "Follow this process to produce an output" | "Read/cite this document" |
| **Primary purpose** | Define what must be done | Define how to systematically do it | Inform or provide evidence |
| **Output when used** | Compliance state | Score, mapping, decision, classification, report | Understanding |
| **Authority** | Standards body (prescriptive) | Process publisher (procedural) | Author (informational) |
| **Consumer question** | "What must I do?" | "How do I produce a defensible result?" | "Where can I read about this?" |

## Multi-Type Is Architecturally Necessary

SecID already supports an entity existing in multiple types. For methodology, this is not a convenience — it's required.

**SOC 2 stress test:**

| Type | Entry | Actor | Use case |
|------|-------|-------|----------|
| `regulation` | `secid:regulation/aicpa.org/soc2` | Compliance team | "What must we comply with?" |
| `methodology` | `secid:methodology/aicpa.org/soc2-examination` | Auditor / audit prep | "How do we scope and conduct the examination?" |
| `reference` | `secid:reference/aicpa.org/soc2-report` | Procurement / vendor assessment | "Provide your SOC 2 report" |

Forcing SOC 2 into a single type would misrepresent it.

## Tool Implementations of Methodologies

Tools and products that implement a specific methodology (e.g., a Claude skill that implements IR 8477, a CVSS calculator) are registered as `entity` type entries. The relationship "entity X implements methodology Y" belongs in the relationship layer (future). This is the same pattern as Prowler (an entity) producing control checks — the tool is an entity, what it does is a relationship.

## Identifier Format

```
secid:methodology/{namespace}/{name}[@version][#{subpath}]
```

**Examples:**

```
secid:methodology/nist.gov/ir-8477                       # IR 8477 (all styles + selection)
secid:methodology/nist.gov/ir-8477#crosswalk             # Crosswalk mapping style
secid:methodology/nist.gov/ir-8477#supportive            # Supportive relationship mapping
secid:methodology/nist.gov/ir-8477#strm                  # Set Theory Relationship Mapping
secid:methodology/nist.gov/ir-8477#structural            # Structural mapping
secid:methodology/nist.gov/ir-8477#selection             # Decision methodology for choosing

secid:methodology/first.org/cvss@4.0                     # CVSS v4.0
secid:methodology/cmu.edu/ssvc@2.0                        # SSVC v2.0 (CMU SEI/CERT/CC)
secid:methodology/iso.org/27005@2022                     # Risk assessment
secid:methodology/nist.gov/rmf                           # Risk Management Framework (800-37)
secid:methodology/mitre.org/stride                       # STRIDE threat modeling
secid:methodology/cloudsecurityalliance.org/ccm-mapping-methodology  # CSA CCM mapping
```

**Subpath convention:** Sub-methodologies use the name the source document gives them. IR 8477 names its four styles explicitly. NIST RMF names its seven steps. CVSS names its metric groups. Follow the source.

**Version convention:** Use `@version` when the methodology has formally versioned editions where the process itself changes between versions (CVSS 3.1 vs 4.0, ISO 27005:2022 vs 2018).

## Registry Scope: Identity + Resolution + Disambiguation Only

Following SecID's three-layer principle, the registry entry contains:

**In the registry:**
- Identity — what is this methodology called, who publishes it
- Resolution — URLs where to find it
- Disambiguation — subpath patterns for sub-methodologies, `version_required` where editions differ materially

**Deferred to the data layer:**
- `input_types`, `output_type` — enrichment
- `use_when`, `do_not_use_when` — selection guidance (enrichment)
- `compared_to` — relationship layer
- `required_by`, `adopted_by` — relationship layer
- `process_steps` — enrichment

Registry files use the same `match_nodes` structure as every other type.

## File Structure

```
registry/
├── methodology.md              # Type description
├── methodology.json            # Type-level JSON metadata
├── methodology/
│   ├── _template.md            # Template for new namespace files
│   ├── gov/
│   │   ├── nist.json           # NIST: ir-8477, rmf, 800-30, 800-61, 800-115
│   │   └── cisa.json           # CISA: attck-mapping
│   ├── org/
│   │   ├── first.json          # FIRST: cvss
│   │   ├── iso.json            # ISO: 27005, 27035, 27037-27043, 29147, 30111, etc.
│   │   ├── mitre.json          # MITRE: ctid-framework-mapping, ctid-platform-mapping
│   │   ├── owasp.json          # OWASP: testing-guide
│   │   ├── opengroup.json      # The Open Group: fair (Open FAIR standard)
│   │   ├── cloudsecurityalliance.json  # CSA: ccm-mapping, incident-to-control, control-to-capability
│   │   └── isecom.json         # ISECOM: osstmm
│   ├── edu/
│   │   └── cmu.json            # CMU SEI/CERT/CC: ssvc
│   ├── dev/
│   │   └── slsa.json           # SLSA (OpenSSF)
│   └── com/
│       ├── microsoft.json      # Microsoft: stride (origin)
│       └── versprite.json      # VerSprite: pasta
```

One file per namespace. All methodologies from one organization in one file.

## Population Plan (~40 Entries)

### Wave 1: High-priority formal standards (validate the pattern)

| SecID | Publisher | Priority |
|-------|-----------|----------|
| `methodology/nist.gov/ir-8477` (5 sub-methodologies) | NIST | High |
| `methodology/first.org/cvss@4.0` | FIRST | High |
| `methodology/cmu.edu/ssvc@2.0` | CMU SEI/CERT/CC | High |
| `methodology/cisa.gov/attck-mapping` | CISA/HSSEDI | High |
| `methodology/iso.org/27005@2022` | ISO | High |

### Wave 2: Vulnerability & incident management

| SecID | Publisher |
|-------|-----------|
| `methodology/first.org/epss` | FIRST |
| `methodology/iso.org/29147@2018` | ISO |
| `methodology/iso.org/30111@2019` | ISO |
| `methodology/nist.gov/800-61` | NIST |
| `methodology/iso.org/27035` | ISO |
| `methodology/verisframework.org/veris` | Verizon RISK Team |

### Wave 3: Risk & assessment

| SecID | Publisher |
|-------|-----------|
| `methodology/nist.gov/800-30` | NIST |
| `methodology/nist.gov/rmf` | NIST |
| `methodology/opengroup.org/fair` | The Open Group |
| `methodology/iso.org/31000` | ISO |
| `methodology/nist.gov/800-115` | NIST |
| `methodology/commoncriteriaportal.org/cem` | Common Criteria |

### Wave 4: Threat modeling

| SecID | Publisher |
|-------|-----------|
| `methodology/microsoft.com/stride` | Microsoft |
| `methodology/versprite.com/pasta` | VerSprite |
| `methodology/threatmodeler.com/vast` | ThreatModeler |
| `methodology/linddun.org/linddun` | LINDDUN (needs namespace verification) |
| `methodology/octotrike.org/trike` | Trike (needs namespace verification) |

### Wave 5: Mapping, forensics, supply chain, audit

| SecID | Publisher |
|-------|-----------|
| `methodology/cloudsecurityalliance.org/ccm-mapping-methodology` | CSA |
| `methodology/mitre.org/ctid-framework-mapping` | MITRE/CTID |
| `methodology/mitre.org/ctid-platform-mapping` | MITRE/CTID |
| `methodology/iso.org/27037` | ISO |
| `methodology/iso.org/27041` | ISO |
| `methodology/iso.org/27042` | ISO |
| `methodology/iso.org/27043` | ISO |
| `methodology/ietf.org/rfc-3227` | IETF |
| `methodology/first.org/tlp` | FIRST |
| `methodology/nist.gov/800-161` | NIST |
| `methodology/slsa.dev/slsa` | OpenSSF/Google |
| `methodology/iso.org/27006` | ISO |
| `methodology/iso.org/27007` | ISO |
| `methodology/iso.org/17021` | ISO |
| `methodology/pentest-standard.org/ptes` | PTES |
| `methodology/owasp.org/testing-guide` | OWASP |
| `methodology/isecom.org/osstmm` | ISECOM |

### Wave 6: CSA draft methodologies (claim namespace)

| SecID | Publisher | Notes |
|-------|-----------|-------|
| `methodology/cloudsecurityalliance.org/incident-to-control` | CSA | Draft — claim namespace |
| `methodology/cloudsecurityalliance.org/control-to-capability` | CSA | Draft — claim namespace |

## Implementation Deliverables

### Proposal documents (docs/proposals/)

| Document | Contents |
|----------|----------|
| `METHODOLOGY-TYPE.md` | Problem statement, duck test, why not reference/control, multi-type examples, identifier format, initial candidates |
| `METHODOLOGY-ARCHITECTURE.md` | How methodology fits the three-layer model: process provenance for relationships, methodology as the "how" connecting controls to capabilities |
| `METHODOLOGY-PROCESS.md` | Research process per entry: what to capture, sub-methodology identification, versioning, status values |
| `METHODOLOGY-TYPE-IMPLEMENTATION-PLAN.md` | Phased rollout: SecID repo → SecID-Service → SecID-Client-SDK → population |

### Registry files

- `registry/methodology.md` — type description
- `registry/methodology.json` — type-level JSON
- `registry/methodology/_template.md` — namespace template

### Spec & doc updates (SecID repo)

- SPEC.md — add methodology to type list (10 types)
- CLAUDE.md — add methodology to type table, update counts
- README.md — add methodology to type table, add examples
- DESIGN-DECISIONS.md — document the 9→10 type split rationale

### Initial proof-of-concept entries (SecID repo)

- `registry/methodology/gov/nist.json` — IR 8477 with 5 sub-methodologies
- `registry/methodology/org/first.json` — CVSS v4.0
- `registry/methodology/edu/cmu.json` — SSVC v2.0

### SecID-Service updates (CloudSecurityAlliance/SecID-Service repo)

- Add `methodology` to `SECID_TYPES` in `src/types.ts`
- Update MCP tool descriptions (resolve, lookup, describe) with methodology examples
- Update website: type count ("Ten Types of Security Knowledge"), add methodology card
- Update TYPE_DESCRIPTIONS in website explorer
- Re-upload KV with methodology type data
- Deploy worker
- Add parser test for methodology type
- Update MCP resource count test

### SecID-Client-SDK updates (CloudSecurityAlliance/SecID-Client-SDK repo)

- Python SDK: update `lookup()` type docstring, add methodology examples to README, add test case
- TypeScript SDK: update `lookup()` type docstring, add methodology examples to README
- Go SDK: update `Lookup()` type documentation, add methodology example
- Cross-SDK methodology test cases

## Decisions Made

| Decision | Rationale |
|----------|-----------|
| Add `methodology` as a tenth SecID type | The process used to produce security relationships is not representable in any existing type |
| Duck test as classification criterion | "Is process the primary purpose?" is answerable in seconds and generates consistent results |
| Multi-type entries are architecturally necessary | SOC 2 demonstrates that a single artifact serves different roles for different actors |
| Sub-components are first-class via subpath | `secid:methodology/nist.gov/ir-8477#strm` resolves to STRM-specific content |
| Leave embedded methodologies in place | Create a `methodology` record that cites the parent document; don't extract |
| Registry fields: identity + resolution + disambiguation only | Defer enrichment (use_when, input_types, compared_to, required_by) to data layer per SecID principles |
| Tool implementations go in `entity` type | A tool that implements a methodology is a product; the "implements" relationship is relationship-layer data |
| No new verb/keyword taxonomy | Documents use their own normative language (RFC 2119 etc.); SecID classifies by primary purpose, not by vocabulary |

## Resolved Attribution Issues

These were identified during review and corrected:

| Item | Was | Corrected To | Reason |
|------|-----|--------------|--------|
| SSVC | `cisa.gov` | `cmu.edu` | CISA is an adopter; CMU SEI/CERT/CC is the publisher |
| PASTA | `owasp.org` | `versprite.com` | Created by Tony UcedaVelez / VerSprite, not OWASP |
| FAIR | `fairinstitute.org` | `opengroup.org` | The Open Group publishes the formal standard (Open FAIR) |
| VERIS | `veriscommunity.net` | `verisframework.org` | Domain redirect; publisher is Verizon RISK Team |
| STIX | Included in Wave 5 | Removed | STIX is a data format/standard, not a methodology — duck test fails |
| Diamond Model | `mitre.org` | Deferred | Not published by MITRE; no stable institutional domain exists |
| Attack Trees | `schneier.com` | Deferred | Concept from 1999 magazine article; no institutional owner; personal domain |

## Open Questions

1. **STRIDE attribution** — originated at Microsoft, now community-adopted. Using `microsoft.com` since they published it. Confirm this is correct.
2. **LINDDUN namespace** — need to verify `linddun.org` is the authoritative domain.
3. **Trike namespace** — need to verify `octotrike.org` is the authoritative domain.
4. **VAST namespace** — using `threatmodeler.com` (the company). Confirm VAST doesn't have a separate community domain.
5. **TLP as methodology** — TLP defines a classification process, but is it primarily a methodology or a reference/convention? Duck test says methodology (you follow it to classify information), but it's borderline.
6. **Diamond Model** — deferred due to no stable publisher domain. Could potentially use `activeresponse.org` (Sergio Caltagirone's org) or file under the DTIC report reference. Revisit when relationship layer ships.
7. **Attack Trees** — deferred. The concept is widely used but has no institutional owner. Could register as `schneier.com` (personal site, best available source) in a later wave if needed.
8. **VERIS publisher** — using `verisframework.org` (project domain). Could also argue for `verizon.com` (the actual publisher). Project domain follows SecID convention of using the domain the project presents as its identity.
