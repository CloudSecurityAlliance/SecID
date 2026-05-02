# Regex Dialect Policy

**Date:** 2026-04-20 (originally 2026-04-17 as migration plan, revised to policy document)
**Status:** Active
**Audience:** SecID maintainers and AI reviewers across `SecID`, `SecID-Service`, `SecID-Server-API`, and `SecID-Client-SDK`.

## Decision

**ECMAScript `RegExp` is the canonical regex dialect for registry patterns.** Specifically, ES2025 ECMAScript as implemented by V8 in Cloudflare Workers — this is the production runtime for SecID-Service.

### Why no migration is needed

The original version of this document planned a multi-wave migration to strip `(?i)` inline modifiers from 684 registry files. That migration was cancelled because:

1. **`(?i)` is valid ES2025 ECMAScript.** V8 added RegExp modifier support (including `(?i)`, `(?m)`, `(?s)`) in Chrome 125 / mid-2024. Cloudflare Workers runs V8. The existing patterns already compile and execute correctly in the production runtime.

2. **`(?i)` is the most portable inline modifier across regex engines.** It works in Python `re`, Go `regexp`, Rust `regex`, Java `Pattern`, .NET `Regex`, PCRE, and now ECMAScript. Stripping it would make patterns LESS portable, not more.

3. **`(?i)` makes patterns self-describing.** The case-sensitivity behavior is visible in the pattern itself, not hidden in external metadata or registry-level defaults.

4. **Zero registry files need editing.** The 684 files with `(?i)` are already in canonical form.

## Policy Rules

### Allowed constructs

| Construct | Status | Rationale |
|---|---|---|
| `(?i)` inline case-insensitive modifier | **Allowed (canonical)** | Valid ES2025, universally portable, self-describing |
| Anchored patterns (`^...$`) | **Required** | Prevents partial matching, reduces ReDoS risk |
| Character classes, quantifiers, alternation | **Allowed** | Standard ECMAScript regex |
| Non-capturing groups `(?:...)` | **Allowed** | Standard ECMAScript regex |
| ECMAScript named groups `(?<name>...)` | **Allowed with caution** | ES2018+, use only when variable extraction requires it |

### Prohibited constructs

| Construct | Status | Rationale |
|---|---|---|
| Python named groups `(?P<name>...)` | **Prohibited** | Not ECMAScript syntax. Use `(?<name>...)` instead |
| Lookbehind `(?<=...)` / `(?<!...)` | **Prohibited** | Portability concerns across non-JS engines |
| Atomic groups `(?>...)` | **Prohibited** | Not supported in ECMAScript |
| Backreferences `\1` | **Prohibited** | Fragile, rarely needed for identifier matching |
| Nested quantifiers `(a+)+` | **Prohibited** | ReDoS risk (catastrophic backtracking) |
| Unanchored patterns | **Prohibited** | Must use `^` and `$` anchors |

### Registry inventory (for reference)

As of 2026-04-17:
- JSON files with `(?i)`: **684** out of 710 total
- Total `(?i)` occurrences: **1,347**
- Most common: `(?i)^cna$` in **478** files (all `registry/disclosure/`)
- Non-ECMAScript constructs (`(?P<...>`, lookbehind, etc.): **0**

The registry is already 100% ECMAScript-compatible. No patterns need migration.

## Cross-Runtime Support

### Production (Cloudflare Workers / V8)

Patterns are consumed directly via `new RegExp(pattern)`. All current patterns compile and execute correctly.

### Self-hosted resolver (SecID-Server-API)

Must match production behavior. `(?i)` is supported in Python `re`, Go `regexp`, and all other target runtimes.

### Client SDKs (SecID-Client-SDK)

SDKs that do local pattern matching can use patterns as-is in Python, Go, Rust, Java, .NET. For older JavaScript runtimes (Node < 22, pre-ES2025 browsers) that lack `(?i)` support, the SDK should provide a shim:

```javascript
// Shim for pre-ES2025 JS runtimes
function compilePattern(pattern) {
  const inlineFlags = pattern.match(/^\(\?([imsu]+)\)/);
  if (inlineFlags) {
    return new RegExp(pattern.slice(inlineFlags[0].length), inlineFlags[1]);
  }
  return new RegExp(pattern);
}
```

API-only clients (no local matching) need no changes.

## CI Validation

Required:
- All patterns in `registry/**/*.json` must compile via `new RegExp(pattern)` in the Workers runtime (or equivalent V8 version).
- CI must block patterns that use prohibited constructs (scan for `(?P<`, `(?<=`, `(?<!`, `(?>`, unanchored patterns).

Optional:
- Secondary compile checks in Python/Go/Rust for portability telemetry.

## Related Docs

- `docs/guides/REGEX-WORKFLOW.md` — pattern authoring guide and safety controls
- `docs/reference/REGISTRY-JSON-FORMAT.md` — registry JSON schema
- `docs/superpowers/specs/2026-04-15-product-tier-labeling-design.md` — product tier design (uses `@version` with regex matching)
