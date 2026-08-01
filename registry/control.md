# Controls Type (`control`)

This type contains references to security controls, frameworks, benchmarks, and documentation standards.

## Purpose

Track and reference things that define security requirements - what you need to do, test, or document:

**Control Requirements** (frameworks that define what to implement):
- NIST Cybersecurity Framework (CSF)
- CSA Cloud Controls Matrix (CCM)
- CSA AI Controls Matrix (AICM)
- CIS Controls
- ISO 27001 Annex A controls
- OWASP ASVS (Application Security Verification Standard)

**Control Capabilities** (guidance that helps implement requirements):
- NIST SP 800-61 (Incident Response)
- NIST SP 800-86 (Forensics)
- NIST SP 800-53 (Security and Privacy Controls)
- CIS Benchmarks (hardening guides)

## Identifier Format

```
secid:control/<namespace>/<name>[@version][#subpath]

secid:control/cloudsecurityalliance.org/aicm@1.1.0#INP-01
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12
secid:control/nist.gov/csf@2.0#PR.AC-1
secid:control/cisecurity.org/controls@8.0#1.1
secid:control/iso.org/27001@2022#A.8.1
secid:control/owasp.org/asvs@4.0#V5.3.4
```

The namespace is the organization, the name is the framework/document, and the subpath references specific controls within that framework.

## Namespaces

### Control Requirements (Frameworks)

| Namespace | Name | Framework | Description |
|-----------|------|-----------|-------------|
| `nist.gov` | `csf` | NIST Cybersecurity Framework | Cybersecurity framework |
| `cisecurity.org` | `controls` | CIS Controls | Center for Internet Security |
| `iso.org` | `27001` | ISO 27001 | Information security standard |
| `owasp.org` | `asvs` | OWASP ASVS | Application security controls |
| `cloudsecurityalliance.org` | `ccm` | CSA Cloud Controls Matrix | Cloud security controls |

### AI-Specific Control Frameworks

| Namespace | Name | Framework | Description |
|-----------|------|-----------|-------------|
| `cloudsecurityalliance.org` | `aicm` | CSA AI Controls Matrix | AI-specific security controls |
| `owasp.org` | `ai-exchange` | OWASP AI Exchange | AI controls mapped to threats |
| `nist.gov` | `ai-rmf` | NIST AI RMF | AI Risk Management Framework |

### Control Capabilities (Guidance)

| Namespace | Name | Publication | Description |
|-----------|------|-------------|-------------|
| `nist.gov` | `800-53` | NIST SP 800-53 | Security and Privacy Controls |
| `nist.gov` | `800-61` | NIST SP 800-61 | Incident Response guidance |
| `nist.gov` | `800-86` | NIST SP 800-86 | Forensics guidance |
| `cisecurity.org` | `benchmark` | CIS Benchmarks | Platform hardening guides |

### Prescriptive Benchmarks

Benchmarks that define **what to test** are semantically requirements - "your model should pass these tests." They live in `control` rather than a separate type.

| Namespace | Name | Benchmark | Description |
|-----------|------|-----------|-------------|
| `safe.ai` | `harmbench`, `wmdp` | CAIS | Harmful behavior and dangerous knowledge benchmarks |
| `allenai.org` | `decodingtrust`, `realtoxicityprompts` | AI2 | Trustworthiness and toxicity benchmarks |
| `mlcommons.org` | `ailuminate` | MLCommons | AI safety benchmark (12 hazard categories) |
| `jailbreakbench.github.io` | `jbb` | JailbreakBench | Jailbreak robustness evaluation |
| `trustllmbenchmark.github.io` | `benchmark` | TrustLLM | Comprehensive LLM trustworthiness benchmark |
| `thu-coai.github.io` | `benchmark` | SafetyBench | Chinese LLM safety evaluation |
| `llm-attacks.github.io` | `benchmark` | AdvBench | Adversarial behavior benchmark |
| `alignment.org` | `evals` | ARC | Dangerous capability evaluations |
| `metr.org` | `task-standard` | METR | AI evaluation task standard |

**Why benchmarks in `control`?** A prescriptive benchmark ("test for X") is functionally a requirement. Results/leaderboards are different - they're data about how models performed, not requirements to meet. If benchmarks diverge enough from traditional controls, we'll split them.

### Documentation Standards

Standards that define **what information to provide** about AI systems - these are disclosure and transparency requirements.

| Namespace | Name | Standard | Description |
|-----------|------|----------|-------------|
| `documentation` | `model-cards`, `datasheets`, `system-cards` | Various | AI documentation standards |

**Why documentation standards in `control`?** "You must document X about your model" is a requirement, similar to "you must implement control Y." The implementation is documentation rather than code, but it's still a compliance requirement.

## Versioning

Controls frameworks have versions. Use `@version` to pin:

```
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12       # CCM version 4.0
secid:control/cisecurity.org/controls@8.0#1.1     # CIS Controls v8
secid:control/nist.gov/csf@2.0#PR.AC-1     # NIST CSF 2.0
```

Omitting version implies "current" or "any version".

## Subpaths

Use `#subpath` with `/` for hierarchy to reference specific controls and sections:

```
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12                   # Specific control
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/audit             # Audit guidance within control
secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12/implementation    # Implementation guidance
secid:control/cloudsecurityalliance.org/aicm@1.1.0#INP-01/Auditing%20Guidelines  # Section with spaces (percent-encoded)
```

## Relationships

Controls mitigate weaknesses:

```json
{
  "from": "secid:control/cloudsecurityalliance.org/aicm@1.1.0#INP-01",
  "to": "secid:weakness/owasp.org/llm-top10@2.0#LLM01",
  "type": "mitigates",
  "strength": "partial",
  "description": "Input validation helps but doesn't fully prevent prompt injection"
}
```

Controls counter TTPs:

```json
{
  "from": "secid:control/nist.gov/csf@2.0#DE.CM-1",
  "to": "secid:ttp/mitre.org/attack#T1059",
  "type": "detects",
  "description": "Monitoring detects command execution"
}
```

Controls satisfy regulatory requirements:

```json
{
  "from": "secid:control/iso.org/27001@2022#A.8.1",
  "to": "secid:regulation/europa.eu/gdpr#art-32",
  "type": "satisfies",
  "description": "Asset management control satisfies GDPR security requirement"
}
```

## AI-Specific Controls

The CSA AI Controls Matrix provides AI-specific controls organized around:
- Input validation and sanitization
- Output filtering and validation
- Model governance and security
- Data protection and privacy
- RAG (Retrieval Augmented Generation) security
- Agent and tool security

## Control vs Weakness vs TTP

- **Weakness** (weakness): What's wrong (CWE-79 = XSS pattern)
- **TTP** (ttp): How attackers exploit it (T1059 = command execution)
- **Control** (control): How to prevent/detect/respond - both requirements and capabilities

## Requirements vs Capabilities

Think of it this way:
- **Requirements** answer: "What security controls must we have?"
- **Capabilities** answer: "How do we implement those controls?"

Example:
- `secid:control/nist.gov/csf@2.0#RS.RP-1` - Requirement: "Response plan is executed"
- `secid:control/nist.gov/800-61#section-3` - Capability: How to do incident response

