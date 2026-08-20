# Advisory Type (`advisory`)

This type contains references to vulnerability advisories, incident reports, and safety publications.

## Purpose

Track and coordinate security and safety publications - anything that documents "something happened":

**Vulnerability Advisories** (traditional security):
- CVE (MITRE) - canonical vulnerability identifier
- NVD (NIST) - CVE enrichment with CVSS, CWE, CPE
- GHSA (GitHub) - package-level advisories
- OSV (Google) - type-specific vulnerability data
- Vendor advisories (Red Hat, Microsoft, Debian, etc.)

## Identifier Format

```
secid:advisory/<namespace>/<name>[#subpath]

secid:advisory/mitre.org/cve#CVE-2024-1234
secid:advisory/nist.gov/nvd#CVE-2024-1234
secid:advisory/github.com/ghsa#GHSA-xxxx-yyyy-zzzz
secid:advisory/google.com/osv#PYSEC-2024-1
secid:advisory/redhat.com/errata#RHSA-2024:1234
secid:advisory/debian.org/dsa#DSA-5678-1
```

## Namespaces

### Core Vulnerability Databases

| Namespace | Names | Source | Description |
|-----------|-------|--------|-------------|
| `mitre.org` | `cve` | MITRE CVE | Canonical vulnerability identifiers |
| `nist.gov` | `nvd` | NIST NVD | CVE enrichment (CVSS, CWE, CPE) |
| `cisa.gov` | `kev`, `vulnrichment` | CISA | Known Exploited Vulnerabilities, CVE enrichment |
| `github.com` | `ghsa` | GitHub | Package security advisories |
| `google.com` | `osv`, `chrome`, `android`, `gcp-bulletins`, `project-zero` | Google | OSV, Chrome, Android, GCP bulletins, P0 |
| `cert.org` | `vu` | CERT/CC | VU# vulnerability notes |

### Ecosystem-Specific

| Namespace | Names | Source | Description |
|-----------|-------|--------|-------------|
| `pypi.org` | `advisory-db` | PyPA | Python package vulnerabilities (PYSEC) |
| `go.dev` | `vulndb` | Go Team | Go module vulnerabilities (GO-) |
| `rustsec.org` | `advisories` | RustSec | Rust crate vulnerabilities (RUSTSEC-) |

### AI Security

| Namespace | Names | Source | Description |
|-----------|-------|--------|-------------|
| `avidml.org` | `avid` | AVID | AI Vulnerability Database (AVID-YYYY-VNNN) |
| `protectai.com` | `huntr`, `sightline` | Protect AI | AI/ML vulnerability tracking |
| `embracethered.com` | `moaib` | Embrace The Red | Month of AI Bugs disclosures |

### Incident Reports

Incident databases track "something happened" events - safety failures, AI harms, autonomous system accidents. These share the `advisory` type because they're structurally similar to vulnerability advisories (publication about an event).

| Namespace | Names | Source | Description |
|-----------|-------|--------|-------------|
| `partnershiponai.org` | `aiid` | Partnership on AI | AI Incident Database |
| `aiaaic.org` | `repository` | AIAAIC | AI/Algorithmic Incidents & Controversies |
| `nhtsa.gov` | `av-safety` | NHTSA | Autonomous vehicle safety data |
| `dmv.ca.gov` | `av-reports` | California DMV | AV collision/disengagement reports |
| `fda.gov` | `maude`, `recalls` | FDA | Medical device adverse events and recalls |

**Why incidents in `advisory`?** Both vulnerability disclosures and incident reports are publications documenting that something went wrong. The resolution pattern is similar (look up by ID, get event details). If incidents grow distinct enough to need different handling, we'll split them into a separate type.

### Linux Distributions

| Namespace | Names | Source | Description |
|-----------|-------|--------|-------------|
| `redhat.com` | `cve`, `errata`, `bugzilla` | Red Hat | CVE pages, RHSA/RHBA/RHEA, Bugzilla |
| `debian.org` | `dsa`, `dla`, `tracker`, `bts` | Debian | DSA, DLA, CVE tracker, bug tracking |
| `ubuntu.com` | `usn`, `launchpad`, `cve-tracker` | Ubuntu | USN, Launchpad bugs, CVE tracker |
| `suse.com` | `suse-su`, `bugzilla` | SUSE | Security updates, Bugzilla |
| `aws.amazon.com` | `alas` | AWS | Amazon Linux Security Advisories |

### Major Vendors

| Namespace | Names | Source | Description |
|-----------|-------|--------|-------------|
| `microsoft.com` | `msrc`, `advisory`, `kb`, `bulletin` | Microsoft | MSRC, ADV, KB, legacy MS bulletins |
| `cisco.com` | `psirt`, `bug` | Cisco | PSIRT advisories, CSC bug IDs |
| `vmware.com` | `vmsa` | VMware/Broadcom | VMSA advisories |
| `fortinet.com` | `fsa` | Fortinet | FG-IR advisories |
| `paloaltonetworks.com` | `pan-sa` | Palo Alto | PAN-SA advisories |
| `oracle.com` | `cpu`, `alert` | Oracle | Critical Patch Updates, Security Alerts |
| `apple.com` | `ht` | Apple | HT security articles |

