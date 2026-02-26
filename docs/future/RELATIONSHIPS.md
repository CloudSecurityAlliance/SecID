# Relationships: Connecting SecIDs

Status: **Exploratory** - Not yet designed

## The Idea

Identifiers alone are just strings. The real value comes from connecting them:

```
CVE-2024-1234
    ├── has the same content as → GHSA-xxxx-yyyy-zzzz
    ├── is classified as → CWE-89
    ├── can be exploited via → T1190
    └── is mitigated by → some control
```

This document captures our thinking about how a relationship layer *might* work. None of this is decided - we're documenting options and open questions.

## Why We're Waiting

We could design a relationship system now, but we'd be guessing. Better to:

1. Build the identifier system and registry
2. Use it for real work
3. See what relationships people actually need
4. Design based on evidence, not speculation

## What We're Considering

### Possible Relationship Categories

| Category | Examples | Notes |
|----------|----------|-------|
| Equivalence | "same as", "aliases" | Different IDs for the same thing |
| Classification | "has weakness", "uses technique" | Categorizing things |
| Mitigation | "mitigates", "addresses" | Controls that help |
| Reference | "about", "cites", "derived from" | Documentation links |
| Succession | "replaces", "preceded by" | Historical changes |

### Open Questions

**Directionality**
- Are relationships one-way (A → B) or bidirectional (A ↔ B)?
- If one-way, do we store both directions or compute the inverse?
- What about asymmetric relationships like "A mitigates B" (B doesn't mitigate A)?

**Cardinality**
- One-to-one, one-to-many, many-to-many?
- Are there constraints? (e.g., "every CVE should have exactly one canonical source")

**Provenance**
- Who asserted this relationship?
- When? Based on what evidence?
- How do we handle disagreements between sources?

**Confidence**
- Is this definitive or inferred?
- Human-curated or machine-harvested?
- How do we express uncertainty?

**Storage**
- JSONL files? (simple, git-friendly)
- Graph database? (queryable, but infrastructure)
- SQLite? (portable, queryable)
- Something else?

### Possible Data Sources

If we build a relationship layer, data might come from:

| Source | What it provides |
|--------|------------------|
| GHSA | CVE cross-references |
| OSV | Aliases across ecosystems |
| NVD | CVE → CWE mappings |
| ATT&CK | Technique → mitigation mappings |
| CAPEC | Attack pattern → CWE links |
| Manual curation | Framework crosswalks, expert knowledge |

### Sketch: What It Might Look Like

This is purely illustrative - not a design:

```json
{
  "from": "secid:advisory/github.com/advisories/ghsa#GHSA-xxxx-yyyy",
  "to": "secid:advisory/mitre.org/cve#CVE-2024-1234",
  "relationship": "aliases",
  "asserted_by": "github",
  "confidence": "high",
  "harvested": "2026-01-08"
}
```

Or maybe relationships are organized by type:

```
data/relationships/
├── aliases/
│   └── ghsa-cve.jsonl
├── classifications/
│   └── cve-cwe.jsonl
└── mitigations/
    └── controls-weaknesses.jsonl
```

Or maybe something completely different. We don't know yet.

## Current State

For now, entity files in the registry may include a `relationships` field:

```yaml
relationships:
  - to: "secid:entity/nist.gov/nvd"
    type: "enriched_by"
    description: "NVD adds CVSS, CPE, CWE to CVE records"
```

This is **documentation only** - it helps humans and AI understand what an entity is. It's not a queryable relationship store.

## What Would Trigger Design Work

We'll start designing the relationship layer when:

1. The registry has enough content that connections become valuable
2. We have concrete use cases that require queryable relationships
3. We understand the patterns from actual usage

## Related

- [OVERLAYS.md](OVERLAYS.md) - Exploratory thinking on enrichment
- [ROADMAP.md](../../ROADMAP.md) - Overall project phases
- [USE-CASES.md](USE-CASES.md) - What relationships would enable

---

*This is exploratory thinking, not a specification.*
