# Registry Guide

This document explains the principles, patterns, and process for contributing to the SecID registry.

For technical details, see:
- [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) - JSON schema, resolution pipeline, variable extraction
- [SPEC.md](../../SPEC.md) - Full SecID specification

## Scope: Labeling and Finding

**SecID is about labeling and finding things. That's it.**

The registry contains:
- **Identity** - What is this thing called?
- **Resolution** - How do I find/access it?
- **Disambiguation** - How do I tell similar things apart?

The registry does NOT contain:
- **Enrichment** - Metadata about the thing (authors, categories, publication dates)
- **Judgments** - Quality assessments, trust scores, recommendations
- **Relationships** - How things connect to each other

## Three Layers

SecID separates concerns into layers:

| Layer | Contains | Example |
|-------|----------|---------|
| **Registry** | Identity, resolution, disambiguation | "CVE is at cve.org, IDs look like CVE-YYYY-NNNNN" |
| **Relationship** | Equivalence, succession, hierarchy | "This DOI and this arXiv ID are the same paper" |
| **Data** | Enrichment, metadata, attributes | "This CVE affects Linux kernel, severity is high" |

When deciding if something belongs in the registry, ask: "Is this needed to **identify**, **find**, or **disambiguate** the thing?" If no, it belongs in another layer.

## Follow the Source

Use names and structures the source uses:

- **Names**: If Red Hat calls it "ROSA", use `rosa`, not `openshift-aws-managed-service`
- **IDs**: If CVE uses `CVE-2024-1234`, use that as the subpath
- **Hierarchy**: If the source has domains/sections, use their structure

Don't invent naming schemes. The source's identifiers are authoritative.

### Preserve Source Identifier Formats

**Subpaths preserve the source's exact identifier format - including special characters.**

If Red Hat uses `RHSA-2026:0932` with a colon, we use `RHSA-2026:0932`. If ATT&CK uses `T1059.003` with a dot, we use `T1059.003`. No sanitization, no transformation.

| Source | Their Format | SecID Subpath |
|--------|--------------|---------------|
| Red Hat errata | `RHSA-2026:0932` | `#RHSA-2026:0932` ✓ (not `#RHSA-2026-0932`) |
| ATT&CK | `T1059.003` | `#T1059.003` ✓ |
| ISO 27001 | `A.8.1` | `#A.8.1` ✓ |
| NIST CSF | `PR.AC-1` | `#PR.AC-1` ✓ |

**Why this matters:**
- Practitioners recognize `RHSA-2026:0932` instantly - no translation needed
- Copy from SecID, paste into search engines - it works
- No information loss from character substitution
- The issuing authority chose the format; we defer to them

## Domain-Name Namespaces

Namespaces are **domain names** of the organizations that publish security knowledge. This enables self-registration, scales without a central naming authority, and provides built-in ownership verification.

**Per-segment validation:** Namespaces may include `/`-separated path segments for platform sub-namespaces. Each segment between `/` must match:

`^[\p{L}\p{N}]([\p{L}\p{N}._-]*[\p{L}\p{N}])?$`

**Allowed characters per segment:**
- `a-z` (lowercase ASCII letters)
- `0-9` (ASCII digits)
- `-` (hyphen, not at start/end)
- `.` (period, as DNS label separator)
- Unicode letters (`\p{L}`) and numbers (`\p{N}`)

**`/` separates segments** within namespaces for platform sub-namespaces.

**Examples:**
```
mitre.org                ✓  Domain name
cloudsecurityalliance.org ✓  Domain name
nist.gov                 ✓  Government domain
github.com/advisories    ✓  Platform sub-namespace (one path segment)
github.com/ModelContextProtocol-Security/vulnerability-db  ✓  Deep sub-namespace (two path segments)
aws.amazon.com           ✓  Subdomain
字节跳动.com              ✓  Unicode domain (ByteDance)
red_hat.com              ✗  Underscore not allowed in segment
```

**Namespace file location:** Namespace files are stored in a reverse-DNS directory hierarchy: `registry/<type>/<tld>/<domain>.md`
- Simple namespace: `registry/advisory/org/mitre.md`
- Sub-namespace: `registry/advisory/com/github/advisories.md` (directory + file)

**Why domain names:**

1. **Self-registration** - Domain owners prove ownership via DNS TXT records or ACME challenges. No central naming authority needed.

2. **Globally unique** - DNS already provides collision-free identifiers. No need for manual arbitration.

3. **Filesystem safety** - Domain names and path segments become file paths. Avoiding shell metacharacters ensures repos work in Git across all platforms.

