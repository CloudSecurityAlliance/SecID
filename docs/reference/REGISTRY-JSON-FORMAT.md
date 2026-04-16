# JSON Format Specification

This document defines the JSON format for SecID registry files. The registry currently uses YAML+Markdown (see [REGISTRY-FORMAT.md](REGISTRY-FORMAT.md)) for flexibility during exploration. This document specifies the target JSON format for v1.0+.

## Scope: Labeling and Finding

**SecID is about labeling and finding things. That's it.**

The registry contains:
- **Identity** - What is this thing called?
- **Resolution** - How do I find/access it?
- **Disambiguation** - How do I tell similar things apart?

The registry does NOT contain:
- **Enrichment** - Metadata about the thing (authors, categories, relationships)
- **Judgments** - Quality assessments, trust scores, recommendations
- **Relationships** - How things connect to each other

Enrichment and relationships belong in separate data layers that reference SecIDs.

## Regex Dialect Policy

Registry `match_nodes[].patterns` are canonicalized to **ECMAScript `RegExp`** syntax because production resolution runs in Cloudflare Workers (JavaScript runtime).

- Store one canonical pattern set in the registry. Do not store per-engine variants (`ecmascript`, `pcre`, `python`, etc.) in registry data.
- Non-JS runtimes should use tooling that translates/validates from canonical ECMAScript patterns.
- Keep patterns in a portable subset when possible.
- Legacy inline-flag patterns (for example `(?i)^cve$`) may still exist during migration; new/updated patterns should use ECMAScript-compatible syntax.

## Resolution Pipeline

This section explains how a SecID string is resolved to URLs using registry data.

**Important:** SecID parsing requires registry access. The registry defines what types, namespaces, and names are valid. This eliminates the need for a complex "banned characters" list - if it's not in the registry, it's not valid.

### Step 1: Parse the SecID String (Registry-Aware)

Parsing uses the registry to identify components:

```
secid:advisory/github.com/advisories/ghsa#GHSA-1234-5678-abcd
      ───┬─── ──────────┬──────────── ─┬── ─────────┬─────────
         │              │              │            └─ subpath
         │              │              └─ name (registry lookup, longest match)
         │              └─ namespace (domain, optionally with /path segments)
         └─ type (known list)
```

| Step | Component | How to Parse |
|------|-----------|--------------|
| 1 | scheme | Literal `secid:` |
| 2 | type | Match against 10 known values |
| 3 | namespace | **Shortest-to-longest matching** against registry. Namespaces can contain `/` (e.g., `github.com/advisories`). See [SPEC.md](../../SPEC.md) Section 4.3. |
| 4 | name | Match remaining path against name-level pattern nodes in `match_nodes` |
| 5 | version | If `@` present after name, match against version-level children |
| 6 | source qualifiers | Parse `?...` until `#` |
| 7 | subpath | If `#` present, match against subpath-level children |
| 8 | item_version | If `@` follows matched subpath pattern, match against deeper children for item version |
| 9 | item qualifiers | If `?` follows the item version (or matched identifier), parse as item-level qualifiers. |

**Why registry-aware?** Names can contain any characters (including `#`, `@`, `?`, `:`). The registry defines what names exist, and longest-match resolves ambiguity.

**Shortest-to-longest namespace resolution:** Since namespaces can contain `/`, the parser tries shortest namespace first against the registry, then progressively longer matches. See [SPEC.md](../../SPEC.md) Section 4.3 for details.

```
Input: secid:advisory/github.com/advisories/ghsa#GHSA-xxxx

After extracting type "advisory", remaining path: github.com/advisories/ghsa#GHSA-xxxx

Try namespace matches (shortest first):
  1. "github.com"              → exists in registry? Yes → candidate
  2. "github.com/advisories"   → exists in registry? Yes → longer candidate
  3. "github.com/advisories/ghsa" → exists? No → stop

Longest matching namespace: "github.com/advisories"
Remaining: "ghsa#GHSA-xxxx" → name="ghsa", subpath="GHSA-xxxx"
```

**Example with special characters:**
```
secid:advisory/vendor.com/weird#name:here#ID-2024
```
If registry has source `weird#name:here` in `advisory/vendor`, then:
- name = `weird#name:here`
- subpath = `ID-2024`

### Step 2: Lookup the Source

Using type, namespace, and name, find the source definition:

```
registry[type][namespace][name] → registry["advisory"]["mitre.org"]["cve"]
```

**Filesystem mapping:** The abstract `registry[type][namespace]` maps to a filesystem path via the reverse-DNS algorithm (see [SPEC.md](../../SPEC.md) Section 4.0):

| Lookup | Filesystem Path |
|--------|----------------|
| `registry["advisory"]["mitre.org"]` | `registry/advisory/org/mitre.json` |
| `registry["advisory"]["github.com/advisories"]` | `registry/advisory/com/github/advisories.json` |
| `registry["control"]["cloudsecurityalliance.org"]` | `registry/control/org/cloudsecurityalliance.json` |

### Step 3: Match Patterns via Tree Traversal

The resolver walks the **pattern tree** (`match_nodes`), matching each portion of the SecID against the corresponding tree level. At each level, all sibling patterns are tested — all matches are traversed to completion, not just the first.

```
secid:advisory/redhat.com/errata#RHSA-2026:1234

1. Name "errata" → match against name-level nodes → "^errata$" matches
2. No @version → skip version-level children
3. Subpath "RHSA-2026:1234" → match against subpath-level children → "^RHSA-\\d{4}:\\d+$" matches
4. Return data from both levels (source info + specific advisory URL)
```

**Chop and pass:** Each regex only sees its portion of the string. The resolver splits at grammar boundaries (`@`, `#`) and hands each piece to the appropriate tree level. No backtracking, no lookahead across levels.

**All matches traversed:** The resolver doesn't stop at the first match — it traverses all matching nodes to completion. Multiple matches are all returned (with weights). When sibling patterns overlap, `weight` helps consumers choose.

**Every level returns data.** Query `secid:advisory/redhat.com/errata` → returns errata info from the name-level node. Query `secid:advisory/redhat.com/errata#RHSA-2026:1234` → returns both the source info AND the specific advisory URL. Incomplete queries get the data available at their depth.

**Patterns match the complete input at each level**, not a substring. Patterns should be anchored with `^...$`.

### Step 4: Extract Variables (if needed)

For simple cases, the subpath is used directly as `{id}` in the URL template:

```json
{"type": "lookup", "url": "https://cve.org/CVERecord?id={id}"}
```

For complex URL structures where parts of the ID need transformation, patterns can specify a `variables` object:

```json
{
  "pattern": "^CWE-\\d+$",
  "url": "https://cwe.mitre.org/data/definitions/{number}.html",
  "variables": {
    "number": {
      "extract": "^CWE-(\\d+)$",
      "description": "Numeric ID portion (e.g., '79' from 'CWE-79')"
    }
  }
}
```

Each variable has:
- `extract` - Regex applied to the subpath. Capture groups `()` are numbered `{1}`, `{2}`, etc.
- `format` - (Optional) How to combine capture groups. Defaults to `{1}` (first group). Can include literals.
- `description` - Explains what this variable represents and how it's derived.

### Step 5: Build URL

Substitute variables into the URL template:

| Placeholder | Source | Example |
|-------------|--------|---------|
| `{id}` | Full subpath | `CVE-2024-1234` |
| `{version}` | From `@version` component | `4.0` |
| `{year}` | Extracted from subpath (if in variables) | `2024` |
| `{number}` | Extracted from subpath (if in variables) | `1234` |

**Result:** `https://cve.org/CVERecord?id=CVE-2024-1234`

### Variable Extraction Example

For CWE, the lookup URL needs just the number, not the full ID:

```json
{
  "pattern": "^CWE-\\d+$",
  "description": "CWE weakness ID",
  "url": "https://cwe.mitre.org/data/definitions/{number}.html",
  "variables": {
    "number": {
      "extract": "^CWE-(\\d+)$",
      "description": "Numeric ID portion (e.g., '79' from 'CWE-79')"
    }
  }
}
```

Resolution of `secid:weakness/mitre.org/cwe#CWE-79`:
1. Subpath: `CWE-79`
2. Pattern matches: `^CWE-\d+$` ✓
3. Extract variables: apply `number.extract` regex → first capture group `(\d+)` captures `79`
4. Build URL: `https://cwe.mitre.org/data/definitions/79.html`

### More Complex Variable Extraction

For the CVE GitHub repository, files are organized by year and a "bucket" (all but last 3 digits + `xxx`):

```json
{
  "pattern": "^CVE-\\d{4}-\\d{4,}$",
  "description": "CVE JSON record on GitHub",
  "url": "https://github.com/CVEProject/cvelistV5/blob/main/cves/{year}/{bucket}/{id}.json",
  "variables": {
    "year": {
      "extract": "^CVE-(\\d{4})-\\d+$",
      "description": "4-digit year (e.g., '2026' from 'CVE-2026-25010')"
    },
    "bucket": {
      "extract": "^CVE-\\d{4}-(\\d+)\\d{3}$",
      "format": "{1}xxx",
      "description": "All but last 3 digits + 'xxx' (e.g., '25xxx' from 'CVE-2026-25010')"
    },
    "id": {
      "extract": "^(CVE-\\d{4}-\\d+)$",
      "description": "Full CVE ID"
    }
  }
}
```

