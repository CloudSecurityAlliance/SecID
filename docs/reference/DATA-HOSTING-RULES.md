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

## Data Repository Structure

### Federation Model

Data is hosted in type-specific repos in the `CloudSecurityAlliance-DataSets` GitHub organization:

```
CloudSecurityAlliance-DataSets/
├── SecID-weakness/          # CWE per-record, OWASP per-item (Rule 2)
├── SecID-control/           # CCM, AICM, NIST CSF per-control (Rule 2)
├── SecID-regulation/        # GDPR, AI Act per-article (Rule 2)
├── SecID-disclosure/        # CNA details (Rule 2)
├── SecID-reference/         # Archived + synthesized content (Rules 1+3)
```

We don't need data repos for types with good existing sources:
- **SecID-advisory** — CVE/GHSA/vendor advisories all have machine-readable sources
- **SecID-ttp** — ATT&CK STIX and ATLAS YAML are excellent
- **SecID-entity** — lightweight metadata, fits in the registry itself

### Directory Layout

The path mirrors the SecID string: `secid:weakness/mitre.org/cwe#CWE-79` → `data/mitre.org/cwe/CWE-79.json`

```
SecID-weakness/
├── README.md                           # Repo overview, rules, how to use
├── CLAUDE.md                           # AI agent instructions
├── LICENSE.md                          # Repo-level license for our additions
├── LICENSES/                           # Per-source license files
│   ├── MITRE-CWE-TERMS-OF-USE.md      # CWE ToU reproduced in full
│   ├── OWASP-CC-BY-SA-4.0.md          # OWASP license
│   └── ...
├── scripts/                            # Extraction/synthesis pipelines
│   ├── split-cwe.py
│   ├── extract-owasp-top10.py
│   └── ...
├── data/
│   ├── README.md                       # "X namespaces, Y total items"
│   ├── mitre.org/
│   │   ├── README.md                   # "CWE — what it is, 944 weaknesses, source URL"
│   │   └── cwe/
│   │       ├── README.md               # "Per-CWE records, extracted from cwec_latest.xml"
│   │       ├── CWE-79.json
│   │       ├── CWE-89.json
│   │       └── ...
│   └── owasp.org/
│       ├── README.md                   # "OWASP weakness taxonomies"
│       ├── top10/
│       │   └── 2021/
│       │       ├── README.md           # "2021 edition, 10 items"
│       │       ├── A01.json
│       │       └── ...
│       └── llm-top10/
│           └── 2025/
│               ├── LLM01.json
│               └── ...
```

README.md at each level serves as the "index page" — explains what's at this level, how many items, where the data came from, and how to use it.

### Per-Item JSON Envelope

Every item file follows the same schema:

```json
{
  "secid": "secid:weakness/mitre.org/cwe#CWE-79",
  "schema_version": "1.0",

  "provenance": {
    "upstream_source": {
      "url": "https://cwe.mitre.org/data/xml/cwec_latest.xml.zip",
      "version": "4.14",
      "license": "MITRE CWE Terms of Use",
      "license_url": "https://cwe.mitre.org/about/termsofuse.html",
      "attribution": "© The MITRE Corporation. CWE™ is a trademark of The MITRE Corporation."
    },
    "processed_source": {
      "repo": "CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards",
      "path": "frameworks-guidance/industry/MITRE/CWE/CWE-Research-Concepts-1000.json",
      "url": "https://github.com/CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards/blob/main/frameworks-guidance/industry/MITRE/CWE/CWE-Research-Concepts-1000.json"
    },
    "extracted_at": "2026-04-04T00:00:00Z",
    "extraction_script": "scripts/split-cwe.py",
    "rule": 2,
    "rule_reason": "CWE source is a monolithic XML dump. Split into per-weakness JSON for AI agent consumption."
  },

  "content": {
    // Source-specific structured data — varies by namespace
  },

  "synthesis": {
    // Optional — only present when Rule 3 applies
    "model": "claude-opus-4-6",
    "generated_at": "2026-04-04T00:00:00Z",
    "summary": "...",
    "key_facts": ["..."],
    "related_secids": ["secid:advisory/mitre.org/cve#CVE-2024-XXXX"]
  }
}
```

