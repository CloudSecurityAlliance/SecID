# SecID Design Rationale

This document captures the reasoning behind SecID's design decisions. Not just *what* we're doing, but *why*.

## The Problem We're Solving

Security knowledge is fragmented across dozens of databases, each with its own:
- Identifier format (CVE-2024-1234, GHSA-xxxx-yyyy-zzzz, CWE-79)
- Data model
- API
- Update cadence
- Coverage gaps

There's no way to say "this CVE in NVD is the same as this advisory in GHSA" without manual lookup. Tools can't easily cross-reference. Humans can't easily navigate.

And critically: **AI/ML vulnerabilities present new challenges** - they often don't fit traditional vulnerability models (no specific software version, behavioral rather than code-level), and the rapid pace of AI development creates coverage gaps that existing systems are still working to address.

## Why Not Just Build a Database?

The instinct is to build a unified vulnerability database. We rejected this because:

1. **It's been tried.** Many have attempted to aggregate everything. They all hit the same walls: data licensing, update lag, who's authoritative, maintenance burden.

2. **It fights existing ecosystems.** CVE, NVD, GHSA aren't going away. Building a competitor creates friction, not adoption.

3. **It's the wrong abstraction.** We don't need another database. We need a **phone book** - a way to look up "where is this thing?" and "how does it relate to that thing?"

### The Phone Book Insight

A phone book doesn't store conversations. It stores:
- Names → Numbers (identifiers → locations)
- Relationships (who works where)

SecID is a coordination layer, not a data layer. It tells you where to find things and how they connect. The actual vulnerability data stays in CVE, NVD, GHSA - we just make it navigable.

## Why PURL Format?

This was a key "aha" moment. We started from first principles designing an identifier scheme and kept arriving at something that looked like... PURL.

### The Journey

1. **First attempt**: Simple namespacing like `cve:CVE-2024-1234`
   - Problem: No room for hierarchy, versions, qualifiers

2. **Second attempt**: Custom grammar with separators
   - Problem: Reinventing wheels, bikeshedding on syntax

3. **Realization**: PURL already solved this for packages
   - Type/namespace/name structure
   - Version support
   - Qualifiers for metadata
   - Battle-tested in production

### The Decision

Rather than invent a new format, we adopted PURL's grammar with `secid:` as the scheme:

```
secid:type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]
```

Benefits:
- **Familiar** to anyone who's used PURL
- **Proven** syntax with edge cases already handled
- **Tooling** can be adapted from PURL libraries
- **Legitimacy** by association with established standard

**SecID uses PURL grammar with `secid:` as the scheme.** Just as PURL uses `pkg:`, SecID uses `secid:`. Everything after `secid:` follows PURL grammar exactly: `type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]`.

For actual packages, we don't wrap PURL at all - just use `pkg:` directly. SecID handles the security knowledge that PURL doesn't cover.

## Why "Advisory" Instead of "Vulnerability"?

This was a crucial design decision that emerged from careful analysis.

### The Initial Approach

We started with a distinction:
- `vulnerability` = the defect itself (the canonical anchor)
- `advisory` = publications/records about the defect

This seemed clean: CVE-2024-1234 is "the vulnerability", and NVD's record, GHSA's advisory, and Red Hat's page are all "advisories about" that vulnerability.

### The Problem

But then we realized: **CVE would exist in both namespaces**.

- `secid:vulnerability/cve/CVE-2024-1234` - the vulnerability
- `secid:advisory/mitre.org/cve#CVE-2024-1234` - the CVE Record at cve.org

The CVE Record IS what defines the CVE. It's not just commentary - it's the authoritative publication. So CVE is both a vulnerability identifier AND an advisory.

This creates redundancy and confusion. Every CVE would have two SecIDs pointing to essentially the same thing.

### The Insight

**A vulnerability doesn't exist without a description.**

There is no platonic CVE-2024-1234 floating in the ether independent of the CVE Record that defines it. The advisory IS what creates the vulnerability's identity.

### The Solution: Collapse to Advisory

Everything is an advisory:

```
secid:advisory/mitre.org/cve#CVE-2024-1234        # CVE Record (canonical)
secid:advisory/nist.gov/nvd#CVE-2024-1234        # NVD enrichment
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx-yyyy      # GitHub advisory
secid:advisory/redhat.com/errata#RHSA-2024:1234    # Red Hat advisory
```

CVE and OSV are "canonical" not because they live in a special namespace, but because other advisories reference them. The canonical nature is expressed through **relationships**, not types.

### Benefits of This Approach

1. **No redundancy** - CVE exists once, not twice
2. **Handles multi-vuln advisories** - RHSA-2024:1234 can be `about` multiple CVEs
3. **Correct semantics** - CVE Records ARE publications
4. **Simpler model** - One less type to explain

### What About "The Vulnerability Concept"?

If you need to refer to "the vulnerability as a concept across all advisories", that's what relationships are for:

```
secid:advisory/nist.gov/nvd#CVE-2024-1234 → aliases → secid:advisory/mitre.org/cve#CVE-2024-1234
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx → aliases → secid:advisory/mitre.org/cve#CVE-2024-1234
secid:advisory/redhat.com/cve#CVE-2024-1234 → enriches → secid:advisory/mitre.org/cve#CVE-2024-1234
```

The CVE advisory is the canonical anchor. Everything else relates to it.

## The Eight Types

We arrived at eight types, each answering a different question:

| Type | Question | Examples |
|------|----------|----------|
| `advisory` | "What's known about this vulnerability?" | CVE, NVD, GHSA, vendor pages |
| `weakness` | "What kind of mistake is this?" | CWE, OWASP Top 10 |
| `ttp` | "How do attackers do this?" | ATT&CK, ATLAS, CAPEC |
| `control` | "How do we prevent/detect this?" | CSA CCM, NIST CSF, CIS |
| `disclosure` | "How do I report a vulnerability?" | PSIRT programs, bug bounties, security.txt |
| `regulation` | "What does the law require?" | GDPR, HIPAA, SOX |
| `entity` | "What/who is this?" | Vendors, products, systems |
| `reference` | "What source supports this?" | Research papers, policy documents |

### Why These Eight?

Each type is **semantically distinct** - no overlaps:

- Advisories are publications about vulnerabilities
- Weaknesses are abstract flaw patterns (not instances)
- TTPs are adversary behaviors (not flaws)
- Controls are what you implement (not what's wrong)
- Disclosures are how to report (not the published record)
- Regulations are legal requirements (not voluntary)
- Entities are things that exist (meta-level)
- References are source documents (citations, research, policy)

### Why Not More Types?

We considered:
- `malware` - Deferred; may be addressed by future CTI type
- `tool` - But entity/product handles it
- `standard` - But control covers frameworks, regulation covers laws
- `cti` - Deferred for later; threat intelligence has complex structure

The `reference` type was added specifically for documents that don't fit elsewhere - research papers, executive orders, policy documents that inform but aren't themselves controls or regulations. We deliberately kept its scope narrow (whitehouse, arxiv) to avoid duplicating what other types cover.

Add types only when existing ones can't handle the semantics.

### Intentional Overloading

We deliberately overload types with related concepts to learn what actually needs separation:

| Type | Also Contains | Rationale |
|------|---------------|-----------|
| `advisory` | Incident reports (AIID, NHTSA, FDA) | Both are "something happened" publications |
| `control` | Prescriptive benchmarks (HarmBench, WMDP) | Benchmarks define what to test = requirements |
| `control` | Documentation standards (Model Cards) | Define what information to provide = requirements |

**Why overload instead of creating new types?**

1. **Data-driven decisions** - We don't know what needs separation until we have enough examples
2. **Avoid premature fragmentation** - New types have real costs (documentation, tooling, mental overhead)
3. **Semantic proximity** - If something fits ~80% in an existing type, put it there
4. **Easy to split later** - Moving things out is easier than merging types

**When to create a new type:**

- The overloaded concept has fundamentally different resolution patterns
- Users consistently need to filter it separately
- The semantic overlap drops below ~50%
- We have enough examples to know the new type's boundaries

For example, if incident databases grow significantly different from vulnerability advisories (different ID patterns, different metadata needs, different consumers), we'd consider an `incident` type. Until then, they live in `advisory`.

## Namespace Conventions

### Short Names When Unambiguous

```
secid:advisory/mitre.org/cve#...       # Everyone knows CVE
secid:advisory/github.com/advisories/ghsa#...      # Everyone knows GHSA
secid:weakness/mitre.org/cwe#...       # Everyone knows CWE
secid:ttp/mitre.org/attack#...         # Everyone knows ATT&CK
```

### Longer Names for Disambiguation

```
secid:weakness/owasp.org/top10@2021#... # OWASP Top 10
secid:weakness/owasp.org/llm-top10@2.0#... # OWASP LLM Top 10
secid:control/cloudsecurityalliance.org/ccm@4.0#...      # CSA Cloud Controls Matrix
secid:control/cloudsecurityalliance.org/aicm@1.0#...    # CSA AI Controls Matrix
secid:control/nist.gov/csf@2.0#...    # NIST Cybersecurity Framework
```

### Vendors with Multiple Systems

For vendors with multiple advisory systems, use different names:

```
secid:advisory/redhat.com/cve#CVE-2024-1234       # Red Hat CVE database
secid:advisory/redhat.com/errata#RHSA-2024:1234   # Red Hat errata (advisories)
secid:advisory/redhat.com/bugzilla#2045678        # Bugzilla bug ID
secid:advisory/redhat.com/bugzilla#CVE-2024-1234  # Bugzilla CVE alias
```

Each name (`cve`, `errata`, `bugzilla`) gets its own registry file documenting subpath patterns and resolution rules. Some systems support aliases - Bugzilla accepts both numeric IDs and CVE identifiers.

## Why Obsidian Format?

We chose YAML frontmatter + Markdown body because:

1. **Human readable**: Open any file in a text editor
2. **Machine parseable**: YAML is structured data
3. **Rich content**: Markdown handles explanations, examples, tables
4. **Tooling**: Obsidian, VS Code, GitHub all render it nicely
5. **Git-friendly**: Text diffs work well

### Frontmatter vs Body

- **Frontmatter (YAML)**: Structured fields for programmatic access
- **Body (Markdown)**: Human context - "What it is", "Caveats", "How to use it"

An AI reading this gets both structured data AND rich context.

## The AI-Centric Philosophy

A key course correction during design: **this is for AI, not traditional software alone**.

### What We Removed

Early drafts included fields like:
- `data_quality: "high/medium/low"`
- `access_barriers: ["api_key", "rate_limit"]`
- `freshness: "real-time/daily/weekly"`

We removed these because AI figures this out from context. If the description says "updated daily" or "requires API key", AI understands.

### What We Kept

- **URLs**: Where to get the data
- **Relationships**: How things connect
- **Rationale**: Why this entity matters
- **Caveats**: What people get wrong (AI benefits from this too)

The test: "Does AI need this field to be structured, or can it derive it from text?"

## JSON Schema: Options Over Answers

The target JSON format (see [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md)) embodies the AI-first philosophy in its structure.

### Traditional vs AI-First

Traditional schemas force single values because old software needed deterministic answers:

```json
"lookup_url": "https://example.com/{id}"
```

AI-first schemas provide options with context:

```json
"urls": [
  {"type": "lookup", "url": "https://example.com/{id}", "note": "Human-readable"},
  {"type": "lookup", "url": "https://api.example.com/{id}", "format": "json", "note": "Machine-readable"}
]
```

**Why?** AI can reason about which option fits the current task. Forcing a single "canonical" choice means the schema designer has to guess what users need. Providing options lets the AI adapt.

### Exposing Gaps, Not Hiding Them

The null vs absent convention makes incompleteness visible:
- Absent field = "we haven't researched this"
- `null` = "we looked, nothing exists"
- `[]` = "we looked, list is empty"

This is the opposite of traditional approaches that default missing values to empty strings or zero. Visible gaps:
1. Signal where contribution is needed
2. Expose problems in the security ecosystem
3. Let AI honestly say "I don't have that information"

See [DESIGN-DECISIONS.md](DESIGN-DECISIONS.md) for detailed JSON schema design decisions.

## Future: Relationships and Enrichment

The real value of SecID will come from connecting identifiers - but we're deliberately deferring this.

### Why Relationships Matter (Eventually)

Vulnerability databases are **graphs**, not tables. A CVE:
- Has a CWE weakness type
- Is enriched by NVD with CVSS score
- Has a GHSA with package versions
- Maps to ATT&CK techniques
- Is mitigated by specific controls

Without relationships, you're just maintaining another list. With relationships, you're enabling navigation across the entire security knowledge landscape.

### Why We're Waiting

Designing relationship and enrichment layers requires answering hard questions:
- Directionality (one-way or bidirectional?)
- Provenance (who said this? when?)
- Conflicts (what if sources disagree?)
- Storage format (JSONL? Graph database?)

We could guess at answers, but we'd probably guess wrong. Better to build the identifier system first and let usage inform the data layer design.

See [RELATIONSHIPS.md](../future/RELATIONSHIPS.md) and [OVERLAYS.md](../future/OVERLAYS.md) for exploratory thinking on these future layers.

## Governance Philosophy

### Guidelines, Not Rules

We deliberately chose soft constraints over hard validation:

- ✅ "Namespaces should be short when unambiguous"
- ❌ "Namespaces MUST match regex ^[a-z][a-z0-9-]*$"

Why? Because edge cases exist. Rather than encode every exception, we trust humans (and AI) to use judgment.

### Some Messiness is OK

Perfect data modeling is the enemy of adoption. We accepted that:
- Some entities won't fit cleanly into one type
- Some relationships will be ambiguous
- Some naming will be inconsistent

The goal is "useful enough to navigate", not "formally verified ontology".

## What We're NOT Doing

### Not a Database of Truth

We don't store vulnerability details. We point to where they live.

### Not a CVE Competitor

We're not trying to replace CVE. We're trying to make CVE (and everything else) more navigable.

### Not a Standards Body

We're not going to spend years in committees defining perfect ontologies. Ship something useful, iterate.

### Not Wrapping PURL

For packages, use PURL directly (`pkg:npm/lodash`). SecID handles what PURL doesn't cover.

## Success Criteria

How do we know if this works?

1. **AI can navigate**: Given a CVE, an AI can find related GHSA, CWE, ATT&CK technique, and controls without manual lookup
2. **Humans can understand**: The entity files are genuinely useful documentation
3. **Tools can integrate**: The structured data enables automation
4. **Community contributes**: Others add entities and relationships
5. **AI vulns get tracked**: Eventually, prompt injection and jailbreaks have a home

## Open Questions

Things we haven't fully resolved:

1. **Versioning**: How to handle when entity definitions change?
2. **Conflict resolution**: What if two sources disagree on a relationship?
3. **Automation**: How much can be auto-generated vs manual curation?
4. **Scope creep**: Where do we draw the line on what's "security knowledge"?

These will be answered through use, not upfront design.

