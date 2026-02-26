# DRAFT: Recommended Crosswalk Mappings for AICM and CCM

**Status:** DRAFT - For internal discussion
**Date:** 2026-02-02
**Author:** Kurt Seifried, kseifried@cloudsecurityalliance.org
## Purpose

This report identifies frameworks, standards, and regulations recommended for crosswalk mapping against the AI Controls Matrix (AICM) and Cloud Controls Matrix (CCM). The goal is comprehensive coverage that serves customer needs, regulatory requirements, and market positioning.

## Note on Current State

**AICM** currently includes mappings to: BSI AI C4, EU AI Act, ISO/IEC 42001:2023, ISO 27001, and NIST AI 600-1.

**CCM** mapping inventory: We were unable to locate the current mapping inventory for CCM. Version 4.1 does not include the mappings spreadsheet, and version 4.0.13 was not accessible within the timeframe for preparing this report. We recommend resolving this documentation gap as a separate action item.

This report focuses on identifying what mappings should exist, independent of what currently exists.

## Category Definitions

Each recommended mapping is tagged with one or more categories explaining why it matters:

- **Table Stakes** - Customers expect this as baseline coverage; absence looks like a gap
- **Regulatory Pressure** - Compliance requirements are driving customer demand
- **Competitive Differentiation** - Opportunity to lead the market while others lack coverage
- **Visibility/Marketing** - Popular frameworks that drive awareness and demonstrate relevance
- **Customer Pull** - Customers have requested this mapping

**Note:** We recommend formalizing a customer feedback mechanism to systematically capture and prioritize mapping requests.

## Recommended Mappings

### NIST Publications

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| NIST Cybersecurity Framework (CSF) 2.0 | No | Table Stakes | Foundational US framework; expected baseline for any security controls matrix |
| NIST SP 800-53 Rev 5 | No | Table Stakes, Regulatory Pressure | Required for US federal and heavily referenced in regulated industries |
| NIST AI Risk Management Framework (AI RMF) 1.0 | Yes | Table Stakes, Competitive Differentiation | Primary US AI governance framework; essential for AICM credibility |
| NIST AI 600-1 | Yes | Competitive Differentiation | AI RMF companion with detailed guidance; demonstrates depth |

### ISO/IEC Standards

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| ISO/IEC 27001:2022 | No | Table Stakes | Global baseline for information security; customers assume this exists |
| ISO/IEC 27002:2022 | No | Table Stakes | Control guidance companion to 27001; provides implementation detail |
| ISO/IEC 27017:2015 | No | Table Stakes | Cloud-specific security controls; directly relevant to CCM |
| ISO/IEC 27018:2019 | No | Table Stakes, Regulatory Pressure | PII protection in cloud; GDPR alignment |
| ISO/IEC 27701:2019 | No | Regulatory Pressure | Privacy information management; GDPR/CCPA alignment |
| ISO/IEC 42001:2023 | Yes | Table Stakes, Competitive Differentiation | AI management system standard; essential for AICM credibility |
| ISO/IEC 23894:2023 | Yes | Competitive Differentiation | AI risk management guidance; complements 42001 |

### OWASP Projects

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| OWASP LLM Top 10 | Yes | Visibility/Marketing | Extremely popular; mapping demonstrates AI security relevance |
| OWASP AI Exchange | Yes | Visibility/Marketing, Competitive Differentiation | Broader AI security coverage; emerging reference |
| OWASP Application Security Verification Standard (ASVS) | No | Table Stakes | Widely used for application security; complements cloud controls |
| OWASP Top 10 | No | Visibility/Marketing | Ubiquitous awareness; expected reference point |

### European Union Regulations

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| EU AI Act | Yes | Regulatory Pressure, Competitive Differentiation | Major AI regulation; mandatory for EU market |
| General Data Protection Regulation (GDPR) | Partial | Regulatory Pressure, Table Stakes | Article 22 automated decision-making; foundational privacy regulation |
| NIS2 Directive | No | Regulatory Pressure | Critical infrastructure security; expanding scope |
| Digital Operational Resilience Act (DORA) | No | Regulatory Pressure | Financial sector mandatory; effective January 2025 |
| EU Cyber Resilience Act | No | Regulatory Pressure | Product security requirements; emerging |

### US Federal Requirements

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| FedRAMP | No | Regulatory Pressure, Table Stakes | Required for US federal cloud; large market |
| FISMA | No | Regulatory Pressure | Federal information security; underpins FedRAMP |
| StateRAMP | No | Competitive Differentiation | Growing state/local adoption; emerging opportunity |
| CMMC 2.0 | No | Regulatory Pressure | Defense industrial base requirement; mandatory for DoD contracts |
| Executive Order 14110 (AI) | Yes | Regulatory Pressure, Competitive Differentiation | Federal AI requirements; signals US direction |

