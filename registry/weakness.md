# Weakness Type (`weakness`)

This type contains references to weakness taxonomies and classifications.

## Purpose

Track and reference weakness types - the abstract "how things go wrong" that underlies vulnerabilities:
- CWE (Common Weakness Enumeration)
- OWASP Top 10 categories
- OWASP LLM Top 10 categories
- Other weakness taxonomies

## Identifier Format

```
secid:weakness/<namespace>/<name>[#subpath]

secid:weakness/mitre.org/cwe#CWE-79
secid:weakness/mitre.org/cwe#CWE-1427
secid:weakness/owasp.org/top10@2021#A01
secid:weakness/owasp.org/llm-top10@2.0#LLM01
```

## Namespaces

### Core Weakness Taxonomies

| Namespace | Name | Taxonomy | Description |
|-----------|------|----------|-------------|
| `mitre.org` | `cwe` | CWE | MITRE Common Weakness Enumeration (900+ weaknesses) |
| `owasp.org` | `top10` | OWASP Top 10 | Web application security risks |

### AI/ML Weakness Taxonomies

| Namespace | Name | Taxonomy | Description |
|-----------|------|----------|-------------|
| `owasp.org` | `llm-top10` | OWASP LLM Top 10 | LLM application security risks |
| `owasp.org` | `ml-top10` | OWASP ML Top 10 | Machine learning security risks |
| `owasp.org` | `ai-exchange` | OWASP AI Exchange | Comprehensive AI security framework |
| `owasp.org` | `agentic-top10` | OWASP Agentic AI Top 10 | AI agent security risks |
| `nist.gov` | `ai-100-2` | NIST AML Taxonomy | Adversarial ML attack taxonomy |
| `berryvilleiml.com` | `ml-risks` | BIML ML Risks | 78 architectural ML risks |
| `berryvilleiml.com` | `llm-risks` | BIML LLM Risks | 81 LLM-specific risks |
| `mit.edu` | `ai-risk-repository` | MIT AI Risks | 1,700+ AI risks across 7 domains |

## Weakness vs Advisory

- **Weakness**: A category of mistake (CWE-79 = XSS pattern)
- **Advisory**: A specific instance (CVE-2024-1234 = XSS in ProductX)

Multiple advisories can share the same weakness type.

## Relationships

Advisories reference their underlying weakness:

```json
{
  "from": "secid:advisory/mitre.org/cve#CVE-2024-1234",
  "to": "secid:weakness/mitre.org/cwe#CWE-79",
  "type": "hasWeakness",
  "asserted_by": "nvd"
}
```

Weaknesses can be related to attack techniques:

```json
{
  "from": "secid:weakness/mitre.org/cwe#CWE-89",
  "to": "secid:ttp/mitre.org/capec#CAPEC-66",
  "type": "exploitedBy",
  "description": "SQL injection exploited by CAPEC-66"
}
```

## AI-Specific Weaknesses

### CWE AI Entries (CWE-1400 series)

| CWE | Name |
|-----|------|
| CWE-1426 | Improper Validation of Generative AI Output |
| CWE-1427 | Improper Neutralization of Input for LLM Prompting |
| CWE-1434 | Insecure ML Model Inference Parameters |

### OWASP LLM Top 10 v2.0 (2025)

| ID | Name |
|----|------|
| LLM01 | Prompt Injection |
| LLM02 | Sensitive Information Disclosure |
| LLM03 | Supply Chain |
| LLM04 | Data and Model Poisoning |
| LLM05 | Improper Output Handling |
| LLM06 | Excessive Agency |
| LLM07 | System Prompt Leakage |
| LLM08 | Vector and Embedding Weaknesses |
| LLM09 | Misinformation |
| LLM10 | Unbounded Consumption |

### OWASP ML Top 10 (Machine Learning)

| ID | Name |
|----|------|
| ML01 | Input Manipulation Attack |
| ML02 | Data Poisoning Attack |
| ML03 | Model Inversion Attack |
| ML04 | Membership Inference Attack |
| ML05 | Model Theft |
| ML06 | AI Supply Chain Attacks |
| ML07 | Transfer Learning Attack |
| ML08 | Model Skewing |
| ML09 | Output Integrity Attack |
| ML10 | Model Poisoning |

### Comprehensive AI Risk Coverage

For deeper AI risk analysis beyond Top 10 lists:

| Source | Scope |
|--------|-------|
| NIST AI 100-2 | Official US government AML taxonomy |
| BIML ML Risks | 78 architectural ML security risks |
| BIML LLM Risks | 81 LLM-specific risks |
| MIT AI Risk Repository | 1,700+ risks across 7 domains |
| OWASP AI Exchange | Comprehensive AI security knowledge base |

