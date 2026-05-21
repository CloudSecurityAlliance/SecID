# TODO

Tracking exploratory work and rough notes. **Committed work lives in GitHub issues**, not here — see [open issues](https://github.com/CloudSecurityAlliance/SecID/issues). Updated 2026-05-21.

This file is for:
- Research/exploration not yet ready for an issue
- Items intentionally deferred until evidence appears
- Notes captured in passing during sessions

Anything with a clear definition-of-done belongs in an issue.

## Recently shipped (May 2026)

This block is a quick read-out of what landed in the most recent burst of work. For the canonical history, see git log + the GitHub issues/PRs.

- **Subtype framework** — [#46](https://github.com/CloudSecurityAlliance/SecID/pull/46) (TYPES-AND-SUBTYPES.md, 43 methodology entries tagged), [#47](https://github.com/CloudSecurityAlliance/SecID/pull/47) (README), [#49](https://github.com/CloudSecurityAlliance/SecID/pull/49) (CI validator)
- **GLOSSARY proposal accepted** — [#46](https://github.com/CloudSecurityAlliance/SecID/pull/46) — `subtype: ["glossary"]` + dataset-repo pointer (Phase 1). Phase 2 content population is open as [#62](https://github.com/CloudSecurityAlliance/SecID/issues/62)
- **CLAUDE.md visibility improvements** — [#44](https://github.com/CloudSecurityAlliance/SecID/pull/44) (plugins/, working-data/, schemas/ surfaced)
- **Cross-source bare-name search fix** — [SecID-Service #9](https://github.com/CloudSecurityAlliance/SecID-Service/pull/9) — `?secid=cwe`/`capec` now finds source-level matches
- **Subtype filter UI** — [SecID-Service #9](https://github.com/CloudSecurityAlliance/SecID-Service/pull/9) — `?subtype=X` filter + clickable homepage chips
- **Auto-deploy on push to main** — [SecID-Service #9](https://github.com/CloudSecurityAlliance/SecID-Service/pull/9) — no more manual `gh workflow run` needed
- **type-registry single source of truth** — [SecID-Service #8](https://github.com/CloudSecurityAlliance/SecID-Service/pull/8) — `/api/v1/types` endpoint, MCP describe + homepage + Resolver all import from one constant

## Open follow-ups discovered during recent work

These have GitHub issues — see those for full context.

- **Overly-broad child patterns pollute search results** — [#52](https://github.com/CloudSecurityAlliance/SecID/issues/52). Patterns like `^.+$` in `control/ibm.com` create ~15 false-positives per common short query. Two strands: tighten the patterns (here) or de-weight at search time (SecID-Service).
- **Subtype tagging coverage audit** — [#53](https://github.com/CloudSecurityAlliance/SecID/issues/53). New methodology entries landed without tags ([#50](https://github.com/CloudSecurityAlliance/SecID/pull/50)); CI catches wrong values but not missing ones. Inventory pass needed.

## Migrated to issues

Items previously tracked here that now have their own issues:

| Item | Issue |
|---|---|
| Entity-vs-Publication Cleanup | [#54](https://github.com/CloudSecurityAlliance/SecID/issues/54) |
| ISF SOGP / ENX ISA control gaps | [#55](https://github.com/CloudSecurityAlliance/SecID/issues/55) |
| Disclosure safe_harbor research | [#56](https://github.com/CloudSecurityAlliance/SecID/issues/56) |
| Disclosure bug_bounty research | [#57](https://github.com/CloudSecurityAlliance/SecID/issues/57) |
| Prowler checks as control entries | [#58](https://github.com/CloudSecurityAlliance/SecID/issues/58) |
| DISA STIGs as control entries | [#59](https://github.com/CloudSecurityAlliance/SecID/issues/59) |
| TIMESTAMP-FIELDS proposal triage | [#60](https://github.com/CloudSecurityAlliance/SecID/issues/60) |
| ASSERTION-CONTENT-TYPES revision | [#61](https://github.com/CloudSecurityAlliance/SecID/issues/61) |
| GLOSSARY Phase 2 dataset entries | [#62](https://github.com/CloudSecurityAlliance/SecID/issues/62) |
| CIS Benchmarks license check | [#63](https://github.com/CloudSecurityAlliance/SecID/issues/63) |
| V2 Data Repositories | [#64](https://github.com/CloudSecurityAlliance/SecID/issues/64) |
| Training course content | [#65](https://github.com/CloudSecurityAlliance/SecID/issues/65) |
| SecID-Service format metadata | [SecID-Service #10](https://github.com/CloudSecurityAlliance/SecID-Service/issues/10) |
| SecID-Server-API format metadata | [SecID-Server-API #3](https://github.com/CloudSecurityAlliance/SecID-Server-API/issues/3) |

## Active — research and exploration

These items don't yet have enough definition to be issues. They're notes for future work.

### Capability Wave 6 — Remaining Cloud Services
**Status:** Planned, ongoing trickle
**Priority:** Low

~200 remaining AWS services, plus Azure/GCP services not yet covered. Most will be stub entries ("reviewed, no service-specific security beyond IAM"). Includes DigitalOcean, OpenShift, and other non-Big-Three providers. Best done as a long-running incremental task rather than a single issue.

### Relationship Layer Design
**Status:** Research/speculation (see [docs/future/RELATIONSHIPS.md](../future/RELATIONSHIPS.md))
**Priority:** Low (V2)

Cross-type connections: CVE → CWE → ATT&CK → control → capability. The relationship data model, storage format, and query API. Becomes more concrete once V2 datasets exist ([#64](https://github.com/CloudSecurityAlliance/SecID/issues/64)).

### Standards Registry Coverage
**Status:** Research needed
**Priority:** Medium

Many security standards span multiple SecID types or don't fit cleanly. The list below is rough — each candidate needs a placement decision before becoming an issue.

**Already covered:**
- CVSS → `methodology/org/first.json` (scoring methodology)
- EPSS → `methodology/org/first.json` (prediction methodology)
- ATT&CK → `ttp/org/mitre.json` (technique taxonomy)

**Need to add (placement TBD):**
- CSAF 2.0/2.1 → `methodology/org/oasis-open.json`? Or `reference`? Defines both a data format AND a distribution process.
- STIX 2.1 → `reference` (data format) or `methodology` (threat intel exchange process)?
- TAXII → `reference` or `methodology`?
- OpenDXL → `reference`?
- SARIF → `reference` (static analysis results format)?
- CycloneDX → `reference` (SBOM format)?
- SPDX → `reference` (SBOM format)?
- VEX / OpenVEX → `reference` or `methodology`?
- OSCAL → `reference` or `methodology`? (security assessment format)
- ROLIE → `reference` (feed format for security data)?

**Working rule:** If the standard defines a *process that produces an output* (CVSS → score, SSVC → decision), it's `methodology`. If it defines a *format for representing data* (CSAF → JSON advisory, STIX → JSON threat intel), it's `reference`. Some may need entries in both types.

### Repo hygiene: periodic stale-branch sweep
**Status:** Ongoing operational task

Local branches accumulate after PR squashes. Run `commit-commands:clean_gone` skill or `git fetch --prune` + manual review periodically. Not worth an issue per cleanup; do it whenever a session notices stragglers.

## Deferred

Items intentionally not scheduled. Promote to an issue if/when a forcing function appears.

- **Resolver and Regex Test Fixture Strategy** — fixture extraction script, negative test fixtures, regex compile checks, overlap detection, deterministic ordering tests. Deferred until CI gates need this level of rigor.
- **Resolution Instructions for Non-Deterministic Systems** — search-based resolution for systems without stable URLs.
- **MCP Interaction Logging** — log every MCP interaction to KV with TTL for usage analytics.
- **Periodic CNA Data Refresh** — re-scrape cve.org/PartnerInformation/ListofPartners on a schedule. Scripts exist in `scripts/fetch-cna-list.py` and `scripts/fetch-cna-details.py`; just needs a cron / GitHub Action.
- **Capability Freshness Monitoring** — monitor cloud provider release notes for new security features.
- **llms.txt for AI Discoverability** — implement llms.txt standard on the website.

## Done (v1.0)

See git history and merged PRs for the full list. Selected highlights:

- SecID-Server-API repo scaffolded (self-hosted Python/TypeScript resolver)
- Participation Model proposal ([docs/proposals/PARTICIPATION-MODEL.md](../proposals/PARTICIPATION-MODEL.md))
- Disclosure structured CNA fields populated across 486 entries ([docs/proposals/DISCLOSURE-TYPE-FIELDS.md](../proposals/DISCLOSURE-TYPE-FIELDS.md))
- JSON Schema for registry validation (`schemas/registry-namespace.schema.json`)
- OpenAPI spec for REST API (`schemas/openapi.yaml`)
- Capability type (9th → 10th type), 54 namespaces, 428 capabilities
- Disclosure type with 486 namespaces / 502 CVE Program partners
- URL normalization (data.source → urls[] arrays)
- Four slide decks published to `slides/` with CSA Marp theme
- MCP server enhancements (CNA workflow, feedback resource, capability descriptions)
- Standalone SecID Claude Code plugin (`/plugin install secid@csa-plugins-official`)
- CI/CD for slide generation (pre-commit hook auto-rebuilds HTML)
