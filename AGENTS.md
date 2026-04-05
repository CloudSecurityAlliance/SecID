# Repository Guidelines

## Project Structure & Module Organization

`registry/` is the core dataset. Top-level files such as `registry/advisory.md` define each SecID type, and namespace entries live under reverse-DNS paths like `registry/advisory/org/mitre.md` or `registry/advisory/com/github/advisories.md`. `docs/` holds contributor guides, reference specs, and operations notes. `seed/` contains research CSVs used to discover candidates; it is not authoritative. `slides/` stores presentation assets, and `.github/workflows/` contains automation such as registry update notifications.

## Build, Test, and Development Commands

This repository does not ship an application build. The normal workflow is document and registry editing plus targeted validation:

- `rg --files registry docs seed` lists the files relevant to a change.
- `git diff -- registry docs` reviews exactly what changed before commit.
- `sed -n '1,160p' registry/<type>/<tld>/<file>.md` spot-checks frontmatter and examples.
- `git log --pretty=format:'%s' -10` samples recent commit style.

If your change affects regex-driven `match_nodes`, follow [docs/guides/REGEX-WORKFLOW.md](/Volumes/MacMiniData/Users/kurt/GitHub/CloudSecurityAlliance/SecID/docs/guides/REGEX-WORKFLOW.md) and record the analyzer or review method in the PR.

## Coding Style & Naming Conventions

Write Markdown in short, direct paragraphs with ATX headings. Preserve source terminology and identifier formats exactly: `RHSA-2026:0932`, `T1059.003`, `A.5.1`. Registry namespaces follow reverse-DNS layout and lowercase file paths. Prefer ASCII unless the source name or domain is genuinely Unicode. Keep examples concrete and aligned with existing registry patterns.

## Testing Guidelines

Testing here is review-driven rather than CI-heavy. For registry changes, verify positive and negative identifier examples, confirm anchored regexes (`^...$`), and check that URLs and variable extraction still match source documentation. Treat `seed/*.csv` as research only; authoritative updates belong in `registry/`.

## Commit & Pull Request Guidelines

Recent commits use short, imperative subjects such as `Add security.txt validation details to Red Hat entity` and `Document regex safety controls and update contributor guidance`. Keep commits narrowly scoped and use one logical change per PR. Open an issue first for substantial additions, link it in the PR, summarize affected paths, and include regex safety notes for pattern changes. Add screenshots only when updating rendered assets such as slides.
