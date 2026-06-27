---
type: control
namespace: github.com/stuwrtlttle
full_name: "Common Mitigation Enumeration"
operator: "secid:entity/github.com/stuwrtlttle"
website: "https://github.com/stuwrtlttle/cme"
status: draft

sources:
  cme:
    full_name: "Common Mitigation Enumeration"
    urls:
      website: "https://github.com/stuwrtlttle/cme"
      site: "https://stuwrtlttle.github.io/cme/"
      schema: "https://raw.githubusercontent.com/stuwrtlttle/cme/refs/heads/main/schema/cme-entry.schema.json"
    id_pattern: "^CME-\\d{3,4}$"
    examples:
      - "secid:control/github.com/stuwrtlttle/cme#CME-601"
      - "secid:control/github.com/stuwrtlttle/cme#CME-1001"
---

# Common Mitigation Enumeration (CME)

CME is a structured taxonomy of **defensive security controls**. Where CVE
identifies vulnerabilities and CWE identifies weakness classes, CME enumerates
the **mitigations** — and maps each control to a deterministic CVSS
environmental-score attenuation and to the CWE classes it addresses.

Prototype by J. West (2026), ~109 entries at time of registration.

## Why CME Matters

- **Deterministic environmental scoring** — replaces subjective CVSS
  environmental judgment with a control → vector-attenuation lookup table
- **D3FEND-aligned** — tactics are Harden, Isolate, Detect, Evict, Restore
- **Machine-verifiable** — each entry ships shell commands a scanner or agent
  can run to confirm the control is active
- **AI-first** — primary consumers are security agents performing "risk
  negotiation" over a host's active controls

---

## cme

CME prescribes defensive controls identified as `CME-NNN` (or `CME-NNNN`).

### Format

```
secid:control/github.com/stuwrtlttle/cme#CME-601
```

### Resolution

Each `CME-NNN` subpath resolves to two URLs (the structured record is primary):

| Weight | Form | URL template |
|--------|------|--------------|
| 100 | Raw JSON (structured, source of truth) | `https://raw.githubusercontent.com/stuwrtlttle/cme/refs/heads/main/data/entries/{id}.json` |
| 50 | GitHub rendered view (human-readable) | `https://github.com/stuwrtlttle/cme/blob/main/data/entries/{id}.json` |

### ID Ranges

| Range | Category |
|-------|----------|
| CME-100–199 | Kernel Hardening |
| CME-200–299 | Network Isolation |
| CME-300–399 | Mandatory Access Control |
| CME-400–499 | Cryptographic Controls |
| CME-500–599 | Filesystem Hardening |
| CME-600–699 | Syscall & BPF Controls |
| CME-700–799 | Container & Privilege Isolation |
| CME-800–899 | Credential & Identity Hardening |
| CME-900–999 | Network Protocol & Application Controls |
| CME-1000–1099 | Detection & Monitoring |
| CME-1100–1199 | Eviction & Patch Management |
| CME-1200–1299 | Restore & Recovery |
| CME-1300–1399 | Application Input Validation |

## Notes

- **Registry scope is identity + resolution only.** Per-control data (CVSS
  attenuation, CWE relationships, verification commands) is not duplicated here;
  it lives in the source records and, in SecID terms, belongs to the future
  Data layer (planned V2).
- The CWE ↔ CME mappings are a natural fit for the future Relationship layer
  ("this weakness is mitigated by this control").
- The `github.com/stuwrtlttle` namespace currently represents the CME project.
