# SecID Data Hosting Rules

How we decide what data to host, where it goes, and how to handle licensing.

## The Three Rules (plus Rule 0)

### Rule 0: Respect the License

**This gates everything else.** Before hosting any data, determine the license status.

| License Status | Action |
|---|---|
| **Public domain / CC0 / US government work** | Host freely. Include attribution. |
| **Permissive open license** (Apache 2.0, CC BY, MIT) | Host with attribution. LICENSE file + per-item provenance. |
| **Share-alike** (CC BY-SA) | Host with same license. Document clearly. |
| **Custom terms of use** (free use with attribution) | Host with terms reproduced in LICENSE. Follow specific requirements. |
| **EU legislation** | Freely reusable per EUR-Lex reuse policy. Attribution to source. |
| **Organization-owned** (need explicit permission) | Get written permission before hosting. Document in LICENSE. |
| **Paywalled / all rights reserved / no license** | **DO NOT HOST CONTENT.** Registry entry with description + purchase/access URL only. |
| **User-generated content** (social media, forums) | Archive for preservation (Rule 1) with clear provenance. Don't claim ownership. Link to original. |
| **No explicit license** | **DO NOT HOST.** Treat as all rights reserved until clarified. |

**When in doubt: don't host.** A registry entry pointing to the source is always safe. Hosting the data requires confirmed license compatibility.

### Rule 1: Persistence Risk

Host the data when the source might disappear.

Examples:
- Tweets/Bluesky posts about vulnerabilities (deletion risk)
- Paste site disclosures (expiration by design)
- Blog posts on ephemeral platforms (site shutdown risk)
- Reddit threads (moderation/deletion risk)

### Rule 2: AI-Unfriendly Format

Host the data when it exists in a reliable place but isn't consumable per-item by AI agents.

Examples:
- CWE — reliable at mitre.org but distributed as a monolithic XML dump, not per-weakness JSON
- GDPR — reliable at EUR-Lex but it's HTML, not per-article structured JSON
- CCM/AICM — reliable at cloudsecurityalliance.org but it's Excel spreadsheets in ZIP bundles
- NIST 800-53 — reliable at csrc.nist.gov but scattered across nested web pages
- OWASP Top 10 — reliable at owasp.org but it's web pages, not per-item data

### Rule 3: Synthesis Needed

Host the data when the raw source is reliable and accessible, but the useful knowledge needs to be extracted or condensed from noisy/scattered content.

Examples:
- Reddit vulnerability discussion (50 replies → key facts, timeline, vendor response)
- Twitter disclosure thread (8 tweets → structured disclosure with affected product, PoC, vendor status)
- Mailing list thread on oss-security (20 emails → structured vulnerability report)
- Conference talk (45-min video → technique description, affected systems, detection methods)
- Blog post series (3 posts → consolidated timeline and root cause analysis)

## What We Don't Host

Data that already has good machine-readable, per-item, reliable sources:

| Source | Why Not | Use Instead |
|--------|---------|-------------|
| CVE records | cvelistV5 is per-record JSON in GitHub | `github.com/CVEProject/cvelistV5` |
| NVD data | NIST provides a structured API | `services.nvd.nist.gov/rest/json/cves/2.0` |
| GHSA | GitHub advisory database is per-advisory JSON | `github.com/github/advisory-database` |
| ATT&CK | MITRE publishes STIX JSON (Apache 2.0) | `github.com/mitre-attack/attack-stix-data` |
| ATLAS | MITRE publishes YAML | `github.com/mitre-atlas/atlas-data` |
| Vendor advisories | Red Hat, Debian, etc. have reliable APIs/feeds | Registry points to their sources |
| ISO standards | Paywalled — we can't host the content | Registry entry with description + purchase URL |

## License Assessment for Known Sources

| Source | License | Can Host? | Notes |
|--------|---------|-----------|-------|
| CWE (MITRE) | MITRE CWE Terms of Use | **Yes** | Include full ToU + attribution |
| OWASP Top 10 / LLM Top 10 | CC BY-SA 4.0 | **Yes** | Attribute OWASP, share-alike applies |
| NIST 800-53 / CSF / AI RMF | US government work (public domain) | **Yes** | Attribution appreciated but not required |
| GDPR / AI Act / NIS2 / DORA | EU legislation (EUR-Lex reuse policy) | **Yes** | Attribution to EUR-Lex |
| CSA CCM / AICM | CSA-owned | **Confirm with CSA legal** | We are CSA but need internal confirmation |
| ATT&CK / ATLAS | Apache 2.0 | Yes but unnecessary | Excellent per-item sources exist |
| CVE data | CVE Terms of Use | Yes but unnecessary | cvelistV5 already provides this |
| ISO 27001/27002 | Paywalled, copyrighted | **NO** | Registry description only |
| IEEE standards | Paywalled, copyrighted | **NO** | Registry description only |
| Twitter/X posts | User content, platform ToS | **Carefully** | Archive for preservation, cite original |
| Reddit posts | User content, Reddit ToS | **Carefully** | Archive for preservation, cite original |

