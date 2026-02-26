# Repository Guidelines

## Project Structure & Module Organization
This repo is documentation-first: foundational specs live at the root (`README.md`, `SPEC.md`) with decision records and format docs under `docs/` (`docs/explanation/DESIGN-DECISIONS.md`, `docs/reference/REGISTRY-FORMAT.md`). Authoritative SecID definitions sit under `registry/` with the pattern `registry/<type>/<tld>/<domain>.md`; for example, `registry/control/gov/nist.md` governs every `secid:control/nist.gov/*` entry. JSON mirrors such as `registry/control/org/cloudsecurityalliance.json` must match the Markdown narrative beside them. Research CSVs (`seed/*.csv`) are scratchpads only—promote finalized data into the registry with provenance notes and SecID examples.

## Build, Test, and Development Commands
- `rg -n 'namespace:' registry/control` — inspect precedent namespaces before minting new ones.
- `python -m json.tool registry/control/org/cloudsecurityalliance.json` — pretty-print and validate JSON mirrors.
- `rg -n 'TODO' registry` — ensure drafts are removed prior to submission.
- `git status -sb` — confirm only intended files are staged for review.

## Coding Style & Naming Conventions
Open every registry file with YAML frontmatter wrapped in `---` and indented with two spaces. Use lower-case reverse-DNS namespaces (`mitre.org`, `cloudsecurityalliance.org`) and match Markdown headings to the source name (e.g., `# MITRE Advisory Sources`). Provide at least one concrete SecID example such as ``secid:advisory/mitre.org/cve#CVE-2024-1234``. Quote identifiers with backticks so downstream tooling can parse them. Keep CSV headers unchanged and favor snake_case column names.

## Testing Guidelines
Manually resolve each SecID example you add to confirm URLs, regexes, and lookup text. When editing `seed/` data, verify whether each row already exists in `registry/` to signal authoritative coverage. There is no automated test suite, so rely on targeted `rg` checks and manual validation before opening a PR.

## Commit & Pull Request Guidelines
Follow the existing history: short imperative commit subjects (`Add CSA CCM sources`) and one logical change per commit. In PRs, reference related issues, summarize any new namespaces or documents, state whether Markdown, JSON, or CSV files were touched, and link to external sources for reviewer verification. Screenshots are only needed when UI output is relevant.

## Agent Workflow Tips
Keep `docs/guides/REGISTRY-GUIDE.md`, `docs/reference/REGISTRY-JSON-FORMAT.md`, and `docs/reference/REGISTRY-FORMAT.md` nearby while editing to confirm field-by-field requirements. Prefer creating new files in the correct registry path rather than reshaping existing namespaces unless you are explicitly refactoring them.
