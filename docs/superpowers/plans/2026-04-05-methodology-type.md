# Methodology Type Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add `methodology` as the 10th SecID type across all repos (spec, registry, service, SDK), with 3 proof-of-concept registry entries.

**Architecture:** Methodology identifies formal processes (scoring, mapping, assessment, classification). Registry entries use the same `match_nodes` tree as every other type. Enrichment metadata (use_when, compared_to, required_by) is deferred to the data layer. Three repos are touched: SecID (spec + registry), SecID-Service (API + MCP + website), SecID-Client-SDK (Python, TypeScript, Go).

**Tech Stack:** Markdown, JSON, TypeScript (Cloudflare Worker), Python, Go

**Spec:** `docs/superpowers/specs/2026-04-05-methodology-type-design.md`

**IMPORTANT:** Another AI agent is actively building out the `capability` type registry. When committing, only stage files you created or modified — do NOT use `git add -A` or `git add .`. Ignore any unstaged capability changes.

---

## Phase 1: SecID Repo — Proposal Documents

### Task 1: Create METHODOLOGY-TYPE.md proposal

**Files:**
- Create: `docs/proposals/METHODOLOGY-TYPE.md`

- [ ] **Step 1: Write the proposal document**

This is the primary rationale document. Adapt from the design spec at `docs/superpowers/specs/2026-04-05-methodology-type-design.md`, following the structure of `docs/proposals/CAPABILITY-TYPE.md`.

