---
type: advisory
namespace: redhat.com
full_name: "Red Hat (IBM)"
operator: "secid:entity/redhat.com"
website: "https://www.redhat.com"
status: active

sources:
  errata:
    full_name: "Red Hat Errata"
    urls:
      website: "https://access.redhat.com/errata/"
      about: "https://access.redhat.com/security/updates/advisory"
      search: "https://access.redhat.com/errata-search/#/"
      api: "https://access.redhat.com/hydra/rest/securitydata"
      lookup: "https://access.redhat.com/errata/{id}"
    id_patterns:
      - pattern: "RHSA-\\d{4}:\\d+"
        description: "Red Hat Security Advisory"
        type: security
      - pattern: "RHBA-\\d{4}:\\d+"
        description: "Red Hat Bug Advisory"
        type: bugfix
      - pattern: "RHEA-\\d{4}:\\d+"
        description: "Red Hat Enhancement Advisory"
        type: enhancement
    examples:
      - "secid:advisory/redhat.com/errata#RHSA-2024:1234"
      - "secid:advisory/redhat.com/errata#RHBA-2024:5678"
      - "secid:advisory/redhat.com/errata#RHEA-2024:9012"

  cve:
    full_name: "Red Hat CVE Database"
    urls:
      website: "https://access.redhat.com/security/"
      api: "https://access.redhat.com/hydra/rest/securitydata"
      lookup: "https://access.redhat.com/security/cve/{id}"
    id_pattern: "CVE-\\d{4}-\\d{4,}"
    examples:
      - "secid:advisory/redhat.com/cve#CVE-2024-1234"
      - "secid:advisory/redhat.com/cve#CVE-2023-44487"

  bugzilla:
    full_name: "Red Hat Bugzilla"
    urls:
      website: "https://bugzilla.redhat.com"
      lookup: "https://bugzilla.redhat.com/show_bug.cgi?id={id}"
    id_patterns:
      - pattern: "\\d+"
        description: "Bugzilla bug ID"
        type: primary
      - pattern: "CVE-\\d{4}-\\d{4,}"
        description: "CVE alias (redirects to associated bug)"
        type: alias
    examples:
      - "secid:advisory/redhat.com/bugzilla#2045678"
      - "secid:advisory/redhat.com/bugzilla#CVE-2024-1234"
---

# Red Hat Advisory Sources

Red Hat is the world's largest open-source software company, acquired by IBM in 2019. Red Hat Enterprise Linux (RHEL) is the leading enterprise Linux distribution. Red Hat Product Security handles vulnerability response.

## Why Red Hat Matters for Security

Red Hat is enterprise Linux:

- **RHEL** - Red Hat Enterprise Linux, the enterprise standard
- **OpenShift** - Kubernetes platform
- **Ansible** - Automation platform
- **Fedora** - Upstream community distribution

RHEL and its derivatives (CentOS Stream, Rocky, Alma, Oracle Linux) run most enterprise Linux workloads.

## Errata Types

| Prefix | Type | Description |
|--------|------|-------------|
| RHSA | Security Advisory | Security vulnerability fixes |
| RHBA | Bug Advisory | Bug fixes (non-security) |
| RHEA | Enhancement Advisory | New features |

## Red Hat CVE Database

Red Hat maintains its own CVE database with:
- Red Hat-specific CVSS scores (may differ from NVD)
- Affected Red Hat products
- Mitigation guidance
- Links to fixing errata

---

## errata

Red Hat's errata system publishes advisories for security fixes, bug fixes, and enhancements to Red Hat products.

### Format

```
secid:advisory/redhat.com/errata#RHSA-YYYY:NNNN   # Security Advisory
secid:advisory/redhat.com/errata#RHBA-YYYY:NNNN   # Bug Advisory
secid:advisory/redhat.com/errata#RHEA-YYYY:NNNN   # Enhancement Advisory
```

### Advisory Types

| Prefix | Type | Description |
|--------|------|-------------|
| `RHSA` | Security Advisory | Fixes for security vulnerabilities (CVEs) |
| `RHBA` | Bug Advisory | Fixes for non-security bugs |
| `RHEA` | Enhancement Advisory | New features or improvements |

### Resolution

All three types resolve to the same URL pattern:

```
secid:advisory/redhat.com/errata#RHSA-2024:1234
  -> https://access.redhat.com/errata/RHSA-2024:1234
```

### Notes

- RHSA advisories often fix multiple CVEs in a single errata
- Errata are tied to specific product versions and architectures
- Each errata includes affected packages and their updated versions
- Security advisories (RHSA) include severity ratings

---

## cve

Red Hat's CVE pages provide Red Hat-specific analysis of CVEs, including their own CVSS scores, affected products, and mitigation guidance.

### Format

```
secid:advisory/redhat.com/cve#CVE-YYYY-NNNN
```

### Resolution

```
secid:advisory/redhat.com/cve#CVE-2024-1234
  -> https://access.redhat.com/security/cve/CVE-2024-1234
  -> https://access.redhat.com/hydra/rest/securitydata/cve/CVE-2024-1234.json
```

### Notes

- Red Hat CVE pages have their own CVSS scores (may differ from NVD)
- Includes RHEL-specific mitigation and remediation guidance
- Shows which Red Hat products are affected
- Links to related errata (RHSA) that fix the CVE

### Relationship to Errata

CVE pages describe the vulnerability. Errata (RHSA/RHBA/RHEA) are the actual fixes:

```
secid:advisory/redhat.com/cve#CVE-2024-1234      # The vulnerability description
secid:advisory/redhat.com/errata#RHSA-2024:1234  # The fix for that vulnerability
```

---

## bugzilla

Red Hat's bug tracking system. Security bugs are tracked here with CVE aliases.

### Format

```
secid:advisory/redhat.com/bugzilla#NNNNNNN           # Direct bug ID
secid:advisory/redhat.com/bugzilla#CVE-YYYY-NNNN    # CVE alias (redirects)
```

### Resolution

Both forms resolve to the same URL pattern - Bugzilla handles CVE aliases automatically:

```
secid:advisory/redhat.com/bugzilla#2045678
  -> https://bugzilla.redhat.com/show_bug.cgi?id=2045678

secid:advisory/redhat.com/bugzilla#CVE-2024-1234
  -> https://bugzilla.redhat.com/show_bug.cgi?id=CVE-2024-1234
  -> (redirects to the bug tracking that CVE)
```

### Alias Support

Bugzilla supports CVE aliases - you can look up a bug by its CVE identifier, and Bugzilla will redirect to the actual bug. This means both forms are valid SecIDs:

- `#2045678` - The canonical Bugzilla bug ID
- `#CVE-2024-1234` - An alias that resolves to the same bug

When possible, prefer the numeric bug ID for stability (aliases can theoretically change, though this is rare).

### Notes

- Security bugs often have restricted access until fixes are released
- CVE aliases are added when a CVE is assigned to a bug
- One bug may track multiple CVEs (or vice versa in rare cases)

### Relationships

```
secid:advisory/redhat.com/bugzilla#2045678 -> tracks -> secid:advisory/mitre.org/cve#CVE-2024-1234
secid:advisory/redhat.com/errata#RHSA-2024:1234 -> fixes -> secid:advisory/redhat.com/bugzilla#2045678
```
