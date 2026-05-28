# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**SecID is about labeling and finding security knowledge. That's it.**

SecID provides a grammar and registry for referencing security knowledge. SecID does not assign identifiers—those come from their respective authorities (MITRE, NIST, etc.).

Format: `secid:type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]`

Examples:
- `secid:advisory/mitre.org/cve#CVE-2024-1234` - CVE record
- `secid:weakness/mitre.org/cwe#CWE-79` - CWE weakness
- `secid:ttp/mitre.org/attack#T1059.003` - ATT&CK technique
- `secid:control/nist.gov/csf@2.0#PR.AC-1` - NIST CSF control
- `secid:reference/arxiv.org/2303.08774` - arXiv paper

## Current Status: v1.0 (Live)

The resolver is live at secid.cloudsecurityalliance.org with 1,768 namespaces across 10 types. The grammar, type list, and registry format are frozen for v1.0. Post-1.0 work continues on the Relationship Data Layer and Data Enrichment Layer (parallel research tracks).

See ROADMAP.md for details.

## Three Layers

SecID separates concerns:

| Layer | Contains | Example |
|-------|----------|---------|
| **Registry** | Identity, resolution, disambiguation | "CVE IDs look like CVE-YYYY-NNNNN, resolve at cve.org" |
| **Relationship** | Equivalence, succession | "This DOI = this arXiv paper" |
| **Data** | Enrichment, metadata | "This CVE affects Linux, severity high" |

The registry (this repo) only handles identity, resolution, and disambiguation.

## Document Map

With 20+ markdown files, know which document answers which question:

| Question | Read This |
|----------|-----------|
| What are the design principles? | [PRINCIPLES.md](PRINCIPLES.md) - AI-first, helpful over correct, four response outcomes |
| How do SecID strings work? | [SPEC.md](SPEC.md) - grammar, types, parsing, encoding |
| Why does SecID exist? | [RATIONALE.md](docs/explanation/RATIONALE.md) |
| Why was X designed this way? | [DESIGN-DECISIONS.md](docs/explanation/DESIGN-DECISIONS.md) - longer-form explanations |
| When was X decided, what were the alternatives? | [DECISIONS.md](DECISIONS.md) - chronological ADR log with rejected alternatives |
| How do I add a namespace? | [REGISTRY-GUIDE.md](docs/guides/REGISTRY-GUIDE.md) - principles, patterns, process |
| How do I add a namespace (step-by-step)? | [ADD-NAMESPACE.md](docs/guides/ADD-NAMESPACE.md) - task-oriented walkthrough |
| How do I update an existing namespace? | [UPDATE-NAMESPACE.md](docs/guides/UPDATE-NAMESPACE.md) |
| How do I convert YAML to JSON? | [YAML-TO-JSON.md](docs/guides/YAML-TO-JSON.md) |
| How do I write and test regex patterns? | [REGEX-WORKFLOW.md](docs/guides/REGEX-WORKFLOW.md) |
| What's the JSON schema? | [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) - target format for v1.0+ |
| What's the current file format? | [REGISTRY-FORMAT.md](docs/reference/REGISTRY-FORMAT.md) - YAML+Markdown (what's in use now) |
| What's being built and when? | [ROADMAP.md](ROADMAP.md) |
| How does versioning work? | [VERSIONING.md](docs/reference/VERSIONING.md) - analysis, API behavior, response outcomes |
| Edge cases with domains? | [EDGE-CASES.md](docs/reference/EDGE-CASES.md) |
| When do we host data ourselves? | [DATA-HOSTING-RULES.md](docs/reference/DATA-HOSTING-RULES.md) - the 3 rules, licensing, data repo structure |
| What's deferred? | [TODO.md](docs/project/TODO.md), [registry/_deferred/](registry/_deferred/) |
| What's proposed? | [docs/proposals/](docs/proposals/) - proposals for registry schema changes |
| Multi-repo architecture? | [INFRASTRUCTURE.md](docs/reference/INFRASTRUCTURE.md) |
| What does the API return? | [API-RESPONSE-FORMAT.md](docs/reference/API-RESPONSE-FORMAT.md) - envelope, progressive resolution, cross-source search |
| AI agent instructions? | [AGENTS.md](AGENTS.md) |
| How is SecID deployed? | [docs/operations/](docs/operations/) - DNS, deployment, CI/CD, bootstrap |
| How do I research a new namespace? | [skills/registry-research/](skills/registry-research/) - research workflow skill |
| How do I convert .md to .json? | [skills/registry-formalization/](skills/registry-formalization/) - formalization skill |
| How do I validate a registry entry? | [skills/registry-validation/](skills/registry-validation/) - validation skill |
| How do I test a resolver? | [skills/compliance-testing/](skills/compliance-testing/) - compliance testing skill |
| How do I use SecID as an end user? | [skills/secid-user/](skills/secid-user/) - end-user usage skill |
| How do I add a methodology? | [METHODOLOGY-PROCESS.md](docs/proposals/METHODOLOGY-PROCESS.md) |
| What format/schema does a URL return? | [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) "Format Metadata" section |
| How do I parse a specific data format? | [docs/parsers/](docs/parsers/) - parsing instruction documents (e.g., cve-json-5.md) |
| Is this acronym/short-name already used? | [NAMING-COLLISIONS.md](docs/NAMING-COLLISIONS.md) - consolidated acronym collisions; resolution is always by canonical DNS namespace |
| What subtypes (kinds) exist within a type? | [TYPES-AND-SUBTYPES.md](docs/reference/TYPES-AND-SUBTYPES.md) - 10 types + named subtypes (e.g., `subtype: ["glossary"]`) + when to subtype vs. split |
| What's the JSON Schema for registry files? | [schemas/registry-namespace.schema.json](schemas/registry-namespace.schema.json) (Draft 2020-12); REST API in [schemas/openapi.yaml](schemas/openapi.yaml) |

