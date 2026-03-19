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

## Current Status: v0.9 (Public Draft)

Working toward v1.0: Given a SecID string, return the URL(s) where that resource can be found.

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
| Why was X designed this way? | [DESIGN-DECISIONS.md](docs/explanation/DESIGN-DECISIONS.md) |
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

Documents in [docs/future/](docs/future/) (RELATIONSHIPS.md, OVERLAYS.md, FUTURE-VISION.md, STRATEGY.md, USE-CASES.md) are exploratory/aspirational — not needed for day-to-day registry work.

## Multi-Repo Architecture

See [INFRASTRUCTURE.md](docs/reference/INFRASTRUCTURE.md) for details. This repo is the spec + registry only:

| Repo | Purpose |
|------|---------|
| **SecID** (this repo) | Specification, registry data, design documents, operations docs |
| **SecID-Service** | Cloudflare Worker REST API + MCP server |
| **SecID-Website** | Cloudflare Pages documentation site |
| **SecID-Client-SDK** | Client libraries + AI instructions (Python, npm, Go, Rust, Java, C#) |

## Repository Structure

```
secid/
├── SPEC.md                  # Full technical specification
├── PRINCIPLES.md            # Foundational design principles
├── ROADMAP.md               # Project status and phases
├── docs/
│   ├── reference/           # Authoritative technical specs
│   │   ├── REGISTRY-FORMAT.md           # Current YAML+Markdown format
│   │   ├── REGISTRY-JSON-FORMAT.md      # Target JSON schema (v1.0+)
│   │   ├── VERSIONING.md               # Version analysis and API behavior
│   │   ├── EDGE-CASES.md               # Domain-name edge cases
│   │   ├── INFRASTRUCTURE.md           # Multi-repo architecture
│   │   └── NAMESPACE-MAPPING.md        # Namespace-to-filesystem mapping
│   ├── explanation/         # Why decisions were made
│   │   ├── RATIONALE.md                # Why SecID exists
│   │   └── DESIGN-DECISIONS.md         # Key design decisions
│   ├── guides/              # Task-oriented step-by-step how-tos
│   │   ├── REGISTRY-GUIDE.md           # Principles and patterns for contributions
│   │   ├── ADD-NAMESPACE.md            # How to add a new namespace
│   │   ├── UPDATE-NAMESPACE.md         # How to update an existing namespace
│   │   ├── YAML-TO-JSON.md             # How to convert YAML to JSON
│   │   └── REGEX-WORKFLOW.md           # How to write and test regex patterns
│   ├── future/              # Aspirational, explicitly not commitments
│   │   ├── FUTURE-VISION.md, STRATEGY.md, USE-CASES.md
│   │   ├── RELATIONSHIPS.md, OVERLAYS.md
│   ├── project/             # Internal tracking and organizational docs
│   │   ├── TODO.md, GAPS.md, CONCERNS.md
│   │   └── csa/             # CSA-internal documents
│   └── operations/          # Infrastructure, DNS, deployment, CI/CD
├── registry/                # Namespace definitions (one file per namespace)
│   ├── <type>.md            # Type description (e.g., advisory.md)
│   ├── <type>/_template.md  # Template for new namespace files
│   ├── <type>/<tld>/<domain>.md    # Namespace file (reverse-DNS, e.g., org/mitre.md)
│   ├── <type>/<tld>/<domain>.json  # JSON format (124 namespaces — 100% coverage)
│   └── _deferred/           # Partially researched entries not ready for main registry
├── seed/                    # Research scratchpad CSVs — promote to registry/ with provenance
└── skills/                  # Claude Code skills (registry-research, registry-formalization, compliance-testing, secid-user)
```

## Registry File Format

**Dual format: YAML+Markdown (`.md`) is authoritative for contributions. JSON (`.json`) files exist alongside `.md` for all 124 namespaces** and are the target format for v1.0+. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) for the JSON schema.

One file per namespace containing all sources from that organization. Use `registry/advisory/_template.md`, `registry/disclosure/_template.md`, or `registry/reference/_template.md` as a starting point for new files.

### Status Values

