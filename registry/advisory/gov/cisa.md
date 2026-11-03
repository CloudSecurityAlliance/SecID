---
type: advisory
namespace: cisa.gov
full_name: "Cybersecurity and Infrastructure Security Agency"
operator: "secid:entity/cisa.gov"
website: "https://www.cisa.gov"
status: active

sources:
  kev:
    full_name: "Known Exploited Vulnerabilities Catalog"
    urls:
      website: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog"
      api: "https://www.cisa.gov/sites/default/files/feeds/known_exploited_vulnerabilities.json"
      bulk_data: "https://www.cisa.gov/sites/default/files/csv/known_exploited_vulnerabilities.csv"
      lookup: "https://www.cisa.gov/known-exploited-vulnerabilities-catalog?search_api_fulltext={id}"
    id_pattern: "CVE-\\d{4}-\\d{4,}"
    examples:
      - "secid:advisory/cisa.gov/kev#CVE-2024-1234"
      - "secid:advisory/cisa.gov/kev#CVE-2021-44228"
  vulnrichment:
    full_name: "CISA Vulnrichment"
    urls:
      website: "https://github.com/cisagov/vulnrichment"
      bulk_data: "https://github.com/cisagov/vulnrichment"
      lookup: "https://github.com/cisagov/vulnrichment/blob/develop/{year}/{bucket}/{id}.json"
      raw: "https://raw.githubusercontent.com/cisagov/vulnrichment/develop/{year}/{bucket}/{id}.json"
    id_pattern: "CVE-\\d{4}-\\d{4,}"
    examples:
      - "secid:advisory/cisa.gov/vulnrichment#CVE-2024-1234"
      - "secid:advisory/cisa.gov/vulnrichment#CVE-2026-0019"
---

# CISA Advisory Sources

CISA is the US government agency responsible for protecting critical infrastructure from cyber threats. CISA coordinates vulnerability disclosure, issues security directives, and maintains the KEV (Known Exploited Vulnerabilities) catalog.

## Why CISA Matters

CISA has operational authority over US federal cybersecurity:

- **KEV Catalog** - Authoritative list of vulnerabilities being actively exploited
- **Vulnrichment** - CVE enrichment to address NVD backlog
- **BOD/ED** - Binding Operational Directives and Emergency Directives for federal agencies
- **CVE Program oversight** - Contracts MITRE to operate CVE

## KEV: Why It's Special

KEV isn't just another vulnerability list - it's a prioritization signal:

- **Confirmed exploitation** - Every KEV entry has evidence of active exploitation
- **Legal mandate** - BOD 22-01 requires federal agencies to remediate KEV entries
- **Quality filter** - ~1,200 entries vs 200,000+ CVEs; only exploited vulnerabilities

Many organizations use KEV status as a prioritization factor even if not legally required.

## Notes

- CISA was created in 2018, replacing NPPD (National Protection and Programs Directorate)
- CISA also handles ICS-CERT advisories for industrial control systems
- CISA's Vulnrichment project helps address NVD's enrichment backlog

---

## kev

CISA's authoritative catalog of vulnerabilities confirmed to be actively exploited in the wild. Federal agencies are required to remediate KEV entries within specified timeframes.

### Format

```
secid:advisory/cisa.gov/kev#CVE-YYYY-NNNNN
```

### Resolution

KEV uses CVE IDs as identifiers:
```
https://www.cisa.gov/known-exploited-vulnerabilities-catalog?search_api_fulltext={id}
```

### Why KEV Matters

KEV is a prioritization signal, not just another vulnerability list:
- **Confirmed exploitation** - Every entry has evidence of active exploitation
- **Binding for federal agencies** - BOD 22-01 requires remediation
- **Industry benchmark** - Many organizations use KEV for prioritization
- **Quality over quantity** - ~1000 entries vs 200,000+ CVEs

### Notes

- KEV entries reference CVE IDs, so SecID representation uses CVE as the subpath
- JSON and CSV feeds updated as vulnerabilities are added
- Due dates included for federal agency compliance tracking

---

## vulnrichment

CISA's CVE enrichment initiative providing additional context for CVE records including CWE mappings, CVSS scores, and CPE data.

### Format

```
secid:advisory/cisa.gov/vulnrichment#CVE-YYYY-NNNNN
```

### Resolution

```
https://github.com/cisagov/vulnrichment/blob/develop/{year}/{bucket}/{id}.json
https://raw.githubusercontent.com/cisagov/vulnrichment/develop/{year}/{bucket}/{id}.json
```

Where `{year}` is the 4-digit year extracted from the CVE ID, `{bucket}` is all but the last 3 digits of the sequence number followed by `xxx` (e.g., `1xxx` from `CVE-2024-1234`, `0xxx` from `CVE-2026-0019`), and `{id}` is the full CVE ID.

### Why Vulnrichment Exists

CISA provides enrichment data to fill gaps in CVE records:
- **Faster enrichment** - Doesn't wait for NVD processing
- **CWE mappings** - Weakness classification
- **CVSS scores** - Severity assessment
- **CPE data** - Affected product identification

### Notes

- Enrichment data follows CVE JSON 5.x format
- Contributed back to the CVE ecosystem
- Addresses NVD enrichment backlog