4. **Unicode for internationalization** - Organizations worldwide should use native language domain names.

## Granularity and Hierarchy

Many sources have hierarchical structure. Use the granularity levels the source provides.

### Example: Cloud Controls Matrix (CCM)

| Level | Example | SecID |
|-------|---------|-------|
| Framework | CCM 4.0 | `secid:control/cloudsecurityalliance.org/ccm@4.0` |
| Domain | Identity & Access Management | `secid:control/cloudsecurityalliance.org/ccm@4.0#IAM` |
| Control | IAM-12 | `secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12` |

### Example: ISO 42001

| Level | Example | SecID |
|-------|---------|-------|
| Standard | ISO 42001 | `secid:control/iso.org/42001` |
| Annex | Annex B | `secid:control/iso.org/42001#B` |
| Section | B.1 | `secid:control/iso.org/42001#B.1` |
| Subsection | B.1.2 | `secid:control/iso.org/42001#B.1.2` |

### Example: GDPR

| Level | Example | SecID |
|-------|---------|-------|
| Regulation | GDPR | `secid:regulation/europa.eu/gdpr` |
| Chapter | Chapter III | `secid:regulation/europa.eu/gdpr#chapter-3` |
| Article | Article 17 | `secid:regulation/europa.eu/gdpr#article-17` |
| Paragraph | Article 17(1) | `secid:regulation/europa.eu/gdpr#article-17-1` |

### Documenting Hierarchy in the Pattern Tree

Each granularity level becomes a child node in the `match_nodes` tree. The tree naturally mirrors the hierarchy — domains as parent-level patterns, controls as children:

```json
"children": [
  {
    "patterns": ["^[A-Z]{2,3}$"],
    "description": "Control domain (e.g., IAM). Contains multiple controls.",
    "data": {
      "type": "domain",
      "known_values": {
        "IAM": "Identity & Access Management",
        "DSP": "Data Security & Privacy Lifecycle Management"
      }
    }
  },
  {
    "patterns": ["^[A-Z]{2,3}-\\d{2}$"],
    "description": "Specific control (e.g., IAM-12). Belongs to a domain.",
    "data": {"type": "control", "url": "https://example.com/control/{id}"}
  }
]
```

**Note:** Patterns should be anchored (`^...$`) to match the complete input at each level. This ensures malformed identifiers are rejected.

Use `known_values` for the domain/category level (finite set) but not for individual controls (open-ended set).

Not every node needs to resolve to a URL. An identifier can be valid for reference purposes even without direct resolution.

### Item-Level Versioning

If your source's items can be versioned independently (e.g., git-backed databases like GHSA, advisory revision histories), add deeper children within subpath-level nodes. This tells parsers what item version formats are valid and how to resolve versioned items:

```json
{
  "patterns": ["^GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$"],
  "description": "GitHub Security Advisory ID",
  "data": {"url": "https://github.com/advisories/{id}"},
  "children": [
    {
      "patterns": ["^[0-9a-f]{7,40}$"],
      "description": "Git commit hash",
      "data": {"url": "https://github.com/github/advisory-database/blob/{item_version}/advisories/github-reviewed/{id}.json"}
    }
  ]
}
```

Most sources don't need item versioning — their items are either immutable (CVE IDs) or versioned at the source level (CCM @4.0). Only add item version children when individual items have independent revision histories.

### Version Requirements and Disambiguation

Some sources reuse item identifiers across versions with different meanings. When this happens, an unversioned SecID is ambiguous and the resolver needs to handle it differently. The registry provides four optional source-level fields to control this behavior.

**When to set `version_required: true`:**
- Item IDs change meaning across versions (OWASP Top 10 `A01` = different weakness in each edition)
- Returning a single version for an unversioned reference would be misleading
- Most sources do NOT need this — the default (`false`) is correct when IDs are unique across versions

**When to set `unversioned_behavior`:**
- `"current"` (default) — IDs are unique or version doesn't matter. No field needed.
- `"current_with_history"` — Current version is a sensible default, but note that other versions exist. Use for actively-maintained frameworks where older versions are still referenced (CCM, ISO 27001).
- `"all_with_guidance"` — Return all matching versions with disambiguation instructions. Use when item IDs are reused across versions with different meanings (OWASP Top 10, any source where numbering restarts per version).

**Writing good `version_disambiguation` text:**