Documents in [docs/future/](docs/future/) (RELATIONSHIPS.md, OVERLAYS.md, FUTURE-VISION.md, STRATEGY.md, USE-CASES.md) are exploratory/aspirational — not needed for day-to-day registry work.

## Multi-Repo Architecture

See [INFRASTRUCTURE.md](docs/reference/INFRASTRUCTURE.md) for details. This repo is the spec + registry only:

| Repo | Purpose |
|------|---------|
| **[SecID](https://github.com/CloudSecurityAlliance/SecID)** (this repo) | Specification, registry data, design documents, operations docs |
| **[SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service)** | Cloudflare Worker REST API + MCP server — live at [secid.cloudsecurityalliance.org](https://secid.cloudsecurityalliance.org/) |
| **[SecID-Server-API](https://github.com/CloudSecurityAlliance/SecID-Server-API)** | Self-hosted resolver — Python, TypeScript, Docker. Run your own SecID server. |
| **[SecID-Client-SDK](https://github.com/CloudSecurityAlliance/SecID-Client-SDK)** | Client libraries + AI instructions (Python, npm, Go, Rust, Java, C#) |
| **SecID-Website** | Cloudflare Pages documentation site (planned) |

## Repository Structure

```
secid/
├── SPEC.md, PRINCIPLES.md, ROADMAP.md, DECISIONS.md, AGENTS.md   # Top-level specs + ADR log
├── docs/                    # reference/, explanation/, guides/, future/, project/, operations/, parsers/ — see Document Map above
├── registry/                # Namespace definitions (one file per namespace)
│   ├── <type>.md            # Type description (e.g., advisory.md)
│   ├── <type>/_template.md  # Template for new namespace files
│   ├── <type>/<tld>/<domain>.md    # Namespace file (reverse-DNS, e.g., org/mitre.md)
│   ├── <type>/<tld>/<domain>.json  # JSON format (1,768 namespaces — 100% coverage)
│   └── _deferred/           # Partially researched entries not ready for main registry (e.g., cti/)
├── schemas/                 # OpenAPI spec + registry-namespace JSON Schema (JSON validation source of truth)
├── scripts/                 # Maintenance/research tooling (CNA pipeline, counts, scanners, stub generators)
├── seed/                    # Research scratchpad CSVs — pre-registry; promote into registry/ with provenance
├── plugins/secid/           # Local Claude Code plugin: MCP server.py + /resolve /lookup /describe commands
├── working-data/            # Out-of-band staging (CNA pages, known-broken overlay, audit artifacts)
├── slides/                  # Presentation assets (overview deck)
└── skills/                  # Top-level workflow skills (registry-research, -formalization, -validation, compliance-testing, secid-user)
```

## Registry File Format

**Dual format: YAML+Markdown (`.md`) is authoritative for contributions. JSON (`.json`) files exist alongside `.md` for all namespaces** and are the target format for v1.0+. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) for the JSON schema.

One file per namespace containing all sources from that organization. Use the appropriate template as a starting point for new files: `registry/advisory/_template.md`, `registry/capability/_template.md`, `registry/disclosure/_template.md`, or `registry/reference/_template.md`.

### Status Values

**Current YAML files** use: `active`, `draft`, `superseded`, `historical`

**Target JSON format** (v1.0+) uses: `proposed`, `draft`, `pending`, `published`

`published` means "reviewed", not "complete". Empty arrays and `null` values are valid—they show we looked and found nothing.

### Null vs Absent Convention

In registry data, `null` and absent mean different things:
- **`null`** = "we looked and found nothing" (researched, confirmed empty)
- **absent field** = "not yet researched" (unknown state)

Optional per-field metadata (`_checked`, `_updated`, `_note` suffixes) record *when* data was verified. A `null` with `_checked` tells you when the absence was confirmed. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) "Per-Field Metadata" for naming conventions and examples.

### Format Metadata

URL objects (both source-level `urls[]` and per-item match_node children) carry optional format metadata:

- **`parsability`**: `"structured"` (machine-readable) or `"scraped"` (HTML/unstructured)
- **`schema`**: SecID reference to the data schema (e.g., `secid:reference/cve.org/cve-schema@5.2.0`). Schemas are `reference` registry entries.
- **`parsing_instructions`**: SecID reference to a parsing instruction document (e.g., `secid:reference/cloudsecurityalliance.org/secid-parsers#cve-json-5`). Documents live in `docs/parsers/`.
- **`auth`**: Free text describing authentication requirements.

All four are optional. Absent means "not yet documented." See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) "Format Metadata" for full details.

## Key Design Principles

See [PRINCIPLES.md](PRINCIPLES.md) for the full treatment. The short version:

1. **Labeling and finding** - Identity, resolution, disambiguation only. Enrichment and relationships are separate layers.
2. **AI-first, human-legible** - Primary consumer is AI agents, but humans must be able to read and write everything.
3. **Helpful over correct** - Always return something useful. Never a bare error.
4. **Four response outcomes** - Every query returns one of: exact match, corrected match, related data, not found (with guidance).
5. **Honest uncertainty** - Say what you know, what you don't, and what the risks are.
6. **Follow the source** - Use names and ID structures the source uses. Preserve identifiers exactly.
7. **Never normalize lossily** - No lowercasing, no character stripping, no format mangling. Canonical form is the source's form.
8. **PURL compatibility** - Same grammar as Package URL, different scheme.
9. **Progressive resolution** - Try most specific match first, loosen progressively.
10. **Wildcard convention** - `/*` at any level for exploration and discovery.

## SecID Types

| Type | Identifies | Notable subtypes / overloads |
|------|------------|------------------------------|
| `advisory` | Publications about vulnerabilities (CVE, GHSA, vendor advisories) | Incident reports (AIID, NHTSA, FDA adverse events) — implicit, untagged today |
| `weakness` | Abstract flaw patterns (CWE, OWASP Top 10) | — |
| `ttp` | Adversary techniques (ATT&CK, ATLAS, CAPEC) | — |
| `control` | Security requirements (NIST CSF, ISO 27001, benchmarks) | Prescriptive benchmarks (HarmBench, WMDP), documentation standards (Model Cards) — implicit, untagged today |
| `capability` | Product security features with configuration, audit, and remediation (AWS S3 encryption, CloudTrail) | — |
| `methodology` | Formal processes for producing security analysis, scores, mappings, decisions (CVSS, SSVC, IR 8477, STRIDE) | — |
| `disclosure` | Vulnerability disclosure programs, policies, reporting channels | — |
| `regulation` | Laws and legal requirements (GDPR, HIPAA) | — |
| `entity` | Organizations, products, services | — |
| `reference` | Documents, research, identifier systems (arXiv, DOI, ISBN, RFCs) | `subtype: ["glossary"]` for glossary-shaped references with term-level subpaths (NIST CSRC, CSA, OWASP, ENISA) |

Types are intentionally overloaded — use the existing type plus a `subtype:` tag rather than splitting unless the four "When to Split" criteria are met. See [TYPES-AND-SUBTYPES.md](docs/reference/TYPES-AND-SUBTYPES.md) for the full subtype catalog, naming convention, and split-vs-subtype decision gate.

**WARNING: Adding a new type requires coordinated changes across multiple repos.** The type list is hardcoded in:
1. **This repo** — SPEC.md, CLAUDE.md, registry directory structure
2. **SecID-Service** — `src/types.ts` (`SECID_TYPES` array), `src/mcp.ts` (type descriptions), website/frontend
3. **SecID-Server-API** — `python/resolver.py` (`SECID_TYPES` list)
4. **SecID-Client-SDK** — type definitions in all language clients

The parser will **reject** queries for types not in the hardcoded list. The website will **not display** types it doesn't know about. CI/CD does **not** auto-detect new types from registry data. A new type is a spec-level change, not just a registry addition.

## Granularity

Use the hierarchy levels the source provides:

```
secid:control/cloudsecurityalliance.org/ccm@4.0           → Whole framework
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM       → Domain (group of controls)
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12    → Specific control
```

Document each level with its own pattern node and description.

## Namespace-to-Filesystem Algorithm

Given a namespace like `github.com/advisories` and type `advisory`:

1. Split namespace at first `/` → domain `github.com`, path `advisories`
2. Split domain on `.` → `github`, `com`
3. Reverse → `com/github`
4. Append path portion → `com/github/advisories`
5. Append `.md` → `com/github/advisories.md`
6. Prepend `registry/<type>/` → `registry/advisory/com/github/advisories.md`

Simple cases: `mitre.org` → `registry/<type>/org/mitre.md`, `nist.gov` → `registry/<type>/gov/nist.md`

## Adding New Namespaces

1. Determine type (advisory, weakness, ttp, control, capability, methodology, disclosure, regulation, entity, reference)
2. Compute the filesystem path using the algorithm above
3. Check if the file already exists — if so, add a source section to it
4. If new, copy from `registry/advisory/_template.md` and fill in fields
5. Include: urls, pattern tree nodes (match_nodes with descriptions), examples
6. Use `registry/_deferred/` for incomplete research

See [REGISTRY-GUIDE.md](docs/guides/REGISTRY-GUIDE.md) for detailed patterns.

## Pattern Tree (match_nodes)

The JSON format uses a nested `match_nodes` array (not flat `id_pattern` lists) to match subpath identifiers. Each node can have children for hierarchical ID systems:

```json
{
  "match_nodes": [
    {
      "patterns": ["(?i)^cve$"],
      "description": "Common Vulnerabilities and Exposures",
      "weight": 100,
      "data": {
        "examples": ["CVE-2024-1234", "CVE-2021-44228"]
      },
      "children": [
        {
          "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
          "description": "Standard CVE ID format",
          "weight": 100,
          "data": {
            "url": "https://www.cve.org/CVERecord?id={id}",
            "examples": [
              {"input": "CVE-2021-44228", "url": "https://www.cve.org/CVERecord?id=CVE-2021-44228"}
            ]
          }
        }
      ]
    }
  ]
}
```

Source-level `data.examples` uses bare strings (representative samples). Child-level `data.examples` uses structured ExampleObject entries (`{input, variables, url, note}`) that serve as test fixtures. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) for full schema.

