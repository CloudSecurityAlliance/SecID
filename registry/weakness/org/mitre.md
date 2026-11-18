---
type: weakness
namespace: mitre.org
full_name: "MITRE Corporation"
operator: "secid:entity/mitre.org"
website: "https://www.mitre.org"
status: active

sources:
  cwe:
    full_name: "Common Weakness Enumeration"
    urls:
      website: "https://cwe.mitre.org"
      api: "https://cwe.mitre.org/data/index.html"
      lookup: "https://cwe.mitre.org/data/definitions/{num}.html"
    id_pattern: "CWE-\\d+"
    examples:
      - "secid:weakness/mitre.org/cwe#CWE-79"
      - "secid:weakness/mitre.org/cwe#CWE-89"
      - "secid:weakness/mitre.org/cwe#CWE-1427"
---

# MITRE Weakness Taxonomies

MITRE operates CWE, the canonical weakness taxonomy referenced by virtually all vulnerability databases.

## Why MITRE CWE Matters

CWE is the foundation of weakness classification:

- **Industry standard** - Referenced by CVE, NVD, and all major vuln databases
- **Hierarchical taxonomy** - Views, categories, and specific weaknesses
- **Comprehensive** - 900+ weakness types
- **AI coverage** - CWE-1400s cover AI/ML weaknesses

## CWE Structure

| Level | Purpose | Example |
|-------|---------|---------|
| Views | Organize by perspective | CWE-1000 (Research) |
| Categories | Group related weaknesses | CWE-19 (Data Processing) |
| Weaknesses | Specific flaw types | CWE-79 (XSS) |

## AI-Specific CWEs

| CWE | Name |
|-----|------|
| CWE-1426 | Improper Validation of Generative AI Output |
| CWE-1427 | Improper Neutralization of Input for LLM Prompting |
| CWE-1434 | Insecure ML Model Inference Parameters |

---

## cwe

The canonical software weakness taxonomy, operated by MITRE.

### Format

```
secid:weakness/mitre.org/cwe#CWE-NNN
```

### Resolution

```
https://cwe.mitre.org/data/definitions/{num}.html
```

### Releases and entry membership

`CWE-79`, `cwe-79`, and `secid:weakness/mitre.org/cwe#CWE-79` resolve to current
MITRE HTML and API endpoints. Unknown numeric IDs do not produce fabricated URLs.

Pin a catalog release with `secid:weakness/mitre.org/cwe@4.19#CWE-79`.
Registered releases are 4.19, 4.19.1, 4.20, 4.21 and 5.0. Each version checks
its own weaknesses, categories/groupings and views against MITRE's XML archive.
Version-pinned results link to the full official ZIP and explain how to select
the requested ID from its XML. MITRE's current HTML/API URLs are not historical
snapshots. The live API reported version 4.21 on 2026-11-18.

CWE-1448 is the AI/ML Products view (introduced in 4.20). CWE-1425 is the
2023 CWE Top 25 view. Categories became Groupings in the 5.0 XML schema;
the API still uses `/category/`.

Section suffixes such as `#CWE-79/potential-mitigations` are not registered.

The reproducible membership manifest is `scripts/data/cwe-releases.json`, with
release dates, schema versions, official URLs, SHA-256 hashes and all IDs by kind.
Run `python3 scripts/sync-cwe.py --check` offline, or add
`--archive-dir /path/to/archives` to check the downloaded catalogs against it.
The CI regression gate checks every numeric ID from 0 through 2100 in each release,
including case variants and the absence of newer entries in older releases.

### Key CWEs

| CWE | Name |
|-----|------|
| CWE-79 | Cross-site Scripting (XSS) |
| CWE-89 | SQL Injection |
| CWE-22 | Path Traversal |
| CWE-78 | OS Command Injection |
| CWE-1427 | Improper Neutralization of Input During LLM Interaction |

### Notes

- Hierarchical taxonomy (views, categories, weaknesses)
- Referenced by CVE, NVD, and most vulnerability databases
- CWE-1400s include AI/ML weaknesses