### Healthcare

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| HIPAA Security Rule | No | Regulatory Pressure, Table Stakes | Healthcare data protection; large regulated market |
| HITRUST CSF | No | Table Stakes | Healthcare industry standard; often required by customers |
| FDA AI/ML Software as Medical Device (SaMD) Guidance | Yes | Regulatory Pressure, Competitive Differentiation | AI in medical devices; growing regulatory focus |

### Financial Services

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| PCI DSS v4.0 | No | Regulatory Pressure, Table Stakes | Payment card security; wide applicability |
| Sarbanes-Oxley Act (SOX) | No | Regulatory Pressure | Financial reporting controls; public companies |
| Gramm-Leach-Bliley Act (GLBA) | No | Regulatory Pressure | Financial privacy; US financial institutions |
| FFIEC Guidance | No | Regulatory Pressure | US financial regulators; banks and credit unions |
| SWIFT Customer Security Controls Framework | No | Competitive Differentiation | Financial messaging; specialized but high-value |
| MAS Technology Risk Management Guidelines | No | Competitive Differentiation | Singapore financial regulation; APAC coverage |
| SEC AI Disclosure Requirements | Yes | Regulatory Pressure | Emerging US requirements for AI in financial services |

### AI-Specific Frameworks and Regulations

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| MITRE ATLAS | Yes | Competitive Differentiation, Visibility/Marketing | AI threat matrix; tactical security mapping |
| BSI AI Cloud Service Compliance Criteria (AIC4) | Yes | Competitive Differentiation | German AI standard; EU market credibility |
| Singapore Model AI Governance Framework | Yes | Competitive Differentiation | APAC AI governance leader; regional coverage |
| OECD AI Principles | Yes | Table Stakes | International foundation; referenced by many national frameworks |
| IEEE 7000 Series (AI Ethics) | Yes | Competitive Differentiation | Technical ethics standards; demonstrates depth |
| Canada Artificial Intelligence and Data Act (AIDA) | Yes | Regulatory Pressure | Emerging Canadian AI law; North American coverage |
| Colorado AI Act | Yes | Regulatory Pressure, Competitive Differentiation | First comprehensive US state AI law; signals trend |
| NYC Local Law 144 | Yes | Regulatory Pressure | Automated employment decisions; operational now |
| China AI Regulations (Algorithmic Recommendations, Deep Synthesis, Generative AI) | Yes | Competitive Differentiation | Major market; demonstrates global coverage |
| UK AI Regulation (emerging framework) | Yes | Competitive Differentiation | Post-Brexit UK approach; distinct from EU |

### Privacy Regulations

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| California Consumer Privacy Act / California Privacy Rights Act (CCPA/CPRA) | Partial | Regulatory Pressure | Automated profiling provisions; major US state |
| Brazil General Data Protection Law (LGPD) | No | Regulatory Pressure | Large market; GDPR-like requirements |
| APEC Privacy Framework | No | Competitive Differentiation | Cross-border privacy; APAC coverage |

### Other Standards and Frameworks

| Framework | AI-Specific | Categories | Why Map |
|-----------|-------------|------------|---------|
| CIS Controls v8 | No | Table Stakes | Practical security controls; widely adopted |
| SOC 2 / AICPA Trust Services Criteria | No | Table Stakes | Cloud audit standard; customer expectation |
| COBIT 2019 | No | Competitive Differentiation | IT governance; enterprise customers |
| Secure Controls Framework (SCF) | No | Competitive Differentiation | Comprehensive meta-framework; potential competitor alignment |
| CSA STAR | No | Table Stakes | Our own certification program; obvious alignment |
| TISAX | No | Competitive Differentiation | Automotive industry; specialized vertical |
| NERC CIP | No | Competitive Differentiation | Energy sector critical infrastructure |

## Strategic Observations

**Sector-Based Grouping:** Several mappings cluster naturally and should be tackled as blocks for efficiency:
- Healthcare (HIPAA, HITRUST, FDA) shares common concepts and customer base
- Financial Services (PCI DSS, SOX, GLBA, FFIEC, DORA) has significant overlap
- US Federal (FedRAMP, FISMA, CMMC) builds on NIST foundations
- EU Regulations (GDPR, AI Act, NIS2, DORA) share regulatory philosophy

**AI-Specific Advantage:** The AI regulatory landscape is immature and fragmented. Comprehensive AICM mappings to emerging AI frameworks (Colorado AI Act, NYC LL144, China regulations) creates competitive differentiation while others are still catching up.

**Visibility vs. Depth:** Some mappings serve different purposes:
- OWASP mappings are primarily visibility/marketing - they're popular and demonstrate relevance
- ISO and NIST mappings provide technical depth and credibility
- Both are valuable for different audiences

**System-Building Approach:** Building a robust mapping methodology enables comprehensive coverage. The investment is primarily in the first mapping; subsequent mappings leverage the same process at marginal cost.

**Customer Feedback:** We recommend establishing a formal mechanism to capture customer mapping requests. This provides data-driven prioritization and demonstrates responsiveness to customer needs.
