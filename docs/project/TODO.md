# TODO

Tracking exploratory work and rough notes. **Committed work lives in GitHub issues**, not here — see [open issues](https://github.com/CloudSecurityAlliance/SecID/issues). Updated 2026-05-21 (second sweep).

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
- **DECISIONS.md ADR log** — [#69](https://github.com/CloudSecurityAlliance/SecID/pull/69) — 8 seed ADRs mirroring SecID-Service convention
- **CVSS reference versioned children** — [#77](https://github.com/CloudSecurityAlliance/SecID/pull/77) — `secid:reference/first.org/cvss@4.0` etc. now resolve to per-version spec docs
- **7 standards added as reference entries** — [#78](https://github.com/CloudSecurityAlliance/SecID/pull/78) — SARIF, CycloneDX, SPDX, VEX, OpenVEX, OSCAL, ROLIE (closed [#72](https://github.com/CloudSecurityAlliance/SecID/issues/72))

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
| Sharper methodology-vs-reference test (ADR-009) | [#73](https://github.com/CloudSecurityAlliance/SecID/issues/73) |
| CCM/AICM multi-type modeling | [#71](https://github.com/CloudSecurityAlliance/SecID/issues/71) |
| Relationship Layer Design | [#75](https://github.com/CloudSecurityAlliance/SecID/issues/75) |
| Automate CNA listing refresh | [#76](https://github.com/CloudSecurityAlliance/SecID/issues/76) |

## Active — research and exploration

A handful of standards-coverage candidates remain where placement decisions haven't been made. Each is a small research task before promotion to an issue.

### Standards Registry Coverage — remaining candidates

The 9 standards from the prior list landed: 3 already existed (CSAF, STIX, TAXII), 1 had ambiguous placement and gained both a reference and methodology entry (CVSS, [#77](https://github.com/CloudSecurityAlliance/SecID/pull/77)), and 7 shipped as reference-only ([#78](https://github.com/CloudSecurityAlliance/SecID/pull/78)). One more standard remains in the original list as a research item:

- **OpenDXL** → likely `reference` (data-exchange spec from McAfee/Trellix). Confirm whether the project is still maintained and whether it has any methodology-shaped content beyond the format.

Other standards worth eventual placement decisions (no committed work; promote to issue when someone wants to land them):

- ASVS (OWASP Application Security Verification Standard) → likely `control`
- MASVS (Mobile Application Security Verification Standard) → likely `control`
- WSTG (Web Security Testing Guide) → likely `methodology` (security-testing subtype)
- SSDF (NIST 800-218) — already in `methodology/gov/nist.json` as 800-218? worth confirming
- VERIS already covered as `methodology` (incident-management subtype)

**Working rule** (now codified as ADR-009 candidate in [#73](https://github.com/CloudSecurityAlliance/SecID/issues/73)): a methodology provides standalone judgement guidance citable independent of any output format. A reference specifies how data should be formatted, with judgement-involved-incidental.

## Deferred

Items intentionally not scheduled. Promote to an issue if/when a forcing function appears.

- **Resolver and Regex Test Fixture Strategy** — fixture extraction script, negative test fixtures, regex compile checks, overlap detection, deterministic ordering tests. Deferred until CI gates need this level of rigor.
- **Resolution Instructions for Non-Deterministic Systems** — search-based resolution for systems without stable URLs.
- **MCP Interaction Logging** — log every MCP interaction to KV with TTL for usage analytics.
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
