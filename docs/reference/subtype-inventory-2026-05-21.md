# Subtype inventory — 2026-05-21

Scope: source-level `match_nodes` under `registry/methodology/` and `registry/reference/`, focused on types that currently have declared subtypes in SecID-Service.

## Summary

| Type | Total source-level match nodes | Tagged | Untagged | Notes |
|---|---:|---:|---:|---|
| `methodology` | 56 | 56 | 0 | This sweep backfills the remaining methodology gaps. |
| `reference` | 204 | 0 | 204 | 109 untagged entries look glossary-shaped by pattern or description; these should be handled in a dedicated reference glossary sweep to avoid mixing policy decisions with the methodology cleanup. |

## Methodology inventory

| File | Pattern | Subtype | Notes |
|---|---|---|---|
| `registry/methodology/com/att.json` | `(?i)^cybersecurity-insights$` | `scoring` | AT&T Cybersecurity Insights: risk-scoring methodology for evaluating organization-level security posture. |
| `registry/methodology/edu/cmu.json` | `(?i)^ssvc$` | `scoring` | Stakeholder-Specific Vulnerability Categorization (SSVC): decision-tree methodology for prioritizing vulnerability response based on stakeholder context. |
| `registry/methodology/edu/cmu.json` | `^2\.0$` | `scoring` | SSVC v2.0: current version with refined decision points and stakeholder roles. |
| `registry/methodology/gov/cisa.json` | `(?i)^ssvc-decision-tree$` | `vulnerability-management` | CISA Customized SSVC Decision Tree: CISA's adapted SSVC methodology for prioritizing vulnerability remediation based on exploitation status, technical impact, automatable status, mission prevalence, and public well-being impact. |
| `registry/methodology/gov/fedramp.json` | `(?i)^threat-based-risk-profiling-methodology$` | `scoring` | FedRAMP Threat-Based Risk Profiling Methodology. |
| `registry/methodology/gov/nist.json` | `(?i)^ir-8477$` | `mapping` | NIST IR 8477: Mapping Relationships Between Documentary Standards, Regulations, Frameworks, and Guidelines. |
| `registry/methodology/gov/nist.json` | `(?i)^crosswalk$` | `mapping` | Crosswalk mapping: identifies direct equivalence or near-equivalence between elements from two documents. |
| `registry/methodology/gov/nist.json` | `(?i)^supportive$` | `mapping` | Supportive relationship mapping: identifies elements that support or contribute to the objectives of elements in another document. |
| `registry/methodology/gov/nist.json` | `(?i)^strm$` | `mapping` | Set Theory Relationship Mapping (STRM): uses set theory notation to express precise mathematical relationships between document elements. |
| `registry/methodology/gov/nist.json` | `(?i)^structural$` | `mapping` | Structural mapping: analyzes the organizational structure and hierarchy of documents. |
| `registry/methodology/gov/nist.json` | `(?i)^selection$` | `mapping` | Selection methodology: decision process for choosing which mapping style(s) to apply. |
| `registry/methodology/gov/nist.json` | `(?i)^rmf$`, `(?i)^800-37$` | `risk-management` | NIST Risk Management Framework (SP 800-37). |
| `registry/methodology/gov/nist.json` | `(?i)^800-30$` | `risk-management` | NIST SP 800-30: Guide for Conducting Risk Assessments. |
| `registry/methodology/gov/nist.json` | `(?i)^800-39$` | `risk-management` | NIST SP 800-39: Managing Information Security Risk. |
| `registry/methodology/gov/nist.json` | `(?i)^800-61$` | `incident-management` | NIST SP 800-61: Incident Handling Guide. |
| `registry/methodology/gov/nist.json` | `(?i)^800-115$` | `security-testing` | NIST SP 800-115: Technical Guide to Information Security Testing and Assessment. |
| `registry/methodology/gov/nist.json` | `(?i)^800-161$` | `supply-chain` | NIST SP 800-161: Cybersecurity Supply Chain Risk Management Practices. |
| `registry/methodology/int/mitre.json` | `(?i)^att&ck-evaluations$`, `(?i)^attack-evaluations$` | `security-testing` | MITRE ATT&CK Evaluations. |
| `registry/methodology/int/mitre.json` | `(?i)^d3fend$` | `mapping` | MITRE D3FEND: knowledge graph methodology mapping defensive cybersecurity techniques. |
| `registry/methodology/org/cisecurity.json` | `(?i)^cis-ram$` | `risk-management` | CIS Risk Assessment Method. |
| `registry/methodology/org/cisecurity.json` | `(?i)^controls-assessment-methodology$`, `(?i)^cam$` | `audit-certification` | CIS Controls Assessment Methodology. |
| `registry/methodology/org/crest.json` | `(?i)^crest-penetration-testing-methodology$`, `(?i)^penetration-testing-methodology$` | `security-testing` | CREST Penetration Testing Methodology. |
| `registry/methodology/org/first.json` | `(?i)^cvss$` | `scoring` | Common Vulnerability Scoring System (CVSS). |
| `registry/methodology/org/first.json` | `^4\.0$` | `scoring` | CVSS v4.0. |
| `registry/methodology/org/first.json` | `^3\.1$` | `scoring` | CVSS v3.1. |
| `registry/methodology/org/first.json` | `^3\.0$` | `scoring` | CVSS v3.0. |
| `registry/methodology/org/first.json` | `^2(\.0)?$` | `scoring` | CVSS v2. |
| `registry/methodology/org/first.json` | `^1(\.0)?$` | `scoring` | CVSS v1. |
| `registry/methodology/org/first.json` | `(?i)^epss$` | `scoring` | Exploit Prediction Scoring System (EPSS). |
| `registry/methodology/org/first.json` | `(?i)^tlp$` | `classification` | Traffic Light Protocol (TLP). |
| `registry/methodology/org/ietf.json` | `(?i)^cvss-v4-usage-guidance$` | `scoring` | IETF CVSS v4.0 usage guidance. |
| `registry/methodology/org/isaca.json` | `(?i)^cobit-design-factors$` | `risk-management` | COBIT design factors. |
| `registry/methodology/org/iso.json` | `(?i)^27005$` | `risk-management` | ISO/IEC 27005: information security risk-management methodology. |
| `registry/methodology/org/iso.json` | `(?i)^19011$` | `audit-certification` | ISO 19011: Guidelines for auditing management systems. |
| `registry/methodology/org/owasp.json` | `(?i)^risk-rating-methodology$` | `risk-management` | OWASP Risk Rating Methodology. |
| `registry/methodology/org/owasp.json` | `(?i)^threat-dragon-methodology$` | `threat-modeling` | OWASP Threat Dragon methodology. |
| `registry/methodology/org/owasp.json` | `(?i)^asvs-assessment-methodology$` | `security-testing` | OWASP ASVS assessment methodology. |
| `registry/methodology/org/owasp.json` | `(?i)^samm-assessment-methodology$` | `risk-management` | OWASP SAMM assessment methodology. |
| `registry/methodology/org/owasp.json` | `(?i)^mobile-security-testing-guide$`, `(?i)^mstg$` | `security-testing` | OWASP Mobile Security Testing Guide. |
| `registry/methodology/org/pci.json` | `(?i)^pci-dss-assessment-procedures$` | `audit-certification` | PCI DSS assessment procedures. |
| `registry/methodology/org/pmi.json` | `(?i)^risk-management-methodology$`, `(?i)^pmbok-risk$` | `risk-management` | PMI PMBOK risk-management methodology. |
| `registry/methodology/org/sans.json` | `(?i)^dfir-incident-response-methodology$` | `digital-forensics` | SANS DFIR incident-response methodology. |
| `registry/methodology/org/sans.json` | `(?i)^critical-security-controls-assessment$` | `audit-certification` | SANS Critical Security Controls assessment methodology. |
| `registry/methodology/org/sans.json` | `(?i)^forensic-analysis-methodology$` | `digital-forensics` | SANS forensic analysis methodology. |
| `registry/methodology/org/sans.json` | `(?i)^pen-testing-methodology$` | `security-testing` | SANS penetration testing methodology. |
| `registry/methodology/org/sans.json` | `(?i)^threat-hunting-methodology$` | `threat-modeling` | SANS threat hunting methodology. |
| `registry/methodology/org/sans.json` | `(?i)^security-awareness-maturity-model$` | `classification` | SANS Security Awareness Maturity Model. |
| `registry/methodology/org/sei.json` | `(?i)^octave$` | `risk-management` | OCTAVE risk assessment methodology. |
| `registry/methodology/org/sei.json` | `(?i)^octave-allegro$` | `risk-management` | OCTAVE Allegro. |
| `registry/methodology/org/tmforum.json` | `(?i)^risk-management-framework$` | `risk-management` | TM Forum risk-management framework. |
| `registry/methodology/org/uitp.json` | `(?i)^cybersecurity-risk-assessment$` | `risk-management` | UITP cybersecurity risk assessment methodology. |
| `registry/methodology/org/ukcybersecuritycouncil.json` | `(?i)^cyber-career-framework$` | `classification` | UK Cyber Security Council career framework. |
| `registry/methodology/org/w3.json` | `(?i)^wcag-evaluation-methodology$` | `security-testing` | W3C WCAG Evaluation Methodology. |
| `registry/methodology/org/weforum.json` | `(?i)^cyber-resilience-framework$` | `risk-management` | World Economic Forum cyber resilience framework. |
| `registry/methodology/org/x940.json` | `(?i)^x940-risk-methodology$` | `risk-management` | X9.40 risk methodology. |
| `registry/methodology/org/x940.json` | `(?i)^x940-control-assessment$` | `audit-certification` | X9.40 control assessment. |

## Follow-up decision points

- Reference glossary entries are still untagged. A targeted follow-up can add `subtype: ["glossary"]` to the glossary-shaped `reference` entries after maintainers confirm they want the broader backfill in one PR.
- Candidate subtypes for `advisory`, `control`, `disclosure`, `entity`, and `regulation` still require SecID-Service type-registry declarations before data can use them.
- Completeness checking in `scripts/validate-subtypes.py` should probably start as warn-only after the current methodology gaps are closed.