See `registry/advisory/com/redhat.json` for a complex example with nested children (RHSA/RHBA/RHEA under errata), and `registry/advisory/org/debian.json` for range-table variable extraction.

## JSON Registry Files

All registry namespaces have been converted to JSON format. These `.json` files sit alongside their `.md` counterparts.

<!-- REGISTRY-COUNTS-START -->

| Type | Count |
|------|-------|
| Advisory | 56 |
| Weakness | 13 |
| Ttp | 4 |
| Control | 208 |
| Capability | 54 |
| Methodology | 23 |
| Disclosure | 486 |
| Regulation | 49 |
| Entity | 690 |
| Reference | 185 |
| **Total** | **1768** |

<!-- REGISTRY-COUNTS-END -->

Run `./scripts/update-counts.sh` to refresh these counts after adding namespaces.

**Key reference files for complex patterns:**
- `registry/advisory/org/mitre.json` — CVE (with cvelistV5 variable extraction)
- `registry/advisory/org/debian.json` — DSA/DLA (range-table year lookup)
- `registry/advisory/com/redhat.json` — Errata (RHSA/RHBA/RHEA), CVE, Bugzilla
- `registry/advisory/com/google.json` — OSV, Chrome, Android, GCP, Project Zero
- `registry/advisory/com/suse.json` — SUSE-SU (colon-in-ID variable extraction)
- `registry/weakness/org/owasp.json` — `version_required`, `version_disambiguation`, structured ExampleObject fixtures
- `registry/control/org/cloudsecurityalliance.json` — CCM, AICM (versioned controls), CCM-CAIQ, AICM-CAIQ (assessment questions, sub-numbered `XXX-NN.M` IDs), STAR (`type: registry` flag)
- `registry/reference/org/cloudsecurityalliance.json` — CSA website artifacts (1,131 publications with known_values lookup)
- `registry/control/org/iso.json` — 6 ISO standards
- `registry/ttp/org/mitre.json` — ATT&CK, ATLAS, CAPEC
- `registry/disclosure/org/cloudsecurityalliance.json` — Product security program (first disclosure entry)

