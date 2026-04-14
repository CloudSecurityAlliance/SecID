# Format & Schema Metadata Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add format/schema metadata to SecID registry URL objects so clients can identify what data format they'll get, which schema it follows, and how to parse it.

**Architecture:** Four new optional fields (`parsability`, `schema`, `parsing_instructions`, `auth`) on both source-level URL objects and per-item match_node children. Schemas and parsing instructions are first-class `reference` registry entries resolvable via SecID. No code changes — this is a spec-only repo. Implementation is documentation updates + new registry JSON files + parser instruction documents.

**Tech Stack:** JSON (registry files), Markdown (docs, parser instructions). No build system.

**Spec:** `docs/superpowers/specs/2026-04-14-format-schema-metadata-design.md`

---

### Task 1: Document new fields in REGISTRY-JSON-FORMAT.md

**Files:**
- Modify: `docs/reference/REGISTRY-JSON-FORMAT.md:629-635` (subpath-level data table)
- Modify: `docs/reference/REGISTRY-JSON-FORMAT.md:622` (source-level urls description)

This is the authoritative spec for the JSON registry format. All four new fields need to be documented at both levels where they appear.

- [ ] **Step 1: Add the four new fields to the subpath-level data table**

In `docs/reference/REGISTRY-JSON-FORMAT.md`, find the "Subpath-level data" table (around line 629). After the existing `content_type` row, add:

```markdown
| `parsability` | string \| null | Data format: `"structured"` (machine-readable, has schema) or `"scraped"` (HTML/unstructured). Absent means not yet documented. |
| `schema` | string \| null | SecID reference to the schema this data conforms to (e.g., `secid:reference/cve.org/cve-schema@5.2.0`). Absent for scraped sources. A formal JSON Schema is ideal but API documentation also qualifies — the field means "what defines this data's structure." |
| `parsing_instructions` | string \| null | SecID reference to a parsing instruction document (e.g., `secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5`). Covers field mappings, access patterns, and provenance notes. |
| `auth` | string \| null | Free-text description of how to authenticate/access this URL. Ranges from `"none"` to multi-paragraph explanations. Absent means not yet documented. |
```

- [ ] **Step 2: Add the same four fields to the source-level urls description**

Find the "Name-level data" table (around line 613). The `urls` row says `Source-level URLs (website, API, bulk_data)`. After this table, add a new subsection:

```markdown
**Source-level URL object fields:**

Each object in the `urls` array has a `type` and `url` field. The following optional fields can be added to characterize the data available at that URL:

| Field | Type | Description |
|-------|------|-------------|
| `type` | string | Access pattern identifier: `website`, `api`, `bulk_data`, `search`, `github`, `download`, `lookup`. Additional types can be added as encountered. |
| `url` | string | The URL |
| `parsability` | string \| null | `"structured"` or `"scraped"`. Same semantics as subpath-level. |
| `schema` | string \| null | SecID schema reference. Same semantics as subpath-level. |
| `parsing_instructions` | string \| null | SecID parsing instructions reference. Same semantics as subpath-level. |
| `auth` | string \| null | Free-text auth description. Same semantics as subpath-level. |
| `notes` | string \| null | Additional context about this access method. |
| `format` | string \| null | Short format hint (e.g., `"json"`, `"xml"`). Legacy field — prefer `parsability` + `schema` for new entries. |
| `note` | string \| null | Legacy alias for `notes`. Use `notes` for new entries. |
```

- [ ] **Step 3: Add a "Format Metadata" section explaining the design**

Before the "Schema Structure" section (around line 344), add a new section:

```markdown
## Format Metadata

Registry URL objects carry optional metadata describing the data format available at each URL. This serves three purposes:

1. **Client filtering** — API clients can request only structured (machine-readable) results
2. **v2.0 data serving** — the service needs to know how to fetch and parse each source
3. **Provenance** — documents how registry entries were derived from raw source data

### Fields

Four optional fields appear on both source-level URL objects and per-item match_node children:

- **`parsability`**: `"structured"` (machine-readable with a schema) or `"scraped"` (HTML/unstructured). Describes data format only — access patterns (API, bulk, search) are captured in the URL `type` field.
- **`schema`**: A SecID string referencing the schema (e.g., `secid:reference/cve.org/cve-schema@5.2.0`). Schemas are `reference` registry entries — versioned, resolvable. Absent for scraped sources.
- **`parsing_instructions`**: A SecID string referencing a parsing instruction document (e.g., `secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5`). CSA-authored documents covering field mappings, access patterns, and provenance.
- **`auth`**: Free text describing authentication requirements. Ranges from `"none"` to multi-paragraph instructions for complex access processes.

All four are optional. Absent means "not yet documented" — entries can be annotated incrementally.

### What counts as a schema?

A formal JSON Schema file is ideal, but API documentation qualifies too. If the NVD API returns structured JSON defined by their API docs, `schema` points at a reference entry for those docs. The field means "what defines this data's structure" — not "is there a `.json` schema file."

### Two levels, same fields

| Level | Where | Purpose |
|-------|-------|---------|
| Source-level `urls` | `match_nodes[].data.urls[]` | Access methods for the source as a whole |
| Per-item child `data` | `match_nodes[].children[].data` | Resolution URLs for specific items |
```

- [ ] **Step 4: Verify the document parses cleanly**

Run: `markdownlint docs/reference/REGISTRY-JSON-FORMAT.md 2>/dev/null || echo "no linter, visual check only"`

Visually confirm the new tables render correctly and don't break existing content.

- [ ] **Step 5: Commit**

```bash
git add docs/reference/REGISTRY-JSON-FORMAT.md
git commit -m "Document format metadata fields in REGISTRY-JSON-FORMAT.md

Add parsability, schema, parsing_instructions, and auth fields to both
source-level and per-item URL object documentation. Add Format Metadata
section explaining the design and what qualifies as a schema reference."
```

---

### Task 2: Create CVE schema reference entry

**Files:**
- Create: `registry/reference/org/cve.json`

This is the first schema-as-reference entry. It creates the `cve.org` namespace in the `reference` type with the CVE JSON Record Format schema (versions 5.0, 5.1, 5.2).

- [ ] **Step 1: Create the registry file**

