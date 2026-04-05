# SecID: Label It. Find It. Use It.

**A universal identifier for security knowledge**

Kurt Seifried · Chief Innovation Officer · Cloud Security Alliance
kseifried@cloudsecurityalliance.org · github.com/kurtseifried

secid.cloudsecurityalliance.org · v1.0 · April 2026

---

## The Problem

**Security knowledge exists — discovering and navigating it is the hard part**

- CVE records can contain links, but it's ad-hoc — no centralized way to **discover** all views of a vulnerability across MITRE, NVD, Red Hat, GitHub
- Navigating from CVE → CWE → ATT&CK → NIST controls is painful and fragile
- AI agents can browse websites, but we need resolution to be **fast, reliable, and structured**
- No one system makes it easy to discover connections between advisories, weaknesses, techniques, controls, and regulations

> The problem isn't that the knowledge doesn't exist — it's that there's no easy way to **discover** it, to **navigate** across it, and to **link and enrich** it.

---

## What SecID Is

**A phone book for security knowledge**

- **One consistent format** to reference anything:
  `secid:advisory/mitre.org/cve#CVE-2024-1234`
- **A registry** that tells you where to find it — URLs, APIs, lookup patterns
- **Not a new authority** — identifiers come from their sources. SecID indexes them.

> We don't replace CVE, CWE, or ATT&CK — we connect them.

---

## Familiar Building Blocks

**No new concepts to learn**

| Design Choice | Why |
|---|---|
| **Package URL grammar** | Millions of developers already know `pkg:type/namespace/name@version` |
| **DNS namespaces** | `mitre.org`, `nist.gov` — globally unique, self-registering, aids discovery |
| **Registry with URLs** | Given a SecID, get back URLs where that thing lives. Like DNS for security knowledge. |

> The innovation is applying proven infrastructure to security knowledge — not inventing new infrastructure.

---

## v1.0 — What's Live Today

**Released April 5, 2026**

| | |
|---|---|
| **10 types** | advisory · weakness · ttp · control · capability · methodology · disclosure · regulation · entity · reference |
| **709+ namespaces** | Covering CVE, CWE, ATT&CK, NIST, ISO, OWASP, CIS, DISA, FIRST, and hundreds more |
| **428 cloud capabilities** | AWS (20 services), Azure (16 services), GCP (18 services) — audit + remediation CLI commands |
| **502 CNA partners** | Every CVE Numbering Authority with scope, contacts, and disclosure policies |
| **Live service** | secid.cloudsecurityalliance.org — REST API, MCP server, interactive resolver |
| **SDKs** | Python, TypeScript, Go — `pip install secid`, `npm install secid` |
| **Open source** | CC0 (spec + data), MIT (service + SDKs) |

---

## v1.0 — Multiple Views of the Same Thing

**One CVE, many perspectives**

```
secid:advisory/mitre.org/cve#CVE-2024-1234      → cve.org (canonical record)
secid:advisory/nist.gov/nvd#CVE-2024-1234       → nvd.nist.gov (CVSS, CPE enrichment)
secid:advisory/redhat.com/cve#CVE-2024-1234     → Red Hat (affected products, patches)
secid:advisory/github.com/advisories/ghsa#...    → GitHub (affected repos, PRs)
```

Same vulnerability. Different context. All findable. No ambiguity about which view.

Also applies to: regulations in different languages, frameworks across versions, standards across jurisdictions.

---

## v1.0 — "Who Do I Report This To?"

**502 CVE Program partners, all discoverable**

```
secid:disclosure/redhat.com/cna
  → scope: "Open source projects affecting Red Hat software"
  → contact: secalert@redhat.com
  → policy: access.redhat.com/articles/red_hat_cna_vulnerability_disclosure_policy

secid:disclosure/mitre.org/cna-lr
  → scope: "Everything not covered by another CNA"
  → contact: cveform.mitre.org (CVE ID Request Form)
```

**Workflow:** Found a vulnerability? → Look up the vendor's CNA → Check scope → Use their contact → If no CNA exists → MITRE CNA-LR is the fallback.

> Every CNA. Every scope. Every contact. Machine-readable.

---

## v1.0 — Cloud Security Capabilities

**What can you configure? How do you audit it? How do you fix it?**

```
secid:capability/amazon.com/aws/s3#default-encryption
  → options: SSE-S3, SSE-KMS, DSSE-KMS
  → default: AES256 (since January 2023)
  → audit: aws s3api get-bucket-encryption --bucket {bucket}
  → fix: aws s3api put-bucket-encryption ...
  → terraform: aws_s3_bucket_server_side_encryption_configuration
```

**428 capabilities across 54 cloud services** — neutral facts about what products provide. Separate from what frameworks say you MUST do (controls) or what the law requires (regulations).

> Capabilities are facts. Controls are opinions. SecID catalogs both.

---

## v1.0 — AI-Native from Day One

**Three interfaces for three audiences**

| Audience | Interface | Example |
|---|---|---|
| **Humans** | secid.cloudsecurityalliance.org | Interactive resolver, browsable registry |
| **Software** | REST API + SDKs | `GET /api/v1/resolve?secid=secid:advisory/mitre.org/cve%23CVE-2021-44228` |
| **AI Agents** | MCP Server | Add `https://secid.cloudsecurityalliance.org/mcp` — no API keys, no config |

The MCP server gives AI agents 3 tools: `resolve`, `lookup`, `describe`. Responses include context, disambiguation guidance, and cross-references — agents can reason about security knowledge without external documentation.

