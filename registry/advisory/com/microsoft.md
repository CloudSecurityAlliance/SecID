---
type: advisory
namespace: microsoft.com
full_name: "Microsoft Corporation"
operator: "secid:entity/microsoft.com"
website: "https://www.microsoft.com"
status: active

sources:
  msrc:
    full_name: "Microsoft Security Response Center"
    urls:
      website: "https://msrc.microsoft.com"
      api: "https://api.msrc.microsoft.com/cvrf/v2.0"
      lookup: "https://msrc.microsoft.com/update-guide/vulnerability/{id}"
    id_pattern: "CVE-\\d{4}-\\d{4,}"
    examples:
      - "secid:advisory/microsoft.com/msrc#CVE-2024-1234"
      - "secid:advisory/microsoft.com/msrc#CVE-2023-44487"
  advisory:
    full_name: "Microsoft Security Advisory"
    urls:
      website: "https://msrc.microsoft.com"
      lookup: "https://msrc.microsoft.com/update-guide/advisory/{id}"
    id_pattern: "ADV\\d{6}"
    examples:
      - "secid:advisory/microsoft.com/advisory#ADV240001"
      - "secid:advisory/microsoft.com/advisory#ADV230001"
  kb:
    full_name: "Microsoft Knowledge Base"
    urls:
      website: "https://support.microsoft.com"
      lookup: "https://support.microsoft.com/kb/{id}"
    id_pattern: "KB\\d+"
    examples:
      - "secid:advisory/microsoft.com/kb#KB5001234"
      - "secid:advisory/microsoft.com/kb#KB5034441"
  bulletin:
    full_name: "Microsoft Security Bulletin (Deprecated)"
    urls:
      website: "https://docs.microsoft.com/en-us/security-updates/"
      lookup: "https://docs.microsoft.com/en-us/security-updates/securitybulletins/{year}/{id}"
    id_pattern: "MS\\d{2}-\\d{3}"
    status: deprecated
    deprecated_by: "secid:advisory/microsoft.com/msrc"
    deprecated_date: "2017-01"
    examples:
      - "secid:advisory/microsoft.com/bulletin#MS17-010"
      - "secid:advisory/microsoft.com/bulletin#MS08-067"

  threat-intel:
    full_name: "Microsoft Threat Intelligence"
    urls:
      website: "https://www.microsoft.com/en-us/security/blog/threat-intelligence/"
      vulnerabilities: "https://www.microsoft.com/en-us/security/blog/threat-intelligence/vulnerabilities-and-exploits/"
      rss: "https://www.microsoft.com/en-us/security/blog/feed/"
    examples:
      - "secid:advisory/microsoft.com/threat-intel#vulnerabilities"
      - "secid:advisory/microsoft.com/threat-intel#exploits"
---

# Microsoft Advisory Sources

Microsoft is one of the world's largest technology companies, producing Windows, Office, Azure, and many other products. The Microsoft Security Response Center (MSRC) handles vulnerability disclosure and security updates.

## Why Microsoft Matters for Security

Microsoft's products are ubiquitous targets:

- **Windows** - Runs on billions of devices
- **Azure** - Major cloud platform
- **Office/365** - Enterprise productivity suite
- **Active Directory** - Enterprise identity infrastructure
- **Exchange** - Email infrastructure

Microsoft vulnerabilities frequently appear in CISA KEV and are targeted by nation-state actors.

## Patch Tuesday

Microsoft releases security updates on the second Tuesday of each month ("Patch Tuesday"). This predictable schedule helps organizations plan patching.

## Historical Note

Before 2017, Microsoft used MS##-### format (e.g., MS17-010 for EternalBlue). These legacy bulletins are still referenced for historical vulnerabilities but new advisories use MSRC and CVE IDs.

## Notes

- Microsoft is a CVE Numbering Authority (CNA)
- MSRC provides its own CVSS scores which may differ from NVD
- Some advisories are Windows-specific, others cover Azure, Office, etc.

---

## msrc

Microsoft Security Response Center vulnerability database.

### Format

```
secid:advisory/microsoft.com/msrc#CVE-YYYY-NNNN
```

