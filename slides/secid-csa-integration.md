# SecID + CSA: Infrastructure for Security Programs

**How SecID powers CCM, AICM, STAR, CCSK, and beyond**

Kurt Seifried · Chief Innovation Officer · Cloud Security Alliance
kseifried@cloudsecurityalliance.org · github.com/kurtseifried

secid.cloudsecurityalliance.org · v1.0 · April 2026

---

## What SecID Gives CSA

**One identifier system connecting all CSA programs**

Today each CSA program has its own reference system:
- CCM has control IDs (IAM-12) — in a spreadsheet
- AICM has control IDs (MDS-01) — in a different spreadsheet
- STAR has assessment records — in a database
- CCSK references controls — in training materials
- Mapping projects cite frameworks — in yet another format

SecID gives every piece of CSA security knowledge a **structured, resolvable identifier**:

```
secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12
secid:control/cloudsecurityalliance.org/aicm@1.0.3#MDS-01
```

> One format. Every program. Machine-readable. AI-ready.

---

## CCM + AICM: Per-Control Resolution

**Every control is individually addressable**

```
secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12
  → Description: Identity & Access Management control 12
  → Domain: IAM (Identity & Access Management)
  → Download: cloudsecurityalliance.org/artifacts/cloud-controls-matrix-v4-1
  → Machine-readable: JSON/YAML/OSCAL bundle available
```

All 17 CCM domains and 207 controls. All 18 AICM domains and 243 controls. Individually resolvable.

**For members:** reference specific controls in compliance documentation, audit reports, and security policies.

**For staff:** every control has a stable URL that AI agents, tools, and partner integrations can use.

---

## CCM + AICM: What v2.0 Unlocks

**From "download the spreadsheet" to "ask for any control"**

Today:
```
"What does IAM-12 say?"
→ Download ZIP → Open Excel → Find IAM-12 row → Read "Control Specification" column
```

v2.0:
```
secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12
→ {
    "title": "Multi-Factor Authentication",
    "specification": "Multi-factor authentication shall be implemented...",
    "implementation_guidance": "...",
    "audit_guidance": "...",
    "applicability": "...",
    "mappings": ["secid:control/nist.gov/800-53#IA-2", "secid:control/iso.org/27001@2022#A.8.5"]
  }
```

An AI agent can look up any CCM or AICM control and get the full text — implementation guidance, audit criteria, and framework mappings — without downloading a spreadsheet.

---

## STAR: Stable References for Assessments

**Assessments reference controls that don't change**

STAR assessments reference CCM controls. SecID makes those references:
- **Versionable** — `secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12` vs `@4.0#IAM-12`
- **Resolvable** — click the identifier, see the control
- **Comparable** — "show me all assessments that reference IAM-12"
- **Stable** — the SecID doesn't change when the CSA website restructures

**For star.watch:** STAR registry entries can include SecID references to the exact CCM version assessed against.

**For assessors:** cite specific controls in assessment reports using SecIDs that resolve to the authoritative text.

---

## CCSK: Training with Live Lookups

**Students learn controls they can immediately look up**

CCSK training references CCM controls. With SecID:
- Training materials include SecIDs: `secid:control/cloudsecurityalliance.org/ccm@4.1#DSP-07`
- Students paste SecIDs into the resolver and see the control details
- Lab exercises: "Look up this control. What does the implementation guidance say?"
- AI tutoring: "Explain CCM IAM-12" → agent resolves the SecID, gets the text, explains it

**For the training team:** embed SecID links in course materials. They resolve to current content even when the underlying data is updated.

**For students:** one tool to look up any CCM control, NIST framework, CWE weakness, or ATT&CK technique they encounter.

---

## Cross-Framework Mapping

**SecID as the common reference for all mapping work**

CSA does extensive mapping: CCM ↔ NIST, CCM ↔ ISO, AICM ↔ NIST AI RMF.

Without SecID:
```
"CCM IAM-12 maps to NIST 800-53 IA-2"
→ Which version of CCM? Which revision of 800-53? Where's the evidence?
```

With SecID:
```
secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12
  → maps_to: secid:control/nist.gov/800-53@r5#IA-2
  → methodology: secid:methodology/nist.gov/ir-8477#crosswalk
  → evidence: "Both require MFA for privileged access"
```

Every mapping claim is versioned, citable, and references the methodology used (NIST IR 8477 defines crosswalk, supportive, STRM, and structural mapping styles — all in SecID).

---

## Vulnerability Disclosure

**502 CVE Program partners — CSA's own program included**

```
secid:disclosure/cloudsecurityalliance.org/responsible-disclosure
  → channels: GitHub PVR (preferred), security@cloudsecurityalliance.org
  → scope: websites, services, GitHub repos, AI prompts
  → policy: coordinated disclosure, 90-day timeline, safe harbor
```

