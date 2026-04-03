<p align="center">
  <img src="csa-logo.jpeg" alt="Cloud Security Alliance" width="200">
</p>

# SecID - Security Identifiers

**SecID provides a grammar and registry for referencing security knowledge. SecID does not assign identifiers—those come from their respective authorities.**

**Live service: [secid.cloudsecurityalliance.org](https://secid.cloudsecurityalliance.org/)**

## SecID MCP Server

Add SecID to your AI assistant as a remote MCP server:

```
https://secid.cloudsecurityalliance.org/mcp
```

That's it. No API keys, no local install, no configuration. Works with Claude Desktop, Claude Code, Cursor, Windsurf, and any MCP client that supports remote servers. Your AI assistant gets three tools (`resolve`, `lookup`, `describe`) and can immediately look up CVEs, CWEs, ATT&CK techniques, NIST controls, and 130+ other security knowledge sources.

## What SecID Does

`secid:advisory/mitre.org/cve#CVE-2024-1234` refers to a CVE record published by MITRE. SecID doesn't create CVEs, assign CWE numbers, or issue ATT&CK technique IDs—it provides a consistent way to reference them all.

## The Problem: Some Things Are Easy to Reference, Others Aren't

Everyone knows how to reference `CVE-2024-1234`. But what about:

| What you want to reference | Without SecID | With SecID |
|---------------------------|---------------|------------|
| A CVE record (MITRE) | `CVE-2025-10725` (easy, well-known) | `secid:advisory/mitre.org/cve#CVE-2025-10725` |
| Red Hat's page for that CVE | "Red Hat's CVE page for CVE-2025-10725" or a URL | `secid:advisory/redhat.com/cve#CVE-2025-10725` |
| That CVE within a specific RHSA | "CVE-2025-10725 as addressed in RHSA-2025:16981" | `secid:advisory/redhat.com/rhsa#RHSA-2025:16981/CVE-2025-10725` |
| A specific ISO 27001 control | "Control A.5.1 in ISO 27001:2022" (no URL exists) | `secid:control/iso.org/27001@2022#A.5.1` |
| An ATT&CK technique | `T1059.003` (different format, different system) | `secid:ttp/mitre.org/attack#T1059.003` |
| A CWE weakness | `CWE-79` (easy) | `secid:weakness/mitre.org/cwe#CWE-79` |

The Red Hat examples show a key pattern: **the same CVE can be referenced in multiple contexts**, and each context has different data. MITRE's CVE record has MITRE's severity rating; Red Hat's CVE page has Red Hat's severity rating (which may differ based on their analysis); and the RHSA tells you which packages fix it. These are all valuable, distinct pieces of information about the same underlying vulnerability.

**SecID helps at both ends of the popularity spectrum:**

- **Popular things** (like CVEs) exist in many places—MITRE, NVD, Red Hat, Ubuntu, GitHub, vendor advisories. SecID lets you reference exactly which source you mean.
- **Obscure things** (like a specific ISO control or a niche framework) become findable. Without SecID, you need a sentence of prose or a URL (if one even exists). With SecID, `secid:control/iso.org/27001@2022#A.5.1` is as easy to reference as a CVE.

## Why Fragmentation Exists (And Why It's Not Going Away)

Security knowledge is fragmented across dozens of databases, each with its own identifier format, API, and data model. **This fragmentation exists for legitimate reasons.** Each database serves a different mission: CVE tracks vulnerabilities, CWE catalogs weakness patterns, ATT&CK documents adversary behavior, NIST provides compliance controls. Different organizations built these systems at different times, with different governance structures, legal constraints, and funding models.

**SecID doesn't try to unify or replace these systems.** They will continue to exist, evolve independently, and serve their communities. SecID provides a coordination layer—a consistent way to reference any of them, alongside each other, in the same format.

## Relationship to Existing Standards

**SecID does not replace CVE, CWE, ATT&CK, NIST, ISO, or any other authority.** These organizations remain the authoritative sources for vulnerability data, weakness taxonomies, attack techniques, and security controls within their respective domains.

SecID is a **cross-reference and resolution convention**:

| What SecID Does | What SecID Does NOT Do |
|-----------------|------------------------|
| Provides a grammar and registry for referencing security knowledge | Assign identifiers (CVE-2024-1234 comes from MITRE, not SecID) |
| Tells you where to find the authoritative source | Decide what is a "valid" vulnerability or weakness |
| Enables cross-references between different systems | Adjudicate disputes between sources |
| Gives AI and tools a consistent navigation format | Replace the governance of existing programs |

When you write `secid:advisory/mitre.org/cve#CVE-2024-1234`, you're saying "the CVE record identified as CVE-2024-1234, as published by MITRE's CVE program." The authority remains with MITRE. SecID just gives you a consistent way to reference it alongside CWEs, ATT&CK techniques, and controls.

**Authority boundaries are explicit.** If MITRE says something is a CVE, it's a CVE. If NIST publishes a CVSS score in NVD, that's NIST's assessment. SecID doesn't resolve disagreements - it makes them navigable. Different sources can have different perspectives on the same vulnerability; that's not a bug, it's reality.

## What Is SecID?

SecID is a **meta-identifier system**—it identifies things that already have identifiers (or should).

[Package URL (PURL)](https://github.com/package-url/purl-spec) provides `pkg:type/namespace/name` for identifying software packages. In security, we need to identify many different things: advisories, weaknesses, attack techniques, controls, regulations, entities, and reference documents. These live in different databases, with different formats, maintained by different organizations.

**SecID uses PURL grammar with `secid:` as the scheme.** Just as PURL uses `pkg:` as its scheme, SecID uses `secid:`. Everything after `secid:` follows PURL grammar exactly: `type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]`.

**What SecID does:**
- Gives you a consistent way to reference CVE-2024-1234, CWE-79, T1059.003, and ISO 27001 A.5.1 in the same format
- Tells you where to find things (URL resolution)
- Works for things that don't have URLs (paywalled standards, specific controls within frameworks)

**What SecID doesn't do:**
- Assign identifiers (those come from their respective authorities)
- Replace CVE, CWE, ATT&CK, or any other database
- Claim authority over vulnerability data
- Store the actual content (it points to it)

**If you need an identifier assigned:** SecID can't help with that directly. Get a CVE from MITRE, a GHSA from GitHub, or publish through AVID for AI vulnerabilities. Once your advisory has an identifier from an authority, SecID provides a consistent way to reference it.

SecID is **explicitly scoped to identifiers only**. On its own, a naming system is useful but limited. The real value comes from what you build on top: relationship graphs, enrichment layers, tooling, and integrations. SecID is foundational infrastructure.

## PURL to SecID Mapping

SecID is PURL with a different scheme. The grammar is identical:

```
PURL:   pkg:type/namespace/name@version?qualifiers#subpath
SecID:  secid:type/namespace/name@version?qualifiers#subpath[@item_version][?qualifiers]
```

**How each component maps:**

| PURL Component | SecID Component | SecID Usage |
|----------------|-----------------|-------------|
| `pkg:` | `secid:` | Scheme (constant prefix) |
| `type` | `type` | Security domain: `advisory`, `weakness`, `ttp`, `control`, `disclosure`, `regulation`, `entity`, `reference` |
| `namespace` | `namespace` | **Domain name**, or **domain name with path**, of the organization that publishes/maintains. Examples: `redhat.com`, `cloudsecurityalliance.org`, `github.com/advisories`, `github.com/ModelContextProtocol-Security/vulnerability-db`. |
| `name` | `name` | **Database/framework/standard** they publish (e.g., `cve`, `nvd`, `cwe`, `attack`, `27001`) |
| `@version` | `@version` | Edition or revision (e.g., `@4.0`, `@2022`, `@2.0`) |
| `?qualifiers` | `?qualifiers` | Optional context (e.g., `?lang=ja`). Can appear on name (source-level) and/or subpath (item-level). |
| `#subpath` | `#subpath` | **Specific item** within the database (e.g., `#CVE-2024-1234`, `#CWE-79`, `#T1059`, `#A.8.1`) |
| — | `@item_version` | **Version of the specific item** (e.g., `@a1b2c3d` for a git commit). SecID extension. |

**Visual mapping:**

```
secid:advisory/mitre.org/cve#CVE-2024-1234
       ───┬─── ──┬── ─┬─ ──────┬──────
          │      │    │        └─ subpath: specific CVE identifier
          │      │    └────────── name: the CVE database
          │      └─────────────── namespace: MITRE (the organization)
          └────────────────────── type: advisory

secid:control/iso.org/27001@2022#A.8.1
       ──┬─── ─┬─ ──┬── ─┬── ──┬──
         │     │    │    │     └─ subpath: specific control (Annex A.8.1)
         │     │    │    └─────── version: 2022 edition
         │     │    └──────────── name: ISO 27001 standard
         │     └───────────────── namespace: ISO (the organization)
         └─────────────────────── type: control
```

**Key insight:** The namespace is always the **organization** (who publishes it), the name is the **thing they publish** (database, framework, standard), and the subpath is the **specific item within** that thing.

### Parsing and Character Rules

**SecID parsing requires the registry — the spec is a guide for building parsers, not a standalone regex.** Rather than memorizing a list of banned characters, the registry defines what's valid. If a type, namespace, or name isn't in the registry, it's not a valid SecID. This keeps parsing simple and the registry authoritative.

Every ambiguity in a SecID string is resolved by registry data:
- **Namespace boundary:** shortest-to-longest matching against registry files
- **Name boundary:** longest match against source names in the registry
- **Item version boundary:** the `id_pattern` regex for each source defines where the item identifier ends. An `@` after the matched pattern is unambiguously a version delimiter. If a source's IDs contain `@`, their pattern includes it. This is why the spec teaches you how to build a parser, not a standalone regex.

**Even unknown SecIDs are solvable.** Because every SecID contains a domain name, encountering `secid:advisory/newvendor.com/alerts#NVA-2026-0042` with no registry match isn't a dead end — you can visit `newvendor.com`, find their advisory system, and contribute a registry entry. The goal is comprehensive registry coverage through a hosted service, easy contribution (one file per namespace), and federation (organizations can run their own registries). Unknown SecIDs are a temporary state, not a permanent gap.

**The domain-name namespace model:** Namespaces are domain names. We need one stable delimiter to separate namespace from name. Since we assign namespaces, we simply don't assign any with `/` (e.g., use `ac-dc` not `ac/dc`).

**Names can contain any characters** (including `#`, `@`, `?`, `:`). The registry lookup determines where the name ends - longest match wins. This keeps identifiers human-friendly and preserves upstream naming exactly.

**Subpath hierarchy:** Subpaths can use `/` to express hierarchy within a document:

```
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12                        # The control
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/audit                  # Audit section within control
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/implementation         # Implementation guidance
secid:regulation/europa.eu/gdpr#art-32/1/a                     # Article 32(1)(a)
secid:weakness/mitre.org/cwe#CWE-79/potential-mitigations   # Mitigations section
```

**Encoding:** The SecID string is human-readable - no percent-encoding required:

```
secid:control/cloudsecurityalliance.org/aicm@1.0#A&A-01                       # A&A-01 control (no encoding)
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/Auditing Guidelines    # Section with space (no encoding)
secid:advisory/redhat.com/errata#RHSA-2024:1234             # Colon in ID (no encoding)
```

**When to encode:** Only when storing SecIDs in contexts with their own syntax:
- As filenames: `secid%3Aadvisory%2Fmitre%2Fcve%23CVE-2024-1234`
- In URL query strings: `?secid=secid%3Aadvisory%2F...`

See [SPEC.md Section 8.2](SPEC.md#82-percent-encoding) for encoding rules when storing/transporting.

## Relationship to PURL

**SecID is 95% identical to PURL.** The grammar, structure, and mental model are the same. If you know PURL, you know SecID.

| Same as PURL | Different in SecID |
|--------------|-------------------|
| Grammar: `scheme:type/namespace/name@version?qualifiers#subpath[@item_version]` | Scheme: `secid:` instead of `pkg:` |
| Percent encoding rules | Types: security domains instead of package ecosystems |
| Version and qualifier semantics | Subpath: references items in databases, not files in packages |

### Why the Differences Matter

PURL identifies packages. SecID identifies security knowledge. Different domains need different schemes - that's expected.

The types change from package ecosystems (`npm`, `pypi`, `maven`) to security domains (`advisory`, `weakness`, `control`). This is vocabulary, not structure.

**The subpath difference is where the real value comes from.**

PURL's `#subpath` points to files: `pkg:npm/lodash@4.17.21#lib/fp.js`

SecID's `#subpath` points to **specific items within security knowledge**:

```
secid:advisory/mitre.org/cve#CVE-2024-1234           # A specific vulnerability
secid:control/nist.gov/800-53@r5#AC-1               # A specific security control
secid:regulation/europa.eu/gdpr#art-32/1/a             # Article 32(1)(a) of GDPR
secid:ttp/mitre.org/attack#T1059.003                # A specific attack technique
secid:weakness/mitre.org/cwe#CWE-79/mitigations     # Mitigations section within a weakness
```

Security knowledge isn't packages with files - it's databases of identifiers, frameworks of controls, and regulations with articles. The subpath lets us precisely reference any item within any security knowledge system.

### What This Precision Enables

Being able to reference specific items - not just "the NIST 800-53 framework" but "control AC-1 in revision 5" - unlocks capabilities that weren't possible before:

- **Cross-reference security knowledge**: Link a CVE to its CWE weakness to the ATT&CK technique that exploits it
- **Map compliance requirements**: Connect GDPR Article 32 to the specific controls that satisfy it
- **Build relationship graphs**: Express that control X mitigates weakness Y which is exploited by technique Z
- **Layer enrichment data**: Add severity scores, organizational context, or remediation guidance on top of canonical identifiers
- **Enable AI-powered security tooling**: Give agents precise handles to fetch, compare, and reason about security knowledge

SecID is foundational infrastructure. The identifier system is deliberately simple; the value comes from what you build on top.

### Subpath Patterns

SecID subpaths support hierarchical references and framework-specific patterns:

```
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/audit           # Audit section of a control
secid:regulation/europa.eu/gdpr#art-32/1/a              # Article 32(1)(a)
secid:advisory/redhat.com/errata#RHSA-2024:1234      # Red Hat Security Advisory
secid:advisory/redhat.com/errata#RHBA-2024:5678      # Red Hat Bug Advisory

# Item versioning (pin a specific revision of an item)
secid:advisory/github.com/advisories/ghsa#GHSA-cxpw-2g23-2vgw@a1b2c3d  # GHSA at specific git commit
secid:advisory/redhat.com/errata#RHSA-2026:3102@rev2                     # Erratum at revision 2
```

Each registry file documents its subpath patterns and resolution rules.

### Registry File Mapping

**One file per namespace.** Each namespace file contains ALL sources for that organization:

```
SecID:                          Registry File:
secid:weakness/mitre.org/cwe        → registry/weakness/org/mitre.md (cwe source section)
secid:advisory/nist.gov/nvd         → registry/advisory/gov/nist.md (nvd source section)
secid:ttp/mitre.org/attack          → registry/ttp/org/mitre.md (attack source section)
secid:control/cloudsecurityalliance.org/ccm           → registry/control/org/cloudsecurityalliance.md (ccm source section)
secid:regulation/europa.eu/gdpr        → registry/regulation/eu/europa.md (gdpr source section)
```

Each registry file contains resolution rules for all sources in that namespace. For example, `registry/weakness/org/mitre.md` contains the `cwe` source section explaining how `#CWE-123` resolves to `https://cwe.mitre.org/data/definitions/123.html`.

## Identifier Format

```
secid:type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]
```

**Examples:**
```
secid:advisory/mitre.org/cve#CVE-2024-1234            # CVE record
secid:weakness/mitre.org/cwe#CWE-79                   # CWE weakness
secid:ttp/mitre.org/attack#T1059.003                  # ATT&CK technique
secid:control/nist.gov/csf@2.0#PR.AC-1               # NIST CSF control
secid:control/cloudsecurityalliance.org/aicm@1.0#A&A-01                # CSA AICM control
secid:advisory/redhat.com/errata#RHSA-2024:1234      # Red Hat advisory (colon in ID)
secid:regulation/europa.eu/gdpr#art-32                  # GDPR Article 32
secid:entity/mitre.org/cve                           # CVE program
secid:reference/whitehouse.gov/eo-14110              # Reference document
```

SecID strings are human-readable - no encoding needed. Subpaths can use `/` for hierarchy.

## Types

| Type | What it identifies |
|------|-------------------|
| `advisory` | Publications/records about vulnerabilities |
| `weakness` | Abstract flaw patterns |
| `ttp` | Adversary techniques and behaviors |
| `control` | Security requirements and capabilities that implement them |
| `disclosure` | Vulnerability disclosure programs, policies, reporting channels |
| `regulation` | Laws and binding legal requirements |
| `entity` | Organizations, products, services, platforms |
| `reference` | Documents, publications, research |

Types are intentionally broad. We overload related concepts into existing types:

| Type | Also Contains | Why |
|------|---------------|-----|
| `advisory` | Incident reports (AIID, NHTSA, FDA) | Both are "something happened" publications |
| `control` | Prescriptive benchmarks, documentation standards | Define requirements (what to test, what to document) |

Split into new types only when usage demonstrates the need. See [DESIGN-DECISIONS.md](docs/explanation/DESIGN-DECISIONS.md#type-evolution).

## Repository Structure

```
secid/
├── SPEC.md              # Identifier specification
├── docs/
│   ├── explanation/             # Why decisions were made
│   │   ├── RATIONALE.md         # Why SecID exists
│   │   └── DESIGN-DECISIONS.md  # Key decisions and architecture
│   ├── guides/                  # Task-oriented how-tos
│   ├── reference/               # Technical specs (formats, versioning, edge cases)
│   └── future/                  # Aspirational (not commitments)
│       ├── STRATEGY.md          # Adoption and governance
│       ├── USE-CASES.md         # Concrete examples
│       ├── RELATIONSHIPS.md     # Relationship layer (exploratory)
│       └── OVERLAYS.md          # Overlay layer (exploratory)
├── ROADMAP.md           # Implementation phases
├── registry/            # Namespace definitions
│   ├── advisory.md      # Type definition (what is an advisory?)
│   ├── advisory/        # Advisory namespaces (ONE FILE PER NAMESPACE)
│   │   ├── org/         # .org TLD
│   │   │   └── mitre.md # MITRE: cve
│   │   ├── gov/         # .gov TLD
│   │   │   └── nist.md  # NIST: nvd
│   │   └── com/         # .com TLD
│   │       ├── github/  # GitHub sub-namespaces
│   │       └── redhat.md# Red Hat: cve, errata, bugzilla (all sources in one file)
│   ├── weakness.md      # Type definition
│   ├── weakness/
│   │   └── org/
│   │       ├── mitre.md # MITRE: cwe
│   │       └── owasp.md # OWASP: top10, llm-top10, etc. (all in one file)
│   ├── ttp.md           # Type definition
│   ├── ttp/
│   │   └── org/
│   │       └── mitre.md # MITRE: attack, atlas, capec (all in one file)
│   ├── control.md       # Type definition
│   ├── control/
│   │   ├── gov/
│   │   │   └── nist.md  # NIST: csf, 800-53, ai-rmf
│   │   └── org/
│   │       └── iso.md   # ISO: 27001, 27002
│   ├── disclosure.md    # Type definition
│   ├── disclosure/      # Disclosure namespaces
│   ├── entity.md        # Type definition
│   ├── entity/
│   │   ├── org/
│   │   │   └── mitre.md # MITRE organization
│   │   └── com/
│   │       └── redhat.md# Red Hat organization
│   └── ...
└── seed/                # Research data (CSV) - see seed/README.md
```

**One file per namespace.** Each namespace file (e.g., `registry/advisory/com/redhat.md`) contains ALL sources for that namespace with ID patterns and URL templates. See [DESIGN-DECISIONS.md](docs/explanation/DESIGN-DECISIONS.md) for the full architecture.

## File Format

SecID is AI-first, meaning files need to be easily parsed by AI agents while remaining human-readable. We use markdown with YAML frontmatter (Obsidian-compatible):

```markdown
---
title: MITRE Advisory Namespace
type: advisory
namespace: mitre.org
---

# Content here...
```

Why this format:
- **Embedded metadata** - Structured data lives with the content, not in a separate file or database
- **AI-parseable** - YAML frontmatter is trivially extracted; markdown is universally understood by LLMs
- **Human-readable** - Works in any text editor, renders nicely on GitHub
- **Tool support** - Compatible with Obsidian, static site generators, and countless other tools
- **No better alternative** - This is the most common, simplest format for structured documents; we haven't found anything easier or more widely supported

## Glossary

| Term | Definition |
|------|------------|
| **SecID** | A complete identifier string starting with `secid:` |
| **Scheme** | The URL scheme - always `secid:` (like `pkg:` in PURL) |
| **Type** | The security domain (advisory, weakness, ttp, control, disclosure, regulation, entity, reference) |
| **Namespace** | **Domain name**, or **domain name with path**, of the organization that publishes/maintains. A plain domain (`redhat.com`, `cloudsecurityalliance.org`) or a domain with `/`-separated path segments (`github.com/advisories`, `github.com/ModelContextProtocol-Security/vulnerability-db`). Allowed per segment: `a-z`, `0-9`, `-`, `.`, and Unicode letters/numbers. |
| **Name** | The database/framework/document they publish (e.g., `cve`, `nvd`, `ccm`, `attack`). Can contain any characters - resolved by registry lookup. |
| **Version** | Optional `@version` suffix on the name for edition/revision of the source (e.g., `@4.0`, `@2021`, `@2016-04-27`) |
| **Item Version** | Optional `@item_version` suffix on the subpath for a specific revision of an individual item (e.g., `@a1b2c3d` for a git commit, `@rev2` for a revision). Parsed using the registry's pattern tree (`match_nodes`). |
| **Version Required** | Some sources declare `version_required: true` in the registry — meaning unversioned references are ambiguous (e.g., OWASP Top 10 `#A01` means different things in 2017 vs 2021). When version is required but absent, the resolver returns all matching versions with disambiguation guidance instead of a single result. |
| **Qualifier** | Optional `?key=value` for context that doesn't change identity |
| **Subpath** | The specific item within the document (e.g., `#CVE-2024-1234`, `#IAM-12`, `#T1059`); can use `/` for hierarchy |
| **Registry** | The collection of namespace definition files that document what identifiers exist |
| **Resolution** | The process of converting a SecID to a URL or retrieving the identified resource |

## Resolution Examples

SecIDs identify things; resolution retrieves them. Each namespace defines how to resolve its identifiers:

```
secid:advisory/mitre.org/cve#CVE-2026-0544
  → https://www.cve.org/CVERecord?id=CVE-2026-0544

secid:advisory/nist.gov/nvd#CVE-2026-0544
  → https://nvd.nist.gov/vuln/detail/CVE-2026-0544

secid:advisory/redhat.com/cve#CVE-2026-0544
  → https://access.redhat.com/security/cve/CVE-2026-0544

secid:advisory/redhat.com/errata#RHSA-2026:0414
  → https://access.redhat.com/errata/RHSA-2026:0414

secid:weakness/mitre.org/cwe#CWE-79
  → https://cwe.mitre.org/data/definitions/79.html

secid:ttp/mitre.org/attack#T1059.003
  → https://attack.mitre.org/techniques/T1059/003/

secid:regulation/europa.eu/gdpr#art-32
  → https://gdpr-info.eu/art-32-gdpr/

secid:advisory/github.com/advisories/ghsa#GHSA-jfh8-c2jp-5v3q@a1b2c3d
  → https://github.com/github/advisory-database/blob/a1b2c3d/advisories/github-reviewed/GHSA-jfh8-c2jp-5v3q.json
```

Resolution URLs are defined in each namespace's registry file. Item versions (like `@a1b2c3d` above) pin a specific revision — the registry's pattern tree determines where the item ID ends and the version begins.

## Documentation

| Document | Purpose |
|----------|---------|
| [SPEC.md](SPEC.md) | Full technical specification for identifiers |
| [RATIONALE.md](docs/explanation/RATIONALE.md) | Why SecID exists and how we got here |
| [DESIGN-DECISIONS.md](docs/explanation/DESIGN-DECISIONS.md) | Key decisions and alternatives considered |
| [EDGE-CASES.md](docs/reference/EDGE-CASES.md) | Domain-name namespace edge cases and how SecID handles them |
| [STRATEGY.md](docs/future/STRATEGY.md) | Adoption, governance, and positioning |
| [ROADMAP.md](ROADMAP.md) | Implementation phases and priorities |
| [USE-CASES.md](docs/future/USE-CASES.md) | Concrete examples of what SecID enables |

## Design Principles

1. **AI-first** - Primary consumer is AI agents; registry content includes context, guidance, and parsing hints that enable AI to work autonomously with security knowledge
2. **Identifiers are just identifiers** - The spec defines identifier syntax; relationships and enrichment are separate future layers
3. **Identifier, not locator** - SecID identifies things; resolution is separate
4. **Identity ≠ authority** - Identifiers don't imply trust or correctness
5. **PURL compatibility** - Same mental model, similar grammar
6. **Guidelines, not rules** - Human/AI readable, some messiness OK

## Non-Goals

Being explicit about scope helps set expectations. SecID is deliberately limited:

| Non-Goal | Why Not |
|----------|---------|
| **Not a numbering authority** | SecID doesn't assign CVE-2024-1234, GHSA-xxxx, or any individual identifiers. Those come from their respective authorities (MITRE, GitHub, AVID, etc.). SecID references what they assign. |
| **Not a vulnerability disclosure program** | CVE, vendors, and coordinated disclosure programs handle this. SecID references their work. |
| **Not an authority on severity or truth** | CVSS scores, exploitability assessments, and validity judgments are the domain of NVD, vendors, and security researchers. SecID points to their assessments without adjudicating. |
| **Not a replacement for CVE/CWE/ATT&CK/NIST** | These are authoritative within their domains. SecID is a coordination layer that makes them easier to reference together. |
| **Not a universal content mirror** | Licensing, copyright, and data ownership vary. SecID provides resolution (where to find things), not redistribution. |
| **Not a policy engine** | "Should we patch this?" is a business decision. SecID helps you find the information; it doesn't make the call. |
| **Not a knowledge graph (yet)** | Relationships and enrichment are future layers, deliberately deferred until we understand real usage patterns. |

**Why these boundaries matter:** Scope creep kills standards. By being explicit about what SecID won't do, we can focus on doing the identifier and resolution job well. Organizations considering adoption can evaluate SecID for what it is, not what it might become.

## Governance

SecID is a Cloud Security Alliance project with a lightweight governance model during early development and an explicit path toward broader community governance. See [GOVERNANCE.md](GOVERNANCE.md) for the current operating model and [STRATEGY.md](docs/future/STRATEGY.md) for long-term governance philosophy.

## Project Repositories

SecID is built across multiple repositories under the [CloudSecurityAlliance](https://github.com/CloudSecurityAlliance) GitHub organization:

| Repo | Purpose |
|------|---------|
| **[SecID](https://github.com/CloudSecurityAlliance/SecID)** (this repo) | Specification, registry data, design documents |
| **[SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service)** | Cloudflare Worker REST API + MCP server — **live** at [secid.cloudsecurityalliance.org](https://secid.cloudsecurityalliance.org/) |
| **[SecID-Client-SDK](https://github.com/CloudSecurityAlliance/SecID-Client-SDK)** | Client libraries + AI instructions (Python, npm, Go, Rust, Java, C#) |
| **SecID-Website** | Cloudflare Pages documentation site (planned) |

## Getting Started

- **Read the spec:** [SPEC.md](SPEC.md)
- **Understand why:** [RATIONALE.md](docs/explanation/RATIONALE.md)
- **See examples:** [USE-CASES.md](docs/future/USE-CASES.md)
- **Browse namespaces:** [registry/](registry/)
- **Contribute:** [CONTRIBUTING.md](CONTRIBUTING.md) and [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Hands-on guides:** [docs/guides/](docs/guides/) — step-by-step walkthroughs for adding namespaces, writing patterns, and converting formats

**Using AI tools?** We encourage it. See [AGENTS.md](AGENTS.md) for general agent instructions. If you're using Claude Code, Gemini, or similar tools, run `/init` to pick up the repo-specific configuration files automatically.

## Current Status

**Version 0.9 - Public Draft**

This specification is open for public comment. We welcome feedback, questions, and suggestions via [GitHub Issues](https://github.com/CloudSecurityAlliance/SecID/issues).

| Component | Status |
|-----------|--------|
| Identifier grammar + 8 types | **Done** |
| Registry namespaces (YAML + JSON) | **Done** — see counts below |
| [REST API + MCP server](https://github.com/CloudSecurityAlliance/SecID-Service) | **Live** at [secid.cloudsecurityalliance.org](https://secid.cloudsecurityalliance.org/) |
| [Client SDKs](https://github.com/CloudSecurityAlliance/SecID-Client-SDK) (Python, npm, Go, etc.) | In progress |
| Registry validation skill | **Active** |
| Compliance test suite | Not started |
| Relationship layer | Post-1.0 |
| Overlay layer | Post-1.0 |

### Registry Namespace Counts

<!-- REGISTRY-COUNTS-START -->

| Type | Count |
|------|-------|
| Advisory | 42 |
| Weakness | 13 |
| Ttp | 4 |
| Control | 24 |
| Disclosure | 1 |
| Regulation | 4 |
| Entity | 14 |
| Reference | 29 |
| **Total** | **131** |

<!-- REGISTRY-COUNTS-END -->

**Where help is needed:** See [docs/project/](docs/project/) for gap analysis, open issues, and known concerns.

## License

[CC0 1.0 Universal](LICENSE) - Public Domain Dedication

---

*A project of the Cloud Security Alliance*