Create `registry/reference/org/cve.json` with this content:

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
  "notes": "The CVE Program maintains the CVE schema and related tooling. Operated by MITRE under contract with CISA. The cve.org website, CVE Services API, and CVEProject GitHub org are all part of this namespace. GitHub verified domain: cve.org on github.com/CVEProject.",
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
        "common_name": null,
        "alternate_names": ["CVE JSON Schema", "CVE Record Format"],
        "description": "JSON schema defining the structure of CVE records, maintained by the CVE Project. Used by CVE Services API, cvelistV5 repository, and all CNAs submitting CVE records.",
        "notes": "The schema accepts any 5.x record — the dataVersion pattern is ^5\\.(0|[1-9][0-9]*)(\\....)$. Older 5.0 and 5.1 records remain valid against the latest schema. The repo also contains bundled schemas, example files, and documentation.",
        "version_required": true,
        "unversioned_behavior": "disambiguation",
        "version_disambiguation": "Multiple schema versions exist. Specify @5.2 for the current production schema, @5.1 for the prior version, or @5.0 for the original 5.x release.",
        "versions_available": ["5.2.0", "5.1.0", "5.0.0"],
        "urls": [
          {"type": "website", "url": "https://cveproject.github.io/cve-schema", "parsability": "scraped"},
          {"type": "github", "url": "https://github.com/CVEProject/cve-schema"}
        ],
        "examples": ["5.2.0", "5.2", "5.1.0", "5.0.0"]
      },
      "children": [
        {
          "patterns": ["^5\\.2(\\.0)?$"],
          "description": "CVE JSON 5.2.0 — current production schema",
          "weight": 100,
          "data": {
            "url": "https://github.com/CVEProject/cve-schema/blob/main/schema/CVE_Record_Format.json",
            "content_type": "application/json",
            "parsability": "structured",
            "notes": "Default dataVersion is 5.2.0. Schema on main branch.",
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
            "content_type": "application/json",
            "parsability": "structured",
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
            "content_type": "application/json",
            "parsability": "structured",
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

- [ ] **Step 2: Validate JSON parses correctly**

```bash
python3 -c "import json; json.load(open('registry/reference/org/cve.json')); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add registry/reference/org/cve.json
git commit -m "Add CVE schema reference entry (cve.org namespace)

First schema-as-reference registry entry. CVE JSON Record Format schema
versions 5.0, 5.1, 5.2 with version_required: true. Namespace is cve.org
per GitHub verified domain on github.com/CVEProject."
```

---

### Task 3: Create first parsing instruction document

**Files:**
- Create: `docs/parsers/cve-json-5.md`

This is the first CSA-authored parsing instruction document, covering both the consuming perspective (field mappings, access patterns) and provenance perspective (how registry patterns were derived).

- [ ] **Step 1: Create the parsers directory and document**

Create `docs/parsers/cve-json-5.md` with this content:

```markdown
# CVE JSON 5.x Parsing Instructions

**SecID:** `secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5`
**Schema:** `secid:reference/cve.org/cve-schema@5.2.0`
**Source:** [github.com/CVEProject/cvelistV5](https://github.com/CVEProject/cvelistV5)

## Overview

CVE records in JSON format following the CVE JSON Record Format schema (5.x). Published by the CVE Program, operated by MITRE under contract with CISA. Individual records are authored by CNAs (CVE Numbering Authorities).

## Key Field Mappings

| Purpose | JSON Path | Notes |
|---------|-----------|-------|
| CVE ID | `cveMetadata.cveId` | Format: `CVE-YYYY-NNNNN+` |
| State | `cveMetadata.state` | `PUBLISHED`, `REJECTED`, or `RESERVED` |
| Date published | `cveMetadata.datePublished` | ISO 8601 |
| Date updated | `cveMetadata.dateUpdated` | ISO 8601 |
| CNA org | `cveMetadata.assignerShortName` | Short name of the assigning CNA |
| Description (EN) | `containers.cna.descriptions[].value` | Filter for `lang: "en"` |
| Affected products | `containers.cna.affected[]` | Product/vendor/version info |
| References | `containers.cna.references[]` | URLs with tags |
| CVSS scores | `containers.cna.metrics[]` | May contain cvssV3_1, cvssV3_0, cvssV2_0 |
| ADP data | `containers.adp[]` | Authorized Data Publishers (e.g., CISA vulnrichment) |

### Record States

- **PUBLISHED** — has CNA container with vulnerability data. Process normally.
- **REJECTED** — was published but later withdrawn. `containers.cna.rejectedReasons[]` explains why. Resolution still valid (URL works), but content indicates rejection.
- **RESERVED** — ID assigned but no data published yet. No CNA container. Resolution valid, content absent.

## Access Patterns

### Per-record via GitHub raw download

```
https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/{year}/{bucket}/{id}.json
```

Variables extracted from CVE ID (e.g., `CVE-2024-1234`):
- `year`: `2024` (extracted via `^CVE-(\d{4})-\d+$`)
- `bucket`: `1xxx` (all but last 3 digits + `xxx`, via `^CVE-\d{4}-(\d+)\d{3}$` → `{1}xxx`)
- `id`: `CVE-2024-1234` (full ID)

### Per-record via CVE Services API

```
https://cveawg.mitre.org/api/cve/{id}
```

Returns the same JSON schema. Richer metadata than the raw file (includes change history).

### Bulk download

Clone the cvelistV5 repo: `git clone https://github.com/CVEProject/cvelistV5.git`

Directory structure: `cves/{year}/{bucket}/{id}.json`

~250,000+ records. Full clone is ~2GB. Use shallow clone or sparse checkout for targeted access.

## Rate Limits and Auth

| Access Method | Auth Required | Rate Limits |
|---------------|--------------|-------------|
| GitHub raw | No | Standard GitHub rate limits (60/hr unauthenticated, 5000/hr with token) |
| CVE Services API | No | Rate limited (exact limits not published, be respectful) |
| Git clone | No | Standard GitHub limits |

For higher GitHub rate limits, use a personal access token in the `Authorization: Bearer {token}` header.

## Provenance Notes

- The `^CVE-\d{4}-\d{4,}$` regex pattern allows 4+ trailing digits. MITRE has assigned 5- and 6-digit IDs in high-volume years (e.g., `CVE-2024-12345`, `CVE-2023-123456`).
- The `{bucket}` variable extraction (`(\d+)\d{3}` → `{1}xxx`) follows the cvelistV5 directory convention exactly.
- Schema version 5.2.0 is backward-compatible with 5.1 and 5.0 records. The `dataVersion` field in each record indicates which version it was authored against.
- The `containers.adp[]` array was added in schema 5.x. CISA's vulnrichment project adds ADP containers with enriched CVSS scores and CWE mappings.
```

- [ ] **Step 2: Commit**

```bash
git add docs/parsers/cve-json-5.md
git commit -m "Add CVE JSON 5.x parsing instructions

First parsing instruction document. Covers field mappings, access patterns
(raw GitHub, API, bulk clone), rate limits, and provenance notes for how
registry patterns were derived from the CVE JSON schema."
```

---

### Task 4: Add secid-parsers match_node to CSA reference file

**Files:**
- Modify: `registry/reference/org/cloudsecurityalliance.json`

Add the `secid-parsers` source as a new match_node in the existing CSA reference file, alongside the existing `artifacts` match_node.

- [ ] **Step 1: Add the secid-parsers match_node**

In `registry/reference/org/cloudsecurityalliance.json`, the file structure is:

```
{
  ...
  "match_nodes": [
    { "patterns": ["(?i)^artifacts$"], ... }    ← existing, ends near bottom of file
  ]
}
```

The file ends with `    }\n  ]\n}`. Add a new match_node after the `artifacts` node (before the closing `]` of `match_nodes`). Insert a comma after the closing `}` of the artifacts node, then add:

```json
    {
      "patterns": ["(?i)^secid-parsers$"],
      "description": "SecID parsing instruction documents — how to consume specific data schemas for registry work and v2.0 data serving",
      "weight": 100,
      "data": {
        "official_name": "SecID Parsing Instructions",
        "common_name": null,
        "alternate_names": null,
        "description": "CSA-authored documents covering field mappings, access patterns, rate limits, and provenance notes for each data format SecID works with.",
        "notes": "Each document serves two audiences: (1) consumers (v2.0 service, pipelines, AI agents) who need to know how to parse the data, and (2) contributors/auditors who want to understand how registry patterns were derived from raw sources.",
        "urls": [
          {"type": "github", "url": "https://github.com/CloudSecurityAlliance/SecID/tree/main/docs/parsers"}
        ],
        "examples": ["cve-json-5"]
      },
      "children": [
        {
          "patterns": ["(?i)^cve-json-5$"],
          "description": "CVE JSON 5.x parsing instructions",
          "weight": 100,
          "data": {
            "url": "https://github.com/CloudSecurityAlliance/SecID/blob/main/docs/parsers/cve-json-5.md",
            "content_type": "text/markdown",
            "parsability": "structured",
            "examples": [
              {"input": "cve-json-5", "url": "https://github.com/CloudSecurityAlliance/SecID/blob/main/docs/parsers/cve-json-5.md"}
            ]
          }
        }
      ]
    }