CSA's product security program is in SecID alongside every other CNA. When someone asks "how do I report a vulnerability in a CSA product?" — the answer is machine-readable.

**For members:** look up any vendor's CNA to find who to report vulnerabilities to.

**For CSA security team:** the authoritative reference for CSA's own disclosure process.

---

## The Capability Type: Cloud Controls Become Actionable

**428 cloud security capabilities with audit + remediation commands**

When a STAR assessment says "implement CCM IAM-12 (MFA)" — the follow-up question is "how, specifically, on AWS?"

```
secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12
  → "Implement MFA"

secid:capability/amazon.com/aws/iam#mfa
  → Options: passkeys, virtual authenticator, hardware TOTP
  → Default: not enabled
  → Audit: aws iam list-mfa-devices --user-name {user}
  → Configure: aws iam enable-mfa-device ...
  → Vendor says: "Use phishing-resistant MFA (passkeys or security keys)"
```

**Control** says what to do. **Capability** says how to do it on a specific platform. The relationship layer (v2.0) connects them.

---

## What CSA Staff Should Be Doing

**Practical actions for each program**

| Program | Action Now | Action for v2.0 |
|---|---|---|
| **CCM/AICM** | Reference SecIDs in documentation. Validate registry entries are correct. | Provide per-control JSON for data federation. |
| **STAR** | Include SecID version references in assessment templates. | Enable STAR→SecID cross-referencing. |
| **CCSK** | Embed SecID links in training materials. Add resolver exercises. | Build AI tutoring that uses SecID for live control lookups. |
| **Mapping** | Ensure mapping outputs reference SecIDs. Document methodology per IR 8477. | Publish mappings as SecID relationship data. |
| **Research** | Reference SecIDs in research papers and guidance docs. | Contribute new namespaces for emerging frameworks. |
| **Product Security** | Keep the disclosure entry current. | Expand to cover all CSA digital properties. |

---

## What CSA Members Should Know

**SecID makes your compliance work easier**

| Use Case | How SecID Helps |
|---|---|
| "What does CCM IAM-12 require?" | `secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12` → instant lookup |
| "How do I implement it on AWS?" | `secid:capability/amazon.com/aws/iam#mfa` → audit + remediation CLI commands |
| "What NIST controls map to CCM?" | Cross-framework mapping via SecID references |
| "Who handles CVEs for vendor X?" | `secid:disclosure/{vendor}.com` → CNA scope, contacts, policy |
| "What's the OWASP LLM Top 10?" | `secid:weakness/owasp.org/llm-top10@2025` → all 10 items |
| "Show me GDPR Article 32" | `secid:regulation/europa.eu/gdpr#art-32` → article text (v2.0) |

**Add the MCP server to your AI assistant:** `https://secid.cloudsecurityalliance.org/mcp` — one URL, no config. Your AI can now look up any control, vulnerability, or framework.

---

## The Big Picture: SecID as CSA Infrastructure

```
                    CSA Programs
        ┌──────────────────────────────────┐
        │  CCM · AICM · STAR · CCSK       │
        │  Mapping · Research · Training   │
        └──────────────┬───────────────────┘
                       │ built on
                ┌──────┴──────┐
                │   SecID     │
                │  Registry   │
                │   + API     │
                └──────┬──────┘
                       │ references
        ┌──────────────┴───────────────────┐
        │  External Security Knowledge     │
        │  CVE · CWE · ATT&CK · NIST     │
        │  ISO · OWASP · CIS · DISA      │
        │  AWS · Azure · GCP · 700+ more  │
        └──────────────────────────────────┘
```

SecID is the connective tissue. CSA programs are the products. External security knowledge is the foundation.

> Every CSA program that references security knowledge benefits from SecID.

---

## Get Started

**For CSA staff:**
- Browse: secid.cloudsecurityalliance.org — try `secid:control/cloudsecurityalliance.org/ccm`
- Review: are your program's SecID entries correct? File issues if not.
- Embed: reference SecIDs in your program's documentation.

**For CSA members:**
- Add MCP server: `https://secid.cloudsecurityalliance.org/mcp` — your AI gets 700+ sources
- Look up controls: `secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12`
- Report gaps: `github.com/CloudSecurityAlliance/SecID/issues`

**For everyone:**
- Spec: `github.com/CloudSecurityAlliance/SecID`
- Service: `github.com/CloudSecurityAlliance/SecID-Service`
- SDKs: `github.com/CloudSecurityAlliance/SecID-Client-SDK`

---

Kurt Seifried · Chief Innovation Officer · Cloud Security Alliance
kseifried@cloudsecurityalliance.org · github.com/kurtseifried

**SecID v1.0** · secid.cloudsecurityalliance.org
"Label It. Find It. Use It."
