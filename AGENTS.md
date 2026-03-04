# Repository Guidelines

## Project Structure & Module Organization
- `registry/` is the source of truth for SecID namespaces and type definitions.
- `registry/<type>.md` describes each type (`advisory`, `weakness`, `ttp`, `control`, `regulation`, `entity`, `reference`).
- `registry/<type>/<tld>/<domain>.md` stores namespace entries (reverse-DNS layout, for example `registry/advisory/org/mitre.md`).
- `docs/` contains guidance and design docs (`guides/`, `reference/`, `operations/`, `explanation/`, `project/`, `future/`).
- `seed/` contains CSV seed datasets used for registry research and expansion.
- `skills/` contains workflow-specific helper guidance.

## Build, Test, and Development Commands
This repo is documentation/data-first and has no local build pipeline.
- `rg --files` lists all tracked files quickly.
- `rg -n 'namespace:' registry/` audits namespace declarations.
- `rg -n 'secid:' registry/ docs/` finds identifier examples and cross-references.
- `ls registry/<type>/<tld>/` verifies namespace placement (example: `ls registry/advisory/org/`).
- Optional (if installed): `markdownlint '**/*.md'` for Markdown style checks.

## Coding Style & Naming Conventions
- Use Markdown for docs and YAML frontmatter + Markdown body for registry files.
- Keep identifiers source-faithful (do not normalize upstream IDs like `RHSA-2026:0932`).
- Use lowercase, domain-based namespaces and reverse-DNS file paths.
- Prefer concise, scannable sections; keep prose instructional.
- Follow existing file naming patterns (`UPPERCASE-WITH-HYPHEN.md` for many docs, lowercase for registry entries by domain).

## Testing Guidelines
- Treat validation as data quality checks:
  - Confirm examples match expected SecID format.
  - Confirm URLs and templates resolve to authoritative sources.
  - Ensure regex/pattern changes reject malformed IDs.
- When editing registry content, check related guidance in `docs/guides/REGISTRY-GUIDE.md` and `docs/guides/REGEX-WORKFLOW.md`.

## Commit & Pull Request Guidelines
- Match existing commit style: short imperative subjects (`Add ...`, `Fix ...`, `Update ...`, `Clarify ...`).
- Keep commits focused to one logical change.
- Open an issue first for non-trivial proposals, then submit a PR.
- PRs should include: purpose, scope, affected paths (for example `registry/control/...`), and any validation notes.
- Link related issues/docs and call out follow-up work explicitly.