Resolution of `secid:advisory/mitre.org/cve#CVE-2026-25010`:
1. Subpath: `CVE-2026-25010`
2. Pattern matches ✓
3. Extract variables:
   - `year`: extract `(2026)` → `2026`
   - `bucket`: extract `(25)` from before last 3 digits, format `{1}xxx` → `25xxx`
   - `id`: extract `(CVE-2026-25010)` → `CVE-2026-25010`
4. Build URL: `https://github.com/CVEProject/cvelistV5/blob/main/cves/2026/25xxx/CVE-2026-25010.json`

## Design Principles

### AI-First Data Modeling

Traditional data formats optimized for software that needed deterministic, single values. SecID takes an AI-first approach:

- **Provide options with context** rather than forcing single "canonical" choices
- **Let AI reason** about which option fits the current need
- **Include metadata** that aids decision-making

Example: Instead of one lookup URL, provide multiple with context about when each is appropriate.

### Pattern Selection

Use the right pattern for the data:

| Situation | Pattern | Example |
|-----------|---------|---------|
| Fixed, small set of categories | Named fields | `official_name`, `common_name`, `alternate_names` |
| Open-ended, numerous categories | Arrays with type/context | `urls`, `match_nodes` |
| Identity/classification | Singular values | `namespace`, `type`, `status` |

**Why?** Named fields are self-documenting. An AI reads `official_name` and immediately knows what it is. Arrays with type require understanding a schema to interpret.

### Null vs Absent Convention

Distinguish between "no data exists" and "not yet researched":

| State | Representation | Meaning |
|-------|----------------|---------|
| Has data | `"field": "value"` | We have the information |
| No data exists | `"field": null` | We looked, nothing to find |
| Not researched | field absent | We haven't looked yet |

For arrays:
- `[]` (empty array) = we looked, there are none
- `null` = we looked, not applicable to this source
- absent = not yet researched

**Why?** This lets us track completeness. An absent field signals work to be done. A `null` signals confirmed absence.

### Per-Field Metadata (`checked` / `updated` / `note`)

Three optional metadata fields record *when* data was verified and *what* was observed:

| Field | Meaning | Changes when |
|-------|---------|--------------|
| `checked` | Date someone last verified the value is still accurate | Every verification pass, even if nothing changed |
| `updated` | Date the value last materially changed | Only when the actual data changes |
| `note` | Free-text observation about what was found during verification | When the observation changes |

Date format: `YYYY-MM-DD` (ISO 8601, no time component — day granularity is sufficient).

#### Naming Convention

| Context | Fields | Example |
|---------|--------|---------|
| **Source-level** (top of file) | `checked`, `updated`, `note` | `"checked": "2026-03-06"` |
| **Attached to a scalar field** | `field_checked`, `field_updated`, `field_note` | `"security_txt_checked": "2026-03-06"` |
| **Inside objects** (URL entries, etc.) | `checked`, `updated`, `note` | `{"url": "...", "checked": "2026-03-06"}` |

Source-level `checked`/`updated` apply to the entire registry entry. Inside objects, the fields are scoped by the object. The `_checked`/`_updated`/`_note` suffix "attaches" metadata to the scalar field it describes.

#### Extending the Null/Absent Convention

Timestamps make null values strictly more informative:

| State | Meaning |
|-------|---------|
| `"field": null` | We looked and found nothing (existing) |
| `"field": null, "field_checked": "2026-03-06"` | We looked **on this date** and found nothing |
| `"field"` absent | Not yet researched (existing, unchanged) |

Existing files without timestamps remain valid — absent timestamps mean "not yet tracked."

#### Examples

**Source-level timestamps:**

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

**URL object with verification note:**

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

**Scalar field — confirmed positive:**

```json
{
  "security_txt": "https://security.access.redhat.com/data/meta/v1/security.txt",
  "security_txt_checked": "2026-03-06",
  "security_txt_updated": "2026-03-06",
  "security_txt_note": "PGP signed, RFC 9116 compliant. Expires 2026-06-04."
}
```

**Scalar field — confirmed negative:**

```json
{
  "security_txt": null,
  "security_txt_checked": "2026-03-06",
  "security_txt_updated": "2026-03-06",
  "security_txt_note": "/.well-known/security.txt redirects to homepage"
}
```

See [TIMESTAMP-FIELDS.md](../proposals/TIMESTAMP-FIELDS.md) for full rationale, backwards compatibility analysis, and pilot files.

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

## Schema Structure

### Top-Level Fields

```json
{
  "schema_version": "1.0",
  "namespace": "mitre.org",
  "type": "advisory",
  "status": "published",
  "checked": "2026-03-06",
  "updated": "2026-01-15",

  "official_name": "MITRE Corporation",
  "common_name": "MITRE",
  "alternate_names": ["MITRE Corp"],
  "notes": "MITRE is a US nonprofit that operates FFRDCs. Created and maintains CVE, CWE, ATT&CK, CAPEC, and ATLAS. CISA contracts MITRE to operate the CVE Program. NVD (NIST) enriches CVE records with CVSS, CPE, CWE data. CNAs can assign CVE IDs under MITRE's program.",

  "urls": [
    {"type": "website", "url": "https://www.mitre.org"}
  ],

  "match_nodes": [
    { "patterns": ["^cve$"], "data": { ... }, "children": [ ... ] }
  ]
}
```

#### Identity Fields (singular, required)

| Field | Type | Description |
|-------|------|-------------|
| `schema_version` | string | JSON schema version for this file |
| `namespace` | string | Organization identifier — domain name (used in SecIDs). See namespace validation below. |
| `type` | string | SecID type: advisory, weakness, ttp, control, capability, methodology, disclosure, regulation, entity, reference |
| `status` | string | Registry entry status (see below) |
| `status_notes` | string \| null | Optional context about status (blockers, gaps, guidance for contributors) |
| `notes` | string \| null | Free-form context for AI and human readers (see Notes Fields below) |
| `alias_of` | string \| null | If present, this is an alias stub — namespace redirects to the value. No sources needed. |

#### Namespace Validation

Namespaces must be safe for filesystems, shells, and URLs while supporting international names.

**Allowed characters:**
- `a-z` (lowercase ASCII letters)
- `0-9` (ASCII digits)
- `-` (hyphen, not at start/end of DNS labels)
- `.` (period, as DNS label separator)
- Unicode letters (`\p{L}`) and numbers (`\p{N}`)

**Validation regex:** `^[\p{L}\p{N}]([\p{L}\p{N}._-]*[\p{L}\p{N}])?$`

**Not allowed within a segment:** Spaces, punctuation (except `-` and `.`), shell metacharacters.

**Per-segment validation:** Namespaces are domain names, optionally with `/`-separated path segments for platform sub-namespaces (e.g., `github.com/advisories`). `/` separates segments but is not allowed *within* a segment. Each segment between `/` must match the regex above.

**Examples:**
```
mitre.org                ✓  Domain name
nist.gov                 ✓  Government domain
github.com/advisories    ✓  Platform sub-namespace
aws.amazon.com           ✓  Subdomain
字节跳动.com              ✓  Unicode domain (ByteDance)
red_hat.com              ✗  Underscore not allowed in segment
```

**Alias stubs:** When `alias_of` is present, the entry is a redirect. Resolvers follow it to the target namespace. Used for Punycode/Unicode IDN equivalence (e.g., `xn--mnchen-3ya.de` → `münchen.de`). See [EDGE-CASES.md](EDGE-CASES.md) for details.

**Why these rules:**

1. **Filesystem safety** - Namespace segments become file paths (`registry/advisory/org/mitre.json`). Sub-namespaces become directories (`registry/advisory/com/github/advisories.json`). Avoiding shell metacharacters ensures repos work in Git across all platforms.

2. **Domain names are globally unique** - DNS already provides authoritative, collision-free identifiers. No centralized namespace assignment needed.

3. **Unicode for internationalization** - Organizations worldwide should use native language names. Unicode letter/number categories include all alphabets while excluding dangerous punctuation.

#### Status Values

Registry entry status reflects documentation completeness and review state:

| Status | Meaning | Field Requirements |
|--------|---------|-------------------|
| `proposed` | Suggested, minimal info | namespace, type, status, official_name required |
| `draft` | Being worked on | Any fields, actively researching |
| `pending` | Awaiting review | All fields present (value, `null`, or `[]`) - nothing absent |
| `published` | Reviewed and approved | Same as pending, but reviewed |

**Key principle:** `published` doesn't mean "complete" - it means "reviewed." Empty arrays and `null` values are valid and valuable - they show we looked and couldn't find anything, which exposes gaps and invites contribution.

**Examples:**
```json
"status": "published",
"status_notes": "Vendor has no public security page - urls intentionally empty"
```

```json
"status": "draft",
"status_notes": "Waiting for vendor response about official URL"
```

#### Disambiguation Fields (optional)

| Field | Type | Description |
|-------|------|-------------|
| `wikidata` | string[] | Wikidata Q-numbers for entity disambiguation (e.g., ["Q1116236"]) |
| `wikipedia` | string[] | Wikipedia article URLs for direct access |

**Why arrays?** Entities can map to multiple Wikidata entries (mergers, name changes, historical entries) or have multiple relevant Wikipedia articles (different languages, related topics). Arrays handle 0, 1, or more consistently.

