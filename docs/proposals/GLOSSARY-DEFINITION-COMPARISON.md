# Proposal: Cross-Source Glossary Definition Comparison

Status: **Approach under revision** — see *Revision and Analysis (2026-05-17)* below
Date: 2026-05-14 (original); 2026-05-17 (revision notes added)
Author: Kurt Seifried, with AI-assisted design
Reviewers: open — please add review notes inline or as PR comments

> **Quick orientation for readers**: this proposal originally argued for a pure relationship-layer approach (glossary documents identified in `reference`, but term-level definitions stored outside the registry). After reflection, the approach is being revised toward a **hybrid**: a `kind: "glossary"` tag on the `reference` entry, full term-level data embedded in a separate dataset repository, and the registry entry as the pointer that ties them together. The original argument is preserved below; the revised approach is in the *Revision and Analysis* section.

## Summary

Add a glossary-definition comparison capability so users and AI agents can query a term (for example, `vulnerability`, `WAF`, `zero trust`) and retrieve how multiple authorities define it.

This closes a practical context gap: security terms are reused across standards bodies, vendors, and training materials, but definitions are often subtly different. Those differences change interpretation, controls mapping, and policy intent.

---

## Revision and Analysis (2026-05-17)

After reflection, the original proposal's pure relationship-layer framing is being revised. The new direction:

1. Tag glossary-shaped `reference` entries explicitly (`kind: "glossary"`)
2. Embed term-level data — but in a separate **glossary dataset repository**, not in the core registry file directly
3. The `reference` registry entry remains identity-only but points at the dataset for term content

This subsection documents *why* we're moving in this direction, what we considered, and what's still open.

### The question that triggered the revision

The original proposal placed all term-level data in a "relationship-layer dataset and service behavior" — outside the core registry. But it also said term-level entries *can* use subpaths (`secid:reference/nist.gov/csrc-glossary#vulnerability`).

That leaves a real question: when someone resolves `secid:reference/nist.gov/csrc-glossary#vulnerability`, what comes back?

- **Pure relationship-layer**: the registry returns "this is a valid term identity" but no definition. To get the definition, you call a separate service or fetch a separate dataset. The SecID resolution itself is bare.
- **Embed everything in the registry file**: the registry file *is* the definition store. Resolving the SecID returns the term + definition + provenance directly.
- **Hybrid**: the registry entry tags itself as a glossary (`kind: "glossary"`) and points at a dataset repository where the term-level data lives. Resolution can be enriched by following the pointer.

The user-experience question is real: **a SecID for a term that doesn't return the definition is a citation primitive, not a useful lookup.** AI agents and humans both expect "show me the definition" to come back when they ask.

### Sizing reality

Embedding everything in the registry file has scale problems:

| Glossary | Approx. terms | Approx. size |
|---|---|---|
| NIST CSRC Glossary | ~6,000 | 3–5 MB |
| AWS security glossary | ~500 | ~250 KB |
| CSA Security Guidance glossary | ~400 | ~200 KB |
| OWASP glossary | ~200 | ~100 KB |
| ENISA glossary | ~2,000 | 1–2 MB |

NIST's glossary alone is 3–5 MB. The current registry files are typically 5–50 KB each. Putting NIST CSRC's full content in a single registry file inflates the file by 100×, which has knock-on effects:

- **Cloudflare KV value limit (25 MB per value)**: NIST fits, but the headroom shrinks
- **KV read cost**: every resolution loads the full file value, even to extract one term
- **Deploy chain churn**: every term update requires the full file to be re-committed and re-deployed
- **Citation latency**: resolving one term reads ~5 MB to extract ~200 bytes
- **Git diff readability**: PRs adding/changing a few terms become unreviewable in a 6,000-line file

### Update cadence

The original proposal mentioned "we will want more aggressive capture and updating of this data." That implies frequent (weekly/monthly) re-crawls. Registry files aren't designed for that cadence:

- Registry changes go through PR review, merge, auto-trigger workflow, KV upload (~1m20s end-to-end)
- That's appropriate for low-frequency identity changes ("the NIST glossary now has a new URL")
- It's *not* appropriate for "NIST added 14 new terms and revised 3 definitions this week"

Embedding everything in the registry file would force frequent term-content updates through registry-change machinery designed for infrequent identity changes. The frictions compound.

### The hybrid approach

The cleanest answer uses two pieces, each playing to its strength:

1. **Core registry entry** (low-churn, identity-only):

```json
{
  "namespace": "csrc.nist.gov",
  "type": "reference",
  "match_nodes": [
    {
      "patterns": ["(?i)^csrc-glossary$"],
      "description": "NIST CSRC Glossary",
      "data": {
        "kind": "glossary",
        "official_name": "NIST Computer Security Resource Center Glossary",
        "common_name": "NIST CSRC Glossary",
        "term_count": 6000,
        "primary_url": "https://csrc.nist.gov/glossary",
        "data_repo": "secid:reference/cloudsecurityalliance.org/secid-glossaries#csrc-nist",
        "license": "Public domain (US government work)",
        "parser": "secid:reference/cloudsecurityalliance.org/secid-parsers#nist-csrc-glossary-json"
      }
    }
  ]
}
```

2. **Glossary dataset repository** (high-churn, term-level content):
   - Lives in `CloudSecurityAlliance-DataSets/SecID-glossary/` (or similar, per `docs/reference/DATA-HOSTING-RULES.md`)
   - One file per glossary source: `csrc-nist.json`, `aws-security.json`, `csa-guidance.json`, `enisa.json`, ...
   - Full term records with provenance, retrieval timestamps, source URLs
   - Independently versioned and updateable on whatever cadence makes sense per source
   - Cross-references back to the registry entry's `secid:reference/...` SecID

This pattern aligns with the existing SecID three-layer model (Registry / Relationship / Data) per CLAUDE.md, and with the V2 Data Repositories item in TODO.md (which proposed exactly this pattern for control, weakness, regulation types). Glossary would be the first V2 dataset.

### Why the `kind: "glossary"` tag is doing real work

A small but powerful addition. The tag signals to consumers (resolver, MCP server, AI agents) that:

- This `reference` entry is glossary-shaped
- Term-level subpaths are expected and meaningful
- A `data_repo` SecID points at the term-level dataset
- The parser document describes how to consume the dataset

Consumers can filter for `kind: "glossary"` entries to find all glossaries across the registry, regardless of source. That's the cross-source comparison the original proposal targeted — but accomplished via a tag on existing entries, not via a new type or new infrastructure.

This mirrors how `disclosure` entries use `cve` blocks to mark CNAs, and how `methodology` entries could grow `kind` tags for variants (scoring methodologies vs. mapping methodologies vs. assessment methodologies).

### What this approach buys vs. costs

| | Pure relationship-layer (original) | Embed-everything | Hybrid (revised) |
|---|---|---|---|
| SecID resolution returns definition | ✗ | ✓ | ✓ (via data_repo pointer) |
| Aggressive update cadence supported | ✓ | ✗ (registry-locked) | ✓ (dataset-locked) |
| Registry file size stable | ✓ | ✗ | ✓ |
| Single-place data | ✗ | ✓ | ✗ (registry + dataset) |
| Aligns with existing 3-layer model | ✓ | ✗ | ✓ |
| Aligns with V2 Data Repositories plan | partial | ✗ | ✓ |
| Pioneer-able now without V2 infrastructure | ✓ | ✓ | partial (needs V2 dataset repo to exist) |

The hybrid wins on most dimensions. Its weakness is operational: it requires the V2 Data Repository pattern to exist, and that's currently "design complete, not started" per TODO.md. The glossary dataset could be the first V2 dataset, which provides the forcing function to actually build the V2 pattern.

### What stays the same

