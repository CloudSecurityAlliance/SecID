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
      - "4.1.1"
      - "4.1.0"
      - "4.0"
      - "3.0.1"
    id_pattern: "[A-Z&]{2,3}-\\d{2}"
    examples:
      - "secid:control/cloudsecurityalliance.org/ccm@4.1.1#IAM-01"
      - "secid:control/cloudsecurityalliance.org/ccm@4.0#DSP-07"
      - "secid:control/cloudsecurityalliance.org/ccm@4.1#I&S-01"

  aicm:
    full_name: "AI Controls Matrix"
    urls:
      website: "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix"
      download: "https://cloudsecurityalliance.org/download/artifacts/ai-controls-matrix"
    versions:
      - "1.1.1"
      - "1.1.0"
      - "1.0.3"
    id_pattern: "[A-Z&]{2,3}-\\d{2}"
    examples:
      - "secid:control/cloudsecurityalliance.org/aicm@1.1.1#IAM-01"
      - "secid:control/cloudsecurityalliance.org/aicm@1.1.1#MDS-01"
      - "secid:control/cloudsecurityalliance.org/aicm@1.1.0#DSP-03"

  ccm-caiq:
    full_name: "Consensus Assessments Initiative Questionnaire"
    urls:
      website: "https://cloudsecurityalliance.org/research/cloud-controls-matrix"
      download: "https://cloudsecurityalliance.org/download/artifacts/cloud-controls-matrix-v4-1"
      machine_readable: "https://cloudsecurityalliance.org/artifacts/ccm-machine-readable-bundle-json-yaml-oscal"
    versions:
      - "4.1.0"
      - "4.0.3"
      - "3.1"
      - "3.0.1"
    id_pattern: "[A-Z&]{2,3}-\\d{2}\\.\\d+"
    examples:
      - "secid:control/cloudsecurityalliance.org/ccm-caiq@4.1.0#IAM-01.1"
      - "secid:control/cloudsecurityalliance.org/ccm-caiq@4.0.3#A&A-01.2"
      - "secid:control/cloudsecurityalliance.org/ccm-caiq#IAM-01"

  aicm-caiq:
    full_name: "AI Consensus Assessments Initiative Questionnaire"
    urls:
      website: "https://cloudsecurityalliance.org/artifacts/ai-controls-matrix"
      download: "https://cloudsecurityalliance.org/download/artifacts/ai-controls-matrix"
    versions:
      - "1.1.0"
      - "1.0.2"
    id_pattern: "[A-Z&]{2,3}-\\d{2}\\.\\d+"
    examples:
      - "secid:control/cloudsecurityalliance.org/aicm-caiq@1.1.0#MDS-01.1"
      - "secid:control/cloudsecurityalliance.org/aicm-caiq@1.1.0#IAM-01.1"

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
secid:control/cloudsecurityalliance.org/ccm@4.1.1#XXX-NN
```

Domain code (2-3 uppercase letters, or A&A / I&S) and two-digit control number. CCM requires a version: each release has its own version node with its own domain codes. No per-control web pages -- resolution returns a download URL with extraction instructions.

### Control Domains (17)

The v4.1 codes. 4.1 renamed `IVS` (Infrastructure & Virtualization Security) to `I&S` (Infrastructure Security); v4.0 uses `IVS`. v3.0.1 uses a different set (AAC, DSI, EKM, GRM, MOS and others).

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
| I&S | Infrastructure Security (v4.0: `IVS`, Infrastructure & Virtualization Security) |
| LOG | Logging & Monitoring |
| SEF | Security Incident Management, E-Discovery & Cloud Forensics |
| STA | Supply Chain Management, Transparency & Accountability |
| TVM | Threat & Vulnerability Management |
| UEM | Universal Endpoint Management |

### Resolution

No per-control web pages exist. The download is a ZIP bundle containing the main Excel spreadsheet, CAIQ questionnaire, implementation/auditing guidelines, and mappings. A machine-readable bundle (JSON/YAML/OSCAL) is also available, but as of 2026-10-23 it is still the 4.1.0 release, so 4.1.1's mappings are only in the spreadsheet.

To find a specific control: download the bundle, open the Excel spreadsheet (`CCMv4.1.1-generated_at_2026_10_02.xlsx`), go to the "CCM" sheet, find the row where "Control ID" matches. Check cell A1 for the patch level: CSA serves 4.1.0 and 4.1.1 under the same "v4.1" artifact. The "Control Specification" column contains the full control text.

### Notes

- 4.1.1 is current (207 controls, 283 CAIQ questions; workbook Change Log dated 2026-10-01). Same control IDs as 4.1.0; adds the first v4.1 mappings (NIST SP 800-171 rev2, MITRE ATT&CK v17.1) and a DORA reverse mapping. `4.1` and `v4.1` resolve to 4.1.1 (ADR-015, second amendment)
- 4.1.0 (2026-01-27) is superseded; addressable only as `@4.1.0`
- v4.0 is superseded (197 controls); `4.0.13`, the stamp on the workbook CSA serves as v4.0, resolves to it
- An unversioned `ccm#XXX-NN` returns the versions with guidance rather than a control
- Maps to ISO 27001, NIST, PCI-DSS
- Used for STAR certification
- The A&A and (from 4.1) I&S domain codes contain an ampersand -- patterns must account for this