**Current YAML files** use: `active`, `draft`, `superseded`, `historical`

**Target JSON format** (v1.0+) uses: `proposed`, `draft`, `pending`, `published`

`published` means "reviewed", not "complete". Empty arrays and `null` values are valid—they show we looked and found nothing.

### Null vs Absent Convention

In registry data, `null` and absent mean different things:
- **`null`** = "we looked and found nothing" (researched, confirmed empty)
- **absent field** = "not yet researched" (unknown state)

Optional per-field metadata (`_checked`, `_updated`, `_note` suffixes) record *when* data was verified. A `null` with `_checked` tells you when the absence was confirmed. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) "Per-Field Metadata" for naming conventions and examples.

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

| Type | Identifies |
|------|------------|
| `advisory` | Publications about vulnerabilities (CVE, GHSA, vendor advisories, incident reports) |
| `weakness` | Abstract flaw patterns (CWE, OWASP Top 10) |
| `ttp` | Adversary techniques (ATT&CK, ATLAS, CAPEC) |
| `control` | Security requirements (NIST CSF, ISO 27001, benchmarks) |
| `disclosure` | Vulnerability disclosure programs, policies, reporting channels |
| `regulation` | Laws and legal requirements (GDPR, HIPAA) |
| `entity` | Organizations, products, services |
| `reference` | Documents, research, identifier systems (arXiv, DOI, ISBN, RFCs) |

Types are intentionally overloaded. Split only when usage proves it necessary.

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

1. Determine type (advisory, weakness, ttp, control, disclosure, regulation, entity, reference)
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

All 121 registry namespaces have been converted to JSON format. These `.json` files sit alongside their `.md` counterparts:

| Type | Count |
|------|-------|
| Advisory | 42 |
| Weakness | 13 |
| TTP | 4 |
| Control | 24 |
| Regulation | 4 |
| Reference | 22 |
| Entity | 14 |

**Key reference files for complex patterns:**
- `registry/advisory/org/mitre.json` — CVE (with cvelistV5 variable extraction)
- `registry/advisory/org/debian.json` — DSA/DLA (range-table year lookup)
- `registry/advisory/com/redhat.json` — Errata (RHSA/RHBA/RHEA), CVE, Bugzilla
- `registry/advisory/com/google.json` — OSV, Chrome, Android, GCP, Project Zero
- `registry/advisory/com/suse.json` — SUSE-SU (colon-in-ID variable extraction)
- `registry/weakness/org/owasp.json` — `version_required`, `version_disambiguation`, structured ExampleObject fixtures
- `registry/control/org/cloudsecurityalliance.json` — CCM, AICM (versioned controls)
- `registry/reference/org/cloudsecurityalliance.json` — CSA website artifacts (1,131 publications with known_values lookup)
- `registry/control/org/iso.json` — 6 ISO standards
- `registry/ttp/org/mitre.json` — ATT&CK, ATLAS, CAPEC

Use `registry/CONVERSION-REVIEW-PROMPT.md` for AI-assisted review of YAML→JSON conversions.

## Entity Type

Entity files describe organizations and their products/services. **YAML `.md` files** use a `names` block; **JSON `.json` files** use `match_nodes` — the same tree structure as all other types. This means the resolver walks the same tree for entities as for advisories.

Entity match_nodes use literal patterns (`(?i)^openshift$`) since entity names are fixed strings. Products with variants become parent → children relationships (e.g., OpenShift → ROSA, ARO). Entity-specific `data` fields include `issues_type` and `issues_namespace` for cross-referencing.

See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) "Entity Type" section for the full schema and example.

## Cross-Type Documentation

Some sources appear in multiple types. For example, a security tool might be both an `entity` (the product) and a `control` (its capabilities). A weakness taxonomy like OWASP AI Exchange defines both `weakness` entries and `control` entries. Each type gets its own registry file — see `registry/README.md` for the dual-documentation pattern.

## Development Commands