### Resolution

```
secid:advisory/microsoft.com/msrc#CVE-2024-1234
  -> https://msrc.microsoft.com/update-guide/vulnerability/CVE-2024-1234
  -> https://api.msrc.microsoft.com/sug/v2.0/en-US/vulnerability/CVE-2024-1234
```

### Notes

- MSRC provides Microsoft's view of CVEs affecting their products
- Patch Tuesday releases monthly security updates
- For security advisories (ADV), see `secid:advisory/microsoft.com/advisory`
- For KB articles, see `secid:advisory/microsoft.com/kb`

---

## advisory

Microsoft security advisories for defense-in-depth updates and security guidance.

### Format

```
secid:advisory/microsoft.com/advisory#ADVYYNNNN
```

Where YY is the year and NNNN is the sequential number.

### Resolution

```
secid:advisory/microsoft.com/advisory#ADV240001
  -> https://msrc.microsoft.com/update-guide/advisory/ADV240001
```

### Notes

- ADV advisories cover defense-in-depth updates
- May not have associated CVE identifiers
- For CVE-specific information, see `secid:advisory/microsoft.com/msrc`
- For KB articles, see `secid:advisory/microsoft.com/kb`

---

## kb

Microsoft Knowledge Base articles documenting security updates and patches.

### Format

```
secid:advisory/microsoft.com/kb#KBNNNNNNN
```

### Resolution

```
secid:advisory/microsoft.com/kb#KB5001234
  -> https://support.microsoft.com/kb/5001234
```

### Notes

- KB articles document specific patches and updates
- Links patches to the CVEs they fix
- Includes installation instructions and known issues
- For CVE details, see `secid:advisory/microsoft.com/msrc`
- For security advisories, see `secid:advisory/microsoft.com/advisory`

---

## bulletin

Legacy Microsoft security bulletin format, discontinued in 2017.

### Format

```
secid:advisory/microsoft.com/bulletin#MSYY-NNN
```

Two-digit year and three-digit sequential number.

### Resolution

```
secid:advisory/microsoft.com/bulletin#MS17-010
  -> https://docs.microsoft.com/en-us/security-updates/securitybulletins/2017/ms17-010

secid:advisory/microsoft.com/bulletin#MS08-067
  -> https://docs.microsoft.com/en-us/security-updates/securitybulletins/2008/ms08-067
```

### Notes

- **Deprecated since January 2017** - Microsoft moved to MSRC Security Update Guide
- Still widely referenced (MS17-010 = EternalBlue, MS08-067 = Conficker)
- Historical bulletins remain accessible
- For current advisories, use `secid:advisory/microsoft.com/msrc`

---

## threat-intel

Microsoft Threat Intelligence blog covering vulnerabilities, exploits, and threat actor activity.

### Format

```
secid:advisory/microsoft.com/threat-intel#<topic>
```

### Coverage

| Category | Description |
|----------|-------------|
| **Vulnerabilities** | Deep dives on specific CVEs |
| **Exploits** | Exploitation analysis and trends |
| **Threat actors** | Nation-state and criminal groups |
| **Attack techniques** | TTPs observed in the wild |

### Why Threat Intel Matters

Goes beyond MSRC patch notes:
- **Exploitation context** - How vulns are being used in attacks
- **Threat actor attribution** - Who's exploiting what
- **Detection guidance** - Hunting queries, indicators
- **Broader ecosystem** - Not just Microsoft products

### Content Types

| Type | Examples |
|------|----------|
| CVE deep dives | Detailed vulnerability analysis |
| Campaign reports | Active threat campaigns |
| Tool analysis | Malware and exploit kits |
| Trend reports | Quarterly threat summaries |

### Relationship to MSRC

| MSRC | Threat Intel Blog |
|------|-------------------|
| Patch availability | Exploitation analysis |
| Technical details | Attack context |
| Affected products | Threat actor attribution |
| CVSS scores | Real-world impact |

### Notes

- Published by Microsoft Threat Intelligence team
- Covers Microsoft and third-party vulnerabilities
- Includes IoCs and detection guidance
- RSS feed available
