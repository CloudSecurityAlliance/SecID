# Bootstrap Runbook

Step-by-step instructions for setting up the full SecID infrastructure from scratch. Use this when deploying for the first time or when self-hosting.

**Status: Outline.** Steps are ordered and rationale is documented. Exact commands and verification steps will be confirmed during the first actual deployment.

## Prerequisites

- Cloudflare account with the target zone (`cloudsecurityalliance.org` or your own domain)
- GitHub organization with repos created (done)
  - [SecID](https://github.com/CloudSecurityAlliance/SecID) (spec + registry)
  - [SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service) (API + MCP)
  - [SecID-Website](https://github.com/CloudSecurityAlliance/SecID-Website) (docs site)
  - [SecID-Client-SDK](https://github.com/CloudSecurityAlliance/SecID-Client-SDK) (client libraries)
- `wrangler` CLI installed and authenticated (`wrangler login`)
- Node.js for building SecID-Service

## Step 1: Create DNS Records (done)

DNS records created for `secid.cloudsecurityalliance.org`:

```
secid.cloudsecurityalliance.org    AAAA    100::              (proxied)
secid.cloudsecurityalliance.org    TXT     "v=spf1 -all"
```

See [DNS.md](DNS.md) for the rationale.

## Step 2: Deploy SecID-Website (Pages)

Deploy the website first because it serves `/*` (the default route). Even a placeholder page confirms the hostname and TLS work.

1. Connect SecID-Website repo to Cloudflare Pages
2. Configure custom domain: `secid.<your-domain>`
3. Deploy (even if it's just a "coming soon" page)

**Verify:** `curl https://secid.<your-domain>/` returns the website content.

## Step 3: Deploy SecID-Service (Worker)

Deploy the Worker and attach it to the API and MCP paths.

1. In SecID-Service repo, configure `wrangler.toml` with the zone and routes
2. Build the registry data: `npm run build:registry`
3. Deploy: `wrangler deploy`
4. Configure Worker Routes in Cloudflare dashboard (or via wrangler.toml):
   - `secid.<your-domain>/api/*` → SecID-Service worker
   - `secid.<your-domain>/mcp/*` → SecID-Service worker

**Verify:**
- `curl https://secid.<your-domain>/api/v1/resolve?secid=secid:advisory/mitre.org/cve%23CVE-2024-1234` returns a resolution response
- `curl https://secid.<your-domain>/mcp` returns MCP server info
- `curl https://secid.<your-domain>/` still returns the website (Pages fallback works)

## Step 4: Set Up CI/CD

Configure GitHub Actions in each repo so merges to main trigger automatic deployments.

1. **SecID-Service:** Add `CLOUDFLARE_API_TOKEN` to GitHub Actions secrets. Create workflow that builds and deploys on push to main.
2. **SecID-Website:** If using Cloudflare Pages git integration, this is automatic. Otherwise, add deploy workflow.
3. **SecID (this repo):** Add workflow that triggers SecID-Service rebuild when registry data changes (see [DATA-FLOW.md](DATA-FLOW.md)).

**Verify:** Push a trivial change to SecID-Service → confirm it auto-deploys.

## Step 5: Verify End-to-End

The full pipeline: registry change in this repo → Service rebuilds → resolution reflects the change.

1. Add or modify a registry entry in this repo
2. Merge to main
3. Confirm SecID-Service rebuild is triggered
4. Query the API for the changed entry
5. Confirm the response reflects the new data

## Step 6: Set Up SecID-Client-SDK (When Ready)

Client libraries are independent of the infrastructure. Set up CI/CD for each language when the libraries are being actively developed.

## Post-Bootstrap

Once the infrastructure is running:
- Monitor via Cloudflare Analytics dashboard
- Review [CI-CD.md](CI-CD.md) for the full automation pipeline
- Review [DEPLOYMENT.md](DEPLOYMENT.md) for rollback procedures