```

- [ ] **Step 2: Validate JSON parses correctly**

```bash
python3 -c "import json; json.load(open('registry/reference/org/cloudsecurityalliance.json')); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
git add registry/reference/org/cloudsecurityalliance.json
git commit -m "Add secid-parsers match_node to CSA reference entry

Registers secid:reference/cloudsecurityalliance.org/secid-parsers as a
resolvable source. First child: cve-json-5 parsing instructions."
```

---

### Task 5: Annotate mitre.json CVE source with format metadata

**Files:**
- Modify: `registry/advisory/org/mitre.json`

This is the proof-of-concept: add `parsability`, `schema`, `parsing_instructions`, and `auth` to the existing CVE source-level URLs and per-item children.

- [ ] **Step 1: Add format metadata to source-level urls (line 30-34)**

Replace the current `urls` array in the CVE match_node `data` block:

```json
        "urls": [
          {"type": "website", "url": "https://www.cve.org"},
          {"type": "api", "url": "https://cveawg.mitre.org/api"},
          {"type": "bulk_data", "url": "https://github.com/CVEProject/cvelistV5", "format": "json"}
        ],
```

With:

```json
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
            "auth": "No auth required. Rate limited; be respectful.",
            "notes": "REST API, per-record access via /api/cve/{id}"
          },
          {
            "type": "bulk_data",
            "url": "https://github.com/CVEProject/cvelistV5",
            "parsability": "structured",
            "schema": "secid:reference/cve.org/cve-schema@5.2.0",
            "auth": "Public GitHub repo, no auth for clone/download. Use token for higher rate limits.",
            "notes": "One JSON file per CVE, organized by year/bucket directories. ~250K+ records, ~2GB full clone."
          }
        ],