**Why both fields?**
- `wikidata` - Stable, language-neutral identifiers. Links to all Wikipedia versions. Preferred for disambiguation.
- `wikipedia` - Direct access to human-readable context. Convenience for AI/humans without extra lookup. Fallback when no Wikidata exists.

#### Name Fields (singular/array)

| Field | Type | Description |
|-------|------|-------------|
| `official_name` | string | Official/legal name of the organization |
| `common_name` | string \| null | Common short name (e.g., "MITRE", "NIST") |
| `alternate_names` | string[] \| null | Other names for search/matching |

**Why separate fields?** Fixed, small set of name categories. Named fields are self-documenting and easier for AI to generate correctly.

#### Notes Fields

The `notes` field provides free-form context that doesn't fit into structured fields. It exists at two levels:

**Top-level `notes`** — context about the organization/namespace:
- History and background ("MITRE created and operates many canonical security identifier systems")
- Relationships to other organizations ("CISA contracts MITRE to operate the CVE Program")
- Why this namespace matters for security practitioners
- Organizational context that helps AI understand the source's role

**Source-level `notes`** — operational context about a specific data source:
- Resolution quirks ("Bugzilla accepts both bug IDs and CVE aliases; CVE aliases redirect")
- Data quality notes ("Quality of descriptions varies by CNA")
- Usage guidance ("The cvelistV5 GitHub repo has raw JSON records organized by year/bucket")
- Processing context ("NVD enriches CVE records but has processing backlogs")
- Historical context about format changes or migrations

**`notes` vs `description`:**

| Field | Purpose | Example |
|-------|---------|---------|
| `description` | What the source **is** (1-3 sentences) | "Red Hat publishes three types of errata: RHSA, RHBA, and RHEA." |
| `notes` | Everything else an AI needs to **use** it well | "RHSA advisories reference CVEs but may bundle multiple CVEs per advisory. Errata IDs contain colons (RHSA-2024:1234) — preserve the colon in subpaths. Red Hat's API requires authentication for some endpoints." |

**Format:** Markdown-allowed string. Can be multiple paragraphs. Keep it concise but don't artificially truncate — if an AI needs to know it to resolve or understand this source, put it here.

**Null vs absent:** Same convention as other fields. `null` means "we looked, nothing noteworthy." Absent means "not yet researched."

**What goes in `notes`:**
- Context migrated from YAML+Markdown body content
- Operational knowledge for resolution
- Quirks, edge cases, known issues
- Relationships to other sources (informational, not machine-readable)

**What does NOT go in `notes`:**
- Structured data that belongs in other fields (URLs, patterns, examples)
- Enrichment data (severity, affected products, authors)
- Relationship data that should be machine-readable (belongs in the relationship layer)

#### URLs

Two URL mechanisms exist in the registry:

**1. `urls` array** — used at top-level, in source-level `data`, and optionally on child nodes. For documentation, reference links, API endpoints, downloads — any URL that provides context.

```json
"urls": [
  {"type": "website", "url": "https://www.mitre.org"},
  {"type": "docs", "url": "https://docs.aws.amazon.com/...", "note": "Security chapter"},
  {"type": "bulk_data", "url": "https://example.com/data.zip", "format": "zip"},
  {"type": "docs", "url": "https://eur-lex.europa.eu/...", "lang": "fr", "note": "French text"}
]
```

**2. `data.url` string** — on child match_nodes only. THE resolution URL template with `{id}` variable substitution. One per child. For multiple resolution URLs (e.g., HTML page + JSON API), use multiple children matching the same pattern with different weights.

```json
"children": [
  {"patterns": ["^CVE-\\d{4}-\\d{4,}$"], "weight": 100, "data": {"url": "https://www.cve.org/CVERecord?id={id}"}},
  {"patterns": ["^CVE-\\d{4}-\\d{4,}$"], "weight": 50, "data": {"url": "https://api.example.com/{id}", "content_type": "application/json"}}
]
```

**URL entry fields:**

| Field | Required | Description |
|-------|----------|-------------|
| `url` | Yes | The actual URL |
| `type` | Yes | Category (see below) |
| `note` | No | Human/AI readable context explaining what this URL is for |
| `lang` | No | ISO 639-1 language code (e.g., "en", "fr", "de") |
| `format` | No | Expected content format: "html", "json", "pdf", "xml", "csv", "zip" |

**Common `type` values** (not a strict enum — use descriptive `note` for specifics):

| Type | Usage |
|------|-------|
| `website` | Main website or product page |
| `docs` | Documentation, guides, reference pages |
| `api` | API endpoint or API reference |
| `bulk_data` | Downloadable dataset (ZIP, JSON, XML, CSV) |
| `lookup` | Search/lookup URL for finding specific items |
| `security` | Security-specific page |
| `security_txt` | RFC 9116 security.txt file |
| `paper` | Research paper or publication |

Other type values are acceptable. The `note` field carries the real context for AI consumption — don't over-enumerate types.

### Match Nodes (Pattern Tree)

The `match_nodes` array replaces the old `sources` block. Each node in the tree matches a portion of the SecID string, returns data if matched, and optionally has children for deeper matching.

```json
"match_nodes": [
  {
    "patterns": ["^cve$"],
    "description": "Common Vulnerabilities and Exposures",
    "weight": 100,
    "data": {
      "official_name": "Common Vulnerabilities and Exposures",
      "common_name": "CVE",
      "alternate_names": null,
      "description": "...",
      "notes": "...",
      "urls": [ ... ],
      "version_required": false,
      "unversioned_behavior": "current",
      "version_disambiguation": null,
      "versions_available": null,
      "examples": [ ... ]
    },
    "children": [
      {
        "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
        "description": "Standard CVE ID format",
        "weight": 100,
        "data": {
          "url": "https://www.cve.org/CVERecord?id={id}"
        }
      }
    ]
  }
]
```

The name-level pattern (e.g., `^cve$`) replaces the literal source key. This is matched against the `name` component of the SecID: `secid:advisory/mitre.org/cve#CVE-2024-1234` → name `cve` matches `^cve$`.

#### Node Schema

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `patterns` | string[] | yes | One or more regex patterns (OR alternatives). All share the same children and data. |
| `description` | string | no | Human/AI-readable description of what this node matches |
| `weight` | integer | no | 0-200, default 0. Higher = more preferred. Returned with results, consumer decides. |
| `data` | object | no | Result data returned when this node matches (see below) |
| `children` | array | no | Child nodes for matching the next portion of the string (recursive) |

**Multiple patterns per node:** A node can have multiple regex alternatives. All share the same children and data. Used when a source is known by multiple names (e.g., `["^top10$", "^top-10$", "^owasp-top-10$"]`).

**Case sensitivity:** Patterns are case-sensitive by default. For case-insensitive matching, add explicit aliases in `patterns` (for common variants) rather than engine-specific inline flags. Convention: keep canonical lowercase name-level patterns and add targeted aliases only where needed. Subpath patterns should match canonical source case. No lossy normalization of input — the original is always preserved.

#### Node Data Object

The `data` object at each level contains whatever result information is appropriate for that depth. Common fields:

**Name-level data** (source metadata):

| Field | Type | Description |
|-------|------|-------------|
| `official_name` | string | Official name of the source |
| `common_name` | string \| null | Common short name |
| `alternate_names` | string[] \| null | Other names for search/matching |
| `description` | string | Brief summary of what this source is |
| `notes` | string \| null | Operational context for AI/human readers |
| `urls` | array | Source-level URLs (website, API, bulk_data) |
| `version_required` | boolean | See Version Resolution Fields |
| `unversioned_behavior` | string | See Version Resolution Fields |
| `version_disambiguation` | string \| null | See Version Resolution Fields |
| `versions_available` | array \| null | See Version Resolution Fields |
| `examples` | (string \| ExampleObject)[] | Representative identifier examples (see Examples) |

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

**Subpath-level data** (pattern-specific resolution):

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | Lookup URL with `{id}` placeholder |
| `format` | string | Response format (json, html, xml) |
| `content_type` | string | Full MIME type from HTTP Content-Type header (e.g., `text/html`, `application/json`). Used by the `?content_type=` qualifier to filter results by format. |
| `parsability` | string \| null | Data format: `"structured"` (machine-readable, has schema) or `"scraped"` (HTML/unstructured). Absent means not yet documented. |
| `schema` | string \| null | SecID reference to the schema this data conforms to (e.g., `secid:reference/cve.org/cve-schema@5.2.0`). Absent for scraped sources. A formal JSON Schema is ideal but API documentation also qualifies — the field means "what defines this data's structure." |
| `parsing_instructions` | string \| null | SecID reference to a parsing instruction document (e.g., `secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5`). Covers field mappings, access patterns, and provenance notes. |
| `auth` | string \| null | Free-text description of how to authenticate/access this URL. Ranges from `"none"` to multi-paragraph explanations. Absent means not yet documented. |
| `lang` | LangConfig | Language availability and URL substitution config. See Language Resolution below. |
| `note` | string | Context for when/why to use this URL |
| `type` | string | Category when source has multiple ID types |
| `known_values` | object | Enumeration of finite, stable values (see Known Values) |
| `lookup_table` | object | Map of IDs to URLs for non-computable URLs (see Lookup Table) |
| `variables` | object | Variable extraction for complex URL building (see Variable Extraction) |
| `examples` | (string \| ExampleObject)[] | Test fixtures with expected outputs (see Examples) |

