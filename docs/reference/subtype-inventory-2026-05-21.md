# Subtype inventory — 2026-05-21

Scope: source-level `match_nodes` under `registry/methodology/` and `registry/reference/`, focused on types that currently have declared subtypes in SecID-Service.

## Summary

| Type | Total source-level match nodes | Tagged | Untagged | Notes |
|---|---:|---:|---:|---|
| `methodology` | 56 | 56 | 0 | This sweep backfills the remaining methodology gaps. |
| `reference` | 236 | 0 | 236 | Untagged reference entries should be handled in a dedicated reference glossary sweep to avoid mixing policy decisions with the methodology cleanup. |

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

## Reference inventory

| File | Pattern | State | Subtype |
|---|---|---|---|
| `registry/reference/au/gov/oaic.json` | `(?i)^app-key-concepts$` | untagged | — |
| `registry/reference/br/gov.json` | `(?i)^glossario-seguranca-informacao$` | untagged | — |
| `registry/reference/ca/bc/gov.json` | `(?i)^infosec-glossary$` | untagged | — |
| `registry/reference/ca/canada.json` | `(?i)^enterprise-cyber-security-strategy-glossary$` | untagged | — |
| `registry/reference/ca/quebec.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/ch/iec.json` | `(?i)^iec-glossary$` | untagged | — |
| `registry/reference/ch/ncsc.json` | `(?i)^ncsc-ch-glossary$` | untagged | — |
| `registry/reference/com/amazon.json` | `^[A-Z0-9]{10}$` | untagged | — |
| `registry/reference/com/anthropic.json` | `(?i)^model-card$` | untagged | — |
| `registry/reference/com/apple.json` | `(?i)^platform-security-glossary$` | untagged | — |
| `registry/reference/com/bankid.json` | `(?i)^glossary$` | untagged | — |
| `registry/reference/com/beyondtrust.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/bitdefender.json` | `(?i)^infozone-glossary$` | untagged | — |
| `registry/reference/com/bitsight.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/blackberry.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/blackduck.json` | `(?i)^application-security-glossary$` | untagged | — |
| `registry/reference/com/broadcom.json` | `(?i)^enterprise-security-glossary$` | untagged | — |
| `registry/reference/com/bsigroup.json` | `(?i)^cyber-security-glossary$` | untagged | — |
| `registry/reference/com/bugcrowd.json` | `(?i)^glossary$` | untagged | — |
| `registry/reference/com/catonetworks.json` | `(?i)^it-security-glossary$` | untagged | — |
| `registry/reference/com/checkmarx.json` | `(?i)^application-security-glossary$` | untagged | — |
| `registry/reference/com/checkmk.json` | `(?i)^glossary$` | untagged | — |
| `registry/reference/com/checkpoint.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/cisco.json` | `(?i)^security-glossary$` | untagged | — |
| `registry/reference/com/citrix.json` | `(?i)^glossary$` | untagged | — |
| `registry/reference/com/cloudflare.json` | `(?i)^security-glossary$` | untagged | — |
| `registry/reference/com/connectwise.json` | `(?i)^connectwise-cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/cyberark.json` | `(?i)^cyberark-glossary$` | untagged | — |
| `registry/reference/com/cybersecurityworks.json` | `(?i)^csw-cyber-security-glossary$` | untagged | — |
| `registry/reference/com/dragos.json` | `(?i)^dragos-ot-cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/equifax.json` | `(?i)^security-guidance$` | untagged | — |
| `registry/reference/com/eset.json` | `(?i)^eset-glossary$` | untagged | — |
| `registry/reference/com/f5.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/fidelissecurity.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/flexerasoftware.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/forcepoint.json` | `(?i)^cyber-edu-glossary$` | untagged | — |
| `registry/reference/com/forescout.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/fortinet.json` | `(?i)^cyberglossary$` | untagged | — |
| `registry/reference/com/github/commit.json` | `^[0-9a-f]{40}$` | untagged | — |
| `registry/reference/com/github/commit.json` | `^[0-9a-f]{7,39}$` | untagged | — |
| `registry/reference/com/github/discussions.json` | `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/\d+$` | untagged | — |
| `registry/reference/com/github/issues.json` | `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/\d+$` | untagged | — |
| `registry/reference/com/github/pull.json` | `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/\d+$` | untagged | — |
| `registry/reference/com/github/releases.json` | `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+/.+$` | untagged | — |
| `registry/reference/com/github/repo.json` | `^[A-Za-z0-9._-]+/[A-Za-z0-9._-]+$` | untagged | — |
| `registry/reference/com/github/users.json` | `^[A-Za-z0-9](?:[A-Za-z0-9-]*[A-Za-z0-9])?$` | untagged | — |
| `registry/reference/com/gitlab.json` | `(?i)^security-glossary$` | untagged | — |
| `registry/reference/com/google.json` | `(?i)^model-card$` | untagged | — |
| `registry/reference/com/hackerone.json` | `(?i)^hackerone-glossary$` | untagged | — |
| `registry/reference/com/huntresslabs.json` | `(?i)^cybersecurity-101-glossary$` | untagged | — |
| `registry/reference/com/hypr.json` | `(?i)^security-encyclopedia$` | untagged | — |
| `registry/reference/com/ibm.json` | `(?i)^security-guidance$` | untagged | — |
| `registry/reference/com/illumio.json` | `(?i)^cybersecurity-101-glossary$` | untagged | — |
| `registry/reference/com/intel.json` | `(?i)^software-security-glossary$` | untagged | — |
| `registry/reference/com/ivanti.json` | `(?i)^ivanti-glossary$` | untagged | — |
| `registry/reference/com/jamf.json` | `(?i)^jamf-platform-glossary$` | untagged | — |
| `registry/reference/com/jupiterone.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/kaspersky.json` | `(?i)^it-encyclopedia-glossary$` | untagged | — |
| `registry/reference/com/keepersecurity.json` | `(?i)^iam-glossary$` | untagged | — |
| `registry/reference/com/microsoft.json` | `(?i)^msrc-glossary$` | untagged | — |
| `registry/reference/com/netapp.json` | `(?i)^netapp-glossary$` | untagged | — |
| `registry/reference/com/netskope.json` | `(?i)^security-defined$` | untagged | — |
| `registry/reference/com/nvidia.json` | `(?i)^nvidia-glossary$` | untagged | — |
| `registry/reference/com/okta.json` | `(?i)^iam-glossary$` | untagged | — |
| `registry/reference/com/openai.json` | `(?i)^system-card$` | untagged | — |
| `registry/reference/com/openai.json` | `(?i)^model-spec$` | untagged | — |
| `registry/reference/com/openai.json` | `(?i)^preparedness$` | untagged | — |
| `registry/reference/com/opentext.json` | `(?i)^appsec-glossary$` | untagged | — |
| `registry/reference/com/oracle.json` | `(?i)^oci-glossary$` | untagged | — |
| `registry/reference/com/palantir.json` | `(?i)^foundry-security-glossary$` | untagged | — |
| `registry/reference/com/paloaltonetworks.json` | `(?i)^cyberpedia-glossary$` | untagged | — |
| `registry/reference/com/panasonic.json` | `(?i)^security-system-glossary$` | untagged | — |
| `registry/reference/com/papercut.json` | `(?i)^print-security-acronyms$` | untagged | — |
| `registry/reference/com/pingidentity.json` | `(?i)^identity-glossary$` | untagged | — |
| `registry/reference/com/profibus.json` | `(?i)^pi-glossary$` | untagged | — |
| `registry/reference/com/progress.json` | `(?i)^data-protection-privacy-glossary$` | untagged | — |
| `registry/reference/com/proofpoint.json` | `(?i)^threat-reference$` | untagged | — |
| `registry/reference/com/rapid7.json` | `(?i)^cloud-security-glossary$` | untagged | — |
| `registry/reference/com/redhat.json` | `(?i)^security-glossary$` | untagged | — |
| `registry/reference/com/sailpoint.json` | `(?i)^identity-security-glossary$` | untagged | — |
| `registry/reference/com/saviynt.json` | `(?i)^identity-security-glossary$` | untagged | — |
| `registry/reference/com/securityscorecard.json` | `(?i)^securityscorecard-glossary$` | untagged | — |
| `registry/reference/com/silabs.json` | `(?i)^security-glossary$` | untagged | — |
| `registry/reference/com/solarwinds.json` | `(?i)^it-glossary$` | untagged | — |
| `registry/reference/com/sonicwall.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/sophos.json` | `(?i)^cybersecurity-explained$` | untagged | — |
| `registry/reference/com/ssrn.json` | `^\d{6,7}$` | untagged | — |
| `registry/reference/com/strongdm.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/tenable.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/trendmicro.json` | `(?i)^what-is-cybersecurity-terms$` | untagged | — |
| `registry/reference/com/txone.json` | `(?i)^ot-cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/upguard.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/vulncheck.json` | `(?i)^vulncheck-glossary$` | untagged | — |
| `registry/reference/com/watchguard.json` | `(?i)^network-security-glossary$` | untagged | — |
| `registry/reference/com/wpscan.json` | `(?i)^wpscan-glossary$` | untagged | — |
| `registry/reference/com/xonasystems.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/com/zohocorp.json` | `(?i)^eprotect-security-glossary$` | untagged | — |
| `registry/reference/com/zscaler.json` | `(?i)^security-terms-glossary$` | untagged | — |
| `registry/reference/de/bund/bsi.json` | `(?i)^glossary$` | untagged | — |
| `registry/reference/edu/cmu.json` | `(?i)^iso-glossary$` | untagged | — |
| `registry/reference/edu/mit.json` | `(?i)^ai-risk-repository$` | untagged | — |
| `registry/reference/es/incibe.json` | `(?i)^glosario-terminos-ciberseguridad$` | untagged | — |
| `registry/reference/eu/europa/enisa.json` | `(?i)^enisa-glossary$` | untagged | — |
| `registry/reference/eu/europa.json` | `(?i)^enisa-glossary$` | untagged | — |
| `registry/reference/fi/ncsc.json` | `(?i)^ncsc-fi-glossary$` | untagged | — |
| `registry/reference/fr/gouv/legifrance.json` | `(?i)^vocabulaire-cyberdefense$` | untagged | — |
| `registry/reference/fr/gouv/numerique.json` | `(?i)^cyberdico$` | untagged | — |
| `registry/reference/gov/ca.json` | `(?i)^sam-5300-definitions$` | untagged | — |
| `registry/reference/gov/cisa.json` | `(?i)^govcar$` | untagged | — |
| `registry/reference/gov/ct.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/gov/fedramp.json` | `(?i)^3pao-.+$` | untagged | — |
| `registry/reference/gov/fedramp.json` | `(?i)^.+-playbook$` | untagged | — |
| `registry/reference/gov/fedramp.json` | `(?i)^.+-(template\|form)$`, `(?i)^fedramp-.+-template$` | untagged | — |
| `registry/reference/gov/fedramp.json` | `(?i)^csp-.+$` | untagged | — |
| `registry/reference/gov/fedramp.json` | `(?i)^fedramp-.+$` | untagged | — |
| `registry/reference/gov/fedramp.json` | `(?i)^ssp-appendix-[a-z]-.+$` | untagged | — |
| `registry/reference/gov/fedramp.json` | `(?i)^reusing-authorizations-for-cloud-products-quick-guide$`, `(?i)^vulnerability-scanning-requirements-for-containers$` | untagged | — |
| `registry/reference/gov/maryland.json` | `(?i)^cybersecurity-privacy-glossary$` | untagged | — |
| `registry/reference/gov/mt.json` | `(?i)^mom-security-glossary$` | untagged | — |
| `registry/reference/gov/nih.json` | `^\d+$` | untagged | — |
| `registry/reference/gov/nist/nvd.json` | `(?i)^cpe$` | untagged | — |
| `registry/reference/gov/nist/nvd.json` | `^cpe:2\.3:[aho]:[^:]+:[^:]+` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^ir-\d+$` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^tn-\d+$` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^cswp-.+$` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^csrc-glossary$` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^ai-rmf-crosswalks$` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^800-\d+[a-z]?(-pt\d+)?(-v\d+)?$` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^1800-\d+$` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^fips-(140(-\d)?\|180\|186\|197\|198\|201\|202\|203\|204\|205)$` | untagged | — |
| `registry/reference/gov/nist.json` | `(?i)^ai-100-\d+$` | untagged | — |
| `registry/reference/gov/ny.json` | `(?i)^its-glossary$` | untagged | — |
| `registry/reference/gov/texas.json` | `(?i)^cybersecurity-terminology$` | untagged | — |
| `registry/reference/gov/virginia.json` | `(?i)^cov-it-glossary$` | untagged | — |
| `registry/reference/gov/wa.json` | `(?i)^data-breach-glossary$` | untagged | — |
| `registry/reference/gov/whitehouse.json` | `^eo-\d{5}$` | untagged | — |
| `registry/reference/gov/whitehouse.json` | `^m-\d{2}-\d{2}$` | untagged | — |
| `registry/reference/gov/whitehouse.json` | `^nsm-\d+$` | untagged | — |
| `registry/reference/gov/whitehouse.json` | `^ncs-\d{4}$` | untagged | — |
| `registry/reference/int/itu.json` | `(?i)^cybex-x.1500$` | untagged | — |
| `registry/reference/io/cribl.json` | `(?i)^cribl-glossary$` | untagged | — |
| `registry/reference/io/kubernetes.json` | `(?i)^kubernetes-glossary$` | untagged | — |
| `registry/reference/io/snyk.json` | `(?i)^ai-cybersecurity-glossary$` | untagged | — |
| `registry/reference/io/socradar.json` | `(?i)^cybersecurity-glossary$` | untagged | — |
| `registry/reference/it/gov/agid.json` | `(?i)^cert-agid-glossario$` | untagged | — |
| `registry/reference/me/proton.json` | `(?i)^encryption-glossary$` | untagged | — |
| `registry/reference/net/devolutions.json` | `(?i)^devolutions-it-security-glossary$` | untagged | — |
| `registry/reference/net/hitrustalliance.json` | `(?i)^glossary-of-terms-and-acronyms$` | untagged | — |
| `registry/reference/net/juniper.json` | `(?i)^juniper-glossary$` | untagged | — |
| `registry/reference/nl/ncsc.json` | `(?i)^cybersecurity-woordenboek$` | untagged | — |
| `registry/reference/org/acm.json` | `^10\.1145/\d+\.\d+$` | untagged | — |
| `registry/reference/org/arxiv.json` | `^\d{4}\.\d{4,5}$` | untagged | — |
| `registry/reference/org/asisonline.json` | `(?i)^security-industry-glossary$` | untagged | — |
| `registry/reference/org/bimco.json` | `(?i)^cyber-security-onboard-ships-glossary$` | untagged | — |
| `registry/reference/org/cisecurity.json` | `(?i)^oval$` | untagged | — |
| `registry/reference/org/cloudsecurityalliance.json` | `(?i)^artifacts$` | untagged | — |
| `registry/reference/org/cloudsecurityalliance.json` | `^-?[a-z0-9]([a-z0-9-]*[a-z0-9])?$` | untagged | — |
| `registry/reference/org/cloudsecurityalliance.json` | `(?i)^secid-parsers$` | untagged | — |
| `registry/reference/org/cloudsecurityalliance.json` | `(?i)^cve-json-5$` | untagged | — |
| `registry/reference/org/cve.json` | `(?i)^cve-schema$` | untagged | — |
| `registry/reference/org/cve.json` | `^5\.2(\.0)?$` | untagged | — |
| `registry/reference/org/cve.json` | `^5\.1(\.0)?$` | untagged | — |
| `registry/reference/org/cve.json` | `^5\.0(\.0)?$` | untagged | — |
| `registry/reference/org/dblp.json` | `^[a-z]+/[a-zA-Z0-9/]+$` | untagged | — |
| `registry/reference/org/debian.json` | `(?i)^debian-security-glossary$` | untagged | — |
| `registry/reference/org/doi.json` | `^10\.\d{4,}/[^\s]+$` | untagged | — |
| `registry/reference/org/first.json` | `(?i)^cvss$` | untagged | — |
| `registry/reference/org/first.json` | `(?i)^epss$` | untagged | — |
| `registry/reference/org/h-isac.json` | `(?i)^health-isac-acronyms$` | untagged | — |
| `registry/reference/org/himss.json` | `(?i)^infosec-cybersecurity-terms$` | untagged | — |
| `registry/reference/org/iacr.json` | `^\d{4}/\d+$` | untagged | — |
| `registry/reference/org/ieee.json` | `^\d{7,8}$` | untagged | — |
| `registry/reference/org/ietf.json` | `^\d+$` | untagged | — |
| `registry/reference/org/isaca.json` | `(?i)^cybersecurity-fundamentals-glossary$` | untagged | — |
| `registry/reference/org/isbn.json` | `^97[89]-?\d{1,5}-?\d{1,7}-?\d{1,7}-?\d$` | untagged | — |
| `registry/reference/org/issn.json` | `^\d{4}-\d{3}[\dX]$` | untagged | — |
| `registry/reference/org/metacpan.json` | `(?i)^cpansec-glossary$` | untagged | — |
| `registry/reference/org/mitre.json` | `(?i)^cpe$` | untagged | — |
| `registry/reference/org/mitre.json` | `(?i)^stix$` | untagged | — |
| `registry/reference/org/mitre.json` | `(?i)^taxii$` | untagged | — |
| `registry/reference/org/mitre.json` | `(?i)^maec$` | untagged | — |
| `registry/reference/org/mitre.json` | `(?i)^oval$` | untagged | — |
| `registry/reference/org/mitre.json` | `(?i)^cwe-schema$` | untagged | — |
| `registry/reference/org/mitre.json` | `^7\.3$` | untagged | — |
| `registry/reference/org/mitre.json` | `^7\.2$` | untagged | — |
| `registry/reference/org/mitre.json` | `^7\.1$` | untagged | — |
| `registry/reference/org/mitre.json` | `^7\.0$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.10$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.9$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.8$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.7$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.6$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.5$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.4$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.3$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.2$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.1$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.0\.1$` | untagged | — |
| `registry/reference/org/mitre.json` | `^6\.0$` | untagged | — |
| `registry/reference/org/mitre.json` | `^5\.4\.4$` | untagged | — |
| `registry/reference/org/mitre.json` | `^5\.4\.3$` | untagged | — |
| `registry/reference/org/mitre.json` | `^5\.4\.2$` | untagged | — |
| `registry/reference/org/mitre.json` | `^5\.4$` | untagged | — |
| `registry/reference/org/mitre.json` | `^5\.3$` | untagged | — |
| `registry/reference/org/mitre.json` | `^5\.2$` | untagged | — |
| `registry/reference/org/mitre.json` | `^5\.0$` | untagged | — |
| `registry/reference/org/mitre.json` | `^4\.5$` | untagged | — |
| `registry/reference/org/mitre.json` | `^4\.4$` | untagged | — |
| `registry/reference/org/mitre.json` | `^4\.3$` | untagged | — |
| `registry/reference/org/mitre.json` | `^4\.2\.1$` | untagged | — |
| `registry/reference/org/mlcommons.json` | `(?i)^ai-safety-glossary$` | untagged | — |
| `registry/reference/org/ndss-symposium.json` | `^[a-z0-9-]+$` | untagged | — |
| `registry/reference/org/nfpa.json` | `(?i)^nfpa-glossary$` | untagged | — |
| `registry/reference/org/oasis-open.json` | `(?i)^stix$` | untagged | — |
| `registry/reference/org/oasis-open.json` | `(?i)^taxii$` | untagged | — |
| `registry/reference/org/oasis-open.json` | `(?i)^csaf$` | untagged | — |
| `registry/reference/org/oecd.json` | `(?i)^oecd-ai-glossary$` | untagged | — |
| `registry/reference/org/openalex.json` | `^W\d+$` | untagged | — |
| `registry/reference/org/opengroup.json` | `(?i)^opaf-glossary$` | untagged | — |
| `registry/reference/org/openidentityexchange.json` | `(?i)^identity-glossary$` | untagged | — |
| `registry/reference/org/openssl.json` | `(?i)^openssl-glossary$` | untagged | — |
| `registry/reference/org/owasp.json` | `(?i)^ai-exchange$` | untagged | — |
| `registry/reference/org/partnershiponai.json` | `(?i)^synthetic-media-glossary$` | untagged | — |
| `registry/reference/org/pcisecuritystandards.json` | `(?i)^pci-glossary$` | untagged | — |
| `registry/reference/org/semanticscholar.json` | `^[a-f0-9]{40}$` | untagged | — |
| `registry/reference/org/sharedassessments.json` | `(?i)^tprm-glossary$` | untagged | — |
| `registry/reference/org/techrxiv.json` | `^\d+(\.v\d+)?$` | untagged | — |
| `registry/reference/org/usenix.json` | `^[a-z0-9-]+/presentation/[a-z0-9-]+$` | untagged | — |
| `registry/reference/org/wikimedia.json` | `(?i)^security-team-definitions$` | untagged | — |
| `registry/reference/org/zenodo.json` | `^\d+$` | untagged | — |
| `registry/reference/sk/gov/nbu.json` | `(?i)^slovnik-hybridnych-hrozieb$` | untagged | — |
| `registry/reference/uk/gov/aisi.json` | `(?i)^uk$` | untagged | — |
| `registry/reference/uk/gov/aisi.json` | `(?i)^us$` | untagged | — |
| `registry/reference/uk/gov/aisi.json` | `(?i)^japan$` | untagged | — |
| `registry/reference/uk/gov/aisi.json` | `(?i)^international$` | untagged | — |
| `registry/reference/uk/gov.json` | `(?i)^ai-safety-report$` | untagged | — |

Total reference source-level match nodes: 236. All are currently untagged; this PR records them for the follow-up glossary backfill decision rather than mixing that broader policy change into the methodology sweep.

## Follow-up decision points

- Reference glossary entries are still untagged. A targeted follow-up can add `subtype: ["glossary"]` to the glossary-shaped `reference` entries after maintainers confirm they want the broader backfill in one PR.
- Candidate subtypes for `advisory`, `control`, `disclosure`, `entity`, and `regulation` still require SecID-Service type-registry declarations before data can use them.
- Completeness checking in `scripts/validate-subtypes.py` is available through `--completeness warn` and can be escalated to `--completeness fail` once maintainers want CI to enforce full subtype coverage for declared-subtype types.