Use `registry/CONVERSION-REVIEW-PROMPT.md` for AI-assisted review of YAML→JSON conversions.

## Entity Type

Entity files describe organizations and their products/services. **YAML `.md` files** use a `names` block; **JSON `.json` files** use `match_nodes` — the same tree structure as all other types. This means the resolver walks the same tree for entities as for advisories.

Entity match_nodes use literal patterns (`(?i)^openshift$`) since entity names are fixed strings. Products with variants become parent → children relationships (e.g., OpenShift → ROSA, ARO). Entity-specific `data` fields include `issues_type` and `issues_namespace` for cross-referencing.

See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) "Entity Type" section for the full schema and example.

**Many entity files are auto-generated stubs.** `scripts/generate-entity-stubs-from-disclosure.py` mines disclosure CNA data to bulk-create thin entity records as resolution anchors — they exist so cross-references (e.g., `issues_namespace` pointers from disclosure entries) resolve. PR #83 created 475 such stubs in one pass. Hand-curated entries can replace stubs and add detail; treat a thin entity file as "stub, expand when needed," not "complete."

## Cross-Type Documentation

Some sources appear in multiple types. For example, a security tool might be both an `entity` (the product) and a `control` (its capabilities). A weakness taxonomy like OWASP AI Exchange defines both `weakness` entries and `control` entries. Each type gets its own registry file — see `registry/README.md` for the dual-documentation pattern.

