# SecID Operations

This directory documents how SecID is deployed and operated as a production service. For *what* the components are and their technical design, see [INFRASTRUCTURE.md](../reference/INFRASTRUCTURE.md). This directory covers *how* they're set up, deployed, and kept running.

## Repositories

SecID is split across four repositories. All are public (see [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md#all-repositories-are-public)).

| Repository | License | Purpose | Why Separate |
|------------|---------|---------|-------------|
| **[SecID](https://github.com/CloudSecurityAlliance/SecID)** | CC0 1.0 | Spec, registry data, design docs, operations docs | Source of truth. Everything starts here. |
| **[SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service)** | Apache 2.0 | Cloudflare Worker serving `/api/*` and `/mcp/*` | Has its own build/deploy/test cycle. Code that runs in production. Can be self-hosted by others. |
| **[SecID-Website](https://github.com/CloudSecurityAlliance/SecID-Website)** | CC0 1.0 | Cloudflare Pages serving `/*` | Derived content (generated from other repos). Different deployment mechanism (Pages vs Workers). |
| **[SecID-Client-SDK](https://github.com/CloudSecurityAlliance/SecID-Client-SDK)** | Apache 2.0 | Client libraries (Python, npm, Go, Rust, Java, C#) | Independent release cadence per language. Consumers of the API, not the API itself. |

**Why not fewer repos?**

- Service and Website have fundamentally different deployment targets (Workers vs Pages) and different CI pipelines. Combining them creates unnecessary coupling.
- Client libraries depend on the API being stable, not on the API code. They release when *they're* ready, not when the service deploys.
- This repo (spec + registry) changes frequently during research. Service only needs to rebuild when registry *data* changes, not when documentation is edited.

**Why not more repos?**

- Operations docs live here because they're documentation, not code (see [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md#operations-documentation-lives-in-this-repo)).
- Client libraries share enough tooling and CI patterns that a monorepo with per-language directories is simpler than 6 separate repos. If a language's needs diverge significantly, it can be extracted later.

## Documents in This Directory

| Document | What It Covers | Status |
|----------|---------------|--------|
| [DNS.md](DNS.md) | Domain, hostname, DNS records, routing layout | Ready |
| [BOOTSTRAP.md](BOOTSTRAP.md) | Step-by-step from zero to running | Outline — details confirmed during first deploy |
| [DATA-FLOW.md](DATA-FLOW.md) | How registry data moves from this repo to SecID-Service | Outline — architecture decided, details emerge during Service build |
| [DEPLOYMENT.md](DEPLOYMENT.md) | How each component deploys, rollback procedures | Outline — depends on Service/Website repos existing |
| [CI-CD.md](CI-CD.md) | Automation pipeline, cross-repo triggers, testing gates | Outline — goal described, implementation during Service build |

## Hostname

All services live under a single hostname with path-based routing:

```
secid.cloudsecurityalliance.org
├── /api/*    → SecID-Service (Cloudflare Worker)
├── /mcp/*    → SecID-Service (Cloudflare Worker)
└── /*        → SecID-Website (Cloudflare Pages)
```

See [DNS.md](DNS.md) for the full rationale and setup.

## Key Principles

**No application secrets.** The Worker reads public registry data and returns URLs. The website is static. No databases, no auth systems, no API keys in application code. The only credential is a CI deploy token in GitHub Actions secrets.

**Minimal human interaction for deploys.** The goal is: merge to main → tested → validated → promoted to production automatically. Human review happens at the PR stage, not the deploy stage.

**Self-hostable.** All repos are public, all code is CC0. Anyone can run their own SecID infrastructure. These docs describe CSA's deployment, but the pattern is reusable.
