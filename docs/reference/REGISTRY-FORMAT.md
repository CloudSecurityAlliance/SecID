# Registry File Format

This document describes the format used for SecID registry files.

## Current Format: YAML + Markdown (Obsidian-style)

Registry files use YAML frontmatter followed by Markdown content. This format is compatible with [Obsidian](https://obsidian.md/) and other knowledge management tools that support frontmatter.

**Why this format for now:**
- Human-readable and easy to author
- Works with existing documentation tools
- Allows rich narrative content alongside structured data
- Facilitates exploration and iteration on the schema

**Future direction:** Once the schema stabilizes, registry data will migrate to JSON for programmatic consumption. See [REGISTRY-JSON-FORMAT.md](REGISTRY-JSON-FORMAT.md) for the target JSON schema specification. The JSON format uses a nested pattern tree (`match_nodes`) instead of the flat `sources`/`id_pattern` structure used in YAML — the data is the same, just restructured for recursive matching. The Markdown narrative content may be retained separately or embedded.

## File Structure

### One File Per Namespace

Each namespace gets a single file containing all its sources, stored in a reverse-DNS directory hierarchy:

```
registry/<type>/<tld>/<domain>.md
```

Examples:
- `registry/advisory/org/mitre.md` - Contains CVE, NVD sources
- `registry/control/gov/nist.md` - Contains CSF, SP 800-53, AI RMF sources
- `registry/weakness/org/owasp.md` - Contains Top 10, ASVS, LLM Top 10 sources

This maps to SecID identifiers:
- `secid:advisory/mitre.org/cve` → defined in `registry/advisory/org/mitre.md`
- `secid:control/nist.gov/csf` → defined in `registry/control/gov/nist.md`

### Basic Structure

```markdown
---
type: advisory
namespace: mitre.org
full_name: "MITRE Corporation"
operator: "secid:entity/mitre"
website: "https://www.mitre.org"
status: active

sources:
  cve:
    full_name: "Common Vulnerabilities and Exposures"
    urls:
      website: "https://www.cve.org"
      lookup: "https://www.cve.org/CVERecord?id={id}"
    id_pattern: "CVE-\\d{4}-\\d{4,}"
    examples:
      - "secid:advisory/mitre.org/cve#CVE-2024-1234"
  nvd:
    full_name: "National Vulnerability Database"
    urls:
      website: "https://nvd.nist.gov"
    examples:
      - "secid:advisory/mitre.org/nvd#CVE-2024-1234"
---

# MITRE Advisory Sources

[Markdown content providing context, history, and notes for AI and human readers]
```

## Frontmatter Fields

### Required Fields

| Field | Description |
|-------|-------------|
| `type` | SecID type: `advisory`, `weakness`, `ttp`, `control`, `regulation`, `entity`, `reference` |
| `namespace` | Organization/source identifier (lowercase, hyphenated) |
| `full_name` | Human-readable name of the namespace operator |

### Common Optional Fields

| Field | Description |
|-------|-------------|
| `operator` | SecID reference to the operating entity |
| `website` | Primary website URL |
| `status` | Registry entry state (see below) |
| `sources` | Map of sources within this namespace |
| `alias_of` | Namespace this entry redirects to (for alias stubs, see below) |

### Alias Stubs

An alias stub is a minimal registry entry that redirects to another namespace. Used for Punycode/Unicode IDN equivalence and other namespace aliases.

```yaml
---
type: advisory
namespace: xn--mnchen-3ya.de
alias_of: münchen.de
---
# Punycode form of münchen.de. See münchen.de for all records.
```

When a resolver encounters an entry with `alias_of`, it follows the redirect to the target namespace and resolves there. Alias stubs have no `sources` block — they exist solely to point resolvers to the canonical entry.

See [EDGE-CASES.md](EDGE-CASES.md#punycode-vs-unicode-idn-resolution) for the full IDN resolution strategy.

### Status Field

The `status` field indicates the state of the **registry entry itself**, not the external source:

| Status | Meaning |
|--------|---------|
| `active` | Entry is current and maintained |
| `draft` | Entry is work-in-progress |
| `superseded` | Entry replaced by another (use `superseded_by` field) |
| `historical` | Kept for reference; source may no longer exist |

### Sources Block

Each source within a namespace can have:

| Field | Description |
|-------|-------------|
| `full_name` | Human-readable name |
| `urls` | Map of relevant URLs (`website`, `lookup`, `api`, `docs`, etc.) |
| `id_pattern` | Regex pattern for valid identifiers |
| `examples` | List of example SecID strings |
| `version` | Current version if applicable |
| `notes` | Additional context |

## URL Templates

The `lookup` URL can include `{id}` as a placeholder for the subpath identifier:

```yaml
urls:
  lookup: "https://www.cve.org/CVERecord?id={id}"
```

This enables resolution: `secid:advisory/mitre.org/cve#CVE-2024-1234` → `https://www.cve.org/CVERecord?id=CVE-2024-1234`

## Markdown Body

The Markdown section after the frontmatter provides:

- **Context** - What this namespace/source is and why it matters
- **History** - How the source evolved
- **Usage notes** - How to interpret or use the identifiers
- **Relationships** - How this relates to other sources
- **Quirks** - Edge cases, known issues, format variations

This content is primarily for AI agents and humans who need to understand the source beyond just the structured data.

## Examples by Type

### Advisory (Vulnerability Publications)

```yaml
---
type: advisory
namespace: github
full_name: "GitHub"
status: active

sources:
  ghsa:
    full_name: "GitHub Security Advisories"
    urls:
      website: "https://github.com/advisories"
      lookup: "https://github.com/advisories/{id}"
    id_pattern: "GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}"
    examples:
      - "secid:advisory/github.com/advisories/ghsa#GHSA-abcd-1234-efgh"
---
```

### Control (Security Requirements)

```yaml
---
type: control
namespace: nist.gov
full_name: "National Institute of Standards and Technology"
status: active

sources:
  csf:
    full_name: "Cybersecurity Framework"
    version: "2.0"
    urls:
      website: "https://www.nist.gov/cyberframework"
    examples:
      - "secid:control/nist.gov/csf@2.0#PR.AC-1"
---
```

### Weakness (Flaw Patterns)

```yaml
---
type: weakness
namespace: mitre.org
full_name: "MITRE Corporation"
status: active

sources:
  cwe:
    full_name: "Common Weakness Enumeration"
    urls:
      website: "https://cwe.mitre.org"
      lookup: "https://cwe.mitre.org/data/definitions/{id}.html"
    id_pattern: "CWE-\\d+"
    examples:
      - "secid:weakness/mitre.org/cwe#CWE-79"
---
```

## File Naming

- Use lowercase
- Namespace `protectai.com` maps to `registry/advisory/com/protectai.md` (domain split on `.`, reversed into directory hierarchy)
- Match the namespace via reverse-DNS: `secid:advisory/protectai.com/...` → `registry/advisory/com/protectai.md`

## Templates

Template files exist in `registry/<type>/_template.md` for each type. Use these as starting points for new entries.

## Deferred Entries

Partially researched or uncertain entries go in `registry/_deferred/` until they're ready for the main registry.