### Common pattern: standards-publishing organizations

An organization that publishes controls almost always belongs in `entity/` *and* `control/` simultaneously. They have separate roles:

| Type file | Represents | Used for |
|---|---|---|
| `registry/entity/<path>.json` | The organization itself (identity, website, brief description) | Citing the org as a stable anchor; "what is UIDAI?", "who publishes ISO 27001?" |
| `registry/control/<path>.json` | The controls/standards/programs they publish | Citing specific standards; `secid:control/iso.org/27001@2022#A.5.1` |
| `registry/regulation/<publisher-path>.json` | Laws authorizing or shaping their work | Citing specific laws; `secid:regulation/in/gov/meity#aadhaar-act-2016` |

The regulation file lives under the **actual legal publisher's** namespace (Parliament of India for Aadhaar Act, European Commission for PSD2, US Congress for HIPAA) — not under the operating-org's namespace. Cross-references between the three layers will be expressed via the future Relationships layer (SPEC §6); today they're documented in `notes:` field text.

### Worked example: Aadhaar / India Stack

| SecID | File | Description |
|---|---|---|
| `secid:regulation/in/gov/meity#aadhaar-act-2016` | `registry/regulation/in/gov/meity.json` | Aadhaar Act 2016 — the enabling legislation |
| `secid:entity/in/gov/uidai` | `registry/entity/in/gov/uidai.json` | UIDAI — the statutory authority |
| `secid:control/in/gov/uidai/auth-api` | `registry/control/in/gov/uidai.json` | Aadhaar Authentication API spec |

