# Repository Guidelines

## Project Structure & Module Organization
- `registry/` is the authoritative SecID namespace data, organized by type and reverse-DNS path (for example, `registry/advisory/org/mitre.json`).
- `docs/` contains guides, references, operations notes, and proposals.
- `schemas/` contains OpenAPI and schema artifacts.
- `scripts/` contains maintenance/research tooling; `seed/` contains research inputs (not source of truth).
- `plugins/secid/` and `skills/` contain local plugin and agent assets.

## Build, Test, and Development Commands
This repo is spec-and-data first; there is no single app build.

- `python3 -m json.tool registry/<type>/<tld>/<namespace>.json > /dev/null`: validate edited JSON files.
- `bash scripts/update-counts.sh`: refresh type/namespace counts embedded in docs.
- `python3 scripts/scan-well-known.py --domains cisco.com,github.com`: scan selected domains for well-known files.
- `python3 scripts/scan-mcp-endpoints.py --domains cisco.com,github.com`: probe MCP endpoints and llms.txt MCP/API mentions.

## Coding Style & Naming Conventions
- Use 2-space indentation and double-quoted keys/strings in JSON.
- Keep `match_nodes[].patterns` ECMAScript-compatible and anchored (`^...$`).
- Preserve source identifier formats in subpaths (for example, `RHSA-2026:0932`, `T1059.003`) without normalization.
- Follow reverse-DNS path conventions when adding namespace files.

## Testing Guidelines
- No standalone unit-test suite is required for routine registry edits; validate modified files directly.
- For pattern changes, include safety checks and example coverage per `docs/guides/REGEX-WORKFLOW.md`.
- Verify URL template variable extraction against at least one real identifier example before PR.

## Commit & Pull Request Guidelines
- Use imperative, focused commit subjects (`Add ...`, `Fix ...`, `Update ...`, `Document ...`).
- Keep one logical change per PR and list impacted paths/types.
- Link issues for larger scope changes and include sample SecIDs in PR notes.
- Changes under `registry/**/*.json` on `main` trigger the service dispatch workflow; call that out in review notes when relevant.

## Security & Configuration Tips
- Never commit secrets from local `.env` files.
- Keep GitHub Actions credentials in repo secrets only (for example, `SECID_TO_SERVICE_DISPATCH`).
