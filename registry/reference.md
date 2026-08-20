# Reference Type

The `reference` type identifies documents and publications that **don't fit into other SecID types**.

## Purpose

References are for citing source materials that aren't covered by other types. If something has a more specific type, use that instead.

## What Belongs Here

| Category | Examples | Why it's a reference |
|----------|----------|---------------------|
| **Executive Orders** | EO 14110 on AI | Policy, not law (yet) |
| **National Strategies** | National Cybersecurity Strategy | Aspirational, not binding |
| **Policy Memos** | OMB M-24-10 | Agency guidance, not regulation |
| **Research Papers** | ArXiv preprints | Academic research |

## What Does NOT Belong Here

| Don't use reference for | Use instead |
|------------------------|-------------|
| NIST SP 800-53 | `secid:control/nist.gov/800-53#AC-1` |
| NIST CSF | `secid:control/nist.gov/csf@2.0#GV.RM-01` |
| ISO 27001 | `secid:control/iso.org/27001@2022#A.8.1` |
| An RFC that defines a *process* | `secid:methodology/ietf.org/rfc-3227` (evidence collection) — but RFCs are `reference` by default: `secid:reference/ietf.org/9116` |
| GDPR, HIPAA | `secid:regulation/europa.eu/gdpr`, `secid:regulation/govinfo.gov/hipaa` |
| CWE, OWASP Top 10 | `secid:weakness/mitre.org/cwe#CWE-79`, `secid:weakness/owasp.org/top10#A01` |
| CVE, NVD | `secid:advisory/mitre.org/cve#...`, `secid:advisory/nist.gov/nvd#...` |
| ATT&CK, ATLAS | `secid:ttp/mitre.org/attack#T1059`, `secid:ttp/mitre.org/atlas#AML.T0043` |

## Identifier Format

```
secid:reference/<namespace>/<identifier>
```

## Namespaces

| Namespace | Description | Example IDs |
|-----------|-------------|-------------|
| `whitehouse.gov` | US Executive Branch publications | `eo-14110`, `ncs-2023`, `m-24-10` |
| `arxiv.org` | ArXiv research papers | `2303.08774`, `2402.05369` |

### Examples

```
secid:reference/whitehouse.gov/eo-14110           # AI Executive Order
secid:reference/whitehouse.gov/ncs-2023           # National Cybersecurity Strategy
secid:reference/whitehouse.gov/m-24-10            # OMB AI Governance Memo
secid:reference/whitehouse.gov/nsm-22             # National Security Memo
secid:reference/arxiv.org/2303.08774              # GPT-4 Technical Report
secid:reference/arxiv.org/2402.05369              # Sleeper Agents paper
secid:reference/arxiv.org/2307.03109              # Jailbroken paper
```

## Subpaths

Reference specific sections within documents:

```
secid:reference/whitehouse.gov/eo-14110#section-4.1
secid:reference/whitehouse.gov/eo-14110#section-4.2
secid:reference/arxiv.org/2303.08774#section-3
secid:reference/arxiv.org/2303.08774#appendix-a
```

## Relationships

| Relationship | Meaning | Example |
|--------------|---------|---------|
| `precedes` | Policy that led to regulation | `reference/whitehouse.gov/eo-14110 → precedes → regulation/govinfo.gov/...` |
| `cites` | Used as evidence | `weakness/... → cites → reference/arxiv.org/...` |
| `informs` | Research informing practice | `reference/arxiv.org/... → informs → control/...` |

## Future Namespaces

As needed, we may add:
- `eu-policy` - EU Commission policy documents (not yet regulations)
- `uk-policy` - UK government policy papers
- `congress` - US Congressional reports, bills

