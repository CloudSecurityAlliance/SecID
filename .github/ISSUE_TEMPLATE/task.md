---
name: Task / Namespace Contribution
about: Propose a registry namespace addition/update, documentation improvement, or tooling task (ready for human or AI agent execution)
title: ""
labels: ["ready-for-agent"]
---

## Context

<!-- Why is this needed? Link upstream sources, feedback submissions, or related issues. -->

## Expected Outcome ("What Good Looks Like")

<!-- Target SecID(s), registry file path(s) (e.g., registry/<type>/<tld>/<domain>.json), or behavior change. -->

## Acceptance Checks

<!-- How an agent or reviewer verifies the work before and after merge. -->
- [ ] `Registry CI` passes (`validate-schema`, `validate-subtypes`, `validate-pattern-breadth`, `tooling-tests`)
- [ ] Regex patterns are ECMAScript-compatible, anchored (`^...$`), and tested against real identifier examples (`docs/guides/REGEX-WORKFLOW.md`)
- [ ] Counts updated via `./scripts/update-counts.sh` (if namespaces were added or removed)
- [ ] Live resolver verified post-deploy (`https://secid.cloudsecurityalliance.org/api/v1/resolve?secid=...`) if `registry/**/*.json` changed
