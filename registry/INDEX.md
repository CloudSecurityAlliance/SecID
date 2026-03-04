# Registry Index

Quick reference for the state of every registry entry. Helps humans track progress
and helps AI agents find relevant entries without reading every file.

Last updated: 2026-03-03

## Summary

**121 entries** across 7 types, **15 JSON conversions**, **67 resolvable** (have patterns + URLs)

| Maturity | Count | Meaning |
|----------|-------|---------|
| pilot | 15 | Has reviewed .json conversion alongside .md |
| draft | 52 | Has patterns, URLs, and substantive documentation |
| partial | 44 | Has URLs and documentation but missing patterns or lookup |
| stub | 10 | Minimal entry, needs significant research |

## Cross-Cutting Concerns

Issues that affect multiple entries. Fix these systematically rather than per-entry.

### No resolution patterns (41 entries)

These entries have no `id_pattern` or `id_patterns` in YAML frontmatter. Without
patterns, the resolver cannot match subpath identifiers. Some are expected (entities
don't resolve subpaths; some sources have no formal IDs). Others need patterns added.

### Download-and-extract sources

Some sources have no per-item web URLs. Resolution returns a download URL and
extraction instructions instead. Known cases:
- **NIST SP 800-53, CSF 2.0** — JavaScript SPA, no stable per-control URLs. Third-party csf.tools provides them.
- **CSA CCM, AICM** — ZIP bundle download, search within spreadsheet or OSCAL data.
- **BIML ML/LLM Risks** — index page only, no per-risk deep links.

### SPA sites (client-side routing)

URLs are correct for browser navigation but return HTTP 404 on direct server requests:
- **MITRE ATLAS** (atlas.mitre.org) — all technique/tactic/study URLs
- **NIST CPRT** (csrc.nist.gov) — hash-fragment-based navigation

### Version handling gaps

Most .md entries list versions but don't document `version_required` or
`versions_available` semantics. The pilot .json files demonstrate the correct
pattern — needs propagation during .md-to-.json conversion.

### Structural inconsistency in .md files

Three frontmatter shapes: nested `sources:` block (most types), flat top-level
fields (reference, regulation), and `names:` block (entity). The JSON format
standardizes everything into `match_nodes`. Not a blocker — the .md→.json
conversion handles the mapping.

## advisory (42 entries, 10 pilots, 30 resolvable)

| Namespace | Description | Maturity | JSON | Patterns | Lookup | Updated | Notes |
|-----------|-------------|----------|------|----------|--------|---------|-------|
| `com/redhat` | Red Hat (IBM) (errata, cve, bugzilla) | pilot | yes | yes | yes | 2026-02-10 |  |
| `org/mitre` | MITRE Corporation (cve) | pilot | yes | yes | yes | 2026-02-10 |  |
| `com/apple` | Apple Inc. (ht) | pilot | yes | yes | yes | 2026-03-03 |  |
| `com/cisco` | Cisco Systems, Inc. (psirt, bug) | pilot | yes | yes | yes | 2026-03-03 |  |
| `com/github` | GitHub (Microsoft) (ghsa) | pilot | yes | yes | yes | 2026-03-03 |  |
| `com/google` | Google LLC (Alphabet) (osv, chrome, android +2) | pilot | yes | yes | yes | 2026-03-03 |  |
| `com/microsoft` | Microsoft Corporation (msrc, advisory, kb +2) | pilot | yes | yes | yes | 2026-03-03 |  |
| `gov/cisa` | CISA (kev, vulnrichment, ics-advisories, alerts) | pilot | yes | yes | yes | 2026-03-03 |  |
| `org/cert` | CERT Coordination Center (vu) | pilot | yes | yes | yes | 2026-03-03 |  |
| `org/debian` | Debian Project (dsa, dla, tracker +1) | pilot | yes | yes | yes | 2026-03-03 |  |
| `com/amazon/aws` | Amazon Web Services (security-bulletins, alas) | draft | — | yes | yes | 2026-02-10 |  |
| `com/atlassian` | Atlassian Corporation (jira-security) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `com/embracethered` | Embrace the Red (monthofaibugs) | draft | — | yes | yes | 2026-02-10 |  |
| `com/fortinet` | Fortinet, Inc. (fsa) | draft | — | yes | yes | 2026-02-10 |  |
| `com/huawei` | Huawei Technologies (psirt, security-advisories, security-noti...) | draft | — | yes | yes | 2026-02-10 |  |
| `com/oracle` | Oracle Corporation (cpu, alert, linux +1) | draft | — | yes | yes | 2026-02-10 |  |
| `com/paloaltonetworks` | Palo Alto Networks (pan-sa) | draft | — | yes | yes | 2026-02-10 |  |
| `com/suse` | SUSE (suse-su, bugzilla) | draft | — | yes | yes | 2026-02-10 |  |
| `com/ubuntu` | Ubuntu (Canonical) (usn, cve-tracker, launchpad) | draft | — | yes | yes | 2026-02-10 |  |
| `com/vmware` | VMware (Broadcom) (vmsa) | draft | — | yes | yes | 2026-02-10 |  |
| `dev/go` | Go Programming Language (vulndb) | draft | — | yes | yes | 2026-02-10 |  |
| `gov/nist` | NIST (nvd) | draft | — | yes | yes | 2026-02-10 |  |
| `org/apache` | Apache Software Foundation (security, jira) | draft | — | yes | yes | 2026-02-10 |  |
| `org/avidml` | AI Vulnerability Database (avid) | draft | — | yes | yes | 2026-02-10 |  |
| `org/kernel` | Linux Kernel (kernel) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `org/mozilla` | Mozilla Foundation (mfsa, bugzilla) | draft | — | yes | yes | 2026-02-10 |  |
| `org/openssl` | OpenSSL Project (secadv) | draft | — | yes | yes | 2026-02-10 |  |
| `org/partnershiponai` | Partnership on AI (aiid) | draft | — | yes | yes | 2026-02-10 |  |
| `org/pypi` | Python Package Index (advisory-db) | draft | — | yes | yes | 2026-02-10 |  |
| `org/rustsec` | RustSec Advisory Database (advisories) | draft | — | yes | yes | 2026-02-10 |  |
| `com/alibaba` | Alibaba Cloud (security) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/baidu` | Baidu (security) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/digitalocean` | DigitalOcean (security) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/hetzner` | Hetzner Online (status) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/ibm` | IBM Corporation (security-bulletin, cloud, psirt +1) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/ovhcloud` | OVHcloud (security) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/protectai` | Protect AI (sightline, huntr) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/tencent` | Tencent (tsrc, cloud) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `gov/ca/dmv` | California DMV (av-collision, av-disengagement) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `gov/fda` | FDA (maude, aiml-devices, recalls) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `gov/nhtsa` | NHTSA (sgo, av-recalls, investigations) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `org/aiaaic` | AIAAIC (incidents) | partial | — | **no** | — | 2026-02-10 | no patterns |

## control (24 entries, 2 pilots, 8 resolvable)

| Namespace | Description | Maturity | JSON | Patterns | Lookup | Updated | Notes |
|-----------|-------------|----------|------|----------|--------|---------|-------|
| `gov/nist` | NIST (800-53, csf) | pilot | yes | yes | yes | 2026-02-10 |  |
| `org/cloudsecurityalliance` | Cloud Security Alliance (ccm, aicm, ai-safety) | pilot | yes | yes | — | 2026-03-02 | no lookup URL (download-and-extract) |
| `cn/org/tc260` | SAC / TC260 (ai-safety-governance) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `com/concordia-ai` | Concordia AI (frontier-ai-rmf) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `org/cisecurity` | CIS Controls (controls) | draft | — | yes | yes | 2026-02-10 |  |
| `org/iso` | ISO (27001, 27002, 42001 +1) | draft | — | yes | — | 2026-02-10 | no lookup URL; paywalled |
| `org/owasp` | OWASP (ai-exchange) | draft | — | yes | yes | 2026-02-10 |  |
| `sh/mcpshark` | MCPShark (smart) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `ai/safe` | Center for AI Safety (harmbench, wmdp) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/github/llm-attacks` | AdvBench (benchmark) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/github/nyu-mll` | Bias Benchmarks (bbq, winobias, stereoset +1) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/github/thu-coai` | SafetyBench (benchmark) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/google` | Google (saif, frontier-safety) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/meta` | Meta Platforms (purple-llama, cyberseceval) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `com/openai` | OpenAI (model-spec, preparedness, red-teaming +1) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `eu/europa` | European Union (altai, ethics-guidelines, ai-act) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `io/github/jailbreakbench` | JailbreakBench (benchmark) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `io/github/trustllmbenchmark` | TrustLLM Benchmark (benchmark) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `org/alignment` | ARC Evals (evals) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `org/allenai` | Allen Institute for AI (decodingtrust, realtoxicityprompts) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `org/ieee` | IEEE (ethically-aligned-design) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `org/metr` | METR (task-standard, evals) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `org/mlcommons` | MLCommons (ai-safety, croissant, mlperf) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `sg/gov/imda` | Singapore (ai-verify, model-governance) | partial | — | **no** | — | 2026-02-10 | no patterns |

## weakness (13 entries, 2 pilots, 9 resolvable)

| Namespace | Description | Maturity | JSON | Patterns | Lookup | Updated | Notes |
|-----------|-------------|----------|------|----------|--------|---------|-------|
| `org/mitre` | MITRE (cwe) | pilot | yes | yes | yes | 2026-02-10 |  |
| `org/owasp` | OWASP (top10, llm-top10, ml-top10, agentic-top10, aivss, ai-exchange) | pilot | yes | yes | yes | 2026-03-02 |  |
| `ai/gpai` | GPAI (risk-sources) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `com/berryvilleiml` | Berryville IML (ml-risks, llm-risks) | draft | — | yes | yes | 2026-02-10 |  |
| `com/ibm` | IBM (ai-risk-atlas) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `edu/mit` | MIT (ai-risk-repository) | draft | — | yes | yes | 2026-02-10 |  |
| `gov/nist` | NIST (ai-100-2) | draft | — | yes | yes | 2026-02-10 |  |
| `org/avidml` | AVID (taxonomy) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `org/mlcommons` | MLCommons (ailuminate) | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `com/anthropic` | Anthropic (asl) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `edu/stanford` | Stanford CRFM (air-bench, helm) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `eu/europa/enisa` | ENISA (ml-threats, ai-framework) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `org/oecd` | OECD (ai-classification) | partial | — | **no** | — | 2026-02-10 | no patterns |

## ttp (4 entries, 1 pilot, 1 resolvable)

| Namespace | Description | Maturity | JSON | Patterns | Lookup | Updated | Notes |
|-----------|-------------|----------|------|----------|--------|---------|-------|
| `org/mitre` | MITRE (attack, atlas, capec) | pilot | yes | yes | yes | 2026-02-10 |  |
| `com/lockheedmartin` | Lockheed Martin (killchain) | partial | — | **no** | — | 2026-02-10 | no patterns; phases are well-known names |
| `com/unifiedkillchain` | Unified Kill Chain (ukc) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `net/veriscommunity` | VERIS Framework (framework) | partial | — | **no** | — | 2026-02-10 | no patterns |

## entity (13 entries, 0 pilots, 0 resolvable)

Entity entries describe organizations, not data sources. They use `names:` blocks
instead of `sources:` and don't resolve subpath identifiers directly — they point
to other types via cross-references. "No patterns" is expected for this type.

| Namespace | Description | Maturity | JSON | Updated | Notes |
|-----------|-------------|----------|------|---------|-------|
| `com/cisco` | Cisco Systems (psirt, ios, ios-xe +3) | partial | — | 2026-02-10 |  |
| `com/github` | GitHub, Inc. (ghsa) | stub | — | 2026-02-10 |  |
| `com/google` | Google LLC (osv) | stub | — | 2026-02-10 |  |
| `com/microsoft` | Microsoft Corporation (msrc, azure, windows +3) | partial | — | 2026-02-10 |  |
| `com/paperpile` | Paperpile (ai-risk-frameworks) | partial | — | 2026-02-10 |  |
| `com/redhat` | Red Hat, Inc. (openshift, rosa +7) | partial | — | 2026-02-10 |  |
| `gov/nist` | NIST (nvd) | stub | — | 2026-02-10 |  |
| `org/cloudsecurityalliance` | Cloud Security Alliance (ccm, aicm) | stub | — | 2026-02-10 |  |
| `org/debian` | Debian Project (debian) | stub | — | 2026-02-10 |  |
| `org/first` | FIRST (cvss, epss) | stub | — | 2026-02-10 |  |
| `org/mitre` | MITRE (cve, cwe, attack +2) | stub | — | 2026-02-10 |  |
| `org/owasp` | OWASP (top-10, llm-top-10) | stub | — | 2026-02-10 |  |
| `sh/mcpshark` | MCPShark (smart) | partial | — | 2026-02-10 |  |

## reference (21 entries, 0 pilots, 19 resolvable)

| Namespace | Description | Maturity | JSON | Patterns | Lookup | Updated | Notes |
|-----------|-------------|----------|------|----------|--------|---------|-------|
| `com/amazon` | Amazon (ASIN) | draft | — | yes | yes | 2026-02-10 |  |
| `com/ssrn` | SSRN | draft | — | yes | yes | 2026-02-10 |  |
| `gov/nih` | PubMed | draft | — | yes | yes | 2026-02-10 |  |
| `gov/whitehouse` | White House / Executive Branch | draft | — | yes | — | 2026-02-10 | no lookup URL |
| `org/acm` | ACM Digital Library | draft | — | yes | yes | 2026-02-10 |  |
| `org/arxiv` | arXiv Preprints | draft | — | yes | yes | 2026-02-10 |  |
| `org/dblp` | DBLP Bibliography | draft | — | yes | yes | 2026-02-10 |  |
| `org/doi` | Digital Object Identifier | draft | — | yes | yes | 2026-02-10 |  |
| `org/iacr` | IACR Cryptology ePrint | draft | — | yes | yes | 2026-02-10 |  |
| `org/ieee` | IEEE Xplore | draft | — | yes | yes | 2026-02-10 |  |
| `org/ietf` | IETF (RFCs, Internet-Drafts) | draft | — | yes | yes | 2026-02-10 |  |
| `org/isbn` | ISBN | draft | — | yes | yes | 2026-02-10 |  |
| `org/issn` | ISSN | draft | — | yes | yes | 2026-02-10 |  |
| `org/ndss-symposium` | NDSS Symposium | draft | — | yes | yes | 2026-02-10 |  |
| `org/openalex` | OpenAlex | draft | — | yes | yes | 2026-02-10 |  |
| `org/semanticscholar` | Semantic Scholar | draft | — | yes | yes | 2026-02-10 |  |
| `org/techrxiv` | TechRxiv | draft | — | yes | yes | 2026-02-10 |  |
| `org/usenix` | USENIX Association | draft | — | yes | yes | 2026-02-10 |  |
| `org/zenodo` | Zenodo | draft | — | yes | yes | 2026-02-10 |  |
| `uk/gov` | UK Government (ai-safety-report) | partial | — | **no** | — | 2026-02-10 | no patterns |
| `uk/gov/aisi` | AI Safety Institutes (uk, us, japan +1) | partial | — | **no** | — | 2026-02-10 | no patterns |

## regulation (4 entries, 0 pilots, 0 resolvable)

| Namespace | Description | Maturity | JSON | Patterns | Lookup | Updated | Notes |
|-----------|-------------|----------|------|----------|--------|---------|-------|
| `eu/europa` | European Union | partial | — | **no** | yes | 2026-02-10 | no patterns; has CELEX lookup but no ID mapping |
| `gov/govinfo` | United States Federal | partial | — | **no** | — | 2026-02-10 | no patterns |
| `gov/ca` | California State | stub | — | **no** | — | 2026-02-10 | no patterns |
| `gov/ny` | New York State | stub | — | **no** | — | 2026-02-10 | no patterns |

## Notable Gaps

Major sources not yet in the registry:

| Type | Source | Notes |
|------|--------|-------|
| advisory | Snyk (snyk.io) | Open-source vulnerability database |
| advisory | Rapid7 (rapid7.com) | AttackerKB, Metasploit modules |
| control | PCI-DSS (pcisecuritystandards.org) | Payment card security standard |
| control | SOC 2 / AICPA (aicpa.org) | Audit framework (no public control list) |
| reference | RFC (rfc-editor.org) | Internet standards (IETF entry covers RFCs but not as reference type) |
| reference | NIST publications (csrc.nist.gov) | SP 800-series beyond 800-53 |
| weakness | CVSS (first.org) | Scoring system — metrics as subpaths |
| ttp | D3FEND (d3fend.mitre.org) | Defensive technique taxonomy |

## Maintenance

This file is manually maintained. Update when:
- Adding a new registry entry
- Converting an entry to JSON (maturity → pilot)
- Adding patterns or lookup URLs to an entry
- Identifying or resolving a cross-cutting concern
