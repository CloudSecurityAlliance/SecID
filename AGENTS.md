# Repository Guidelines

## Project Structure & Module Organization
This is a documentation-first repo. Canonical specs (`README.md`, `SPEC.md`) and rationale (`docs/`) define how SecIDs work, while the authoritative registry lives under `registry/<type>/<tld>/<domain>.md`. For example, `registry/control/gov/nist.md` governs every `secid:control/nist.gov/*`. Keep the JSON mirrors beside each Markdown file in sync (e.g., `registry/control/org/cloudsecurityalliance.json`). Research notes belong in `seed/` CSVs until they are promoted into the registry with provenance comments and concrete SecID examples.

## Build, Test, and Development Commands
- `rg -n 'namespace:' registry/control` — confirm existing namespace patterns before minting new ones.
- `python -m json.tool registry/control/org/cloudsecurityalliance.json` — pretty-print and validate mirrors.
- `rg -n 'TODO' registry` — surface unfinished prose before review.
- `git status -sb` — verify only intentional files are staged.

## Coding Style & Naming Conventions
Open every registry doc with YAML frontmatter bounded by `---` and indent keys with two spaces. Use lower-case reverse DNS namespaces (`mitre.org`, `cloudsecurityalliance.org`) and copy the source name verbatim into the first heading (e.g., `# MITRE Advisory Sources`). Quote SecIDs with backticks so tooling can parse entries such as ``secid:advisory/mitre.org/cve#CVE-2024-1234``. CSV headers stay untouched and rely on snake_case to keep ingestion scripts stable.

## Testing Guidelines
No automated suite exists, so manually resolve every SecID URL, regex, and lookup workflow before merging. When editing `seed/` rows, confirm the same coverage is not already represented in `registry/` and promote authoritative material with references plus sample SecIDs. Rerun focused `rg` checks anytime you add namespaces or placeholders.

## Commit & Pull Request Guidelines
Ensure commits are small, single-purpose, and use imperative subjects such as `Add CSA CCM sources`. Pull requests must link related issues, summarize any new namespaces or files, note which artifacts changed (Markdown, JSON, CSV), and cite source URLs reviewers can verify. Include screenshots only when UI output materially changes.

## Security & Provenance Tips
Cite the authoritative source, URL, and publication date inside each registry entry. Before shipping, confirm mirrors and Markdown both resolve remotely, include at least one working `secid:` example, and capture any restrictions or licensing notes in the provenance block.
