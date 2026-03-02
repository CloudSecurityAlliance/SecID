# CI/CD Pipeline

Automation for testing, validating, and promoting changes to production.

**Status: Outline.** The goal and per-repo pipeline design are documented. Exact GitHub Actions workflows will be written when the repos exist.

## Goal

**Merge to main → tested → validated → production with minimal human interaction.**

Human review happens at the PR stage. Once a PR is approved and merged, the pipeline handles everything else. No manual deploy steps, no "did someone remember to push to production?"

## Per-Repo Pipelines

### SecID (This Repo)

This repo has two kinds of changes: documentation and registry data. Only registry data changes need to trigger downstream rebuilds.

**On every PR:**
- Lint markdown (if markdownlint is configured)
- Validate YAML frontmatter in registry files (required fields present)
- Validate JSON registry files against schema (when schema exists)
- Check for broken internal links between documents

**On merge to main (when `registry/**/*.json` changes):**
- Trigger SecID-Service rebuild via `repository_dispatch` (see [DATA-FLOW.md](DATA-FLOW.md))

**On merge to main (documentation-only changes):**
- No downstream action needed. Docs are consumed directly from GitHub.

### SecID-Service

**On every PR:**
- Install dependencies
- Build registry data from latest SecID repo
- Run unit tests
- Run compliance test suite against the built Worker (see [skills/compliance-testing/](../../skills/compliance-testing/))
- Deploy to Cloudflare preview URL
- Run integration tests against preview URL
- Report preview URL in PR comment for manual verification

**On merge to main:**
- Same build + test steps
- Deploy to production via `wrangler deploy`
- Run smoke tests against production URL (basic resolution check)
- If smoke tests fail: alert (but don't auto-rollback — investigate first)

### SecID-Website

**On every PR:**
- Build the site
- Deploy to Cloudflare Pages preview URL
- Report preview URL in PR comment

**On merge to main:**
- Build and deploy to production (automatic via Cloudflare Pages git integration)

### SecID-Client

**On every PR (per language):**
- Run language-specific tests
- Run compliance test suite against the public API
- Lint / type-check

**On release tag:**
- Build package
- Publish to language registry (PyPI, npm, etc.)
- Run post-publish verification (install from registry, run smoke test)

## Cross-Repo Triggers

The main cross-repo dependency: registry changes here → Service rebuild.

```
SecID repo                          SecID-Service repo
────────                            ──────────────────
push to main
    │
    ├── registry/**/*.json changed?
    │       │
    │       yes → repository_dispatch ──→ "registry-updated" event
    │                                         │
    │                                         ├── build:registry
    │                                         ├── test
    │                                         └── wrangler deploy
    │
    └── docs only? → no downstream action
```

**Implementation:** A GitHub Actions workflow in this repo uses `peter-evans/repository-dispatch` (or equivalent) to send an event to SecID-Service. The Service repo has a workflow that triggers on `repository_dispatch` with type `registry-updated`.

**Credential needed:** A GitHub token (fine-grained PAT or GitHub App token) with permission to dispatch events to the SecID-Service repo. This lives in this repo's GitHub Actions secrets.

## Testing Strategy

| Test Type | When | Where |
|-----------|------|-------|
| Registry validation (YAML/JSON lint) | PR to SecID | GitHub Actions in this repo |
| Unit tests | PR to SecID-Service | GitHub Actions in Service repo |
| Compliance test suite | PR to SecID-Service | Against preview deployment |
| Integration tests | Merge to SecID-Service | Against production |
| Smoke tests | After any production deploy | Against production |
| Client tests | PR to SecID-Client | Against public API |

The compliance test suite (see [skills/compliance-testing/](../../skills/compliance-testing/)) is the most important quality gate. It runs canonical test cases (input SecID → expected parse + expected URLs) against the actual deployed service. A PR to SecID-Service cannot merge if compliance tests fail.

## Failure Handling

**PR fails tests:** Block merge. Author fixes and re-pushes.

**Production deploy fails:** Wrangler reports the failure. Previous deployment remains active (Cloudflare Workers are atomic — a failed deploy doesn't affect the running version).

**Smoke tests fail after deploy:** Alert the team. Investigate before rolling back — the failure might be in the smoke test, not the deploy. Use `wrangler rollback` if the deploy is confirmed bad.

**Cross-repo dispatch fails:** SecID-Service doesn't rebuild. Registry change is delayed but not lost — next push to Service, or a manual dispatch, picks it up. Not critical enough to page anyone.