```bash
# Check registry files have required metadata
rg -n '^type:' registry/**/*.md

# List all namespaces and their types
rg -n '^namespace:' registry/**/*.md

# Find all files for a specific namespace (e.g., mitre.org appears in multiple types)
rg -l 'namespace: mitre.org' registry/

# Count registry files per type
for type in advisory weakness ttp control disclosure regulation entity reference; do echo "$type: $(find registry/$type -name '*.md' -not -name '_*' 2>/dev/null | wc -l)"; done

# Validate all JSON registry files parse correctly
for f in registry/**/*.json; do python3 -c "import json; json.load(open('$f'))" && echo "OK: $f" || echo "FAIL: $f"; done

# List JSON files with structured examples
python3 -c "import json,glob; [print(f) for f in sorted(glob.glob('registry/**/*.json',recursive=True)) if any(isinstance(e,dict) for n in json.load(open(f)).get('match_nodes',[]) for c in n.get('children',[]) for e in c.get('data',{}).get('examples',[]))]"

# Lint markdown (if markdownlint is installed)
markdownlint **/*.md
```

This is a **specification-only repository** — no build system, no tests, no compiled code. Validation is manual review + grep/ripgrep over YAML frontmatter and JSON parsing.

## Parsing Rules

**SecID parsing requires registry access.** The registry defines what's valid - no banned character list to memorize.

**Namespaces are domain names**, optionally with `/`-separated path segments for platform sub-namespaces.

| Component | Character Rules |
|-----------|-----------------|
| `type` | Fixed list of 8 values |
| `namespace` | Domain name, optionally with `/`-separated sub-namespace path segments. Per-segment: `a-z`, `0-9`, `-`, `.`, Unicode `\p{L}\p{N}`. |
| `name` | **Anything** - resolved by registry lookup, longest match wins |
| `subpath` | Anything (everything after `#`). May include `@item_version` suffix — parsed via pattern tree matching. |

**Per-segment validation regex:** `^[\p{L}\p{N}]([\p{L}\p{N}._-]*[\p{L}\p{N}])?$` (applies to each segment between `/`)

**Namespace resolution: shortest-to-longest matching.** Since namespaces can contain `/`, the parser tries shortest namespace first against the registry, then progressively longer matches. Example: for `github.com/advisories/ghsa`, try `github.com` then `github.com/advisories` — longest match wins.

**Why domain-name namespaces?**
- **Self-registration (future)** - Domain owners will prove ownership via DNS/ACME; currently manual via pull requests
- **No naming authority** - DNS already provides globally unique names
- **Filesystem safety** - Namespaces become file paths (`registry/advisory/org/mitre.md`)
- **Unicode for internationalization** - Native language domain names supported

**Why registry-required?** Names can contain `#`, `@`, `?`, `:` - the registry lookup determines where name ends.

**Version resolution:** Sources with `version_required: true` behave differently when `@version` is omitted — the resolver returns all matching versions with disambiguation guidance instead of a single result. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) "Version Resolution Fields".

## Preserve Source Identifiers

**Subpaths preserve the source's exact format - including special characters.**

| Source Format | SecID | NOT This |
|---------------|-------|----------|
| `RHSA-2026:0932` (colon) | `#RHSA-2026:0932` ✓ | `#RHSA-2026-0932` ✗ |
| `T1059.003` (dot) | `#T1059.003` ✓ | `#T1059-003` ✗ |
| `PR.AC-1` (dot+dash) | `#PR.AC-1` ✓ | Unchanged |

**Why:** Human recognition, copy-paste workflow, no information loss. What practitioners know is what SecID uses.

## Encoding Rules

**In the SecID string:** No encoding needed. Write identifiers naturally: `RHSA-2024:1234`, `A&A-01`.

**For storage/transport (filenames, URLs):** Percent-encode special characters:
- `&` → `%26`, Space → `%20`, `:` → `%3A`, `/` → `%2F`, `#` → `%23`

**Flexible input resolution:** Resolvers try input as-is first, then percent-decoded. Registry patterns match human-readable (unencoded) form. Backend storage format is an implementation choice. Do NOT strip quotes or other characters from input - the registry determines what matches.

## Writing Principle

Explain **why**, not just what. "SecID uses `#subpath` because security knowledge is databases of identifiers, not packages with files" is better than just "SecID uses `#subpath` for specific items."
