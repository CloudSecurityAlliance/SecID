# Deployment

How each SecID component is deployed, updated, and rolled back.

**Status: Outline.** Deployment targets and strategy are decided. Exact commands and configurations will be filled in when the repos exist.

## Components

| Component | Deployment Target | Mechanism |
|-----------|------------------|-----------|
| SecID-Service | Cloudflare Worker | `wrangler deploy` (via GitHub Actions) |
| SecID-Website | Cloudflare Pages | Git integration or `wrangler pages deploy` |
| SecID-Client | Package registries (PyPI, npm, etc.) | Per-language publish workflows |

## SecID-Service (Worker)

### Deploy

Triggered automatically on merge to main (see [CI-CD.md](CI-CD.md)):

1. GitHub Actions checks out the repo
2. Builds registry data from latest SecID repo (`npm run build:registry`)
3. Runs test suite
4. Deploys via `wrangler deploy`

**Preview deploys:** Every PR gets a preview deployment on a unique URL for testing before merge.

### Rollback

Cloudflare Workers support instant rollback to previous deployments:

```bash
wrangler rollback
```

The previous version is restored immediately at the edge. No rebuild needed.

### Configuration

Worker configuration lives in `wrangler.toml` in the SecID-Service repo:
- Worker name
- Route patterns (`/api/*`, `/mcp/*`)
- Compatibility date
- KV namespace bindings (future, if needed)

## SecID-Website (Pages)

### Deploy

**Option 1: Cloudflare Pages git integration (recommended)**
- Connect the SecID-Website repo to Cloudflare Pages
- Every push to main auto-deploys
- Every PR gets a preview deployment
- No GitHub Actions needed

**Option 2: Manual/CI deploy**
- Build the site locally or in CI
- Deploy via `wrangler pages deploy <directory>`

### Rollback

Cloudflare Pages maintains deployment history. Rollback to any previous deployment via the Cloudflare dashboard or API.

## SecID-Client (Libraries)

Each language publishes independently:

| Language | Registry | Publish Command |
|----------|----------|----------------|
| Python | PyPI | `twine upload` or `flit publish` |
| npm/TypeScript | npm | `npm publish` |
| Go | Go module proxy | `git tag` (automatic) |
| Rust | crates.io | `cargo publish` |
| Java | Maven Central | `mvn deploy` |
| C#/.NET | NuGet | `dotnet nuget push` |

Client releases are **not** triggered by Service or registry changes. They have their own version numbers and release when their code changes warrant it.

## Environment Strategy

**Production only, with preview deploys.** No separate staging environment.

**Why no staging?**
- Cloudflare preview deploys serve the same purpose (test before merge)
- The service is stateless (no database migrations to worry about)
- Registry data is the same everywhere (no staging-specific data)
- Rollback is instant if something goes wrong in production

If operational experience shows we need a persistent staging environment, we can add one later by deploying a second Worker with a different route (e.g., `staging-secid.cloudsecurityalliance.org`).
