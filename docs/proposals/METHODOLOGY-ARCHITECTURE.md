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
