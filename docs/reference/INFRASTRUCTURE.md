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
| **SecID** (this repo) | Spec + Registry | Specification, registry data, design docs. Source of truth. |
| **SecID-Service** | API + MCP | Cloudflare Worker code for `/v1/` and `/mcp`. Consumes registry. |
| **SecID-Website** | Documentation site | Cloudflare Pages. Generated from other repos by Claude skill. |
| **SecID-Client** | Official clients | Python, npm, Go libraries. Claude skills for using SecID. |

**Why split?**
- Different release cadences
- Clear ownership and CI/CD
- Service can be self-hosted by others
- Website is derived content, not source
- Clients are independent of service implementation

**Registry curator:** CSA maintains the default registry data in the SecID repo.

## URL Structure

```
https://secid.cloudsecurityalliance.org/  (provisional)
├── /              → Static website (Cloudflare Pages)
├── /mcp           → MCP endpoint (Cloudflare Worker)
├── /v1/           → REST API v1 (Cloudflare Worker)
├── /v2/           → REST API v2 (future)
└── /llms.txt      → LLM-friendly site summary (llmstxt.org standard)
```

### llms.txt Support

We support the [llms.txt standard](https://llmstxt.org/) for LLM-friendly content discovery:
- `/llms.txt` - Markdown summary of the site with links to key resources
- Individual pages available as `.md` for direct LLM consumption
- Enables AI agents to efficiently understand SecID without processing the entire site

## Components

### Static Website (Cloudflare Pages)

- Landing page explaining SecID
- Documentation
- Interactive examples
- Served from Cloudflare Pages (separate from Worker)

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
- `registry` resource - Browse available namespaces

### REST API (`/v1/`)

Traditional REST API for programmatic access.

**Endpoints (v1):**

```
GET /v1/resolve?secid={secid}
    → Returns URL(s) for the given SecID

GET /v1/resolve?secid={secid}&include=description,patterns
    → Returns URL(s) plus additional metadata

GET /v1/registry
    → Returns full registry (all namespaces, sources, patterns)

GET /v1/registry/{type}
    → Returns all namespaces for a type (e.g., advisory, control)

GET /v1/registry/{type}/{namespace}
    → Returns all sources for a namespace

GET /v1/registry/{type}/{namespace}/{source}
    → Returns details for a specific source
```

**Core principle: Format validation, not existence checking.**
SecID validates that an identifier matches a known pattern - it does NOT check if the thing exists. `secid:advisory/mitre.org/cve#CVE-2099-99999` is valid (fits pattern) even if that CVE doesn't exist yet. Existence is for the relationship/enrichment layers.

**Discovery mode:** Partial or bare identifiers return ALL matching patterns:
- `CVE-2024-1234` (bare) → Returns matches from mitre/cve, nist/nvd, redhat/cve, etc.
- `secid:advisory/cve#...` (missing namespace) → Returns all advisory namespaces with matching patterns

**Invalid format handling:** If input doesn't match any pattern for the specified namespace, return suggestions ("did you mean...") with valid options.

**Response format:** JSON (JSON-LD under consideration)

**Response modes:**
| Mode | Parameter | Contains | Use Case |
|------|-----------|----------|----------|
| `full` | `?mode=full` | Rule matched, source data, derivation, verifiable | Debugging, transparency, auditing |
| `answers` | `?mode=answers` (default) | Just URLs/instructions | Production, minimal bandwidth |

**Hierarchical lookup:** Responses aggregate data from four levels:
1. **Registry level** - System-wide announcements (e.g., "API keys required March 1", "Migrating to new domain")
2. **Type level** - Type-wide hints (e.g., advisory aggregator services)
3. **Namespace level** - Namespace-wide hints (e.g., "Also try secid.mitre.org")
4. **Pattern level** - Specific regex match with resolution URL

**Authentication:** Public/no auth initially. Future: API key via header.

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

One Cloudflare Worker handles both `/mcp` and `/v1/`:

```typescript
import { Hono } from 'hono'

const app = new Hono()

// MCP endpoint (Streamable HTTP)
app.post('/mcp', handleMCPPost)
app.get('/mcp', handleMCPGet)

// REST API v1
app.get('/v1/resolve', handleResolve)
app.get('/v1/registry', handleRegistryList)
app.get('/v1/registry/:type', handleRegistryType)
app.get('/v1/registry/:type/:namespace', handleRegistryNamespace)
app.get('/v1/registry/:type/:namespace/:source', handleRegistrySource)

export default app
```

**Why single Worker?**
- Shared registry data
- Simpler deployment
- Easier to keep in sync
- Both use same resolution logic

### Data Storage

**Approach:** Compile all registry JSON files into a single registry object, embedded in the Worker code.

```typescript
// registry.ts - generated at build time
export const REGISTRY = {
  advisory: {
    "mitre.org": {
      official_name: "MITRE Corporation",
      match_nodes: [
        {
          patterns: ["(?i)^cve$"],
          data: { official_name: "Common Vulnerabilities and Exposures", urls: [...] },
          children: [...]
        }
      ]
    }
  },
  // ...
}
```

**Why embedded?**
- Fast (no external fetch)
- Simple (no KV/R2 complexity)
- Discoverable (single endpoint returns everything)
- Versioned with code

**Build process:**
1. Read all `registry/**/*.json` files
2. Merge into single object
3. Generate `registry.ts`
4. Bundle with Worker

**Future:** If registry grows too large, migrate to Cloudflare KV.

### OpenAPI Schema

Use [Chanfana](https://github.com/cloudflare/chanfana) for OpenAPI schema generation:
- Auto-generates OpenAPI 3.1 spec
- Request/response validation with Zod
- Serves `/v1/openapi.json` automatically

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

**Note:** The API and website are in separate repositories. This section describes the planned structure for **SecID-Service** (not this repo).

### SecID-Service Repository Structure (Planned)

```
secid-service/
├── src/
│   ├── index.ts        # Main entry, Hono app
│   ├── mcp.ts          # MCP handlers
│   ├── api.ts          # REST API handlers
│   ├── resolve.ts      # Resolution logic
│   └── registry.ts     # Generated from SecID repo registry/
├── wrangler.toml
├── package.json
└── scripts/
    └── build-registry.ts   # Fetches and compiles registry from SecID repo
```

### Build & Deploy (SecID-Service)

```bash
# Build registry (fetches from SecID repo, compiles to registry.ts)
npm run build:registry

# Deploy worker
wrangler deploy
```

### SecID-Website Repository (Planned)

Separate Cloudflare Pages deployment. Structure TBD.

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
- **Health check endpoint** - `/health` or `/v1/health`?
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

### Documentation Pending

- **API-RESPONSE-FORMAT.md** - Formal spec for API/MCP response format. Natural extension of REGISTRY-JSON-FORMAT.md wrapped in a lightweight container. Will define response envelope, hierarchical lookup results, error format, and mode differences (full vs answers).