```

- [ ] **Step 2: Add format metadata to child 1 — cve.org HTML page (line 38-50)**

Add `parsability` and `auth` to the first child's `data` block. After `"content_type": "text/html",` add:

```json
            "parsability": "scraped",
            "auth": "none",
```

- [ ] **Step 3: Add format metadata to child 2 — GitHub web view (line 51-83)**

Add after `"content_type": "text/html",` (line 58):

```json
            "parsability": "scraped",
            "auth": "none",
```

This child returns an HTML page that *shows* JSON — but the response itself is text/html (GitHub's web UI), so it's `scraped` not `structured`.

- [ ] **Step 4: Add format metadata to child 3 — GitHub raw JSON (line 84-116)**

Add after `"content_type": "application/json",` (line 91):

```json
            "parsability": "structured",
            "schema": "secid:reference/cve.org/cve-schema@5.2.0",
            "parsing_instructions": "secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5",
            "auth": "No auth required. Standard GitHub rate limits (60/hr unauthenticated, 5000/hr with token).",
```

- [ ] **Step 5: Add format metadata to child 4 — CVE API (line 117-127)**

Add after `"content_type": "application/json",` (line 124):

```json
            "parsability": "structured",
            "schema": "secid:reference/cve.org/cve-schema@5.2.0",
            "parsing_instructions": "secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5",
            "auth": "No auth required. Rate limited.",
```

- [ ] **Step 6: Validate JSON parses correctly**

```bash
python3 -c "import json; json.load(open('registry/advisory/org/mitre.json')); print('OK')"
```

Expected: `OK`

- [ ] **Step 7: Commit**

```bash
git add registry/advisory/org/mitre.json
git commit -m "Annotate CVE sources with format metadata (proof-of-concept)