Write as if explaining to an AI agent that has access to the referring document but doesn't know which version was meant. Include:
- How versions are structured (by year, by semantic version, etc.)
- Date-based heuristics ("match the version whose release year is closest to but not after the referring document's publication date")
- Structural differences between versions ("item numbering restarts with each version")
- A sensible fallback ("if no date context is available, use the latest version")

Example:
```
"Versions are released by year. Match the version whose release year is closest to
but not after the referring document's publication date. If no date context is available,
use the latest version (2021). Note: item numbering restarts with each version — A01 in
one version is unrelated to A01 in another."
```

**Populating `versions_available`:**

List all known versions with release dates and status. This helps resolvers and AI agents understand the version landscape:
```yaml
versions_available:
  - version: "2021"
    release_date: "2021-09-24"
    status: current
    note: "Major restructuring from 2017."
  - version: "2017"
    release_date: "2017-11-20"
    status: superseded
    note: "Still widely referenced in existing documentation."
```

See [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) for the complete field definitions and JSON examples.

## Common Patterns

### Security Tools: Entity + Control

Security tools that provide security checks should appear in **both** types:

| Type | Documents | Example |
|------|-----------|---------|
| `entity` | What the tool IS | Product description, capabilities, access methods |
| `control` | What checks it PROVIDES | Specific detections, validations, mappings |

Example: A vulnerability scanner is an entity (`secid:entity/vendor.com/scanner`) and its detection rules are controls (`secid:control/vendor.com/scanner#rule-123`).

### Identifier Systems as Namespaces

Standard identifier systems (DOI, ISBN, arXiv, etc.) are **namespaces**, not fields:

```
secid:reference/doi.org/10.6028/NIST.AI.100-1
secid:reference/isbn.org/978-0-13-468599-1
secid:reference/arxiv.org/2303.08774
```

If a document has multiple identifiers (DOI and arXiv ID for the same paper), the equivalence relationship belongs in the relationship layer, not the registry.

### Frameworks with Weaknesses AND Controls

Some frameworks define both problems and solutions (like OWASP AI Exchange):

```
secid:weakness/owasp.org/ai-exchange#DIRECTPROMPTINJECTION   → The threat
secid:control/owasp.org/ai-exchange#INPUTVALIDATION          → The mitigation
```

Document in both types when the source provides both perspectives.

## Adding to the Registry

### Step 1: Understand the Source

Before adding anything, study how the source is **presented** and how people **use** it:

**Examine the structure:**
- How is the document/framework organized? (chapters, sections, domains, categories)
- What identifier system does it use? (numeric, alphanumeric, hierarchical)
- Are there multiple levels of granularity? (framework → domain → control)
- Does the source have an official ID scheme, or just titles/descriptions?

**Observe real-world usage:**
- How do practitioners actually reference it? ("GDPR Article 17" vs "GDPR Art. 17" vs "right to erasure")
- What granularity levels do people cite? (whole framework, sections, specific items)
- Are there common abbreviations or shorthand? (CCM, CSF, 800-53)
- Do other tools/databases reference it, and how?

**Check for existing patterns:**
- Does the source provide lookup URLs for specific items?
- Is there an API or structured data export?
- Are there official ID patterns documented?

**Document what you find** - this research informs every field in the registry entry.

### Step 2: Decision Tree

1. **Is this security knowledge?** If not, it doesn't belong in SecID.

2. **What type is it?**
   - Publications about vulnerabilities → `advisory`
   - Abstract flaw patterns → `weakness`
   - Adversary techniques → `ttp`
   - Security requirements → `control`
   - Laws and legal requirements → `regulation`
   - Organizations, products, services → `entity`
   - Documents and research → `reference`

3. **Does the namespace exist?**
   - Yes → Add a source to the existing namespace file
   - No → Create a new namespace file

4. **What granularity levels exist?** Document each as a child node in the pattern tree.

### Step 3: Namespace File Location

```
registry/<type>/<tld>/<domain>.md
```

One file per namespace containing all sources from that organization:
- `registry/advisory/com/redhat.md` → Red Hat CVE, errata, bugzilla
- `registry/control/gov/nist.md` → NIST CSF, 800-53, AI RMF

### Step 4: Required Information

For each source, you need:
- **Name**: `official_name`, `common_name` (if different)
- **Resolution**: `urls[]` with lookup templates
- **Recognition**: Pattern tree nodes (`match_nodes` children) for each granularity level
- **Examples**: Representative SecID strings

### Status Progression