### Open Source Projects

| Namespace | Names | Source | Description |
|-----------|-------|--------|-------------|
| `mozilla.org` | `mfsa`, `bugzilla` | Mozilla | MFSA advisories, Bugzilla bugs |
| `apache.org` | `security`, `jira` | Apache | Security pages, Jira issues |
| `kernel.org` | `kernel` | Linux | Kernel CVEs |
| `openssl.org` | `secadv` | OpenSSL | Security advisories |
| `atlassian.com` | `jira-security` | Atlassian | Confluence, Jira, Bitbucket advisories |

### National/Regional

| Namespace | Names | Source | Description |
|-----------|-------|--------|-------------|
| `cnvd.org.cn` | `cnvd` | China CNVD | Chinese vulnerability database |
| `europa.eu` | `euvd` | EU EUVD | European vulnerability database |

## Why "Advisory" (Not "Vulnerability")?

A vulnerability doesn't exist without a description. The CVE Record IS what defines the CVE - there's no platonic vulnerability floating independent of some advisory describing it.

- **No redundancy**: CVE exists once, not in both `vulnerability/` and `advisory/`
- **Handles multi-vuln advisories**: RHSA-2024:1234 can be about multiple CVEs
- **Correct semantics**: All vulnerability records ARE publications/advisories

Canonical sources (CVE, OSV) are distinguished through **relationships**, not separate types.

## Vendors with Multiple Advisory Systems

Some vendors have multiple advisory systems, each with its own `name`:

**Red Hat example:**

```
secid:advisory/redhat.com/cve#CVE-2024-1234      # Red Hat CVE Database (vulnerability info)
secid:advisory/redhat.com/errata#RHSA-2024:1234  # Red Hat Security Advisory (the fix)
secid:advisory/redhat.com/errata#RHBA-2024:5678  # Red Hat Bug Advisory
secid:advisory/redhat.com/errata#RHEA-2024:9012  # Red Hat Enhancement Advisory
secid:advisory/redhat.com/bugzilla#2045678       # Bugzilla bug (by ID)
secid:advisory/redhat.com/bugzilla#CVE-2024-1234 # Bugzilla bug (by CVE alias)
```

The `name` distinguishes the system (`cve` vs `errata` vs `bugzilla`). Within errata, the subpath prefix (`RHSA-`, `RHBA-`, `RHEA-`) distinguishes advisory types. Bugzilla accepts both numeric IDs and CVE aliases.

**Microsoft example:**

```
secid:advisory/microsoft.com/msrc#CVE-2024-1234      # MSRC CVE database
secid:advisory/microsoft.com/advisory#ADV240001      # Security Advisory (defense-in-depth)
secid:advisory/microsoft.com/kb#KB5001234            # Knowledge Base article (patch)
```

**Debian example:**

```
secid:advisory/debian.org/dsa#DSA-5678-1         # Debian Security Advisory (stable)
secid:advisory/debian.org/dla#DLA-3456-1         # Debian LTS Advisory (extended support)
secid:advisory/debian.org/tracker#CVE-2024-1234  # Debian Security Tracker (CVE status)
```

## Advisory vs Weakness vs Reference

- **Advisory** (advisory): A publication about a *specific* vulnerability or event — CVE-2021-44228, RHSA-2026:0932
- **Weakness** (weakness): The *category* of mistake that instance belongs to — CWE-79
- **Reference** (reference): A document *about* vulnerabilities generally — a threat report, a research paper

The test is specificity plus event-hood. An advisory says "this happened, here, to this" and carries an
identifier issued when it was published. A report discussing a class of vulnerabilities is `reference`,
even when it names CVEs; a paper proposing a new attack technique is `reference`, even when the technique
later earns a `ttp` entry.

Incident reports — an AI system caused harm, a vehicle behaved unsafely — are `advisory` with
`subtype: ["incident"]`. They differ from vulnerability advisories in *what happened* (an event occurred, as
against a flaw being disclosed) but are identical in resolution shape: a publication with an ID and a URL.

## Relationships

Advisories connect through aliasing and enrichment:

```json
{
  "from": "secid:advisory/github.com/ghsa#GHSA-xxxx-yyyy",
  "to": "secid:advisory/mitre.org/cve#CVE-2024-1234",
  "type": "aliases",
  "asserted_by": "github"
}
```

```json
{
  "from": "secid:advisory/nist.gov/nvd#CVE-2024-1234",
  "to": "secid:advisory/mitre.org/cve#CVE-2024-1234",
  "type": "enriches",
  "description": "NVD adds CVSS, CPE, CWE to CVE records"
}
```

```json
{
  "from": "secid:advisory/redhat.com/errata#RHSA-2024:1234",
  "to": "secid:advisory/mitre.org/cve#CVE-2024-1234",
  "type": "about",
  "description": "RHSA addresses this CVE"
}
```

## Notes

- CVE is a MITRE project: `secid:advisory/mitre.org/cve#CVE-2024-1234`
- NVD enriches CVE but doesn't issue IDs - it's NIST's view: `secid:advisory/nist.gov/nvd#CVE-2024-1234`
- Different databases may have the same vulnerability with different IDs
- Use `aliases` relationship to connect equivalent advisories

