@AGENTS.md

# Code Review Rules — CloudSecurityAlliance/SecID

Review instructions for Claude Code Review, GitHub Copilot Code Review, and human/agent reviewers. OpenAI Codex (`codex review` / `codex exec`) reads the matching [`## Code Review Rules`](AGENTS.md#code-review-rules) section in [`AGENTS.md`](AGENTS.md).

Because **merging changes under `registry/**/*.json` to `main` automatically deploys to production** at `secid.cloudsecurityalliance.org` once `Registry CI` passes (`ci-passed` → `notify-service`), check every PR against these rules:

## 1. Authority, Provenance, and CI Gate Guardrails

- **Agent attribution:** Agent-authored commits must end with `AI-Agent: <Name>`, and agent PR descriptions/comments must start with `*Agent: <Name> (SecID governing agent)*` (or the contributing agent's role).
- **Governance and gate changes (`GOVERNANCE.md`):** Every change to CI gates (`.github/workflows/registry-ci.yml`), required checks (`ci-passed`), branch protection, validator/test scripts (`scripts/validate-*.py`, `scripts/check-*.py`, `scripts/test-*.py`, `scripts/test-*.sh`, `scripts/*-todo.json`), `GOVERNANCE.md`, `AGENTS.md`, or `REVIEW.md` unconditionally requires a different-vendor review and a decision record, and never merges on the authoring agent's review alone. Anything that widens agent authority requires Kurt's approval first.
- **Complete CI pipeline integrity:** Preserve all four blocking gate jobs (`validate-schema`, `validate-subtypes`, `validate-pattern-breadth`, and `tooling-tests` covering `test-update-counts.sh`, `test-validate-type-list.sh`, `test-encoding.py`, `test-secid-complete-sync.sh`), the validator self-tests (`test-validate-schema.py`, `test-validate-subtypes.py`, `test-validate-pattern-breadth.py`), and the fail-closed `ci-passed` aggregation gate that `notify-service` depends on.
- **No licensed content:** Content from `dataset-private-laws-regulations-standards` or non-redistributable standards (e.g., ISO/IEC text) must never enter this public repository.

## 2. JSON Authoritativeness and Schema Compliance

- **`.json` is authoritative:** `SecID-Service` and all CI gates read only `registry/<type>/<tld>/<domain>.json` (`.md` alone is never served).
- **Reverse-DNS path & schema:** Verify path mapping (`registry/<type>/<tld>/<domain>[/<subpath>].json`), internal `"type"` and `"namespace"` parity, and schema validity against `schemas/registry-namespace.schema.json` (`python3 scripts/validate-registry-schema.py`).
- **Null vs. absent convention:** `null` means *"researched and confirmed empty"* (paired with `_checked` / `_note`); omitting a field means *"not yet researched."*

## 3. Pattern Breadth, Canonical Names, and Regex Safety

- **Safe anchored regexes:** Every `match_nodes[].patterns` entry must be anchored (`^...$`), ECMAScript-compatible (Cloudflare Workers V8), and free of catastrophic backtracking.
- **Pattern breadth (`scripts/check-pattern-breadth.py`):** No catch-alls (`^.+$`, `^.*$`, `^[a-z0-9-]+$`); sets ≤ 50 values must be enumerated in the regex; `"open_pattern": true` is allowed **only** for genuinely unbounded identifier spaces.
- **Canonical names (`scripts/check-canonical-names.py`):** Top-level `match_nodes` `patterns[0]` must strip to `[A-Za-z0-9_-]` (no dots or slashes). Do not expand `scripts/*-todo.json` allowlists without a tracking issue.

## 4. Subpath URL Templates and URL Policy

- **Subpath URLs in `data.url` (`scripts/check-url-templates.py`):** Below top-level source nodes, resolvers substitute `{id}` and variables into `data.url` **only** (`data.urls[]` is ignored on child nodes).
- **URL scheme policy (`scripts/validate-urls.py`):** Require `https://` unless the host is in `scripts/http-exception-allowlist.txt`. Reject `javascript:`, `data:`, `file:`, and internal/private hosts. Preserve exact upstream identifier formats (Principle #7).

## 5. Version Resolution, Examples, and Cross-Repo Lockstep

- **Version resolution (`scripts/validate-version-aliases.py`):** When `version_required: true` or `versions_available` is used, verify `version_disambiguation`, version-node patterns, and `data.versions_available[].aliases` (`label` and `on_match` in `substitute | reject | resolve`, never shadowing a real `version`).
- **Structured child examples:** Child-level `data.examples` must use `ExampleObject` entries (`{input, url, variables?}`) whose `input` matches the parent regex and produces `url` (`SecID-Service` auto-generates `test/resolver.test.ts` from these on deploy).
- **Cross-repo release train guard:** If a PR removes/renames a source or version, or changes `version_required` or version ordering asserted in `SecID-Service` tests (`test/resolver.test.ts`, `test/parser.test.ts`, `test/website.spec.ts`) or `SecID-Client-SDK` conformance fixtures (`tests/conformance/fixtures.json`), require compatible updates in each affected repository (`SecID-Service` **first** before merging here).
- **Type, subtype, and count parity:** Run `./scripts/update-counts.sh` when adding/removing namespace files. Changes to `type` or `subtype` values must match `SecID-Service/src/type-registry.ts` (`scripts/validate-type-list.py`, `scripts/validate-subtypes.py`, updating their pinned `SecID-Service` SHA together).
