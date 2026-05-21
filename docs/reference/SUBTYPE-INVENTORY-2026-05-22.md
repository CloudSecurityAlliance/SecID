# Subtype Inventory, 2026-05-22

This is the inventory pass for types that currently declare named subtypes in
SecID-Service's `type-registry.ts`: `methodology` and `reference`.

The pass only counts source-level `match_nodes`. Child nodes are not subtype
owners under the current convention.

## Summary

| Type | Source-level match_nodes | Tagged | Untagged | Notes |
| --- | ---: | ---: | ---: | --- |
| `methodology` | 45 | 45 | 0 | This PR adds the missing FedRAMP scoring tag. |
| `reference` | 214 | 0 | 214 | Not all references are glossaries; this needs a separate glossary backfill decision. |

## Methodology

Before this sweep, one methodology entry was missing an obvious subtype:

| File | Patterns | Subtype decision |
| --- | --- | --- |
| `registry/methodology/gov/fedramp.json` | `(?i)^threat-based-risk-profiling-methodology$` | `["scoring"]` |

`registry/methodology/gov/nist.json#800-39` already carried
`["risk-management"]` on the current `main` branch.

## Reference

Every current source-level `reference` match_node is untagged. Many of them are
glossary-shaped, but the set also includes identifier systems, model/system
cards, security guidance collections, GitHub object references, and other
non-glossary references. I did not backfill `reference` in this PR because a
blind `subtype: ["glossary"]` pass would over-tag non-glossary entries.

Recommended next step: run a dedicated reference-glossary classification pass
that separates at least:

- obvious glossaries and controlled vocabularies
- identifier/reference systems such as ASIN, GitHub object references, DOI/RFC
  style entries
- model cards, system cards, and security guidance collections

After that split is reviewed, `reference` can move from warn-only completeness
checking toward fail-on-missing for entries that should be glossary-tagged.

## Validator Change

`scripts/validate-subtypes.py` now has a completeness mode:

```bash
python3 scripts/validate-subtypes.py --completeness-policy warn
```

The normal undeclared-subtype check still fails on invalid values. Completeness
can be run as `warn` while the inventory is still open, and later changed to
`fail` once existing gaps are closed.
