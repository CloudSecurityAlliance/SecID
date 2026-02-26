# Overlays: Enriching Without Mutating

Status: **Exploratory** - Not yet designed

## The Idea

Sometimes you want to add information to something without changing the source. For example:

- A CVE exists but NVD enrichment is pending - you want to add a CVSS score from the vendor
- A vulnerability has no AI classification - you want to note it's related to prompt injection
- Two sources disagree on severity - you want to flag the dispute

Overlays would let you layer additional assertions on top of existing data.

This document captures our thinking about how overlays *might* work. None of this is decided.

## Why We're Waiting

Overlays seem simple but have subtle questions:

- **Conflicts**: What if two overlays say different things?
- **Authority**: Whose overlay wins? Is there a hierarchy?
- **Scope**: Can you overlay a single field? A whole record? A pattern?
- **Lifecycle**: Do overlays expire? Get superseded?
- **Validation**: How do you prevent garbage?

We don't have good answers yet. Usage will teach us.

## What We're Considering

### Possible Overlay Types

| Type | What it might do |
|------|------------------|
| Enrich | Add data not in source |
| Normalize | Standardize messy values |
| Warn | Flag quality issues |
| Dispute | Note disagreements |
| Deprecate | Mark as outdated |

### Open Questions

**Conflict Resolution**
- First overlay wins? Last overlay wins? Merge somehow?
- Do we need explicit priority/authority levels?
- What if two trusted sources disagree?

**Scope**
- Single identifier? Pattern of identifiers?
- Single field? Multiple fields? Whole record?
- Can overlays reference other overlays?

**Lifecycle**
- Are overlays permanent or can they be retracted?
- Do they have expiration dates?
- How do you supersede an overlay?

**Trust**
- Who can create overlays?
- Are some sources more authoritative?
- How do consumers decide which overlays to trust?

### Sketch: What It Might Look Like

This is purely illustrative - not a design:

```json
{
  "target": "secid:advisory/mitre.org/cve#CVE-2024-1234",
  "type": "enrich",
  "adds": {
    "cvss_v3": "8.8",
    "source": "vendor advisory"
  },
  "rationale": "NVD enrichment pending, using vendor score",
  "asserted_by": "example-org",
  "created": "2026-01-08"
}
```

Or maybe overlays are simple key-value patches:

```yaml
target: secid:advisory/mitre.org/cve#CVE-2024-1234
overlay:
  ai_relevant: true
  atlas_technique: AML.T0043
note: "This CVE involves prompt injection"
```

Or maybe something completely different. We don't know yet.

## Core Principle (Probably)

One thing we're fairly confident about:

**Overlays shouldn't mutate source data.**

They're assertions *about* data, not changes *to* data. The original stays intact; overlays provide an interpretation layer.

## Use Cases We're Thinking About

1. **Supplementing delayed enrichment** - Add severity scores while waiting for NVD
2. **AI classification** - Tag CVEs with ATLAS techniques or OWASP LLM categories
3. **Quality flags** - Note when descriptions are incomplete or scores are disputed
4. **Cross-references** - Link to related research papers or incidents

## What Would Trigger Design Work

We'll start designing the overlay layer when:

1. We have specific enrichment needs that can't wait
2. We understand what data people actually want to add
3. We see patterns in how corrections/additions are needed

## Related

- [RELATIONSHIPS.md](RELATIONSHIPS.md) - Exploratory thinking on connections
- [ROADMAP.md](../../ROADMAP.md) - Overall project phases
- [USE-CASES.md](USE-CASES.md) - What overlays would enable

---

*This is exploratory thinking, not a specification.*
