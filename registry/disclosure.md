# Disclosure Type (`disclosure`)

Identifiers for **vulnerability disclosure programs, policies, reporting channels, and contacts** — how to report security issues to an organization.

## Purpose

Track and reference the mechanisms through which security vulnerabilities are reported and coordinated. This includes:

**Disclosure Programs:**
- PSIRT teams (Red Hat Product Security, Cisco PSIRT)
- Bug bounty programs (HackerOne, Bugcrowd-hosted programs)
- Coordinated disclosure policies

**Reporting Channels:**
- security.txt files (RFC 9116)
- Security contact emails
- Vulnerability reporting forms

**Disclosure Policies:**
- Responsible disclosure timelines
- Safe harbor statements
- Scope definitions

## Identifier Format

```
secid:disclosure/<namespace>/<name>[#subpath]

secid:disclosure/redhat.com/psirt                     # Red Hat's PSIRT program
secid:disclosure/redhat.com/security-txt              # Red Hat's security.txt
secid:disclosure/hackerone.com/programs#redhat         # Red Hat's HackerOne bug bounty
secid:disclosure/bugcrowd.com/programs#tesla           # Tesla's Bugcrowd program
secid:disclosure/microsoft.com/msrc                    # Microsoft Security Response Center
secid:disclosure/google.com/vrp                        # Google Vulnerability Reward Program
```

## Why Disclosure Is Separate from Entity and Advisory

| Type | What It Answers | Resolution Target |
|------|----------------|-------------------|
| `entity` | "What is this organization/product?" | Product descriptions, capabilities |
| `advisory` | "What vulnerabilities were published?" | Published vulnerability records |
| `disclosure` | "How do I report a vulnerability?" | Contact info, policies, reporting channels |

The **disclosure** type was split from `entity` because:

1. **Resolution patterns diverge** — Disclosure entries resolve to contact information, policy documents, and reporting forms. Entity entries resolve to product descriptions and capabilities. Different data, different consumers.
2. **Freshness requirements differ** — Contact emails, reporting URLs, and policy descriptions go stale fast. Entity descriptions are relatively stable. Disclosure data needs more frequent verification (tracked via `_checked` / `_updated` metadata).
3. **Consumer workflows differ** — A security researcher finding a vulnerability needs disclosure channels immediately. That's a different workflow from looking up what an organization's products are.

## Weight-Based Channel Ranking

Match nodes use weights to rank channels by preference:

| Weight | Channel Type | Example |
|--------|-------------|---------|
| 100 | Primary contact (official PSIRT) | `secalert@redhat.com` |
| 80 | Bug bounty platform | HackerOne program |
| 60 | security.txt | `/.well-known/security.txt` |
| 40 | General security page | `/security` webpage |
| 20 | Fallback contact | `security@example.com` |

Higher weights indicate the organization's preferred reporting channel. Resolvers should present channels in weight order.

## Namespaces

### Organizations (Direct Programs)

| Namespace | Names | Description |
|-----------|-------|-------------|
| `redhat.com` | `psirt`, `security-txt` | Red Hat Product Security |
| `microsoft.com` | `msrc` | Microsoft Security Response Center |
| `google.com` | `vrp` | Google Vulnerability Reward Program |
| `cisco.com` | `psirt` | Cisco PSIRT |
| `apple.com` | `security-research` | Apple Security Research |

### Bug Bounty Platforms

| Namespace | Names | Description |
|-----------|-------|-------------|
| `hackerone.com` | `programs` | HackerOne-hosted bug bounty programs |
| `bugcrowd.com` | `programs` | Bugcrowd-hosted programs |
| `intigriti.com` | `programs` | Intigriti-hosted programs |

### Standards

| Namespace | Names | Description |
|-----------|-------|-------------|
| `ietf.org` | `security-txt` | RFC 9116 security.txt standard |

## security.txt (RFC 9116)

The `security-txt` name within any namespace refers to that organization's security.txt file. This is the most machine-readable disclosure channel and the easiest to verify programmatically.

```
secid:disclosure/redhat.com/security-txt         # Red Hat's security.txt
secid:disclosure/github.com/security-txt         # GitHub's security.txt
secid:disclosure/cloudflare.com/security-txt     # Cloudflare's security.txt
```

Resolution: `https://<domain>/.well-known/security.txt`

## Relationships

Disclosure entries connect to entities and advisories:

```json
{
  "from": "secid:disclosure/redhat.com/psirt",
  "to": "secid:entity/redhat.com",
  "type": "operated_by",
  "description": "Red Hat's PSIRT is operated by Red Hat"
}
```

```json
{
  "from": "secid:advisory/redhat.com/errata#RHSA-2026:1234",
  "to": "secid:disclosure/redhat.com/psirt",
  "type": "reported_through",
  "description": "Vulnerability reported through Red Hat PSIRT"
}
```

## Notes

- Disclosure data goes stale fast — use `_checked` / `_updated` metadata to track verification dates
- An organization may have multiple disclosure channels (PSIRT, bug bounty, security.txt) — each gets its own name within the namespace
- Bug bounty platforms host programs for many organizations — the platform is the namespace, the organization is in the subpath
