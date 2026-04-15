# TODO

Tracking work items for SecID. Updated 2026-04-06.

## Active — Next Up

### Training Course Content
**Status:** Planned
**Priority:** High

Develop training content for CSA's education platform (Skilljar/training.cloudsecurityalliance.org):
- "Using SecID" self-paced module — resolve CVEs, look up controls, find CNAs
- Lab exercises using the live resolver and MCP server
- Integration with CCSK curriculum (SecID as the lookup tool for CCM controls)
- Integration with AI security training (SecID for AI weaknesses, ATLAS techniques, AICM controls)

**Depends on:** Slide decks (overview + CSA integration done), live service (done)

### Disclosure: Safe Harbor Research
**Status:** Not started
**Priority:** Medium

Research and populate `data.safe_harbor` for disclosure entries. No standard URL or authoritative list to scrape — requires manual research per vendor.

**Approach:** Start with top 20 most-reported-to vendors (Microsoft, Google, Apple, Red Hat, Cisco, etc.). Look for safe harbor / legal safe harbor statements on their security pages. Record URL or null.

**Context:** Part of disclosure type-specific fields proposal (`docs/proposals/DISCLOSURE-TYPE-FIELDS.md`). The `cve`, `security_txt`, and `disclosure_policy` fields are already populated.

### Disclosure: Bug Bounty Research
**Status:** Not started
**Priority:** Medium

Research and populate `data.bug_bounty` for disclosure entries. Array of `{url, paid}` objects.

**Approach:** Start with top 20 vendors. Check HackerOne, Bugcrowd, Intigriti, and vendor security pages for bounty program URLs. `paid` is optional (absent = unknown).

