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

That's it. No API keys, no local install, no configuration. Works with Claude Desktop, Claude Code, Cursor, Windsurf, and any MCP client that supports remote servers. Your AI assistant gets three tools (`resolve`, `lookup`, `describe`) and can immediately look up CVEs, CWEs, ATT&CK techniques, NIST controls, and 121 other security knowledge sources.

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

## Vision

**A SecID isn't just an identifier - it's a handle that gives you everything you need to understand and work with security knowledge.**

Today, security data is fragmented. CVEs live in one place, CWEs in another, controls in spreadsheets, regulations in PDFs. Finding information requires knowing where to look. Understanding it requires domain expertise. Connecting it requires manual effort.

SecID changes this. When you have a SecID, you can:

1. **Find it** - Get the URL or search instructions
2. **Understand it** - Read a description of what it is
3. **Read it** - Get the actual content (where licensing permits)
4. **Interpret it** - Understand what the fields mean
5. **Use it** - Know what to do with this data
6. **Connect it** - See related concepts, mitigations, and examples

**This is AI-first infrastructure** - but not AI-only. The primary consumer is AI agents that need to navigate security knowledge autonomously. When an agent receives a SecID response, it should be self-describing - the agent knows what it has, how to interpret it, and what to do with it.

**Traditional tools are first-class consumers too.** SecID identifiers work in:
- **SIEMs and SOC platforms** - Correlate alerts across vulnerability, weakness, and technique taxonomies
- **GRC tools** - Map controls to regulations to compliance evidence
- **Vulnerability scanners** - Link findings to weaknesses, techniques, and remediations
- **SBOMs and VEX documents** - Reference advisories with consistent identifiers
- **Asset inventories** - Tag systems with applicable controls and regulations
- **Policy automation** - Define rules that reference specific controls or requirements

AI agents accelerate adoption because they can consume SecID immediately without organizational buy-in. But the long-term value is infrastructure that humans, traditional tools, and AI all use together.

We're building this in layers:
- **v1.0**: URL resolution + descriptions (where to find it, what it is)
- **v1.x**: Raw content with licensing (the actual text, properly attributed)
- **v2.x**: Metadata wrapper (interpretation and usage guidance for AI)
- **Future**: Relationships and overlays (connections and enrichment)

See [ROADMAP.md](ROADMAP.md) for the full implementation plan.

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
| `regulation` | Laws and binding legal requirements |
| `disclosure` | Vulnerability disclosure programs, policies, reporting channels |
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
│   ├── disclosure/      # Disclosure namespaces (empty — new type)
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

### Future Work (Not Yet Designed)

| Document | Purpose |
|----------|---------|
| [RELATIONSHIPS.md](docs/future/RELATIONSHIPS.md) | Exploratory thinking on how identifiers might connect |
| [OVERLAYS.md](docs/future/OVERLAYS.md) | Exploratory thinking on enrichment without mutation |

**The spec is just IDs.** Relationships and overlays are future layers that will be designed based on real-world usage of the identifier system. We're deliberately deferring these to avoid premature complexity.

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

SecID currently uses a **Benevolent Dictator For Life (BDFL)** model for rapid early-stage decision making. This is a pragmatic choice - premature governance complexity kills more projects than it saves.

**Long-term intent:** We are explicitly working toward a sustainable, vendor-neutral, multi-stakeholder governance structure appropriate for industry infrastructure. The spec and registry content are separable governance artifacts - the identifier format can stabilize while registry policies continue to evolve.

See [STRATEGY.md](docs/future/STRATEGY.md) for detailed governance philosophy, funding approach, and organizational strategy.

## Ecosystem Architecture

SecID is designed as a federated ecosystem with multiple independent components:

