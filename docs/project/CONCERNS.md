# Open Concerns

## [RESOLVED] Entity Structure vs. README Claim
**Status: Resolved**

The registry architecture has been documented in DESIGN-DECISIONS.md ("Registry Architecture: Hierarchical, One File Per Namespace"). The new architecture uses:
- One file per namespace (e.g., `registry/advisory/com/redhat.md`)
- Sources as sections within that file
- No subdirectories for individual sources

README.md, SPEC.md, and CLAUDE.md have been updated to reflect this architecture.

## [RESOLVED] Bare `secid:entity/<namespace>` Identifiers
**Status: Resolved**

The architecture documentation explains that bare namespace identifiers are valid:
- `secid:entity/redhat` refers to Red Hat as an organization
- `secid:entity/redhat/rhel` refers to a specific product/sub-entity

This pattern is documented in:
- DESIGN-DECISIONS.md (architecture overview)
- registry/entity.md (detailed guidance on when to use bare vs. full identifiers)

## Registry Front-Matter Schema Is Unspecified
**Status: Deferred**

DESIGN-DECISIONS.md now includes a detailed namespace file format example showing:
- Required fields: `type`, `namespace`, `full_name`, `operator`, `status`, `sources`
- Each source requires: `full_name`, `urls`, `id_pattern` or `id_patterns`, `examples`
- Optional fields: `versions`, `description`

JSON Schema creation deferred until registry format stabilizes. See TODO.md for details.

## Resolution Instructions for Non-Deterministic Systems
**Status: Deferred**

- ROADMAP.md:101-108 promises "search instructions" when no stable URL exists.
- No namespace currently demonstrates a `resolution` block or equivalent structure.
- Before adding such systems we should settle the YAML format (e.g., `resolution: type: search ...`).

Deferred until we encounter a namespace that requires search-based resolution. See TODO.md for details.

## [RESOLVED] ISO 27001 Example Without Registry Entry
**Status: Resolved**

Created `registry/control/org/iso.md` with comprehensive coverage of:
- ISO/IEC 27001 Information Security Management (with 2022 and 2013 versions)
- ISO/IEC 27002 Information Security Controls

The flagship example `secid:control/iso/27001@2022#A.5.1` now resolves to a real registry entry.
