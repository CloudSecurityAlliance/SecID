# TODO

Tracking deferred work items for SecID.

## Deferred (Registry in Flux)

### JSON Schema for Registry Validation
**Status:** Deferred until registry format stabilizes

Registry files use YAML frontmatter + Markdown. A formal JSON Schema would enable:
- Automated validation of registry files
- IDE autocompletion for contributors
- CI/CD checks for PRs

Deferring because:
- Registry format is still evolving
- Current state documented in DESIGN-DECISIONS.md
- Manual review sufficient for now

**When to revisit:** After v1.0 registry format is stable.

### Resolution Instructions for Non-Deterministic Systems
**Status:** Deferred - design decision needed

ROADMAP.md mentions "search instructions" for resources without stable URLs:
```yaml
resolution:
  type: search
  instructions: "Search the vendor's security portal for the advisory ID"
  search_url: "https://example.com/security/search?q={id}"
```

Need to:
- Identify namespaces that need this pattern
- Settle on YAML format
- Add examples to registry

**When to revisit:** When adding a namespace that requires search-based resolution.

## Completed

- [x] Registry architecture refactoring (one file per namespace)
- [x] ISO 27001/27002 control entry
- [x] CONCERNS.md updates
- [x] CLAUDE.md contributor guidance updates
