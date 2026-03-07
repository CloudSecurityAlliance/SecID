# Proposal: `_checked` / `_updated` / `_note` Fields for Registry Data

**Status:** Proposed
**Date:** 2026-03-06
**Author:** SecID maintainers

## Problem Statement

SecID registry data includes URLs, email addresses, policy descriptions, and null values that represent negative findings ("we checked, they don't have one"). Currently there's no way to know *when* any of this was verified.

Git history tracks when files were committed, but not when the real-world facts were last confirmed accurate. This distinction matters because:

- A `null` `security_txt` from 6 months ago needs re-checking; a `null` from last week is trustworthy
- A PSIRT URL confirmed working last week is reliable; one set 2 years ago might 404
- The upcoming `disclosure` type will heavily depend on freshness — contact info, reporting channels, and policy descriptions go stale fast
- AI agents consuming registry data need to assess trustworthiness of individual facts

The existing null/absent convention tells you *if* we looked, but not *when*:

| Current State | Meaning |
|---------------|---------|
| `"field": null` | We looked and found nothing |
| `"field"` absent | Not yet researched |

This is insufficient. A null from yesterday and a null from a year ago look identical.

## Proposed Fields

Three metadata fields per verifiable datum:

| Field | Meaning | Changes When |
|-------|---------|--------------|
| **`_updated`** | Date the value last materially changed | Only when the actual data changes |
| **`_checked`** | Date someone last verified the value was still accurate | Every verification pass, even if nothing changed |
| **`_note`** | Free-text observation about what was found during verification | When the observation changes |

### Interpretation

| `_updated` | `_checked` | Meaning |
|------------|------------|---------|
| `2025-06-01` | `2026-03-01` | Hasn't changed in 9 months, confirmed a week ago — very trustworthy |
| `2025-06-01` | `2025-06-01` | Set 9 months ago, never re-verified — worth re-checking |
| `2026-03-06` | `2026-03-06` | First recorded today, not yet re-verified |
| (absent) | (absent) | Not yet tracked (legacy data) |

`_checked` without `_updated` (or same date) means first recorded, not yet re-verified.

## Naming Convention (Resolved)

Two contexts, consistent naming across all three fields:

| Context | Fields | Example |
|---------|--------|---------|
| **Source-level** (top of file) | `checked`, `updated`, `note` | `"checked": "2026-03-06"` |
| **Attached to a specific field** (scalar suffix) | `field_checked`, `field_updated`, `field_note` | `"security_txt_checked": "2026-03-06"` |
| **Inside objects** (URL entries, etc.) | `checked`, `updated`, `note` | `{"url": "...", "checked": "2026-03-06"}` |

The `_checked`/`_updated`/`_note` suffix "attaches" the metadata to the field it describes. Inside objects, the fields are already scoped by the object, so no suffix needed.

Source-level `checked`/`updated` means "someone verified this entire registry entry is still accurate on this date." Source-level `note` captures general observations about the entry as a whole.

## Application Patterns

### Source-Level Timestamps

Top-level `checked` and `updated` on the registry file itself:

```json
{
  "schema_version": "1.0",
  "namespace": "redhat.com",
  "type": "entity",
  "status": "draft",
  "checked": "2026-03-06",
  "updated": "2026-03-06",
  ...
}
```

### URL Objects in Arrays

URLs are already structured as objects, so `checked`/`updated` are sibling fields:

```json
"urls": [
  {
    "type": "security",
    "url": "https://access.redhat.com/security/",
    "checked": "2026-03-06",
    "updated": "2026-03-06"
  }
]
```

### Scalar Fields

For flat fields (email, security.txt, policy text, etc.), use `_checked` / `_updated` / `_note` suffixes:

Confirmed positive (checked and found something):

```json
{
  "security_txt": "https://security.access.redhat.com/data/meta/v1/security.txt",
  "security_txt_checked": "2026-03-06",
  "security_txt_updated": "2026-03-06",
  "security_txt_note": ".well-known/security.txt redirects here. PGP signed, RFC 9116 compliant. Expires 2026-06-04."
}
```

Confirmed negative (checked and found nothing):