Same `uidai.gov.in` namespace; two type-specific files (entity + control). Plus the regulation under the Indian government's `meity.gov.in` legal-publisher namespace.

### EU directive transposition

EU directives (PSD2, NIS2, eIDAS amendments) get a record under `regulation/eu/europa.json` *and* a per-member-state record under that country's legal publisher (`regulation/de/gesetze-im-internet.json`, `regulation/fr/gov/legifrance.json`, etc.). Each national transposition record notes the parent EU directive's SecID in its `notes:` field. Cross-references will move to structured fields once the Relationships layer ships.

## Claude Code Skills

The `skills/` directory contains workflow skills for common registry tasks. Use the appropriate skill for the task at hand:

| Skill | Status | When to Use |
|-------|--------|-------------|
| `registry-research` | Stub | Researching a new source and creating a `.md` registry entry |
| `registry-formalization` | Stub | Converting `.md` to production `.json` format |
| `registry-validation` | **Active (v0.1)** | Validating `.json` and `.md` files for structural/safety/consistency errors |
| `compliance-testing` | Stub | Testing a resolver implementation against the canonical test suite |
| `secid-user` | Stub | End-user SecID lookups and referencing |

**Typical new-namespace workflow:** research → formalize → validate. Only `registry-validation` is currently built; the others have documentation but no implementation yet.

## Local Claude Code Plugin (`plugins/secid/`)

This repo ships its own Claude Code plugin alongside the spec. Installing it gives Claude direct access to the live resolver without leaving the repo:

- **`server.py`** — local MCP server bridging to the live resolver at secid.cloudsecurityalliance.org
- **`commands/`** — `/resolve`, `/lookup`, `/describe` slash commands (each maps to one resolver tool)
- **`agents/`**, **`skills/`** — plugin-scoped agents and skills (separate from the top-level `skills/` workflow toolkit)
- **`plugin.json`** — manifest

When working in this repo, prefer the MCP resolver tools (`mcp__plugin_secid_secid__resolve`, `__lookup`, `__describe` — or the `mcp__claude_ai_SecID__*` equivalents when connected via the hosted server) over manually grepping `registry/**/*.json`. They return canonical resolution output and are the same answer a user-facing client would see. Fall back to filesystem reads only when (a) the resolver is unreachable, (b) you need to inspect or modify registry data, or (c) you're debugging a deploy-chain issue where live and local may legitimately disagree.

## Development Commands

```bash
# Check registry files have required metadata
rg -n '^type:' registry/**/*.md

# List all namespaces and their types
rg -n '^namespace:' registry/**/*.md

# Find all files for a specific namespace (e.g., mitre.org appears in multiple types)
rg -l 'namespace: mitre.org' registry/

# Count registry files per type
for type in advisory weakness ttp control capability methodology disclosure regulation entity reference; do echo "$type: $(find registry/$type -name '*.md' -not -name '_*' 2>/dev/null | wc -l)"; done

# Validate all JSON registry files parse correctly
for f in registry/**/*.json; do python3 -c "import json; json.load(open('$f'))" && echo "OK: $f" || echo "FAIL: $f"; done

# List JSON files with structured examples
python3 -c "import json,glob; [print(f) for f in sorted(glob.glob('registry/**/*.json',recursive=True)) if any(isinstance(e,dict) for n in json.load(open(f)).get('match_nodes',[]) for c in n.get('children',[]) for e in c.get('data',{}).get('examples',[]))]"

# Update namespace counts in CLAUDE.md and README.md
./scripts/update-counts.sh

# Lint markdown (if markdownlint is installed)
markdownlint **/*.md
```

