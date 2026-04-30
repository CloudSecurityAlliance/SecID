# Repository Guidelines

## Project Structure & Module Organization
`registry/` is the source of truth for SecID namespaces and resolution rules, stored as JSON by type (`advisory`, `control`, etc.) and reverse-DNS path (for example, `registry/advisory/org/mitre.json`).  
`docs/` contains guides, reference material, operations notes, and proposals.  
`scripts/` contains maintenance and research automation (Python, shell, and JS utilities).  
`schemas/` holds schema and API definitions; `seed/` holds research CSV inputs (not authoritative registry data).  
`plugins/secid/` and `skills/` contain agent/plugin-specific assets.

## Build, Test, and Development Commands
This repository is data/docs-first; there is no single app build target.

- `python3 -m json.tool registry/<type>/<tld>/<file>.json > /dev/null` validates edited JSON.
- `python3 scripts/scan-well-known.py --domains cisco.com,github.com` scans well-known files for selected domains.
- `python3 scripts/scan-mcp-endpoints.py --domains cisco.com,github.com` checks live MCP endpoints and llms.txt mentions.
- `bash scripts/update-counts.sh` refreshes namespace counts used in project docs.

## Coding Style & Naming Conventions
Use 2-space indentation in JSON, double quotes, and stable key ordering consistent with nearby files.  
Regex in `match_nodes[].patterns` must be ECMAScript-compatible and anchored with `^...$`.  
Preserve upstream identifier formats in subpaths (for example, `RHSA-2026:0932`, `T1059.003`) without normalization.  
Follow reverse-DNS naming and file placement conventions for namespaces.

## Testing Guidelines
There is no standalone unit test suite in this repo today; validation is done per change.  
Before opening a PR, verify JSON parsing, example/pattern alignment, and URL template variable extraction.  
For regex changes, include ReDoS and ECMAScript compile checks in PR notes, following `docs/guides/REGEX-WORKFLOW.md`.

## Commit & Pull Request Guidelines
Follow the existing imperative commit style: `Add ...`, `Fix ...`, `Update ...`, `Document ...`.  
Keep one logical change per PR and include clear scope, impacted paths, and representative SecID examples.  
Discuss larger changes in an issue first (per `CONTRIBUTING.md`).  
If editing `registry/**/*.json`, note that merge to `main` triggers a SecID-Service dispatch workflow.

## Security & Configuration Tips
Do not commit secrets from local `.env` files.  
Repository dispatch uses the GitHub secret `SECID_TO_SERVICE_DISPATCH`; keep credential handling in Actions secrets only.