Add parsability, schema, parsing_instructions, and auth to all CVE
source-level URLs and per-item children in mitre.json. First registry
entry to use the new format metadata fields."
```

---

### Task 6: Update API-RESPONSE-FORMAT.md

**Files:**
- Modify: `docs/reference/API-RESPONSE-FORMAT.md:376-383` (resolution result table)

Document the four new fields on resolution results and the `parsability` query parameter for filtering.

- [ ] **Step 1: Add new fields to the resolution result table**

In `docs/reference/API-RESPONSE-FORMAT.md`, find the "Resolution result" table (line 376). After the `url` row, add:

```markdown
| `content_type` | string | MIME type of the response (e.g., `text/html`, `application/json`). Present when the registry specifies it. |
| `parsability` | string | Data format: `"structured"` or `"scraped"`. Present when the registry specifies it. |
| `schema` | string | SecID reference to the data schema (e.g., `secid:reference/cve.org/cve-schema@5.2.0`). Present for structured sources. |
| `parsing_instructions` | string | SecID reference to parsing instruction document. Present when the registry specifies it. |
| `auth` | string | Free-text auth description. Present when the registry specifies it. |
```

- [ ] **Step 2: Add filtering section**

After the "Cross-Source Search" section (before "Corrected Queries"), add:

```markdown
## Filtering by Parsability

Clients can filter resolution results to only structured (machine-readable) sources:

```
GET /api/v1/resolve?secid=secid:advisory/mitre.org/cve%23CVE-2026-1234&parsability=structured
```

Returns only results where `parsability` is `"structured"`. This filters out HTML pages and other unstructured sources, returning only machine-readable URLs with defined schemas.

When `parsability` is combined with `content_type`, both filters apply:

```
GET /api/v1/resolve?secid=secid:advisory/mitre.org/cve%23CVE-2026-1234&parsability=structured&content_type=application/json
```

Returns only structured JSON sources — excludes HTML pages and structured XML sources.
```

- [ ] **Step 3: Add an example resolution result with format metadata**

After the existing Level 1 resolution example (line 108-125), add a note:

```markdown
**With format metadata:** Resolution results include format metadata when the registry specifies it:

```json
{
  "secid_query": "secid:advisory/mitre.org/cve#CVE-2026-1234",
  "status": "found",
  "results": [
    {
      "secid": "secid:advisory/mitre.org/cve#CVE-2026-1234",
      "weight": 100,
      "url": "https://www.cve.org/CVERecord?id=CVE-2026-1234",
      "content_type": "text/html",
      "parsability": "scraped",
      "auth": "none"
    },
    {
      "secid": "secid:advisory/mitre.org/cve#CVE-2026-1234",
      "weight": 45,
      "url": "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/2026/1xxx/CVE-2026-1234.json",
      "content_type": "application/json",
      "parsability": "structured",
      "schema": "secid:reference/cve.org/cve-schema@5.2.0",
      "parsing_instructions": "secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5",
      "auth": "No auth required. Standard GitHub rate limits."
    }
  ]
}
```

Format metadata fields are omitted from results when the registry doesn't specify them.
```

- [ ] **Step 4: Commit**

```bash
git add docs/reference/API-RESPONSE-FORMAT.md
git commit -m "Document format metadata in API response format

Add parsability, schema, parsing_instructions, auth to resolution result
fields. Add parsability query parameter for filtering. Add example showing
format metadata on resolution results."
```

---

### Task 7: Update namespace counts and verify

**Files:**
- Run: `scripts/update-counts.sh`

After adding `registry/reference/org/cve.json`, the reference count needs updating.

- [ ] **Step 1: Run the count update script**

```bash
./scripts/update-counts.sh
```

- [ ] **Step 2: Verify the reference count increased**

The reference count should have gone from 34 to 35 (one new file: `cve.json`).

```bash
grep -A1 'Reference' CLAUDE.md | head -2
```

- [ ] **Step 3: Commit if counts changed**

```bash
git add CLAUDE.md README.md
git commit -m "Update namespace counts after adding cve.org reference entry"
```

---

### Task 8: Update design spec status

**Files:**
- Modify: `docs/superpowers/specs/2026-04-14-format-schema-metadata-design.md:4`

- [ ] **Step 1: Update status**

Change line 4 from:
```
**Status:** Approved design, pending implementation
```
To:
```
**Status:** Implemented
```

- [ ] **Step 2: Commit**

```bash
git add docs/superpowers/specs/2026-04-14-format-schema-metadata-design.md
git commit -m "Mark format metadata design as implemented"
```
