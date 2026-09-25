# SecID Infrastructure

This document describes the hosting architecture and technical decisions for the SecID service.

## Design Principle: Cloudflare-Native When on Cloudflare

**Policy:** When building on Cloudflare, follow Cloudflare's recommended approaches and use their native services.

We may use other platforms and services where appropriate, but when we're in Cloudflare's ecosystem:
1. Follow what Cloudflare recommends in their documentation
2. Use Cloudflare-native services (Workers, Pages, KV, R2, D1, Queues, etc.)
3. Use frameworks with first-class Cloudflare support (Hono, etc.)
4. Follow patterns from Cloudflare's examples and blog posts

**Why:**
- Best performance on their edge network
- Simplest integration between their services
- Access to latest features and optimizations
- Supported upgrade path as platform evolves

## Repository Structure

SecID is split across multiple repositories for clear separation of concerns:

| Repository | Purpose | Contents |
|------------|---------|----------|
| **SecID** (this repo) | Spec + Registry + Operations | Specification, registry data, design docs, infrastructure/deployment docs. Source of truth. |
| **[SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service)** | API + MCP + website | Cloudflare Worker serving `/api/v1/` and `/mcp`, plus the public website (Astro static site in `website/`, served as Worker static assets). Reads registry data from Cloudflare KV. |
| **[SecID-Server-API](https://github.com/CloudSecurityAlliance/SecID-Server-API)** | Self-hosted resolver | Python reference implementation (REST API + optional MCP, pluggable storage). TypeScript and Go implementations are planned. |
| **[SecID-Client-SDK](https://github.com/CloudSecurityAlliance/SecID-Client-SDK)** | Official clients | Python, TypeScript, Go libraries. Claude skills for using SecID. |
| **[SecID-Data-disa.mil](https://github.com/CloudSecurityAlliance/SecID-Data-disa.mil)** | Data (SecID 2.0) | DISA STIG/SRG content, ingested quarterly. The first data repository; sets the standard layout for `SecID-Data-*` repos (ADR-013, ADR-014). |

**Why split?**
- Different release cadences
- Clear ownership and CI/CD
- Service can be self-hosted by others
- Clients are independent of service implementation

**Why operations lives here (not a separate repo):** Operations content is documentation (bootstrap runbook, DNS decisions, CI/CD design), not code with its own build/release lifecycle. See [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md#operations-documentation-lives-in-this-repo). Operations docs live at `docs/operations/`.

**Registry curator:** CSA maintains the default registry data in the SecID repo.

## URL Structure

```
https://secid.cloudsecurityalliance.org/
├── /              → Static website (Worker static assets, built from SecID-Service/website)
├── /mcp           → MCP endpoint (Cloudflare Worker)
├── /api/v1/       → REST API v1 (Cloudflare Worker)
├── /api/v2/       → REST API v2 (future)
└── /llms.txt      → LLM-friendly site summary (llmstxt.org standard)
```

### llms.txt Support

We support the [llms.txt standard](https://llmstxt.org/) for LLM-friendly content discovery:
- `/llms.txt` - Markdown summary of the site with links to key resources
- Individual pages available as `.md` for direct LLM consumption
- Enables AI agents to efficiently understand SecID without processing the entire site

## Components

### Static Website

- Landing page explaining SecID, with an interactive resolver
- `llms.txt`, `robots.txt`, `sitemap.txt`, slides
- Built with [Astro](https://astro.build/) from the `website/` directory of SecID-Service (`npm run build:website`) and served by the same Worker through Workers static assets (`[assets] directory = "./website/dist"` in `wrangler.toml`). There is no separate website repository or Pages project.

### MCP Endpoint (`/mcp`)

Model Context Protocol server for AI agent integration.

**Transport:** Streamable HTTP (2025-03-26 spec)
- Single endpoint handles both POST and GET
- SSE deprecated but may support for backwards compatibility
- Reference: [MCP Transport Specification](https://modelcontextprotocol.io/specification/2025-03-26/basic/transports)

**Authentication:** Public/no auth initially. Future: email registration for API key.

**Capabilities:**
- `resolve` tool - Given a SecID, return URL(s)
- `lookup` tool - Given a partial ID, find matching SecIDs
- `describe` tool - Return description and metadata for a SecID
- `submit_feedback` tool - Request a missing source, report wrong data, suggest improvements
- `secid://registry` and `secid://registry/{type}` resources - Browse available namespaces
- `secid://docs/...` resources - Instructions for building SecID clients

### REST API (`/api/v1/`)

Single endpoint handles all queries — resolution, browsing, and cross-source search.

**Endpoint:**

```
GET /api/v1/resolve?secid={secid}
```

Query depth determines response depth:

| Query | Returns |
|-------|---------|
| `secid:advisory/mitre.org/cve#CVE-2026-1234` | Resolved URL(s) with weights |
| `secid:advisory/mitre.org/cve` | Source record (data, urls, patterns, examples) |
| `secid:advisory/mitre.org` | All sources under namespace |
| `secid:advisory` | List of namespaces |
| `secid:advisory/CVE-2026-1234` | Cross-source search across all advisory namespaces |

**Core principle: Format validation, not existence checking.**
SecID validates that an identifier matches a known pattern — it does NOT check if the thing exists. `secid:advisory/mitre.org/cve#CVE-2099-99999` is valid (fits pattern) even if that CVE doesn't exist yet. Existence is for the relationship/enrichment layers.

**Cross-source search:** When the client provides an identifier without specifying which source, the resolver tries it against all match_node children in scope and returns all matches ranked by weight. `secid:advisory/CVE-2026-1234` returns every place that CVE can be found.

**Authentication:** Public/no auth initially. Future: API key via header.

See [API-RESPONSE-FORMAT.md](API-RESPONSE-FORMAT.md) for the complete response specification.

## Technical Stack

### Framework: Hono

[Hono](https://hono.dev/) is the recommended framework for Cloudflare Workers:
- Ultrafast (402k ops/sec)
- Under 14KB minified
- Zero dependencies
- Built on Web Standards
- First-class Cloudflare support

Reference: [Hono on Cloudflare Workers](https://hono.dev/docs/getting-started/cloudflare-workers)

### Single Worker

One Cloudflare Worker handles both `/mcp` and `/api/v1/` (and serves the static website as assets):

```typescript
import { Hono } from 'hono'

const app = new Hono()

// MCP endpoint (Streamable HTTP)
app.post('/mcp', handleMCPPost)
app.get('/mcp', handleMCPGet)

// REST API v1 — single resolve endpoint
app.get('/api/v1/resolve', handleResolve)

export default app
```

**Why single Worker?**
- Shared registry data
- Simpler deployment
- Easier to keep in sync
- Both use same resolution logic

### Data Storage

**Approach:** Registry data lives in Cloudflare KV (binding `secid_REGISTRY`). The Worker reads only the keys a query needs (`kv-registry.ts`, `kv-resolve.ts`) — one key per `secid:<type>/<namespace>`, plus per-type listing keys and a few index keys (`secid:*`, `secid:registry`, `secid:meta`, `secid:subtypes`).

The registry was originally compiled into the Worker bundle; it outgrew that approach. SecID-Service still has `scripts/build-registry.ts`, which generates `src/registry.ts`, but that file is a snapshot used by tests only — production never reads it, so tests and the live resolver can disagree if the snapshot is stale.

**Upload process** (`scripts/upload-registry-kv.ts`, run by SecID-Service CI on every registry change):
1. Read all `registry/**/*.json` files from a SecID checkout
2. Build the expected set of KV keys and values
3. `--sync`: upload every expected key and delete orphan keys, so KV exactly matches the registry (a 50-orphan safety threshold blocks accidental mass deletes)

See [CLAUDE.md "CI/CD"](../../CLAUDE.md#cicd) for the deploy chain from a merge here to KV.

### OpenAPI Schema

The REST API is described by a hand-maintained OpenAPI document in this repo: [schemas/openapi.yaml](../../schemas/openapi.yaml). The Worker does not generate or serve an OpenAPI document.

## MCP Implementation

Reference: [Cloudflare MCP Documentation](https://developers.cloudflare.com/agents/model-context-protocol/)

### Tools

```typescript
const tools = {
  resolve: {
    description: "Resolve a SecID to its URL(s)",
    parameters: {
      secid: { type: "string", description: "The SecID to resolve" }
    }
  },
  lookup: {
    description: "Find SecIDs matching a pattern or keyword",
    parameters: {
      query: { type: "string", description: "Search query" },
      type: { type: "string", optional: true, description: "Filter by type" }
    }
  },
  describe: {
    description: "Get description and metadata for a SecID",
    parameters: {
      secid: { type: "string", description: "The SecID to describe" }
    }
  }
}
```

### Resources

```typescript
const resources = {
  "secid://registry": {
    description: "The full SecID registry",
    mimeType: "application/json"
  },
  "secid://registry/{type}": {
    description: "Registry entries for a specific type",
    mimeType: "application/json"
  }
}
```

## Authentication (Future)

**Phase 1:** Public, no authentication

**Phase 2:** Optional API key
- Register with email
- Receive API key via email
- Pass key in header: `Authorization: Bearer {key}`
- Rate limiting per key

**Phase 3:** OAuth (if needed)
- Use Cloudflare's `workers-oauth-provider`
- Reference: [MCP Authorization](https://developers.cloudflare.com/agents/model-context-protocol/authorization/)

## Deployment

**Note:** This section describes **SecID-Service** (not this repo). Its own [CLAUDE.md](https://github.com/CloudSecurityAlliance/SecID-Service/blob/main/CLAUDE.md) is authoritative.

### SecID-Service Repository Structure

```
SecID-Service/
├── src/
│   ├── index.ts          # Worker entry (Hono) — routes /api/v1/*, /mcp, /health
│   ├── api.ts            # REST API handlers (resolve, registry.json, types)
│   ├── mcp.ts            # MCP tools (resolve, lookup, describe, submit_feedback)
│   ├── parser.ts         # Registry-aware SecID parsing
│   ├── resolver.ts       # Pattern-tree resolution, URL templates, format metadata
│   ├── kv-registry.ts    # KV reads for registry data
│   ├── kv-resolve.ts     # KV-backed resolution path (production)
│   ├── registry.ts       # Snapshot from build-registry.ts — used by tests only
│   ├── type-registry.ts  # Canonical TYPE_REGISTRY constant
│   └── ...               # feedback, observability, sanitize, identity, types
├── scripts/
│   ├── build-registry.ts       # SecID JSON → src/registry.ts (test snapshot)
│   ├── upload-registry-kv.ts   # SecID JSON → KV (--sync deletes orphans)
│   └── setup-dns.sh
├── test/                 # vitest; resolver fixtures auto-generated from registry examples
├── website/              # Astro static site, served as Worker static assets
├── wrangler.toml         # Worker config (routes, KV bindings, assets)
└── .github/workflows/registry-kv-upload.yml   # Triggered by repository_dispatch from SecID
```

### Build & Deploy (SecID-Service)

Normally automatic: a registry merge here dispatches SecID-Service's "Upload registry to KV" workflow, which tests, syncs KV, and deploys the Worker. Manually:

```bash
# Sync registry data to KV (audit first with --dry-run)
npx tsx scripts/upload-registry-kv.ts --sync --dry-run /path/to/SecID
npx tsx scripts/upload-registry-kv.ts --sync /path/to/SecID

# Build the website and deploy the Worker
npm run deploy
```

## Monitoring

- Cloudflare Analytics for request metrics
- Error tracking via Worker logs
- Future: usage analytics per API key

## Decisions Pending

These items need decisions before production deployment. Pinned for later discussion.

### Security & Access Control

- **CORS policy** - Allow all origins (`*`), or restrict to specific domains?
- **Rate limiting** - Requests per minute/hour for anonymous access? Per IP? Per API key?
- **Anti-abuse** - Block known bad actors? Cloudflare WAF rules? Bot detection?
- **Input validation** - Max SecID length? Sanitization rules?

### Caching & Performance

- **Cache-Control headers** - How long to cache registry data? Different TTLs for different endpoints?
- **CDN caching** - Let Cloudflare cache at edge? Purge strategy on registry updates?
- **Response compression** - Gzip/Brotli for large registry responses?

### Versioning & Compatibility

- **Registry version vs API version** - Are these coupled or independent?
- **Breaking changes** - How do we signal breaking changes in registry format?
- **Deprecation policy** - How long do we support old API versions?

### Operational

- **Error responses** - Standard error format? Error codes?
- **Health check endpoint** - Decided: `GET /health` returns `{"status":"ok"}`.
- **Metrics & logging** - What to track? Privacy considerations?
- **Alerting** - What triggers alerts? Who gets notified?

### MCP-Specific

- **Backwards compatibility** - Support deprecated SSE transport or only Streamable HTTP?
- **Tool granularity** - Fewer broad tools or many specific tools?
- **Resource URIs** - `secid://` scheme or something else?

### Future Features

- **Webhooks** - Notify on registry updates?
- **Batch operations** - Resolve multiple SecIDs in one request?
- **GraphQL** - Offer GraphQL alongside REST?
- **SDK generation** - Auto-generate client SDKs from OpenAPI?

### Documentation

- **[API-RESPONSE-FORMAT.md](API-RESPONSE-FORMAT.md)** - Formal spec for API/MCP response format: envelope, progressive resolution, cross-source search, status values, result shapes.
