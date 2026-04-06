# TODO

Tracking work items for SecID. Updated 2026-04-05 (v1.0 release).

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

### Technical Deep Dive Slide Deck
**Status:** Planned
**Priority:** High

Developer/integrator deck covering:
- API contract (one endpoint, encoding gotcha, response envelope)
- MCP server setup and tool descriptions
- SDK examples (Python, TypeScript, Go)
- JSON Schema for registry validation
- OpenAPI spec for code generation
- Resolution depth and cross-source search
- Building a client from the prompt template

**File:** `slides/secid-technical.md`

### Contributing Slide Deck
**Status:** Planned
**Priority:** Medium

Community contribution deck covering:
- Registry file format and templates
- Namespace-to-filesystem algorithm
- Research workflow (for capabilities: vendor docs → API scan → cross-reference)
- PR process and review
- How AI agents help with research

**File:** `slides/secid-contributing.md`

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
**Status:** Partially done
- Overview deck (17 slides) — Done
- CSA Integration deck (14 slides) — Done
- Technical deck — Planned
- Contributing deck — Planned

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
**Status:** Deferred

Auto-generate PDF/HTML from Marp markdown on push to slides/.

### llms.txt for AI Discoverability
**Status:** Deferred

Implement llms.txt standard on the website for AI-friendly content discovery.

### Standalone SecID Plugin
**Status:** Deferred

Claude Code plugin for SecID operations.