| Status | Meaning | Requirements |
|--------|---------|--------------|
| `proposed` | Suggested, minimal info | namespace, type, status, official_name |
| `draft` | Being worked on | Any fields, actively researching |
| `pending` | Awaiting review | All fields present (value, `null`, or `[]`) |
| `published` | Reviewed and approved | Same as pending, reviewed by maintainer |

**Key insight**: `published` means "reviewed", not "complete". Empty arrays and `null` values are valid—they show we looked and couldn't find anything.

Use `status_notes` to explain blockers or gaps:
```json
"status": "draft",
"status_notes": "Waiting for vendor response about official URL"
```

### Using _deferred/

Put partially researched entries in `registry/_deferred/` until they're ready. This keeps the main registry clean while preserving research in progress.

## Quality Standards

### Null vs Absent Convention

| State | Representation | Meaning |
|-------|----------------|---------|
| Has data | `"field": "value"` | We have the information |
| No data exists | `"field": null` | We looked, nothing to find |
| Not researched | field absent | We haven't looked yet |

This lets us track completeness. An absent field signals work to be done.

Optional `_checked`/`_updated`/`_note` suffixes make null values more informative — `"field": null` plus `"field_checked": "2026-03-06"` tells you *when* the absence was confirmed. See [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) "Per-Field Metadata" for the full convention.

### Data Freshness

When creating or updating registry entries, add verification timestamps:

- Set source-level `checked` and `updated` dates
- For null fields, include a `_note` explaining why the value is null (e.g., "redirects to homepage")
- For positive findings with caveats, use `_note` to record validation details

These fields are optional and additive — adoption is incremental, field by field.

### Good Patterns

- **Anchor patterns** with `^...$` to match the complete input at each level (rejects malformed IDs)
- Use PCRE2-compatible regex (safe subset for cross-platform compatibility)
- Include `description` explaining what the pattern matches
- Use `(?i)` prefix for case-insensitive matching on name-level patterns
- Patterns are **format checks**, not validity checks—they recognize structure, not existence
- Use `variables` with `extract` and `format` in node `data` for complex URL building (see REGISTRY-JSON-FORMAT.md)

### Good Descriptions

Explain what and why:
- What kind of thing is this?
- When would someone use it vs alternatives?
- Any quirks or gotchas?

**The rule of thumb:** Is it an object or a class of objects?

- **Describe classes** - Always explain what categories, types, or domains mean (RHSA vs RHBA vs RHEA)
- **Sometimes describe unique objects** - Include hints for important individual items (ISO 27001 vs 42001 deserve titles)
- **Never describe every instance** - Don't describe individual CVEs or advisories

### When to Use known_values

Use `known_values` to enumerate finite, stable value sets:

```json
{
  "patterns": ["^[A-Z]{2,3}$"],
  "description": "Control domain. Contains multiple controls.",
  "data": {
    "type": "domain",
    "known_values": {
      "IAM": "Identity & Access Management",
      "DSP": "Data Security & Privacy Lifecycle Management"
    }
  }
}
```

**Good candidates for known_values:**
- Control framework domains (IAM, DSP, GRC)
- Advisory type prefixes (RHSA, RHBA, RHEA)
- ISO standard numbers with titles (27001, 42001)
- Small, stable category codes

**Not good candidates:**
- Growing or open-ended sets (individual CVEs)
- Self-explanatory values (years, sequential numbers)
- Instance data (specific controls within a domain)

### When to Use lookup_table

Use `lookup_table` when URLs can't be computed from a pattern template — the source uses inconsistent slugs, human-readable paths, or URL structures that changed between entries.

**Good candidates for lookup_table:**
- URLs with human-readable slugs not derivable from the ID (e.g., OWASP LLM Top 10: `LLM01` → `llm01-prompt-injection`, `LLM02` → `llm022025-sensitive-information-disclosure`)
- Sources with inconsistent URL patterns across entries
- Small, finite sets where enumerating every URL is practical

**Not good candidates:**
- URLs that follow a consistent, computable pattern (use the `url` template with variables instead)
- Open-ended or very large sets (thousands of entries)

**Always include `provenance`** — record how you found the URLs, when you verified them, and from what source page. This lets reviewers re-verify the data and future maintainers know where to check for updates.

See [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) for the full schema, examples, and the relationship between `lookup_table`, `known_values`, and `url` templates.

### Why This Isn't Enrichment

Descriptions and known_values walk a line - technically "what is IAM" could be enrichment. We include it because:

1. **Critical for finding** - You can't use `secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12` without knowing what IAM means
2. **Class-level** - We describe categories, not instances
3. **Stable** - Category names rarely change
4. **Aids disambiguation** - Helps distinguish IAM (controls) from IAM (cloud services)