### Scripts

```bash
# Update namespace counts in CLAUDE.md and README.md (run after adding namespaces)
./scripts/update-counts.sh

# CNA disclosure pipeline (generates disclosure registry entries from CVE CNA partner data)
./scripts/fetch-cna-pages.sh              # Download CNA partner HTML pages
node scripts/fetch-cna-details.js         # Extract structured details (or use .py variant)
python3 scripts/generate-cna-disclosure.py # Generate disclosure/*.json files
python3 scripts/enrich-cna-from-cnalist.py # Add cna_id and disclosure_policy from CNAsList.json
python3 scripts/apply-known-broken.py     # Apply known-broken validation overlay (URLs/emails verified broken)
python3 scripts/audit-known-broken.py     # Audit overlay against fresh CNAsList.json (report-only; classifies entries into 4 buckets)

# Entity stub generation (mines disclosure CNA data to bulk-create thin entity records)
python3 scripts/generate-entity-stubs-from-disclosure.py

# Domain-scanning / annotation utilities
python3 scripts/check-security-txt.py     # Fetch security.txt across disclosure namespace domains; annotate registry
python3 scripts/scan-well-known.py        # Scan entity domains for well-known files (llms.txt, robots.txt, security.txt)
python3 scripts/scan-mcp-endpoints.py     # Detect MCP endpoints + API/MCP mentions in entity domains' llms.txt

# Subtype validation against SecID-Service's type-registry.ts (CI check)
python3 scripts/validate-subtypes.py
```

The `apply-known-broken.py` step reads [`working-data/cna/known-broken.json`](working-data/cna/known-broken.json) — a v2.0 schema, AI-consumable, JSON-Patch-like validation overlay. Each entry asserts "at this JMESPath `field_path` in upstream `CNAsList.json`, the `current_value` is broken — here is the `failure`, the `evidence`, and the `upstream_issue` tracking the fix." Matching URL/email values in the disclosure entries are annotated with `_broken: true` plus per-entry metadata (`_broken_verified`, `_broken_failure`, `_broken_note`, `_broken_source`). URL entries carry `_broken_source: CVEProject/cve-website#3937`; email entries carry `_broken_source: CVEProject/cve-website#3938`. Idempotent: removing an entry from the overlay and re-running the script strips the corresponding `_broken_*` fields automatically.

The companion `scripts/audit-known-broken.py` fetches the current upstream `CNAsList.json` (or uses `--cnas-list PATH` for offline runs) and classifies each overlay entry into four buckets: **still_present** (upstream still holds the broken value at the named `field_path`), **replaced** (`field_path` now resolves to a different value — manual re-validation needed), **disappeared** (`field_path` no longer resolves — orphan, candidate for removal), and **partial** (entry has multiple `field_paths` with mixed buckets). Entries whose `evidence.last_verified` is older than `--stale-days` (default 90) get a stale flag orthogonally. The audit reports only — it does not auto-reprobe URLs/emails. Exit code: 0 if every entry is still_present-and-not-stale; 1 otherwise. Supports `--json` for machine-readable output.

This is a **specification-only repository** — no build system, no tests, no compiled code. Validation is manual review + grep/ripgrep over YAML frontmatter and JSON parsing.

## CI/CD

**JSON registry changes merged to main are automatically deployed to the live resolver at secid.cloudsecurityalliance.org.** Broken patterns or invalid JSON will break live resolution — validate before merging.

**Deploy chain:**

1. Push to `main` touching `registry/**/*.json` triggers `.github/workflows/update-registry.yml` (also has `workflow_dispatch:` for manual testing)
2. That workflow uses the `SECID_TO_SERVICE_DISPATCH` PAT (fine-grained, scoped to SecID-Service only) to send a `repository_dispatch` event
3. SecID-Service receives the dispatch and runs its "Upload registry to KV" workflow, which:
   - Builds and tests
   - Runs `scripts/upload-registry-kv.ts --sync` using the `SECID_SERVICE_DEPLOY` Cloudflare token
   - Uploads all expected keys (overwrites) AND deletes orphans (KV keys no longer produced by registry)
   - Deploys the Worker
