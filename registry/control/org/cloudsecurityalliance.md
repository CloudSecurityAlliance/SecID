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

  ccm-caiq:
    full_name: "Consensus Assessments Initiative Questionnaire"
    urls:
      website: "https://cloudsecurityalliance.org/research/cloud-controls-matrix"
      download: "https://cloudsecurityalliance.org/download/artifacts/cloud-controls-matrix-v4-1"
      machine_readable: "https://cloudsecurityalliance.org/artifacts/ccm-machine-readable-bundle-json-yaml-oscal"
    versions:
      - "4.0.3"
      - "3.1"
      - "3.0.1"
    id_pattern: "[A-Z&]{2,3}-\\d{2}\\.\\d+"
    examples:
      - "secid:control/cloudsecurityalliance.org/ccm-caiq@4.0.3#IAM-01.1"
      - "secid:control/cloudsecurityalliance.org/ccm-caiq@4.0.3#A&A-01.2"
      - "secid:control/cloudsecurityalliance.org/ccm-caiq#IAM-01"

  aicm-caiq:
    full_name: "AI Consensus Assessments Initiative Questionnaire"
    urls:
      website: "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix"
      download: "https://cloudsecurityalliance.org/download/artifacts/ai-controls-matrix"
    versions:
      - "1.0"
    id_pattern: "[A-Z&]{2,3}-\\d{2}\\.\\d+"
    examples:
      - "secid:control/cloudsecurityalliance.org/aicm-caiq@1.0#MDS-01.1"
      - "secid:control/cloudsecurityalliance.org/aicm-caiq@1.0#IAM-01.1"

  star:
    full_name: "Security, Trust, Assurance and Risk Registry"
    type: registry
    note: "Registry of CAIQ submissions and third-party assessments — not itself a control framework. Listed here for discoverability."
    urls:
      website: "https://cloudsecurityalliance.org/star"
      registry: "https://cloudsecurityalliance.org/star/registry"
      third_party_search: "https://star.watch"
    examples:
      - "secid:control/cloudsecurityalliance.org/star"
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

- Version 1.0 released July 2025 (243 controls, updated to v1.0.3)
- Complements CCM for AI workloads
- Aligns with NIST AI RMF, ISO 42001, BSI AI C4
- Spreadsheet format (ZIP bundle download)

---

## ccm-caiq

The Consensus Assessments Initiative Questionnaire — yes/no assessment questions mapped to CCM controls.

### Format

```
secid:control/cloudsecurityalliance.org/ccm-caiq@4.0.3#IAM-01.1
```

Question ID format is `XXX-NN.M` where `XXX-NN` is the parent CCM control and `M` is the question number within that control. One or more questions per control.

### Resolution

CAIQ ships in the same ZIP bundle as CCM. The CAIQ is a separate sheet within the bundle's main Excel file.

To find a specific question: download the CCM bundle, open the spreadsheet, go to the "CAIQ" sheet, and find the row where "Question ID" matches.

Bare control IDs (without `.M` sub-number) resolve to the full set of questions for that control. For the control specification itself, use `secid:control/cloudsecurityalliance.org/ccm#XXX-NN`.

### Notes

- v4.0.3 current (283 questions); pairs with CCM v4.1
- Used for STAR Level 1 self-assessments
- Same ZIP/Excel bundle as CCM

---

## aicm-caiq

The AI Consensus Assessments Initiative Questionnaire — yes/no assessment questions mapped to AICM controls. CSA's own branding is "AI-CAIQ".

### Format

```
secid:control/cloudsecurityalliance.org/aicm-caiq@1.0#MDS-01.1
```

Same `XXX-NN.M` format as CCM CAIQ. Includes the MDS (Model Security) domain unique to AICM.

### Resolution

AI-CAIQ ships in the same ZIP bundle as AICM. The questionnaire is a separate sheet within the AICM Excel file.

Bare control IDs resolve to the full set of questions for that control. For the control specification itself, use `secid:control/cloudsecurityalliance.org/aicm#XXX-NN`.

### Notes

- v1.0 (released July 2025); pairs with AICM v1.0/v1.0.3
- AI-specific assessment questions including MDS (Model Security)

---

## star

The Security, Trust, Assurance and Risk Registry — a public registry of CAIQ submissions and third-party assessments.

**Important:** STAR is a *registry* (an index/lookup), not a control framework. It is included in the control namespace for discoverability. The underlying controls are CCM (`secid:control/cloudsecurityalliance.org/ccm`); the assessment questionnaire is CAIQ (`secid:control/cloudsecurityalliance.org/ccm-caiq`). STAR is the public collection of organizations' submitted CAIQ files plus third-party attestations.

### Format

```
secid:control/cloudsecurityalliance.org/star
```

No per-entry pattern is currently defined — bare `star` resolves to the registry homepage.

### Levels

- **Level 1** — Self-assessment via CAIQ (free; publicly downloadable submissions). Largest portion of the registry.
- **Level 2** — Third-party audit (STAR Certification based on ISO 27001; STAR Attestation based on SOC 2).
- **Level 3** — Continuous monitoring (planned/emerging).

### Resolution

The registry is publicly browsable and searchable. Each entry corresponds to a cloud provider organization and lists their submitted assessments. Level 1 CAIQ submissions are downloadable as Excel/PDF files from the registry pages.

### Notes

- Largest public collection of CAIQ submissions
- Registry/index, not a control set
- Third-party search/analytics available at star.watch
