# Governance

## Current Model & AI Agent Delegation

SecID is a **Cloud Security Alliance (CSA)** project. **Kurt Seifried** (Chief Innovation Officer, CSA) is the executive sponsor and human escalation point.

Day-to-day governance, engineering, issue triage, pull request review, and release management for SecID are delegated to **Gemini** as the **SecID governing agent** under the CSA Internal Governance Charter:

- **Program governance repository:** [`CSA-Internal-Governance/SecID`](https://github.com/CSA-Internal-Governance/SecID)
- **Handoff & operating rules:** [`AGENTS.md`](https://github.com/CSA-Internal-Governance/SecID/blob/main/AGENTS.md), [ADR-001 (SecID Handed to Gemini)](https://github.com/CSA-Internal-Governance/SecID/blob/main/DECISIONS-ADR/ADR-001-secid-handed-to-gemini.md), and [ADR-002 (100% Autonomy, Recursive Self-Improvement, and Learning Velocity)](https://github.com/CSA-Internal-Governance/SecID/blob/main/DECISIONS-ADR/ADR-002-100-percent-autonomy-and-recursive-self-improvement.md)
- **Repository membership & inventory:** Membership is decided in [`CSA-Internal-Governance/Charter/PROGRAMS.md`](https://github.com/CSA-Internal-Governance/Charter/blob/main/PROGRAMS.md); [`CSA-Internal-Governance/SecID/README.md`](https://github.com/CSA-Internal-Governance/SecID/blob/main/README.md) provides the descriptive inventory of each repository in the program.

Every commit authored by an AI agent carries an `AI-Agent: <Name>` trailer, and every agent-authored pull request body or issue comment begins with `*Agent: <Name> (SecID governing agent)*` so AI actions are always distinguishable from Kurt Seifried's personal statements.

## Merge = Deploy

**Merging to `main` deploys to production.**

When a pull request that modifies `registry/**/*.json` is merged to `main`, the `notify-service` job in [`.github/workflows/registry-ci.yml`](.github/workflows/registry-ci.yml) (gated on `ci-passed`) sends a `repository_dispatch` (`registry-updated`) event to [`CloudSecurityAlliance/SecID-Service`](https://github.com/CloudSecurityAlliance/SecID-Service), which syncs the updated registry to Cloudflare KV and runs post-deploy end-to-end checks against `https://secid.cloudsecurityalliance.org` (~80 seconds end-to-end).

Every merge requires:

1. **Green CI:** All required checks in `Registry CI` (`validate-schema`, `validate-subtypes`, `validate-pattern-breadth`, `tooling-tests`, aggregated in `ci-passed`) must pass.
2. **Two reviews:** The authoring agent's self-review plus a second review from an independent agent in a fresh context (and from a different model vendor — e.g. OpenAI Codex or Claude Code Review — for substantial changes that deploy to production, change the spec or registry schema, touch security-relevant code, or add a data source).
3. **Watched deploy:** Any merge that triggers production deployment is monitored through post-deploy verification.

## What the Governing Agent Decides vs. Escalates

| Category | Authority | Process |
|---|---|---|
| **Registry additions & corrections** (`registry/**/*.json`, `registry/**/*.md`) | Governing agent (autonomous) | Issue → branch → PR → `Registry CI` green → two reviews → merge → watch deploy |
| **Tooling, validators, docs, and non-breaking spec clarifications** | Governing agent (autonomous) | Same PR + CI + two-review path; design decisions recorded in [`DECISIONS.md`](DECISIONS.md) |
| **Adding a new SecID type** | Governing agent (coordinated multi-repo train) | Recorded in [`DECISIONS.md`](DECISIONS.md); coordinated across `SecID`, `SecID-Service`, `SecID-Server-API`, and `SecID-Client-SDK` |
| **Breaking changes to the v1.0 grammar (`SPEC.md`), legal/licensing questions, or CSA policy decisions** | Human decision required (**Kurt Seifried**) | Labelled `needs-human-decision` here and escalated via a `needs-kurt` issue in [`CSA-Internal-Governance/SecID`](https://github.com/CSA-Internal-Governance/SecID/issues) |
| **Changes to CI gates, required checks, branch protection, `REVIEW.md`, or reviewer instructions** | Different-vendor review + decision record required | Must be reviewed by an independent agent from a different model vendor and recorded; never merges on the authoring agent's review alone ([`CSA-Internal-Governance/SecID/AGENTS.md`](https://github.com/CSA-Internal-Governance/SecID/blob/main/AGENTS.md)) |
| **Widening agent authority, non-delegated credentials/secrets, or adding a repository to the program** | Ask-first (**Kurt Seifried**) | Propose via PR and open a `needs-kurt` issue in [`CSA-Internal-Governance/SecID`](https://github.com/CSA-Internal-Governance/SecID/issues); no actor promotes itself |
| **Charter §4 Red Lines** (deleting a repo/account/org/tenant, purging data, removing legal holds/retention, financial operations, or changing organization membership/roles/permissions) | Entrenched prohibition | Never performed by the agent at any autonomy level ([`CSA-Internal-Governance/Charter/CHARTER.md` §4](https://github.com/CSA-Internal-Governance/Charter/blob/main/CHARTER.md)) |

## Contributions & Issue Labels

Contributions from both humans and AI agents are welcome via GitHub pull requests and issues. See [`AGENTS.md`](AGENTS.md) for the full contributor guide, including **Definitions of Ready and Done**.

We use four workflow hand-off labels on issues:

- `ready-for-agent` — Scoped, acceptance criteria clear, ready for an autonomous agent or contributor to pick up.
- `in-progress` — Actively being worked by an agent or human contributor.
- `needs-human-decision` — Blocked on human policy, scope, or architectural sign-off from Kurt Seifried.
- `blocked` — Waiting on an external dependency, upstream repository, or prerequisite issue.

## Namespace Ownership (`CODEOWNERS`)

Default repository ownership is defined in [`.github/CODEOWNERS`](.github/CODEOWNERS). Under [`SPEC.md` §4.4](SPEC.md) (*Namespace Ownership and Self-Service Maintenance*) and [`docs/proposals/PARTICIPATION-MODEL.md`](docs/proposals/PARTICIPATION-MODEL.md), external organizations that verify ownership of their domain may be granted `CODEOWNERS`-scoped review/maintainership over their `registry/<type>/<tld>/<domain>.json` files.

## Feedback and Discussion

If you have questions or concerns about a decision, please open a GitHub issue (or submit feedback via the MCP `submit_feedback` tool on `secid.cloudsecurityalliance.org`). Good-faith feedback is valued and decisions can always be revisited with new information or perspective. Ultimately, CSA retains final authority over the project's direction and ownership of its repositories.
