# Methodology Type Implementation Plan

Implements the `methodology` type as the 10th SecID type.

## Repos Affected

| Repo | Changes |
|------|---------|
| **SecID** (spec + registry) | SPEC.md, type definition, registry template, CLAUDE.md, README.md, DESIGN-DECISIONS.md, type-level JSON, POC entries |
| **SecID-Service** | SECID_TYPES, MCP descriptions, website, KV upload, deploy |
| **SecID-Client-SDK** | Python, TypeScript, Go — type lists, docs, examples |

## Phase 1: Spec + Registry (SecID repo)

### 1.1 Update SPEC.md
- Change "nine types" to "ten types" (line 387 and elsewhere)
- Add `methodology` to type list table (after `capability`, before `disclosure`)
- Add `methodology` to every enumeration of types (lines 51, 242, 350, 1142)
- Add methodology examples to format examples section

### 1.2 Create type definition files
- `registry/methodology.md` — type description
- `registry/methodology.json` — type-level JSON metadata
- `registry/methodology/_template.md` — template for new namespace files

### 1.3 Update documentation
- CLAUDE.md — add methodology to type table, update type count references
- README.md — add methodology to type table, update counts, add examples
- DESIGN-DECISIONS.md — add methodology case study to "Type Evolution" section (9→10 split)

### 1.4 Update counts
- Run `./scripts/update-counts.sh`

### 1.5 Initial proof-of-concept entries
- `registry/methodology/gov/nist.json` — IR 8477 with 5 sub-methodologies
- `registry/methodology/org/first.json` — CVSS v4.0
- `registry/methodology/edu/cmu.json` — SSVC v2.0

## Phase 2: Service Update (SecID-Service repo)

### 2.1 Add methodology to SECID_TYPES
- `src/types.ts` — add `"methodology"` to SECID_TYPES array

### 2.2 Update MCP tool descriptions
- `src/mcp.ts` — add methodology section to resolve tool description
- Add methodology examples to lookup tool description
- Update type list strings everywhere (9→10, add "methodology")
- Update describe tool's registry resource description

### 2.3 Update website
- `website/src/pages/index.astro` — change "Nine Types" to "Ten Types", add methodology card
- `website/src/components/Resolver.astro` — add methodology to TYPE_DESCRIPTIONS

### 2.4 Upload and deploy
- Re-upload KV with methodology type data
- Deploy worker

## Phase 3: Client SDK Update (SecID-Client-SDK repo)

### 3.1 Python SDK
- `python/secid_client.py` — update lookup() type docstring to include `methodology`
- `python/README.md` — add methodology example and type table row

### 3.2 TypeScript SDK
- `typescript/src/secid-client.ts` — update lookup() type docstring
- `typescript/README.md` — add methodology example and type table row

### 3.3 Go SDK
- `go/secid.go` — update Lookup() type documentation

## Phase 4: Registry Population (future)

Waves 1-6 as defined in METHODOLOGY-PROCESS.md. ~41 entries across 6 waves.

## Execution Order

1. **SecID repo first** — spec changes, proposal docs, registry files, doc updates
2. **SecID-Service second** — type recognition, MCP descriptions, website, deploy
3. **SecID-Client-SDK third** — SDK updates reference the live service
4. **Registry population fourth** — POC first, then waves 2-6
