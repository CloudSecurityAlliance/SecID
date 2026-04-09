---
marp: true
theme: csa
paginate: true
header: 'SecID Technical'
footer: 'Cloud Security Alliance · secid.cloudsecurityalliance.org'
---

<!-- _class: title -->

# SecID: Technical Deep Dive

**API, MCP, SDKs, and building integrations**

Kurt Seifried · Chief Innovation Officer · Cloud Security Alliance
kseifried@cloudsecurityalliance.org · github.com/kurtseifried

secid.cloudsecurityalliance.org · v1.0 · April 2026

---

## One Endpoint. That's It.

```
GET https://secid.cloudsecurityalliance.org/api/v1/resolve?secid={encoded}
```

No auth. No API keys. No headers. CORS enabled.

**The one gotcha:** `#` in SecID strings must be encoded as `%23` in the query parameter.

```
CORRECT: ?secid=secid:advisory/mitre.org/cve%23CVE-2021-44228
WRONG:   ?secid=secid:advisory/mitre.org/cve#CVE-2021-44228
```

This is the #1 failure mode for new clients. Your URL encoder may treat `#` as a fragment separator and silently drop it.

---

## Response Envelope

Every response has the same shape:

```json
{
  "secid_query": "secid:advisory/mitre.org/cve#CVE-2021-44228",
  "status": "found",
  "results": [
    {
      "secid": "secid:advisory/mitre.org/cve#CVE-2021-44228",
      "weight": 100,
      "url": "https://www.cve.org/CVERecord?id=CVE-2021-44228"
    }
  ]
}
```

| Field | Always present | What it tells you |
|-------|---------------|-------------------|
| `secid_query` | Yes | Exactly what you sent (echoed back) |
| `status` | Yes | `found`, `corrected`, `related`, `not_found`, `error` |
| `results` | Yes | Zero or more result objects |

Compare `secid_query` with `results[].secid` to see what the server actually resolved.

---

## Status Values

| Status | Meaning | Example |
|--------|---------|---------|
| `found` | Matched as-is | `secid:advisory/mitre.org/cve#CVE-2021-44228` |
| `corrected` | Fixed your input, resolved anyway | `secid:advisory/redhat.com/RHSA-2026:1234` → corrected to `errata#RHSA-2026:1234` |
| `related` | Partial match — here's what we have | `secid:advisory/redhat.com/junk` → here's what redhat.com offers |
| `not_found` | Nothing matched | `secid:advisory/totallyinvented.com/whatever` |
| `error` | Structurally unparseable | Empty string, gibberish |

**The server always tries to help.** Even `not_found` may include suggestions. `corrected` tells you what the right form was.

**Gotcha:** All responses return HTTP 200 — including `not_found` and `error`. Check the `status` field in the JSON, not the HTTP status code.

---

## Query Depth = Response Depth

```
secid:advisory                              → list all advisory namespaces
secid:advisory/mitre.org                    → list MITRE's advisory sources
secid:advisory/mitre.org/cve               → describe the CVE source
secid:advisory/mitre.org/cve#CVE-2021-44228 → resolve to URL
```

Less specific → registry data (what exists). More specific → resolution (where it lives).

**Cross-source search:** omit the namespace to search across all sources:

```
secid:advisory/CVE-2021-44228  → every source that knows this CVE
secid:weakness/CWE-79          → every source that has CWE-79
```

---

## MCP Server — One URL, Three Tools

```
https://secid.cloudsecurityalliance.org/mcp
```

Add this URL to Claude Desktop, Claude Code, Cursor, Windsurf, or any MCP client.

| Tool | Input | What it does |
|------|-------|-------------|
| `resolve` | Full SecID string | Resolve to URLs and data |
| `lookup` | Type + identifier | Search across sources (constructs the SecID for you) |
| `describe` | Partial SecID | Browse types, namespaces, sources |

The MCP server includes context, disambiguation guidance, and cross-references in every response. AI agents can reason about security knowledge without external documentation.

---

## MCP — What AI Agents See

```
Agent: resolve("secid:advisory/mitre.org/cve#CVE-2021-44228")

→ {
    "secid": "secid:advisory/mitre.org/cve#CVE-2021-44228",
    "weight": 100,
    "url": "https://www.cve.org/CVERecord?id=CVE-2021-44228"
  }

Agent: lookup(type="disclosure", identifier="redhat.com")

→ {
    "secid": "secid:disclosure/redhat.com",
    "data": {
      "official_name": "Red Hat, Inc.",
      "source_count": 3,
      "patterns": [
        {"pattern": "cna-tlr", "description": "Root CNA"},
        {"pattern": "cna-lr", "description": "CNA of Last Resort"},
        {"pattern": "cna", "description": "CNA"}
      ]
    }
  }
```

---

## SDKs — Python, TypeScript, Go

**Python:**
```python
from secid_client import SecIDClient
client = SecIDClient()

result = client.resolve("secid:advisory/mitre.org/cve#CVE-2021-44228")
print(result["results"][0]["url"])

results = client.lookup("weakness", "CWE-79")
```

