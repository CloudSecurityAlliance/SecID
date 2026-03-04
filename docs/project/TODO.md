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

### Resolver and Regex Test Fixture Strategy
**Status:** Planned - start during SecID-Service API development

Current coverage is split across docs:
- `docs/reference/REGISTRY-JSON-FORMAT.md` defines resolver behavior and fields (`match_nodes`, `version_required`, `unversioned_behavior`, `examples`)
- `docs/guides/REGEX-WORKFLOW.md` defines regex authoring and manual testing workflow
- `skills/compliance-testing/` describes compliance-test direction

Current gap:
- ~~`data.examples` are input samples only (not executable input/output fixtures)~~ **Partially addressed:** Structured ExampleObject entries now exist in all 15 JSON registry files (input, variables, url, note fields). These serve as positive test fixtures for resolver conformance. See `REGISTRY-JSON-FORMAT.md` "Examples" section for the schema.
- No canonical fixture set yet for negative/rejection tests or multi-resolution behavior tests
- No fixture extraction tooling yet (to pull structured examples from registry JSON into a test runner)

Need to add:
- Fixture extraction script to collect all structured examples from registry JSON files into a test corpus
- Negative test fixtures (invalid inputs that should be rejected) — these are API-level, not registry-level
- Regex compile checks in resolver runtime (not just generic regex lint)
- Overlap detection checks for sibling patterns (with explicit allow/tie policy)
- Deterministic ordering tests for multiple matches (weight + stable tie-break)
- Version-behavior tests (`version_required`, `current_with_history`, `all_with_guidance`)
- Placeholder/variable expansion tests (`{id}`, `{year}`, custom `variables`)

Open decisions (must be explicit before enforcing CI gates):
- Overlap policy: fail by default vs allow with documented justification
- API result policy: return all matches vs single primary match
- Tie-break policy when weights are equal
- Regex dialect policy for runtime compatibility
- URL health checks: blocking vs non-blocking in CI

**When to revisit:** Before enabling strict resolver conformance gates in CI.

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

### Cross-Source Search Index for KV
**Status:** Deferred — accept N reads for now, optimize later

Cross-source search (`secid:advisory/CVE-2024-1234`) requires checking every namespace in a type to find which children match the identifier. With KV storage, this means reading all ~42 advisory namespace records.

Planned optimization: build a cross-source index into the type-level key. The `advisory` key value would include a mapping of child patterns to namespaces they belong to, so a single KV read returns enough information to identify which namespace(s) to fetch. Example structure:

```json
{
  "namespaces": ["mitre.org", "redhat.com", ...],
  "child_index": [
    {"pattern": "^CVE-\\d{4}-\\d{4,}$", "namespaces": ["mitre.org", "nist.gov", "redhat.com", ...]},
    {"pattern": "^RHSA-\\d{4}:\\d+$", "namespaces": ["redhat.com"]}
  ]
}
```

This turns cross-source from N reads into 1 read (type index) + 1-3 reads (matched namespaces).

**When to revisit:** After KV migration is working. Only matters if cross-source search latency becomes a problem.

### Standalone SecID Plugin
**Status:** Planned

Create a standalone plugin (Claude Code plugin, VS Code extension, etc.) that bundles the SecID MCP server for users who want a local/installable option rather than pointing at the remote MCP server. The remote server at `https://secid.cloudsecurityalliance.org/mcp` works for most users, but a plugin provides:
- Offline access
- Bundled tool descriptions and resources
- Integration with IDE-specific features (e.g., hover-to-resolve SecID strings)
- A presence in plugin marketplaces for discoverability

**When to revisit:** After MCP tool descriptions are enriched and SecID-Client-SDK reference implementations are published.

### SecID-Client-SDK Reference Implementations and Package Publishing
**Status:** Planned

Publish reference SecID client libraries to PyPI (`pip install secid`) and npm (`npm install secid`) for SEO and discoverability. These are thin wrappers around the one-endpoint API — the real value is that people searching "secid" on PyPI/npm find something. The packages should:
- Be single-file, zero-external-dep implementations
- Include CLI mode
- Link back to the MCP server as the primary integration path
- Live in the SecID-Client-SDK repo alongside AI-consumable instructions

**When to revisit:** After MCP server improvements are deployed.

## Completed

- [x] Registry architecture refactoring (one file per namespace)
- [x] ISO 27001/27002 control entry
- [x] CONCERNS.md updates
- [x] CLAUDE.md contributor guidance updates