Key fields:
- **`secid`** — the SecID string this item corresponds to
- **`provenance.upstream_source`** — where the original data came from, with license
- **`provenance.processed_source`** — where we processed/stored the bulk data (links to the datasets repo)
- **`provenance.rule`** — which hosting rule (1, 2, or 3) justifies hosting this data
- **`content`** — the actual data, format varies by namespace
- **`synthesis`** — AI-generated summary/extraction (optional, only for Rule 3 items)

### Linking to the Datasets Repo

When a bulk source has already been processed in the `dataset-public-laws-regulations-standards` repo, the provenance includes a `processed_source` field pointing to it:

```json
"processed_source": {
  "repo": "CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards",
  "path": "regulations-mandatory/EU/EU-GDPR-ACT/eu-gdpr-act.json",
  "url": "https://github.com/CloudSecurityAlliance-DataSets/dataset-public-laws-regulations-standards/blob/main/regulations-mandatory/EU/EU-GDPR-ACT/eu-gdpr-act.json"
}
```

This creates a traceable chain: upstream source → bulk processing → per-item split.

### Connecting Registry to Data

The registry entry gains a `data_federation` field in its data block, pointing to the data repo:

```json
{
  "data": {
    "data_federation": {
      "repo": "CloudSecurityAlliance-DataSets/SecID-weakness",
      "path_template": "data/mitre.org/cwe/{id}.json",
      "raw_url_template": "https://raw.githubusercontent.com/CloudSecurityAlliance-DataSets/SecID-weakness/main/data/mitre.org/cwe/{id}.json"
    }
  }
}
```

The SecID-Service can use `raw_url_template` to fetch per-item data on demand. Users can clone the repo for bulk access.

## Decision Flowchart

```
Q: Should this data be in a SecID-Data repo?

Step 0: Is the license compatible? (See license table above)
  NO → STOP. Registry entry with description + access URL only.
  YES → Continue.

Step 1: Does a reliable, machine-readable, per-item source already exist?
  YES → Don't host. Point to it in the registry entry.
        (CVE → cvelistV5, ATT&CK → STIX, GHSA → advisory-database)
  NO → Continue.

Step 2: Does the source exist but in a bad format? (PDF, Excel, giant XML, HTML)
  YES → Rule 2. Extract into per-item JSON. Host in SecID-Data-{type}.

Step 3: Might the source disappear? (tweets, pastes, ephemeral pages)
  YES → Rule 1. Archive raw content. Host in SecID-Data-reference.

Step 4: Is the raw source reliable but useful knowledge needs extraction?
  (Reddit thread → key facts, mailing list → timeline, blog series → summary)
  YES → Rule 3. Archive raw + synthesize. Host in SecID-Data-reference.

Step 5: None of the above?
  → Don't host. The registry entry with URLs is sufficient.
```

## V2 Scope Expansion

The reference type will expand significantly in V2 to cover sources that need archiving (Rule 1) or synthesis (Rule 3):

| Source | Rule(s) | What We Store |
|--------|---------|---------------|
| Twitter/X vulnerability disclosures | 1+3 | Raw thread + AI-synthesized structured disclosure |
| Bluesky security announcements | 1+3 | Raw posts + synthesized summary |
| Reddit /r/netsec discussions | 1+3 | Raw thread + AI-extracted key facts, timeline |
| Paste site disclosures | 1 | Raw paste + metadata |
| Mailing list threads (oss-security) | 3 | Raw emails + synthesized vulnerability report |
| Conference talk summaries | 3 | Metadata + AI summary of technique/findings |
| Blog post series | 1+3 | Archived content + consolidated analysis |

These all go in `SecID-reference/` since they're reference materials, regardless of whether they describe vulnerabilities (advisory), techniques (ttp), or other topics. The SecID type in the identifier will be `reference` — the content may cross-reference other types via `related_secids`.