```json
{
  "security_txt": null,
  "security_txt_checked": "2026-03-06",
  "security_txt_updated": "2026-03-06",
  "security_txt_note": "https://www.oracle.com/.well-known/security.txt redirects to homepage"
}
```

The `_note` field records *what was observed* — particularly useful for null findings (why it's null) and for recording validation details on positive findings.

### Template URLs in `data` Blocks

For URL templates inside `match_nodes` → `data`:

```json
"data": {
  "url": "https://www.cve.org/CVERecord?id={id}",
  "url_checked": "2026-03-06",
  "url_updated": "2025-06-01",
  "examples": [
    {"input": "CVE-2021-44228", "url": "https://www.cve.org/CVERecord?id=CVE-2021-44228"}
  ]
}
```

## Interaction with Null/Absent Convention

This proposal extends the existing convention — it does not replace it:

| State | Meaning |
|-------|---------|
| `"field": null` | We looked and found nothing (existing) |
| `"field": null, "field_checked": "2026-03-06"` | We looked **on this date** and found nothing (proposed) |
| `"field"` absent | Not yet researched (existing, unchanged) |
| `"field"` absent, no `_checked`/`_updated` | Not yet tracked (proposed — same as "not yet researched") |

Adding timestamps to a null value makes it strictly more informative. Existing files without timestamps remain valid under the "not yet tracked" interpretation.

## Backwards Compatibility

Fully backwards-compatible:

- **Existing files without timestamps remain valid** — absent timestamps mean "not yet tracked"
- **No existing fields change meaning** — timestamps are additive
- **Timestamps are optional** — adoption is incremental, file by file, field by field
- **Consumers that don't understand timestamps ignore them** — unrecognized fields are already expected in JSON

No migration required. New timestamps can be added to existing files as they're verified, without touching unverified fields.

## What These Fields Are NOT

**Not a scheduling system.** There is no `_check_frequency` field. Consumers decide their own re-check cadence based on the dates. A security team might re-check null values weekly while established URLs get monthly verification. This is an operational concern, not a data modeling concern.

**Not per-regex-pattern.** Regex patterns rarely change — they describe ID formats that are stable for years. Timestamps apply to URLs, contact info, policy descriptions, and null findings — things that actually go stale.

**Not a replacement for git history.** Git history remains the source of truth for *who* changed *what*. These timestamps record *when someone last verified real-world facts*, which git cannot capture.

## Date Format

ISO 8601 date: `YYYY-MM-DD`

No time component needed — day granularity is sufficient for freshness assessment. Time zones are irrelevant at day granularity.

## Scope

Applies to all 7 registry types. Impact varies by type:

| Impact | Types | Why |
|--------|-------|-----|
| **High** | `disclosure` (proposed), `entity` | Contact info, reporting channels, product URLs — go stale fast |
| **Medium** | `advisory` | Source URLs, API endpoints — mostly stable but can move |
| **Low** | `control`, `weakness`, `ttp`, `regulation`, `reference` | URLs and descriptions rarely change, but should still be verifiable |

## Resolved Questions

1. **Naming convention:** `checked`/`updated`/`note` inside objects and at source level; `field_checked`/`field_updated`/`field_note` suffix for scalars. No `last_` prefix — it's redundant and verbose.

2. **Source-level fields:** Yes. Top-level `checked`/`updated`/`note` fields apply to the entire registry entry.

3. **Note field:** Yes. `_note` (or `note` at source/object level) records what was observed during verification. Particularly valuable for null findings ("redirects to homepage") and positive findings with caveats ("RFC 9116 compliant, missing Canonical field").

## Open Questions

1. **Tooling:** Should there be a registry maintenance script that flags fields where `_checked` is older than a threshold? This is an operational concern but would drive adoption.

## Pilot Files

The following registry files serve as the initial implementation to validate these patterns:

- `registry/entity/com/redhat.json` — positive `security_txt` finding, source-level timestamps
- `registry/entity/com/oracle.json` — null `security_txt` (confirmed negative), source-level timestamps

## References

- [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) — JSON schema that these fields extend
- [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md) — rationale for the null/absent convention this builds on
- [PRINCIPLES.md](../../PRINCIPLES.md) — "honest uncertainty" principle that motivates freshness tracking
