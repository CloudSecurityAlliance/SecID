# Regulation Type (`regulation`)

This type contains references to laws, directives, and binding legal requirements.

## Purpose

Track and reference regulatory requirements - the "what the law requires":
- GDPR (EU General Data Protection Regulation)
- HIPAA (US Health Insurance Portability and Accountability Act)
- SOX (Sarbanes-Oxley Act)
- NIS2 (EU Network and Information Security Directive)
- EU AI Act
- State/provincial privacy laws (CCPA, etc.)

## Identifier Format

```
secid:regulation/<jurisdiction>/<law>[@version][#article]

secid:regulation/europa.eu/gdpr
secid:regulation/europa.eu/gdpr@2016-04-27
secid:regulation/europa.eu/gdpr#art-32
secid:regulation/europa.eu/gdpr#art-32.1.a
secid:regulation/govinfo.gov/hipaa
secid:regulation/govinfo.gov/hipaa#164.312.a.1
secid:regulation/govinfo.gov/sox
secid:regulation/europa.eu/nis2
secid:regulation/europa.eu/ai-act
secid:regulation/ca.gov/ccpa
```

## Namespaces (Jurisdictions)

| Namespace | Jurisdiction | Description |
|-----------|--------------|-------------|
| `europa.eu` | European Union | GDPR, NIS2, AI Act |
| `govinfo.gov` | United States | HIPAA, SOX, federal laws |
| `ca.gov` | California | CCPA, CPRA |
| `ny.gov` | New York | SHIELD Act, DFS requirements |
| `gov.uk` | United Kingdom | UK GDPR, Data Protection Act |
| `gov.cn` | China | PIPL, Cybersecurity Law |

## Versioning and Citations

Use `@version` for specific versions (often publication dates):

```
secid:regulation/europa.eu/gdpr@2016-04-27     # GDPR publication date
secid:regulation/europa.eu/ai-act@2024-06-13   # AI Act publication date
```

Use `#subpath` for specific articles, sections, or citations:

```
secid:regulation/europa.eu/gdpr#art-32         # Article 32
secid:regulation/europa.eu/gdpr#art-32.1.a     # Article 32(1)(a)
secid:regulation/govinfo.gov/hipaa#164.312.a.1   # Security Rule citation
```

## Key Regulations

### Data Protection
| ID | Name | Jurisdiction |
|----|------|--------------|
| `europa.eu/gdpr` | General Data Protection Regulation | EU |
| `govinfo.gov/hipaa` | Health Insurance Portability and Accountability Act | US |
| `ca.gov/ccpa` | California Consumer Privacy Act | California |
| `gov.cn/pipl` | Personal Information Protection Law | China |

### Security and Infrastructure
| ID | Name | Jurisdiction |
|----|------|--------------|
| `europa.eu/nis2` | Network and Information Security Directive 2 | EU |
| `govinfo.gov/fisma` | Federal Information Security Management Act | US |
| `govinfo.gov/sox` | Sarbanes-Oxley Act | US |

### AI-Specific
| ID | Name | Jurisdiction |
|----|------|--------------|
| `europa.eu/ai-act` | EU Artificial Intelligence Act | EU |

## EU AI Act Detail

The EU AI Act (entered into force August 2024) is the first comprehensive AI regulation. It uses a risk-based approach:

### Risk Categories

| Risk Level | Examples | Requirements |
|------------|----------|--------------|
| **Unacceptable** | Social scoring, real-time biometric ID | Prohibited |
| **High-risk** | Critical infrastructure, employment, credit | Conformity assessment, registration |
| **Limited** | Chatbots, deepfakes | Transparency obligations |
| **Minimal** | Spam filters, games | No requirements |

### Key Articles

```
secid:regulation/europa.eu/ai-act#art-5      # Prohibited AI practices
secid:regulation/europa.eu/ai-act#art-6      # High-risk classification
secid:regulation/europa.eu/ai-act#art-9      # Risk management system
secid:regulation/europa.eu/ai-act#art-10     # Data governance
secid:regulation/europa.eu/ai-act#art-13     # Transparency
secid:regulation/europa.eu/ai-act#art-14     # Human oversight
secid:regulation/europa.eu/ai-act#art-52     # Transparency for certain AI systems
```

### Timeline

- **August 2024**: Entry into force
- **February 2025**: Prohibited practices apply
- **August 2025**: GPAI (general-purpose AI) rules apply
- **August 2026**: High-risk AI system rules apply

### Relationship to Controls

The AI Act creates demand for AI-specific controls:

```json
{
  "from": "secid:control/cloudsecurityalliance.org/aicm@1.1.0#GOV-01",
  "to": "secid:regulation/europa.eu/ai-act#art-9",
  "type": "satisfies",
  "description": "AI governance controls address AI Act risk management requirements"
}
```

## Relationships

Controls satisfy regulatory requirements:

```json
{
  "from": "secid:control/iso.org/27001@2022#A.8.1",
  "to": "secid:regulation/europa.eu/gdpr#art-32",
  "type": "satisfies",
  "description": "Asset management addresses GDPR security requirements"
}
```

Regulations may reference other regulations:

```json
{
  "from": "secid:regulation/europa.eu/nis2",
  "to": "secid:regulation/europa.eu/gdpr",
  "type": "references",
  "description": "NIS2 builds on GDPR data protection requirements"
}
```

## Regulation vs Control vs Standard

- **Regulation** (regulation): What the law requires (GDPR, HIPAA)
- **Control** (control): How to meet requirements (ISO 27001, CIS)
- **Scoring/Formats**: Technical specifications (CVSS via `entity/first.org/cvss`, etc.)

Regulations are **mandatory** within their jurisdiction. Controls are **voluntary** frameworks (unless regulation mandates them). Technical standards are referenced via their operating entity.

## Notes

- Regulations change over time - use version when precision matters
- Subpaths for article citations follow each regulation's numbering scheme
- Some regulations (like GDPR) have extensive guidance documents that may warrant separate entries

