# How to Convert YAML Registry Files to JSON

> **Status:** Stub — outline only. Contributions welcome.

This guide covers the process of converting registry files from the current YAML+Markdown format to the target JSON format.

## When to Create a .json File

Not every registry file needs a JSON counterpart yet. Create one when:

- The YAML file is `active` status and well-researched
- You need to validate the JSON schema against real data
- The namespace is a pilot for the v1.0 format

All namespaces have been converted to JSON (100% coverage):

| Type | Count |
|------|-------|
| Advisory | 42 |
| Weakness | 13 |
| TTP | 4 |
| Control | 24 |
| Regulation | 4 |
| Reference | 21 |
| Entity | 13 |

## Lifecycle Stages

```
draft .md → active .md → create .json mirror → validate → .json becomes authoritative (v1.0+)
                                  ▲
                          we are here (v1.0)
```

During transition, the `.md` file remains authoritative. The `.json` is a derived mirror. The flip to ".json becomes authoritative" has not happened yet — that is a v1.0+ milestone.

## Field Migration Table

| YAML Field | JSON Field | Notes |
|------------|-----------|-------|
| `title` / `full_name` | `official_name` | Use the source's official name |
| `website` | `urls[]` | Array of URL objects with `type` and `url` |
| `sources` (flat) | top-level `match_nodes` (nested tree) | Convert flat source patterns into nested `match_nodes` |
| `id_pattern` | `match_nodes[].pattern` | Move into tree nodes |
| `url_template` | `match_nodes[].url_template` | Move into tree nodes |
| `description` | `description` | Preserve as-is |

See [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) for the complete schema.

## Conversion Process

### Step 1: Read the YAML file thoroughly

Understand all sources, patterns, and URL templates before converting.

### Step 2: Create the JSON structure

Start with the top-level fields: `schema_version`, `type`, `namespace`, `official_name`, `status`, `urls`.

### Step 3: Convert sources to match_nodes

The biggest structural change: flat `id_pattern` lists become nested `match_nodes` trees. Each node can have children for hierarchical ID systems.

### Step 4: Validate

- JSON parses without errors: `python -m json.tool <file>.json`
- All fields match the schema in [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md)
- Examples resolve correctly through the pattern tree

### Step 5: AI-Assisted Review

Use the conversion review prompt for systematic checking:

```bash
# The prompt is at:
cat registry/CONVERSION-REVIEW-PROMPT.md
```

This prompt guides AI review of field mapping, pattern correctness, and completeness.

## Re-sync Process

When updating a namespace that has both `.md` and `.json`:

1. Edit the `.md` file first (it's authoritative)
2. Update the `.json` to match
3. Verify both files tell the same story

## See Also

- [REGISTRY-FORMAT.md](../reference/REGISTRY-FORMAT.md) - Current YAML+Markdown format (source)
- [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) - Target JSON schema (destination)
- `registry/CONVERSION-REVIEW-PROMPT.md` - AI-assisted review prompt
