# SecID Specification

Version: 0.9
Status: Public Draft - Open for Comment

> **This is a draft specification.** We welcome feedback, questions, and suggestions. Please open an issue at [github.com/kurtseifried/SecID/issues](https://github.com/kurtseifried/SecID/issues) or submit a pull request.

## 1. Overview

**SecID provides a grammar and registry for referencing security knowledge. SecID does not assign identifiers—those come from their respective authorities.**

SecID is directly modeled after [Package URL (PURL)](https://github.com/package-url/purl-spec). It provides a consistent way to reference existing databases like CVE, CWE, ATT&CK, and ISO standards.

**This specification is not a recipe for parsing individual SecID strings in isolation. It is a blueprint for building a parser** — a system that combines this grammar with registry data to parse, validate, and resolve SecIDs. A standalone regex cannot parse SecIDs because the registry resolves every structural ambiguity: where the namespace ends, where the name ends, whether `@` is a version delimiter or part of an identifier.

This is by design. Because every SecID contains a domain name (`mitre.org`, `github.com/advisories`, `redhat.com`), even an unknown SecID carries enough information to bootstrap its own resolution. A human or AI encountering `secid:advisory/newvendor.com/alerts#ALERT-2026-001` can visit `newvendor.com`, understand their alert system, and contribute a registry entry. The goal is comprehensive registry coverage — and the ecosystem (hosted service, easy contribution, federation) is how we get there. But the domain-name design means encountering an unknown SecID is a solvable problem, not a dead end.

**SecID does not replace CVE, CWE, ATT&CK, or any other authority.** It references them. `secid:advisory/mitre.org/cve#CVE-2024-1234` points to MITRE's CVE record; it doesn't create a new one. CVE-2024-1234 is assigned by MITRE—SecID provides a consistent way to reference it.

**SecID identifies things. It does not imply authority, truth, severity, or correctness.**

This is intentionally aligned with PURL:
- Identity ≠ metadata
- Identity ≠ trust
- Identity ≠ location

Resolution, dereferencing, or retrieval happens via APIs outside the identifier itself.

### 1.1 Relationship to PURL

Package URL (PURL) provides a universal scheme for identifying software packages: `pkg:<type>/<namespace>/<name>`. But PURL is explicitly for packages only.

In the security world, we need to identify many things that aren't packages: advisories, weaknesses, attack techniques, controls, regulations, entities, and reference documents. Rather than invent something new, we essentially created a "package URL" for each category of security knowledge we needed to identify.

**Why `secid:`?** PURL uses `pkg:` as its scheme for packages. SecID uses `secid:` as its scheme for security knowledge. What follows the scheme is identical to PURL grammar: `type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]`. Everywhere in SecID, we're using PURL-compliant grammar - just with `secid:` as the scheme because we're identifying security knowledge, not software packages. The `@item_version` extension allows pinning specific revisions of individual items (e.g., a GHSA advisory at a specific git commit), and qualifiers can appear on both the name (source-level) and the subpath (item-level).

### 1.2 Exact PURL to SecID Mapping

SecID is PURL with a different scheme. The grammar is identical:

```
PURL:   pkg:type/namespace/name@version?qualifiers#subpath
SecID:  secid:type/namespace/name@version?qualifiers#subpath[@item_version][?qualifiers]
```

**Component-by-component mapping:**

| PURL Component | SecID Component | Required | SecID Usage |
|----------------|-----------------|----------|-------------|
| `pkg:` | `secid:` | Yes | Scheme (constant prefix) |
| `type` | `type` | Yes | Security domain: `advisory`, `weakness`, `ttp`, `control`, `regulation`, `entity`, `reference` |
| `namespace` | `namespace` | Yes | **Domain name**, or **domain name with path**, of the organization that publishes/maintains. A plain domain (`redhat.com`, `cloudsecurityalliance.org`) or a domain with `/`-separated path segments (`github.com/advisories`, `github.com/ModelContextProtocol-Security/vulnerability-db`). |
| `name` | `name` | Yes | **Database/framework/standard** they publish (e.g., `cve`, `nvd`, `cwe`, `attack`, `ccm`, `27001`) |
| `@version` | `@version` | No | Edition or revision (e.g., `@4.0`, `@2022`, `@2.0`) |
| `?qualifiers` | `?qualifiers` | No | Optional context that doesn't change identity (e.g., `?lang=ja`) |
| `#subpath` | `#subpath` | No | **Specific item** within the database/framework (e.g., `#CVE-2024-1234`, `#CWE-79`, `#T1059`, `#A.8.1`) |
| `@item_version` | `@item_version` | No | **Version of the specific item** (e.g., `@a1b2c3d` for a git commit, `@rev2` for a revision). SecID extension — not in PURL. |

**Visual breakdown:**

```
secid:advisory/mitre.org/cve#CVE-2024-1234
────┬─ ────┬──── ────┬──── ─┬─ ──────┬──────
    │      │         │      │        └─ #subpath: specific item (CVE-2024-1234)
    │      │         │      └────────── name: database they publish (cve)
    │      │         └───────────────── namespace: domain name (mitre.org)
    │      └─────────────────────────── type: security domain (advisory)
    └────────────────────────────────── scheme: always "secid:"

secid:control/iso.org/27001@2022#A.8.1
────┬─ ──┬──── ──┬─── ──┬── ─┬── ──┬──
    │    │       │      │    │     └─ #subpath: specific control (A.8.1)
    │    │       │      │    └─────── @version: edition (2022)
    │    │       │      └──────────── name: standard (27001)
    │    │       └─────────────────── namespace: domain name (iso.org)
    │    └─────────────────────────── type: security domain (control)
    └──────────────────────────────── scheme: always "secid:"

secid:weakness/owasp.org/top10@2021#A03
────┬─ ───┬──── ────┬──── ──┬── ─┬── ─┬─
    │     │         │       │    │    └─ #subpath: specific weakness (A03)
    │     │         │       │    └────── @version: edition year (2021)
    │     │         │       └─────────── name: framework (top10)
    │     │         └─────────────────── namespace: domain name (owasp.org)
    │     └───────────────────────────── type: security domain (weakness)
    └─────────────────────────────────── scheme: always "secid:"
```

**Key insight:** The namespace is always the **domain name** of the organization (who publishes it), the name is the **thing they publish** (database, framework, standard), and the subpath is the **specific item within** that thing. Platform namespaces can include path segments (e.g., `github.com/advisories`).

**Subpath hierarchy:** Subpaths can use `/` to express hierarchy within a document (just like PURL):

```
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12                        # The control
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/audit                  # Audit section within control
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/implementation         # Implementation guidance
secid:regulation/europa.eu/gdpr#art-32/1/a                     # Article 32(1)(a)
secid:weakness/mitre.org/cwe#CWE-79/potential-mitigations   # Mitigations section within CWE
secid:ttp/mitre.org/attack#T1059/detection                  # Detection guidance for technique
```

**Percent encoding:** Special characters in names and subpaths must be percent-encoded (URL encoding). This ensures cross-platform compatibility and safe storage/transport:

| Character | Encoded | Example |
|-----------|---------|---------|
| Space | `%20` | `Auditing Guidelines` → `Auditing%20Guidelines` |
| `&` | `%26` | `A&A-01` → `A%26A-01` |
| `(` `)` | `%28` `%29` | `(Draft)` → `%28Draft%29` |
| `/` | `%2F` | Only encode if literal (not a hierarchy separator) |
| `#` | `%23` | Only encode if literal (not the subpath prefix) |
| `@` | `%40` | Only encode if literal (not the version prefix) |
| `?` | `%3F` | Only encode if literal (not the qualifier prefix) |

```
secid:control/cloudsecurityalliance.org/aicm@1.0#A%26A-01                     # A&A-01 control (& encoded)
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/Auditing%20Guidelines  # Section with space
secid:control/nist.gov/800-53#AC-1/Control%20Enhancements  # Section with space
```

Tools should render identifiers human-friendly for display while storing the encoded form. See Section 8.2 for complete encoding rules.

**Registry file mapping:** Every level of the SecID hierarchy maps to a registry file:

```
SecID:                          Registry File:
secid:advisory                  → registry/advisory.md (type definition)
secid:advisory/redhat.com       → registry/advisory/com/redhat.md (namespace, all sources)
secid:advisory/redhat.com/cve  → section within registry/advisory/com/redhat.md
secid:weakness                  → registry/weakness.md (type definition)
secid:weakness/mitre.org        → registry/weakness/org/mitre.md (namespace, all sources)
secid:control/nist.gov          → registry/control/gov/nist.md (namespace, all sources)
```

**One file per namespace.** Each namespace file contains ALL sources for that namespace. For example, `registry/advisory/com/redhat.md` contains rules for `cve`, `errata`, and `bugzilla`—not separate files for each.

Each registry file contains:
- Metadata (namespace, full name, website, status)
- Sections for each source with ID patterns and URL templates
- Examples and documentation

For example, `registry/weakness/org/mitre.md` contains the rules for resolving CWE:

```yaml
# In registry/weakness/org/mitre.md
---
namespace: mitre.org
full_name: "MITRE Corporation"
website: "https://mitre.org"
status: active
---

# MITRE (Weakness Namespace)

## Sources

### cwe

| Field | Value |
|-------|-------|
| id_pattern | `CWE-\d+` |
| url_template | `https://cwe.mitre.org/data/definitions/{num}.html` |
| example | `secid:weakness/mitre.org/cwe#CWE-79` |
```

**Resolution process (6 steps):**

```
secid:weakness/mitre.org/cwe#CWE-123

1. Parse SecID → type=weakness, namespace=mitre.org, name=cwe, subpath=CWE-123
2. Lookup source → registry["weakness"]["mitre.org"]["cwe"]
3. Match patterns → subpath "CWE-123" matches pattern "^CWE-\d+$"
4. Extract variables → "number" regex captures "123" from "CWE-123"
5. Extract item version → if "@" follows the matched pattern, extract item_version (none in this case)
6. Build URL → https://cwe.mitre.org/data/definitions/123.html
```

**Note:** If version is absent in step 2, check the source's `version_required` field. If `true`, the resolver's behavior changes — instead of building a single URL, it returns multiple versions with disambiguation guidance. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) for details.

For complex URLs, patterns define variables that extract parts of the ID:

```json
{
  "pattern": "^CWE-\\d+$",
  "url": "https://cwe.mitre.org/data/definitions/{number}.html",
  "variables": {
    "number": {
      "extract": "^CWE-(\\d+)$",
      "description": "Numeric ID portion"
    }
  }
}
```

When URLs can't be computed from patterns — because the source uses inconsistent slugs or non-derivable paths — `lookup_table` maps specific IDs directly to their URLs. For example, the OWASP LLM Top 10 entries have inconsistent URL slugs (`llm01-prompt-injection` vs `llm022025-sensitive-information-disclosure`), so each entry is mapped explicitly. A `provenance` object records how the lookup data was gathered (method, date, source URL) so reviewers can re-verify it.

See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) for the complete schema.

**More examples showing the pattern:**

| SecID | namespace (org) | name (what they publish) | subpath (specific item) |
|-------|-----------------|--------------------------|-------------------------|
| `secid:advisory/mitre.org/cve#CVE-2024-1234` | MITRE | CVE database | CVE-2024-1234 |
| `secid:advisory/nist.gov/nvd#CVE-2024-1234` | NIST | NVD database | CVE-2024-1234 |
| `secid:advisory/redhat.com/errata#RHSA-2024:1234` | Red Hat | Errata system | RHSA-2024:1234 |
| `secid:weakness/mitre.org/cwe#CWE-79` | MITRE | CWE taxonomy | CWE-79 |
| `secid:ttp/mitre.org/attack#T1059` | MITRE | ATT&CK framework | T1059 |
| `secid:ttp/mitre.org/capec#CAPEC-66` | MITRE | CAPEC catalog | CAPEC-66 |
| `secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12` | CSA | CCM framework | IAM-12 |
| `secid:control/nist.gov/csf@2.0#PR.AC-1` | NIST | CSF framework | PR.AC-1 |
| `secid:control/iso.org/27001@2022#A.8.1` | ISO | 27001 standard | A.8.1 |
| `secid:regulation/europa.eu/gdpr#art-32` | EU | GDPR regulation | Article 32 |

### 1.3 Comparison with PURL Examples

| What you're identifying | Scheme | Example |
|------------------------|--------|---------|
| Software packages | `pkg:` | `pkg:npm/lodash@4.17.21` |
| Vulnerability advisories | `secid:` | `secid:advisory/mitre.org/cve#CVE-2024-1234` |
| Weakness patterns | `secid:` | `secid:weakness/mitre.org/cwe#CWE-79` |
| Attack techniques | `secid:` | `secid:ttp/mitre.org/attack#T1059` |
| Security controls | `secid:` | `secid:control/nist.gov/csf@2.0#PR.AC-1` |
| Regulations | `secid:` | `secid:regulation/europa.eu/gdpr#art-32` |
| Entities | `secid:` | `secid:entity/mitre.org/cve` |
| Reference documents | `secid:` | `secid:reference/whitehouse.gov/eo-14110` |

Think of it this way: `secid:` is the scheme (like `pkg:`), and what follows uses the exact same grammar as PURL.

### 1.4 Divergences from PURL

SecID uses PURL grammar but diverges in three specific ways:

#### 1. Scheme: `secid:` instead of `pkg:`

PURL uses `pkg:` to identify packages. SecID uses `secid:` to identify security knowledge. This is the expected way to use PURL grammar for a different domain.

#### 2. Type: Security domains instead of package ecosystems

PURL types are package ecosystems: `npm`, `pypi`, `maven`, `cargo`, `nuget`, etc.

SecID types are security domains: `advisory`, `weakness`, `ttp`, `control`, `regulation`, `entity`, `reference`.

This is semantic, not structural - the grammar is identical, just the vocabulary differs.

#### 3. Subpath: Identifier references instead of file paths

**This is the significant divergence.**

In PURL, `#subpath` is defined as "a subpath within the package, relative to the package root" - meant for file paths like `pkg:npm/lodash@4.17.21#lib/fp.js`.

In SecID, `#subpath` identifies **specific items within a database or framework**:

```
secid:advisory/mitre.org/cve#CVE-2024-1234       # A specific CVE
secid:weakness/mitre.org/cwe#CWE-79              # A specific weakness
secid:ttp/mitre.org/attack#T1059.003             # A specific technique
secid:control/nist.gov/800-53@r5#AC-1            # A specific control
secid:control/iso.org/27001@2022#A.8.1           # An ISO Annex control
secid:advisory/redhat.com/errata#RHSA-2024:1234  # A Red Hat advisory
```

**Why this divergence is necessary:**

Security databases aren't packages with files - they're registries of identifiers. CVE-2024-1234 isn't a file path; it's an identifier within the CVE database. The subpath lets us say "this specific item within that database" using PURL-compatible syntax.

**Extended subpath semantics:**

Because security knowledge is often hierarchical, SecID subpaths support:

1. **Identifier prefixes** - Different item types within one name:
   ```
   secid:advisory/redhat.com/errata#RHSA-2024:1234  # Security Advisory
   secid:advisory/redhat.com/errata#RHBA-2024:5678  # Bug Advisory
   secid:advisory/redhat.com/errata#RHEA-2024:9012  # Enhancement Advisory
   ```

2. **Hierarchical references** using `/`:
   ```
   secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/audit           # Audit section of control
   secid:regulation/europa.eu/gdpr#art-32/1/a              # Article 32(1)(a)
   secid:weakness/mitre.org/cwe#CWE-79/mitigations      # Mitigations for CWE-79
   ```

3. **Framework-specific patterns**:
   ```
   secid:ttp/mitre.org/attack#T1059.003    # Sub-technique (ATT&CK uses dots)
   secid:control/iso.org/27001@2022#A.8.1  # Annex control (ISO uses dots)
   secid:control/nist.gov/800-53@r5#AC-1   # Control family-number format
   ```

Each registry file documents its subpath patterns and how to resolve them to URLs.

### 1.3 Scope: What SecID Identifies (and What It Doesn't)

**SecID identifies structured security knowledge with defined namespaces.** This includes:
- Advisories from known sources (CVE, GHSA, vendor advisories)
- Weakness taxonomies (CWE, OWASP Top 10)
- Attack techniques (ATT&CK, ATLAS, CAPEC)
- Security controls (NIST CSF, ISO 27001, CIS Controls)
- Regulations (GDPR, HIPAA)
- Entities (organizations, products, services)
- Reference documents (standards, research papers, executive orders)

**SecID does not assign identifiers.** SecID maintains a registry of identifier *systems* (CVE, GHSA, CWE, etc.) and provides a grammar to reference identifiers within those systems. The identifiers themselves (CVE-2024-1234, CWE-79, T1059) are assigned by their respective authorities (MITRE, GitHub, NIST, etc.).

**SecID does NOT provide identifiers for arbitrary URLs.** There is no `secid:url/...` type.

| What | In Scope? | Reason |
|------|-----------|--------|
| `secid:advisory/mitre.org/cve#CVE-2024-1234` | ✅ Yes | Structured security knowledge with namespace |
| `secid:weakness/mitre.org/cwe#CWE-79` | ✅ Yes | Structured security knowledge with namespace |
| `secid:url/https://example.com/...` | ❌ No | URLs are already identifiers; no need to wrap them |
| `https://stackoverflow.com/a/12345678` | ❌ No | Not a SecID - just a URL |

**Why exclude arbitrary URLs?**

1. **URLs are already identifiers** - Wrapping a URL in `secid:url/...` adds no value; the URL itself is globally unique
2. **Encoding nightmare** - URLs contain `:`, `/`, `?`, `#` which are reserved in SecID, requiring ugly percent-encoding
3. **Breaks the namespace model** - SecID's value comes from `type/namespace/name` structure; arbitrary URLs have no namespace
4. **Redundant resolution** - `secid:url/X` would just resolve to `X`

**What about referencing arbitrary web content?**

SecID APIs and relationship/enrichment databases MAY support arbitrary URLs as query inputs and relationship targets. This is an API/database feature, not part of the identifier specification.

For example, a SecID API might accept:
```
GET /api/v1/lookup?secid=secid:weakness/mitre.org/cwe%23CWE-732
GET /api/v1/lookup?url=https://stackoverflow.com/a/12345678
```

Both are valid queries to the API. The URL query returns any relationship/enrichment data associated with that URL in the database. But the URL itself is not a SecID - it's a URL that the API happens to support.

This separation keeps the identifier specification focused while allowing implementations flexibility.

## 2. Grammar

SecID follows PURL's grammar exactly, with `secid:` as the scheme:

```
secid:type/namespace/name@version?qualifiers#subpath[@item_version][?qualifiers]
```

### 2.1 Components

| Component | Required | Description |
|-----------|----------|-------------|
| `secid:` | Yes | The URL scheme (constant, like `pkg:` in PURL) |
| `type` | Yes | The security domain: advisory, weakness, ttp, control, regulation, entity, reference |
| `namespace` | Yes | The domain name of the organization (mitre.org, nist.gov, owasp.org, etc.), optionally with sub-namespace path segments (github.com/advisories) |
| `name` | Yes | The database/framework/document they publish (cve, nvd, ccm, attack, etc.) |
| `@version` | No | Edition or revision of the thing itself |
| `?qualifiers` | No | Optional disambiguation or scope. Can appear on the name (source-level) and/or on the subpath (item-level). |
| `#subpath` | No | The specific item within the document (CVE-2024-1234, IAM-12, T1059, etc.) |
| `@item_version` | No | Version of the specific item within the subpath (e.g., git commit hash for a GHSA advisory, revision number for an erratum). Follows the subpath. |

### 2.2 Hard Rules

1. The primary identifier must live in `name`, never in qualifiers
2. Qualifiers never define identity, only context
3. Subpaths reference internal structure (articles, sections, controls) - can use `/` for hierarchy
4. Canonical form always includes `secid:`, type, and namespace
5. Shorthands may exist for display but must normalize to canonical

### 2.3 Examples

```
secid:advisory/mitre.org/cve#CVE-2024-1234
secid:advisory/nist.gov/nvd#CVE-2024-1234
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx-yyyy-zzzz
secid:advisory/redhat.com/errata#RHSA-2024:1234
secid:weakness/mitre.org/cwe#CWE-79
secid:ttp/mitre.org/attack#T1059.003
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12
secid:control/cloudsecurityalliance.org/aicm@1.0#IAM-12/Auditing%20Guidelines
secid:regulation/europa.eu/gdpr@2016-04-27
secid:regulation/europa.eu/gdpr#art-32
secid:entity/mitre.org/cve
secid:entity/openai.com/gpt-4
secid:reference/whitehouse.gov/eo-14110
secid:reference/arxiv.org/2303.08774
```

## 3. Types

SecID defines seven types. Each answers a different question. Types are intentionally broad - we overload existing types with related concepts (e.g., incidents in `advisory`) and only create new types when real-world usage demonstrates the need. See [DESIGN-DECISIONS.md](docs/explanation/DESIGN-DECISIONS.md#type-evolution) for the rationale.

| Type | What it identifies | Question it answers |
|------|-------------------|---------------------|
| `advisory` | Publications/records about vulnerabilities and incidents | "What's known about this event?" |
| `weakness` | Abstract flaw patterns | "What kind of mistake is this?" |
| `ttp` | Adversary techniques and behaviors | "How do attackers do this?" |
| `control` | Security requirements, benchmarks, and documentation standards | "How do we prevent/detect/document this?" |
| `regulation` | Laws and binding legal requirements | "What does the law require?" |
| `entity` | Vendors, products, services, platforms | "What/who is this?" |
| `reference` | Documents, publications, research | "What source supports this?" |

**Current type overloading:**

| Type | Also Contains | Why |
|------|---------------|-----|
| `advisory` | Incident reports (AIID, NHTSA, FDA) | Both are "something happened" publications |
| `control` | Prescriptive benchmarks (HarmBench, WMDP) | "Test for X" is a requirement |
| `control` | Documentation standards (Model Cards) | "Document X" is a requirement |

### 3.1 Advisory

Publications, records, or analyses about vulnerabilities **and incidents**.

```
secid:advisory/mitre.org/cve#CVE-2024-1234        # CVE record (canonical)
secid:advisory/nist.gov/nvd#CVE-2024-1234         # NVD enrichment
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx-yyyy     # GitHub Security Advisory
secid:advisory/google.com/osv#PYSEC-2024-1        # OSV/PyPI advisory
secid:advisory/redhat.com/cve#CVE-2024-1234       # Red Hat CVE page
secid:advisory/redhat.com/errata#RHSA-2024:1234   # Red Hat Security Advisory
secid:advisory/debian.org/dsa#DSA-5678-1          # Debian Security Advisory
secid:advisory/ubuntu.com/usn#USN-6789-1          # Ubuntu Security Notice
```

**Why "advisory" instead of "vulnerability"?**

A vulnerability doesn't exist without a description. The CVE Record IS what defines the CVE - there's no platonic vulnerability floating in the ether independent of some advisory describing it. CVE and OSV are "canonical" not because they live in a special namespace, but because other advisories reference them.

**Vendor advisory ID routing:**

For vendors with multiple systems, the ID pattern determines routing:

```yaml
# Entity definition for advisory/redhat namespace
namespace: redhat.com
id_routing:
  - pattern: "CVE-*"
    system: "Red Hat CVE Database"
  - pattern: "RHSA-*"
    system: "Red Hat Security Advisory"
  - pattern: "RHBA-*"
    system: "Red Hat Bug Advisory"
  - pattern: "RHEA-*"
    system: "Red Hat Enhancement Advisory"
```

### 3.2 Weakness

Abstract, recurring flaw patterns - the "what kind of mistake" that underlies vulnerabilities.

```
secid:weakness/mitre.org/cwe#CWE-79               # Cross-site Scripting
secid:weakness/mitre.org/cwe#CWE-89               # SQL Injection
secid:weakness/mitre.org/cwe#CWE-1427             # Prompt Injection
secid:weakness/owasp.org/top10@2021#A03           # Injection (2021)
secid:weakness/owasp.org/llm-top10@2.0#LLM01      # Prompt Injection
```

Multiple advisories can share the same weakness type.

### 3.3 TTP (Tactics, Techniques, Procedures)

Reusable adversary behaviors - how attacks are carried out.

```
secid:ttp/mitre.org/attack#T1059               # Command and Scripting Interpreter
secid:ttp/mitre.org/attack#T1059.003           # Windows Command Shell
secid:ttp/mitre.org/attack#TA0001              # Initial Access (tactic)
secid:ttp/mitre.org/atlas#AML.T0043            # Prompt Injection
secid:ttp/mitre.org/atlas#AML.T0051            # LLM Jailbreak
secid:ttp/mitre.org/capec#CAPEC-66             # SQL Injection attack pattern
```

### 3.4 Control

Security requirements (from frameworks) or capabilities (from vendors).

```
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12              # CSA CCM control
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/audit        # Audit guidance within control
secid:control/cloudsecurityalliance.org/aicm@1.0#INP-01             # CSA AI Controls Matrix control
secid:control/nist.gov/csf@2.0#PR.AC-1            # NIST CSF subcategory
secid:control/cisecurity.org/controls@8.0#1.1            # CIS Control
secid:control/iso.org/27001@2022#A.8.1            # ISO 27001 Annex A control
```

### 3.5 Regulation

Laws, directives, and binding legal requirements.

```
secid:regulation/europa.eu/gdpr                   # GDPR
secid:regulation/europa.eu/gdpr@2016-04-27        # GDPR with version date
secid:regulation/europa.eu/gdpr#art-32            # Article 32
secid:regulation/europa.eu/gdpr#art-32/1/a        # Article 32(1)(a)
secid:regulation/govinfo.gov/hipaa                  # HIPAA
secid:regulation/govinfo.gov/hipaa#164.312/a/1      # Security Rule citation
secid:regulation/govinfo.gov/sox                    # Sarbanes-Oxley
secid:regulation/europa.eu/nis2                   # NIS2 Directive
```

### 3.6 Entity

Organizations, products, services, platforms - stable anchors when PURL/SPDX are unavailable.

```
secid:entity/mitre.org/cve                     # CVE program (operated by MITRE)
secid:entity/mitre.org/cwe                     # CWE taxonomy
secid:entity/mitre.org/attack                  # ATT&CK framework
secid:entity/nist.gov/nvd                      # NVD (operated by NIST)
secid:entity/openai.com/gpt-4                  # GPT-4 product
secid:entity/aws.amazon.com/s3                        # S3 service
secid:entity/redhat.com/rhel                   # RHEL product
```

The namespace is the organization; the name is the specific thing (product, service, system) within that organization. The namespace definition file (e.g., `registry/entity/org/mitre.md`) describes the organization itself.

### 3.7 Reference

Documents, publications, and research that don't fit into other categories. The reference type has a **deliberately narrow scope** to avoid duplicating what other types cover well.

```
secid:reference/whitehouse.gov/eo-14110           # Executive Order on AI
secid:reference/whitehouse.gov/eo-14028           # Cybersecurity Executive Order
secid:reference/whitehouse.gov/m-24-10            # OMB AI Governance Memo
secid:reference/arxiv.org/2303.08774              # GPT-4 Technical Report
secid:reference/arxiv.org/2307.03109              # Jailbroken paper
secid:reference/arxiv.org/2402.05369              # Sleeper Agents paper
```

**What belongs in reference:**
- White House executive orders and policy documents
- Research papers (particularly AI security research on arXiv)
- Primary sources that inform security practices

**What does NOT belong in reference:**
- NIST publications → Use `control/nist.gov/*` for frameworks, entity for systems
- ISO standards → Use `control/iso.org/*`
- OWASP documents → Use `weakness/owasp.org/*`
- Vendor security pages → Use `advisory/*` or `entity/*`

**Reference namespaces (current):**
```
whitehouse.gov  # White House publications (EOs, NSMs, OMB memos)
arxiv.org       # ArXiv preprints (AI/ML security research)
```

Additional namespaces may be added when there's a clear need for documents that genuinely don't fit elsewhere.

**Subpaths:**

```
secid:reference/whitehouse.gov/eo-14110#section-4.1   # Specific section
secid:reference/arxiv.org/2303.08774#appendix-a       # Paper appendix
```

**Note:** Document classification (research paper, position paper, etc.) lives in metadata, not in the identifier.

## 4. Namespaces

Namespaces are **domain names** that identify the organization that issued the identifier. Using domain names enables self-registration via DNS/ACME, scales without a central naming authority, and provides built-in ownership verification.

### 4.0 Namespaces and the Registry

Each type has a directory in the registry. **One file per namespace** contains all sources for that namespace. Namespace domain names are stored using a reverse-DNS directory hierarchy, and platform sub-namespaces append their path after the reversed domain:

```
registry/
├── advisory.md                    # Type definition (what is an advisory?)
├── advisory/                      # Advisory namespaces
│   ├── org/                       # .org TLD
│   │   └── mitre.md               # MITRE: cve source
│   ├── gov/                       # .gov TLD
│   │   └── nist.md                # NIST: nvd source
│   ├── com/                       # .com TLD
│   │   ├── github/                # GitHub platform sub-namespaces
│   │   │   └── advisories.md      # GitHub: ghsa source
│   │   └── redhat.md              # Red Hat: cve, errata, bugzilla sources (ALL IN ONE FILE)
├── weakness.md                    # Type definition (what is a weakness?)
├── weakness/
│   ├── org/
│   │   ├── mitre.md               # MITRE: cwe source
│   │   └── owasp.md               # OWASP: top10, llm-top10, etc. (ALL IN ONE FILE)
├── entity.md                      # Type definition (what is an entity?)
├── entity/
│   ├── org/
│   │   └── mitre.md               # MITRE organization
│   └── com/
│       └── redhat.md              # Red Hat organization
...
```

**Namespace-to-filesystem-path algorithm:**

1. If the namespace contains `/`, split into **domain portion** (before first `/`) and **path portion** (after first `/`)
2. Split the domain portion on `.`
3. Reverse the domain segments
4. Join with `/` to form the directory path
5. If there is a path portion, append it after the reversed domain
6. Append `.md` to the final segment (the file)
7. Prepend `registry/<type>/`

**Examples:**

| Namespace | Step 1: domain / path | Step 2-3: reverse domain | Step 5: append path | Filesystem Path |
|-----------|----------------------|-------------------------|--------------------|----|
| `mitre.org` | `mitre.org` / (none) | `org/mitre` | — | `registry/<type>/org/mitre.md` |
| `aws.amazon.com` | `aws.amazon.com` / (none) | `com/amazon/aws` | — | `registry/<type>/com/amazon/aws.md` |
| `gov.uk` | `gov.uk` / (none) | `uk/gov` | — | `registry/<type>/uk/gov.md` |
| `github.com/advisories` | `github.com` / `advisories` | `com/github` | `com/github/advisories` | `registry/<type>/com/github/advisories.md` |
| `github.com/ModelContextProtocol-Security/vulnerability-db` | `github.com` / `ModelContextProtocol-Security/vulnerability-db` | `com/github` | `com/github/ModelContextProtocol-Security/vulnerability-db` | `registry/<type>/com/github/ModelContextProtocol-Security/vulnerability-db.md` |

For sub-namespaces (containing `/`), only the domain portion is reversed; the sub-namespace path segments are appended as-is. The YAML `namespace:` field in each file remains the canonical namespace (e.g., `namespace: mitre.org` or `namespace: github.com/advisories`).

The namespace file (e.g., `registry/advisory/com/redhat.md`) contains sections for each source with rules for parsing and resolving `#subpath` (e.g., `#CVE-2024-1234` or `#RHSA-2025:1234`).

### 4.1 Domain-Name Namespaces

**Namespace = domain name of the organization, Name = what they publish:**
```
secid:advisory/mitre.org/cve#CVE-2024-1234              # namespace=mitre.org, name=cve
secid:advisory/nist.gov/nvd#CVE-2024-1234               # namespace=nist.gov, name=nvd
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx      # namespace=github.com/advisories, name=ghsa
secid:weakness/mitre.org/cwe#CWE-79                      # namespace=mitre.org, name=cwe
secid:ttp/mitre.org/attack#T1059                         # namespace=mitre.org, name=attack
```

**Why domain names?**

1. **Self-registration** - Domain owners prove ownership via DNS TXT records or ACME-style challenges. No central naming authority needed.
2. **Globally unique** - DNS already solves the namespace collision problem. No risk of two organizations claiming the same name.
3. **Scales without governance** - Adding 10,000 namespaces requires no committee. Domain ownership is self-evident.
4. **Federated management** - Organizations manage their own registry paths via CODEOWNERS.

**Platform sub-namespaces** use `/` to express organizational hierarchy within platforms:
```
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx      # GitHub's advisory database
secid:control/github.com/llm-attacks/advbench#...         # Research project on GitHub
secid:control/github.com/thu-coai/safetybench#...         # Another GitHub-hosted project
```

**Keep names short and recognizable:**
```
cve         # Not "common-vulnerabilities-and-exposures"
cwe         # Not "common-weakness-enumeration"
attack      # Not "att-and-ck" or "adversarial-tactics"
nvd         # Not "national-vulnerability-database"
```

**Framework examples:**
```
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12    # CSA Cloud Controls Matrix
secid:control/cloudsecurityalliance.org/aicm@1.0#INP-01   # CSA AI Controls Matrix
secid:control/nist.gov/csf@2.0#PR.AC-1                    # NIST Cybersecurity Framework
secid:weakness/owasp.org/top10@2021#A03                    # OWASP Top 10
secid:weakness/owasp.org/llm-top10@2.0#LLM01              # OWASP LLM Top 10
```

**For vendors with multiple databases, use different names:**
```
secid:advisory/redhat.com/cve#CVE-2024-1234      # Red Hat CVE database
secid:advisory/redhat.com/errata#RHSA-2024:1234  # Red Hat errata system
secid:advisory/debian.org/dsa#DSA-5678-1         # Debian Security Advisory
secid:advisory/debian.org/dla#DLA-1234-1         # Debian LTS Advisory
```

### 4.2 Namespace Character Rules

Namespaces are domain names, optionally followed by path segments separated by `/`. A namespace has two parts:

1. **Domain portion** (required): a standard domain name (e.g., `github.com`, `mitre.org`)
2. **Path portion** (optional): one or more `/`-separated segments (e.g., `/advisories`, `/ModelContextProtocol-Security/vulnerability-db`)

**Both domain labels and path segments follow the same character rules.** Each segment (whether a DNS label like `github` or a path segment like `advisories`) must match:

`^[\p{L}\p{N}]([\p{L}\p{N}._-]*[\p{L}\p{N}])?$`

**Allowed characters per segment (domain labels and path segments alike):**
- `a-z` (lowercase ASCII letters)
- `0-9` (ASCII digits)
- `-` (hyphen, not at start/end)
- `.` (period, as DNS label separator within domain portion)
- Unicode letters (`\p{L}`) and numbers (`\p{N}`)

**`.` separates labels** within the domain portion (standard DNS). **`/` separates the domain from the path portion**, and separates path segments from each other. Neither `/` nor `.` is interchangeable.

**Not allowed within a segment:** Spaces, punctuation (except `-` and `.`), shell metacharacters.

**Examples:**
```
mitre.org                ✓  Domain name
cloudsecurityalliance.org ✓  Domain name
nist.gov                 ✓  Domain name
github.com/advisories    ✓  Platform sub-namespace (one path segment)
github.com/ModelContextProtocol-Security/vulnerability-db  ✓  Deep sub-namespace (two path segments)
字节跳动.com              ✓  Unicode domain (ByteDance)
aws.amazon.com           ✓  Subdomain
red_hat.com              ✗  Underscore not allowed in segment
```

**Why these rules:**

1. **Filesystem safety** - Namespace segments become file paths (`registry/advisory/org/mitre.md`). Sub-namespaces become directories (`registry/advisory/com/github/advisories.md`). Avoiding shell metacharacters ensures repos work in Git across all platforms.

2. **Domain names are globally unique** - DNS already provides authoritative, collision-free identifiers. No centralized namespace assignment needed.

3. **Ownership is verifiable** - Domain owners can prove ownership via DNS TXT records or ACME-style challenges. Platform users prove ownership via challenge files in their repositories.

4. **Unicode for internationalization** - Organizations worldwide should use native language domain names. Unicode letter/number categories (`\p{L}`, `\p{N}`) include all alphabets while excluding dangerous punctuation and symbols.

### 4.3 Namespace Resolution

When parsing a SecID, the parser must determine where the namespace ends and the name begins. Since namespaces can now contain `/`, the parser uses **shortest-to-longest matching** against the registry:

```
Input: secid:advisory/github.com/advisories/ghsa#GHSA-xxxx

After extracting type "advisory", remaining path is: github.com/advisories/ghsa#GHSA-xxxx

Try namespace matches (shortest first, using reverse-DNS path lookup):
  1. "github.com"              → registry/advisory/com/github.md exists? Yes → candidate
  2. "github.com/advisories"   → registry/advisory/com/github/advisories.md exists? Yes → longer candidate
  3. "github.com/advisories/ghsa" → registry/advisory/com/github/advisories/ghsa.md exists? No → stop

Longest matching namespace: "github.com/advisories"
Remaining: "ghsa#GHSA-xxxx" → name="ghsa", subpath="GHSA-xxxx"
```

**Why shortest-to-longest?** The most authoritative namespace is the shortest one. `github.com` is GitHub itself; `github.com/advisories` is GitHub's advisory team; `github.com/someuser` is a random user. Starting from the shortest prevents namespace hijacking - a malicious user can't register `github.com/evil` and intercept traffic meant for `github.com`.

**Why not reverse DNS order?** Languages like Java use reverse DNS (`com.google.android`) because their `.` separator also appears inside domain names, creating parsing ambiguity. SecID uses `/` as the separator, and domain names **cannot contain `/`** — so `github.com/advisories/ghsa` is unambiguous without reversal. Natural reading order is preserved.

### 4.4 Namespace Governance

- **Currently manual** - Namespace registration is via pull request. Automated self-registration is a planned future feature.
- **Future: DNS/ACME verification** - Domain owners will prove ownership via DNS TXT records or ACME-style challenges. Platform sub-namespace owners will prove control via challenge files.
- **Designed for humans and AI agents** - Registration and maintenance mechanisms (DNS, ACME, challenge files) are machine-friendly by design, enabling AI agents to manage namespaces on behalf of organizations.
- Domain owners manage their registry paths via CODEOWNERS
- Namespaces identify identifier systems, not trust

### 4.5 Namespace Documentation

Each namespace has a documentation file explaining:
- What identifiers it issues
- URLs for lookup/resolution
- How to reference items within documents (subpath conventions)
- Version history and conventions

See Section 8 for the entity registry format used for namespace documentation.

## 5. Versions, Qualifiers, and Subpaths

### 5.1 Source Version (`name@version`)

Pins a specific edition of the source (database, framework, standard) itself. Use version when the **content changes across releases**.

#### When to Use Versions

| Scenario | Use Version? | Example |
|----------|--------------|---------|
| Framework releases | Yes | `@4.0`, `@8.0`, `@2.0` |
| Law publication dates | Yes | `@2016-04-27`, `@2022` |
| Annual updates | Yes | `@2021`, `@2024` |
| Scoring system versions | Yes | `@3.1`, `@4.0` |
| Static IDs that never change | No | CVE IDs don't need versions |

#### Version Format Conventions

**Semantic versions** - for frameworks with numbered releases:
```
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12           # CCM version 4.0
secid:control/cisecurity.org/controls@8.0#1.1         # CIS Controls v8
secid:control/nist.gov/csf@2.0#PR.AC-1         # NIST CSF 2.0
secid:weakness/owasp.org/top10@2021#A03        # OWASP Top 10 2021 edition
secid:weakness/owasp.org/llm-top10@2.0#LLM01   # OWASP LLM Top 10 v2
```

**Date versions** - for laws and dated publications:
```
secid:regulation/europa.eu/gdpr@2016-04-27        # GDPR publication date
secid:regulation/europa.eu/ai-act@2024-08-01      # EU AI Act effective date
secid:regulation/govinfo.gov/hipaa@1996             # Year for older laws
```

**Year versions** - for annual updates:
```
secid:weakness/owasp.org/top10@2021#A01        # 2021 edition
secid:weakness/owasp.org/top10@2017#A01        # 2017 edition (different!)
secid:control/iso.org/27001@2022#A.8.1         # ISO 27001:2022
secid:control/iso.org/27001@2013#A.8.1         # ISO 27001:2013
```

#### Versionless References

When version is omitted, the default behavior is "current" or "latest":
```
secid:control/cloudsecurityalliance.org/ccm#IAM-12               # Current CCM version
secid:advisory/mitre.org/cve#CVE-2024-1234                       # CVE — version irrelevant
```

However, some sources declare `version_required: true` in the registry because unversioned references are ambiguous. OWASP Top 10 is the canonical example — `top10#A01` means "Broken Access Control" in 2021 but "Injection" in 2017. For these sources, when version is omitted the resolver returns all matching versions with disambiguation guidance rather than silently picking one:

```
secid:weakness/owasp.org/top10#A01             # Ambiguous — returns 2021 + 2017 + 2013
                                               # with instructions for determining which
secid:weakness/owasp.org/top10@2021#A01        # Unambiguous — Broken Access Control
```

The registry controls this via three `unversioned_behavior` values: `"current"` (default), `"current_with_history"`, and `"all_with_guidance"`. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) for field definitions.

### 5.1b Item Version (`#subpath@item_version`)

Pins a specific revision of an individual item within a source. Use item version when the **item itself changes over time** independently of the source as a whole.

#### When to Use Item Versions

| Scenario | Use Item Version? | Example |
|----------|-------------------|---------|
| Git-backed advisory databases | Yes | GHSA advisory at a specific commit |
| Advisory revisions | Yes | Red Hat erratum at revision 2 |
| Content that gets updated in place | Yes | Wiki-style entries with edit history |
| Version already baked into the ID | No | arXiv `2303.08774v2` — the `v2` is part of the arXiv ID itself |
| Source already versions as a whole | No | OWASP Top 10 `@2021` — use source version instead |

#### Item Version Format

```
secid:advisory/github.com/advisories/ghsa#GHSA-cxpw-2g23-2vgw@a1b2c3d    # GHSA at specific git commit
secid:advisory/redhat.com/errata#RHSA-2026:3102@rev2                       # Erratum at revision 2
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12@draft               # Control at draft stage (both source and item version)
```

#### How Parsing Works

**This is a key example of why SecID parsing requires the registry.**

The `@` character can appear in subpaths as either a version delimiter or as part of an identifier. The registry's pattern tree resolves this ambiguity:

1. The parser matches the subpath against the source's subpath-level patterns (children in the `match_nodes` tree)
2. The pattern regex defines where the item identifier ends
3. If `@` follows the matched identifier, it's the item version delimiter
4. If a source's IDs legitimately contain `@`, their pattern includes it, and the parser knows it's not a version delimiter

**Example:** GHSA IDs match `^GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$`. This pattern does not include `@`. So in `GHSA-cxpw-2g23-2vgw@a1b2c3d`, the parser matches `GHSA-cxpw-2g23-2vgw` against the pattern, sees the `@` after the match boundary, and extracts `a1b2c3d` as the item version.

#### When NOT to Use Item Versions

**Version already in the ID:** arXiv papers include version numbers as part of their identifier (`2303.08774v2`). The `v2` is part of the arXiv ID, not a SecID item version. The registry's `id_pattern` matches the full `2303.08774v2` string.

```
secid:reference/arxiv.org/papers#2303.08774v2       ← v2 is part of the arXiv ID itself (not @v2)
```

**Source versions the whole thing:** When a framework releases numbered editions (OWASP Top 10 @2021, CCM @4.0), use the source version, not item versions on individual controls.

```
secid:weakness/owasp.org/top10@2021#A01             ← Source version (whole framework is versioned)
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12   ← Source version (framework release)
```

### 5.2 Qualifiers (`?key=value`)

Optional context that doesn't change identity. Qualifiers can appear in two positions:

**Source-level qualifiers** (on the name, before `#`):
```
secid:control/cloudflare.com/waf?surface=api           # API-specific context for the whole source
secid:advisory/nist.gov/nvd?lang=ja#CVE-2024-1234      # Japanese NVD, then the specific CVE
```

**Item-level qualifiers** (on the subpath, after the item):
```
secid:advisory/nist.gov/nvd#CVE-2024-1234?lang=ja      # This specific CVE in Japanese
secid:control/iso.org/27001@2022#A.8.1?format=pdf      # This specific control as PDF
```

**Both positions:**
```
secid:advisory/nist.gov/nvd?format=json#CVE-2024-1234?lang=ja   # JSON API, Japanese translation of this CVE
```

When both positions are present: source-level qualifiers apply to the resolution context, item-level qualifiers apply to the specific item. If the same key appears in both positions, the item-level qualifier takes precedence.

Qualifiers never define identity — two SecIDs differing only in qualifiers refer to the same thing with different context.

### 5.3 Subpath (`#subpath`)

Addressable parts inside the thing. Use subpath to reference **structural components** within a document. Subpaths can use `/` for hierarchical depth.

#### Subpath Conventions by Type

**Regulations - Legal Citations:**
```
# Articles (using / for hierarchy)
secid:regulation/europa.eu/gdpr#art-32            # Article 32
secid:regulation/europa.eu/gdpr#art-32/1          # Article 32, paragraph 1
secid:regulation/europa.eu/gdpr#art-32/1/a        # Article 32(1)(a)
secid:regulation/europa.eu/gdpr#art-32/1/a/ii     # Article 32(1)(a)(ii)

# Chapters and Sections
secid:regulation/europa.eu/gdpr#chapter-4         # Chapter IV
secid:regulation/europa.eu/gdpr#recital-78        # Recital 78

# US Code Style
secid:regulation/govinfo.gov/hipaa#164.312          # 45 CFR 164.312
secid:regulation/govinfo.gov/hipaa#164.312/a/1      # 164.312(a)(1)
secid:regulation/govinfo.gov/hipaa#164.312/a/2/iv   # 164.312(a)(2)(iv)

# Sections
secid:regulation/govinfo.gov/sox#section-302        # Section 302
secid:regulation/govinfo.gov/sox#section-404        # Section 404
```

**Controls - Guidance Sections:**
```
# CCM control guidance (framework is name, control is subpath)
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/audit-guidance
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/implementation-guidance
secid:control/cloudsecurityalliance.org/aicm@1.0#INP-01/Auditing%20Guidelines

# NIST sections
secid:control/nist.gov/csf@2.0#PR.AC-1
secid:control/nist.gov/csf@2.0#PR.AC-1/examples
secid:control/nist.gov/csf@2.0#PR.AC-1/informative-references

# ISO control parts
secid:control/iso.org/27001@2022#A.8.1
secid:control/iso.org/27001@2022#A.8.1/purpose
secid:control/iso.org/27001@2022#A.8.1/guidance
```

**Advisories - Multiple CVEs in One Advisory:**
```
# Red Hat advisory covering multiple CVEs
secid:advisory/redhat.com/errata#RHSA-2024:1234/CVE-2024-1111
secid:advisory/redhat.com/errata#RHSA-2024:1234/CVE-2024-2222
secid:advisory/redhat.com/errata#RHSA-2024:1234/CVE-2024-3333

# Debian advisory sections
secid:advisory/debian.org/dsa#DSA-5678-1/CVE-2024-1234

# GHSA with multiple affected packages
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx-yyyy-zzzz/npm
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx-yyyy-zzzz/pip
```

**Weaknesses - Structural Sections:**
```
# CWE sections
secid:weakness/mitre.org/cwe#CWE-79/extended-description
secid:weakness/mitre.org/cwe#CWE-79/potential-mitigations
secid:weakness/mitre.org/cwe#CWE-79/detection-methods
secid:weakness/mitre.org/cwe#CWE-79/observed-examples

# OWASP Top 10 sections (framework is name, specific item is subpath)
secid:weakness/owasp.org/top10@2021#A03
secid:weakness/owasp.org/top10@2021#A03/description
secid:weakness/owasp.org/top10@2021#A03/how-to-prevent
secid:weakness/owasp.org/top10@2021#A03/example-attack-scenarios
```

**TTPs - Framework Sections:**
```
# ATT&CK technique sections
secid:ttp/mitre.org/attack#T1059/detection
secid:ttp/mitre.org/attack#T1059/mitigation
secid:ttp/mitre.org/attack#T1059/procedure-examples

# Sub-techniques (note: these are names, not subpaths)
secid:ttp/mitre.org/attack#T1059.003                 # This is the ID, not a subpath
secid:ttp/mitre.org/attack#T1059.003/detection       # Section within sub-technique
```

**References - Document Sections:**
```
# Executive orders and policy documents
secid:reference/whitehouse.gov/eo-14110#section-4/1   # AI EO section 4.1
secid:reference/whitehouse.gov/eo-14110#section-4/2   # AI EO section 4.2
secid:reference/whitehouse.gov/m-24-10#appendix-a     # OMB memo appendix

# Research paper sections
secid:reference/arxiv.org/2303.08774#section-3        # GPT-4 paper section
secid:reference/arxiv.org/2307.03109#appendix         # Jailbroken appendix
secid:reference/arxiv.org/2402.05369#methodology      # Sleeper Agents methodology
```

#### Subpath Naming Rules

1. Use lowercase with hyphens: `#implementation-guidance` not `#ImplementationGuidance`
2. Keep it short but descriptive: `#art-32` not `#article-number-32`
3. Mirror source structure when possible: use the document's own section names
4. Preserve upstream IDs: `#CVE-2024-1234` keeps the CVE format

### 5.4 Combined Version, Subpath, and Item Version

Source version, subpath, and item version can be used together:

```
# Source version + subpath (already supported)
secid:regulation/europa.eu/gdpr@2016-04-27#art-32/1/a
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/audit-guidance
secid:weakness/owasp.org/top10@2021#A03/how-to-prevent
secid:control/iso.org/27001@2022#A.8.1/implementation-guidance

# Subpath + item version (new)
secid:advisory/github.com/advisories/ghsa#GHSA-cxpw-2g23-2vgw@a1b2c3d
secid:advisory/redhat.com/errata#RHSA-2026:3102@rev2

# Source version + subpath + item version (both)
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12@draft
```

## 6. Future Layers: Relationships and Overlays

**Identifiers are just identifiers.** This specification defines how to write SecID strings. What you can say *about* SecIDs - relationships between them, enrichments, corrections - belongs in separate data layers.

### Planned Layers

| Layer | Purpose | Status |
|-------|---------|--------|
| **Relationships** | Connect SecIDs (aliases, enriches, mitigates, etc.) | Planned - see [RELATIONSHIPS.md](docs/future/RELATIONSHIPS.md) |
| **Overlays** | Add metadata without modifying sources | Planned - see [OVERLAYS.md](docs/future/OVERLAYS.md) |

### Why Deferred?

These layers involve design decisions that benefit from real-world usage:

- Relationship directionality and cardinality
- Conflict resolution between assertions
- Provenance and authority tracking
- Storage formats and query patterns

Rather than design these upfront, we're building the identifier system and registry first. Usage will inform the data layer design.


## 7. Namespace Definition Format

**Note:** The registry is transitioning from YAML+Markdown to JSON. See [REGISTRY-JSON-FORMAT.md](docs/reference/REGISTRY-JSON-FORMAT.md) for the target JSON schema, including the resolution pipeline, variable extraction, and pattern matching.

During transition, `.md` files are authoritative for contributions. Pilot namespaces have `.json` mirrors derived from the `.md`; JSON parity may lag for non-pilot entries. The examples below show the current YAML format.

### 7.1 Frontmatter (Structured Data)

```yaml
---
# What type this namespace belongs to
type: "advisory"
namespace: "redhat.com"

# Human-readable names
common_name: "Red Hat Security"
full_name: "Red Hat Product Security"

# Resolution
urls:
  website: "https://access.redhat.com/security/"
  api: "https://access.redhat.com/hydra/rest/securitydata"

# ID routing - how to parse and resolve <name> patterns
id_routing:
  - pattern: "CVE-\\d{4}-\\d{4,}"
    system: "Red Hat CVE Database"
    url_template: "https://access.redhat.com/security/cve/{id}"
  - pattern: "RHSA-\\d{4}:\\d+"
    system: "Red Hat Security Advisory"
    url_template: "https://access.redhat.com/errata/{id}"
  - pattern: "RHBA-\\d{4}:\\d+"
    system: "Red Hat Bug Advisory"
    url_template: "https://access.redhat.com/errata/{id}"
  - pattern: "\\d{7}"
    system: "Bugzilla"
    url_template: "https://bugzilla.redhat.com/show_bug.cgi?id={id}"

# Examples
examples:
  - "secid:advisory/redhat.com/cve#CVE-2024-1234"
  - "secid:advisory/redhat.com/errata#RHSA-2024:1234"

status: "active"
---
```

### 7.2 Markdown Body (Rich Context)

The body contains human/AI-readable context:

- **What It Is** - Description of this namespace
- **ID Formats** - Detailed explanation of name patterns
- **Resolution** - How to look up identifiers
- **Caveats** - Important gotchas, edge cases
- **Recent Developments** - Current events, changes

## 8. Parsing and Normalization

### 8.0 Registry-Required Parsing

**SecID parsing requires access to the registry.** This specification is not a standalone grammar you can implement with a regex — it is a guide for building a parser that uses registry data. This is by design.

Rather than defining a complex list of banned characters that users must memorize, the registry itself defines what's valid. If a type, namespace, or name isn't in the registry, it's not a valid SecID. This keeps the parser and registry always in sync.

**Even for unknown SecIDs, the domain name provides a starting point.** Because every namespace is a domain name, encountering a SecID not in the registry is a solvable problem: visit the domain, understand the source, contribute a registry entry. The hosted SecID service, easy contribution model (one file per namespace), and federation support (organizations can run their own registries) mean that unknown SecIDs are a temporary state. The spec teaches you how to build a parser; the registry and ecosystem grow to cover what's out there.

**Parsing algorithm:**

1. **Type** - Match against known list: `advisory`, `weakness`, `ttp`, `control`, `regulation`, `entity`, `reference`
2. **Namespace** - Try shortest-to-longest namespace matches against the registry (see below)
3. **Name** - Match remaining path against source names in `registry[type][namespace]`. **Longest match wins.** Names can contain any characters including `#`, `@`, `?`, `:`.
4. **Source version** - After name match, parse `@...` until `?` or `#`
5. **Source qualifiers** - Parse `?...` until `#`
6. **Subpath** - Everything after the `#` that follows version/qualifiers
7. **Item version** - Match subpath against the source's subpath-level patterns (children in the `match_nodes` tree). If the matched identifier is followed by `@`, extract the remainder as `item_version`. **This is why SecID parsing requires the registry** — the pattern regex determines where the item identifier ends, resolving the ambiguity of `@` in subpaths.
8. **Item qualifiers** - If `?` follows the item version (or the matched identifier if no item version), parse `?...` as item-level qualifiers.

**Namespace resolution (shortest-to-longest):**

Since namespaces are domain names that can include `/` for sub-namespaces, the parser cannot simply split at the first `/` after the type. Instead, it tries progressively longer namespace matches against the registry.

**"Exists in registry" means:** convert the candidate namespace to a filesystem path using the namespace-to-path algorithm (Section 4.0) and check if that file exists. For example, checking whether `github.com/advisories` exists in `registry["advisory"]` means checking whether `registry/advisory/com/github/advisories.md` exists on disk (or in the registry index).

```
Input: secid:advisory/github.com/advisories/ghsa#GHSA-xxxx-yyyy-zzzz

After extracting type "advisory", remaining: github.com/advisories/ghsa#GHSA-xxxx-yyyy-zzzz

Step 2 - Try namespace matches (shortest first):
  "github.com"              → registry/advisory/com/github.md exists? Yes → candidate
  "github.com/advisories"   → registry/advisory/com/github/advisories.md exists? Yes → longer candidate
  "github.com/advisories/ghsa" → registry/advisory/com/github/advisories/ghsa.md exists? No → stop

Winner: namespace = "github.com/advisories"
Remaining: ghsa#GHSA-xxxx-yyyy-zzzz

Step 3 - Name resolution:
  Try "ghsa" against sources in registry/advisory/com/github/advisories.md → match ✓
  name = "ghsa", subpath = "GHSA-xxxx-yyyy-zzzz"
```

**Simple case (no sub-namespace):**

```
Input: secid:advisory/mitre.org/cve#CVE-2024-1234

Step 2 - Namespace:
  "mitre.org"     → registry/advisory/org/mitre.md exists? Yes → candidate
  "mitre.org/cve" → registry/advisory/org/mitre/cve.md exists? No → stop

Winner: namespace = "mitre.org"
Step 3 - Try "cve" against sources in registry/advisory/org/mitre.md → match ✓
  name = "cve", subpath = "CVE-2024-1234"
```

**Why shortest-to-longest?** The shortest matching namespace is the most authoritative. `github.com` is GitHub itself; `github.com/advisories` is a team within GitHub; `github.com/someuser` is a random user. Starting from the shortest and working outward prevents namespace hijacking — a malicious user cannot register `github.com/evil` and intercept parsing meant for `github.com`.

**Why registry-required parsing?**

- No banned character list to memorize
- Registry is the single source of truth
- Parser handles edge cases automatically (including sub-namespaces)
- Human-friendly: names preserve original identifiers exactly

**Example with special characters in name:**

```
secid:advisory/vendor.com/some#weird:name#ID-2024-001
```

Registry lookup:
1. Type: `advisory` ✓
2. Namespace: `vendor.com` (shortest match in registry["advisory"]) ✓
3. Name: Try sources in that namespace. If `some#weird:name` exists, match it.
4. Subpath: `ID-2024-001`

### 8.1 Preserve Source Identifiers

**Names and subpaths preserve the source's exact identifier format.** This is a core principle.

If Red Hat uses `RHSA-2026:0932` with a colon, we use `RHSA-2026:0932` - not `RHSA-2026-0932` or any sanitized variant. If ATT&CK uses `T1059.003` with a dot, we use `T1059.003`. The identifier in SecID matches exactly what practitioners already know.

**Why preserve exactly?**

1. **Human readability** - Security practitioners recognize `RHSA-2026:0932` instantly. No translation layer needed.
2. **No lossy transformation** - Sanitizing `:` to `-` loses information. What if a source legitimately uses both `RHSA-2026:0932` and `RHSA-2026-0932`?
3. **Follow the source** - The issuing authority decided on the format. We defer to them.
4. **Searchability** - Copy `RHSA-2026:0932` from SecID, paste into search - it works.

**Examples of preserved formats:**

| Source | Identifier Format | SecID |
|--------|-------------------|-------|
| Red Hat errata | `RHSA-2026:0932` (colon separator) | `secid:advisory/redhat.com/errata#RHSA-2026:0932` |
| CVE | `CVE-2024-1234` (dash separator) | `secid:advisory/mitre.org/cve#CVE-2024-1234` |
| ATT&CK | `T1059.003` (dot for sub-technique) | `secid:ttp/mitre.org/attack#T1059.003` |
| ISO controls | `A.8.1` (dots in hierarchy) | `secid:control/iso.org/27001@2022#A.8.1` |
| NIST CSF | `PR.AC-1` (dots and dashes) | `secid:control/nist.gov/csf@2.0#PR.AC-1` |
| Debian | `DSA-5678-1` (dashes) | `secid:advisory/debian.org/dsa#DSA-5678-1` |

**What we normalize vs what we preserve:**

| Component | Normalized? | Rule |
|-----------|-------------|------|
| `type` | Yes | Always lowercase (`advisory` not `Advisory`) |
| `namespace` | Yes | Always lowercase (`mitre.org` not `MITRE.ORG`) |
| `name` | Preserve | Keep source format (`cve` or `CVE` as registered) |
| `subpath` | Preserve | Keep exact source format (`RHSA-2026:0932`) |

### 8.2 String Normalization Summary

- Lowercase type and namespace: `secid:advisory/mitre.org/cve#...`
- Preserve case in name and subpath: `CVE-2024-1234` not `cve-2024-1234`
- Preserve special characters in subpath: `RHSA-2026:0932` not `RHSA-2026-0932`
- Namespace uses only allowed characters (see Section 4.2)
- Names can contain any characters (resolved by registry lookup)

### 8.3 Flexible Input Resolution

**Resolvers SHOULD try multiple interpretations of input to find a registry match.**

In practice, users provide SecIDs in different forms. Someone might copy a URL-encoded string, type the human-readable form, or paste from a system that pre-encoded it. Rather than mandating one input format, resolvers try interpretations until one matches:

**Resolution order (subpath/name):**

1. **Try input as-is** - Most inputs are already in human-readable form
2. **Try percent-decoded** (if input contains `%XX` sequences) - Handles URL-encoded input

**Resolution order (namespace — IDN/Punycode):**

Punycode-encoded domain labels are identified by the `xn--` ACE prefix ([RFC 3492](https://www.rfc-editor.org/rfc/rfc3492), [RFC 5890](https://www.rfc-editor.org/rfc/rfc5890)–5893). Every major language has built-in IDNA support for conversion (Python `idna`, Java `java.net.IDN`, Go `golang.org/x/net/idna`, Rust `idna` crate, JS `URL` API).

1. **Try namespace as-is** - Look up the input form in the registry
2. **If not found and input contains `xn--` labels (Punycode)** - Convert to Unicode, try again
3. **If not found and input is Unicode** - Convert to Punycode, try again

If the resolver hits an **alias stub** (a registry entry with `alias_of` and no sources), it follows the redirect to the canonical namespace. Only one form holds actual records; the other is an alias. See [REGISTRY-FORMAT.md](docs/reference/REGISTRY-FORMAT.md) for alias stub format and [EDGE-CASES.md](docs/reference/EDGE-CASES.md#punycode-vs-unicode-idn-resolution) for full details.

```
Input: "secid:control/cloudsecurityalliance.org/ccm#IAM-12/Auditing%20Guidelines"
  1. Try as-is:   "Auditing%20Guidelines" → no match
  2. Try decoded: "Auditing Guidelines"   → match ✓ → return result

Input: "secid:control/cloudsecurityalliance.org/ccm#IAM-12/Auditing Guidelines"
  1. Try as-is:   "Auditing Guidelines"   → match ✓ → return result

Input: "secid:advisory/redhat.com/errata#RHSA-2026:0932"
  1. Try as-is:   "RHSA-2026:0932"        → match ✓ → return result

Input: "secid:advisory/redhat.com/errata#RHSA-2026%3A0932"
  1. Try as-is:   "RHSA-2026%3A0932"      → no match
  2. Try decoded: "RHSA-2026:0932"        → match ✓ → return result
```

**Why this works:**

- **Registry is the authority.** The registry patterns determine what matches - we're just trying different interpretations of the input.
- **As-is first prevents false matches.** If a source literally uses `%20` in an identifier (unlikely but possible), the as-is match finds it before decoding could misinterpret it.
- **Collision risk is negligible.** A false match would require the registry to have both `Foo Bar` and `Foo%20Bar` as distinct identifiers for different things - essentially impossible in practice.

**Important: Do NOT strip or normalize input beyond decoding.** Quotes, backticks, and other characters might be part of the identifier. If `"Auditing Guidelines"` (with quotes) is the input, try matching it with the quotes first - the registry determines if those quotes are part of the identifier or not.

**Backend storage is an implementation choice.** Since resolvers handle both forms, backends can store whichever is convenient:

| Backend | Stores | Why |
|---------|--------|-----|
| Database | `Auditing Guidelines` (unencoded) | String fields handle spaces natively |
| Filesystem | `Auditing%20Guidelines` (encoded) | Filenames may require encoding |
| KV store | Either | Implementation preference |

**Registry patterns match the human-readable form.** Pattern authors write what they see in the source documentation. A pattern like `^Auditing Guidelines$` matches the literal space. The resolver is responsible for getting input into the form that patterns expect.

### 8.4 Percent Encoding

**Context matters:** The SecID *string* preserves identifiers as-is for human readability. Percent encoding applies when storing or transporting SecIDs in contexts with their own syntax requirements.

| Context | Encoding needed? | Example |
|---------|------------------|---------|
| SecID string (canonical) | No | `secid:advisory/redhat.com/errata#RHSA-2024:1234` |
| Filesystem (as filename) | Yes | `secid%3Aadvisory%2Fredhat%2Ferrata%23RHSA-2024%3A1234` |
| URL query parameter | Yes | `?secid=secid%3Aadvisory%2Fredhat...` |
| JSON value | No (JSON handles it) | `{"secid": "secid:advisory/redhat.com/errata#RHSA-2024:1234"}` |

**Unicode support:** SecID supports full Unicode in names and subpaths. When encoding for filesystem/URL use, non-ASCII characters are percent-encoded as UTF-8 bytes (e.g., `é` → `%C3%A9`).

#### Characters to Encode for Storage/Transport

**SecID Structural Characters** - When embedding a SecID in a URL or filename, encode these:

| Character | Encoded | SecID Meaning |
|-----------|---------|---------------|
| `:` | `%3A` | Scheme separator (`secid:`) |
| `/` | `%2F` | Path separator (type/namespace/name) |
| `@` | `%40` | Version prefix |
| `?` | `%3F` | Qualifier prefix |
| `#` | `%23` | Subpath prefix |
| `%` | `%25` | Encoding escape character |

**URL Reserved Characters** - Per RFC 3986, these have special meaning in URLs and should be encoded:

| Character | Encoded | Notes |
|-----------|---------|-------|
| `&` | `%26` | Query parameter separator |
| `=` | `%3D` | Query key-value separator |
| `+` | `%2B` | Sometimes interpreted as space |
| `;` | `%3B` | Parameter separator |
| `[` | `%5B` | IPv6 address delimiter |
| `]` | `%5D` | IPv6 address delimiter |
| `{` | `%7B` | URI template syntax |
| `}` | `%7D` | URI template syntax |
| `!` | `%21` | Sub-delimiter |
| `'` | `%27` | Sub-delimiter |
| `(` | `%28` | Sub-delimiter |
| `)` | `%29` | Sub-delimiter |
| `*` | `%2A` | Sub-delimiter |
| `,` | `%2C` | Sub-delimiter |

**Filesystem Invalid Characters** - These are invalid in filenames on one or more operating systems:

| Character | Encoded | Invalid On |
|-----------|---------|------------|
| `\` | `%5C` | Path separator on Windows |
| `<` | `%3C` | Windows |
| `>` | `%3E` | Windows |
| `"` | `%22` | Windows |
| `\|` | `%7C` | Windows |
| `*` | `%2A` | Windows |
| `?` | `%3F` | Windows |
| `:` | `%3A` | Windows (except after drive letter) |

**Shell-Sensitive Characters** - These have special meaning in shell environments and should be encoded to prevent unexpected behavior:

| Character | Encoded | Shell Risk |
|-----------|---------|------------|
| `$` | `%24` | Variable expansion |
| `` ` `` | `%60` | Command substitution |
| `!` | `%21` | History expansion (bash) |
| `~` | `%7E` | Home directory expansion |
| `^` | `%5E` | History substitution, regex |
| Space | `%20` | Argument separator |
| Tab | `%09` | Whitespace |
| Newline | `%0A` | Command separator |

**Other Characters to Encode:**

| Character | Encoded | Notes |
|-----------|---------|-------|
| `\`` | `%5C%60` | Backtick (command substitution) |
| `"` | `%22` | Quote character |
| `'` | `%27` | Quote character |

#### Examples

```
A&A-01                    → A%26A-01
INP-01 (Draft)            → INP-01%20%28Draft%29
Price: $100               → Price%3A%20%24100
File[1]                   → File%5B1%5D
{template}                → %7Btemplate%7D
```

#### Summary: When to Encode

**In the SecID string itself:** No encoding required. Write identifiers naturally: `RHSA-2024:1234`, `A&A-01`, `some#name`.

**When storing as filename or embedding in URLs:** Encode these characters for compatibility:

```
Space  &  =  +  ;  [  ]  {  }  !  '  (  )  *  ,
:  /  @  ?  #  %  \  <  >  "  |  $  `  ~  ^
```

Tools should render identifiers human-friendly for display while storing the encoded form.

**Filename encoding:** When using SecIDs as filenames, encode all characters invalid on the target filesystem. For cross-platform compatibility, encode all characters listed above. The full SecID `secid:advisory/mitre.org/cve#CVE-2024-1234` becomes `secid%3Aadvisory%2Fmitre%2Fcve%23CVE-2024-1234` as a filename.

### 8.5 Canonical Form

All SecIDs should normalize to:
```
secid:type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]
```

Display shorthands must expand to canonical form for storage and comparison.

## 9. Design Principles

1. **Identifiers are just identifiers** - Registry defines what exists; relationships and enrichment are separate future layers
2. **Identifier, not locator** - SecID identifies things; resolution is separate
3. **Identity ≠ authority** - Identifiers don't imply trust or correctness
4. **Guidelines, not rules** - Human/AI readable, some messiness OK
5. **PURL compatibility** - Same mental model, similar grammar

### 9.1 The Three Layers

SecID separates concerns into three layers:

| Layer | Purpose | Status |
|-------|---------|--------|
| **Registry** | Defines namespaces, ID patterns, resolution | Current (`registry/`) |
| **Relationships** | Connections between identifiers | Future (see [RELATIONSHIPS.md](docs/future/RELATIONSHIPS.md)) |
| **Overlays** | Corrections, enrichments, warnings | Future (see [OVERLAYS.md](docs/future/OVERLAYS.md)) |

The registry is definitional: "what identifiers exist and how to resolve them." It doesn't track history, state changes, or connections - those will belong in relationship and overlay layers once designed.

## 10. Repository Structure

SecID is a single repository containing specification and registry. **One file per namespace** contains all sources for that namespace:

```
secid/
├── README.md              # Project overview
├── SPEC.md                # This specification
├── DESIGN-DECISIONS.md    # Key decisions and rationale
├── STRATEGY.md            # Adoption and governance
├── ROADMAP.md             # Implementation phases
├── USE-CASES.md           # Concrete examples
├── RELATIONSHIPS.md       # Future layer (exploratory)
├── OVERLAYS.md            # Future layer (exploratory)
├── registry/                    # Namespace definitions
│   ├── advisory.md              # Type definition (what is an advisory?)
│   ├── advisory/                # Advisory namespaces
│   │   ├── org/                 # .org TLD
│   │   │   └── mitre.md         # MITRE: cve
│   │   ├── gov/                 # .gov TLD
│   │   │   └── nist.md          # NIST: nvd
│   │   ├── com/                 # .com TLD
│   │   │   ├── github/          # GitHub platform sub-namespaces
│   │   │   │   └── advisories.md# GitHub: ghsa
│   │   │   └── redhat.md        # Red Hat: cve, errata, bugzilla (ALL IN ONE)
│   ├── weakness.md              # Type definition (what is a weakness?)
│   ├── weakness/
│   │   └── org/
│   │       ├── mitre.md         # MITRE: cwe
│   │       └── owasp.md         # OWASP: top10, llm-top10, etc. (ALL IN ONE)
│   ├── ttp.md                   # Type definition
│   ├── ttp/
│   │   └── org/
│   │       └── mitre.md         # MITRE: attack, atlas, capec (ALL IN ONE)
│   ├── control.md               # Type definition
│   ├── control/
│   │   ├── gov/
│   │   │   └── nist.md          # NIST: csf, 800-53, ai-rmf (ALL IN ONE)
│   │   └── org/
│   │       ├── iso.md           # ISO: 27001, 27002 (ALL IN ONE)
│   │       └── cisecurity.md    # CIS: controls, benchmarks
│   ├── entity.md                # Type definition
│   ├── entity/
│   │   ├── org/
│   │   │   ├── mitre.md         # MITRE organization
│   │   │   └── nist.md          # NIST organization
│   │   └── com/
│   │       └── redhat.md        # Red Hat organization
│   ├── regulation.md            # Type definition
│   ├── regulation/
│   │   └── eu/
│   │       └── europa.md        # EU: gdpr, ai-act, nis2 (ALL IN ONE)
│   ├── reference.md             # Type definition
│   └── reference/
│       └── gov/
│           └── whitehouse.md    # White House: executive orders
└── seed/                  # Seed data for bulk import
    └── *.csv
```

