# Methodology Type (`methodology`)

Identifiers for **formal processes with defined inputs, steps, and outputs** — the named, published methodologies used to produce security analysis, scores, mappings, decisions, classifications, and reports.

## Purpose

Track and reference the processes used to produce security knowledge:

**Mapping Methodologies:**
- NIST IR 8477 (crosswalk, supportive, STRM, structural + selection)
- CTID Control Framework → ATT&CK mapping
- CSA CCM mapping methodology

**Scoring and Prioritization:**
- CVSS v4.0 (vulnerability severity scoring)
- SSVC v2.0 (stakeholder-specific vulnerability categorization)
- EPSS (exploit prediction scoring)

**Risk and Assessment:**
- ISO 27005 (information security risk assessment)
- NIST RMF / SP 800-37 (risk management framework)
- FAIR (Factor Analysis of Information Risk)

**Threat Modeling:**
- STRIDE, PASTA, VAST, LINDDUN, TRIKE

## Why Methodology Is Separate from Control and Reference

| | Control | Methodology | Reference |
|--|---------|-------------|-----------|
| **Duck test** | "Implement these requirements" | "Follow this process to produce an output" | "Read/cite this document" |
| **Primary purpose** | Define what must be done | Define how to systematically do it | Inform or provide evidence |
| **Output when used** | Compliance state | Score, mapping, decision, classification, report | Understanding |
| **Authority** | Standards body (prescriptive) | Process publisher (procedural) | Author (informational) |
| **Consumer question** | "What must I do?" | "How do I produce a defensible result?" | "Where can I read about this?" |

**Classification criterion ("duck test"):** "If someone hands you this document and asks 'what do I DO with it?' — is the primary answer 'follow this process to produce an output'?" If yes, it's a methodology.

## Identifier Format

```
secid:methodology/<namespace>/<name>[@version][#<subpath>]

secid:methodology/nist.gov/ir-8477                       # All mapping styles
secid:methodology/nist.gov/ir-8477#strm                  # STRM specifically
secid:methodology/first.org/cvss@4.0                     # CVSS v4.0
secid:methodology/cmu.edu/ssvc@2.0                       # SSVC v2.0
secid:methodology/iso.org/27005@2022                     # Risk assessment
secid:methodology/microsoft.com/stride                   # STRIDE threat modeling
```

## Namespaces

| Namespace | Methodologies | Description |
|-----------|---------------|-------------|
| `nist.gov` | ir-8477, rmf, 800-30, 800-61, 800-115, 800-161 | NIST process standards |
| `first.org` | cvss, epss, tlp | FIRST scoring and classification |
| `cmu.edu` | ssvc | CMU SEI/CERT/CC prioritization |
| `iso.org` | 27005, 27035, 29147, 30111, 31000, 27037-27043, 27006, 27007, 17021 | ISO process standards |
| `cisa.gov` | attck-mapping | CISA mapping best practices |
| `microsoft.com` | stride | STRIDE threat modeling |

## Relationships

Methodologies connect to controls and capabilities as process provenance:

```json
{
  "from": "secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-01",
  "to": "secid:control/nist.gov/csf@2.0#PR.AC-1",
  "relationship": "supports",
  "methodology": "secid:methodology/nist.gov/ir-8477#supportive"
}
```

## Notes

- Methodology is the smallest SecID type by volume (~40-60 entries) but high importance: provides process provenance for the relationship layer
- Sub-methodologies are first-class referenceable entities via subpath
- Tools that implement methodologies (CVSS calculators, mapping tools) go in `entity` type; the "implements" relationship is relationship-layer data
- Documents that contain embedded methodology alongside primarily-control content stay in their original type; create a separate `methodology` record that cites the parent
