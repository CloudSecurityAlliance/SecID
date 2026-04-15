# Format & Schema Metadata Design

**Date:** 2026-04-14
**Status:** Implemented
**Scope:** Registry URL objects, schema references, parsing instructions, auth documentation
**Affects:** Registry JSON format, API responses, v2.0 data serving

## Problem

The registry resolves SecIDs to URLs, but doesn't characterize *what you get* at those URLs. For the same CVE, you might get:
- An HTML webpage (cve.org) — human-readable, must scrape
- A JSON record (cvelistV5 on GitHub) — structured, CVE JSON 5.2.0 schema
- A JSON response (CVE Services API) — structured, same schema, different access pattern
- An enriched HTML page (NVD) — different data, must scrape

Without format metadata, clients can't filter for machine-readable sources, v2.0 can't know how to fetch and parse data, and nobody can audit how we derived our structured data from raw sources.

## Approach: Flat Fields + Schemas as Reference Entries (Approach C)

Three complementary pieces:

1. **URL object extensions** — four new optional fields on every match_node child `data` block
2. **Schemas as `reference` registry entries** — versioned, resolvable via SecID
3. **Parsing instructions as `reference` entries** — CSA-authored documents describing how to consume each format

## 1. URL Object Extensions

Every URL entry in a match_node child gains four new optional fields alongside the existing `content_type` and `format`:

| Field | Type | Description |
|-------|------|-------------|
| `parsability` | enum string | How processable is the data at this URL |
| `schema` | SecID string | What schema the data conforms to (absent for unstructured) |
| `parsing_instructions` | SecID string | Document describing how to consume this data |
| `auth` | string (free text) | How to authenticate/access this URL. Ranges from `"none"` to multi-paragraph explanations of custom account creation processes. Absent means "not yet documented." |

All four are optional. Absent means "not yet documented."

### `parsability` enum values

`parsability` describes **data format only** — how machine-readable the content is. Access patterns (API, bulk download, search interface) are captured separately in the source-level `urls` array `type` field.

| Value | Meaning | Example |
|-------|---------|---------|
| `"structured"` | Machine-readable with a defined schema. `schema` field applies. | CVE JSON from cvelistV5, CSAF advisory XML, NVD API responses |
| `"scraped"` | HTML/PDF/unstructured — processable but fragile, no stable schema | NVD detail page, vendor security portal |

**What counts as `schema`?** A formal JSON Schema file is ideal, but API documentation is also valid. If the NVD API returns well-structured JSON defined by their API docs, `schema` points at a reference entry for those docs. The field means "what defines the structure of this data" — not "is there a `.json` schema file."

### Example: Structured source

```json
{
  "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
  "description": "Raw CVE JSON from cvelistV5 (GitHub raw download)",
  "weight": 45,
  "data": {
    "url": "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/{year}/{bucket}/{id}.json",
    "content_type": "application/json",
    "parsability": "structured",
    "schema": "secid:reference/cve.org/cve-schema@5.2.0",
    "parsing_instructions": "secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5",
    "auth": "GitHub raw: standard rate limits, no auth. For higher limits, use a GitHub personal access token in the Authorization header."
  }
}
```

### Example: Scraped HTML source

```json
{
  "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
  "description": "NVD vulnerability detail page",
  "weight": 100,
  "data": {
    "url": "https://nvd.nist.gov/vuln/detail/{id}",
    "content_type": "text/html",
    "parsability": "scraped",
    "parsing_instructions": "secid:reference/cloudsecurityalliance.org/secid-parsers#nvd-html",
    "auth": "none"
  }
}
```

No `schema` field — there's nothing to reference for a scraped page.

### Source-level URL objects

The same four fields apply to **source-level `urls` arrays** — the access methods listed on each source's `data` block. This is where bulk downloads, APIs, search interfaces, and other access patterns live. Each URL object in the array gets enriched with format metadata:

```json
{
  "patterns": ["(?i)^cve$"],
  "data": {
    "official_name": "Common Vulnerabilities and Exposures",
    "urls": [
      {
        "type": "website",
        "url": "https://www.cve.org",
        "parsability": "scraped"
      },
      {
        "type": "api",
        "url": "https://cveawg.mitre.org/api",
        "parsability": "structured",
        "schema": "secid:reference/cve.org/cve-schema@5.2.0",
        "auth": "No auth required. Rate limited; request API key for higher limits.",
        "notes": "REST API, per-record access via /api/cve/{id}"
      },
      {
        "type": "bulk_data",
        "url": "https://github.com/CVEProject/cvelistV5",
        "parsability": "structured",
        "schema": "secid:reference/cve.org/cve-schema@5.2.0",
        "auth": "Public GitHub repo, no auth for clone/download",
        "notes": "One JSON file per CVE, organized by year/bucket directories"
      }
    ]
  }
}
```

**Two levels, same fields:**

| Level | Where | Purpose |
|-------|-------|---------|
| Source-level `urls` | `match_nodes[].data.urls[]` | Access methods for the source as a whole (API, bulk download, website, search) |
| Per-item child `data` | `match_nodes[].children[].data` | Resolution URLs for specific items (given an ID, here's the URL) |

The `type` field on source-level URLs identifies the access pattern. Existing values include `website`, `api`, `bulk_data`, `search`, `github`. These are already in use across registry entries — no new enum needed. Additional types can be added as encountered.

## 2. Schemas as `reference` Registry Entries

Schemas are documents published by authoritative organizations. They belong in `reference` — same as RFCs, arXiv papers, or specifications.

### Namespace convention

The namespace is the domain of the org that owns the schema:

| Schema | SecID |
|--------|-------|
| CVE JSON 5.2.0 | `secid:reference/cve.org/cve-schema@5.2.0` |
| CSAF 2.0 | `secid:reference/oasis-open.org/csaf@2.0` |
| OSV 1.3 | `secid:reference/ossf.github.io/osv-schema@1.3` |
| STIX 2.1 | `secid:reference/oasis-open.org/stix@2.1` |
| CVRF 1.2 | `secid:reference/icasi.org/cvrf@1.2` |

### Registry entry example

File: `registry/reference/org/cve.json`

The CVE Project's GitHub presence (github.com/CVEProject) falls under the `cve.org` namespace — it's the same organization.

```json
{
  "schema_version": "1.0",
  "namespace": "cve.org",
  "type": "reference",
  "status": "draft",
  "status_notes": null,

  "official_name": "CVE Program",
  "common_name": "CVE",
  "alternate_names": ["CVE Project", "Common Vulnerabilities and Exposures"],
  "notes": "The CVE Program maintains the CVE schema and related tooling. Operated by MITRE under contract with CISA. The cve.org website, CVE Services API, and CVEProject GitHub org are all part of this namespace.",
  "wikidata": null,
  "wikipedia": null,

  "urls": [
    {"type": "website", "url": "https://www.cve.org"},
    {"type": "github", "url": "https://github.com/CVEProject"}
  ],

  "match_nodes": [
    {
      "patterns": ["(?i)^cve-schema$"],
      "description": "CVE JSON Record Format schema",
      "weight": 100,
      "data": {
        "official_name": "CVE JSON Record Format",
        "description": "JSON schema defining the structure of CVE records, maintained by the CVE Project",
        "version_required": true,
        "urls": [
          {"type": "website", "url": "https://cveproject.github.io/cve-schema"},
          {"type": "github", "url": "https://github.com/CVEProject/cve-schema"}
        ]
      },
      "children": [
        {
          "patterns": ["^5\\.2(\\.0)?$"],
          "description": "CVE JSON 5.2.0 — current production schema",
          "weight": 100,
          "data": {
            "url": "https://github.com/CVEProject/cve-schema/blob/main/schema/CVE_Record_Format.json",
            "notes": "Schema accepts any 5.x record via dataVersion pattern ^5\\.(0|[1-9][0-9]*)(\\....)$. Default dataVersion is 5.2.0.",
            "examples": [
              {"input": "5.2.0", "url": "https://github.com/CVEProject/cve-schema/blob/main/schema/CVE_Record_Format.json"},
              {"input": "5.2", "url": "https://github.com/CVEProject/cve-schema/blob/main/schema/CVE_Record_Format.json"}
            ]
          }
        },
        {
          "patterns": ["^5\\.1(\\.0)?$"],
          "description": "CVE JSON 5.1.0",
          "weight": 100,
          "data": {
            "url": "https://github.com/CVEProject/cve-schema/blob/5.1.0/schema/CVE_Record_Format.json",
            "examples": [
              {"input": "5.1.0", "url": "https://github.com/CVEProject/cve-schema/blob/5.1.0/schema/CVE_Record_Format.json"}
            ]
          }
        },
        {
          "patterns": ["^5\\.0(\\.0)?$"],
          "description": "CVE JSON 5.0.0",
          "weight": 100,
          "data": {
            "url": "https://github.com/CVEProject/cve-schema/blob/v5.0.0/schema/CVE_Record_Format.json",
            "examples": [
              {"input": "5.0.0", "url": "https://github.com/CVEProject/cve-schema/blob/v5.0.0/schema/CVE_Record_Format.json"}
            ]
          }
        }
      ]
    }
  ]
}
```

### Key properties

- **`version_required: true`** — referencing `secid:reference/cve.org/cve-schema` without a version returns disambiguation guidance, not a schema URL.
- **Reuse across namespaces** — every advisory source publishing CVE JSON 5.2 records references the same `secid:reference/cve.org/cve-schema@5.2.0`. Schema version bump updates one entry.
- **Standard match_nodes** — the resolver walks the same tree structure as any other type, no special handling needed.
- **`cve.org` vs `mitre.org`** — CVE advisories are under `secid:advisory/mitre.org/cve` (MITRE operates the CVE Program). The CVE schema is under `secid:reference/cve.org/cve-schema` (the CVE Project publishes the schema at cve.org). Different namespaces because different organizational roles — MITRE is the operator, cve.org is the publication identity.

## 3. Parsing Instructions as `reference` Entries

Parsing instructions are CSA-authored documents. They live under `cloudsecurityalliance.org` as a collection called `secid-parsers`, with each instruction as a subpath item.

### SecID convention

```
secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5
secid:reference/cloudsecurityalliance.org/secid-parsers#csaf-2
secid:reference/cloudsecurityalliance.org/secid-parsers#osv-1
secid:reference/cloudsecurityalliance.org/secid-parsers#nvd-html
```

### What a parsing instruction document contains

Each document covers two perspectives:

| Perspective | Audience | Content |
|-------------|----------|---------|
| **Consuming** | v2.0 service, pipelines, AI agents | Field mappings, ID extraction, URL construction, auth/rate limits, error handling |
| **Provenance** | Contributors, auditors | How registry patterns were derived, edge cases encountered, decisions made |

### Document structure (example: `docs/parsers/cve-json-5.md`)

```markdown
# CVE JSON 5.x Parsing Instructions

**Schema:** secid:reference/cve.org/cve-schema@5.2.0
**Source URL pattern:** github.com/CVEProject/cvelistV5

## Key field mappings
- ID: `cveMetadata.cveId` (e.g., "CVE-2024-1234")
- State: `cveMetadata.state` — skip REJECTED and RESERVED records
- Description: `containers.cna.descriptions[0].value` (prefer lang: "en")
- Published: `cveMetadata.datePublished`

## Access patterns
- Per-record: raw.githubusercontent.com URL with {year}/{bucket}/{id}.json
- Bulk: git clone the cvelistV5 repo
- API: cveawg.mitre.org/api/cve/{id}

## Rate limits and auth
- GitHub raw: standard GitHub rate limits apply
- CVE Services API: no auth required, rate limited

## Provenance notes
- Patterns derived from cve-schema 5.2.0 default dataVersion
- The `^CVE-\d{4}-\d{4,}$` pattern allows >4 trailing digits
  (MITRE assigns 5- and 6-digit IDs in high-volume years)
- RESERVED CVEs have no CNA container — resolution valid, content absent
```

### Physical location

- **Now:** `docs/parsers/` directory in this repo. One markdown file per parser ID.
- **Registry entry:** `secid-parsers` match_node added to existing `registry/reference/org/cloudsecurityalliance.json`
- **Later:** Served from SecID API when the website/docs infrastructure grows

### Registry entry addition

Added to the existing CSA reference file (`registry/reference/org/cloudsecurityalliance.json`):

```json
{
  "patterns": ["(?i)^secid-parsers$"],
  "description": "SecID parsing instruction documents",
  "weight": 100,
  "data": {
    "official_name": "SecID Parsing Instructions",
    "description": "How to consume specific data schemas for SecID registry work and v2.0 data serving. Each document covers field mappings, access patterns, and provenance notes.",
    "urls": [
      {"type": "github", "url": "https://github.com/CloudSecurityAlliance/SecID/tree/main/docs/parsers"}
    ],
    "examples": ["cve-json-5", "csaf-2", "osv-1", "nvd-html"]
  },
  "children": [
    {
      "patterns": ["(?i)^cve-json-5$"],
      "description": "CVE JSON 5.x parsing instructions",
      "weight": 100,
      "data": {
        "url": "https://github.com/CloudSecurityAlliance/SecID/blob/main/docs/parsers/cve-json-5.md",
        "examples": [
          {"input": "cve-json-5", "url": "https://github.com/CloudSecurityAlliance/SecID/blob/main/docs/parsers/cve-json-5.md"}
        ]
      }
    }
  ]
}
```

## 4. API Response Changes

Minimal. The four new fields pass through on resolution results when present:

```json
{
  "secid": "secid:advisory/mitre.org/cve#CVE-2024-1234",
  "weight": 45,
  "url": "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2024/1xxx/CVE-2024-1234.json",
  "content_type": "application/json",
  "parsability": "structured",
  "schema": "secid:reference/cve.org/cve-schema@5.2.0",
  "parsing_instructions": "secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5",
  "auth": "GitHub raw: standard rate limits, no auth required for public repos"
}
```

### Filtering

Clients can filter results by parsability:

```
GET /api/v1/resolve?secid=secid:advisory/mitre.org/cve%23CVE-2024-1234&parsability=structured
```

Returns only results where `parsability` is `"structured"` — machine-readable sources with defined schemas.

### v2.0 implications

When v2.0 serves data, the service uses `schema` and `parsing_instructions` to:
1. Fetch data from the resolved URL
2. Parse it according to the instructions
3. Wrap it in the content metadata envelope (per ROADMAP.md Phase 3)

The format metadata designed here is the foundation v2.0 needs to decide how to process each source.

## Implementation Order

1. **Update REGISTRY-JSON-FORMAT.md** — document the four new fields on URL objects (at both source-level and per-item level), parsability enum, schema and parsing_instructions conventions
2. **Create `registry/reference/org/cve.json`** — first schema entry (CVE JSON 5.x)
3. **Create `docs/parsers/` directory** — first parser document (cve-json-5.md)
4. **Add `secid-parsers` match_node to `registry/reference/org/cloudsecurityalliance.json`**
5. **Annotate `registry/advisory/org/mitre.json`** — add parsability/schema/parsing_instructions to CVE URL children as proof-of-concept
6. **Update API-RESPONSE-FORMAT.md** — document passthrough fields and filtering
7. **Roll out incrementally** — annotate additional registry entries as time permits

## What This Does NOT Include

- Actual v2.0 data serving implementation (separate design)
- Format transformation or normalization (SecID doesn't transform data)
- Schema validation at query time (the registry says what schema to expect; it doesn't validate the remote data)
- Parsing instruction execution (that's the v2.0 service's concern)