> One URL. Three tools. Every AI assistant becomes security-aware.

---

## v1.0 — Cross-Source Search

**Don't know which database? Just give the type and the ID.**

```
secid:advisory/CVE-2024-1234
  → MITRE CVE    (weight: 100, url: cve.org/...)
  → NVD          (weight: 80,  url: nvd.nist.gov/...)
  → Red Hat      (weight: 80,  url: access.redhat.com/...)
  → SUSE         (weight: 80,  url: suse.com/...)
  → GitHub GHSA  (weight: 70,  url: github.com/advisories/...)
```

One query. Every source that knows about this CVE. Sorted by authority.

Works for any type: `secid:weakness/CWE-79`, `secid:ttp/T1059.003`, `secid:control/AC-1`.

---

## v2.0 — What's Coming Next

**From URLs to content. From links to knowledge.**

| v1.0 (today) | v2.0 (next) |
|---|---|
| "CWE-79 is at cwe.mitre.org/..." | Here's the full CWE-79 description, mitigations, and examples — inline |
| "GDPR Article 32 is at eur-lex..." | Here's the article text in your language — inline |
| "CCM IAM-12 is in this Excel ZIP" | Here's the control text, implementation guidance, and audit criteria — inline |
| Links between types | Traversable relationship graph: CVE → CWE → ATT&CK → controls |

> v1.0 tells you where to look. v2.0 gives you the answer.

---

## v2.0 — Data Federation

**Three rules for hosting data**

| Rule | When | Example |
|---|---|---|
| **Persistence** | Source might disappear | Tweets, paste site disclosures, blog posts |
| **AI-unfriendly format** | Data exists but not per-item JSON | CWE (XML dump), GDPR (HTML), CCM (Excel) |
| **Synthesis needed** | Raw source needs AI condensation | Reddit vuln discussion → structured timeline |

**Rule 0: Respect the license.** ISO standards? Registry entry only. CWE (MITRE ToU)? Host with attribution. US government work? Public domain, host freely.

Data repos: `CloudSecurityAlliance-DataSets/SecID-weakness/`, `SecID-control/`, `SecID-regulation/`, etc.

---

## v2.0 — The Full Security Picture

**One query, complete context**

```
"Tell me about CVE-2024-1234"

→ CVE description + severity (from cvelistV5, cached)
→ CWE-79 weakness description + mitigations (from SecID-weakness data)
→ ATT&CK T1059 technique + detection methods (from STIX)
→ NIST 800-53 SI-4 control text (from SecID-control data)
→ CCM LOG-01 CSA control text (from SecID-control data)
→ AWS CloudTrail capability + audit CLI (from SecID-capability data)
→ CIS Benchmark 3.1 check (from SecID-control data)
→ Prowler automated check (from SecID-control data)
→ All vendor advisories with patch status
```

**Today:** 10 databases, manual navigation, hope you don't miss a connection.
**v2.0:** One traversal. Complete picture. Actual content at every node.

---

## v2.0 — Capabilities as the Anchor

**Facts vs. opinions**

```
FACT (capability):
  secid:capability/amazon.com/aws/s3#default-encryption
  "S3 has encryption. Options: SSE-S3, SSE-KMS, DSSE-KMS."

OPINIONS (controls — may conflict):
  CIS says: "Must be enabled" (any option)
  DISA says: "Must use KMS specifically"
  PCI-DSS says: "Cardholder data must be encrypted"
  Your CISO says: "DSSE-KMS only, no exceptions"
```

The capability is neutral. The controls are opinions from different authorities. SecID catalogs all of them — the engineer compares and decides.

> Capabilities don't change when a new regulation comes along. Opinions swirl around them. SecID makes both visible.

---

## What SecID Enables at CSA

**Infrastructure for the next generation of security programs**

| Program | What SecID Unblocks |
|---|---|
| **CCM / AICM** | Per-control resolution. AI agents can look up any control by ID and get the full text. |
| **STAR** | Vendor/product/control assessment tracking with stable references |
| **CCSK** | Training materials reference SecIDs — students can look up anything |
| **Mapping Pipeline** | All cross-framework mapping claims reference SecIDs. IR 8477 methodology encoded. |
| **CNA Program** | 502 CVE partners with scope, contacts, policies — discoverable via SecID |

> SecID is infrastructure. These programs are the products built on it.

---

## Try It → Integrate It → Contribute

**1. Try it**
secid.cloudsecurityalliance.org — paste any CVE, CWE, ATT&CK ID, or type `secid:` to browse

**2. Add to your AI assistant**
MCP server: `https://secid.cloudsecurityalliance.org/mcp` — one URL, no config

**3. Integrate it**
REST API: `GET /api/v1/resolve?secid=...` — no auth, CORS enabled
SDKs: Python (`pip install secid`), TypeScript (`npm install secid`), Go

**4. Contribute**
Found something missing? `github.com/CloudSecurityAlliance/SecID/issues`
Adding a source is one JSON file. AI agents can help.

---

Kurt Seifried · Chief Innovation Officer · Cloud Security Alliance
kseifried@cloudsecurityalliance.org · github.com/kurtseifried

**SecID v1.0** — 10 types · 709+ namespaces · 428 cloud capabilities · 502 CNA partners
secid.cloudsecurityalliance.org · github.com/CloudSecurityAlliance/SecID
CC0 (Public Domain)
