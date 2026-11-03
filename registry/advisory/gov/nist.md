---
type: advisory
namespace: nist.gov
full_name: "National Institute of Standards and Technology"
operator: "secid:entity/nist.gov"
website: "https://www.nist.gov"
status: active

sources:
  nvd:
    full_name: "National Vulnerability Database"
    urls:
      website: "https://nvd.nist.gov"
      api: "https://services.nvd.nist.gov/rest/json/cves/2.0"
      bulk_data: "https://nvd.nist.gov/vuln/data-feeds"
      lookup: "https://nvd.nist.gov/vuln/detail/{id}"
    id_pattern: "^CVE-\\d{4}-\\d{4,}$"
    examples:
      - "secid:advisory/nist.gov/nvd#CVE-2024-1234"
      - "secid:advisory/nist.gov/nvd#CVE-2023-44487"
---

# NIST Advisory Sources

NIST is a US government agency that develops standards, guidelines, and measurements for technology and cybersecurity. In security, NIST is known for the NVD, Cybersecurity Framework, and SP 800 series publications.

## Why NIST Matters

NIST provides authoritative security guidance used worldwide:

- **NVD (National Vulnerability Database)** - Enriches CVE records with CVSS scores, CPE, and CWE mappings
- **NIST Cybersecurity Framework (CSF)** - Widely adopted security framework
- **SP 800 series** - Security guidance documents (800-53, 800-61, etc.)
- **CVSS hosting** - While FIRST owns CVSS, NVD provides CVSS scores

## NVD vs CVE

Both use the same CVE identifiers, but they serve different purposes:

- **CVE (MITRE)** - The canonical vulnerability record (description, references)
- **NVD (NIST)** - Enrichment layer adding CVSS, CPE, CWE, analysis

```
secid:advisory/mitre.org/cve#CVE-2021-44228   -> The CVE record itself
secid:advisory/nist.gov/nvd#CVE-2021-44228    -> NVD's enriched view of that CVE
```

## Notes

- NVD had a significant enrichment backlog in 2024; CISA Vulnrichment helps fill gaps
- NIST standards are often mandated for US federal agencies (FISMA)
- Many international organizations adopt NIST frameworks voluntarily

---

## nvd

NIST's enrichment layer for CVE records.

### Format

```
secid:advisory/nist.gov/nvd#CVE-YYYY-NNNNN
```

### Resolution

```
https://nvd.nist.gov/vuln/detail/{id}
https://services.nvd.nist.gov/rest/json/cves/2.0?cveId={id}
```

### What NVD Adds

- CVSS scores (base, temporal, environmental)
- CPE (affected product) mappings
- CWE classification
- Reference categorization
- Analysis notes

### Notes

- Uses same CVE IDs as MITRE's CVE database
- `advisory/nist.gov/nvd#CVE-X` is NVD's enrichment of `advisory/mitre.org/cve#CVE-X`
- NVD has 20,000+ CVE backlog; enrichment can take weeks or months
