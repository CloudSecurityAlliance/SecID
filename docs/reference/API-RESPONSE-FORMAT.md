# API Response Format

This document specifies the JSON response format for the SecID REST API (`/api/v1/`) and the data structures shared with the MCP server (`/mcp/`).

## Design Principles

1. **One endpoint, one format.** All queries go through `/api/v1/resolve?secid=...` and return the same envelope.
2. **Query depth determines response depth.** More specific queries return resolved URLs. Less specific queries return registry data.
3. **Always return something useful.** Malformed input gets corrected. Partial matches get related data. Nothing is a bare error.
4. **The client compares `secid_query` with `results[].secid` to understand what happened.** No need for the server to explain what the client can see for itself.

## Envelope

Every response has the same top-level shape:

```json
{
  "secid_query": "secid:advisory/CVE-2026-1234",
  "status": "found",
  "results": [...]
}
```

| Field | Type | Description |
|-------|------|-------------|
| `secid_query` | string | Exactly what the client sent, echoed back verbatim |
| `status` | string | How the query was processed (see Status Values) |
| `results` | array | Zero or more result objects |

## Status Values

The `status` field tells the client how the server interpreted their query:

| Status | Meaning | When |
|--------|---------|------|
| `found` | Query parsed and matched as-is | `secid:advisory/mitre.org/cve#CVE-2026-1234` → matched exactly |
| `corrected` | Query had issues but we resolved it anyway | `secid:advisory/redhat.com/RHSA-2026:1234` → corrected to `errata#RHSA-2026:1234` |
| `related` | Query partially matched; returning what we have | `secid:advisory/redhat.com/total_junk` → here's what redhat.com offers |
| `not_found` | Nothing matched | `secid:advisory/totallyinvented.com/whatever` → no such namespace |
| `error` | Query is structurally unparseable | Empty string, missing `secid:` prefix with no identifiable content |

**`found` vs `corrected`:** If `secid_query` would produce the same `results[].secid` values through normal resolution, it's `found`. If the server had to fix, reinterpret, or guess, it's `corrected`. The client can always compare `secid_query` with the returned `secid` values to see exactly what changed.

**`related`:** The server recognized something (a valid type, a valid namespace) but couldn't fully resolve. Results contain registry data about what's available at the level that did match.

**`not_found`:** Results may still contain guidance — valid types, similar namespaces, suggestions.

## Result Objects

Each entry in `results` has `secid` plus either resolution data or registry data.

### Resolution Result (specific item)

When the query resolves to a specific item with a URL:

```json
{
  "secid": "secid:advisory/mitre.org/cve#CVE-2026-1234",
  "weight": 100,
  "url": "https://www.cve.org/CVERecord?id=CVE-2026-1234"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `secid` | string | The fully-qualified SecID for this result |
| `weight` | integer | Match quality (100 = authoritative, 50 = indirect). From registry match_node weights. |
| `url` | string | The resolved URL where this resource can be found |

One result = one SecID = one URL. If a source resolves to multiple URLs, those are separate results.

### Registry Result (browsing / discovery)

When the query returns registry information rather than a resolved URL:

```json
{
  "secid": "secid:advisory/mitre.org/cve",
  "data": {
    "official_name": "Common Vulnerabilities and Exposures",
    "common_name": "CVE",
    "description": "The canonical vulnerability identifier system...",
    "urls": [
      {"type": "website", "url": "https://cve.org"},
      {"type": "api", "url": "https://cveawg.mitre.org/api"},
      {"type": "bulk_data", "url": "https://github.com/CVEProject/cvelistV5"}
    ],
    "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
    "examples": ["CVE-2024-1234", "CVE-2021-44228"]
  }
}
```

| Field | Type | Description |
|-------|------|-------------|
| `secid` | string | The SecID this data describes |
| `data` | object | Registry metadata (contents vary by depth — see Progressive Resolution) |

The `data` object contains whatever registry fields are relevant at that level. No `url` or `weight` — this isn't a resolution, it's information.

## Progressive Resolution

Query depth determines what comes back. The resolver narrows scope based on how much the client specified.

### Level 1: Specific item (type + namespace + name + subpath)

```
GET /api/v1/resolve?secid=secid:advisory/mitre.org/cve%23CVE-2026-1234
```

The `#` must be percent-encoded as `%23` in the query parameter (otherwise it's interpreted as the URL fragment). Alternatively, send it as a POST body.

```json
{
  "secid_query": "secid:advisory/mitre.org/cve#CVE-2026-1234",
  "status": "found",
  "results": [
    {
      "secid": "secid:advisory/mitre.org/cve#CVE-2026-1234",
      "weight": 100,
      "url": "https://www.cve.org/CVERecord?id=CVE-2026-1234"
    }
  ]
}
```

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

