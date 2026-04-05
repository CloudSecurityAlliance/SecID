# SecID v1.0.0 Release Plan

## Decision: Version Alignment

All components go to 1.0.0 simultaneously:

| Component | Current | New | Where |
|-----------|---------|-----|-------|
| SPEC.md | 0.9 | 1.0 | Line 3 |
| schema_version in registry files | "1.0" | "1.0" (keep — it's already right, adding .0.0 to 719 files is churn for no value) |
| SecID-Service package.json | 0.1.0 | 1.0.0 |
| MCP server version | 0.2.0 | 1.0.0 | src/mcp.ts |
| Python SDK | 0.1.0 | 1.0.0 | pyproject.toml |
| TypeScript SDK | 0.1.0 | 1.0.0 | package.json |
| Go SDK | (check) | 1.0.0 | go.mod or const |
| OpenAPI spec | 1.0.0 | 1.0.0 (already correct) |
| JSON Schema | (no version field) | add "version": "1.0.0" |

**schema_version stays "1.0"** — it refers to the registry file format version, not the project version. The format hasn't broken backward compatibility. Changing 719 files is noise.

## Phase 1: Fix SecID Spec Repo Documentation

### 1.1 Version bump
- SPEC.md line 3: "Version: 0.9" → "Version: 1.0"
- SPEC.md line 4: "Status: Public Draft - Open for Comment" → "Status: 1.0 Release"

### 1.2 Stale type counts
Files with wrong type count:

| File | Current | Fix |
|------|---------|-----|
| ROADMAP.md ~line 390 | "All 8 types documented" | "All 10 types documented" |
| ROADMAP.md ~line 389 | "121 namespace definitions" | Update to current count |
| ROADMAP.md ~line 398 | "In progress (121 done)" | Update to current count |
| PRINCIPLES.md | Error message example lists old types | Add capability, methodology |
| registry/README.md | Types table missing methodology | Add methodology row |
| REGISTRY-JSON-FORMAT.md ~line 43 | "7 known values" | "10 known values" |
| docs/guides/YAML-TO-JSON.md | "121 namespaces" | Update count |
| slides/secid-overview.md | Lists 7 types | Update to 10 (or note slides may be separately maintained) |

### 1.3 Stale namespace counts
Run `./scripts/update-counts.sh` to fix CLAUDE.md and README.md automatically.

For other files with hardcoded counts — replace with "700+" or current exact number. Files:
- CLAUDE.md line ~120: "124 namespaces" → remove or update
- README.md "600+" → "700+"

### 1.4 Missing template files
Create _template.md for 5 types that lack them:
- registry/control/_template.md
- registry/entity/_template.md
- registry/regulation/_template.md
- registry/ttp/_template.md
- registry/weakness/_template.md

Base each on the existing advisory/_template.md pattern, adapted for the type's specific fields.

### 1.5 ROADMAP.md update
Mark completed items as done:
- Registry data: 709+ namespaces (not 121)
- REST API + MCP server: Live
- 10 types defined and documented
- JSON Schema and OpenAPI spec created

### 1.6 Commit
One commit: "Release SecID v1.0 — spec, docs, templates"

## Phase 2: Fix SecID-Service

### 2.1 Version bumps
- package.json: "0.1.0" → "1.0.0"
- src/mcp.ts McpServer version: "0.2.0" → "1.0.0"

### 2.2 Stale counts in website
- index.astro: "600+" → "700+"
- index.astro: "661 namespaces" → current count
- These will drift again — consider making them dynamic from the API, or accept they're approximate

### 2.3 Stale counts in MCP descriptions
- "486 CNAs" — still accurate, keep
- "616+" in registry resource description → current count or "700+"

### 2.4 Stale comment in registry.ts
- Line 2: "121 namespaces compiled from..." — update comment

### 2.5 Build, test, commit
- npm test (all 230 must pass)
- Rebuild website
- One commit: "Release SecID-Service v1.0.0"

### 2.6 Deploy
- Upload KV
- Deploy worker

## Phase 3: Fix SecID-Client-SDK

### 3.1 Version bumps
- python/pyproject.toml: "0.1.0" → "1.0.0"
- typescript/package.json: "0.1.0" → "1.0.0"
- go/: check for version constant, update

### 3.2 Commit and push
One commit: "Release SecID-Client-SDK v1.0.0"

## Phase 4: Tag releases

### 4.1 Git tags
```bash
# SecID repo
git tag -a v1.0.0 -m "SecID v1.0 — 10 types, 709+ namespaces, JSON Schema, OpenAPI spec"
git push origin v1.0.0

# SecID-Service repo  
git tag -a v1.0.0 -m "SecID-Service v1.0.0 — full type support, KV-backed resolution, MCP server"
git push origin v1.0.0

# SecID-Client-SDK repo
git tag -a v1.0.0 -m "SecID-Client-SDK v1.0.0 — Python, TypeScript, Go clients"
git push origin v1.0.0
```

### 4.2 GitHub releases (optional)
Create GitHub releases from the tags with changelog summaries.

## Pre-Release Checklist

Before executing, verify:

- [ ] All tests pass in SecID-Service (npm test)
- [ ] Website builds (npm run build in website/)
- [ ] All registry JSON files parse (validate script)
- [ ] Live service resolves correctly (test a few queries)
- [ ] MCP server responds to tool calls
- [ ] SDKs work against live service
- [ ] No uncommitted changes in any repo
- [ ] All repos pushed to origin

## What 1.0 Means

1.0 means:
- **The identifier format is stable.** `secid:type/namespace/name[@version]#subpath` won't change.
- **The 10 types are stable.** We may add more types in the future but won't remove or rename existing ones.
- **The registry JSON format is stable.** Files written today will still be valid.
- **The API response format is stable.** Clients written against 1.0 will continue to work.
- **Registry data will grow.** New namespaces, new capabilities, new sources — but that's additive.

1.0 does NOT mean:
- The registry is "complete" — it will always grow
- Relationships are implemented — that's v2
- Data federation is live — that's v2
- Every cloud service is covered — capability type will grow for years