**Capability-type data** (product security features — `type: capability`):

| Field | Type | Description |
|-------|------|-------------|
| `options` | array | Configuration options. Each entry has `value`, `name`, `description`, and optionally `setting`, `type`, `range`, `default`. |
| `default` | object \| string | Default value/configuration. Object with `value`, `since` (date of change), `note`. String for simple defaults. |
| `vendor_recommendation` | string | What the vendor recommends for this capability. Labeled as the vendor's opinion, not a universal requirement. |
| `audit` | object | Commands to check current configuration. Keys: `cli` (CLI command), `api` (API operation), `console` (UI path). May have additional keys like `cli_root`, `cli_all` for variations. |
| `configure` | object | Commands to set/enable the capability. Keys: `cli`, `api`, `console`, `terraform` (resource name), `cloudformation` (resource type). May have additional keys like `cli_create`, `cli_delete`. |
| `cross_references` | string[] | SecID strings for related capabilities in other services (e.g., `["secid:capability/amazon.com/aws/kms"]`). |
| `limits` | string | Service limits or quotas relevant to this capability. |
| `recent_changes` | string | Notable recent changes to defaults or behavior. |

Example:

```json
{
  "description": "S3 bucket default server-side encryption",
  "options": [
    {"value": "AES256", "name": "SSE-S3", "description": "Amazon S3 managed keys"},
    {"value": "aws:kms", "name": "SSE-KMS", "description": "AWS KMS managed keys"}
  ],
  "default": {"value": "AES256", "since": "2023-01-05", "note": "Enabled by default since January 2023"},
  "vendor_recommendation": "Use SSE-KMS for sensitive data",
  "audit": {
    "cli": "aws s3api get-bucket-encryption --bucket {bucket}",
    "api": "GetBucketEncryption",
    "console": "S3 → Bucket → Properties → Default encryption"
  },
  "configure": {
    "cli": "aws s3api put-bucket-encryption --bucket {bucket} --server-side-encryption-configuration ...",
    "terraform": "aws_s3_bucket_server_side_encryption_configuration",
    "cloudformation": "AWS::S3::Bucket BucketEncryption"
  },
  "urls": [
    {"type": "docs", "url": "https://docs.aws.amazon.com/...", "note": "AWS documentation"}
  ]
}
```

**Disclosure-type data** (vulnerability reporting — `type: disclosure`):

| Field | Type | Description |
|-------|------|-------------|
| `scope` | string | What products/projects this disclosure program covers. The key field — answers "does this program cover my product?" |
| `cve_program_role` | string | Role in the CVE Program (e.g., "CNA", "Root", "CNA-LR", "Top-Level Root", "Secretariat"). |
| `organization_type` | string | Organization classification (e.g., "Vendor", "Open Source", "CERT", "Bug Bounty Provider"). |
| `contacts` | array \| null | Reporting contacts. Each entry: `type` ("email", "web", "github_pvr"), `value` (address/URL), `note`, optionally `preferred` (boolean). |

Example:

```json
{
  "scope": "Vulnerabilities in open source projects affecting Red Hat software",
  "cve_program_role": "CNA (reports to Red Hat Root)",
  "organization_type": "Vendor, Open Source",
  "contacts": [
    {"type": "email", "value": "secalert@redhat.com", "note": "CNA contact email"},
    {"type": "web", "value": "https://access.redhat.com/security/team/contact", "note": "Security contact page"}
  ],
  "urls": [
    {"type": "docs", "url": "https://access.redhat.com/articles/...", "note": "Disclosure policy"}
  ]
}
```

#### Content-Type Verification

The `content_type` field records the MIME type that the URL's HTTP server actually returns in its `Content-Type` header. Values should be verifiable — CI can `HEAD` each URL and compare the header to the registry value.

Common values:
- `text/html` — web pages (cve.org record pages, GitHub blob views)
- `application/json` — JSON APIs and raw JSON files
- `application/pdf` — PDF documents (ISO standards, compliance reports)
- `text/xml` or `application/xml` — XML feeds and OVAL definitions

**`content_type` vs `format`:** The existing `format` field describes the *data format* of the content (e.g., a GitHub blob page has `"format": "json"` because it displays JSON data, but `"content_type": "text/html"` because the HTTP response is HTML). `content_type` reflects what the HTTP server returns; `format` reflects what the underlying data is. Both can coexist on the same node.

#### Language Resolution

The `lang` field declares that a child node's URL is available in multiple languages. It uses the `LangConfig` schema:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `available` | string[] | Yes | ISO 639-1 language codes (e.g., `["en", "de", "fr"]`) |
| `default` | string | Yes | Default language code (e.g., `"en"`) |
| `url_transform` | string | No | Transform applied to lang code in URL. `"uppercase"` → `"EN"`. Absent/null → as-is. |

The URL template uses `{lang}` as a placeholder:

```json
{
  "patterns": ["^art-\\d+(\\.[a-z])?$"],
  "description": "GDPR article reference",
  "weight": 100,
  "data": {
    "url": "https://eur-lex.europa.eu/legal-content/{lang}/TXT/HTML/?uri=CELEX:32016R0679",
    "content_type": "text/html",
    "lang": {
      "available": ["en", "de", "fr", "es", "it", "nl", "pt", "pl", "ro", "cs", "da", "el", "et", "fi", "ga", "hr", "hu", "lt", "lv", "mt", "sk", "sl", "sv", "bg"],
      "default": "en",
      "url_transform": "uppercase"
    }
  }
}
```

**Resolution behavior:**
- `?lang=de` → substitute `{lang}` with `DE` (uppercase transform), return URL with `lang: "de"` on result
- No `?lang=` → use default (`en`), substitute `{lang}` with `EN`, return with `lang: "en"` and +1 weight nudge
- `?lang=xx` (not in `available`) → `not_found` with available languages listed

**Why `url_transform`?** Some services use uppercase language codes in URLs (EUR-Lex uses `/legal-content/EN/...`). The transform lets the registry declare this so the API consumer always receives standard lowercase ISO 639-1 codes regardless of the upstream URL format.

#### Description and Notes (in Node Data)

The `description` field provides a brief summary of what this source is. The `notes` field provides deeper operational context:

```json
"sources": {
  "errata": {
    "official_name": "Red Hat Security Advisories",
    "description": "Red Hat publishes three types of errata: RHSA (Security Advisory) for security fixes, RHBA (Bug Advisory) for bug fixes, and RHEA (Enhancement Advisory) for new features. Most security work focuses on RHSA.",
    "notes": "Errata IDs contain colons (e.g., RHSA-2024:1234) — preserve the colon in subpaths. A single RHSA may bundle fixes for multiple CVEs. Red Hat's API at access.redhat.com/hydra/rest/securitydata provides machine-readable advisory data. Errata are also linked from Bugzilla entries. Numbering resets annually — the number after the colon is sequential within a year.",
    ...
  }
}
```

**`description` — what the source is (1-3 sentences):**
- Classes of objects the source contains (what is an RHSA vs RHBA vs RHEA?)
- When to use this source vs similar ones

**`notes` — everything else an AI needs to use it well:**
- Resolution quirks and edge cases
- Data quality observations
- Format details and gotchas
- Relationships to other sources (informational)
- Historical context about migrations or format changes
- Processing notes (backlogs, update frequency, authentication requirements)