### Level 2: Source record (type + namespace + name)

```
GET /api/v1/resolve?secid=secid:advisory/mitre.org/cve
```

```json
{
  "secid_query": "secid:advisory/mitre.org/cve",
  "status": "found",
  "results": [
    {
      "secid": "secid:advisory/mitre.org/cve",
      "data": {
        "official_name": "Common Vulnerabilities and Exposures",
        "common_name": "CVE",
        "description": "The canonical vulnerability identifier system, operated by MITRE under contract with CISA.",
        "notes": "CVE is the canonical identifier — other advisories cross-reference CVEs...",
        "urls": [
          {"type": "website", "url": "https://cve.org"},
          {"type": "api", "url": "https://cveawg.mitre.org/api"},
          {"type": "bulk_data", "url": "https://github.com/CVEProject/cvelistV5"}
        ],
        "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
        "examples": ["CVE-2024-1234", "CVE-2021-44228"]
      }
    }
  ]
}
```

### Level 3: Namespace listing (type + namespace)

```
GET /api/v1/resolve?secid=secid:advisory/mitre.org
```

```json
{
  "secid_query": "secid:advisory/mitre.org",
  "status": "found",
  "results": [
    {
      "secid": "secid:advisory/mitre.org/cve",
      "data": {
        "official_name": "Common Vulnerabilities and Exposures",
        "common_name": "CVE"
      }
    },
    {
      "secid": "secid:advisory/mitre.org/cvelistV5",
      "data": {
        "official_name": "CVE List V5 (cvelistV5)",
        "common_name": "cvelistV5"
      }
    }
  ]
}
```

### Level 4: Type listing (type only)

```
GET /api/v1/resolve?secid=secid:advisory
```

```json
{
  "secid_query": "secid:advisory",
  "status": "found",
  "results": [
    {
      "secid": "secid:advisory/mitre.org",
      "data": {"official_name": "MITRE Corporation", "common_name": "MITRE"}
    },
    {
      "secid": "secid:advisory/nist.gov",
      "data": {"official_name": "National Institute of Standards and Technology", "common_name": "NIST"}
    },
    {
      "secid": "secid:advisory/redhat.com",
      "data": {"official_name": "Red Hat, Inc.", "common_name": "Red Hat"}
    }
  ]
}
```

## Cross-Source Search

When the client provides a subpath identifier without specifying which source (name), the resolver tries it against all match_node children in scope. This is the key feature for "give me everything about this CVE."

### Namespace-scoped search (type + namespace + bare identifier)

```
GET /api/v1/resolve?secid=secid:advisory/mitre.org/CVE-2026-1234
```

The name `CVE-2026-1234` doesn't match any match_node name (`(?i)^cve$`, etc.). The resolver tries it as a subpath against all children in mitre.org:

```json
{
  "secid_query": "secid:advisory/mitre.org/CVE-2026-1234",
  "status": "found",
  "results": [
    {
      "secid": "secid:advisory/mitre.org/cve#CVE-2026-1234",
      "weight": 100,
      "url": "https://www.cve.org/CVERecord?id=CVE-2026-1234"
    },
    {
      "secid": "secid:advisory/mitre.org/cvelistV5#CVE-2026-1234",
      "weight": 80,
      "url": "https://github.com/CVEProject/cvelistV5/tree/main/cves/2026/1xxx/CVE-2026-1234.json"
    }
  ]
}
```

### Type-scoped search (type + bare identifier)

```
GET /api/v1/resolve?secid=secid:advisory/CVE-2026-1234
```

`CVE-2026-1234` is not a domain name, so no namespace matches. The resolver searches all advisory namespaces:

```json
{
  "secid_query": "secid:advisory/CVE-2026-1234",
  "status": "found",
  "results": [
    {
      "secid": "secid:advisory/mitre.org/cve#CVE-2026-1234",
      "weight": 100,
      "url": "https://www.cve.org/CVERecord?id=CVE-2026-1234"
    },
    {
      "secid": "secid:advisory/nist.gov/nvd#CVE-2026-1234",
      "weight": 100,
      "url": "https://nvd.nist.gov/vuln/detail/CVE-2026-1234"
    },
    {
      "secid": "secid:advisory/redhat.com/cve#CVE-2026-1234",
      "weight": 100,
      "url": "https://access.redhat.com/security/cve/CVE-2026-1234"
    },
    {
      "secid": "secid:advisory/redhat.com/bugzilla#CVE-2026-1234",
      "weight": 50,
      "url": "https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2026-1234"
    },
    {
      "secid": "secid:advisory/suse.com/bugzilla#CVE-2026-1234",
      "weight": 50,
      "url": "https://bugzilla.suse.com/show_bug.cgi?id=CVE-2026-1234"
    },
    {
      "secid": "secid:advisory/gov/cisa.json/vulnrichment#CVE-2026-1234",
      "weight": 80,
      "url": "https://github.com/cisagov/vulnrichment/tree/develop/2026/1xxx/CVE-2026-1234.json"
    }
  ]
}
```