4. Live resolver serves from `secid_REGISTRY` KV; chain completes in ~1m20s

**Sync semantics:** `--sync` mode means KV exactly matches what the registry produces. Modifying a namespace overwrites its value; deleting a namespace deletes its key; renaming creates new + orphans old (both handled). Source-level changes within a namespace are content-only updates (the namespace key still exists, value gets the new sources array). A 50-key safety threshold blocks accidental mass-delete.

**For manual operations:**

- Test the auto-trigger chain: `gh workflow run "Notify registry update" -R CloudSecurityAlliance/SecID`
- Force a fresh KV sync: `gh workflow run "Upload registry to KV" -R CloudSecurityAlliance/SecID-Service`
- Local audit (no mutations): `npx tsx scripts/upload-registry-kv.ts --sync --dry-run /path/to/SecID` from the SecID-Service repo with `CLOUDFLARE_API_TOKEN` env var set

**Checking deploy-chain health** (do this when a registry change doesn't seem to be reaching the live resolver):

```bash
# Should show recent successful runs of "Notify registry update"
gh run list -R CloudSecurityAlliance/SecID -L 5

# Should show recent successful runs of "Upload registry to KV" triggered as "registry-updated"
gh run list -R CloudSecurityAlliance/SecID-Service -L 5

# End-to-end check via live resolver (replace with any recently-merged namespace):
curl -s https://secid.cloudsecurityalliance.org/api/v1/resolve/secid:control/iso.org/27017 | head
```

Failure modes seen historically (none active as of the last verification):
- `SECID_TO_SERVICE_DISPATCH` PAT unauthorized — auto-trigger workflow on SecID side fails on the dispatch step
- `cve-schema` test failures in SecID-Service — manual `Upload registry to KV` runs fail in the test stage
- `CLOUDFLARE_API_TOKEN` expired/scoped wrong — upload step fails

If health-check commands show failures, inspect the failing run's logs and check token validity first.

## Commit and PR Style

Use short, imperative commit subjects (e.g., "Add EUVD advisory namespace", "Update Red Hat errata patterns"). One logical change per commit. For PRs that modify regex patterns, include a note about regex safety (anchored, no catastrophic backtracking).

## Parsing, Encoding, Preservation (load-bearing rules)

See [SPEC.md](SPEC.md) §4 (grammar), §7 (parsing), §8 (encoding) for the authoritative treatment. The rules below are the ones future Claude instances most commonly get wrong:

- **Parsing requires registry access.** `name` and `subpath` can contain `#`, `@`, `?`, `:` — the registry lookup determines where each component ends. Don't pre-tokenize on punctuation.
- **Namespace matching is shortest-to-longest.** For `github.com/advisories/ghsa`, the parser tries `github.com` first, then `github.com/advisories`. Longest match wins.
- **Subpaths preserve the source's exact format.** Keep colons, dots, dashes as the source writes them: `RHSA-2026:0932` (not `RHSA-2026-0932`), `T1059.003` (not `T1059-003`), `PR.AC-1` unchanged. Never lossy-normalize — that's principle #7 in [PRINCIPLES.md](PRINCIPLES.md).
- **No encoding inside the SecID string itself.** Write `A&A-01` naturally. Percent-encoding (`&`→`%26`, space→`%20`, `:`→`%3A`, `/`→`%2F`, `#`→`%23`) only applies when SecIDs are stored as filenames or carried in URL paths. Resolvers try the input as-is first, then percent-decoded.
- **Version resolution behaves differently when `version_required: true`.** Omitting `@version` against a version-required source returns all matching versions with disambiguation guidance, not a single result. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) "Version Resolution Fields".

## Writing Principle

Explain **why**, not just what. "SecID uses `#subpath` because security knowledge is databases of identifiers, not packages with files" is better than just "SecID uses `#subpath` for specific items."