**What does NOT go in either field:**
- Every individual instance (don't describe CVE-2024-1234)
- Data enrichment (severity, affected products, authors)
- Machine-readable relationships (belongs in the relationship layer)

**Rule of thumb:** `description` answers "what is this?" in a sentence. `notes` answers "what do I need to know to work with this effectively?"

#### URLs (array with context)

```json
"urls": [
  {"type": "website", "url": "https://cve.org"},
  {"type": "lookup", "url": "https://cve.org/CVERecord?id={id}", "note": "Human-readable page"},
  {"type": "lookup", "url": "https://cveawg.mitre.org/api/cve/{id}", "format": "json", "note": "API, richer data"},
  {"type": "bulk_data", "url": "https://github.com/CVEProject/cvelistV5", "format": "json"},
  {"type": "api", "url": "https://cveawg.mitre.org/api"}
]
```

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `type` | string | yes | URL category (see below) |
| `url` | string | yes | The URL, may contain `{placeholder}` templates |
| `format` | string | no | Response format: json, html, xml, csv, pdf |
| `note` | string | no | Context for AI: when/why to use, access instructions, auth requirements, download hints |

**URL type vocabulary:**

| Type | Description |
|------|-------------|
| `website` | Main website for humans |
| `docs` | Documentation pages |
| `search` | Search interface (human or programmatic) |
| `lookup` | Resolution URL with `{id}` placeholder |
| `api` | API endpoint |
| `bulk_data` | Bulk download location |
| `github` | GitHub repository |
| `paper` | Academic paper |
| `secid_api` | SecID REST API for this source (if different from main) |
| `secid_mcp` | SecID MCP endpoint for this source (if different from main) |

**Why an array?** Multiple URLs of the same type are common (e.g., primary and fallback lookup endpoints, multiple mirrors). The `note` field provides context to help AI choose appropriately.

#### URL Template Placeholders

URLs may contain placeholders for dynamic resolution:

| Placeholder | Description | Example |
|-------------|-------------|---------|
| `{id}` | Full identifier from subpath | `CVE-2024-1234` |
| `{num}` | Numeric portion of identifier | `1234` |
| `{year}` | Year component of identifier | `2024` |
| `{version}` | Version from `@version` component | `4.0` |
| `{item_version}` | Item version from `@item_version` after subpath | `a1b2c3d` |

#### Tree Matching Algorithm

The resolver walks the tree level by level, matching each portion of the SecID string:

1. **Name level:** Match the `name` component against `patterns` in each top-level `match_nodes` entry. All matching nodes are traversed.
2. **Version level:** If `@version` is present, match against children of the name-level node. If no version children exist, the version is passed through as `{version}` for URL templates.
3. **Subpath level:** If `#subpath` is present, match against children at the next level. These are the equivalent of the old `id_patterns`.
4. **Item version level:** If `@item_version` follows a matched subpath pattern, match against deeper children.

At each level, the node's `data` is collected into the result set. The resolver returns data from **every matched level**, not just the deepest.

**Key properties:**

- **Chop and pass.** Each regex only sees its portion of the string. The resolver splits at grammar boundaries (`@`, `#`) and passes each piece to the appropriate tree level. No backtracking, no lookahead across levels.
- **All matches traversed.** The resolver doesn't stop at the first match — all matching sibling nodes are traversed to completion. Multiple matches are returned with weights.
- **Case sensitivity per-pattern.** Use explicit alias patterns when case-insensitive behavior is needed. No lossy normalization of input.
- **Mutual exclusivity is checkable.** At each level, you can validate that sibling patterns don't overlap. When they do overlap, `weight` disambiguates.

For sources with multiple subpath types (old `id_patterns` with `type` field), each type becomes a sibling child node:

```json
"children": [
  {
    "patterns": ["^T\\d{4}(\\.\\d{3})?$"],
    "description": "ATT&CK technique",
    "data": {"type": "technique", "url": "https://attack.mitre.org/techniques/{id}/"}
  },
  {
    "patterns": ["^TA\\d{4}$"],
    "description": "ATT&CK tactic",
    "data": {"type": "tactic", "url": "https://attack.mitre.org/tactics/{id}/"}
  },
  {
    "patterns": ["^G\\d{4}$"],
    "description": "Threat group",
    "data": {"type": "group", "url": "https://attack.mitre.org/groups/{id}/"}
  }
]
```

For sources where different subpath patterns need different lookup URLs:

```json
"children": [
  {
    "patterns": ["^ALAS-\\d{4}-\\d+$"],
    "description": "Amazon Linux 1",
    "data": {"url": "https://alas.aws.amazon.com/{id}.html"}
  },
  {
    "patterns": ["^ALAS2-\\d{4}-\\d+$"],
    "description": "Amazon Linux 2",
    "data": {"url": "https://alas.aws.amazon.com/AL2/{id}.html"}
  },
  {
    "patterns": ["^ALAS2023-\\d{4}-\\d+$"],
    "description": "Amazon Linux 2023",
    "data": {"url": "https://alas.aws.amazon.com/AL2023/{id}.html"}
  }
]
```

#### Variables (in Node Data)

For complex URL structures where parts of the ID need transformation, a node's `data` can include a `variables` object:

Each key in `variables` is a placeholder name (e.g., `number`, `year`). The value is an object:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `extract` | string | yes | Regex with capture groups. Groups are numbered `{1}`, `{2}`, etc. |
| `format` | string | no | How to assemble the value from capture groups. Defaults to `{1}`. Can include literals. |
| `description` | string | yes | Explains what this variable is and how it's derived from the ID. |

Simple example (single capture group, default format):
```json
"variables": {
  "number": {
    "extract": "^CWE-(\\d+)$",
    "description": "Numeric ID portion (e.g., '79' from 'CWE-79')"
  }
}
```

Example with format (appending literal text):
```json
"variables": {
  "bucket": {
    "extract": "^CVE-\\d{4}-(\\d+)\\d{3}$",
    "format": "{1}xxx",
    "description": "All but last 3 digits + 'xxx' (e.g., '25xxx' from 'CVE-2026-25010')"
  }
}
```

#### Pattern Conventions

**Why anchored patterns?** Anchored patterns (`^CVE-\d{4}-\d{4,}$`) ensure the entire input at each level must match. Unanchored patterns would match substrings, allowing invalid input.

**Patterns match the human-readable (unencoded) form.** Write patterns matching what you see in the source documentation. `^Auditing Guidelines$` with a literal space, not `^Auditing%20Guidelines$`. Resolvers are responsible for decoding percent-encoded input before matching against patterns (see [SPEC.md](../../SPEC.md) Section 8.3).

**Sibling patterns are independent.** All sibling patterns at each level are tested independently. All matching patterns contribute results. When siblings overlap on the same input, `weight` helps consumers choose.

**Format patterns, not validity checks.** A pattern like `CVE-\d{4}-\d{4,}` tells you "this looks like a CVE ID" — whether that specific CVE actually exists is only known when you try to resolve it.

#### Known Values (in Node Data)

For patterns with finite, stable value sets, use `known_values` in the node's `data` to enumerate them with descriptions:

```json
{
  "patterns": ["^[A-Z]{2,3}$"],
  "description": "Control domain. Contains multiple controls.",
  "data": {
    "type": "domain",
    "known_values": {
      "IAM": "Identity & Access Management",
      "DSP": "Data Security & Privacy Lifecycle Management",
      "GRC": "Governance, Risk & Compliance",
      "SEF": "Security Incident Management, E-Discovery & Forensics"
    }
  },
  "children": [
    {
      "patterns": ["^[A-Z]{2,3}-\\d{2}$"],
      "description": "Specific control (e.g., IAM-12). Belongs to a domain.",
      "data": {"type": "control", "url": "https://ccm.cloudsecurityalliance.org/control/{id}"}
    }
  ]
}
```

**When to use `known_values`:**
- Finite, stable sets (control domains, advisory types, document categories)
- Classes that need disambiguation (what is IAM vs DSP vs GRC?)
- Important individual items worth enumerating (ISO standard numbers with their titles)

**When NOT to use:**
- Open-ended or growing sets (individual CVEs, specific controls)
- Values that are obvious from context (years, sequential numbers)

**Examples of good candidates:**

Control framework domains:
```json
"known_values": {
  "IAM": "Identity & Access Management",
  "DSP": "Data Security & Privacy Lifecycle Management"
}
```

Advisory types (Red Hat errata):
```json
"known_values": {
  "RHSA": "Security Advisory - security fixes, most commonly referenced",
  "RHBA": "Bug Advisory - non-security bug fixes",
  "RHEA": "Enhancement Advisory - new features"
}
```

ISO standard numbers with titles:
```json
"known_values": {
  "27001": "Information security management systems — Requirements",
  "27002": "Information security controls",
  "42001": "Artificial intelligence — Management system"
}
```

**Rule of thumb:** Ask "is this a class of objects?" If yes, describe it. For individual instances, only include in `known_values` when they're distinct enough to need disambiguation (ISO 27001 vs 42001) or when the set is small and stable.

#### Lookup Table (in Node Data)

When URLs can't be computed from the ID pattern alone — because the source uses inconsistent slugs, human-readable paths, or other non-derivable URL components — use `lookup_table` in the node's `data` to map each ID directly to its URL.

```json
{
  "patterns": ["^LLM\\d{2}$"],
  "description": "LLM Top 10 item number",
  "data": {
    "lookup_table": {
      "LLM01": {"url": "https://genai.owasp.org/llmrisk/llm01-prompt-injection/", "title": "Prompt Injection"},
      "LLM02": {"url": "https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/", "title": "Sensitive Information Disclosure"},
      "LLM03": {"url": "https://genai.owasp.org/llmrisk/llm032025-supply-chain/", "title": "Supply Chain"},
      "LLM04": {"url": "https://genai.owasp.org/llmrisk/llm042025-data-and-model-poisoning/", "title": "Data and Model Poisoning"},
      "LLM05": {"url": "https://genai.owasp.org/llmrisk/llm052025-improper-output-handling/", "title": "Improper Output Handling"},
      "LLM06": {"url": "https://genai.owasp.org/llmrisk/llm062025-excessive-agency/", "title": "Excessive Agency"},
      "LLM07": {"url": "https://genai.owasp.org/llmrisk/llm072025-system-prompt-leakage/", "title": "System Prompt Leakage"},
      "LLM08": {"url": "https://genai.owasp.org/llmrisk/llm082025-vector-and-embedding-weaknesses/", "title": "Vector and Embedding Weaknesses"},
      "LLM09": {"url": "https://genai.owasp.org/llmrisk/llm092025-misinformation/", "title": "Misinformation"},
      "LLM10": {"url": "https://genai.owasp.org/llmrisk/llm102025-unbounded-consumption/", "title": "Unbounded Consumption"}
    },
    "provenance": {
      "method": "Searched genai.owasp.org/llm-top-10/ listing page, then verified each individual URL. LLM01 slug lacks the year prefix that all other entries have — confirmed this is how OWASP published it, not a data entry error.",
      "date": "2026-02-22",
      "source_url": "https://genai.owasp.org/llm-top-10/"
    }
  }
}
```

Each `lookup_table` entry maps an ID to:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `url` | string | yes | The actual URL for this specific ID |
| `title` | string | no | Human-readable title (useful when it differs from the ID) |

The `provenance` object documents how the lookup table was built:

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `method` | string | yes | How the URLs were found and verified (searched site, scraped listing page, read documentation, etc.) |
| `date` | string | yes | When the lookup table was last verified (ISO 8601 date) |
| `source_url` | string | no | The page or API used to build the table |

**When to use `lookup_table`:**
- URLs contain human-readable slugs not derivable from the ID (`llm01-prompt-injection`)
- The source uses inconsistent URL patterns (LLM01 has no year, LLM02-10 do)
- URL structure changed between entries and can't be expressed as a single template
- Small, finite sets where enumerating every URL is practical

**When NOT to use:**
- URLs follow a consistent, computable pattern (use `url` with `{id}` template instead)
- The set is open-ended or very large (thousands of entries)

**Relationship to `known_values`:** A node's `data` can have both. `known_values` provides descriptions for disambiguation. `lookup_table` provides URLs for resolution. If you have `lookup_table` with `title` fields, `known_values` is redundant — but including both is fine since they serve different purposes (description vs resolution).

**Relationship to `url`:** If a node's `data` has both a `url` template and a `lookup_table`, the `lookup_table` takes priority for IDs it contains. The `url` template serves as a fallback for IDs not in the table (useful when most IDs follow a pattern but some exceptions exist).

**Why `provenance`?** Registry data is only trustworthy if you can verify it. Provenance records how the data was gathered so reviewers (human or AI) can re-verify it, and future maintainers know where to check for updates. Sources change their URL structures — provenance tells you where to look when that happens.

#### Version-Level Children (in the Tree)

For sources where different versions have different URL structures, add version-level children to the name-level node. These match against the `@version` component:

```json
{
  "patterns": ["^ccm$"],
  "description": "Cloud Controls Matrix",
  "data": { "..." : "..." },
  "children": [
    {
      "patterns": ["^4\\..*$"],
      "description": "Version 4.x",
      "data": {"url": "https://ccm.cloudsecurityalliance.org/v4/control/{id}"},
      "children": [
        {
          "patterns": ["^[A-Z]{2,3}-\\d{2}$"],
          "description": "Specific control",
          "data": {"type": "control"}
        }
      ]
    },
    {
      "patterns": ["^3\\..*$"],
      "description": "Version 3.x (legacy)",
      "data": {"url": "https://cloudsecurityalliance.org/artifacts/ccm-v3/{id}"}
    }
  ]
}
```

**Resolution example:** `secid:control/cloudsecurityalliance.org/ccm@4.0.1#IAM-12`
1. Name `ccm` → matches name-level node → returns source metadata
2. Version `4.0.1` → matches version-level child `^4\..*$` → returns v4 URL template
3. Subpath `IAM-12` → matches subpath-level child `^[A-Z]{2,3}-\d{2}$` → returns control type

**When not needed:** Most sources don't need version-level children. Use when:
- Different major versions have incompatible URL structures
- Legacy versions are hosted on different infrastructure

If URLs are predictable (just substitute `{version}`), use the `{version}` placeholder in the name-level data's URLs instead.

#### Item Version Children (Deeper in the Tree)

For sources where individual items can be versioned independently (e.g., git-backed databases, advisory revision histories), add deeper children within subpath-level nodes:

```json
{
  "patterns": ["^GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$"],
  "description": "GitHub Security Advisory ID",
  "data": {"url": "https://github.com/advisories/{id}"},
  "children": [
    {
      "patterns": ["^[0-9a-f]{7,40}$"],
      "description": "Git commit hash (short or full)",
      "data": {"url": "https://github.com/github/advisory-database/blob/{item_version}/advisories/github-reviewed/{id}.json"}
    }
  ]
}
```

**Resolution example:** `secid:advisory/github.com/advisories/ghsa#GHSA-jfh8-c2jp-5v3q@a1b2c3d`
1. Subpath `GHSA-jfh8-c2jp-5v3q` → matches subpath-level node → returns advisory URL
2. Item version `a1b2c3d` → matches deeper child `^[0-9a-f]{7,40}$` → returns commit-specific URL

**When not needed:** Most sources don't need item version children. Use when:
- The source is git-backed and items change over time (GHSA, CVE list repo)
- Advisory revisions are tracked independently (Red Hat errata revisions)
- Content is wiki-like with edit history

**When not appropriate:**
- The version is already part of the ID itself (arXiv `2303.08774v2`)
- The whole source is versioned as a unit (OWASP Top 10 `@2021`)
- Items are immutable once published

#### Version Resolution Fields (in Name-Level Node Data)

These fields live in the name-level node's `data` object. They control what happens when a SecID omits the `@version` component. Most sources don't need them — the default behavior ("return current") is correct for sources like CVE where IDs are unique across all versions.

| Field | Type | Description |
|-------|------|-------------|
| `version_required` | boolean, optional | `true` if unversioned references are ambiguous. Default: `false`. When `true`, the resolver should not silently return a single version. |
| `unversioned_behavior` | string, optional | One of `"current"` (default), `"current_with_history"`, `"all_with_guidance"`. How the resolver should respond when version is omitted. |
| `version_disambiguation` | string, optional | AI-readable instructions for determining which version was intended based on available context (publication date, ID format, surrounding references, etc.). |
| `versions_available` | array, optional | Array of objects documenting known versions. Each object has: `version` (string, required), `release_date` (string, ISO date, optional), `status` (string: `"current"`, `"superseded"`, `"draft"`, optional), `note` (string, optional). |

##### Unversioned Behavior Values

| Value | Resolver Response | Use When |
|-------|-------------------|----------|
| `"current"` | Return the current/latest version. No ambiguity signal. | IDs are unique across all versions, or the source doesn't meaningfully version (CVE, CWE, GHSA). This is the default. |
| `"current_with_history"` | Return the current version, plus a note that other versions exist. | The current version is a sensible default, but older versions are still actively referenced (CCM, ISO 27001). |
| `"all_with_guidance"` | Return **all matching versions** with disambiguation instructions from `version_disambiguation`. | Item identifiers are reused across versions with different meanings (OWASP Top 10 — A01 means something different in each edition). |

##### Disambiguation Guidance

The `version_disambiguation` field provides instructions for AI clients to determine the intended version from surrounding context. Write it as if explaining to another AI agent that has access to the referring document but doesn't know which version was meant:

```json
"version_disambiguation": "Versions are released by year. Match the version whose release year is closest to but not after the referring document's publication date. If no date context is available, use the latest version (2021). Note: item numbering restarts with each version — A01 in one version is unrelated to A01 in another."
```

This implements the **"AI on both ends" pattern**: the registry provides reasoning guidance (server side), and the AI client applies it to the local context it has access to (publication dates, surrounding references, document age). Neither side alone can resolve the ambiguity.

##### Versions Available

```json
"versions_available": [
  {
    "version": "2021",
    "release_date": "2021-09-24",
    "status": "current",
    "note": "Major restructuring from 2017. A01 changed from Injection to Broken Access Control."
  },
  {
    "version": "2017",
    "release_date": "2017-11-20",
    "status": "superseded",
    "note": "Still widely referenced in existing documentation and certifications."
  }
]
```

##### Version Resolution Examples

**OWASP Top 10 (`all_with_guidance`):**

```json
{
  "official_name": "OWASP Top 10",
  "version_required": true,
  "unversioned_behavior": "all_with_guidance",
  "version_disambiguation": "Versions are released by year. Match the version whose release year is closest to but not after the referring document's publication date. If no date context is available, use the latest version (2021). Note: item numbering restarts with each version — A01 in one version is unrelated to A01 in another.",
  "versions_available": [
    {"version": "2021", "release_date": "2021-09-24", "status": "current"},
    {"version": "2017", "release_date": "2017-11-20", "status": "superseded"},
    {"version": "2013", "release_date": "2013-06-12", "status": "superseded"}
  ]
}
```

**CCM (`current_with_history`):**

```json
{
  "official_name": "Cloud Controls Matrix",
  "version_required": false,
  "unversioned_behavior": "current_with_history",
  "versions_available": [
    {"version": "4.0", "release_date": "2021-06-01", "status": "current"},
    {"version": "3.0.1", "release_date": "2017-06-01", "status": "superseded", "note": "Still referenced in older compliance documentation."}
  ]
}
```

**CVE (default — no fields needed):** When `version_required` and `unversioned_behavior` are absent, the default behavior is `current` — just resolve the identifier. CVE IDs are globally unique and don't need version context.

#### Examples

The `examples` field accepts both bare strings and structured ExampleObject entries:

```json
"examples": ["CVE-2024-1234", "CVE-2021-44228", "CVE-2023-44487"]
```

Bare strings show valid ID formats. Helps humans and AI understand what identifiers look like.

**Structured ExampleObject** adds expected outputs, turning examples into test fixtures:

```json
"examples": [
  {
    "input": "DSA-5678-1",
    "variables": {"num": "5678", "year": "2024"},
    "url": "https://www.debian.org/security/2024/dsa-5678",
    "note": "Year 2024: 5678 >= 5593 (2024 start) and < 5839 (2025 start)"
  }
]
```

**ExampleObject Fields:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `input` | string | yes | The identifier string to resolve |
| `version` | string | no | Version context for versioned sources (e.g., `"2.0"` for CSF) |
| `variables` | object | no | Expected variable extraction results (keys match the `variables` definition) |
| `url` | string | no | Expected resolved URL |
| `note` | string | no | Human/AI context explaining resolution logic or notable behavior |

**Placement conventions:**

- **Source-level** `data.examples`: bare strings (representative samples of valid identifiers)
- **Child-level** (leaf pattern nodes) `data.examples`: structured ExampleObjects where variables, URLs, or notes add value. Bare strings remain valid at any level.

Structured examples support future resolver conformance testing — each ExampleObject is a positive test case with expected outputs that a resolver implementation can verify against.

## Reference Type Fields

For `type: reference` (documents, papers, standards), additional fields help with identity:

```json
{
  "type": "reference",
  "namespace": "nist.gov",

  "title": "AI RMF",
  "full_title": "Artificial Intelligence Risk Management Framework",

  "sources": { ... }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `title` | string | Short/common title |
| `full_title` | string \| null | Complete formal title |

**Note:** Standard identifier systems (DOI, ISBN, ISSN, arXiv, etc.) are **namespaces**, not fields:

```
secid:reference/doi.org/10.6028/NIST.AI.100-1
secid:reference/isbn.org/978-0-123456-78-9
secid:reference/arxiv.org/2303.08774
secid:reference/ietf.org/rfc9110
```

If a document has both a human-readable reference (`secid:reference/nist.gov/ai-rmf`) and a DOI (`secid:reference/doi.org/10.6028/NIST.AI.100-1`), the equivalence relationship between them belongs in the **relationship layer**, not the registry.

## Entity Type

Entity files describe organizations and their products/services. They use the same `match_nodes` structure as other types — the resolver walks the same tree for `secid:entity/redhat.com/openshift` as it does for `secid:advisory/redhat.com/errata#RHSA-2024:1234`.

Entity match_nodes typically use literal patterns (`^openshift$`) rather than regex patterns, since entity names are fixed strings rather than structured identifier formats. However, the same tree shape enables hierarchical navigation — products can have sub-products as children.

### Entity-specific data fields

Entity match_nodes may include these additional fields in `data`:

| Field | Type | Description |
|-------|------|-------------|
| `issues_type` | string | SecID type this entity issues (`"advisory"`, `"weakness"`, `"ttp"`, `"control"`) |
| `issues_namespace` | string | SecID namespace for those identifiers |
| `established` | integer | Year the organization was established |

### Example

```json
{
  "namespace": "redhat.com",
  "type": "entity",
  "official_name": "Red Hat, Inc.",
  "common_name": "Red Hat",
  "notes": "Enterprise open source company, part of IBM since 2019.",

  "urls": [
    {"type": "website", "url": "https://www.redhat.com"},
    {"type": "security", "url": "https://access.redhat.com/security/"}
  ],

  "match_nodes": [
    {
      "patterns": ["^openshift$"],
      "description": "Red Hat OpenShift",
      "weight": 100,
      "data": {
        "official_name": "Red Hat OpenShift",
        "description": "Kubernetes-based container platform (general/umbrella term)",
        "urls": [
          {"type": "website", "url": "https://www.redhat.com/en/technologies/cloud-computing/openshift"},
          {"type": "docs", "url": "https://docs.openshift.com"}
        ],
        "examples": ["openshift"]
      },
      "children": [
        {
          "patterns": ["^rosa$"],
          "description": "Red Hat OpenShift Service on AWS",
          "weight": 100,
          "data": {
            "official_name": "Red Hat OpenShift Service on AWS",
            "common_name": "ROSA",
            "description": "Managed OpenShift on AWS (jointly operated with AWS)",
            "urls": [
              {"type": "website", "url": "https://www.redhat.com/en/technologies/cloud-computing/openshift/aws"},
              {"type": "aws", "url": "https://aws.amazon.com/rosa/"}
            ],
            "examples": ["rosa"]
          }
        }
      ]
    },
    {
      "patterns": ["^rhel$"],
      "description": "Red Hat Enterprise Linux",
      "weight": 100,
      "data": {
        "official_name": "Red Hat Enterprise Linux",
        "description": "Enterprise Linux distribution",
        "urls": [
          {"type": "website", "url": "https://www.redhat.com/en/technologies/linux-platforms/enterprise-linux"}
        ],
        "examples": ["rhel"]
      }
    }
  ]
}
```

The `match_nodes` approach means the resolver doesn't need entity-specific logic. `secid:entity/redhat.com/openshift` walks the tree the same way `secid:advisory/redhat.com/errata` does. Products with variants (OpenShift → ROSA, ARO) naturally become parent → children relationships.

Cross-references between entities and their publications (e.g., "MITRE operates CVE") are documented via `issues_type` and `issues_namespace` fields in entity data, but the formal equivalence belongs in the relationship layer.

## Complete Example

```json
{
  "schema_version": "1.0",
  "namespace": "mitre.org",
  "type": "advisory",
  "status": "published",
  "status_notes": null,

  "official_name": "MITRE Corporation",
  "common_name": "MITRE",
  "alternate_names": ["The MITRE Corporation"],
  "notes": "MITRE is a US nonprofit that operates federally funded research and development centers (FFRDCs). In cybersecurity, MITRE created and maintains CVE, CWE, ATT&CK, CAPEC, and ATLAS — foundational identifier systems and frameworks used across the industry. CISA contracts MITRE to operate the CVE Program. CNAs (CVE Numbering Authorities) can assign CVE IDs under MITRE's program.",
  "wikidata": ["Q1116236"],
  "wikipedia": ["https://en.wikipedia.org/wiki/Mitre_Corporation"],

  "urls": [
    {"type": "website", "url": "https://www.mitre.org"}
  ],

  "match_nodes": [
    {
      "patterns": ["^cve$"],
      "description": "Common Vulnerabilities and Exposures",
      "weight": 100,
      "data": {
        "official_name": "Common Vulnerabilities and Exposures",
        "common_name": "CVE",
        "alternate_names": null,
        "description": "The canonical vulnerability identifier system, operated by MITRE under contract with CISA.",
        "notes": "CVE is the canonical identifier — other advisories cross-reference CVEs. NVD (NIST) enriches CVE records with CVSS scores, CPE entries, and CWE mappings, but NVD enrichment has processing backlogs. Quality of CVE descriptions varies by CNA — some provide detailed technical analysis, others provide minimal information. The cvelistV5 GitHub repo contains raw JSON records organized by year and bucket directories.",
        "urls": [
          {"type": "website", "url": "https://cve.org"},
          {"type": "api", "url": "https://cveawg.mitre.org/api"},
          {"type": "bulk_data", "url": "https://github.com/CVEProject/cvelistV5"}
        ],
        "examples": ["CVE-2024-1234", "CVE-2021-44228", "CVE-2026-25010"]
      },
      "children": [
        {
          "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
          "description": "Standard CVE ID format",
          "weight": 100,
          "data": {
            "url": "https://cve.org/CVERecord?id={id}",
            "content_type": "text/html"
          }
        },
        {
          "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
          "description": "CVE JSON record on GitHub (web view)",
          "weight": 50,
          "data": {
            "url": "https://github.com/CVEProject/cvelistV5/blob/main/cves/{year}/{bucket}/{id}.json",
            "format": "json",
            "content_type": "text/html",
            "note": "GitHub web page showing CVE JSON record from cvelistV5 repository",
            "variables": {
              "year": {
                "extract": "^CVE-(\\d{4})-\\d+$",
                "description": "4-digit year (e.g., '2026' from 'CVE-2026-25010')"
              },
              "bucket": {
                "extract": "^CVE-\\d{4}-(\\d+)\\d{3}$",
                "format": "{1}xxx",
                "description": "All but last 3 digits + 'xxx' (e.g., '25xxx' from 'CVE-2026-25010')"
              },
              "id": {
                "extract": "^(CVE-\\d{4}-\\d+)$",
                "description": "Full CVE ID"
              }
            }
          }
        },
        {
          "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
          "description": "CVE raw JSON from GitHub",
          "weight": 45,
          "data": {
            "url": "https://raw.githubusercontent.com/CVEProject/cvelistV5/main/cves/{year}/{bucket}/{id}.json",
            "format": "json",
            "content_type": "application/json",
            "note": "Raw CVE JSON file — direct download, no HTML wrapper",
            "variables": {
              "year": {
                "extract": "^CVE-(\\d{4})-\\d+$",
                "description": "4-digit year (e.g., '2026' from 'CVE-2026-25010')"
              },
              "bucket": {
                "extract": "^CVE-\\d{4}-(\\d+)\\d{3}$",
                "format": "{1}xxx",
                "description": "All but last 3 digits + 'xxx' (e.g., '25xxx' from 'CVE-2026-25010')"
              },
              "id": {
                "extract": "^(CVE-\\d{4}-\\d+)$",
                "description": "Full CVE ID"
              }
            }
          }
        },
        {
          "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
          "description": "CVE JSON via API",
          "weight": 50,
          "data": {
            "url": "https://cveawg.mitre.org/api/cve/{id}",
            "format": "json",
            "content_type": "application/json",
            "note": "API endpoint, richer data than web page"
          }
        }
      ]
    }
  ]
}
```

## Complete Example: Sub-Namespace

This example shows a namespace with a `/`-separated path portion (`github.com/advisories`). The namespace maps to `registry/advisory/com/github/advisories.json` via the reverse-DNS algorithm.

```json
{
  "schema_version": "1.0",
  "namespace": "github.com/advisories",
  "type": "advisory",
  "status": "draft",
  "status_notes": null,

  "official_name": "GitHub Advisory Database",
  "common_name": "GitHub Advisories",
  "alternate_names": null,
  "notes": "GitHub's advisory database aggregates vulnerabilities across package ecosystems. Acquired npm's advisory database. Advisories are community-editable and cross-reference CVEs.",

  "urls": [
    {"type": "website", "url": "https://github.com/advisories"}
  ],

  "match_nodes": [
    {
      "patterns": ["^ghsa$"],
      "description": "GitHub Security Advisories",
      "weight": 100,
      "data": {
        "official_name": "GitHub Security Advisories",
        "common_name": "GHSA",
        "alternate_names": null,
        "description": "GitHub-native security advisory identifiers for vulnerabilities in open source packages.",
        "notes": "GHSA IDs use a base-32 encoding scheme (lowercase letters and digits). Most GHSAs have a corresponding CVE, but some ecosystem-specific advisories may not. The advisory-database GitHub repo contains the raw advisory data in OSV format.",
        "urls": [
          {"type": "website", "url": "https://github.com/advisories"},
          {"type": "api", "url": "https://api.github.com/advisories"},
          {"type": "bulk_data", "url": "https://github.com/github/advisory-database"}
        ],
        "examples": ["GHSA-jfh8-c2jp-5v3q", "GHSA-8v63-cqqc-6r2c"]
      },
      "children": [
        {
          "patterns": ["^GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$"],
          "description": "GitHub Security Advisory ID",
          "weight": 100,
          "data": {"url": "https://github.com/advisories/{id}"}
        }
      ]
    }
  ]
}
```

**Key differences from simple namespace:**
- `namespace` includes a path: `github.com/advisories` (not just `github.com`)
- Filesystem path uses reverse-DNS for domain + appended path: `registry/advisory/com/github/advisories.json`
- SecID references use the full namespace: `secid:advisory/github.com/advisories/ghsa#GHSA-jfh8-c2jp-5v3q`

## Migration from YAML+Markdown

The current YAML frontmatter maps to JSON as follows:

| YAML Field | JSON Field | Notes |
|------------|------------|-------|
| `full_name` | `official_name` | Renamed for clarity |
| `website` | `urls[] where type=website` | Now array with context |
| `sources` (keyed object) | `match_nodes` (array of pattern nodes) | Literal keys become `patterns` regex values (ECMAScript-compatible) |
| `id_pattern` / `id_patterns` | `children` on name-level nodes | Subpath patterns become child nodes |
| `id_routing` | `data.url` on child nodes | Merged into node data |
| `version_patterns` | Version-level children | Intermediate tree level between name and subpath |
| `item_version_patterns` | Deeper children within subpath nodes | Same nesting, just deeper in the tree |
| `urls.lookup` | `urls[] where type=lookup` | Now array with context |
| `wikidata` | `wikidata[]` | Now array |
| `wikipedia` | `wikipedia[]` | New field, array |
| `status` | `status` | New values: proposed, draft, pending, published |
| `status_notes` | `status_notes` | New field |
| Markdown body | `notes` (top-level and/or in node data) | Narrative content migrates to `notes` fields |

### Fields Moved to Data Layer

The following fields were considered but belong in the enrichment/relationship data layer, not the registry:

| Field | Reason |
|-------|--------|
| `operator` | Relationship (who operates what) |
| `superseded_by` | Relationship + judgment (X replaced Y) |
| `deprecated_by` | Relationship (source X replaced by Y) |
| `deprecated_date` | Temporal enrichment |
| `established` | Temporal enrichment |
| `versions[]` | Replaced by version-level children in the pattern tree for resolution; version catalog is enrichment |

The registry focuses on identity, resolution, and disambiguation. Relationships and lifecycle metadata belong in separate data layers that reference SecIDs.

The Markdown body content (narrative documentation) migrates to `notes` fields — top-level `notes` for organizational context, source-level `notes` for source-specific operational knowledge. No companion `.md` files needed; everything lives in one `.json` file.

## Multi-Level Pattern Example

For sources with hierarchical identifiers, the tree naturally mirrors the hierarchy. Domain → control → section becomes parent → child → grandchild:

```json
{
  "schema_version": "1.0",
  "namespace": "cloudsecurityalliance.org",
  "type": "control",
  "status": "published",

  "official_name": "Cloud Security Alliance",
  "common_name": "CSA",
  "notes": "CSA is a nonprofit focused on cloud security best practices. Publishes multiple control frameworks (CCM, AICM) and runs the STAR certification program. Also publishes research on AI security through its AI Safety Initiative.",
  "wikidata": ["Q5135329"],

  "urls": [
    {"type": "website", "url": "https://cloudsecurityalliance.org"}
  ],

  "match_nodes": [
    {
      "patterns": ["^ccm$"],
      "description": "Cloud Controls Matrix",
      "weight": 100,
      "data": {
        "official_name": "Cloud Controls Matrix",
        "common_name": "CCM",
        "description": "Security controls framework organized by domains. Domains contain controls, controls may have implementation sections.",
        "notes": "CCM v4 has 17 domains and 197 controls. Domain codes are 2-3 uppercase letters (e.g., IAM, DSP). Control IDs append a dash and two-digit number (e.g., IAM-12). Some controls have implementation sections with a dot suffix (e.g., IAM-12.1). CCM is available as a spreadsheet download — no direct per-control URL for all versions.",
        "urls": [
          {"type": "website", "url": "https://cloudsecurityalliance.org/research/cloud-controls-matrix"},
          {"type": "docs", "url": "https://cloudsecurityalliance.org/artifacts/cloud-controls-matrix-v4"}
        ],
        "version_required": false,
        "unversioned_behavior": "current_with_history",
        "versions_available": [
          {"version": "4.0", "release_date": "2021-06-01", "status": "current"},
          {"version": "3.0.1", "release_date": "2017-06-01", "status": "superseded", "note": "Still referenced in older compliance documentation."}
        ],
        "examples": [
          "secid:control/cloudsecurityalliance.org/ccm#IAM",
          "secid:control/cloudsecurityalliance.org/ccm#IAM-12",
          "secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12",
          "secid:control/cloudsecurityalliance.org/ccm#IAM-12.1"
        ]
      },
      "children": [
        {
          "patterns": ["^4\\..*$"],
          "description": "Version 4.x",
          "data": {"url": "https://ccm.cloudsecurityalliance.org/v4/control/{id}"},
          "children": [
            {
              "patterns": ["^[A-Z]{2,3}$"],
              "description": "Control domain (e.g., IAM). Contains multiple controls.",
              "data": {
                "type": "domain",
                "known_values": {
                  "A&A": "Audit & Assurance",
                  "AIS": "Application & Interface Security",
                  "BCR": "Business Continuity Management & Operational Resilience",
                  "CCC": "Change Control & Configuration Management",
                  "CEK": "Cryptography, Encryption & Key Management",
                  "DCS": "Datacenter Security",
                  "DSP": "Data Security & Privacy Lifecycle Management",
                  "GRC": "Governance, Risk & Compliance",
                  "HRS": "Human Resources",
                  "IAM": "Identity & Access Management",
                  "IPY": "Interoperability & Portability",
                  "IVS": "Infrastructure & Virtualization Security",
                  "LOG": "Logging & Monitoring",
                  "SEF": "Security Incident Management, E-Discovery & Forensics",
                  "STA": "Supply Chain Management, Transparency & Accountability",
                  "TVM": "Threat & Vulnerability Management",
                  "UEM": "Universal Endpoint Management"
                }
              }
            },
            {
              "patterns": ["^[A-Z]{2,3}-\\d{2}$"],
              "description": "Specific control (e.g., IAM-12). Belongs to a domain.",
              "data": {"type": "control", "url": "https://ccm.cloudsecurityalliance.org/v4/control/{id}"}
            },
            {
              "patterns": ["^[A-Z]{2,3}-\\d{2}\\.\\d{1,2}$"],
              "description": "Control section (e.g., IAM-12.1). Implementation detail within a control.",
              "data": {"type": "section"}
            }
          ]
        },
        {
          "patterns": ["^3\\..*$"],
          "description": "Version 3.x (legacy)",
          "data": {"url": "https://cloudsecurityalliance.org/artifacts/ccm-v3/{id}"}
        },
        {
          "patterns": ["^[A-Z]{2,3}$"],
          "description": "Control domain (unversioned fallback)",
          "data": {"type": "domain"}
        },
        {
          "patterns": ["^[A-Z]{2,3}-\\d{2}$"],
          "description": "Specific control (unversioned fallback)",
          "data": {"type": "control"}
        },
        {
          "patterns": ["^[A-Z]{2,3}-\\d{2}\\.\\d{1,2}$"],
          "description": "Control section (unversioned fallback)",
          "data": {"type": "section"}
        }
      ]
    }
  ]
}
```

**Key points:**
- The tree mirrors the hierarchy naturally: name → version → subpath
- `known_values` on the domain-level node (finite, stable set)
- Version-level children route to different URL structures (v4 vs v3)
- Subpath children within version children for version-specific resolution
- Unversioned fallback children handle queries without `@version`
- Not every node needs a URL (domain-level returns known_values without a lookup URL)

## Schema Versioning

The `schema_version` field allows for future evolution. Parsers should check this field and handle unknown versions gracefully.

Current version: `1.0` (draft)