```markdown
# Proposal: `methodology` Type (10th SecID Type)

Status: Research / proposal
Date: 2026-04-05

## Summary

Add a 10th SecID type: `methodology` — identifying formal processes with defined inputs, steps, and outputs used to produce security analysis, scores, mappings, decisions, classifications, and reports.

## The Problem

SecID currently has 9 types. When a practitioner writes "CCM control IAM-01 maps to NIST CSF PR.AC-1," there is no machine-readable way to express *how* that mapping was established, *why* that methodology was chosen over alternatives, or *who requires* it. The mapping floats without process provenance.

This matters because the methodology chosen changes the meaning and defensibility of the output. CVSS and SSVC both produce vulnerability priorities but are not interchangeable. STRM and a simple crosswalk both produce control mappings but carry different evidentiary weight. Without a citable methodology type, AI agents and human practitioners are left to infer or ignore the process behind every security relationship assertion.

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

### Embedded Methodology: Leave It Alone

ISO 27001 contains an ISMS management process within a primarily-requirements document. Do not extract it. Create a `methodology` record that cites ISO 27001 as its normative reference. Separate records that cross-reference, not absorbing control documents into methodology entries.

## Why Not Use Existing Types?

### Why not `reference`?

Both resolve to documents. But `reference` is SecID's catch-all bucket — "documents that don't fit elsewhere." Leaving methodologies in `reference` makes the type less navigable and hides the semantic signal that this is a **process**, not a document to read.

When you see `secid:methodology/first.org/cvss@4.0`, you immediately know it's a process that produces outputs from inputs — something you *follow*, not something you *read about*. That semantic clarity in the type field is worth the cost of a 10th type.

Consumer divergence is real: a GRC analyst asking "which methodology should I use for control mapping?" is a different workflow from "give me this document."

### Why not `control`?

Controls define requirements. Methodologies define processes. A methodology may contain normative language (SHALL, MUST per RFC 2119) but its primary purpose is procedural, not prescriptive. The duck test distinguishes them cleanly.

## The Distinction

| | Control | Methodology | Reference |
|--|---------|-------------|-----------|
| **Duck test answer** | "Implement these requirements" | "Follow this process to produce an output" | "Read/cite this document" |
| **Primary purpose** | Define what must be done | Define how to systematically do it | Inform or provide evidence |
| **Output when used** | Compliance state | Score, mapping, decision, classification, report | Understanding |
| **Authority** | Standards body (prescriptive) | Process publisher (procedural) | Author (informational) |
| **Consumer question** | "What must I do?" | "How do I produce a defensible result?" | "Where can I read about this?" |

## Multi-Type Is Architecturally Necessary

SOC 2 simultaneously belongs in three types:

| Type | Entry | Actor | Use case |
|------|-------|-------|----------|
| `regulation` | `secid:regulation/aicpa.org/soc2` | Compliance team | "What must we comply with?" |
| `methodology` | `secid:methodology/aicpa.org/soc2-examination` | Auditor | "How do we scope and conduct the examination?" |
| `reference` | `secid:reference/aicpa.org/soc2-report` | Procurement | "Provide your SOC 2 report" |

## Tool Implementations of Methodologies

Tools that implement a methodology (e.g., a CVSS calculator, an IR 8477 mapping tool) are registered as `entity` type entries. The "implements" relationship belongs in the relationship layer (future).

## Identifier Format

```
secid:methodology/{namespace}/{name}[@version][#{subpath}]

secid:methodology/nist.gov/ir-8477                       # All mapping styles + selection
secid:methodology/nist.gov/ir-8477#crosswalk             # Crosswalk mapping style
secid:methodology/nist.gov/ir-8477#supportive            # Supportive relationship mapping
secid:methodology/nist.gov/ir-8477#strm                  # Set Theory Relationship Mapping
secid:methodology/nist.gov/ir-8477#structural            # Structural mapping
secid:methodology/nist.gov/ir-8477#selection             # Decision methodology for choosing
secid:methodology/first.org/cvss@4.0                     # CVSS v4.0
secid:methodology/cmu.edu/ssvc@2.0                       # SSVC v2.0
secid:methodology/iso.org/27005@2022                     # Risk assessment
```

## Registry Scope

Identity + resolution + disambiguation only. Enrichment metadata (input_types, use_when, compared_to, required_by, process_steps) is deferred to the data layer per SecID principles.

## Scale

~40-60 formally published, named process methodologies exist in information security. This is bounded and manageable.

## Why a 10th Type

The 9→10 type transition follows the same pattern as 7→8 (adding disclosure) and 8→9 (adding capability):

1. **Resolution patterns diverge** — methodology entries resolve to process documents with sub-methodology subpaths; the resolution tree structure differs from reference
2. **Consumers diverge** — GRC analysts choosing a methodology vs. researchers citing a document
3. **Semantics drift** — "follow this process" is a fundamentally different primary purpose from "read this" or "implement this"
4. **Volume** — ~40 entries is small but the entries are high-importance: they provide process provenance for the entire future relationship layer
```

- [ ] **Step 2: Verify the file parses as valid Markdown**

Run: `head -5 docs/proposals/METHODOLOGY-TYPE.md`
Expected: Shows the title and status lines.

- [ ] **Step 3: Commit**

```bash
git add docs/proposals/METHODOLOGY-TYPE.md
git commit -m "Add methodology type proposal: rationale, duck test, identifier format"
```

---

### Task 2: Create METHODOLOGY-ARCHITECTURE.md proposal

**Files:**
- Create: `docs/proposals/METHODOLOGY-ARCHITECTURE.md`

- [ ] **Step 1: Write the architecture document**

This describes how methodology fits the three-layer model. Follow the structure of `docs/proposals/CAPABILITY-ARCHITECTURE.md`.

```markdown
# Methodology Architecture: Process Provenance for Security Relationships

Status: Research / design
Date: 2026-04-05

## Core Insight

Security knowledge has a process layer that is currently invisible:

1. **What** — controls, regulations, requirements (what must be done)
2. **How (product)** — capabilities (what products can do)
3. **How (process)** — methodologies (what process was followed to produce a result)
4. **Connections** — relationships between all of the above

SecID's methodology type makes the process layer citable and machine-readable.

## The Methodology as Process Provenance

A methodology entry describes a formal process: what it takes as input, what steps it defines, and what it produces as output. It does NOT contain:

- Whether you MUST use it (that's a regulation or contractual requirement)
- Whether it's better than alternatives (that's a judgment call)
- The actual outputs it produced (that's relationship/data layer)

Example: NIST IR 8477 defines four mapping styles plus a selection methodology:

```
secid:methodology/nist.gov/ir-8477                   → The complete toolkit
secid:methodology/nist.gov/ir-8477#crosswalk         → Direct equivalence mapping
secid:methodology/nist.gov/ir-8477#supportive        → Supportive relationship mapping
secid:methodology/nist.gov/ir-8477#strm              → Set Theory Relationship Mapping
secid:methodology/nist.gov/ir-8477#structural        → Structural decomposition mapping
secid:methodology/nist.gov/ir-8477#selection         → Decision process for choosing a style
```

Each sub-methodology is independently referenceable because practitioners cite specific mapping styles, not the whole document.

## How Methodology Connects Controls to Capabilities

The methodology type completes a triangle:

```
Control (what must be done)
    ↓ "mapped_using" methodology
Capability (what a product can do)
    ↑ "assessed_using" methodology
Regulation (what the law requires)
```

When someone asserts "NIST 800-53 SC-28 is implemented by S3 Default Encryption," the methodology type lets you ask: was that mapping done via STRM (high evidentiary weight) or a simple crosswalk (low evidentiary weight)? The answer changes the defensibility of the assertion.

## The Process Provenance Chain

1. An AI agent encounters: "CCM IAM-01 supports NIST CSF PR.AC-1"
2. The assertion carries: `secid:methodology/nist.gov/ir-8477#supportive`
3. The agent resolves that identifier and retrieves: the definition of supportive relationship mapping
4. The agent can now assess the quality and context of the mapping

Without methodology, step 2 is impossible and steps 3-4 collapse.

## Methodology Categories

| Category | Examples | Count |
|----------|----------|-------|
| Mapping | IR 8477, CTID framework mapping, CSA CCM mapping | ~6 |
| Scoring/Prioritization | CVSS, SSVC, EPSS | ~3 |
| Risk Management | ISO 27005, NIST 800-30, NIST RMF, FAIR, ISO 31000 | ~5 |
| Vulnerability Management | ISO 29147, ISO 30111, NIST 800-61 | ~3 |
| Threat Modeling | STRIDE, PASTA, VAST, LINDDUN, TRIKE | ~5 |
| Security Testing | NIST 800-115, PTES, OWASP Testing Guide, OSSTMM | ~4 |
| Digital Forensics | ISO 27037, 27041, 27042, 27043, RFC 3227 | ~5 |
| Incident Management | ISO 27035, VERIS | ~2 |
| Supply Chain | NIST 800-161, SLSA | ~2 |
| Audit/Certification | ISO 27006, 27007, 17021, Common Criteria CEM | ~4 |
| **Total** | | **~40** |

This is a bounded set. New formal methodologies are published rarely (a few per year across the entire field).

## Relationship Layer Integration (Future)

When the relationship layer ships, methodology becomes the provenance qualifier:

```json
{
  "from": "secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-01",
  "to": "secid:control/nist.gov/csf@2.0#PR.AC-1",
  "relationship": "supports",
  "methodology": "secid:methodology/nist.gov/ir-8477#supportive",
  "evidence": "...",
  "producer": "secid:entity/cloudsecurityalliance.org"
}
```

Every relationship assertion becomes auditable: who made it, using what process, producing what level of evidence.

## Registry vs. Data Layer Boundary

**Registry (this repo):**
- Identity: what is this methodology, who publishes it
- Resolution: URLs to the authoritative document
- Disambiguation: subpath patterns for sub-methodologies, version_required

**Data layer (future):**
- input_types, output_type — what the methodology consumes and produces
- use_when, do_not_use_when — selection guidance
- compared_to — relationship to competing methodologies
- required_by, adopted_by — who mandates or endorses it
- process_steps — structured step descriptions

## Principles

1. **Methodologies are process descriptions.** They describe how to do something, not what must be done.
2. **The duck test is the classifier.** "Is process the primary purpose?" — not "does it contain a process?"
3. **Sub-methodologies are first-class.** IR 8477's four styles are independently referenceable.
4. **Tools implement methodologies.** A CVSS calculator is an entity that implements methodology/first.org/cvss@4.0.
5. **Embedded methodology stays embedded.** Don't extract processes from primarily-control documents.
6. **Registry stays tight.** Enrichment belongs in the data layer.
```

- [ ] **Step 2: Commit**

```bash
git add docs/proposals/METHODOLOGY-ARCHITECTURE.md
git commit -m "Add methodology architecture: process provenance and three-layer integration"
```

---

### Task 3: Create METHODOLOGY-PROCESS.md proposal

**Files:**
- Create: `docs/proposals/METHODOLOGY-PROCESS.md`

- [ ] **Step 1: Write the authoring process document**

Follow the structure of `docs/proposals/CAPABILITY-PROCESS.md`.

```markdown
# Methodology Authoring Process

How we research, document, and maintain methodology registry entries.

## Principles

1. **One file per namespace.** `registry/methodology/gov/nist.json` contains all NIST methodologies (IR 8477, RMF, 800-30, 800-61, 800-115).
2. **Follow the source's structure.** If NIST IR 8477 names four mapping styles, those become subpath match_nodes. Don't invent hierarchy the source doesn't have.
3. **Explicit "we looked and found nothing."** If a methodology has no sub-methodologies, use `children: []`. Null means researched; absent means not yet researched.
4. **The authoritative document is the source of truth.** Not blog posts, not summaries, not third-party descriptions.
5. **Verify the publisher domain.** SecID namespaces are domain names. Confirm the organization's actual domain before creating a file. SSVC is `cmu.edu` (CMU SEI/CERT/CC), not `cisa.gov` (CISA is an adopter).

## File Structure

Each namespace gets its own file:

```
registry/methodology/
├── gov/
│   ├── nist.json           # NIST: ir-8477, rmf, 800-30, 800-61, 800-115
│   └── cisa.json           # CISA: attck-mapping
├── org/
│   ├── first.json          # FIRST: cvss, epss, tlp
│   ├── iso.json            # ISO: 27005, 27035, 27037-27043, 29147, 30111, 31000, 27006, 27007, 17021
│   ├── mitre.json          # MITRE: ctid-framework-mapping, ctid-platform-mapping
│   ├── owasp.json          # OWASP: testing-guide
│   ├── opengroup.json      # The Open Group: fair
│   ├── cloudsecurityalliance.json  # CSA: ccm-mapping-methodology, incident-to-control, control-to-capability
│   ├── isecom.json         # ISECOM: osstmm
│   ├── verisframework.json # Verizon/VERIS: veris
│   └── commoncriteriaportal.json  # CCRA: cem
├── edu/
│   └── cmu.json            # CMU SEI/CERT/CC: ssvc
├── dev/
│   └── slsa.json           # OpenSSF: slsa
└── com/
    ├── microsoft.json      # Microsoft: stride
    ├── versprite.json      # VerSprite: pasta
    ├── threatmodeler.json  # ThreatModeler: vast
    └── pentest-standard.json  # PTES community: ptes (pentest-standard.org → com/pentest-standard.json)
```

## JSON Structure Per Namespace

```json
{
  "schema_version": "1.0",
  "namespace": "nist.gov",
  "type": "methodology",
  "status": "draft",
  "status_notes": "Initial research from NIST publication. Reviewed 2026-04-05.",

  "official_name": "National Institute of Standards and Technology",
  "urls": [
    {"type": "website", "url": "https://www.nist.gov/"}
  ],

  "match_nodes": [
    {
      "patterns": ["(?i)^ir-8477$"],
      "description": "NIST IR 8477: Mapping Relationships Between Documentary Standards, Regulations, Frameworks, and Guidelines",
      "weight": 100,
      "data": {
        "url": "https://csrc.nist.gov/pubs/ir/8477/final",
        "examples": ["ir-8477"]
      },
      "children": [
        {
          "patterns": ["(?i)^crosswalk$"],
          "description": "Crosswalk mapping: direct equivalence between elements from two documents",
          "weight": 100,
          "data": {
            "url": "https://csrc.nist.gov/pubs/ir/8477/final",
            "examples": [
              {"input": "crosswalk", "url": "https://csrc.nist.gov/pubs/ir/8477/final", "note": "Section describing crosswalk methodology"}
            ]
          }
        }
      ]
    }
  ]
}
```

## Research Process Per Methodology

### Pass 1: Identify and Verify (15 minutes)

1. Confirm the methodology is formally published (not just a blog concept)
2. Verify the publisher and their authoritative domain
3. Find the canonical URL for the methodology document
4. Identify if it has sub-methodologies (named components, steps, or metric groups)

### Pass 2: Document Structure (15 minutes)

1. Read the methodology document's table of contents / structure
2. Identify sub-components that should be independently referenceable (subpath match_nodes)
3. For versioned methodologies, check if `version_required` applies (do versions change the process materially?)
4. Note the canonical name the source uses

### Pass 3: Build Registry Entry (15 minutes)

1. Create the JSON entry following the schema above
2. Write match_node patterns (usually case-insensitive literal matches)
3. Write descriptions that explain what the methodology/sub-methodology does
4. Add resolution URLs
5. Add examples (bare strings at source level, ExampleObject at child level)

### Pass 4: Review (5 minutes)

1. Validate JSON parses: `python3 -c "import json; json.load(open('file.json'))"`
2. Check regex patterns are anchored (`^...$`)
3. Verify URLs are accessible
4. Confirm namespace matches filesystem path (reverse-DNS algorithm)

## Status Values

| Status | Meaning |
|--------|---------|
| `draft` | Entry created, needs review |
| `published` | Reviewed and verified against current source document |
| `needs-update` | Source has published a new version not yet reflected |

## Wave Plan

| Wave | Entries | Focus |
|------|---------|-------|
| 1 | IR 8477, CVSS, SSVC, CISA ATT&CK mapping, ISO 27005 | Validate pattern with high-priority standards |
| 2 | EPSS, ISO 29147, ISO 30111, NIST 800-61, ISO 27035, VERIS | Vulnerability & incident management |
| 3 | NIST 800-30, NIST RMF, FAIR, ISO 31000, NIST 800-115, CEM | Risk & assessment |
| 4 | STRIDE, PASTA, VAST, LINDDUN, TRIKE | Threat modeling |
| 5 | CSA CCM mapping, CTID, ISO forensics, TLP, SLSA, PTES, OWASP, OSSTMM, audit standards | Everything else |
| 6 | CSA incident-to-control, CSA control-to-capability | CSA draft methodologies (claim namespace) |
```

- [ ] **Step 2: Commit**

```bash
git add docs/proposals/METHODOLOGY-PROCESS.md
git commit -m "Add methodology authoring process: research workflow, JSON structure, wave plan"
```

---

### Task 4: Create METHODOLOGY-TYPE-IMPLEMENTATION-PLAN.md proposal

**Files:**
- Create: `docs/proposals/METHODOLOGY-TYPE-IMPLEMENTATION-PLAN.md`

- [ ] **Step 1: Write the implementation plan document**

Follow the structure of `docs/proposals/CAPABILITY-TYPE-IMPLEMENTATION-PLAN.md`.

```markdown
# Methodology Type Implementation Plan

Implements the `methodology` type as the 10th SecID type.

## Repos Affected

| Repo | Changes |
|------|---------|
| **SecID** (spec + registry) | SPEC.md, type definition, registry template, CLAUDE.md, README.md, DESIGN-DECISIONS.md, type-level JSON, POC entries |
| **SecID-Service** | SECID_TYPES, MCP descriptions, website, KV upload, deploy |
| **SecID-Client-SDK** | Python, TypeScript, Go — type lists, docs, examples |

## Phase 1: Spec + Registry (SecID repo)

### 1.1 Update SPEC.md
- Change "nine types" to "ten types" (line 387 and elsewhere)
- Add `methodology` to type list table (after `capability`, before `disclosure`)
- Add `methodology` to every enumeration of types (lines 51, 242, 350, 1142)
- Add methodology examples to format examples section

### 1.2 Create type definition files
- `registry/methodology.md` — type description
- `registry/methodology.json` — type-level JSON metadata
- `registry/methodology/_template.md` — template for new namespace files

### 1.3 Update documentation
- CLAUDE.md — add methodology to type table, update type count references
- README.md — add methodology to type table, update counts, add examples
- DESIGN-DECISIONS.md — add methodology case study to "Type Evolution" section (9→10 split)

### 1.4 Update counts
- Run `./scripts/update-counts.sh`

### 1.5 Initial proof-of-concept entries
- `registry/methodology/gov/nist.json` — IR 8477 with 5 sub-methodologies
- `registry/methodology/org/first.json` — CVSS v4.0
- `registry/methodology/edu/cmu.json` — SSVC v2.0

## Phase 2: Service Update (SecID-Service repo)

### 2.1 Add methodology to SECID_TYPES
- `src/types.ts` — add `"methodology"` to SECID_TYPES array

### 2.2 Update MCP tool descriptions
- `src/mcp.ts` — add methodology section to resolve tool description
- Add methodology examples to lookup tool description
- Update type list strings everywhere (9→10, add "methodology")
- Update describe tool's registry resource description

### 2.3 Update website
- `website/src/pages/index.astro` — change "Nine Types" to "Ten Types", add methodology card
- `website/src/components/Resolver.astro` — add methodology to TYPE_DESCRIPTIONS

### 2.4 Upload and deploy
- Re-upload KV with methodology type data
- Deploy worker

## Phase 3: Client SDK Update (SecID-Client-SDK repo)

### 3.1 Python SDK
- `python/secid_client.py` — update lookup() type docstring to include `methodology`
- `python/README.md` — add methodology example and type table row

### 3.2 TypeScript SDK
- `typescript/src/secid-client.ts` — update lookup() type docstring
- `typescript/README.md` — add methodology example and type table row

### 3.3 Go SDK
- `go/secid.go` — update Lookup() type documentation

## Phase 4: Registry Population (future)

Waves 1-6 as defined in METHODOLOGY-PROCESS.md. ~41 entries across 6 waves.

## Execution Order

1. **SecID repo first** — spec changes, proposal docs, registry files, doc updates
2. **SecID-Service second** — type recognition, MCP descriptions, website, deploy
3. **SecID-Client-SDK third** — SDK updates reference the live service
4. **Registry population fourth** — POC first, then waves 2-6
```

- [ ] **Step 2: Commit**

```bash
git add docs/proposals/METHODOLOGY-TYPE-IMPLEMENTATION-PLAN.md
git commit -m "Add methodology type implementation plan: phased rollout across 3 repos"
```

---

## Phase 2: SecID Repo — Type Infrastructure

### Task 5: Create registry/methodology.md type description

**Files:**
- Create: `registry/methodology.md`
- Reference: `registry/capability.md` for structure

- [ ] **Step 1: Write the type description**

```markdown
# Methodology Type (`methodology`)

Identifiers for **formal processes with defined inputs, steps, and outputs** — the named, published methodologies used to produce security analysis, scores, mappings, decisions, classifications, and reports.

## Purpose

Track and reference the processes used to produce security knowledge:

**Mapping Methodologies:**
- NIST IR 8477 (crosswalk, supportive, STRM, structural + selection)
- CTID Control Framework → ATT&CK mapping
- CSA CCM mapping methodology

**Scoring and Prioritization:**
- CVSS v4.0 (vulnerability severity scoring)
- SSVC v2.0 (stakeholder-specific vulnerability categorization)
- EPSS (exploit prediction scoring)

**Risk and Assessment:**
- ISO 27005 (information security risk assessment)
- NIST RMF / SP 800-37 (risk management framework)
- FAIR (Factor Analysis of Information Risk)

**Threat Modeling:**
- STRIDE, PASTA, VAST, LINDDUN, TRIKE

## Why Methodology Is Separate from Control and Reference

| | Control | Methodology | Reference |
|--|---------|-------------|-----------|
| **Duck test** | "Implement these requirements" | "Follow this process to produce an output" | "Read/cite this document" |
| **Primary purpose** | Define what must be done | Define how to systematically do it | Inform or provide evidence |
| **Output when used** | Compliance state | Score, mapping, decision, classification, report | Understanding |
| **Authority** | Standards body (prescriptive) | Process publisher (procedural) | Author (informational) |
| **Consumer question** | "What must I do?" | "How do I produce a defensible result?" | "Where can I read about this?" |

**Classification criterion ("duck test"):** "If someone hands you this document and asks 'what do I DO with it?' — is the primary answer 'follow this process to produce an output'?" If yes, it's a methodology.

## Identifier Format

```
secid:methodology/<namespace>/<name>[@version][#<subpath>]

secid:methodology/nist.gov/ir-8477                       # All mapping styles
secid:methodology/nist.gov/ir-8477#strm                  # STRM specifically
secid:methodology/first.org/cvss@4.0                     # CVSS v4.0
secid:methodology/cmu.edu/ssvc@2.0                       # SSVC v2.0
secid:methodology/iso.org/27005@2022                     # Risk assessment
secid:methodology/microsoft.com/stride                   # STRIDE threat modeling
```

## Namespaces

| Namespace | Methodologies | Description |
|-----------|---------------|-------------|
| `nist.gov` | ir-8477, rmf, 800-30, 800-61, 800-115, 800-161 | NIST process standards |
| `first.org` | cvss, epss, tlp | FIRST scoring and classification |
| `cmu.edu` | ssvc | CMU SEI/CERT/CC prioritization |
| `iso.org` | 27005, 27035, 29147, 30111, 31000, 27037-27043, 27006, 27007, 17021 | ISO process standards |
| `cisa.gov` | attck-mapping | CISA mapping best practices |
| `microsoft.com` | stride | STRIDE threat modeling |

## Relationships

Methodologies connect to controls and capabilities as process provenance:

```json
{
  "from": "secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-01",
  "to": "secid:control/nist.gov/csf@2.0#PR.AC-1",
  "relationship": "supports",
  "methodology": "secid:methodology/nist.gov/ir-8477#supportive"
}
```

## Notes

- Methodology is the smallest SecID type by volume (~40-60 entries) but high importance: provides process provenance for the relationship layer
- Sub-methodologies are first-class referenceable entities via subpath
- Tools that implement methodologies (CVSS calculators, mapping tools) go in `entity` type; the "implements" relationship is relationship-layer data
- Documents that contain embedded methodology alongside primarily-control content stay in their original type; create a separate `methodology` record that cites the parent
```

- [ ] **Step 2: Commit**

```bash
git add registry/methodology.md
git commit -m "Add methodology type description"
```

---

### Task 6: Create registry/methodology.json type-level metadata

**Files:**
- Create: `registry/methodology.json`
- Reference: `registry/capability.json` for structure

- [ ] **Step 1: Write the type-level JSON**

```json
{
  "schema_version": "1.0",
  "type": "methodology",
  "official_name": "Methodology",
  "description": "Formal processes with defined inputs, steps, and outputs — named, published methodologies for producing security analysis, scores, mappings, decisions, classifications, and reports.",
  "purpose": "Track and reference the processes used to produce security knowledge. Each methodology defines how to systematically produce a specific type of output (score, mapping, decision, classification, report). Sub-methodologies are independently referenceable via subpath.",
  "format": "secid:methodology/<namespace>/<name>[@version][#<subpath>]",
  "examples": [
    "secid:methodology/nist.gov/ir-8477",
    "secid:methodology/nist.gov/ir-8477#strm",
    "secid:methodology/first.org/cvss@4.0",
    "secid:methodology/cmu.edu/ssvc@2.0",
    "secid:methodology/iso.org/27005@2022"
  ],
  "notes": "The methodology type is the smallest by volume (~40-60 entries) but provides critical process provenance for the relationship layer. Classification criterion: 'Is process the primary purpose of this document?' (the duck test). Tools implementing methodologies go in entity type.",
  "namespace_count": 0,
  "namespaces": []
}
```

- [ ] **Step 2: Validate JSON**

Run: `python3 -c "import json; json.load(open('registry/methodology.json'))"`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add registry/methodology.json
git commit -m "Add methodology type-level JSON metadata"
```

---

### Task 7: Create registry/methodology/_template.md

**Files:**
- Create: `registry/methodology/_template.md`
- Reference: `registry/capability/_template.md` for structure

- [ ] **Step 1: Create the directory and template**

```bash
mkdir -p registry/methodology
```

Write `registry/methodology/_template.md`:

```markdown
---
# Identity
namespace: ""
full_name: ""
type: methodology

# Access
urls:
  website: ""
  document: ""  # URL to the authoritative methodology document

# Methodology
methodology_name: ""  # e.g., "CVSS", "STRM", "STRIDE"
publisher: ""  # e.g., "FIRST", "NIST", "Microsoft"

# Pattern
id_pattern: ""  # Regex for methodology/sub-methodology IDs

# Examples
examples: []

status: draft  # draft, published, needs-update
---

# [Methodology Name]

[Brief description of what the methodology is and what output it produces]

## Sub-Methodologies

[Named sub-components that are independently referenceable, if any]

## Versioning

[How versions work for this methodology, if applicable]

## Notes

[Publisher attribution, adoption context, etc.]
```

- [ ] **Step 2: Commit**

```bash
git add registry/methodology/_template.md
git commit -m "Add methodology namespace template"
```

---

### Task 8: Create proof-of-concept entry — NIST IR 8477

**Files:**
- Create: `registry/methodology/gov/nist.json`

This is the most important POC entry — IR 8477 with 5 sub-methodologies demonstrates the subpath pattern.

- [ ] **Step 1: Create the directory structure**

```bash
mkdir -p registry/methodology/gov
```

- [ ] **Step 2: Research IR 8477 and write the registry entry**

Read the IR 8477 publication at `https://csrc.nist.gov/pubs/ir/8477/final` to get the exact names, descriptions, and structure of the four mapping styles and the selection methodology. Write `registry/methodology/gov/nist.json`:

```json
{
  "schema_version": "1.0",
  "namespace": "nist.gov",
  "type": "methodology",
  "status": "draft",
  "status_notes": "Initial entry from NIST IR 8477 publication. Reviewed 2026-04-05.",

  "official_name": "National Institute of Standards and Technology",
  "urls": [
    {"type": "website", "url": "https://www.nist.gov/"},
    {"type": "docs", "url": "https://csrc.nist.gov/", "note": "NIST Computer Security Resource Center"}
  ],

  "match_nodes": [
    {
      "patterns": ["(?i)^ir-8477$"],
      "description": "NIST IR 8477: Mapping Relationships Between Documentary Standards, Regulations, Frameworks, and Guidelines. Defines four mapping styles (crosswalk, supportive, STRM, structural) plus a selection methodology for choosing among them.",
      "weight": 100,
      "data": {
        "url": "https://csrc.nist.gov/pubs/ir/8477/final",
        "examples": ["ir-8477"]
      },
      "children": [
        {
          "patterns": ["(?i)^crosswalk$"],
          "description": "Crosswalk mapping: identifies direct equivalence or near-equivalence between elements from two documents. Produces a table of element-to-element correspondences. Simplest mapping style with lowest evidentiary weight.",
          "weight": 100,
          "data": {
            "url": "https://csrc.nist.gov/pubs/ir/8477/final",
            "examples": [
              {"input": "crosswalk", "url": "https://csrc.nist.gov/pubs/ir/8477/final", "note": "Crosswalk mapping methodology defined in IR 8477"}
            ]
          }
        },
        {
          "patterns": ["(?i)^supportive$"],
          "description": "Supportive relationship mapping: identifies elements that support or contribute to the objectives of elements in another document, without requiring direct equivalence. Captures partial and indirect relationships.",
          "weight": 100,
          "data": {
            "url": "https://csrc.nist.gov/pubs/ir/8477/final",
            "examples": [
              {"input": "supportive", "url": "https://csrc.nist.gov/pubs/ir/8477/final", "note": "Supportive relationship mapping methodology defined in IR 8477"}
            ]
          }
        },
        {
          "patterns": ["(?i)^strm$"],
          "description": "Set Theory Relationship Mapping (STRM): uses set theory notation to express precise mathematical relationships (subset, superset, intersection, disjoint) between document elements. Highest evidentiary weight among IR 8477 mapping styles.",
          "weight": 100,
          "data": {
            "url": "https://csrc.nist.gov/pubs/ir/8477/final",
            "examples": [
              {"input": "strm", "url": "https://csrc.nist.gov/pubs/ir/8477/final", "note": "Set Theory Relationship Mapping (STRM) methodology defined in IR 8477"}
            ]
          }
        },
        {
          "patterns": ["(?i)^structural$"],
          "description": "Structural mapping: analyzes the organizational structure and hierarchy of documents to identify structural parallels and alignment between frameworks.",
          "weight": 100,
          "data": {
            "url": "https://csrc.nist.gov/pubs/ir/8477/final",
            "examples": [
              {"input": "structural", "url": "https://csrc.nist.gov/pubs/ir/8477/final", "note": "Structural mapping methodology defined in IR 8477"}
            ]
          }
        },
        {
          "patterns": ["(?i)^selection$"],
          "description": "Selection methodology: decision process for choosing which mapping style(s) to apply based on the purpose of the mapping, the nature of the documents, and the intended use of the results.",
          "weight": 100,
          "data": {
            "url": "https://csrc.nist.gov/pubs/ir/8477/final",
            "examples": [
              {"input": "selection", "url": "https://csrc.nist.gov/pubs/ir/8477/final", "note": "Selection methodology for choosing mapping style(s)"}
            ]
          }
        }
      ]
    },
    {
      "patterns": ["(?i)^rmf$", "(?i)^800-37$"],
      "description": "NIST Risk Management Framework (SP 800-37): seven-step process for managing security and privacy risk — prepare, categorize, select, implement, assess, authorize, monitor.",
      "weight": 100,
      "data": {
        "url": "https://csrc.nist.gov/projects/risk-management/about-rmf",
        "examples": ["rmf", "800-37"]
      }
    },
    {
      "patterns": ["(?i)^800-30$"],
      "description": "NIST SP 800-30: Guide for Conducting Risk Assessments. Methodology for identifying, estimating, and prioritizing information security risks.",
      "weight": 100,
      "data": {
        "url": "https://csrc.nist.gov/pubs/sp/800/30/r1/final",
        "examples": ["800-30"]
      }
    },
    {
      "patterns": ["(?i)^800-61$"],
      "description": "NIST SP 800-61: Incident Handling Guide. Methodology for detecting, analyzing, containing, eradicating, and recovering from computer security incidents.",
      "weight": 100,
      "data": {
        "url": "https://csrc.nist.gov/pubs/sp/800/61/r3/final",
        "examples": ["800-61"]
      }
    },
    {
      "patterns": ["(?i)^800-115$"],
      "description": "NIST SP 800-115: Technical Guide to Information Security Testing and Assessment. Methodology for planning, conducting, and analyzing security testing.",
      "weight": 100,
      "data": {
        "url": "https://csrc.nist.gov/pubs/sp/800/115/final",
        "examples": ["800-115"]
      }
    },
    {
      "patterns": ["(?i)^800-161$"],
      "description": "NIST SP 800-161: Cybersecurity Supply Chain Risk Management (C-SCRM) Practices. Methodology for identifying, assessing, and mitigating supply chain risks.",
      "weight": 100,
      "data": {
        "url": "https://csrc.nist.gov/pubs/sp/800/161/r1/final",
        "examples": ["800-161"]
      }
    }
  ]
}
```

- [ ] **Step 3: Validate JSON**

Run: `python3 -c "import json; json.load(open('registry/methodology/gov/nist.json'))"`
Expected: No output (success)

- [ ] **Step 4: Commit**

```bash
git add registry/methodology/gov/nist.json
git commit -m "Add NIST methodology namespace: IR 8477 (5 sub-methodologies), RMF, 800-30, 800-61, 800-115, 800-161"
```

---

### Task 9: Create proof-of-concept entry — FIRST (CVSS)

**Files:**
- Create: `registry/methodology/org/first.json`

- [ ] **Step 1: Create directory and write entry**

```bash
mkdir -p registry/methodology/org
```

Write `registry/methodology/org/first.json`:

```json
{
  "schema_version": "1.0",
  "namespace": "first.org",
  "type": "methodology",
  "status": "draft",
  "status_notes": "Initial entry. Reviewed 2026-04-05.",

  "official_name": "Forum of Incident Response and Security Teams",
  "urls": [
    {"type": "website", "url": "https://www.first.org/"}
  ],

  "match_nodes": [
    {
      "patterns": ["(?i)^cvss$"],
      "description": "Common Vulnerability Scoring System (CVSS): methodology for scoring the severity of software vulnerabilities. Produces a numerical score (0.0-10.0) and severity rating from a set of metrics.",
      "weight": 100,
      "version_required": true,
      "version_disambiguation": "CVSS versions differ materially in metric groups and scoring algorithms. v3.1 and v4.0 produce different scores for the same vulnerability. Always specify version.",
      "data": {
        "url": "https://www.first.org/cvss/",
        "examples": ["cvss"]
      },
      "children": [
        {
          "patterns": ["^4\\.0$"],
          "description": "CVSS v4.0: released 2023. Adds Supplemental metric group, refines Temporal into Threat, adds granularity to Environmental metrics.",
          "weight": 100,
          "data": {
            "url": "https://www.first.org/cvss/v4.0/specification-document",
            "examples": [
              {"input": "4.0", "url": "https://www.first.org/cvss/v4.0/specification-document", "note": "CVSS v4.0 specification"}
            ]
          }
        },
        {
          "patterns": ["^3\\.1$"],
          "description": "CVSS v3.1: released 2019. Widely adopted. Base, Temporal, and Environmental metric groups.",
          "weight": 90,
          "data": {
            "url": "https://www.first.org/cvss/v3.1/specification-document",
            "examples": [
              {"input": "3.1", "url": "https://www.first.org/cvss/v3.1/specification-document", "note": "CVSS v3.1 specification"}
            ]
          }
        }
      ]
    },
    {
      "patterns": ["(?i)^epss$"],
      "description": "Exploit Prediction Scoring System (EPSS): data-driven methodology for estimating the probability that a software vulnerability will be exploited in the wild within 30 days.",
      "weight": 100,
      "data": {
        "url": "https://www.first.org/epss/",
        "examples": ["epss"]
      }
    },
    {
      "patterns": ["(?i)^tlp$"],
      "description": "Traffic Light Protocol (TLP): information sharing classification methodology. Defines four levels (RED, AMBER+STRICT, AMBER, GREEN, CLEAR) for marking sensitivity of shared information.",
      "weight": 100,
      "data": {
        "url": "https://www.first.org/tlp/",
        "examples": ["tlp"]
      }
    }
  ]
}
```

- [ ] **Step 2: Validate JSON**

Run: `python3 -c "import json; json.load(open('registry/methodology/org/first.json'))"`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add registry/methodology/org/first.json
git commit -m "Add FIRST methodology namespace: CVSS (v3.1, v4.0), EPSS, TLP"
```

---

### Task 10: Create proof-of-concept entry — CMU SSVC

**Files:**
- Create: `registry/methodology/edu/cmu.json`

- [ ] **Step 1: Create directory and write entry**

```bash
mkdir -p registry/methodology/edu
```

Write `registry/methodology/edu/cmu.json`:

```json
{
  "schema_version": "1.0",
  "namespace": "cmu.edu",
  "type": "methodology",
  "status": "draft",
  "status_notes": "Initial entry from CERT/CC SSVC documentation. Reviewed 2026-04-05.",

  "official_name": "Carnegie Mellon University Software Engineering Institute",
  "urls": [
    {"type": "website", "url": "https://www.sei.cmu.edu/"},
    {"type": "docs", "url": "https://certcc.github.io/SSVC/", "note": "SSVC documentation"}
  ],

  "match_nodes": [
    {
      "patterns": ["(?i)^ssvc$"],
      "description": "Stakeholder-Specific Vulnerability Categorization (SSVC): decision-tree methodology for prioritizing vulnerability response based on stakeholder context. Developed by CERT/CC at CMU SEI. Produces prioritization decisions (defer, scheduled, out-of-cycle, immediate) rather than numerical scores.",
      "weight": 100,
      "version_required": true,
      "version_disambiguation": "SSVC versions change the decision tree structure. CISA has published a customized SSVC decision tree for their context (see secid:methodology/cisa.gov/ssvc-decision-tree if registered).",
      "data": {
        "url": "https://certcc.github.io/SSVC/",
        "examples": ["ssvc"]
      },
      "children": [
        {
          "patterns": ["^2\\.0$"],
          "description": "SSVC v2.0: current version with refined decision points and stakeholder roles.",
          "weight": 100,
          "data": {
            "url": "https://certcc.github.io/SSVC/",
            "examples": [
              {"input": "2.0", "url": "https://certcc.github.io/SSVC/", "note": "SSVC v2.0 documentation"}
            ]
          }
        }
      ]
    }
  ]
}
```

- [ ] **Step 2: Validate JSON**

Run: `python3 -c "import json; json.load(open('registry/methodology/edu/cmu.json'))"`
Expected: No output (success)

- [ ] **Step 3: Commit**

```bash
git add registry/methodology/edu/cmu.json
git commit -m "Add CMU SEI/CERT/CC methodology namespace: SSVC v2.0"
```

---

## Phase 3: SecID Repo — Documentation Updates

### Task 11: Update SPEC.md

**Files:**
- Modify: `SPEC.md` (lines 51, 242, 350, 387, 389-398, 1142)

- [ ] **Step 1: Update all type references from 9 to 10**

Every occurrence of "nine types" or the type enumeration list needs `methodology` added. There are 5 locations:

1. **Line 51** — component table type description: add `, methodology` after `capability`
2. **Line 242** — type list sentence: add `, methodology` after `capability`
3. **Line 350** — parsing table type row: add `, methodology` after `capability`
4. **Line 387** — "SecID defines nine types" → "SecID defines ten types"
5. **Lines 389-398** — type table: add methodology row after capability
6. **Line 1142** — parser matching: add `, methodology` after `capability`

For the type table (lines 389-398), add this row after `capability`:

```markdown
| `methodology` | Formal processes for producing security analysis | "How do I produce a defensible result?" |
```

- [ ] **Step 2: Verify the changes**

Run: `grep -n 'methodology' SPEC.md | head -10`
Expected: Shows methodology in all updated locations

- [ ] **Step 3: Commit**

```bash
git add SPEC.md
git commit -m "Add methodology as 10th type in SPEC.md"
```

---

### Task 12: Update CLAUDE.md

**Files:**
- Modify: `CLAUDE.md`

- [ ] **Step 1: Update type table**

In the "SecID Types" section, add methodology row after `capability`:

```markdown
| `methodology` | Formal processes for producing security analysis, scores, mappings, decisions (CVSS, SSVC, IR 8477, STRIDE) |
```

- [ ] **Step 2: Update type count references**

Change "9" to "10" in:
- "Fixed list of 9 values" → "Fixed list of 10 values" (Parsing Rules table)
- Any other count references

- [ ] **Step 3: Add methodology to Document Map**

In the Document Map table, add:
```markdown
| How do I add a methodology? | [METHODOLOGY-PROCESS.md](docs/proposals/METHODOLOGY-PROCESS.md) |
```

- [ ] **Step 4: Update type enumeration in Adding New Namespaces**

Step 1 currently lists 9 types. Add `methodology` to the list.

- [ ] **Step 5: Run update-counts.sh**

Run: `./scripts/update-counts.sh`
Expected: Updates counts in CLAUDE.md and README.md

- [ ] **Step 6: Commit**

```bash
git add CLAUDE.md
git commit -m "Add methodology type to CLAUDE.md"
```

---

### Task 13: Update README.md

**Files:**
- Modify: `README.md`

- [ ] **Step 1: Update type table**

Add methodology row to the Types table:

```markdown
| `methodology` | Formal processes for producing security analysis |
```

- [ ] **Step 2: Add methodology examples**

In the "Identifier Format" examples section, add:

```
secid:methodology/nist.gov/ir-8477#strm                  # NIST mapping methodology
secid:methodology/first.org/cvss@4.0                     # CVSS vulnerability scoring
```

- [ ] **Step 3: Update PURL mapping table**

Add methodology to the type component description.

- [ ] **Step 4: Update any "nine types" or "9 types" text**

Search for "nine" and "9 type" throughout README.md and update to "ten" / "10 types".

- [ ] **Step 5: Commit**

```bash
git add README.md
git commit -m "Add methodology type to README.md"
```

---

### Task 14: Update DESIGN-DECISIONS.md

**Files:**
- Modify: `docs/explanation/DESIGN-DECISIONS.md`

- [ ] **Step 1: Add methodology case study to Type Evolution section**

After the "Case Study: The `disclosure` Split" section (around line 209), add:

```markdown
### Case Study: The `methodology` Split

The `methodology` type is the third type added after the original seven (following `disclosure` at 8 and `capability` at 9). It was created because all four "When to Split" criteria were met:

1. **Resolution patterns diverge** — Methodology entries resolve to process documents with sub-methodology subpaths (e.g., `#strm`, `#crosswalk`). The resolution tree structure supports independently referenceable sub-processes. Reference entries resolve to documents without this process-component subpath convention.

2. **Consumers diverge** — A GRC analyst asking "which methodology should I use for control mapping?" is a different workflow from a researcher citing a document. Methodology consumers need to discover, compare, and select processes — not just retrieve documents.

3. **Semantics drift** — "Follow this process to produce an output" is a fundamentally different primary purpose from "read this document" or "implement this requirement." The **duck test** — "if someone hands you this document and asks 'what do I DO with it?', is the primary answer 'follow this process'?" — cleanly separates methodologies from references and controls.

4. **Volume** — ~40-60 formally published named methodologies is small but the entries are architecturally critical: they provide process provenance for the entire future relationship layer. Without citable methodology identifiers, every relationship assertion in SecID is ungrounded.

**Additional factor: process provenance.** When the relationship layer ships, every assertion ("CCM IAM-01 maps to NIST CSF PR.AC-1") will carry a methodology reference explaining how the mapping was produced and what evidentiary weight it carries. This is the foundational use case that no existing type can serve.
```

- [ ] **Step 2: Commit**

```bash
git add docs/explanation/DESIGN-DECISIONS.md
git commit -m "Add methodology case study to type evolution in DESIGN-DECISIONS.md"
```

---

## Phase 4: SecID-Service Repo

> **Note:** Tasks 15-17 are in the `CloudSecurityAlliance/SecID-Service` repo, NOT the SecID repo. Change to that directory before starting.

### Task 15: Add methodology to SECID_TYPES

**Files:**
- Modify: `src/types.ts` (SecID-Service repo)

- [ ] **Step 1: Add methodology to the types array**

In `src/types.ts`, add `"methodology"` to the `SECID_TYPES` array. Place it after `"capability"` and before `"disclosure"` to maintain alphabetical-ish ordering consistent with the spec:

```typescript
export const SECID_TYPES = [
  "advisory",
  "weakness",
  "ttp",
  "control",
  "capability",
  "methodology",
  "disclosure",
  "regulation",
  "entity",
  "reference",
] as const;
```

The `SecIDType` type is derived from `SECID_TYPES` automatically, so no other type changes needed.

- [ ] **Step 2: Commit**

```bash
git add src/types.ts
git commit -m "Add methodology to SECID_TYPES"
```

---

### Task 16: Update MCP tool descriptions

**Files:**
- Modify: `src/mcp.ts` (SecID-Service repo)

- [ ] **Step 1: Add methodology section to resolve tool description**

Find the capability section in the resolve tool description (around line 277) and add after it:

```
  The methodology type identifies formal processes for producing security analysis:
    secid:methodology/nist.gov/ir-8477           → NIST mapping methodology (4 styles + selection)
    secid:methodology/nist.gov/ir-8477#strm      → Set Theory Relationship Mapping specifically
    secid:methodology/first.org/cvss@4.0         → CVSS v4.0 vulnerability scoring
    secid:methodology/cmu.edu/ssvc@2.0           → SSVC stakeholder-specific prioritization
```

- [ ] **Step 2: Update type list strings**

Update all hardcoded type list strings in `src/mcp.ts` to include `methodology`. Search for:
- `"advisory, weakness, ttp, control, capability, disclosure"` — add `methodology` after `capability`
- `"9 types"` or `"nine types"` — change to `"10 types"` / `"ten types"`
- The describe tool's registry resource description (around line 520)
- The lookup tool's type enum description (around line 418)

- [ ] **Step 3: Add methodology to TYPE_DESCRIPTIONS in website**

In `website/src/components/Resolver.astro` (around line 383), add to the `TYPE_DESCRIPTIONS` object:

```typescript
methodology: "Formal processes — scoring (CVSS, SSVC), mapping (IR 8477), risk assessment (ISO 27005), threat modeling (STRIDE)",
```

- [ ] **Step 4: Update website index page**

In `website/src/pages/index.astro` (around line 84), change "Nine Types" to "Ten Types" and add a methodology card.

- [ ] **Step 5: Commit**

```bash
git add src/mcp.ts website/src/components/Resolver.astro website/src/pages/index.astro
git commit -m "Add methodology to MCP tool descriptions and website"
```

---

### Task 17: Deploy SecID-Service

- [ ] **Step 1: Re-upload KV registry data**

The registry data upload happens automatically when JSON files are pushed to the SecID repo's main branch. After merging the SecID repo changes, the GitHub Actions workflow triggers SecID-Service to re-upload. Verify the workflow ran:

Run: `gh run list --repo CloudSecurityAlliance/SecID-Service --limit 3`

- [ ] **Step 2: Deploy the worker**

Run: `npx wrangler deploy`
Expected: Successful deployment

- [ ] **Step 3: Verify methodology type works**

Run: `curl -s "https://secid.cloudsecurityalliance.org/resolve?secid=secid:methodology/nist.gov/ir-8477" | python3 -m json.tool | head -20`
Expected: Returns IR 8477 resolution data

- [ ] **Step 4: Commit (if any deployment config changes needed)**

```bash
git add -A && git commit -m "Deploy with methodology type support"
```

---

## Phase 5: SecID-Client-SDK Repo

> **Note:** Tasks 18-20 are in the `CloudSecurityAlliance/SecID-Client-SDK` repo.

### Task 18: Update Python SDK

**Files:**
- Modify: `python/secid_client.py`
- Modify: `python/README.md`

- [ ] **Step 1: Update type docstring in secid_client.py**

Find the `lookup()` method (around line 154) and update the type parameter docstring:

```python
            type: SecID type (advisory, weakness, ttp, control, capability, methodology, disclosure, regulation, entity, reference).
```

- [ ] **Step 2: Update Python README.md**

Add methodology to the type table:

```markdown
| `methodology` | Formal processes for producing security analysis |
```

Add a methodology example:

```python
# Look up a scoring methodology
response = client.resolve("secid:methodology/first.org/cvss@4.0")
```

- [ ] **Step 3: Commit**

```bash
git add python/secid_client.py python/README.md
git commit -m "Add methodology type to Python SDK"
```

---

### Task 19: Update TypeScript SDK

**Files:**
- Modify: `typescript/src/secid-client.ts`
- Modify: `typescript/README.md`

- [ ] **Step 1: Update type docstring in secid-client.ts**

Find the `lookup()` method (around line 211) and update:

```typescript
   * @param type - SecID type (advisory, weakness, ttp, control, capability, methodology, disclosure, regulation, entity, reference).
```

- [ ] **Step 2: Update TypeScript README.md**

Add methodology to the type table and add example:

```typescript
// Look up a scoring methodology
const cvss = await client.resolve("secid:methodology/first.org/cvss@4.0");
```

- [ ] **Step 3: Commit**

```bash
git add typescript/src/secid-client.ts typescript/README.md
git commit -m "Add methodology type to TypeScript SDK"
```

---

### Task 20: Update Go SDK

**Files:**
- Modify: `go/secid.go`

- [ ] **Step 1: Update type documentation in secid.go**

Find the `Lookup()` function (around line 167) and update:

```go
// typ is a SecID type (advisory, weakness, ttp, control, capability, methodology, disclosure, regulation, entity, reference).
```

- [ ] **Step 2: Commit**

```bash
git add go/secid.go
git commit -m "Add methodology type to Go SDK"
```

---

## Summary

| Phase | Tasks | Repo | What |
|-------|-------|------|------|
| 1 | 1-4 | SecID | Proposal documents (4 docs) |
| 2 | 5-10 | SecID | Type infrastructure + 3 POC entries |
| 3 | 11-14 | SecID | SPEC.md, CLAUDE.md, README.md, DESIGN-DECISIONS.md updates |
| 4 | 15-17 | SecID-Service | SECID_TYPES, MCP, website, deploy |
| 5 | 18-20 | SecID-Client-SDK | Python, TypeScript, Go SDK updates |

**Total: 20 tasks.** Phases 1-3 (SecID repo) should be done first and merged. Phase 4 (Service) depends on Phase 3 being merged (triggers KV re-upload). Phase 5 (SDK) can be done in parallel with Phase 4.
