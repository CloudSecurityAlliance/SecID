@AGENTS.md

# Code Review Rules — CloudSecurityAlliance/SecID

This file provides review instructions for automated and agent reviewers (Claude Code Review, GitHub Copilot Code Review, and human/agent reviewers). OpenAI Codex (`codex review` / `codex exec`) reads the matching [`## Code Review Rules`](AGENTS.md#code-review-rules) section in [`AGENTS.md`](AGENTS.md).

Because **merging changes under `registry/**/*.json` to `main` automatically deploys to production** at `secid.cloudsecurityalliance.org` once `Registry CI` passes, every pull request must be checked against the rules below.

## 1. Authority, Provenance, and Marking Guardrails

- **Agent attribution:** Agent-authored commits must end with the trailer `AI-Agent: <Name>`, and agent-authored PR descriptions and review comments must start with `*Agent: <Name> (SecID governing agent)*` (or the contributing agent's role).
- **No self-weakening of gates:** Any PR that modifies `.github/workflows/registry-ci.yml`, `schemas/registry-namespace.schema.json`, `scripts/validate-*.py`, `scripts/check-*.py`, `scripts/*-todo.json` allowlists, `GOVERNANCE.md`, `AGENTS.md`, or `REVIEW.md` must be scrutinized to ensure it does not weaken validation gates or widen authority without an independent cross-vendor review recorded on the PR.
- **No licensed content in public repos:** Content from `dataset-private-laws-regulations-standards` or non-redistributable standards (e.g., ISO/IEC text) must never be committed here.

## 2. JSON Authoritativeness and Schema Compliance

- **`.json` is authoritative:** The live resolver (`SecID-Service`) and all CI gates read only `registry/<type>/<tld>/<domain>.json`. A legacy `.md` file alone is never served. Any PR adding or updating a namespace must update the `.json` file.
- **Filesystem path algorithm:** Verify the file path matches the reverse-DNS algorithm (`registry/<type>/<tld>/<domain>[/<subpath>].json`, e.g., `github.com/advisories` → `registry/advisory/com/github/advisories.json`) and that internal `"type"` and `"namespace"` fields match the path.
- **Schema validity:** Every modified `.json` file must validate cleanly against `schemas/registry-namespace.schema.json` (`python3 scripts/validate-registry-schema.py`).
- **Null vs. absent convention:** In registry data, `null` means *"researched and confirmed empty"* (ideally paired with `_checked` / `_note`), whereas omitting a field means *"not yet researched."* Do not replace researched `null` values with empty strings or drop `_checked` metadata without explanation.

## 3. Pattern Breadth, Canonical Names, and Regex Safety

- **Anchored, safe ECMAScript regexes:** Every `match_nodes[].patterns` entry must be anchored (`^...$`), ECMAScript-compatible (compiled by Cloudflare Workers V8 in `SecID-Service`), and free of catastrophic backtracking (nested ambiguous quantifiers).
- **Pattern breadth gate (`scripts/check-pattern-breadth.py`):**
  - Never allow catch-all patterns (`^.+$`, `^.*$`, `^[a-z0-9-]+$`) without a bounding mechanism; a permissive pattern pollutes cross-source search across the entire registry.
  - Finite sets of 50 values or fewer must be enumerated directly in the regex rather than using `open_pattern: true`.
  - `"open_pattern": true` is permitted **only** when the identifier space is genuinely unbounded (e.g., arbitrary usernames, project keys, paper slugs) — never as a shortcut for an unresearched finite set.
- **Canonical names (`scripts/check-canonical-names.py`):** Every top-level `match_nodes` entry must have a `patterns[0]` that strips to a clean literal (`[A-Za-z0-9_-]`, no dots or slashes). Do not add new entries to `scripts/canonical-names-todo.json` or `scripts/pattern-breadth-todo.json` unless genuinely unavoidable and tracked by an issue.

## 4. Subpath URL Templates and URL Policy

- **Subpath URLs in `data.url` (`scripts/check-url-templates.py`):** Below the top-level source node, resolvers substitute `{id}` and extracted variables into `data.url` **only** — `data.urls[]` is ignored on child nodes. Any child `match_node` that resolves to a per-item URL must place the template in `data.url`.
- **URL scheme policy (`scripts/validate-urls.py`):** All URLs must use `https://` unless the host is explicitly listed in `scripts/http-exception-allowlist.txt`. `javascript:`, `data:`, `file:`, and internal/private network hosts are strictly forbidden.
- **Exact identifier preservation:** Subpath patterns and variable extractions must preserve the upstream authority's exact identifier format (`RHSA-2026:0932`, `T1059.003`, `PR.AC-1`) with no lossy normalization (Principle #7).

## 5. Version Resolution, Examples, and Cross-Repo Lockstep

- **Version resolution fields (`scripts/validate-version-aliases.py`):** When `version_required: true` or `versions_available` is used, verify that `version_disambiguation`, `version_aliases`, and child version nodes are consistent and that every alias target exists.
- **Structured child examples:** Top-level `data.examples` uses bare strings, whereas child-level `data.examples` uses structured `ExampleObject` entries (`{"input": "...", "url": "...", "variables": {...}}`). Verify that every `input` matches its parent node's regex and produces the exact `url` shown — `SecID-Service` auto-generates unit tests (`test/resolver.test.ts`) from these examples on deploy, so a mismatch breaks the deploy pipeline!
- **Cross-repo release train check:** If a PR removes or renames a source/version that is hardcoded in `SecID-Service` tests (`test/resolver.test.ts`, `test/parser.test.ts`) or `SecID-Client-SDK` conformance fixtures (`tests/conformance/fixtures.json`), flag that `SecID-Service` must be updated **first** before merging the registry change here.
- **Type, subtype, and count parity:**
  - Adding or removing namespace `.json` files requires running `./scripts/update-counts.sh` so the `REGISTRY-COUNTS` tables in `AGENTS.md` and `README.md` stay in sync.
  - Changes to `type` or `subtype` values must match `SecID-Service/src/type-registry.ts` (`scripts/validate-type-list.py`, `scripts/validate-subtypes.py`).