## Self-Registration (Future)

> **Current state:** Namespace registration is manual — submit a pull request. Automated self-registration is a planned future feature.

Domain-name namespaces are designed for eventual decentralized ownership verification. When automated registration is implemented, namespace owners will prove control without a central naming authority. This is designed for both **human operators** and **AI agents acting on behalf of organizations** — an agent managing security operations for a company should be able to register and maintain that organization's namespace programmatically, just as it might manage DNS records or certificates today.

### Domain Owners

Organizations that own a domain will prove namespace ownership via:

1. **DNS TXT record** - Add a TXT record to the domain:
   ```
   _secid.redhat.com  TXT  "secid-verify=<challenge-token>"
   ```

2. **ACME-style challenge** - Place a verification file at a well-known URL:
   ```
   https://redhat.com/.well-known/secid-verify/<challenge-token>
   ```

Either method proves the registrant controls the domain, which maps directly to the namespace (`redhat.com` → `registry/*/com/redhat/**`). These mechanisms are machine-friendly by design — AI agents can perform DNS updates and file placement without human intervention.

### Platform Sub-Namespace Owners

For platform sub-namespaces (e.g., `github.com/username`), the platform user (or their agent) proves control by placing a challenge file in their repository:

```
https://github.com/username/.secid-verify
```

The ownership chain follows left-to-right URL authority delegation:
- `github.com` is owned by GitHub (verified via DNS)
- `github.com/username` is delegated to the GitHub user (verified via repo challenge)
- `github.com/username/project` inherits from the user's namespace

### Ownership Scope

Verified owners manage their own registry paths. Ownership of `redhat.com` grants authority over:
- `registry/advisory/com/redhat.md`
- `registry/entity/com/redhat.md`
- Any future `registry/*/com/redhat/**` files

But NOT over sub-namespaces they don't control (e.g., a third party's `redhat.com/partner` would require separate verification).

## CODEOWNERS

Self-registration integrates with GitHub's CODEOWNERS mechanism for federated management:

```
# registry/*/com/redhat/**         @redhat-security-team
# registry/*/gov/nist/**           @nist-csrc
# registry/*/com/github/advisories/** @github-security
```

This enables:
- **Verified owners review their own files** - Changes to `redhat.com.md` require Red Hat approval
- **Sub-namespace delegation** - `github.com/advisories` can have different owners than `github.com`
- **Scalable governance** - No central bottleneck for reviewing namespace changes

### Pre-Seeding

Before self-registration opens, high-value namespaces should be claimed proactively:

| Priority | Namespaces | Reason |
|----------|-----------|--------|
| Critical | `mitre.org`, `nist.gov`, `cisa.gov` | Core vulnerability infrastructure |
| High | `redhat.com`, `microsoft.com`, `google.com`, `apple.com` | Major CNAs |
| High | `owasp.org`, `iso.org`, `cisecurity.org` | Major frameworks |
| Medium | `europa.eu`, `govinfo.gov` | Regulatory bodies |
| Medium | `doi.org`, `arxiv.org`, `isbn.org` | Identifier systems |

Pre-seeded namespaces are transferred to verified domain owners upon successful self-registration.

## Migration from Short Names

SecID previously used short names for namespaces (`mitre`, `nist`, `redhat`). These have been replaced with domain-name namespaces (`mitre.org`, `nist.gov`, `redhat.com`).

**Why the change:**
- Short names create collision risks at scale (10,000+ namespaces)
- No ownership verification mechanism
- Required a central naming authority

**For the complete old→new mapping**, see [NAMESPACE-MAPPING.md](../reference/NAMESPACE-MAPPING.md).

**Quick reference for common namespaces:**

| Old | New |
|-----|-----|
| `mitre` | `mitre.org` |
| `nist` | `nist.gov` |
| `redhat` | `redhat.com` |
| `github` (advisory) | `github.com/advisories` |
| `github` (entity) | `github.com` |
| `csa` | `cloudsecurityalliance.org` |
| `owasp` | `owasp.org` |
| `iso` | `iso.org` |

## See Also

- [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) - Technical schema specification
- [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md) - Rationale for design choices
- [EDGE-CASES.md](../reference/EDGE-CASES.md) - Domain-name namespace edge cases
- [NAMESPACE-MAPPING.md](../reference/NAMESPACE-MAPPING.md) - Complete short-name to domain-name mapping
- [registry/README.md](../../registry/README.md) - Registry structure overview
