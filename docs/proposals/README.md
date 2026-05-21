# Proposals

Registry schema changes and significant design additions go through a proposal process. This directory contains proposal documents for review.

## Active Proposals

| Proposal | Status | Date | Summary |
|----------|--------|------|---------|
| [TIMESTAMP-FIELDS.md](TIMESTAMP-FIELDS.md) | Proposed | 2026-03-06 | Per-field `_checked`/`_updated`/`_note` metadata for freshness and verification tracking |
| [ASSERTION-CONTENT-TYPES.md](ASSERTION-CONTENT-TYPES.md) | Under revision | 2026-05-12 | Two new types for the credential/education ecosystem; current discussion is collapsing the design toward fewer types using existing `control` and `reference` |
| [GLOSSARY-DEFINITION-COMPARISON.md](GLOSSARY-DEFINITION-COMPARISON.md) | Accepted | 2026-05-20 | Cross-source term-definition comparison; `subtype: "glossary"` tag on `reference` + dataset-repo for term content (Phase 1), copy into registry for direct API serving (Phase 2) |
| [ENTITY-REGULATION-CONTROL-SPLIT.md](ENTITY-REGULATION-CONTROL-SPLIT.md) | Declined (with rationale) | 2026-05-14 | Three-type split rejected; entity-vs-publication cleanup may be salvaged separately |

## Process

1. Write a proposal document in this directory
2. Open a PR for review and discussion
3. Update status as the proposal progresses: `Proposed` → `Accepted` → `Implemented`
4. Declined proposals stay in the directory with status `Declined` and a brief rationale of why
5. Proposals whose approach was revised mid-stream stay with status `Under revision` or `Approach under revision`, with both the original argument and the revised direction preserved in the document — this serves as decision-record documentation showing how the project analyzes and makes design choices
