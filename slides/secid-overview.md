# SecID: Label It. Find It. Use It.

**A universal identifier for security knowledge**

Cloud Security Alliance · secid.cloudsecurityalliance.org

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

## How It Works

**Sources**
MITRE · NIST · OWASP · Red Hat · ISO · GitHub · ...
*publish security knowledge*

↓

**SecID Registry**
`advisory` · `weakness` · `ttp` · `control` · `capability` · `methodology` · `disclosure` · `regulation` · `entity` · `reference`
*namespace (DNS) + patterns + URLs*

↓

**Consumers**
Humans (website) · Software (API, SDKs) · AI Agents (MCP server)

> Sources → Registry → Consumers. Three layers, one identifier format.

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

## Multiple Views of the Same Thing

**One CVE, many perspectives**

```
secid:advisory/mitre.org/cve#CVE-2024-1234      → cve.org (canonical record)
secid:advisory/mitre.org/nvd#CVE-2024-1234      → nvd.nist.gov (CVSS, CPE enrichment)
secid:advisory/redhat.com/cve#CVE-2024-1234     → Red Hat (affected products, patches)
secid:advisory/github.com/advisories/ghsa#...    → GitHub (affected repos, PRs)
```

Same vulnerability. Different context. All findable. No ambiguity about which view.

Also applies to: regulations in different languages, frameworks across versions, standards across jurisdictions.

---

## The Cross-Type Query

**From one CVE to a complete security picture**

```
CVE-2021-44228 (Log4Shell)
  → CWE-502  (Deserialization weakness)
    → T1190   (Exploit Public-Facing Application)
      → NIST CSF PR.IP-12  (Implementation protection)
        → CCM IAM-12  (Cloud control)
```

**Today:** 5 databases, manual navigation, hope you don't miss a connection.

**With SecID:** one traversal across the security knowledge graph.

> This is the query nobody can do today. SecID makes it possible.

---

## Human Directed. Agent Native. Human Legible.

- **Human Directed** — humans set goals, make strategic decisions, exercise judgment
- **Agent Native** — outputs designed for AI agents to consume and act on. MCP server = native tool access.
- **Human Legible** — structured so humans can verify the critical parts

| Audience | Interface |
|---|---|
| Humans | secid.cloudsecurityalliance.org — interactive resolver |
| Software | REST API + SDKs (Python, npm, Go, Rust, Java, C#) |
| AI Agents | MCP Server — native tool access to the full registry |

---

## What SecID Enables at CSA

**Infrastructure for the next generation of security programs**

| Program | What SecID Unblocks |
|---|---|
| **CAVEaT 2.0** | CVE → Control mapping becomes machine-readable. Original stalled partly due to no identifier infrastructure. |
| **Security Controls Catalog** | Unified identifiers across CCM, AICM, and third-party frameworks |
| **STAR** | Vendor/product/control assessment tracking with stable references |
| **Mapping Pipeline** | All cross-framework mapping claims reference SecIDs |
| **Valid-AI-ted** | Regulation identifiers across jurisdictions for compliance |

> SecID is infrastructure. These programs are the products built on it.

---

## Easy to Contribute

**We meet you where you are**

| Effort | What You Do |
|---|---|
| **Minimal** | File a GitHub issue: "this source is missing" |
| **Some** | Submit a markdown file with your research notes |
| **Full** | Submit a structured JSON registry file, ready to merge |

AI agents can contribute too — automated research, verification, and freshness checks.

> Contributing is less work than keeping your own notes. If you found it, telling us is easier than bookmarking it.

---

## Federation

**Your data, your rules**

- Organizations run **private registries** that reference the public one
- Domain owners manage their own namespaces via **DNS verification**
- Private standards stay private; public references stay public
- Same identifier format everywhere — public, organizational, personal

> SecID scales because it doesn't require centralization. The same model that made DNS and CVE's CNA program successful.

---

## Try It → Integrate It → Contribute

1. **Try it:** secid.cloudsecurityalliance.org — paste any CVE, CWE, or ATT&CK ID
2. **Integrate it:** REST API, MCP server, SDKs for Python, npm, Go, Rust, Java, C#
3. **Contribute:** Found something missing? Add it — easier than keeping your own notes

`github.com/CloudSecurityAlliance/SecID`

Cloud Security Alliance
