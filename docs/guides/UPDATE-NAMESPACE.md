# How to Update an Existing Namespace

> **Status:** Stub — outline only. Contributions welcome.

This guide covers common maintenance tasks for existing namespace registry files.

## Adding a New Source to an Existing Namespace

When an organization publishes a new database or framework, add a source section to their existing namespace file rather than creating a new file.

1. Open the namespace file (e.g., `registry/advisory/org/mitre.md`)
2. Add a new source section with YAML frontmatter fields and Markdown documentation
3. Include: `match_nodes` patterns, URL templates, description, examples
4. Follow the same format as existing sources in the file

## Updating URLs That Changed

Sources occasionally change their URL structure.

1. Find the affected `url_template` in the source's `match_nodes`
2. Update to the new URL pattern
3. Verify resolution with existing examples
4. Note the change date and reason in a commit message

## Adding Version Fields for a New Edition

When a framework releases a new version (e.g., OWASP Top 10 2025):

1. Check if the source has `version_required: true`
2. Update `versions_available` to include the new version
3. If the new version changes ID formats, update `match_nodes` patterns
4. Add examples for the new version
5. If the latest version changes meaning of unversioned references, update `version_disambiguation`

See [VERSIONING.md](../reference/VERSIONING.md) for version resolution behavior.

## Promoting Status

Registry files progress through status values:

**Current YAML format:** `draft` → `active`
**Target JSON format:** `proposed` → `draft` → `pending` → `published`

`published` means "reviewed", not "complete". Promote when:
- All required fields are filled in
- At least one example resolves correctly
- Patterns have been tested against real IDs

## Handling Deprecation

When a source is deprecated or superseded:

1. Set status to `superseded` (YAML) or note the supersession
2. Add a note pointing to the replacement source
3. Keep the old entry for historical resolution — don't delete it

## Handling Acquisition or Domain Changes

When an organization changes domains (e.g., acquisition):

1. Create an alias stub at the old namespace pointing to the new one
2. Move the full content to the new namespace file
3. See [EDGE-CASES.md](../reference/EDGE-CASES.md) for domain change patterns

## Syncing .md and .json When Both Exist

Some namespaces have both `.md` (current) and `.json` (pilot) files:

1. The `.md` file remains authoritative during transition
2. After editing `.md`, update the `.json` to match
3. Use `registry/CONVERSION-REVIEW-PROMPT.md` for AI-assisted review
4. See [YAML-TO-JSON.md](YAML-TO-JSON.md) for the conversion workflow

### When to sync

**Sync immediately** when:
- The namespace is a pilot (see [YAML-TO-JSON.md](YAML-TO-JSON.md) for the list)
- Downstream tooling, tests, or runtime consume the `.json` data
- The PR explicitly targets JSON schema or consumer behavior

**Sync can wait** when:
- The `.md` changes are exploratory research or still in flux
- The namespace is not a pilot
- The change is minor (e.g., fixing a typo in narrative content not reflected in JSON)

## See Also

- [REGISTRY-GUIDE.md](REGISTRY-GUIDE.md) - Principles and quality standards
- [REGISTRY-FORMAT.md](../reference/REGISTRY-FORMAT.md) - Current YAML+Markdown format
- [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) - Target JSON schema
