# URL Field Normalization Plan

## Decision

Two URL mechanisms, nothing else:

1. **`data.url`** (single string on child match_nodes) — THE resolution URL template. Supports `{id}` variable substitution. One per child. Multiple children with different weights/formats for multiple resolution paths.

2. **`urls`** (array) — ALL other URLs. Documentation, source references, API endpoints, downloads, security pages, translations. Appears at: top-level on namespace entries, `data` block on source-level match_nodes, optionally on child match_nodes alongside `data.url`.

**Eliminated:** `data.source` (bare string) — convert to `urls` array entry.

## URL Array Entry Schema

```json
{
  "url": "https://...",              // required — the actual URL
  "type": "docs",                    // required — rough category
  "note": "Human/AI readable context", // optional — what this URL is for
  "lang": "en",                      // optional — ISO 639-1 language code
  "format": "json"                   // optional — content format (html, json, pdf, xml, csv)
}
```

### Common `type` values (not a strict enum)

| Type | Usage |
|------|-------|
| `website` | Main website or product page |
| `docs` | Documentation, guides, references |
| `api` | API endpoint or API reference |
| `bulk_data` | Downloadable dataset (ZIP, JSON, XML, CSV) |
| `lookup` | Lookup/search URL for finding specific items |
| `security` | Security-specific page |
| `security_txt` | RFC 9116 security.txt file |
| `paper` | Research paper or publication |

Other values are fine — the `note` field carries the real context for AI consumption. Don't over-enumerate.

## Changes Required

### Phase 1: Documentation (SecID repo)

| File | Change |
|------|--------|
| `docs/reference/REGISTRY-JSON-FORMAT.md` | Document the URL array schema. Add `lang` and `format` as optional fields. Clarify `data.url` vs `urls` distinction. Document common type values. |
| `SPEC.md` | Mention URL convention in the registry format section if not already there. |
| `docs/proposals/CAPABILITY-PROCESS.md` | Update to say "use `urls` array, not `source` field" |
| `docs/proposals/CAPABILITY-ARCHITECTURE.md` | Update example JSON to use `urls` not `source` |

### Phase 2: Fix capability registry data (SecID repo)

**428 `data.source` strings across 54 capability files** → convert each to:

```json
// Before:
"source": "https://docs.aws.amazon.com/..."

// After:
"urls": [
  {"type": "docs", "url": "https://docs.aws.amazon.com/...", "note": "AWS documentation"}
]
```

Script: `scripts/normalize-capability-urls.py` — reads each capability JSON, converts `source` → `urls` entry, writes back.

### Phase 3: Update website renderer (SecID-Service repo)

The Resolver.astro currently has three separate URL rendering blocks:
- `d.urls` array (line 739)
- `d.url` bare string (line 765)
- `d.source` bare string (line 780)

After normalization, `d.source` block can be removed. `d.url` block stays for child resolution URLs displayed as registry data. `d.urls` block handles everything else.

### Phase 4: Update service types (SecID-Service repo)

`src/types.ts` `MatchNodeData` interface — add `lang` and `format` as optional fields on the URL type if not already there. Verify `RegistryUrl` type matches the schema.

### Phase 5: Re-upload KV and deploy

Standard upload + deploy cycle after registry data changes.

## Execution Order

1. Write the normalization script
2. Run it on all 54 capability files
3. Update docs (REGISTRY-JSON-FORMAT.md at minimum)
4. Commit + push SecID repo
5. Clean up website renderer
6. Commit + push + deploy SecID-Service
7. Re-upload KV

## What Does NOT Change

- `data.url` on child match_nodes (resolution templates) — stays as-is
- Existing `urls` arrays on non-capability files — already correct
- The resolver's `resolveChildUrl` function — reads `data.url`, works fine
- Multiple resolution URLs via multiple children — pattern is correct
- `data.lookup_table` — separate mechanism, unrelated
