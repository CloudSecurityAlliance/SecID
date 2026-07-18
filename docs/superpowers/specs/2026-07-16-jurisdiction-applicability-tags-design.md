# Jurisdiction/Applicability Tags Design

**Date:** 2026-07-16
**Status:** Approved design, pending implementation
**Scope:** Optional `tags` field for filtering registry entries by country, sector, and other dimensions
**Affects:** Registry JSON format (all types), `schemas/registry-namespace.schema.json`, `docs/reference/REGISTRY-JSON-FORMAT.md`

## Problem

SecID has no structured way to answer "show me everything from Japan" or "everything in the financial sector" — the closest signal today is the domain TLD and reversed-path directory structure (e.g. `registry/control/jp/go/*.json`), which isn't queryable and doesn't cover supra-national or sector scope at all.

This surfaced while adding ~40 Japanese sources (PRs #112-116): every entry is implicitly Japan-scoped, several are sector-specific (FSA → financial, MHLW → healthcare, MLIT → transport sub-sectors), and there was no way to record that structurally.

Note on scope: per PRINCIPLES.md's three-layer model (Registry / Relationship / Data), some richer applicability questions ("does this apply to my org" — entity-size thresholds, extraterritorial reach) lean toward the future Data Enrichment layer rather than the Registry. This design covers lightweight, filterable **tags** only — not a compliance-applicability rules engine. That distinction can be revisited if usage pushes toward richer semantics.

## Design

### `tags` field, same shape at two levels

```json
"tags": {
  "country": ["JP"],
  "sector": ["financial"]
}
```

A dict of key → array of strings. Values are always arrays, even for a single value, so a key can hold multiple values without a shape change (e.g. `"country": ["DE", "FR", "IT"]`).

`tags` is optional and can appear:
1. **At the namespace level** (top of a registry file) — describes the org/source as a whole.
2. **On any individual match_node's `data` block** — describes that specific document.

### Resolution semantics: per-level, not merged

There is no merge/override logic. A query resolves to whichever level it names, and tags are read from that level:

- `secid:control/jpsomething.jp` → namespace-level tags.
- `secid:control/jpsomething.jp/some-item` → that match_node's own tags if present; if the match_node doesn't declare `tags` at all, it falls back to the namespace-level tags (same "closest-defined-ancestor" idea already implicit elsewhere in the registry, e.g. how `notes`/`urls` work).

This means a source that applies to a different country/sector than its parent namespace (e.g. a Korea-relevant item under a Japanese org's namespace) just declares its own `tags` — no special override syntax needed.

### Keys are open, not enumerated (for now)

No fixed schema enum of allowed keys yet. The JSON Schema only validates the *shape* (object of string arrays), not specific keys/values:

```json
"tags": {
  "type": "object",
  "additionalProperties": {
    "type": "array",
    "items": {"type": "string"}
  }
}
```

Starter convention (documented, not enforced): `country` using ISO 3166-1 alpha-2 codes, plus `EU` and `INTL` for supra-national/international sources. Other keys (`sector`, etc.) are free text until real usage shows what a controlled vocabulary should look like. Revisit enumeration once enough entries are tagged to see the actual key/value spread.

### Rollout

- Add `tags` as an optional field to `schemas/registry-namespace.schema.json` (top level and inside match_node `data`).
- Document in `docs/reference/REGISTRY-JSON-FORMAT.md`.
- Pilot: tag all ~19 Japan registry files from this session's work with `"tags": {"country": ["JP"]}` at the namespace level; add `sector` at the match_node level where clearly applicable (FSA → `financial`, MHLW/medical guidelines → `healthcare`, MLIT guidelines → their transport sub-sector).
- No mass retrofit of the existing ~2,058 namespaces — absent `tags` means "not yet tagged," consistent with the registry's existing null-vs-absent convention.
- Out of scope for this change: any query/filter capability in the API (SecID-Service). Adding the data doesn't itself expose a "browse by country" endpoint — that's a separate follow-on in a different repo, only worth building once there's enough tagged data to filter over.

## Self-review

- No placeholders remain.
- Consistent with the null-vs-absent convention already documented in CLAUDE.md/REGISTRY-JSON-FORMAT.md.
- Scoped to this repo only; explicitly calls out that API/filtering is a separate, not-yet-scoped follow-on elsewhere.
