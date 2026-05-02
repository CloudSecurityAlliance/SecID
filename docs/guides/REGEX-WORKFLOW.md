# How to Write and Test Regex Patterns for match_nodes

## Security Status
**Status: Active guidance (not a stub).**

This guide defines how SecID handles regex safety for registry `match_nodes`.

## Dialect Policy
Canonical registry regex syntax is **ECMAScript `RegExp`** (ES2025, as implemented by V8 in Cloudflare Workers).

- Registry files store one canonical pattern set only (no per-engine pattern variants).
- Non-JS runtimes (Python, Go, Rust, etc.) can consume patterns as-is — all allowed constructs are cross-engine portable.
- **`(?i)` inline modifier is allowed and canonical.** It is valid ES2025 ECMAScript (V8 125+), universally portable across Python/Go/Rust/Java/.NET/PCRE, and makes patterns self-describing.
- **Prohibited constructs:** Python-style `(?P<name>...)` named groups (use `(?<name>...)` instead), lookbehind `(?<=`/`(?<!`, atomic groups `(?>`, backreferences `\1`, nested quantifiers `(a+)+`, unanchored patterns.

See `docs/project/REGEX-ECMASCRIPT-MIGRATION-PLAN.md` for the full dialect policy and rationale.

## Threat Model
SecID-Service executes registry patterns against user-controlled identifiers at runtime. A pathological pattern could cause catastrophic backtracking (ReDoS) and CPU spikes.

## Accepted Risk Statement
SecID **accepts** runtime regex execution risk because flexible identifier support depends on source-specific patterns. Risk is controlled at registry authoring/review time, not eliminated at runtime.

## Required Controls Before Merge
For every new or changed pattern:

1. Anchor patterns with `^` and `$`.
2. Avoid backtracking-prone constructs: nested quantifiers (`(a+)+`), ambiguous overlap (`(a|aa)+`), wide `.*` inside repeated groups.
3. Validate against real positive and negative examples from the source.
4. Run a ReDoS check (for example `recheck` or equivalent analyzer) and capture the result in PR notes.
5. Confirm every pattern compiles in ECMAScript (`new RegExp(pattern)` in JS/TS).
6. Optionally run cross-runtime compatibility checks (Python, Go, Rust) and capture results when relevant.
7. Include explicit reviewer sign-off that regex safety was checked.

## Implementation Reality (Current)
These controls are currently enforced through contributor workflow and review discipline, including AI-assisted analysis, not through a hard CI gate.

## PR Checklist Snippet
Add this to PR descriptions for regex changes:

- `ReDoS reviewed:` Yes/No
- `Analyzer/tool used:` ...
- `Worst-case behavior checked:` ...
- `Example set added/updated:` ...
- `ECMAScript compile check:` Pass/Fail
- `Cross-runtime check (optional):` Python/Go/Rust results

## Residual Risk and Escalation
Residual risk remains if a bad pattern passes review. If production latency or CPU behavior indicates regex abuse, rollback the registry change and re-review affected patterns before re-deploy.
