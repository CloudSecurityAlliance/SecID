# SecID Registry

Namespace definitions for all SecID types. The directory structure mirrors SecID identifiers.

## Structure

```
registry/
├── <type>.md                    # Type description (e.g., advisory.md)
├── <type>/                      # Namespaces for that type (reverse-DNS layout)
│   └── <tld>/<domain>.md        # Organization namespace definition
...

# Examples:
registry/advisory/org/mitre.md   → secid:advisory/mitre.org/cve, secid:advisory/mitre.org/nvd
registry/weakness/org/mitre.md   → secid:weakness/mitre.org/cwe
registry/ttp/org/mitre.md        → secid:ttp/mitre.org/attack, secid:ttp/mitre.org/atlas
registry/control/gov/nist.md     → secid:control/nist.gov/csf, secid:control/nist.gov/800-53
```

Each type has:
- A **type.md** file at the root describing the type
- A **type/** directory containing namespace files
- Each namespace file defines all databases/frameworks from that organization

## Types

| Type | Description | Also Contains |
|------|-------------|---------------|
| `advisory` | Publications/records about vulnerabilities | Incident reports (AIID, NHTSA, FDA adverse events) |
| `weakness` | Abstract flaw patterns | |
| `ttp` | Adversary techniques and behaviors | |
| `control` | Security requirements and specifications | Prescriptive benchmarks, documentation standards |
| `capability` | Product security features with configuration, audit, remediation | Cloud provider security settings (AWS, Azure, GCP) |
| `disclosure` | Vulnerability disclosure programs, policies, reporting channels | |
| `regulation` | Laws and binding legal requirements | |
| `entity` | Organizations, products, services, platforms | |
| `reference` | Documents, publications, research | |

**Note:** Some types intentionally contain related concepts (see "Also Contains" column). This allows the spec to evolve based on real usage patterns rather than premature categorization. See DESIGN-DECISIONS.md for the rationale.

## Namespace File Format

Namespace files use YAML frontmatter + Markdown body:

```yaml
---
type: "weakness"
namespace: "mitre.org"
name: "cwe"
full_name: "Common Weakness Enumeration"
operator: "secid:entity/mitre.org/cwe"

urls:
  website: "https://cwe.mitre.org"
  lookup: "https://cwe.mitre.org/data/definitions/{num}.html"

id_pattern: "CWE-\\d+"
examples:
  - "secid:weakness/mitre.org/cwe#CWE-79"
  - "secid:weakness/mitre.org/cwe#CWE-89"

status: "active"
---

# CWE (MITRE)

The canonical software weakness taxonomy...

## Format

secid:weakness/mitre.org/cwe#CWE-NNN

## Resolution

https://cwe.mitre.org/data/definitions/{num}.html
```

The file location `registry/weakness/org/mitre.md` corresponds to `secid:weakness/mitre.org/*` (all MITRE weakness namespaces like CWE).

JSON files support optional per-field metadata (`checked`, `updated`, `note`) for tracking when data was last verified. This extends the null/absent convention — a null value with a `_checked` date tells you *when* the absence was confirmed. See [REGISTRY-JSON-FORMAT.md](../docs/reference/REGISTRY-JSON-FORMAT.md) "Per-Field Metadata" for the full convention.

## Patterns

### Security Tools: Entity + Control

Security tools that provide security checks should be documented in **both** entity and control:

| Type | Purpose | Example |
|------|---------|---------|
| `entity` | What the tool IS | Product description, capabilities, access methods |
| `control` | What security checks it PROVIDES | Specific checks, detections, mappings |

**Example: MCPShark Smart Scan**

```
secid:entity/mcpshark.sh/smart      → The Smart Scan tool itself
secid:control/mcpshark.sh/smart     → Security checks it provides
```

**Entity file** (`registry/entity/sh/mcpshark/smart.md`):
- What the tool is and does
- CLI, API, Dashboard access methods
- CI/CD integration capabilities
- What it scans (MCP servers, AI agents)

**Control file** (`registry/control/sh/mcpshark/smart.md`):
- `#agent-analysis` - Agent security assessment
- `#privilege-escalation-detection` - Finds escalation paths
- `#owasp-mapping` - Maps findings to OWASP LLM Top 10
- `#agent-topology` - Visualizes security relationships

This pattern applies to any security tool with defined checks:
- Vulnerability scanners (Trivy, Grype, Snyk)
- SAST tools (Semgrep, CodeQL)
- AI/MCP scanners (MCPShark Smart Scan)

### Weakness + Control Pairing

Some frameworks define both weaknesses AND controls (like OWASP AI Exchange):

```
secid:weakness/owasp.org/ai-exchange#DIRECTPROMPTINJECTION  → The threat
secid:control/owasp.org/ai-exchange#PROMPTINJECTIONIOHANDLING  → The mitigation
```

Document in both types when the source provides both perspectives.

## Contributing

To add a new namespace:
1. Determine which type it belongs to
2. Identify the organization (namespace)
3. Create or update `registry/<type>/<tld>/<domain>.md`
4. Fill in the frontmatter with resolution info (urls, id_pattern, examples)
5. Add context in the markdown body (format, resolution rules, notes)

**For security tools:** Consider both entity (what it is) and control (what it checks).