The original proposal's other elements remain valid:
- Glossary documents identified in `reference` (✓ unchanged)
- Term-level subpaths where possible (✓ unchanged — `reference/nist.gov/csrc-glossary#vulnerability`)
- Per-source provenance (timestamps, source URLs, licenses) (✓ unchanged — just lives in dataset, not relationship-layer)
- Goals, non-goals, use cases, risks (✓ unchanged)

What changes is the *storage location* for the term-level data: from "relationship-layer dataset and service behavior" (vague) to "named glossary dataset repository following V2 pattern" (concrete) — and the addition of the `kind: "glossary"` tag on the registry entry as the bridge.

### Open questions for this revision

1. **Should the `kind` field be a single value (`"glossary"`) or an array (`["glossary", "controlled-vocabulary"]`)?** Some sources are glossary-shaped AND also other things (controlled vocabularies, ontologies). An array gives flexibility; a single value keeps schema simple.
2. **How small a glossary justifies the dataset-repo pattern vs. inline embedding?** A 20-term glossary fits easily in a registry file. A 6,000-term glossary doesn't. Is there a threshold (50 terms? 500 terms?), or always-use-dataset for consistency?
3. **Do we ship the registry-side `kind: "glossary"` tag *now* (before V2 datasets exist), as preparation?** Tagging existing glossary `reference` entries is cheap and useful even if the dataset repo isn't built yet — at minimum it makes them discoverable as glossaries.
4. **Naming the dataset repo**: `CloudSecurityAlliance-DataSets/SecID-glossary/` (matches V2 plan from TODO.md) or something more specific like `CloudSecurityAlliance-DataSets/SecID-reference-glossaries/` to distinguish from other reference-type data?
5. **Cross-source comparison query**: still relationship-layer service behavior, or implementable as a simple dataset-repo scan?

### Invitation to challenge this revision

If you think the original "pure relationship-layer" framing was better, or you have a stronger argument for embed-everything, please open a PR or comment. Specific cases where this revision could be wrong:

- **If V2 dataset infrastructure is not built in a reasonable timeframe**, the hybrid approach has no operational landing; we'd be better off with pure relationship-layer + a temporary service.
- **If glossary update cadence turns out to be infrequent (annual, not weekly)**, the registry-only embed approach becomes viable and avoids the multi-repo complexity.
- **If consumer demand turns out to be only "is X a recognized glossary?" not "what does X say about term Y?"**, the lighter tag-only approach without dataset infrastructure is sufficient.

This revision was reached on 2026-05-17 based on current understanding of glossary size distributions, update cadence expectations, and the existing three-layer model. A future reviewer with different evidence might reasonably reach a different conclusion.

---

## Problem

Today, SecID can identify many glossary *documents* under `reference`, but cannot systematically compare term-level definitions across sources.

Examples:

- NIST, CSA, and vendors may all define `vulnerability` differently
- `WAF` may be scoped as a product category, control function, or deployment model depending on source
- AI systems ingesting mixed-source content can misinterpret intent if source-specific definitions are not visible

Without term-level comparison, users and AI agents lose critical semantic context.

## Goals

- Query a term and get per-source definitions with provenance
- Preserve source authority (no forced "single canonical definition")
- Support machine consumption (LLM grounding, retrieval, citation)
- Keep SecID registry scope constraints intact

## Non-Goals

- Do not adjudicate which definition is "correct"
- Do not flatten all term differences into one normalized meaning
- Do not move large, mutable semantic content into the core registry

## Design Constraints

SecID design docs currently state that enrichment and relationships belong outside the core registry. Cross-source semantic comparison is relationship/enrichment data, not identifier grammar.

Therefore this capability should be implemented as a **relationship-layer dataset and service behavior**, not as registry bloat.

## Proposed Model

### 1) Keep source identities in `reference`

Glossary artifacts remain identifiable as normal SecIDs, for example:

- `secid:reference/nist.gov/csrc-glossary`
- `secid:reference/cloudsecurityalliance.org/artifacts#data-security-glossary`

Where possible, term-level entries can use subpaths:

- `secid:reference/nist.gov/csrc-glossary#vulnerability`
- `secid:reference/nist.gov/csrc-glossary#waf`

If a source has no stable term identifiers, the relationship layer stores a stable synthetic key with provenance.

### 2) Add relationship-layer "definition observations"

Each record captures one source's definition of one term:

```json
{
  "term_query": "vulnerability",
  "term_normalized": "vulnerability",
  "source_term_secid": "secid:reference/nist.gov/csrc-glossary#vulnerability",
  "source_document_secid": "secid:reference/nist.gov/csrc-glossary",
  "source_label": "NIST CSRC Glossary",
  "definition_text": "...",
  "notes": "Definition cites SP 800-53 Rev. 5",
  "effective_date": "2024-01-15",
  "retrieved_at": "2026-05-14",
  "source_url": "https://csrc.nist.gov/glossary/term/vulnerability",
  "license": "Source terms apply",
  "provenance": {
    "method": "api",
    "collector": "secid-glossary-harvester"
  }
}
```

### 3) Query behavior

Input: term string (and optional filters)

Output:

- Raw per-source definitions
- Optional normalized summary for AI use
- Metadata: source, date, citation URL, extraction confidence

Optional filters:

- source authority list (`nist.gov`, `cloudsecurityalliance.org`, `amazon.com`)
- date cutoff
- exact term vs alias expansion

## Why Relationship Layer (Not New Type)

A new `definition`/`glossary` type in core registry is not required for this use case:

- The hard problem is cross-source semantic comparison, which is enrichment/relationship data
- Term text changes over time and is high-churn relative to identifier mappings
- Keeping this in a separate layer aligns with existing SecID scope principles

## Data Acquisition Plan

1. Start with 3-5 high-value glossary sources (NIST, CSA, AWS, optionally OWASP)
2. Build source-specific collectors (API or structured scrape)
3. Normalize term keys (lowercase + punctuation policy) while retaining original term forms
4. Store full provenance and retrieval timestamps
5. Re-crawl on schedule (weekly/monthly by source volatility)

## Initial Use Cases

- Prompt-time grounding for AI analysis of mixed-source documents
- Policy and control mapping when terms differ by authority
- Training-content harmonization (show definitional deltas before mapping)
- Analyst workflows: "show me all definitions of X"

## Risks and Mitigations

- **Licensing constraints**: some sources may restrict redistribution of full text
  - Mitigation: store citations and short excerpts where needed; retain fetch-on-demand mode
- **Term ambiguity**: one token may represent multiple concepts (`WAF` vs `web app firewall` context)
  - Mitigation: support alias groups + optional domain tags
- **Staleness**: glossary content changes
  - Mitigation: timestamped observations + recrawl policy
- **Over-normalization**: accidental loss of source nuance
  - Mitigation: preserve full source text; normalized summaries are additive only

## Open Questions

1. Should term canonicalization live in SecID core, or strictly in relationship datasets?
2. Should synthetic term IDs be standardized when a source does not provide stable term URLs?
3. Do we return full definition text, excerpt, or citation-only by default?
4. What minimum provenance fields are mandatory for trustable AI use?
5. Should this ship as a service endpoint first, or as static dataset files first?

## Validation Criteria

The design is successful if:

- Querying `vulnerability` returns distinct, source-attributed definitions from at least 3 authorities
- Users can cite exact definition sources and dates
- AI outputs referencing terms improve precision in mixed-source tasks
- No core-registry schema expansion is required to support ongoing definition updates

## Suggested Next Step

Run a pilot for 10 terms (`vulnerability`, `risk`, `threat`, `incident`, `control`, `safeguard`, `WAF`, `zero trust`, `identity`, `assurance`) across NIST + CSA first, then evaluate data quality and operational cost.
