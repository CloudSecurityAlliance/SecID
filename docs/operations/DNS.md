# DNS and Routing

## Hostname

**`secid.cloudsecurityalliance.org`**

This is the permanent, canonical hostname for all SecID services. It lives under a domain CSA controls, is self-explanatory, and is stable long-term.

A shorter vanity domain (e.g., `secid.dev`) could be added later as a redirect or alias without changing anything about the underlying infrastructure.

## DNS Records

**Status: Created.**

Two records exist for the hostname:

```
secid.cloudsecurityalliance.org    AAAA    100::              (proxied)
secid.cloudsecurityalliance.org    TXT     "v=spf1 -all"
```

### AAAA Record

A proxied AAAA record pointing to the IPv6 discard prefix. Traffic never reaches `100::` — Cloudflare intercepts it at the edge and routes to the appropriate Worker or Pages deployment. The record exists solely to attach Cloudflare's proxy to the hostname.

**Why `100::`?** Standard Cloudflare pattern for Workers and Pages.

**Why AAAA, not A?** Either works. `100::` (IPv6 discard) is cleaner than `192.0.2.1` (IPv4 documentation range) and is Cloudflare's recommended approach.

### SPF Record

An explicit SPF denial: this subdomain does not send email. Without it, attackers could spoof email from `secid.cloudsecurityalliance.org` for phishing. See [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md#spf-record-on-service-subdomains) for rationale.

Both records should be created at subdomain creation time and left permanently.

## Path-Based Routing

All services share the single hostname, differentiated by path:

```
secid.cloudsecurityalliance.org
├── /api/*    → SecID-Service (Cloudflare Worker)
├── /mcp      → SecID-Service (Cloudflare Worker)
└── /*        → SecID-Service static assets (Astro site built from its website/ directory)
```

### How This Works in Cloudflare

1. A single **Worker Route**, `secid.cloudsecurityalliance.org/*`, sends every request on the hostname to the SecID-Service Worker.
2. **Workers static assets** (`[assets] directory = "./website/dist"` in SecID-Service's `wrangler.toml`) serve the website: a request that matches a built asset file is answered from the asset store.
3. Everything else reaches the Worker's Hono app, which routes `/api/v1/*`, `/mcp`, and `/health`, and returns a JSON 404 for anything else. It is one deployment for API, MCP, and website.

An earlier design put the website on a separate Cloudflare Pages project with Worker Routes for `/api/*` and `/mcp/*` in front of it. That separate site was never needed; the Worker serves the site itself.

### Why Single Hostname

- **Simple for consumers.** One domain to remember, one DNS entry, one TLS cert.
- **No CORS issues.** Website and API on the same origin means no cross-origin configuration needed.
- **Clean URL structure.** `/api/v1/resolve?secid=...` reads better than `api.secid.cloudsecurityalliance.org/v1/resolve?secid=...`.
- **Easy to add paths.** Future services (e.g., `/api/v2/`) are just new routes in the Worker.

### Why Not Separate Subdomains

Separate subdomains (`api.secid...`, `mcp.secid...`) would mean:
- Multiple DNS records to manage
- CORS configuration between origins
- More complex TLS setup
- No real benefit since everything runs on Cloudflare's edge anyway

## Future Considerations

- **Vanity domain:** If `secid.dev` or similar is acquired, it could CNAME to `secid.cloudsecurityalliance.org` or serve as a redirect. No architecture changes needed.
- **Regional endpoints:** Not planned. Cloudflare's edge network handles geographic distribution automatically.
- **API versioning:** New API versions (`/api/v2/`, `/api/v3/`) are just new routes in the same Worker. Old versions can coexist indefinitely.
