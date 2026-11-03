---
type: advisory
namespace: paloaltonetworks.com
full_name: "Palo Alto Networks"
operator: "secid:entity/paloaltonetworks.com"
website: "https://www.paloaltonetworks.com"
status: active

sources:
  pan-sa:
    full_name: "Palo Alto Networks Security Advisory"
    urls:
      website: "https://security.paloaltonetworks.com/"
      lookup: "https://security.paloaltonetworks.com/{id}"
      json: "https://security.paloaltonetworks.com/json/{id}"
      csaf: "https://security.paloaltonetworks.com/csaf/{id}"
    id_pattern: "CVE-\\d{4}-\\d{4,}"
    examples:
      - "secid:advisory/paloaltonetworks.com/pan-sa#CVE-2024-3400"
      - "secid:advisory/paloaltonetworks.com/pan-sa#CVE-2024-0012"
---

# Palo Alto Advisory Sources

Palo Alto Networks is a cybersecurity company known for next-generation firewalls and the Cortex security platform. They pioneered application-aware firewalls.

## Why Palo Alto Matters for Security

Palo Alto protects enterprise networks:

- **PAN-OS** - Operating system for firewalls
- **GlobalProtect** - VPN and endpoint protection
- **Cortex XDR** - Extended detection and response
- **Prisma** - Cloud security platform
- **Unit 42** - Threat intelligence team

Like Fortinet, Palo Alto firewall vulnerabilities are high-value targets.

## Advisory ID Format

Palo Alto indexes advisories by CVE ID rather than a proprietary ID format. The security portal allows lookup by CVE number directly.

## Notable Vulnerabilities

- **CVE-2024-3400** - Critical PAN-OS command injection (actively exploited)
- **CVE-2024-0012** - Authentication bypass in management interface

Both appeared in CISA KEV with evidence of nation-state exploitation.

## Notes

- Palo Alto is a CVE Numbering Authority (CNA)
- GlobalProtect VPN vulnerabilities are high-risk (internet-exposed)
- Unit 42 publishes detailed threat research and IOCs

---

## pan-sa

Palo Alto Networks security advisories.

### Format

```
secid:advisory/paloaltonetworks.com/pan-sa#CVE-YYYY-NNNN
```

Palo Alto indexes advisories by CVE ID.

### Resolution

```
secid:advisory/paloaltonetworks.com/pan-sa#CVE-2024-3400
  -> https://security.paloaltonetworks.com/CVE-2024-3400
  -> https://security.paloaltonetworks.com/json/CVE-2024-3400
  -> https://security.paloaltonetworks.com/csaf/CVE-2024-3400
```

### Notes

- Covers PAN-OS, GlobalProtect, Cortex, Prisma, etc.
- High-profile vulnerabilities (firewalls are critical infrastructure)
- Also publishes PAN-SA-* identifiers in some contexts
