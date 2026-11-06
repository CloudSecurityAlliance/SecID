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

- **The registry schema is unchanged (`ADR-010`):** Registry `match_nodes` point to extracted content using standard `data.url` templates (on subpath child nodes) and `data.urls[]` entries (on document-level source nodes) with `"format": "json"` (or `"markdown"`), `"content_type": "application/json"`, and `"parsability": "structured"`. No custom `data_federation` field is used.
- **`SecID-Service` never proxies payload bytes:** The Worker resolves the SecID to its deterministic `raw.githubusercontent.com` URL (alongside the official publisher URL), and callers/SDKs fetch the JSON or Markdown directly from GitHub's CDN.

### 2. Domain-First Exhaustive Local Extraction & Sizing Before Committing to Git

Because **`git rm` does not reclaim space in `.git/objects/pack`** (without history-rewriting force-pushes that break clones and tags), we **never** commit half-extracted or binary-bloated content to a `SecID-Data*` repository with the plan to delete or split it later:

1. **Exhaustive local extraction first:** For any target domain (`mitre.org`, `cloudsecurityalliance.org`, `nist.gov`, `cisa.gov`, `fedramp.gov`, `europa.eu`, etc.) or jurisdiction (`.gov`, `.ca`, `.uk`, `.de`, `.jp`), we aggressively discover and extract **every** SecID-resolvable artifact for that domain/jurisdiction locally first.
2. **Text-only in Git (no binary bloat):** Only deterministic, human-diffable text (`.json`, `.md`, `.csv`, `.yaml`) enters `SecID-Data*` git history. Binary source files (`.pdf`, `.xlsx`, `.docx`, `.zip`) and PDF-extracted page/figure images (`.jpeg`, `.png`) must never be committed to `SecID-Data*` (text-only JSON/Markdown delta-compresses ~10:1 in Git — e.g., `SecID-Data-disa.mil` holds 54,185 JSON files / 245 MB on disk in an **18 MiB** `.git` packfile).
3. **Measure, then choose the repository boundary:**
   - **Anchor authorities & large domains (>50–100 MB unpacked or high-volume/high-cadence):** Get their own dedicated `CloudSecurityAlliance/SecID-Data-<domain>` or `SecID-Data-<tld>` repository from day one:
     - `CloudSecurityAlliance/SecID-Data-disa.mil` *(live — 175 STIGs/SRGs, 53,674 rules)*
     - `CloudSecurityAlliance/SecID-Data-nist.gov` *(SP 800-53, CSF, AI RMF, 800-171, SP series, CSRC Glossary)*
     - `CloudSecurityAlliance/SecID-Data-cisa.gov` *(SCuBA baselines, CPGs, ZTMM, ICS/KEV guidance)*
     - `CloudSecurityAlliance/SecID-Data-fedramp.gov` *(High/Moderate/Low/LI-SaaS baselines, KSIs, guidance)*
     - `CloudSecurityAlliance/SecID-Data-cloudsecurityalliance.org` *(CCM, AICM, CAIQ, AI-CAIQ, CSA guidance)*
     - `CloudSecurityAlliance/SecID-Data-europa.eu` *(GDPR, AI Act, NIS2, DORA, CRA, ENISA)*
     - Jurisdiction/TLD shards where appropriate (`SecID-Data-gov`, `SecID-Data-ca`, `SecID-Data-uk`, `SecID-Data-de`, `SecID-Data-jp`) to stay comfortably below GitHub's 1 GB repository limit without creating hundreds of tiny repos.
   - **Smaller domains (<50 MB when fully extracted):** Go into the general `CloudSecurityAlliance/SecID-Data` repository.
4. **Point Once (No Registry URL Churn):**
   - `CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards` (which predates SecID) is gradually phased out into `SecID-Data*`.
   - We **never** point `SecID` registry nodes at `dataset-public-laws-regulations-standards`. Registry `raw.githubusercontent.com` links are added **only once** a domain's content has landed in its permanent `SecID-Data*` repository.

### 3. Standard Repository Layout (`ADR-014`)

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

### 4. Connecting Registry to Data

Registry entries link to `SecID-Data*` using standard `match_node` URL fields (no special schema extension):

- **Document-level node (`match_nodes[]`):** Includes a `lookup` entry in `data.urls[]` (and on `versions_available[].url`) pointing to the document JSON/Markdown in `SecID-Data*`:
  ```json
  {
    "type": "lookup",
    "url": "https://raw.githubusercontent.com/CloudSecurityAlliance/SecID-Data-disa.mil/main/data/control/mil/disa/aaa-services/V2R2/stig.json",
    "format": "json",
    "content_type": "application/json",
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