| Component | What It Is | Can Be Multiple? |
|-----------|------------|------------------|
| **SecID Standard** | The identifier specification (`secid:type/namespace/name#subpath`) | One canonical spec, versioned |
| **SecID Registries** | Namespace definitions, resolution rules | Yes - private registries, organizational overlays |
| **Relationship Databases** | Connections between identifiers | Yes - different sources, perspectives |
| **Enrichment Databases** | Metadata, annotations, context | Yes - organizational data, private enrichments |
| **SecID APIs** | Services that resolve and query | Yes - different providers, implementations |

**Federation means:** Organizations can run their own registries, databases, and APIs that overlay or extend the canonical data. A company might maintain private namespace definitions, internal relationship mappings, or proprietary enrichments - all compatible with the public ecosystem.

### Arbitrary URL Support

SecID identifiers are for **structured security knowledge with defined namespaces**. Arbitrary URLs are explicitly NOT part of the identifier specification (no `secid:url/...` type). However, APIs and databases can support URL queries:

| Component | SecID Identifiers | Arbitrary URLs |
|-----------|-------------------|----------------|
| **SecID Standard** | ✅ Defines these | ❌ Explicitly excluded |
| **SecID Registry** | ✅ Contains these | ❌ Not applicable |
| **Our API** | ✅ Must support | ✅ Probably will support |
| **Our Relationship DB** | ✅ Must include | ✅ Probably will include |
| **Our Enrichment DB** | ✅ Must include | ✅ Probably will include |

**Why this separation?** URLs are already globally unique identifiers - wrapping them in `secid:url/...` adds complexity without value. But APIs and databases can accept URLs as query inputs and store relationships/enrichments for arbitrary web content. This keeps the spec clean while enabling practical use cases like "what do we know about this Stack Overflow answer?"

See [SPEC.md Section 1.3](SPEC.md#13-scope-what-secid-identifies-and-what-it-doesnt) for the full rationale.

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

**What's Ready:**
- Identifier grammar defined
- Eight types established
- Registry structure with 100+ namespace definitions
- Documentation for spec, rationale, design decisions, and strategy

**What's In Progress:**
- Registry expansion (targeting broader coverage)
- Reference implementations (Python library first)
- Compliance test suite
- [REST API + MCP server](https://github.com/CloudSecurityAlliance/SecID-Service) (live, iterating)

**What's Planned (Post-1.0):**
- Relationship layer
- Overlay layer

**Where help is needed:** See [docs/project/](docs/project/) for gap analysis, open issues, and known concerns.

## Future: Making SecID Easy to Consume

Our goal is to make SecID as easy to consume as possible. We're building:

| Repository | Purpose | Status |
|------------|---------|--------|
| **SecID** (this repo) | Spec, registry, operations docs | Active |
| **[SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service)** | Hosted API + MCP server | Active |
| **SecID-Website** | Documentation and registry browser | Planned |
| **SecID-Client-SDK** | Client libraries + AI instructions | Planned |

### SecID-Service

**The SecID service is live!** See the [SecID-Service repository](https://github.com/CloudSecurityAlliance/SecID-Service) for details.

Cloudflare Worker providing:
- REST API at `/api/v1/` for programmatic access
- MCP server at `/mcp` for AI agent integration

**Primary integration path:** Add `https://secid.cloudsecurityalliance.org/mcp` as a remote MCP server. Your AI assistant can then use the tools directly or generate API client code on the fly.

### SecID-Client-SDK

Reference client libraries and AI-consumable instructions:
- Python (`pip install secid`) and npm/TypeScript (`npm install secid`) for SEO and discoverability
- AI instructions for generating clients in any language
- Test fixtures extracted from the registry

### LLM-Friendly

We support the [llms.txt standard](https://llmstxt.org/) for AI-friendly content discovery. The website provides `/llms.txt` with structured links to key resources, enabling AI agents to efficiently understand SecID.

See [INFRASTRUCTURE.md](docs/reference/INFRASTRUCTURE.md) for technical details on hosting and architecture

## License

[CC0 1.0 Universal](LICENSE) - Public Domain Dedication

---

*A project of the Cloud Security Alliance*
