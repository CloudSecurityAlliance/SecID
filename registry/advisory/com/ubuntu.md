---
type: advisory
namespace: ubuntu.com
full_name: "Ubuntu (Canonical)"
operator: "secid:entity/ubuntu.com"
website: "https://ubuntu.com"
status: active

sources:
  usn:
    full_name: "Ubuntu Security Notice"
    urls:
      website: "https://ubuntu.com/security/notices"
      lookup: "https://ubuntu.com/security/notices/USN-{id}"
    id_pattern: "USN-\\d+-\\d+"
    examples:
      - "secid:advisory/ubuntu.com/usn#USN-6543-1"
      - "secid:advisory/ubuntu.com/usn#USN-6789-2"
  cve-tracker:
    full_name: "Ubuntu CVE Tracker"
    urls:
      website: "https://ubuntu.com/security/cves"
      api: "https://ubuntu.com/security/cves/{id}.json"
      lookup: "https://ubuntu.com/security/cves/{id}"
    id_pattern: "CVE-\\d{4}-\\d{4,}"
    examples:
      - "secid:advisory/ubuntu.com/cve-tracker#CVE-2024-1234"
      - "secid:advisory/ubuntu.com/cve-tracker#CVE-2023-44487"
  launchpad:
    full_name: "Launchpad Bugs"
    urls:
      website: "https://bugs.launchpad.net"
      lookup: "https://bugs.launchpad.net/bugs/{id}"
    id_pattern: "\\d+"
    examples:
      - "secid:advisory/ubuntu.com/launchpad#1234567"
      - "secid:advisory/ubuntu.com/launchpad#2045678"
---

# Ubuntu Advisory Sources

Ubuntu is the most popular Linux distribution for desktops and cloud servers. It's developed by Canonical Ltd and based on Debian. Ubuntu has a dedicated security team and predictable release cycle.

## Why Ubuntu Matters for Security

Ubuntu's reach is extensive:

- **Cloud** - Default/popular choice on AWS, Azure, GCP
- **Desktop** - Most popular Linux desktop distribution
- **Containers** - Common base image for Docker containers
- **IoT** - Ubuntu Core for embedded devices

## Ubuntu Security Notice (USN)

USN format: `USN-NNNN-R` where R indicates revisions/updates.

Each USN may address multiple CVEs and specifies which Ubuntu releases are affected.

## Release Cycle

Ubuntu releases every 6 months (April, October):
- **LTS (Long Term Support)** - Every 2 years (e.g., 22.04, 24.04), 5+ years support
- **Interim releases** - 9 months support

Security support duration varies significantly by release type.

## Pro/Advantage

Ubuntu Pro (formerly Ubuntu Advantage) extends security support:
- Extended security maintenance (ESM)
- Kernel livepatch
- FIPS-certified packages

## Notes

- Ubuntu is downstream of Debian; many packages are shared
- Canonical is a CVE Numbering Authority (CNA)
- Ubuntu's CVE Tracker shows fix status across releases

---

## usn

Canonical's security advisories for Ubuntu.

### Format

```
secid:advisory/ubuntu.com/usn#USN-NNNN-N
```

The suffix (-1, -2, etc.) indicates revisions or updates to the notice.

### Resolution

```
secid:advisory/ubuntu.com/usn#USN-6543-1
  -> https://ubuntu.com/security/notices/USN-6543-1
```

### Notes

- USN advisories cover multiple Ubuntu releases
- Often reference multiple CVEs in a single notice
- For bug tracking, see `secid:advisory/ubuntu.com/launchpad`
- For CVE status, see `secid:advisory/ubuntu.com/cve-tracker`

---

## cve-tracker

Ubuntu's CVE tracking showing status across Ubuntu releases.

### Format

```
secid:advisory/ubuntu.com/cve-tracker#CVE-YYYY-NNNN
```

### Resolution

```
secid:advisory/ubuntu.com/cve-tracker#CVE-2024-1234
  -> https://ubuntu.com/security/cves/CVE-2024-1234
  -> https://ubuntu.com/security/cves/CVE-2024-1234.json
```

### Notes

- Shows CVE status across all supported Ubuntu releases
- Indicates which releases are affected and fix status
- Links to related USN advisories
- For official advisories, see `secid:advisory/ubuntu.com/usn`

---

## launchpad

Ubuntu/Canonical's bug tracking system.

### Format

```
secid:advisory/ubuntu.com/launchpad#NNNNNNN
```

### Resolution

```
secid:advisory/ubuntu.com/launchpad#1234567
  -> https://bugs.launchpad.net/bugs/1234567
```

### Notes

- Launchpad is used for Ubuntu and many other open source projects
- Security bugs may be marked private until fixed
- For official security notices, see `secid:advisory/ubuntu.com/usn`