Results are sorted by weight descending. The client gets every place that CVE can be found, ranked by match quality.

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

## Corrected Queries

When the server fixes the input:

```
GET /api/v1/resolve?secid=secid:advisory/redhat.com/RHSA-2026:1234
```

The name `RHSA-2026:1234` doesn't match any match_node name. The resolver tries it as a subpath against children and finds it matches under `errata`:

```json
{
  "secid_query": "secid:advisory/redhat.com/RHSA-2026:1234",
  "status": "corrected",
  "results": [
    {
      "secid": "secid:advisory/redhat.com/errata#RHSA-2026:1234",
      "weight": 100,
      "url": "https://access.redhat.com/errata/RHSA-2026:1234"
    }
  ]
}
```

Status is `corrected` because the server had to reinterpret the input — the client put the identifier as the name instead of the subpath. The result includes the correct SecID form.

## Not Found

```
GET /api/v1/resolve?secid=secid:advisory/totallyinvented.com/whatever
```

```json
{
  "secid_query": "secid:advisory/totallyinvented.com/whatever",
  "status": "not_found",
  "results": [],
  "message": "No namespace 'totallyinvented.com' in the advisory registry."
}
```

```
GET /api/v1/resolve?secid=secid:frobnicate/mitre.org/cve
```

```json
{
  "secid_query": "secid:frobnicate/mitre.org/cve",
  "status": "not_found",
  "results": [],
  "message": "'frobnicate' is not a valid type. Valid types: advisory, weakness, ttp, control, disclosure, regulation, entity, reference."
}
```

The `message` field is present on `not_found` and `error` responses to provide human/AI-readable guidance. It is absent on `found` and `corrected` responses (the results speak for themselves).

## Error

```
GET /api/v1/resolve?secid=
```

```json
{
  "secid_query": "",
  "status": "error",
  "results": [],
  "message": "Empty query. Provide a SecID string (e.g., secid:advisory/mitre.org/cve#CVE-2024-1234)."
}
```

## Summary of Response Fields

### Envelope

| Field | Type | Always present | Description |
|-------|------|----------------|-------------|
| `secid_query` | string | Yes | Verbatim echo of client input |
| `status` | string | Yes | `found`, `corrected`, `related`, `not_found`, `error` |
| `results` | array | Yes | Result objects (may be empty) |
| `message` | string | Only on `not_found` / `error` | Human/AI-readable guidance |

### Resolution result (item resolved to URL)

| Field | Type | Description |
|-------|------|-------------|
| `secid` | string | Fully-qualified SecID |
| `weight` | integer | Match quality (higher = better) |
| `url` | string | Resolved URL |
| `content_type` | string | MIME type of the response (e.g., `text/html`, `application/json`). Present when the registry specifies it. |
| `parsability` | string | Data format: `"structured"` or `"scraped"`. Present when the registry specifies it. |
| `schema` | string | SecID reference to the data schema (e.g., `secid:reference/cve.org/cve-schema@5.2.0`). Present for structured sources. |
| `parsing_instructions` | string | SecID reference to parsing instruction document. Present when the registry specifies it. |
| `auth` | string | Free-text auth description. Present when the registry specifies it. |

### Registry result (browsing / discovery)

| Field | Type | Description |
|-------|------|-------------|
| `secid` | string | SecID for this registry entry |
| `data` | object | Registry metadata (varies by depth) |

## URL Encoding Note

The `#` character in SecID subpaths conflicts with the URL fragment identifier. Clients must percent-encode `#` as `%23` in the query parameter:

```
/api/v1/resolve?secid=secid:advisory/mitre.org/cve%23CVE-2026-1234
```

The server decodes `%23` back to `#` before processing. The `secid_query` in the response contains the decoded form.

## MCP Server

The MCP server at `/mcp/` uses the same resolution logic and returns the same data structures. The three MCP tools map to the same resolve pipeline:

| MCP Tool | Equivalent API Call |
|----------|-------------------|
| `resolve(secid)` | `GET /api/v1/resolve?secid={secid}` |
| `lookup(query)` | `GET /api/v1/resolve?secid={query}` (cross-source search) |
| `describe(secid)` | `GET /api/v1/resolve?secid={secid}` (returns registry data when no subpath) |

All three tools are effectively the same operation with different framing. The resolve endpoint handles all cases based on query depth.
