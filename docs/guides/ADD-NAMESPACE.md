# How to Add a New Namespace

> **Status:** Stub — outline only. Contributions welcome.

This guide walks through adding a new namespace to the SecID registry, from initial research to a complete registry file.

## Prerequisites

- Understand SecID types (advisory, weakness, ttp, control, regulation, entity, reference)
- Have a source to register (a database, framework, standard, or authority)
- Read [REGISTRY-GUIDE.md](REGISTRY-GUIDE.md) for principles and patterns

## Step 1: Determine Type and Namespace

Identify which SecID type fits the source. The namespace is always the domain name of the publishing organization (e.g., `mitre.org`, `nist.gov`, `cloudsecurityalliance.org`).

If the source is a sub-project on a platform, use a path namespace (e.g., `github.com/advisories`).

## Step 2: Research the Source

Document before you build:

- Official URLs (website, API endpoints, documentation)
- Identifier formats (what do IDs look like? regex patterns)
- Versioning (does the source have editions/revisions?)
- API availability (programmatic access for resolution)
- Licensing and access (open, paywalled, restricted?)

## Step 3: Compute Filesystem Path

Use the namespace-to-filesystem algorithm:

1. Split namespace at first `/` to get domain and path
2. Split domain on `.` and reverse: `mitre.org` → `org/mitre`
3. Append path portion if present
4. Append `.md`
5. Prepend `registry/<type>/`

Example: `advisory/github.com/advisories` → `registry/advisory/com/github/advisories.md`

See [NAMESPACE-MAPPING.md](../reference/NAMESPACE-MAPPING.md) for the complete mapping reference.

## Step 4: Check if Namespace Already Exists

```bash
# Check if the file already exists
ls registry/<type>/<tld>/<domain>.md

# Check if the namespace appears in any type
rg -l 'namespace: <domain>' registry/
```

If the file exists, add a new source section to it rather than creating a new file.

## Step 5: Create the Registry File

Copy from the appropriate template:

```bash
cp registry/advisory/_template.md registry/<type>/<tld>/<domain>.md
```

Fill in the YAML frontmatter: `title`, `type`, `namespace`, `status`.

## Step 6: Write match_nodes Patterns

Define the pattern tree for identifier matching. Each node needs:

- `pattern`: Anchored regex matching the source's ID format
- `description`: What this identifier represents
- `url_template`: How to resolve to a URL (with `{id}` or extracted variables)

See [REGEX-WORKFLOW.md](REGEX-WORKFLOW.md) for pattern development and testing.
See [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) for the full `match_nodes` schema.

## Step 7: Add Examples

Include at least one concrete SecID example per source:

```
secid:<type>/<namespace>/<name>#<example-id>
  → <resolved-url>
```

## Step 8: Validate

- [ ] URL templates resolve to real pages
- [ ] Regex patterns match all example IDs
- [ ] Regex patterns reject obviously wrong IDs
- [ ] No ReDoS risk in patterns (see [REGEX-WORKFLOW.md](REGEX-WORKFLOW.md))
- [ ] Source-level `checked` and `updated` dates are set
- [ ] Null fields include a `_note` explaining why the value is null

## Step 9: Decide Readiness

- **Ready for registry:** Set status to `draft`, place in `registry/<type>/`
- **Incomplete research:** Place in `registry/_deferred/` for later completion

## See Also

- [REGISTRY-GUIDE.md](REGISTRY-GUIDE.md) - Principles, patterns, and quality standards
- [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) - Target JSON schema
- [REGISTRY-FORMAT.md](../reference/REGISTRY-FORMAT.md) - Current YAML+Markdown format
- [REGEX-WORKFLOW.md](REGEX-WORKFLOW.md) - Pattern development workflow