**Context:** Same proposal as safe harbor. Note that some `disclosure_policy` URLs from CNAsList.json already point to bug bounty platforms (e.g., Adobe's points to HackerOne) — these could be cross-referenced.

### CIS Benchmarks as Control Entries
**Status:** Research needed
**Priority:** High

CIS Benchmarks contain per-check specifications for AWS/Azure/GCP. Each check maps to capabilities and abstract controls.

**Blockers:**
- License check needed — can we redistribute per-check data? CIS Terms of Use unclear on this.
- Need to determine: registry entries only (identifier + description + URL) or V2 data (full check content)?
- If license permits, extract from CIS benchmark PDFs into per-check JSON

**Namespaces:** `control/cisecurity.org/aws-benchmark`, `control/cisecurity.org/azure-benchmark`, `control/cisecurity.org/gcp-benchmark`

### Prowler Checks as Control Entries
**Status:** Research needed
**Priority:** Medium

Prowler has 938 structured checks (Apache 2.0 licensed). Each check is a prescriptive specification.

**Questions:**
- Namespace: `control/prowler.com/aws`, `control/prowler.com/azure`, `control/prowler.com/gcp`, `control/prowler.com/kubernetes`?
- Granularity: one match_node per check (938 children) or grouped by service?
- Relationship to capabilities: each Prowler check verifies a capability
- Similar tools: ScoutSuite, Steampipe, CloudCustodian — same pattern?

**License:** Apache 2.0 — no redistribution concerns for registry entries

### DISA STIGs as Control Entries
**Status:** Planned
**Priority:** Medium

DISA STIGs are US government work (public domain). Structured XCCDF XML.

**Namespaces:** `control/disa.mil/aws-stig`, `control/disa.mil/rhel9-stig`, etc.
**Data source:** https://www.cyber.mil/stigs/downloads/
**Format:** XCCDF XML → per-check JSON extraction

### SecID-Service: Surface Format Metadata in API Responses
**Status:** Not started
**Priority:** High

The registry now includes `parsability`, `schema`, `parsing_instructions`, and `auth` fields on URL objects (both source-level and per-item children). The SecID-Service resolver needs to:
- Pass through these fields in resolution result objects when present
- Support `?parsability=structured` query parameter for filtering results
- Existing `?content_type=` filter should compose with `?parsability=`

**Repo:** [CloudSecurityAlliance/SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service)
**Spec:** See `docs/reference/API-RESPONSE-FORMAT.md` "Filtering by Parsability" section
**Depends on:** Registry data already deployed (auto-deploys via GitHub Actions)

### SecID-Server-API: Surface Format Metadata in API Responses
**Status:** Not started
**Priority:** Medium

Same changes as SecID-Service but for the self-hosted resolver. Pass through `parsability`, `schema`, `parsing_instructions`, `auth` fields. Support `?parsability=` filter.

**Repo:** [CloudSecurityAlliance/SecID-Server-API](https://github.com/CloudSecurityAlliance/SecID-Server-API)
**Depends on:** SecID-Service implementation (use as reference)

### V2 Data Repositories
**Status:** Design complete, not started
**Priority:** Medium

Per DATA-HOSTING-RULES.md, create type-specific data repos:
- `CloudSecurityAlliance-DataSets/SecID-weakness/` — CWE per-record, OWASP per-item
- `CloudSecurityAlliance-DataSets/SecID-control/` — CCM/AICM per-control, NIST per-control
- `CloudSecurityAlliance-DataSets/SecID-regulation/` — GDPR per-article, AI Act per-article

**Depends on:** Existing processed data in `dataset-public-laws-regulations-standards` repo

### Capability Wave 6 — Remaining Cloud Services
**Status:** Planned
**Priority:** Low

~200 remaining AWS services, plus Azure/GCP services not yet covered. Most will be stub entries ("reviewed, no service-specific security beyond IAM"). Includes DigitalOcean, OpenShift, and other non-Big-Three providers.

### Relationship Layer Design
**Status:** Research/speculation (see docs/future/RELATIONSHIPS.md)
**Priority:** Low (V2)

Cross-type connections: CVE→CWE→ATT&CK→control→capability. The relationship data model, storage format, and query API.

## Completed (v1.0)

### SecID-Server-API Repo
**Status:** Done (v1.0)
Scaffolded `CloudSecurityAlliance/SecID-Server-API` — self-hosted Python/TypeScript resolver with same API as the Cloudflare Worker. Supports in-memory, Redis, memcached, and SQLite storage backends. Docker image published as `secid-server-api`. Any SecID client works with any server (same API contract).

### Participation Model Proposal
**Status:** Done (proposal)
`docs/proposals/PARTICIPATION-MODEL.md` defines four participation levels: pull requests (live), self-service namespace ownership (proposed), federation (proposed), private resolvers (proposed). Maps out how organizations can eventually own their own namespace files and run public resolvers.

### Disclosure: Structured CNA Fields
**Status:** Done (v1.0)
`data.cve` (role, cna_id, assignerShortName, assignerOrgId, last_assigned_cve, last_assigned_date, scope), `data.security_txt` (url), and `data.disclosure_policy` (url) populated across all 486 CNA disclosure entries. See `docs/proposals/DISCLOSURE-TYPE-FIELDS.md`.

### JSON Schema for Registry Validation
**Status:** Done (v1.0)
Created `schemas/registry-namespace.schema.json` — validates all 719 registry files.

### OpenAPI Spec for REST API
**Status:** Done (v1.0)
Created `schemas/openapi.yaml` — documents resolve, registry download, health, MCP endpoints.

### Capability Type (9th → 10th type)
**Status:** Done (v1.0)
54 capability namespaces, 428 individual capabilities across AWS/Azure/GCP.

### Disclosure Type + CNA Data
**Status:** Done (v1.0)
486 disclosure namespaces covering 502 CVE Program partners with scope, contacts, policies.

### URL Normalization
**Status:** Done (v1.0)
All `data.source` fields converted to `urls[]` arrays. Two URL mechanisms: `data.url` (resolution template) and `urls[]` (everything else).

### Slide Decks
**Status:** Done (v1.0)
- Overview deck (19 slides) — Done
- CSA Integration deck (14 slides) — Done
- Technical Deep Dive deck (16 slides) — Done
- Contributing deck (14 slides) — Done

All four decks published to `slides/` with CSA-branded Marp theme. Pre-commit hook auto-rebuilds HTML on markdown/theme changes.

### MCP Server Enhancements
**Status:** Done (v1.0)
CNA vulnerability reporting workflow, feedback resource, capability type descriptions, all 10 types.

## Deferred

### Resolver and Regex Test Fixture Strategy
**Status:** Deferred until CI gates needed

Need: fixture extraction script, negative test fixtures, regex compile checks, overlap detection, deterministic ordering tests.

### Resolution Instructions for Non-Deterministic Systems
**Status:** Deferred until needed

Search-based resolution for systems without stable URLs.

### MCP Interaction Logging
**Status:** Deferred

Log every MCP interaction to KV with TTL for usage analytics.

### Periodic CNA Data Refresh
**Status:** Deferred

Re-scrape cve.org/PartnerInformation/ListofPartners periodically. Scripts exist in `scripts/fetch-cna-list.py` and `scripts/fetch-cna-details.py`.

### Capability Freshness Monitoring
**Status:** Deferred

Monitor cloud provider release notes for new security features. Update capability entries when services change.

### CI/CD for Slide Generation
**Status:** Done (pre-commit hook)

Pre-commit hook at `.git/hooks/pre-commit` auto-rebuilds HTML from Marp markdown when `slides/*.md` or `slides/theme/*.css` are staged. Full GitHub Actions workflow for PDF generation remains deferred.

### llms.txt for AI Discoverability
**Status:** Deferred

Implement llms.txt standard on the website for AI-friendly content discovery.

### Standalone SecID Plugin
**Status:** Done (v1.0)

Claude Code plugin scaffolded and published to `CloudSecurityAlliance/csa-plugins-official` marketplace. Install via `/plugin install secid@csa-plugins-official`. Provides resolve, lookup, and describe tools via local MCP server. Supports `--base-url` flag for internal resolvers.
