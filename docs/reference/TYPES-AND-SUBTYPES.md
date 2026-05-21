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

A subtype is a string value in the `subtype:` field of a match_node's `data:` block. It's normal registry data — no schema change needed (`data:` is `additionalProperties: true` in [registry-namespace.schema.json](../../schemas/registry-namespace.schema.json)).

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
        "subtype": "glossary",
        "data_repo": "secid:reference/cloudsecurityalliance.org/secid-glossaries#csrc-nist",
        "...": "..."
      }
    }
  ]
}
```

Consumers can filter for `subtype: "glossary"` to find all glossary-shaped reference entries across the registry, regardless of source. That's the cross-source-discovery affordance.

Subtypes are placed at the **source-level** match_node (the top-level entries in `match_nodes[]`), not on individual children. The subtype describes the whole namespace entry's character. Don't confuse subtypes with the existing child-level `data.type:` fields used for internal node typing — those describe what *kind of item* a specific child matches within a source's internal taxonomy (e.g., an ATT&CK child match_node with `type: "tactic"` vs. `type: "technique"`). Different level, different purpose.

## Named subtypes in use today

Only one named subtype is currently in active use. The two implicit overloads listed below operate the same way conceptually but don't yet carry a `subtype:` tag — they're identified by which entries live in which directory.

| Type | `subtype:` value | What it means | Where to find it | Defined by |
|------|------------------|---------------|------------------|------------|
| `reference` | `"glossary"` | A glossary document with addressable term-level subpaths. Entry is identity-only; term data lives in a separate dataset repo (Phase 1) and will be copied into the registry for direct API serving in Phase 2. | `registry/reference/<path>.json` entries carrying `subtype: "glossary"` | [GLOSSARY-DEFINITION-COMPARISON](../proposals/GLOSSARY-DEFINITION-COMPARISON.md) (Accepted 2026-05-20) |

## Implicit overloads (subtypes-in-spirit, not yet tagged)

These two patterns predate the `subtype:` convention and are documented in [DESIGN-DECISIONS.md §"Current Overloading"](../explanation/DESIGN-DECISIONS.md). They behave like subtypes — distinct sub-categories within a type — but they don't currently carry a `subtype:` tag in registry data. They're identified by *which namespace* they live in, not by a discriminator field.

| Type | Implicit sub-category | What it covers | Example sources | Anticipated `subtype:` value (if backfilled) |
|------|----------------------|----------------|-----------------|---------------------------------------------|
| `advisory` | Incident reports | "This AI system caused harm" / "this device failed" publications | AIID, NHTSA, FDA adverse events | `subtype: "incident-report"` |
| `control` | Prescriptive benchmarks | "Test for these behaviors" eval suites that function as requirements | HarmBench, WMDP | `subtype: "benchmark"` |
| `control` | Documentation standards | Templates for describing a model/system, treated as a normative format requirement | Model Cards | `subtype: "documentation-standard"` |

We are not doing a backfill sweep of these implicit overloads. New entries that match these patterns should carry the `subtype:` value from day one, and existing entries pick it up opportunistically when they're touched for other reasons. Over time the implicit overloads become explicit.

## When to add a subtype vs. split into a new type

The default — and a load-bearing project principle — is **use the existing type plus a `subtype:` tag**. Splitting into a new type is the exception path, gated by the four criteria documented in [DESIGN-DECISIONS.md §"When to Split"](../explanation/DESIGN-DECISIONS.md):

1. **Resolution patterns diverge.** Different URL structures, different APIs, different metadata shapes.
2. **Consumers diverge.** Different tools need to filter them separately, with materially different workflows.
3. **Semantics drift.** The "question answered" becomes meaningfully different.
4. **Volume justifies it.** Enough examples exist to define clear boundaries.

The `disclosure` type passed all four. So did `capability` and `methodology`. Recent decisions to *not* split (glossary, regulation/control, assertion/content under revision) failed at least one criterion — usually #1 (resolution patterns can fit within the parent type's shape) or #2 (consumers don't actually need the filtering distinction).

The cost gradient:

- **Subtype tag** — change one field in a registry file, document the value here, ship. Reversible.
- **New type** — coordinate changes across 4 repos, update parser/resolver/MCP/client logic, migrate existing entries, update all documentation. Hard to reverse.

So the practical rule: **try a subtype first**. If lived experience shows the four split criteria are genuinely met, promote to a new type. If a subtype works fine, leave it as a subtype.

## Decision history (proposals that landed as subtypes)

Three proposals were resolved using existing types instead of adding new ones. See the proposals for full rationale.

| Proposal | Decision | Mechanism | Status |
|----------|----------|-----------|--------|
| [GLOSSARY-DEFINITION-COMPARISON](../proposals/GLOSSARY-DEFINITION-COMPARISON.md) | Glossaries stay in `reference` | `subtype: "glossary"` + `data_repo:` pointer (Phase 1); copy into registry (Phase 2) | Accepted 2026-05-20 |
| [ASSERTION-CONTENT-TYPES](../proposals/ASSERTION-CONTENT-TYPES.md) | Originally proposed two new types; collapsing toward existing `control` (BoKs as normative knowledge specs) + `reference` (courses as content artifacts) + relationship-layer (org compliance attestations) | Specific subtype values TBD as the revision lands | Under revision |
| [ENTITY-REGULATION-CONTROL-SPLIT](../proposals/ENTITY-REGULATION-CONTROL-SPLIT.md) | Regulations stay in `control/`; small entity-cleanup may still extract clearly-org-not-control entries into `entity/` | Cross-reference fields (`publishedBy:`, `authorizedBy:`) instead of type split | Declined (with rationale) 2026-05-17 |

For the contrast — proposals that did become new types — see [CAPABILITY-TYPE](../proposals/CAPABILITY-TYPE.md), [METHODOLOGY-TYPE](../proposals/METHODOLOGY-TYPE.md), and [DESIGN-DECISIONS.md §"Case Study: The `disclosure` Split"](../explanation/DESIGN-DECISIONS.md).

## Adding a new subtype

To propose a new named subtype:

1. **Check whether it really needs a name.** A subtype is worth defining when (a) multiple registry entries will share it, and (b) consumers will want to filter or behave differently based on it. A one-off classification with no consumer affordance doesn't justify a named subtype.
2. **Pick a kebab-case string value** — `"glossary"`, `"incident-report"`, `"benchmark"`. Match the conceptual name a practitioner would use.
3. **Add a row to the "Named subtypes in use today" table** above, with the type, value, meaning, where to find entries, and the proposal/decision document.
4. **Tag entries from day one**; don't backfill in a sweep — pick up existing matches opportunistically as they're touched for other reasons.
5. **If consumer behavior depends on the subtype**, document that behavior wherever the consumer lives (resolver, MCP server, client SDK).

A subtype proposal lives at the same level as a feature decision — a short proposal doc in [docs/proposals/](../proposals/) is appropriate if the subtype changes API behavior or introduces cross-repo coordination; otherwise a PR adding the row to this doc is sufficient.