## Data Repository Structure (SecID 2.0)

> **Historical note (2026-11-06):** Earlier drafts of this document (and [`SecID#64`](https://github.com/CloudSecurityAlliance/SecID/issues/64)) proposed per-type repositories (`SecID-weakness`, `SecID-control`, …) and a `data_federation` registry field, and [`ADR-011`](../../DECISIONS.md#adr-011-data-repositories-shard-by-region-keyed-by-the-authority-behind-the-material) explored regional repositories (`SecID-Data-North-America`, …). Those were superseded by [`ADR-010`](../../DECISIONS.md#adr-010-secid-20-serves-content-the-registry-is-unchanged), [`ADR-013`](../../DECISIONS.md#adr-013-a-single-source-corpus-promotes-out-of-its-region-repository-at-a-size-threshold), [`ADR-014`](../../DECISIONS.md#adr-014-every-secid-data--repository-uses-one-layout-mirroring-the-registry), and the 2026-11-06 **Domain-First Exhaustive Extraction & Zero-Egress GitHub Serving** decision below.

### 1. Zero-Egress Serving via GitHub (`raw.githubusercontent.com`)

SecID 2.0 serves public structured content directly from GitHub repositories under `CloudSecurityAlliance` via `raw.githubusercontent.com` (shelving Cloudflare R2 / S3 serving so transfer and storage costs stay `$0` and every dataset is trivially `git clone`-able and git-tag-versioned):

- **The registry schema is unchanged (`ADR-010`):** Registry `match_nodes` point to extracted content using standard `data.url` templates (on subpath child nodes) and `data.urls[]` entries (on document-level source nodes) with `"format": "json"` (or `"markdown"`) and `"parsability": "structured"` (`content_type` is omitted on `raw.githubusercontent.com` URLs because GitHub serves raw files with HTTP `Content-Type: text/plain`). No custom `data_federation` field is used.
- **`SecID-Service` never proxies payload bytes:** The Worker resolves the SecID to its deterministic `raw.githubusercontent.com` URL (alongside the official publisher URL), and callers/SDKs fetch the JSON or Markdown directly from GitHub's CDN.

### 2. Upstream Catalog Discovery, Domain-First Exhaustive Local Extraction & Sizing Before Committing to Git

Because **`git rm` does not reclaim space in `.git/objects/pack`** (without history-rewriting force-pushes that break clones and tags), we **never** commit half-extracted or binary-bloated content to a `SecID-Data*` repository with the plan to delete or split it later:

1. **Upstream catalog & publishing architecture discovery first ([`#244`](https://github.com/CloudSecurityAlliance/SecID/issues/244)):**
   - Before running bulk extraction for a jurisdiction or standards authority, map its complete upstream publishing architecture and catalog:
     - **Jurisdictions** split laws across multiple official portals by lifecycle stage (e.g., US bills on `congress.gov`, enacted Public Laws on `govinfo.gov`, codified U.S. Code on `uscode.house.gov`, codified agency regulations on `ecfr.gov`, and daily rules/Executive Orders on `federalregister.gov` and `whitehouse.gov`; Canada bills on `parl.ca` and consolidated Acts/Regulations on `laws-lois.justice.gc.ca`; UK Acts/SIs on `legislation.gov.uk`; EU CELEX texts on `eur-lex.europa.eu`; Japan laws on `laws.e-gov.go.jp`; Germany federal laws on `gesetze-im-internet.de`).
     - **Standards & control authorities** (`nist.gov`, `mitre.org`+`cve.org`, `cisa.gov`, `fedramp.gov`, `cloudsecurityalliance.org`, `owasp.org`+`cyclonedx.org`, `openssf.org`+`spdx.dev`, `ietf.org`) are inventoried against their full upstream catalogs before extraction.
     - **Paywalled / membership SDOs (`Rule 0`, [`#255`](https://github.com/CloudSecurityAlliance/SecID/issues/255)):** `iso.org`+`iec.ch`, `isaca.org`, `isc2.org`, `cisecurity.org`, `pcisecuritystandards.org`, `aicpa.org`, `hitrustalliance.net`, `etsi.org`+`cen.eu`, `sans.org`+`giac.org`, and `comptia.org` have `0 MB` of copyrighted prose in public `SecID-Data*` repositories, but their complete standard and control/clause ID catalogs (`known_values` / child `match_nodes`) are registered in `CloudSecurityAlliance/SecID/registry/` so resolution and crosswalks work 100%.
2. **Exhaustive local extraction & text-only policy (no binary bloat):**
   - Only deterministic, human-diffable text (`.json`, `.md`, `.csv`, `.yaml`) enters `SecID-Data*` git history. Binary source files (`.pdf`, `.xlsx`, `.docx`, `.zip`) and PDF-extracted page/figure images (`.jpeg`, `.png`) must never be committed to `SecID-Data*` (text-only JSON/Markdown delta-compresses ~5–10x in Git — e.g., `SecID-Data-disa.mil` holds 54,185 JSON files / 245 MB on disk in an **18 MiB** `.git` packfile).
3. **Umbrella Domain Grouping, Sector Metadata & Legal-Layer Modeling ([`#245`](https://github.com/CloudSecurityAlliance/SecID/issues/245), [`#256`](https://github.com/CloudSecurityAlliance/SecID/issues/256)):**
   - **Umbrella grouping preserves `ADR-014` paths:** Rolling a sibling domain (such as `cve.org` into `SecID-Data-mitre.org`, `cyclonedx.org` and `owaspai.org` into `SecID-Data-owasp.org`, `ico.org.uk` into `SecID-Data-uk`, `gesetze-im-internet.de` into `SecID-Data-de`, `cert-in.org.in` and `rbi.org.in` into `SecID-Data-in`, `tc260.org.cn` into `SecID-Data-cn`, or `uscode.house.gov` into `SecID-Data-gov`) never changes its SecID namespace or its internal `data/<type>/<tld>/<domain>/<name>/<version>/...` path.
   - **Sector (`financial`, `healthcare`, `transportation`, `energy`, `telecom`, `government`, `cross-sector`) is a metadata/index axis, not a repository boundary:** National banking/healthcare rules (`fsa.go.jp`, `mhlw.go.jp`, `govinfo.gov/hipaa`, `ecfr.gov`, `europa.eu/dora`) live in their jurisdiction repository and use the existing `tags.sector` / `data.tags.sector` metadata field + cross-repo `indexes/by-sector/<sector>.json` manifests.
   - **Point Once (No Registry URL Churn):** `dataset-public-laws-regulations-standards` is gradually phased out into `SecID-Data*` (with proprietary PCI DSS and HITRUST moved to `dataset-private`). Registry `raw.githubusercontent.com` links are added **only once** a corpus has landed in its permanent `SecID-Data*` repository.

### 3. Canonical List of Separate `SecID-Data-*` Repositories

Below is the canonical inventory of all **28 `SecID-Data-*` repositories** under `CloudSecurityAlliance` — grouped into (A) US Government & Global Standards Anchor Authorities, (B) Major National & Supranational Jurisdictions, (C) Shared General Repository, and (D) Defensive Upstream Dataset Mirror Forks.

#### 3A. US Government & Global Standards Anchor Authorities (7 Repositories)

| Repository (`CloudSecurityAlliance/*`) | Status / Tracking Issue | Primary & Rolled-In Umbrella Domains (`ADR-014` paths preserved) | Measured / Target Text Footprint | Rationale for Separate Repository |
|---|---|---|---|---|
| **[`SecID-Data-disa.mil`](https://github.com/CloudSecurityAlliance/SecID-Data-disa.mil)** | **Live** ([`#64`](https://github.com/CloudSecurityAlliance/SecID/issues/64), [`PR #237`](https://github.com/CloudSecurityAlliance/SecID/pull/237)) | `disa.mil`, `cyber.mil` (`data/control/mil/disa/...`) | `245 MB` unpacked (`54,185` JSON files across `175` STIGs/SRGs, `53,674` rules) / **`18 MiB`** `.git` packfile | Exceeds the 50–100 MB threshold on its own; quarterly compilation tags (`vYYYY.MM`) delta-compress ~13:1 within a dedicated packfile. |
| **`SecID-Data-cloudsecurityalliance.org`** | Planned ([`#238`](https://github.com/CloudSecurityAlliance/SecID/issues/238)) | `cloudsecurityalliance.org` (`data/<type>/org/cloudsecurityalliance/...`) | `47.4 MB` pure text in `dataset-public` (`94.2 MB` raw across `242` files); `~50–75 MB` full corpus | First-party CSA flagship corpus (CCM, AICM, CAIQ, AI-CAIQ, SDP, Glueck, auditing/implementation guidelines, Cloud Security Glossary). |
| **`SecID-Data-nist.gov`** | Planned ([`#239`](https://github.com/CloudSecurityAlliance/SecID/issues/239)) | `nist.gov`, `csrc.nist.gov`, `nvd.nist.gov`, `pages.nist.gov` (`data/<type>/gov/nist/...`) | `135.8 MB` pure text in `dataset-public` (`317.8 MB` raw across `688` files) + `usnistgov/oscal-content` (`93.8 MB`) | Largest standards corpus in `dataset-public` (SP 800/1800 series, CSF, AI RMF, FIPS, CSRC Glossary, OSCAL/CPE schemas). |
| **`SecID-Data-fedramp.gov`** | Planned ([`#240`](https://github.com/CloudSecurityAlliance/SecID/issues/240)) | `fedramp.gov` (`data/<type>/gov/fedramp/...`) | `23.7 MB` pure text in `dataset-public` (`31.9 MB` raw across `100` files) + `GSA/fedramp-automation` (`144.6 MB`) | High-demand US federal cloud authorization anchor (Rev 4/5 High/Moderate/Low/LI-SaaS baselines, 20x KSIs, playbooks, guidance). |
| **`SecID-Data-cisa.gov`** | Planned ([`#241`](https://github.com/CloudSecurityAlliance/SecID/issues/241)) | `cisa.gov`, `niccs.cisa.gov`, `us-cert.cisa.gov` (`data/<type>/gov/cisa/...`) | `10.1 MB` pure text in `dataset-public` (`14.1 MB` raw across `98` files); `~30–60 MB` full corpus | Primary US operational cyber authority (KEV catalog, SCuBA baselines, CPGs, ZTMM, BOD/ED directives, GovCAR, NICCS Glossary). |
| **`SecID-Data-mitre.org`** | Planned ([`#245`](https://github.com/CloudSecurityAlliance/SecID/issues/245)) | `mitre.org` (`attack.mitre.org`, `cwe.mitre.org`, `capec.mitre.org`, `d3fend.mitre.org`, `atlas.mitre.org`, `emb3d.mitre.org`, `saf.mitre.org`) + rolled-in **`cve.org`** (`data/<type>/org/mitre/...` and `data/<type>/org/cve/...`) | `41.5 MB` pure text in `dataset-public`; `~150–250 MB` unpacked (`~25–40 MB` `.git` packfile) across full MITRE + `cve.org` program docs | MITRE operates `cve.org` alongside CWE, CAPEC, D3FEND, EMB3D, FiGHT, MAEC, CTID mappings, and CVE program schemas/glossaries. |
| **`SecID-Data-owasp.org`** | Planned ([`#262`](https://github.com/CloudSecurityAlliance/SecID/issues/262), [`#253`](https://github.com/CloudSecurityAlliance/SecID/issues/253)) | `owasp.org` + rolled-in **`cyclonedx.org`** and **`owaspai.org`** (`data/<type>/org/owasp/...`, `data/<type>/org/cyclonedx/...`, `data/<type>/org/owaspai/...`) | `~4.15 GB` raw across 60+ upstream OWASP GitHub repos → **`~45–90 MB`** clean multi-version structured text | Strips ~4 GB of upstream images/translations/website bloat into uniform per-requirement JSON/Markdown across ASVS, MASVS, MASTG, WSTG, SAMM, ~110 Cheat Sheets, Top 10 family, CRS, CycloneDX, and OWASP AI Exchange. |

#### 3B. Major National & Supranational Jurisdictions (10 Repositories)

Each major jurisdiction gets a single dedicated repository containing all of its national/state statutes, codified regulations, national cyber controls, sector regulator mandates (`tags.sector`), and national cybersecurity strategies so practitioners in that jurisdiction can clone one repository:

| Repository (`CloudSecurityAlliance/*`) | Status / Tracking Issue | Primary & Rolled-In Jurisdiction Domains (`ADR-014` paths preserved) | Measured / Target Text Footprint | Jurisdiction Coverage |
|---|---|---|---|---|
| **`SecID-Data-europa.eu`** | Planned ([`#242`](https://github.com/CloudSecurityAlliance/SecID/issues/242)) | `europa.eu`, `eur-lex.europa.eu`, `enisa.europa.eu`, `edpb.europa.eu`, `eba.europa.eu`, `esma.europa.eu`, `eiopa.europa.eu`, `ecb.europa.eu`, `cert.europa.eu` | `14.1 MB` pure text in `dataset-public` (`20.8 MB` raw across `73` files); `~50–100 MB` full corpus | European Union regulations & directives (GDPR, AI Act, NIS2, DORA, CRA, eIDAS2, EHDS, Cyber Solidarity Act), Delegated/Implementing Acts, ENISA frameworks (EUCS), EDPB guidelines, and EBA/ESMA/EIOPA RTS. |
| **`SecID-Data-gov`** | Planned ([`#247`](https://github.com/CloudSecurityAlliance/SecID/issues/247)) | All non-anchor US Federal & 50 State `.gov`/`.mil` domains (`congress.gov`, `govinfo.gov`, `ecfr.gov`, `federalregister.gov`, `whitehouse.gov`, `acquisition.gov`, `sec.gov`, `hhs.gov`, `treasury.gov`, `ftc.gov`, `fda.gov`, `nsa.gov`, state `.gov`) + rolled-in **`uscode.house.gov`** | `19.3 MB` pure text in `dataset-public` (`45.7 MB` raw across `46` non-anchor `.gov` domains); `~60–120 MB` full corpus | US Federal statutes (Public Laws & US Code), codified regulations (`eCFR` Titles 6, 12, 15, 16, 17, 21, 32, 45, 47, 48 incl. HIPAA, GLBA, FAR/DFARS/CMMC, SEC, CIRCIA), White House EOs/OMB memos, NSA guidance, and all 50 US state privacy/breach/cyber laws (NYDFS 23 NYCRR 500, CCPA/CPRA, StateRAMP/GovRAMP). |
| **`SecID-Data-ca`** | Planned ([`#248`](https://github.com/CloudSecurityAlliance/SecID/issues/248)) | `parl.ca`, `laws-lois.justice.gc.ca`, `cyber.gc.ca`, `canada.ca`, `tbs-sct.gc.ca`, `publicsafety.gc.ca`, `priv.gc.ca`, `osfi-bsif.gc.ca`, provincial `.ca` (`ontario.ca`, `alberta.ca`, `quebec.ca`, `gov.bc.ca`) | `14.5 MB` pure text in `dataset-public` (`15.3 MB` raw across `63` files); upstream `justicecanada/laws-lois-xml` is `317.8 MB` (`~30–60 MB` security/privacy slice) | Canada Federal bills (`parl.ca` C-26, C-27, C-8) & consolidated Acts/Regulations (`justice.gc.ca` PIPEDA, Privacy Act), CCCS ITSG-33 (`ITSP.10.040`) & Cloud Baseline, TBS directives, OSFI B-13/B-10, and provincial statutes (Quebec Law 25, Ontario PHIPA, BC/Alberta PIPA). |
| **`SecID-Data-jp`** | Planned ([`#249`](https://github.com/CloudSecurityAlliance/SecID/issues/249)) | `laws.e-gov.go.jp`, `nisc.go.jp`, `cyber.go.jp`, `cas.go.jp`, `meti.go.jp`, `ipa.go.jp`, `ismap.go.jp`, `fsa.go.jp`, `mhlw.go.jp`, `mlit.go.jp`, `ppc.go.jp`, `soumu.go.jp`, `digital.go.jp`, `mod.go.jp` + rolled-in **`cryptrec.go.jp`**, **`jpcert.or.jp`**, **`jipdec.or.jp`**, **`fisc.or.jp`** | `11.6 MB` pure text in `dataset-public` (`24.8 MB` raw across `242` files in `13` Japanese authorities); `~30–60 MB` full corpus | Japan e-Gov Law XML statutes (Basic Act on Cybersecurity, APPI, Active Cyber Defense Act, Economic Security Promotion Act), NISC Unified Standards, METI/IPA CPSF, ISMAP, JC-STAR, CRYPTREC, FSA financial guidelines, MHLW medical 3-ministry guidelines, MLIT UN-R155/R156, PPC APPI guidelines, and Soumu cloud/telecom guidelines. |
| **`SecID-Data-uk`** | Planned ([`#250`](https://github.com/CloudSecurityAlliance/SecID/issues/250)) | `legislation.gov.uk`, `ncsc.gov.uk`, `gov.uk` + rolled-in non-`.gov.uk` UK regulators **`ico.org.uk`**, **`fca.org.uk`**, and **`bankofengland.co.uk`** | `6.8 MB` pure text in `dataset-public` (`10.1 MB` raw across `47` files); `~25–50 MB` full corpus | UK Primary Acts & Statutory Instruments (`legislation.gov.uk` UK GDPR, DPA 2018, NIS Regulations, PSTI Act, Online Safety Act), NCSC Cyber Assessment Framework (CAF), Cyber Essentials, 14 Cloud Security Principles, DSIT AI/App Store/Enterprise Cyber Codes, ICO Age Appropriate Design & AI guidance, and FCA/PRA/BoE CBEST & operational resilience rules. |
| **`SecID-Data-de`** | Planned ([`#251`](https://github.com/CloudSecurityAlliance/SecID/issues/251)) | `bsi.bund.de`, `bmi.bund.de`, `bundesregierung.de`, `bfdi.bund.de` + rolled-in **`gesetze-im-internet.de`** and **`bafin.de`** | `8.9 MB` pure text in `dataset-public` (`11.5 MB` raw across `22` files); upstream `bundestag/gesetze` is `440.7 MB` (`~30–60 MB` security/privacy slice) | German federal statutes (`gesetze-im-internet.de` BSIG, NIS2UmsuCG, BDSG, KRITISV, IT-SiG 2.0, TDDDG), BSI IT-Grundschutz Compendium, BSI C5 (Cloud Computing Compliance Criteria Catalogue), AIC4, Technical Guidelines (`TR-02102`, `TR-03108`), BfDI data protection guidance, and BaFin BAIT/VAIT/KAIT/ZAIT. |
| **`SecID-Data-au`** | Planned ([`#258`](https://github.com/CloudSecurityAlliance/SecID/issues/258), [`#252`](https://github.com/CloudSecurityAlliance/SecID/issues/252)) | `legislation.gov.au`, `cyber.gov.au`, `asd.gov.au`, `homeaffairs.gov.au`, `cisc.gov.au`, `apra.gov.au`, `oaic.gov.au`, state `.gov.au` (`nsw.gov.au`, `vic.gov.au`, `qld.gov.au`) | `4.1 MB` pure text in `dataset-public` (`25` files); `~25–50 MB` full corpus | Australia Commonwealth Acts (`legislation.gov.au` Privacy Act 1988, SOCI Act 2018, Cyber Security Act 2024), ASD/ACSC Information Security Manual (`ISM`) & Essential Eight, APRA CPS 234 & CPS 230, OAIC APP guidelines, and state cyber frameworks. |
| **`SecID-Data-sg`** | Planned ([`#259`](https://github.com/CloudSecurityAlliance/SecID/issues/259), [`#252`](https://github.com/CloudSecurityAlliance/SecID/issues/252)) | `sso.agc.gov.sg`, `csa.gov.sg`, `mas.gov.sg`, `pdpc.gov.sg`, `imda.gov.sg`, `aiverifyfoundation.sg`, `tech.gov.sg`, `gov.sg` | `3.8 MB` pure text in `dataset-public` (`19` files); `~15–35 MB` full corpus | Singapore Statutes Online (`sso.agc.gov.sg` Cybersecurity Act, PDPA, CMA), CSA CCoP/CLS/Safe App Standard, MAS Technology Risk Management (`TRM`) & Cyber Hygiene Notices, PDPC guidelines, and IMDA MTCS/IoT/AI Verify frameworks. |
| **`SecID-Data-in`** | Planned ([`#260`](https://github.com/CloudSecurityAlliance/SecID/issues/260), [`#252`](https://github.com/CloudSecurityAlliance/SecID/issues/252)) | `indiacode.nic.in`, `egazette.gov.in`, `meity.gov.in`, `nciipc.gov.in`, `sebi.gov.in`, `irdai.gov.in`, `uidai.gov.in`, `abdm.gov.in` + rolled-in **`cert-in.org.in`** and **`rbi.org.in`** | `4.9 MB` pure text in `dataset-public` (`24` files); `~20–45 MB` full corpus | India statutes (DPDP Act 2023, IT Act 2000), MeitY Rules, CERT-In 2022 Cyber Security Directions, NCIIPC guidelines, RBI Cyber Security Framework & Master Directions, SEBI CSCRF, IRDAI guidelines, and UIDAI Aadhaar regulations. |
| **`SecID-Data-cn`** | Planned ([`#261`](https://github.com/CloudSecurityAlliance/SecID/issues/261), [`#252`](https://github.com/CloudSecurityAlliance/SecID/issues/252)) | `npc.gov.cn`, `flk.npc.gov.cn`, `cac.gov.cn`, `gov.cn`, `samr.gov.cn` (`openstd.samr.gov.cn`), `miit.gov.cn`, `pbc.gov.cn`, `nfra.gov.cn` + rolled-in **`tc260.org.cn`** | `4.7 MB` pure text in `dataset-public` (`21` files); `~25–60 MB` full corpus | PRC statutes (Cybersecurity Law `CSL`, Data Security Law `DSL`, Personal Information Protection Law `PIPL`, Cryptography Law), CAC regulations & cross-border data measures, and SAC/TC260 national standards (`GB/T 22239-2019` MLPS 2.0, `GB/T 35273`, GenAI security standards). |

#### 3C. Shared General Repository (1 Repository)

| Repository (`CloudSecurityAlliance/*`) | Status / Tracking Issue | Scope & Umbrella Domains Included | Measured / Target Text Footprint | Promotion Rule |
|---|---|---|---|---|
| **`SecID-Data`** | Planned ([`#243`](https://github.com/CloudSecurityAlliance/SecID/issues/243), [`#254`](https://github.com/CloudSecurityAlliance/SecID/issues/254), [`#203`](https://github.com/CloudSecurityAlliance/SecID/issues/203), [`#62`](https://github.com/CloudSecurityAlliance/SecID/issues/62)) | All remaining `<50 MB` public open standards, Linux Foundation / OpenSSF / SPDX (`spdx.dev`) / OpenVEX (`openvex.dev`) / SLSA (`slsa.dev`) / CNCF (`cncf.io`, `kubernetes.io`) umbrella ([`#254`](https://github.com/CloudSecurityAlliance/SecID/issues/254)), IETF (`ietf.org`, `rfc-editor.org`), FIRST (`first.org` CVSS/EPSS/SSVC/TLP), OASIS (`oasis-open.org` CSAF/STIX/TAXII/CACAO/ODRL), CIS Controls metadata, SAFECode, FinOps, C2PA, format schemas ([`#203`](https://github.com/CloudSecurityAlliance/SecID/issues/203)), cross-domain glossaries ([`#62`](https://github.com/CloudSecurityAlliance/SecID/issues/62)), vendor capability baselines, and smaller national jurisdictions (`kr`, `br`, `fr`, `ch`, `nl`, `es`, `it`, `ae`, `sa`, `za`, `il`, `nz`, `mx`, etc.) | `~85 MB` pure text currently in `dataset-public` across `~200` smaller domains (`~17 MB` compressed) | Any domain or national jurisdiction whose full text extraction crosses **~50–100 MB** promotes out into its own `SecID-Data-<domain/cc>` repository BEFORE bulk history is committed. |

#### 3D. Defensive Upstream Dataset Forks / Mirror Insurance (10 Repositories, Umbrella [`#246`](https://github.com/CloudSecurityAlliance/SecID/issues/246))

For large, authoritative upstream GitHub vulnerability, advisory, TTP, and schema repositories, SecID points directly to the upstream repository in day-to-day resolution (`Step 1` of the Decision Flowchart) and maintains a **gated-sync public GitHub fork** under `CloudSecurityAlliance` as insurance against upstream deletion, restructuring, or corruption (sharing GitHub's parent object store at `$0` storage quota):

| Mirror Repository (`CloudSecurityAlliance/*`) | Tracking Issue | Upstream Source Repository | Measured Upstream Git Size | Primary SecID Namespace(s) Protected |
|---|---|---|---|---|
| **`SecID-Data-cvelistV5`** | [`#263`](https://github.com/CloudSecurityAlliance/SecID/issues/263) | [`CVEProject/cvelistV5`](https://github.com/CVEProject/cvelistV5) | `3,253.2 MB` (`~3.25 GB`) | `secid:advisory/mitre.org/cve` (335,000+ CVE v5 JSON records) |
| **`SecID-Data-advisory-database`** | [`#264`](https://github.com/CloudSecurityAlliance/SecID/issues/264) | [`github/advisory-database`](https://github.com/github/advisory-database) | `3,503.0 MB` (`~3.50 GB`) | `secid:advisory/github.com/ghsa`, `secid:advisory/google.com/osv` |
| **`SecID-Data-vulnrichment`** | [`#265`](https://github.com/CloudSecurityAlliance/SecID/issues/265) | [`cisagov/vulnrichment`](https://github.com/cisagov/vulnrichment) | `375.7 MB` | `secid:advisory/cisa.gov/vulnrichment` (CISA ADP SSVC/KEV/CVSS/CWE enrichment) |
| **`SecID-Data-attack-stix-data`** | [`#266`](https://github.com/CloudSecurityAlliance/SecID/issues/266) | [`mitre-attack/attack-stix-data`](https://github.com/mitre-attack/attack-stix-data) | `134.3 MB` | `secid:ttp/mitre.org/attack` (Enterprise, Mobile & ICS STIX 2.1 bundles) |
| **`SecID-Data-cve-schema`** | [`#267`](https://github.com/CloudSecurityAlliance/SecID/issues/267) | [`CVEProject/cve-schema`](https://github.com/CVEProject/cve-schema) | `482.8 MB` | `secid:reference/cve.org/cve-schema` (CVE Record Format v5.x JSON Schemas) |
| **`SecID-Data-osv-schema`** | [`#268`](https://github.com/CloudSecurityAlliance/SecID/issues/268) | [`ossf/osv-schema`](https://github.com/ossf/osv-schema) | `0.9 MB` | `secid:reference/ossf.github.io/osv-schema` (OSV JSON Schema & ecosystems) |
| **`SecID-Data-CSAF`** | [`#269`](https://github.com/CloudSecurityAlliance/SecID/issues/269) | [`cisagov/CSAF`](https://github.com/cisagov/CSAF) | `59.0 MB` | `secid:advisory/cisa.gov/csaf` (CISA ICS & Medical CSAF 2.0 advisories) |
| **`SecID-Data-vulndb`** | [`#270`](https://github.com/CloudSecurityAlliance/SecID/issues/270) | [`golang/vulndb`](https://github.com/golang/vulndb) | `53.8 MB` | `secid:advisory/go.dev/vulndb` (`GO-YYYY-NNNN` advisories) |
| **`SecID-Data-rustsec-advisory-db`** | [`#271`](https://github.com/CloudSecurityAlliance/SecID/issues/271) | [`rustsec/advisory-db`](https://github.com/rustsec/advisory-db) | `44.5 MB` | `secid:advisory/rustsec.org/advisories` (`RUSTSEC-YYYY-NNNN` advisories) |
| **`SecID-Data-pypa-advisory-database`** | [`#272`](https://github.com/CloudSecurityAlliance/SecID/issues/272) | [`pypa/advisory-database`](https://github.com/pypa/advisory-database) | `21.9 MB` | `secid:advisory/pypi.org/advisory-db` (`PYSEC-YYYY-NNN` advisories) |

### 4. Standard Repository Layout (`ADR-014`)

Every `SecID-Data*` repository uses the identical layout established by [`SecID-Data-disa.mil`](https://github.com/CloudSecurityAlliance/SecID-Data-disa.mil), mirroring the registry's reverse-DNS convention so one path-derivation algorithm works everywhere:

```
SecID-Data-<shard>/
├── README.md                           # Corpus overview, provenance, refresh procedure
├── AGENTS.md                           # Canonical agent instructions (CLAUDE.md / GEMINI.md shims)
├── LICENSE                             # Repo license + per-source attribution in provenance
├── data/                               # Extracted content, addressed mechanically by SecID
│   └── <type>/
│       └── <tld>/<domain>/             # Reverse-DNS (e.g. control/mil/disa, control/org/cloudsecurityalliance)
│           └── <name>/
│               └── <version>/
│                   ├── <doc>.json      # Document-level metadata, provenance, and item index
│                   └── rules/          # (or items/) Per-item JSON keyed by subpath ID
│                       └── <id>.json
├── schemas/                            # JSON Schemas validated in CI
├── scripts/                            # Deterministic acquisition, extraction, and validation scripts
├── indexes/                            # Generated corpus and provenance manifests
└── docs/                               # Source notes and extraction documentation
```

A SecID maps to a path mechanically:

```
secid:control/disa.mil/rhel-9@V2R9#V-257505
  -> data/control/mil/disa/rhel-9/V2R9/rules/V-257505.json
```

### 5. Connecting Registry to Data

Registry entries link to `SecID-Data*` using standard `match_node` URL fields (no special schema extension):

- **Document-level node (`match_nodes[]`):** Includes a `lookup` entry in `data.urls[]` (and on `versions_available[].url`) pointing to the document JSON/Markdown in `SecID-Data*`:
  ```json
  {
    "type": "lookup",
    "url": "https://raw.githubusercontent.com/CloudSecurityAlliance/SecID-Data-disa.mil/main/data/control/mil/disa/aaa-services/V2R2/stig.json",
    "format": "json",
    "parsability": "structured",
    "note": "Extracted document metadata and rule index in SecID-Data-disa.mil."
  }
  ```
- **Item/subpath child node (`children[]`):** Sets `data.url` to the per-item `raw.githubusercontent.com` template:
  ```json
  {
    "url": "https://raw.githubusercontent.com/CloudSecurityAlliance/SecID-Data-disa.mil/main/data/control/mil/disa/aaa-services/V2R2/rules/{id}.json",
    "format": "json",
    "parsability": "structured"
  }
  ```

## Decision Flowchart

```
Q: Should this data be in a SecID-Data* repo?

Step 0: Is the license compatible? (See license table above)
  NO → STOP. Registry entry with description + access URL only (or private repo for internal use).
  YES → Continue.

Step 1: Does a reliable, machine-readable, per-item source already exist upstream?
  YES → Don't host. Point directly to upstream in the registry entry.
        (CVE → cvelistV5, CWE → cwe-api.mitre.org REST API, ATT&CK → attack-stix-data, GHSA/OSV → api.osv.dev)
  NO → Continue.

Step 2: Aggressively discover and extract ALL SecID-resolvable content for the domain/jurisdiction locally (Rule 1/2/3).
  → Strip binary files (.pdf, .xlsx, .jpeg, .png); keep deterministic .json / .md / .csv.
  → Measure total unpacked and git-packed size.

Step 3: Place in the permanent SecID-Data* repository and link once:
  → Anchor / >50-100 MB domain or TLD → SecID-Data-<domain/tld> (e.g. SecID-Data-nist.gov, SecID-Data-cisa.gov, SecID-Data-europa.eu)
  → Smaller domain → SecID-Data
  → Wire raw.githubusercontent.com URLs into CloudSecurityAlliance/SecID registry nodes once landed.
```
