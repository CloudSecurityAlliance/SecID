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
