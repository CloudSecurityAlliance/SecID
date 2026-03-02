---
type: control
namespace: cloudsecurityalliance.org
full_name: "Cloud Security Alliance"
operator: "secid:entity/cloudsecurityalliance.org"
website: "https://cloudsecurityalliance.org"
status: active

sources:
  ccm:
    full_name: "Cloud Controls Matrix"
    urls:
      website: "https://cloudsecurityalliance.org/research/cloud-controls-matrix"
      download: "https://cloudsecurityalliance.org/artifacts/cloud-controls-matrix-v4"
      download_v41: "https://cloudsecurityalliance.org/download/artifacts/cloud-controls-matrix-v4-1"
      machine_readable: "https://cloudsecurityalliance.org/artifacts/ccm-machine-readable-bundle-json-yaml-oscal"
    versions:
      - "4.1"
      - "4.0"
      - "3.0.1"
    id_pattern: "[A-Z&]{2,3}-\\d{2}"
    examples:
      - "secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-01"
      - "secid:control/cloudsecurityalliance.org/ccm@4.0#DSP-07"
      - "secid:control/cloudsecurityalliance.org/ccm@4.1#A&A-01"

  aicm:
    full_name: "AI Controls Matrix"
    urls:
      website: "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix"
      download: "https://cloudsecurityalliance.org/download/artifacts/ai-controls-matrix"
    versions:
      - "1.0"
    id_pattern: "[A-Z&]{2,3}-\\d{2}"
    examples:
      - "secid:control/cloudsecurityalliance.org/aicm@1.0#IAM-01"
      - "secid:control/cloudsecurityalliance.org/aicm@1.0#MDS-01"
      - "secid:control/cloudsecurityalliance.org/aicm@1.0#DSP-03"

  ai-safety:
    full_name: "AI Safety Initiative"
    urls:
      website: "https://cloudsecurityalliance.org/research/working-groups/artificial-intelligence"
    examples:
      - "secid:control/cloudsecurityalliance.org/ai-safety"
---

# Cloud Security Alliance Controls

CSA provides cloud and AI security control frameworks widely used for compliance and security assessments.

## Why CSA Matters

CSA is the leading cloud security standards body:

- **Industry standard** - CCM used in thousands of organizations
- **Vendor neutral** - Not tied to specific cloud providers
- **AI expansion** - New AI Controls Matrix
- **STAR registry** - Public compliance attestations

---

## ccm

The Cloud Controls Matrix (CCM) is the de facto standard for cloud security controls.

### Format

```
secid:control/cloudsecurityalliance.org/ccm@4.1#XXX-NN
```

Domain code (2-3 uppercase letters, or A&A) and two-digit control number. No per-control web pages -- resolution returns a download URL with extraction instructions.

### Control Domains (17)

| Code | Domain |
|------|--------|
| A&A | Audit & Assurance |
| AIS | Application & Interface Security |
| BCR | Business Continuity Management & Operational Resilience |
| CCC | Change Control & Configuration Management |
| CEK | Cryptography, Encryption & Key Management |
| DCS | Datacenter Security |
| DSP | Data Security & Privacy Lifecycle Management |
| GRC | Governance, Risk & Compliance |
| HRS | Human Resources |
| IAM | Identity & Access Management |
| IPY | Interoperability & Portability |
| IVS | Infrastructure & Virtualization Security |
| LOG | Logging & Monitoring |
| SEF | Security Incident Management, E-Discovery & Cloud Forensics |
| STA | Supply Chain Management, Transparency & Accountability |
| TVM | Threat & Vulnerability Management |
| UEM | Universal Endpoint Management |

### Resolution

No per-control web pages exist. The download is a ZIP bundle containing the main Excel spreadsheet, CAIQ questionnaire, implementation/auditing guidelines, and mappings. A machine-readable bundle (JSON/YAML/OSCAL) is also available for programmatic access.

To find a specific control: download the bundle, open the Excel spreadsheet, go to the "CCM Controls" sheet, find the row where "Control ID" matches. The "Control Specification" column contains the full control text.

### Notes

- Version 4.1 current (207 controls, 283 CAIQ questions); v4.0 superseded (197 controls)
- Maps to ISO 27001, NIST, PCI-DSS
- Used for STAR certification
- A&A domain code contains an ampersand -- patterns must account for this

---

## aicm

The AI Controls Matrix provides security controls specific to AI/ML systems.

### Format

```
secid:control/cloudsecurityalliance.org/aicm@1.0#XXX-NN
```

Same ID format as CCM (domain code + two-digit number). AICM shares all 17 CCM domains and adds MDS (Model Security) for 18 total.

### Control Domains (18)

AICM reuses all 17 CCM domain codes (see table above) and adds:

| Code | Domain |
|------|--------|
| MDS | Model Security (AICM-only) |

### Coverage

AICM addresses:
- Model training security
- Data poisoning prevention
- Inference security
- Model theft protection
- Bias and fairness controls
- AI supply chain security

Distinguishes between "Cloud & AI Related" controls (shared with CCM) and "Strictly AI Related" controls (AICM-only).

### Resolution

Same as CCM: no per-control web pages. Download the AICM bundle, open the spreadsheet, find the row where "Control ID" matches. The "Specifications" column contains the full control text.

### Relationship to CCM

| Matrix | Scope | Domains | Controls |
|--------|-------|---------|----------|
| CCM v4.1 | General cloud security | 17 | 207 |
| AICM v1.0 | AI-specific (extends CCM) | 18 (adds MDS) | 243 |

Use both for comprehensive AI cloud security.

### Notes

- Version 1.0 released July 2025 (243 controls, updated to v1.0.2)
- Complements CCM for AI workloads
- Aligns with NIST AI RMF, ISO 42001, BSI AI C4
- Spreadsheet format (ZIP bundle download)

---

## ai-safety

CSA's AI Safety Initiative brings together industry efforts on AI security.

### Format

```
secid:control/cloudsecurityalliance.org/ai-safety
```

### Working Group Activities

- AI Controls Matrix development
- AI security research papers
- Best practices documentation
- Industry collaboration

### Notes

- Part of CSA research program
- Open participation
- Regular publications and updates