**TypeScript:**
```typescript
import { SecIDClient } from "secid";
const client = new SecIDClient();

const result = await client.resolve("secid:weakness/mitre.org/cwe#CWE-79");
```

**Go:**
```go
client := secid.NewClient()
result, _ := client.Resolve("secid:ttp/mitre.org/attack#T1059.003")
```

All SDKs: `github.com/CloudSecurityAlliance/SecID-Client-SDK`

---

## Self-Hosted Server

**Run your own resolver — for privacy, latency, or internal data**

```bash
# Python (quickest)
pip install fastapi uvicorn
python secid_server.py --registry /path/to/SecID/registry

# Docker
docker run -p 8000:8000 -v ./SecID/registry:/data/registry secid-server-api

# With Redis
python secid_server.py --storage redis --redis-url redis://localhost:6379
```

Same API as the hosted service. Any SecID client works with any server.

**Storage backends:** in-memory (default), Redis, memcached, SQLite

**Repo:** `github.com/CloudSecurityAlliance/SecID-Server-API`

---

## Claude Code Plugin

**Local MCP server with internal resolver support**

```
/plugin marketplace add CloudSecurityAlliance/csa-plugins-official
/plugin install secid@csa-plugins-official
```

Same three tools as the remote MCP. Runs locally, calls the REST API.

**Point to an internal resolver:**
```json
{
  "mcpServers": {
    "secid": {
      "command": "python3",
      "args": ["server.py", "--base-url", "https://internal-secid.example.org"]
    }
  }
}
```

---

## Building a Client — The Minimal Version

**A working SecID client in any language is ~20 lines:**

1. URL-encode the SecID string (especially `#` → `%23`)
2. `GET https://secid.cloudsecurityalliance.org/api/v1/resolve?secid={encoded}`
3. Parse JSON response
4. Check `status` field
5. Use `results[0].url` if resolved, `results[0].data` if browsing

**That's it.** No auth negotiation, no token refresh, no pagination, no webhooks. One GET, one JSON response, done.

The SDKs add convenience (retry, caching, type safety) but they're not required.

---

## SecID String Anatomy

```
secid:advisory/mitre.org/cve#CVE-2024-1234
────┬─ ────┬──── ────┬──── ─┬─ ──────┬──────
    │      │         │      │        └─ subpath: specific item
    │      │         │      └────────── name: the database
    │      │         └───────────────── namespace: who publishes it
    │      └─────────────────────────── type: security domain
    └────────────────────────────────── scheme: always "secid:"
```

**10 types:** advisory · capability · control · disclosure · entity · methodology · reference · regulation · ttp · weakness

**Namespaces are domain names:** `mitre.org`, `nist.gov`, `amazon.com/aws`

**Subpath preserves source format:** `#CVE-2024-1234`, `#T1059.003`, `#RHSA-2026:0932` — what practitioners know is what SecID uses.

---

## Structured CNA Data on Disclosure Entries

```json
"cve": {
  "role": ["cna"],
  "cna_id": "CNA-2005-0006",
  "assignerShortName": "redhat",
  "assignerOrgId": "53f830b8-0a3f-465b-8143-3b8a9948e749",
  "last_assigned_cve": "CVE-2026-3184",
  "last_assigned_date": "2026-04-03",
  "scope": "Red Hat products and the open source community"
},
"security_txt": { "url": "https://redhat.com/.well-known/security.txt" },
"disclosure_policy": { "url": "https://access.redhat.com/articles/..." }
```

**502 CNA partners** with formal CNA IDs, CVE Program UUIDs, staleness indicators, security.txt status, and disclosure policy URLs. All machine-queryable.

---

## Architecture — Five Repos

| Repo | What | You need it for |
|------|------|----------------|
| **SecID** | Spec + registry (709+ JSON files) | Understanding the data |
| **SecID-Service** | Cloudflare Worker (hosted at secid.cloudsecurityalliance.org) | Using the public API |
| **SecID-Server-API** | Python/TypeScript self-hosted server | Running your own resolver |
| **SecID-Client-SDK** | Python, TypeScript, Go | Building apps |
| **csa-plugins-official** | Claude Code plugin | Using in Claude Code |

Everything is open: CC0 (spec + data), MIT (service + SDKs).

---

## Try It Now

**1. Browser:** secid.cloudsecurityalliance.org — paste any CVE, CWE, or ATT&CK ID

**2. curl:**
```bash
curl "https://secid.cloudsecurityalliance.org/api/v1/resolve?\
secid=secid:advisory/mitre.org/cve%23CVE-2021-44228"
```

**3. MCP:** add `https://secid.cloudsecurityalliance.org/mcp` to your AI assistant

**4. Plugin:** `/plugin install secid@csa-plugins-official`

**5. SDK:** `pip install secid` / `npm install secid`

---

<!-- _class: closing -->

Kurt Seifried · Chief Innovation Officer · Cloud Security Alliance
kseifried@cloudsecurityalliance.org · github.com/kurtseifried

**SecID v1.0** — One endpoint · No auth · 709+ namespaces · 10 types
secid.cloudsecurityalliance.org · github.com/CloudSecurityAlliance/SecID
