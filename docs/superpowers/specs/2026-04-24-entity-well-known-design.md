# Entity Well-Known Files Design

**Date:** 2026-04-24
**Status:** Approved design, pending implementation
**Scope:** Entity-level `well_known` block for tracking machine-discoverable files at org domains
**Affects:** Registry JSON format (entity type), entity registry entries, scanner tooling

## Problem

Organizations expose machine-readable files at well-known paths (llms.txt, robots.txt, CSAF provider metadata, OAuth discovery, etc.). This data helps AI agents and security tools understand what an org provides — but SecID entity entries don't capture it.

We've already scanned 487 CNA domains and found 969 valid files across 394 domains. The data exists in `seed/well-known-scan.json` and raw content in `SecID-Entity-Data`. It needs a home in the entity registry.

## Design

### `well_known` block on entity entries

A top-level `well_known` object on entity registry files. Each key is the raw filename (exactly as it appears in the URL path). Three states:

```json
"well_known": {
  "llms.txt": {"status": 200},
  "robots.txt": {"status": 200},
  ".well-known/security.txt": {"status": 301, "url": "https://www.cisco.com/c/dam/.../security.txt"},
  ".well-known/csaf/provider-metadata.json": {"status": 200},
  "sitemap.xml": null,
  "skill.md": null,
  "llms-full.txt": null
}
```

| State | Meaning |
|-------|---------|
| `{"status": 200}` | Found at the obvious URL (`https://{domain}/{key}`) |
| `{"status": 3xx, "url": "..."}` | Redirected — `url` is where it landed |
| `null` | Checked, not found |
| absent key | Not yet checked |

### Keys are raw filenames

Keys match exactly what you'd append to `https://{domain}/`:

- `llms.txt` (not `llms_txt`)
- `.well-known/security.txt` (not `well_known_security_txt`)
- `.well-known/csaf/provider-metadata.json` (full path)

### Files tracked

48 well-known files organized by category:

**Root-level conventions:**
`llms.txt`, `llms-full.txt`, `robots.txt`, `sitemap.xml`, `security.txt`, `humans.txt`, `skill.md`, `SKILL.MD`

**Security — advisories, disclosure, SBOM:**
`.well-known/security.txt`, `.well-known/csaf/provider-metadata.json`, `.well-known/csaf-aggregator`, `.well-known/sbom`

**Auth & identity:**
`.well-known/openid-configuration`, `.well-known/oauth-authorization-server`, `.well-known/oauth-protected-resource`, `.well-known/openid-federation`, `.well-known/webauthn`, `.well-known/uma2-configuration`, `.well-known/gnap-as-rs`, `.well-known/hoba`, `.well-known/did.json`, `.well-known/did-configuration.json`, `.well-known/ssf-configuration`, `.well-known/idp-proxy`

**Encryption & PKI:**
`.well-known/est`, `.well-known/cmp`, `.well-known/pki-validation`, `.well-known/posh`, `.well-known/acme-challenge`, `.well-known/ssh-known-hosts`, `.well-known/sshfp`, `.well-known/stun-key`, `.well-known/edhoc`, `.well-known/brski`

**Email & transport security:**
`.well-known/mta-sts.txt`, `.well-known/enterprise-transport-security`, `.well-known/enterprise-network-security`

**Privacy:**
`.well-known/gpc.json`, `.well-known/dnt-policy.txt`, `.well-known/ohttp-gateway`, `.well-known/private-token-issuer-directory`

**Network:**
`.well-known/looking-glass`, `.well-known/probing.txt`

**App linking:**
`.well-known/assetlinks.json`

**Host metadata:**
`.well-known/host-meta`, `.well-known/host-meta.json`

**MCP endpoints:**
`mcp`, `_api/mcp`

### Content validation

Each file type has a validator to filter out soft 404s (sites that return 200 with a search page instead of a real 404). Validators check for expected content signatures:

- `llms.txt` — starts with `#` (markdown heading)
- `robots.txt` — contains `User-agent:` or `Disallow:`
- `security.txt` — contains `Contact:`
- `.well-known/openid-configuration` — valid JSON with `issuer` key
- `.well-known/csaf/provider-metadata.json` — valid JSON with `publisher` or `metadata_version`
- etc.

Full validator table in `scripts/scan-well-known.py`.

### Relationship to disclosure

`security.txt` appears in both entity `well_known` (presence/status) and disclosure entries (`security_txt` field with parsed contact data). This is intentional duplication — entity records presence, disclosure records content. Different audiences, different purposes.

### Relationship to SecID-Entity-Data

Entity registry says "this org has a valid llms.txt" (labeling and finding). The [SecID-Entity-Data](https://github.com/CloudSecurityAlliance-DataSets/SecID-Entity-Data) repo stores the actual file content (data layer). Clean separation per SecID's three-layer architecture.

### Entity entry generation

~380 domains from the CNA scan don't have entity entries yet. These get minimal auto-generated entries:

```json
{
  "schema_version": "1.0",
  "namespace": "acronis.com",
  "type": "entity",
  "status": "draft",
  "status_notes": "Auto-generated from CNA disclosure data and well-known file scan.",

  "official_name": "Acronis",
  "common_name": "Acronis",
  "alternate_names": null,
  "notes": null,
  "wikidata": null,
  "wikipedia": null,

  "urls": [
    {"type": "website", "url": "https://acronis.com"}
  ],

  "well_known": {
    "llms.txt": {"status": 200},
    "llms-full.txt": {"status": 200},
    "robots.txt": {"status": 200},
    "sitemap.xml": null,
    ...
  },

  "match_nodes": []
}
```

Fields populated from disclosure entries: `official_name`, `common_name`, `urls` (website). `match_nodes` is empty — products/teams can be added later. `well_known` populated from scan data.

### Existing entity entries

The 14 existing entity entries get `well_known` blocks added from scan data. Existing fields are not modified.

## Implementation Order

1. **Document `well_known` in REGISTRY-JSON-FORMAT.md** — add Entity Well-Known section
2. **Write generator script** — reads `seed/well-known-scan.json` + disclosure entries, generates entity JSON files
3. **Add `well_known` to existing 14 entity entries** — from scan data
4. **Generate ~380 new entity entries** — minimal auto-generated entries
5. **Update namespace counts**
6. **Update CLAUDE.md** — mention `well_known` in entity type description

## What This Does NOT Include

- Parsing well-known file content (that's SecID-Entity-Data's job)
- Updating disclosure entries (security_txt already handled)
- Scheduled re-scanning (future automation)
- CSAF data in advisory entries (separate design if needed)