---

## aicm

The AI Controls Matrix provides security controls specific to AI/ML systems.

### Format

```
secid:control/cloudsecurityalliance.org/aicm@1.1.1#XXX-NN
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
| AICM v1.1.1 (current) | AI-specific (extends CCM) | 18 (adds MDS) | 247 |
| AICM v1.1.0 (superseded) | AI-specific (extends CCM) | 18 (adds MDS) | 247 |
| AICM v1.0.3 (superseded) | AI-specific (extends CCM) | 18 (adds MDS) | 243 |

Use both for comprehensive AI cloud security.

### Notes

- 1.1.1 (247 controls) is current; same control IDs as 1.1.0, adds NIST AI 600-1 and AIUC-1 mappings. `1.1` and `v1.1` resolve to 1.1.1, matching CSA's csa-mcp server
- 1.1.0 (2026-06-22, 247 controls) is superseded; control IDs were renumbered in place from 1.0.3, so IDs are not interchangeable between the 1.0 and 1.1 series
- 1.0.3 (243 controls) is superseded
- Complements CCM for AI workloads
- Aligns with NIST AI RMF, ISO 42001, BSI AI C4
- Spreadsheet format (ZIP bundle download)

---

## ccm-caiq

The Consensus Assessments Initiative Questionnaire — yes/no assessment questions mapped to CCM controls.

### Format

```
secid:control/cloudsecurityalliance.org/ccm-caiq@4.1.0#IAM-01.1
```

Question ID format is `XXX-NN.M` where `XXX-NN` is the parent CCM control and `M` is the question number within that control. One or more questions per control.

### Resolution

CAIQ ships in the same ZIP bundle as CCM. The CAIQ is a separate sheet within the bundle's main Excel file.

To find a specific question: download the CCM bundle, open the spreadsheet, go to the "CAIQ" sheet, and find the row where "Question ID" matches.

Bare control IDs (without `.M` sub-number) resolve to the full set of questions for that control. For the control specification itself, use `secid:control/cloudsecurityalliance.org/ccm@4.1.1#XXX-NN` (CCM requires a version).

### Notes

- v4.1.0 current (283 questions); pairs with CCM v4.1.0 and v4.1.1. CSA regenerated the workbook on 2026-10-02 under the same 4.1.0 label, and 26 question texts differ from the 2026-01-13 generation
- v4.0.3 superseded (261 questions); pairs with CCM v4.0
- Used for STAR Level 1 self-assessments
- Same ZIP/Excel bundle as CCM

---

## aicm-caiq

The AI Consensus Assessments Initiative Questionnaire — yes/no assessment questions mapped to AICM controls. CSA's own branding is "AI-CAIQ".

### Format

```
secid:control/cloudsecurityalliance.org/aicm-caiq@1.1.0#MDS-01.1
```

Same `XXX-NN.M` format as CCM CAIQ. Includes the MDS (Model Security) domain unique to AICM.

### Resolution

AI-CAIQ ships in the same ZIP bundle as AICM. The questionnaire is a separate sheet within the AICM Excel file.

Bare control IDs resolve to the full set of questions for that control. For the control specification itself, use `secid:control/cloudsecurityalliance.org/aicm#XXX-NN`.

### Notes

- 1.1.0 (2026-06-22) is current; pairs with AICM 1.1.0 and 1.1.1 (CSA issued no AI-CAIQ 1.1.1)
- 1.0.2 (superseded) pairs with AICM 1.0.3; question IDs are not interchangeable with 1.1.0
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
