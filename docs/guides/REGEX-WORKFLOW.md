# How to Write and Test Regex Patterns for match_nodes

> **Status:** Stub — outline only. Contributions welcome.

This guide covers developing, testing, and validating regex patterns used in registry `match_nodes` entries.

## Overview

Every registry source needs regex patterns that match valid identifiers from that source. Patterns appear in `match_nodes` entries and must:

- Match all valid IDs from the source
- Reject obviously invalid IDs
- Be safe from ReDoS (catastrophic backtracking)
- Work across runtimes (JavaScript, Python, Go, Rust)

## Step 1: Derive Patterns from Source ID Formats

Start with the source's documentation:

1. Find the official ID format specification
2. Collect 10+ real example IDs
3. Identify the pattern: prefix, separator, variable parts
4. Note edge cases: minimum/maximum lengths, allowed characters

Example: CVE IDs are `CVE-YYYY-NNNN+` where YYYY is a 4-digit year and NNNN+ is 4 or more digits.

Pattern: `^CVE-\d{4}-\d{4,}$`

## Step 2: Encode in match_nodes

Patterns must be anchored with `^` and `$`:

```json
{
  "match_nodes": {
    "CVE": {
      "pattern": "^CVE-\\d{4}-\\d{4,}$",
      "description": "CVE identifier",
      "url_template": "https://www.cve.org/CVERecord?id={id}"
    }
  }
}
```

For hierarchical ID systems, use children:

```json
{
  "match_nodes": {
    "errata": {
      "pattern": "^RH[SBE]A-\\d{4}:\\d+$",
      "children": {
        "RHSA": { "pattern": "^RHSA-\\d{4}:\\d+$", "description": "Security Advisory" },
        "RHBA": { "pattern": "^RHBA-\\d{4}:\\d+$", "description": "Bug Fix Advisory" },
        "RHEA": { "pattern": "^RHEA-\\d{4}:\\d+$", "description": "Enhancement Advisory" }
      }
    }
  }
}
```

## Step 3: Test with Command-Line Tools

### Using ripgrep (rg)

```bash
# Test pattern against example IDs in a file
echo "CVE-2024-1234" | rg '^CVE-\d{4}-\d{4,}$'

# Test against real registry data
rg 'CVE-\d{4}-\d{4,}' registry/advisory/org/mitre.md
```

### Using Python re module

```python
import re
pattern = r'^CVE-\d{4}-\d{4,}$'

# Should match
assert re.match(pattern, 'CVE-2024-1234')
assert re.match(pattern, 'CVE-2024-12345')

# Should not match
assert not re.match(pattern, 'CVE-2024-123')   # too few digits
assert not re.match(pattern, 'cve-2024-1234')  # wrong case
```

## Step 4: Test SecID Examples Against Patterns

For each example in your registry file, verify the subpath matches the pattern:

```python
import re

examples = [
    ("CVE-2024-1234", r"^CVE-\d{4}-\d{4,}$"),
    ("RHSA-2024:1234", r"^RHSA-\d{4}:\d+$"),
]

for id_str, pattern in examples:
    assert re.match(pattern, id_str), f"FAIL: {id_str} vs {pattern}"
```

## Step 5: ReDoS Detection

Patterns with nested quantifiers can cause catastrophic backtracking. Avoid:

- `(a+)+` — nested quantifiers
- `(a|a)+` — overlapping alternations
- `(.*a){10}` — greedy quantifiers with backtracking

Tools for detection:
- [recheck](https://makenowjust-labs.github.io/recheck/) — online ReDoS checker
- `rxxr2` — academic ReDoS analyzer
- Python `re` with timeout (Python 3.11+ supports `re.match(..., timeout=1)`)

## Step 6: Cross-Runtime Compatibility

SecID patterns must work in JavaScript, Python, Go, and Rust. Stick to:

**Safe to use:**
- Character classes: `\d`, `\w`, `[A-Z]`, `[0-9]`
- Quantifiers: `+`, `*`, `?`, `{n}`, `{n,m}`
- Anchors: `^`, `$`
- Grouping: `(...)`, `(?:...)`
- Alternation: `|`
- Escapes: `\.`, `\-`, `\:`

**Avoid (inconsistent across runtimes):**
- Lookbehind: `(?<=...)` — not in all JS engines
- Unicode properties: `\p{L}` — syntax varies by runtime
- Named groups: `(?P<name>...)` vs `(?<name>...)` — syntax differs
- Possessive quantifiers: `a++` — not in Python

## See Also

- [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) - `match_nodes` schema specification
- [REGISTRY-GUIDE.md](REGISTRY-GUIDE.md) - Pattern quality standards
- [ADD-NAMESPACE.md](ADD-NAMESPACE.md) - Full namespace creation workflow
