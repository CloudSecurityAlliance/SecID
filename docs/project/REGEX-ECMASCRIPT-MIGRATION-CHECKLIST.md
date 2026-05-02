# Regex Dialect — Inventory and CI Tasks

**Date:** 2026-04-20 (originally 2026-04-16 as migration checklist, revised after `(?i)` declared canonical)
**Status:** Active reference

## Background

This document was originally a migration checklist to strip `(?i)` from registry patterns. That migration was cancelled — `(?i)` is valid ES2025 ECMAScript and works in the production Cloudflare Workers runtime. See `docs/project/REGEX-ECMASCRIPT-MIGRATION-PLAN.md` (now the Regex Dialect Policy) for the full decision.

The inventory data and CI tasks below remain useful as a reference.

## Registry Inventory (as of 2026-04-17)

- JSON files with inline `(?i)`: **684** out of 710 total
- Total `(?i)` occurrences in JSON: **1,347**
- By type (files): `disclosure` 486, `capability` 54, `advisory` 42, `control` 32, `methodology` 18, `entity` 14, `weakness` 13, `regulation` 12, `reference` 9, `ttp` 4
- Most common pattern: `(?i)^cna$` in **478** files (all under `registry/disclosure/`)
- Non-ECMAScript constructs found: **0** (no `(?P<...>`, no lookbehind, no atomic groups)

## CI Tasks

- [ ] Add JS compile validation: all patterns in `registry/**/*.json` must pass `new RegExp(pattern)` in V8/Workers runtime.
- [ ] Add prohibited-construct scanner: block `(?P<`, `(?<=`, `(?<!`, `(?>`, unanchored patterns on changed files.
- [ ] Optional: add secondary compile checks in Python/Go/Rust for portability telemetry.

## Useful Commands

```bash
# Count inline-flag usage (for inventory tracking, not removal)
rg -n -F "(?i)" registry --glob "*.json" | wc -l
rg --files-with-matches -F "(?i)" registry --glob "*.json" | wc -l

# Files by top-level type
rg --files-with-matches -F "(?i)" registry --glob "*.json" \
  | awk -F'/' '{print $2}' | sort | uniq -c | sort -nr

# Scan for prohibited non-ECMAScript constructs
rg -n '(\(\?P<|\(\?<=|\(\?<!|\(\?>)' registry --glob "*.json"

# Verify all patterns compile in Node/V8
node -e "
const fs = require('fs'), glob = require('glob');
glob.sync('registry/**/*.json').forEach(f => {
  const data = JSON.parse(fs.readFileSync(f));
  (function walk(nodes) {
    for (const n of nodes || []) {
      for (const p of n.patterns || []) {
        try { new RegExp(p); } catch(e) { console.error(f, p, e.message); }
      }
      walk(n.children);
    }
  })(data.match_nodes);
});
"
```
