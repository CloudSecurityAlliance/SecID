# Disclosure Registry — Known Gaps

Generated: 2026-04-03
Source: CVE CNA partner data from [cve.org/PartnerInformation/ListofPartners](https://www.cve.org/PartnerInformation/ListofPartners)

**486 files, 513 match_nodes** covering all 502 CVE Program partners.

## Missing Detail Data

~~8 partners originally timed out during batch scraping.~~ **Resolved** — all 8 were re-scraped manually via Playwright and their disclosure files updated with contacts, policy URLs, and advisories URLs. Zero partners remain without detail data.

## No Contact Info (24 nodes)

These nodes have no email or web form. Breakdown:

- **4 CISA nodes** (CISA uses cveform.mitre.org, not listed on partner pages)
- **1 MITRE** (Secretariat — uses cveform.mitre.org)
- **1 HackerOne** (platform CNA — contact is through customer programs, not direct)
- **1 CSA security-txt** (contact is in the security.txt file itself)
- **~17 CNAs with empty contact on their cve.org partner page** (Nintendo, Canon, Xerox, Fedora, etc.)

## No Disclosure Policy URL (13 nodes)

These nodes have no "View Policy" link on their cve.org partner page:

- 2 CSA hand-crafted nodes (policy is in `notes` field)
- 1 MITRE Secretariat
- 10 CNAs that genuinely lack a policy link (42Gears, ESET, INCIBE, NCSC-FI, Payara, Teradyne, TR-CERT, CERT.PL, CERT/CC Taiwan)

## No Security Advisories URL (31 nodes)

These nodes have no "View Advisories" link. Some are expected (CERTs coordinate but don't publish advisories), others are gaps.

## Stale Scope (1 node)

| Node | Scope Text |
|------|-----------|
| cisa.gov/cna-adp | "View scope here." (placeholder from cve.org) |

## Scope as First-Class Field

The `scope` field was introduced with this CNA data load. The pre-existing CSA entry (`cloudsecurityalliance.org`) has scope information in `description` and `notes` but no explicit `scope` field — it should be updated to match the new pattern.

## TLD Distribution

| TLD | Count | TLD | Count |
|-----|-------|-----|-------|
| com | 345 | io | 21 |
| org | 50 | jp | 6 |
| de | 5 | net | 5 |
| au | 4 | tw | 4 |
| nl, se, sg, tr | 3 each | co, kr | 2 each |
| 25 other TLDs | 1 each | | |

Includes non-traditional TLDs: `.canon`, `.fish`, `.cloud`, `.company`, `.systems`, `.services`, `.works`, `.tech`, `.ist`
