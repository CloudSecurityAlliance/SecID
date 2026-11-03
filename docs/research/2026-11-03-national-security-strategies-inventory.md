# National Security Strategies, Implementation Plans, and Review Processes — Coverage Inventory (`SecID#215`)

**Date:** 2026-11-03
**Issue:** [`CloudSecurityAlliance/SecID#215`](https://github.com/CloudSecurityAlliance/SecID/issues/215)
**Agent:** Gemini (SecID governing agent)

---

## 1. Scope & Classification Rules Applied

Per [`docs/guides/CLASSIFY.md`](../guides/CLASSIFY.md) and [`docs/reference/TYPES-AND-SUBTYPES.md`](../reference/TYPES-AND-SUBTYPES.md), national security strategy materials span three SecID types depending on their legal character and structural addressability:

1. **`reference`** — Whole-of-government national security strategies, national cyber security strategies, defence policy updates, multi-year action/implementation plans, annual implementation/progress reports, mid-term reviews, horizontal program evaluations, public consultation green papers, and "What We Heard / What We Learned" synthesis reports that set policy direction or audit strategy execution without themselves constituting binding statutes or enumerable control catalogues.
2. **`regulation`** — Enacted statutes, presidential decrees, or parliamentary acts that either:
   - enact a national security/cybersecurity strategy directly into binding law (e.g., Brazil's *Decreto nº 10.222/2020* enacting E-Ciber), or
   - mandate the statutory review cycle, oversight authorities, and parliamentary reporting processes for national security policy (e.g., Canada's *National Security Act, 2017*, *NSIRA Act*, and *NSICOP Act*; the US *National Security Act of 1947* § 108 / 50 U.S.C. § 3043).
3. **`control`** — National cybersecurity frameworks, baseline catalogues, or compliance standards issued alongside a national strategy that contain individually addressable control requirements (e.g., UAE *National Information Assurance Standard* `secid:control/csc.gov.ae/ias`, Qatar *National Information Assurance Standard* `secid:control/ncsa.gov.qa/nia`).

**Multi-edition resolution note:** For multi-edition `reference` entries (such as `national-security-strategy` or `national-cyber-security-strategy`), querying with `#<edition>` (e.g., `secid:reference/whitehouse.gov/national-security-strategy#2022` or `@2022#2022`) resolves directly to that specific edition's primary-source URL via the version child node (`ResolutionResult`), whereas querying at the source level with `@<edition>` alone (`secid:reference/whitehouse.gov/national-security-strategy@2022`) returns the source-level `RegistryResult` containing the structured per-edition `versions_available` array.

---

## 2. Canada — First Worked Set (Strategies, Implementation Plans, and Review Processes)

Canada's national security and cyber security strategy ecosystem is distributed across four primary publishing authorities: the Privy Council Office / Treasury Board / Department of National Defence (`canada.ca`), Public Safety Canada (`publicsafety.gc.ca`), the Canadian Centre for Cyber Security (`cyber.gc.ca`), and the Parliament of Canada / Department of Justice (`parl.ca`).

### 2.1 Overarching National Security Strategy & Defence Policy Cycle (`canada.ca`)

| SecID | Official Title | Issuing Body | Editions / Versions | Document Role | Primary Source URL |
|---|---|---|---|---|---|
| `secid:reference/canada.ca/national-security-policy` | *Securing an Open Society: Canada's National Security Policy* | Privy Council Office | `@2004` (April 2004) | Overarching Federal National Security Policy | [CP22-77-2004E.pdf](https://publications.gc.ca/collections/Collection/CP22-77-2004E.pdf) |
| `secid:reference/canada.ca/national-security-policy-progress-report` | *Securing an Open Society: One Year Later — Progress Report on the Implementation of Canada's National Security Policy* | Privy Council Office | `@2005` (April 2005) | 1-Year Strategy Implementation Progress Audit | [CP22-77-2005E.pdf](https://publications.gc.ca/collections/Collection/CP22-77-2005E.pdf) |
| `secid:reference/canada.ca/our-north-strong-and-free` | *Our North, Strong and Free: A Renewed Vision for Canada's Defence* | Department of National Defence | `@2024` (2024-04-08) | Defence Policy Update & commitment to a renewed National Security Strategy on a 4-year review cycle | [canada.ca](https://www.canada.ca/en/department-national-defence/corporate/reports-publications/north-strong-free-2024.html) |
| `secid:reference/canada.ca/national-security-transparency-commitment` | *National Security Transparency Commitment* | Government of Canada | 2017–present | Whole-of-government national security transparency principles & review framework | [canada.ca](https://www.canada.ca/en/services/defence/nationalsecurity/national-security-transparency-commitment.html) |
| `secid:reference/canada.ca/enterprise-cyber-security-strategy` | *Government of Canada Enterprise Cyber Security Strategy* | Treasury Board of Canada Secretariat (OCIO) | `@2024` (2024-05-22) | Federal internal enterprise cyber security strategy | [canada.ca](https://www.canada.ca/en/government/system/digital-government/online-security-privacy/enterprise-cyber-security-strategy.html) |

### 2.2 National Cyber Security, Critical Infrastructure, and Counter-Terrorism Strategies, Action Plans, and Review Reports (`publicsafety.gc.ca`)

| SecID | Official Title | Editions / Versions | Document Role | Primary Source URL |
|---|---|---|---|---|
| `secid:reference/publicsafety.gc.ca/national-cyber-security-strategy` | *Canada's National Cyber Security Strategy* (*Securing Canada's Digital Future*) | `@2025` (current, 2025-02-06), `@2018` (superseded, 2018-06-12), `@2010` (deprecated, 2010-10-03) | National Cyber Security Strategy | [2025](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/ntnl-cbr-scrt-strtg-2025/index-en.aspx), [2018](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/ntnl-cbr-scrt-strtg/index-en.aspx), [2010](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/archive-cbr-scrt-strtgy/archive-index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/national-cyber-security-action-plan` | *National Cyber Security Action Plan* | `@2019-2024` (current, 2019-08-07), `@2010-2015` (superseded) | 5-Year Horizontal Implementation Plan | [2019-2024](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/ntnl-cbr-scrt-strtg-2019/index-en.aspx), [2010-2015](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/ctn-pln-cbr-scrt/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/national-cyber-security-strategy-mid-term-review` | *National Cyber Security Strategy 2019-2024: Report on the Mid-term Review* | `@2022` (June 2022) | Mid-Term Strategy Review Report | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/ntnl-cbr-scrt-strtg-2019-md-trm/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/national-cyber-security-strategy-evaluation` | *Mid-Term and Horizontal Evaluations of Canada's National Cyber Security Strategy* | `@2022` (current, 2022-03-28), `@2017` (superseded, Sept 2017) | Formal Treasury Board Program Evaluation | [2022](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/2022-vtn-ntnl-cbr-strtgy/index-en.aspx), [2017](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/vltn-cnd-scrt-strtg/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/cyber-review-consultations-report-2017` | *Cyber Review Consultations Report (2017)* | 2017 | Public Consultation Synthesis Report | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/2017-cybr-rvw-cnslttns-rprt/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/federal-cyber-incident-response-plan` | *Federal Cyber Incident Response Plan* | `@2023` (2023-05-12) | National Incident Response Governance Plan | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/fdrl-cbr-ncdnt-rspns-pln-2023/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/national-strategy-critical-infrastructure` | *National Strategy for Critical Infrastructure* | `@2009` | National Critical Infrastructure Strategy | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/srtg-crtcl-nfrstrctr/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/action-plan-critical-infrastructure` | *Action Plan for Critical Infrastructure* | `@2021-2023` (current), `@2018-2020`, `@2014-2017`, `@2010` | Multi-Year Critical Infrastructure Implementation Plans | [2021-2023](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/2021-ctn-pln-crtcl-nfrstrctr/index-en.aspx), [2018-2020](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/pln-crtcl-nfrstrctr-2018-20/index-en.aspx), [2014-2017](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/pln-crtcl-nfrstrctr-2014-17/index-en.aspx), [2010](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/pln-crtcl-nfrstrctr/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/critical-infrastructure-consultation-report-2022` | *Renewing Canada's Approach to Critical Infrastructure Resilience: What We Heard Report* | 2022 | Strategy Renewal Consultation Report | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/rnwng-cnd-pprch-crtcl-nfrstrctr-rslnc-2022/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/counter-terrorism-strategy` | *Building Resilience Against Terrorism: Canada's Counter-terrorism Strategy* | `@2012` | National Counter-Terrorism Strategy | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/rslnc-gnst-trrrsm/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/national-security-green-paper-2016` | *Our Security, Our Rights: National Security Green Paper, 2016* | 2016 | Pre-Legislative National Security Consultation Paper | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/ntnl-scrt-grn-ppr-2016/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/national-security-consultations-report-2017` | *National Security Consultations: What We Learned Report* | 2017 | Public Consultation Synthesis Report | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/2017-nsc-wwlr/index-en.aspx) |
| `secid:reference/publicsafety.gc.ca/nstag-reports` | *National Security Transparency Advisory Group (NS-TAG) Reports* | 2020–2024 | Independent Advisory Review Reports | [publicsafety.gc.ca](https://www.publicsafety.gc.ca/cnt/rsrcs/pblctns/nstag-gctsn-dgtztn-ntnl-scrt-2024/index-en.aspx) |

### 2.3 Statutory Review, Parliamentary Oversight, and Critical Cyber Legislation (`parl.ca`)

| SecID | Official Title | Citation / Status | Review & Oversight Mechanism | Primary Source URL |
|---|---|---|---|---|
| `secid:regulation/parl.ca/national-security-act-2017` | *National Security Act, 2017* | S.C. 2019, c. 13 (Bill C-59, in force 2019) | Section 168(1) mandates a comprehensive parliamentary review of the Act's provisions and operation beginning in its fourth year. | [laws-lois.justice.gc.ca](https://laws-lois.justice.gc.ca/eng/annualstatutes/2019_13/) |
| `secid:regulation/parl.ca/nsira-act` | *National Security and Intelligence Review Agency Act* | S.C. 2019, c. 13, s. 2 / Justice Laws c. N-16.62 (in force 2019) | Establishes NSIRA with cross-government authority to review any federal national security or intelligence activity and table annual public reports. | [laws-lois.justice.gc.ca](https://laws-lois.justice.gc.ca/eng/acts/N-16.62/FullText.html) |
| `secid:regulation/parl.ca/nsicop-act` | *National Security and Intelligence Committee of Parliamentarians Act* | S.C. 2017, c. 15 / Justice Laws c. N-16.6 (Bill C-22, in force 2017) | Section 8 empowers NSICOP to review the legislative, regulatory, policy, administrative, and financial framework for national security; Section 34 mandates a 5-year statutory parliamentary review. | [laws-lois.justice.gc.ca](https://laws-lois.justice.gc.ca/eng/acts/N-16.6/) |
| `secid:regulation/parl.ca/ccspa` | *Critical Cyber Systems Protection Act* | S.C. 2026, c. 9 (Bill C-8 in 45-1, Royal Assent June 15, 2026; formerly Bill C-26 in 44-1) | Legislative pillar implementing the critical-infrastructure protection commitments of the National Cyber Security Strategy. | [parl.ca](https://www.parl.ca/legisinfo/en/bill/45-1/c-8) |

---

## 3. Comparator Jurisdictions Registered in SecID

| Jurisdiction | SecID | Official Title | Type | Role / Review Mechanism |
|---|---|---|---|---|
| **United States** | `secid:reference/whitehouse.gov/national-security-strategy` | *National Security Strategy of the United States of America* (`@2025`, `@2022`, `@2017`, `@2015`, `@2010`) | `reference` | Statutorily mandated presidential report to Congress under 50 U.S.C. § 3043 (Goldwater-Nichols Act § 603). |
| **United States** | `secid:reference/whitehouse.gov/national-cybersecurity-strategy` | *United States National Cybersecurity Strategy* (`@2026` *President Trump's Cyber Strategy for America*, `@2023`, `@2018`) | `reference` | National cybersecurity strategies issued by the White House (2026 Cyber Strategy for America; 2023 National Cybersecurity Strategy; 2018 National Cyber Strategy). |
| **United States** | `secid:reference/whitehouse.gov/national-cybersecurity-strategy-implementation-plan` | *National Cybersecurity Strategy Implementation Plan (NCSIP)* (`@2` May 2024, `@1` July 2023) | `reference` | Living interagency implementation tracker with numbered initiatives, lead agencies, and annual ONCD posture reviews. |
| **United Kingdom** | `secid:reference/gov.uk/national-security-strategy` | *UK National Security Strategy* (`@2025` CP 1338, `@2015` Cm 9161, `@2010` Cm 7953) | `reference` | Overarching UK National Security Strategy series; scrutinized by the parliamentary Joint Committee on the National Security Strategy (JCNSS). |
| **United Kingdom** | `secid:reference/gov.uk/integrated-review` | *Integrated Review of Security, Defence, Development and Foreign Policy* (`@2023` Refresh CP 811, `@2021` CP 403) | `reference` | 2021 and 2023 Integrated Review series bridging the 2015 NSS/SDSR and the 2025 National Security Strategy. |
| **United Kingdom** | `secid:reference/gov.uk/national-cyber-strategy` | *National Cyber Strategy 2022* (`@2022`, `@2016-2021`) | `reference` | Whole-of-UK cyber strategy paired with the Government Cyber Security Strategy (2022–2030) and annual Cabinet Office progress reports. |
| **Australia** | `secid:regulation/homeaffairs.gov.au/cyber-security-strategy-2023-2030` | *2023–2030 Australian Cyber Security Strategy* | `regulation` | Six-shield national strategy implemented via two-year Action Plans (Horizon 1: 2023–2025) and the *Cyber Security Act 2024*. |
| **Japan** | `secid:regulation/cyber.go.jp/cybersecurity-basic-act` | *Basic Act on Cybersecurity (Act No. 104 of 2014)* | `regulation` | Statutory mandate (Article 12) requiring the Cabinet to formulate and periodically revise Japan's Cybersecurity Strategy. |
| **Brazil** | `secid:regulation/gsi.gov.br/e-ciber` | *Estratégia Nacional de Segurança Cibernética (E-Ciber, Decreto nº 10.222/2020)* | `regulation` | Enacted by presidential decree on a four-year cycle, superseded/extended via the National Cybersecurity Policy (*PNCiber*, Decreto nº 11.856/2023). |
| **United Arab Emirates** | `secid:control/csc.gov.ae/ncss` | *UAE National Cybersecurity Strategy* | `control` | Five-pillar national strategy paired with the UAE Information Assurance Standard (`secid:control/csc.gov.ae/ias`). |
| **Qatar** | `secid:control/ncsa.gov.qa/ncss` | *Qatar National Cyber Security Strategy (2024–2030)* | `control` | Third-generation national strategy paired with the National Information Assurance Standard (`secid:control/ncsa.gov.qa/nia`). |

---

## 4. Explicit Worldwide Expansion Backlog

This initial batch establishes Canada as the complete worked reference set (covering strategy, action plan, mid-term review, program evaluation, public consultation, and statutory review organs) alongside key Five Eyes and international comparators. It does **not** claim worldwide completeness.

The following jurisdictions and document families constitute the prioritized worldwide expansion backlog for subsequent registry sweeps:

### 4.1 European Union & NATO Member States
- **European Union (`europa.eu` / `eeas.europa.eu`):** *Strategic Compass for Security and Defence* (2022, annual progress reports) and *EU Cybersecurity Strategy for the Digital Decade* (`JOIN(2020) 18 final`).
- **Germany (`bundesregierung.de` / `bmi.bund.de`):** *Nationale Sicherheitsstrategie: Wehrhaft. Resilient. Nachhaltig. Integrierte Sicherheit für Deutschland* (first German National Security Strategy, June 2023) and *Cybersicherheitsstrategie für Deutschland* (2021).
- **France (`sgdsn.gouv.fr` / `ssi.gouv.fr`):** *Revue nationale stratégique (RNS)* (2022, updated 2025 by SGDSN) and *Stratégie nationale pour la sécurité du numérique*.
- **Netherlands (`ncsc.nl` / `rijksoverheid.nl`):** *Veiligheidsstrategie voor het Koninkrijk der Nederlanden* (2023–2029) and *Nederlandse Cybersecuritystrategie (NLCS)* (2022–2028) with annual NCSC implementation monitoring.
- **Estonia (`ria.ee` / `valitsus.ee`):** *National Security Concept of Estonia* (*Eesti julgeolekupoliitika alused*, 2023, approved by the Riigikogu) and *Cybersecurity Strategy of Estonia (2024–2027)*.

### 4.2 Indo-Pacific
- **Japan (`cas.go.jp` / `nisc.go.jp`):** *National Security Strategy of Japan (NSS)* (Dec 2022 revision, National Security Secretariat) and the Cabinet-approved *Cybersecurity Strategy* texts issued under the *Basic Act on Cybersecurity*.
- **South Korea (`president.go.kr` / `nis.go.kr`):** *National Security Strategy: Global Pivotal State for Freedom, Peace, and Prosperity* (June 2023) and *National Cybersecurity Strategy* (2024) + *National Cybersecurity Basic Plan*.
- **Singapore (`csa.gov.sg`):** *Singapore Cybersecurity Strategy 2021* (and OT Cybersecurity Masterplan 2024) under the Cyber Security Agency of Singapore.
- **New Zealand (`dpmc.govt.nz` / `ncsc.govt.nz`):** *Aotearoa New Zealand's First National Security Strategy: Secure Together (2023–2028)* and *New Zealand's Cyber Security Strategy*.
- **India (`nciipc.gov.in` / `meity.gov.in`):** *National Cyber Security Policy (2013)* and the forthcoming *National Cyber Security Strategy (NCSS)*.

### 4.3 Multilateral & Comparative Strategy Repositories
- **ENISA (`enisa.europa.eu`):** *National Capabilities Assessment Framework (NCAF)* and *National Cyber Security Strategies (NCSS) Good Practice Guide* (design, implementation, and evaluation lifecycle guides).
- **ITU (`itu.int`):** *Guide to Developing a National Cybersecurity Strategy* (multi-stakeholder lifecycle edition) and the ITU Global Cybersecurity Index (GCI) national strategy directory.
- **OECD / NATO CCDCOE:** Comparative national cyber and security strategy repositories.
