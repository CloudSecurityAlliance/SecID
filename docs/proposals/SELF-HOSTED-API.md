# Proposal: Self-Hosted SecID API (SecID-API Repo)

Status: Draft / discussion
Date: 2026-04-07

## Summary

Create a `SecID-API` repo with portable server implementations that anyone can run — on a laptop, in Docker, or on internal infrastructure. Three deployment options: Cloudflare Worker (already exists), Docker container (TypeScript), and Python reference server.

## The Problem

SecID-Service is Cloudflare-specific (Workers + KV). Organizations that want to run their own resolver — for privacy, latency, internal data, or air-gapped environments — have no option today. The participation model proposes federated and private resolvers, but there's no "run your own" artifact to give people.

## Deployment Options

| Option | Target user | What it is |
|--------|-------------|-----------|
| **Cloudflare Worker** | Already done — `SecID-Service` repo | Fork, configure, `wrangler deploy`. Add a "Deploy your own" guide. |
| **Docker container** | Ops teams, Kubernetes, internal infrastructure | Same resolver logic, pluggable storage backend, standard HTTP server |
| **Python server** | Developers, quick local setup, reference implementation | FastAPI, reads JSON files, ~300 lines. Easiest way to understand how resolution works. |

## Architecture

### The resolver is a key-value lookup

The entire SecID resolution pipeline is:

1. Parse the SecID string (type, namespace, name, subpath)
2. Look up the namespace key in the store
3. Walk the `match_nodes` tree to find the matching pattern
4. Return the result

The storage layer is a simple interface:

```
get(key: string) → string | null
set(key: string, value: string) → void
```

### Registry data is read-only at runtime

The registry JSON files are the source of truth. At startup (or on first request), the server loads them into whatever storage backend is configured. During serving, it's pure reads. No writes, no mutations, no coordination.

The entire registry is ~5-10MB of JSON. It fits in any storage backend trivially.

### Pluggable storage backends

| Backend | Config | Best for |
|---------|--------|----------|
| **In-memory** (dict/Map) | Default, no config | Development, single-container, small deployments |
| **Redis / Valkey** | `STORAGE=redis REDIS_URL=redis://...` | Multi-container, shared cache, production |
| **Memcached** | `STORAGE=memcached MEMCACHED_URL=...` | If you already run memcached |
| **SQLite** | `STORAGE=sqlite SQLITE_PATH=./secid.db` | Single-node production, no external deps |

All backends support the same loading strategies:

| Strategy | Behavior | Trade-off |
|----------|----------|-----------|
| **Bulk load** | Startup: load all entries into cache | Slower startup, every key ready immediately |
| **Lazy load** | First request per key: read from JSON, cache it, return | Instant startup, first hit per key is slower |
| **Warm + lazy** | Bulk load top N keys at startup, lazy load the rest | Balance of startup time and hit latency |

For in-memory and SQLite, bulk load is fine (fast enough). For Redis/memcached, lazy load or warm+lazy avoids blocking startup on network I/O.

Cache miss always falls back to reading the JSON file from disk. The cache is disposable — if memcached restarts, entries reload on next request.

## API Compatibility

The self-hosted server implements the same API as SecID-Service:

```
GET /api/v1/resolve?secid=secid:advisory/mitre.org/cve%23CVE-2021-44228
```

Same request format, same response envelope (`secid_query`, `status`, `results`), same status values (`found`, `corrected`, `related`, `not_found`, `error`). Clients (SDK, plugin, MCP) work with any SecID server — public or private — because the API is identical.

### MCP endpoint

The self-hosted server also serves `/mcp` — the same three MCP tools (resolve, lookup, describe). This means you can point Claude Desktop or any MCP client at your internal server directly:

```
https://internal-secid.example.org/mcp
```

## Registry Data

The server reads registry JSON files from a local directory. Three ways to get the data:

| Method | How | When to use |
|--------|-----|-------------|
| **Git clone** | `git clone https://github.com/CloudSecurityAlliance/SecID` and point at `registry/` | Development, small deployments |
| **Git submodule** | Add SecID as a submodule in your deployment repo | CI/CD managed deployments |
| **Custom registry** | Your own JSON files in the same format, with or without the public data | Private resolvers with internal data |

For private resolvers, you can merge public + private registry data:

```bash
# Start with public registry
git clone https://github.com/CloudSecurityAlliance/SecID /data/public

# Add your private registry data
cp -r /path/to/internal/registry/* /data/private/

# Point server at both
secid-api --registry /data/public/registry --registry /data/private/registry
```

## Repo Structure

```
SecID-API/
├── python/
│   ├── secid_server.py      # FastAPI server (~300 lines)
│   ├── resolver.py           # Core resolution logic
│   ├── storage.py            # Storage interface + backends
│   ├── requirements.txt      # fastapi, uvicorn, redis (optional)
│   └── README.md
├── docker/
│   ├── Dockerfile            # Multi-stage: build TypeScript, run with Node
│   ├── docker-compose.yml    # Server + Redis (optional)
│   └── README.md
├── docs/
│   ├── cloudflare-deploy.md  # "Deploy to your own Cloudflare account"
│   ├── docker-deploy.md      # Docker / Kubernetes deployment guide
│   └── python-quickstart.md  # "Run locally in 2 minutes"
├── tests/
│   └── test_resolve.py       # Shared test suite (any server should pass these)
└── README.md                 # Overview, comparison of deployment options
```

The TypeScript resolver logic for Docker can be extracted from SecID-Service (portable parts of `parser.ts`, `resolver.ts`). The Python server is a clean-room implementation of the same algorithm.

## Relationship to Other Repos

| Repo | Role |
|------|------|
| **SecID** | Spec + registry data (source of truth for JSON files) |
| **SecID-Service** | Cloudflare-hosted production (CSA runs this) |
| **SecID-API** (new) | Portable server — run your own resolver anywhere |
| **SecID-Client-SDK** | Client libraries that call any SecID server |

The local MCP plugin (`SecID/plugins/secid/server.py`) calls whichever server you point it at — public or self-hosted.

## Shared Test Suite

All server implementations (Cloudflare, Docker, Python) should pass the same test suite. Tests are input/output pairs:

```json
{
  "input": "secid:advisory/mitre.org/cve#CVE-2021-44228",
  "expected_status": "found",
  "expected_url": "https://www.cve.org/CVERecord?id=CVE-2021-44228"
}
```

This lives in `tests/` and can be run against any server URL:

```bash
python tests/test_resolve.py --server http://localhost:8000
python tests/test_resolve.py --server https://secid.cloudsecurityalliance.org
```

## Implementation Priority

1. **Python server** — simplest, most useful for developers and quick demos
2. **Docker container** — extract portable TypeScript, add Dockerfile
3. **Cloudflare deploy guide** — docs only, the code already exists
4. **Shared test suite** — validates all implementations produce identical results

## Open Questions

1. **How often should self-hosted servers refresh their registry data?** `git pull` on a cron? Webhook from the SecID repo? Manual?

2. **Should the Docker image bundle the registry data or mount it?** Bundling means you rebuild the image to update. Mounting means the data can update independently. Probably mount, with an optional bundled fallback.

3. **Authentication** — the public CSA service has no auth. Self-hosted servers may want auth. Should the API spec define auth headers, or leave it to the deployment? Probably leave it — auth is an infrastructure concern, not an API concern.

4. **Rate limiting** — self-hosted servers may want rate limiting. Same answer: infrastructure concern, not API concern. Document it in the deployment guides.

5. **Should SecID-API include a registry editor/admin UI?** Probably not in v1 — keep it as a resolver. Editing goes through git/PRs.

---

*Complements the participation model proposal. Federated and private resolvers need a "run your own" artifact — this is it.*
