# Proposal: Disclosure Type-Specific Standard Fields

Status: Draft / discussion
Date: 2026-04-05

## Summary

Add standard fields to disclosure registry entries that capture the information security researchers need when reporting vulnerabilities. These fields live at both the namespace level (org-wide defaults) and the match_node level (per-program overrides), with child inheriting from parent.

This establishes a pattern for **type-specific standard fields** that will extend to other types as they mature (capability → audit/remediation fields, methodology → input/output fields, etc.).

## The Problem

When a researcher finds a vulnerability, they need answers to five questions:

1. **Am I legally safe?** — safe harbor statement
2. **How do I report?** — contacts, security.txt (already captured)
3. **Will I get a CVE?** — CNA status, CVE program participation
4. **Is there money?** — bug bounty program(s)
5. **What's the timeline?** — disclosure policy, stated timeline

Today, disclosure entries have `contacts` and `scope` but lack structured data for safe harbor, CVE participation, bug bounties, security.txt, and disclosure policies. The `cve_program_role` field exists in ~513 CNA-sourced entries but is a free-text string, not structured.

## Null vs Absent Convention

Consistent with existing SecID convention:

- **`null`** = "we looked and found nothing" (researched, confirmed absent)
- **absent field** = "not yet researched" (unknown state)
- **object with data** = the thing exists, here are the details

No redundant `"exists": true` booleans. The presence of data means it exists.

## Proposed Fields

### `cve`

CVE program participation. One object per namespace (an org has one relationship with the CVE Program).

```json
"cve": {
  "roles": ["cna"],
  "scope": "All Example Corp products and services",
  "root": "mitre.org",
  "last_assigned": "2026-03-28",
  "url": "https://www.cve.org/PartnerInformation/ListofPartners/partner/example"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `roles` | `string[]` | CVE Program roles. Controlled vocabulary from CVE Program terminology. |
| `scope` | `string` | What products/services the CNA covers (from CVE Program data). |
| `root` | `string` | Domain of the Root CNA this org reports to. |
| `last_assigned` | `string` (date) | Date of most recent CVE assignment. Staleness indicator. |
| `url` | `string` | Link to CVE Partner listing or equivalent. |

**`roles` controlled vocabulary** (from CVE Program — their terminology, not ours):

| Value | Meaning |
|-------|---------|
| `cna` | CVE Numbering Authority — assigns CVEs directly |
| `cna-lr` | CNA of Last Resort — assigns when no other CNA covers it |
| `root` | Root CNA — manages a group of CNAs |
| `tlr` | Top-Level Root |
| `adp` | Authorized Data Publisher |
| `secretariat` | CVE Secretariat |

For non-CNA organizations that cooperate with CVE but don't have a formal role:

| Value | Meaning |
|-------|---------|
| `requests` | Will request CVE from upstream on reporter's behalf |
| `none` | Does not participate in CVE program |

### `safe_harbor`

Legal protection statement for good-faith security research.

```json
"safe_harbor": {
  "url": "https://example.com/security/safe-harbor"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `url` | `string` | Link to the safe harbor or legal safe harbor statement. |

`null` means "researched, no safe harbor statement found." This is a meaningful signal — researchers may choose not to report without safe harbor.

### `bug_bounty`

Bug bounty program(s). **Array** — organizations may run multiple programs on different platforms or for different product lines.

```json
"bug_bounty": [
  {
    "url": "https://hackerone.com/example",
    "paid": true
  },
  {
    "url": "https://bugcrowd.com/example-iot",
    "paid": true
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `url` | `string` | Link to the bug bounty program page. |
| `paid` | `boolean` | Whether the program pays monetary rewards. |

`null` means "researched, no bug bounty program found." An empty array `[]` means the same thing but prefer `null` for consistency.

No `platform` field — the URL tells you the platform, and tracking platform names creates unnecessary maintenance burden.

### `security_txt`

RFC 9116 machine-readable security contact file.

```json
"security_txt": {
  "url": "https://example.com/.well-known/security.txt"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `url` | `string` | URL of the security.txt file. |

### `disclosure_policy`

Vulnerability disclosure policy.

```json
"disclosure_policy": {
  "url": "https://example.com/security/disclosure",
  "stated_timeline": "90 days"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `url` | `string` | Link to the disclosure policy document. |
| `stated_timeline` | `string` | The timeline as stated by the vendor. Free text — vendors use the words inconsistently ("90 days", "90 business days", "negotiable", "we will coordinate"). Quote what they say. |

No `type` vocabulary (coordinated / responsible / full) — the industry uses these terms inconsistently. The URL and stated_timeline are the useful machine-readable data.

## Inheritance: Namespace Level + Match Node Level

These fields can appear at both levels. Large multinationals have org-wide policies with per-product overrides.

**Namespace level** — org-wide defaults:

```json
{
  "namespace": "microsoft.com",
  "type": "disclosure",

  "safe_harbor": {
    "url": "https://www.microsoft.com/en-us/msrc/bounty-safe-harbor"
  },
  "disclosure_policy": {
    "url": "https://www.microsoft.com/en-us/msrc/cvd",
    "stated_timeline": "90 days"
  },

  "match_nodes": [...]
}
```

**Match node level** — per-program overrides:

```json
{
  "match_nodes": [
    {
      "patterns": ["(?i)^msrc$"],
      "description": "Microsoft Security Response Center",
      "bug_bounty": [
        {"url": "https://www.microsoft.com/en-us/msrc/bounty", "paid": true}
      ],
      "cve": {
        "roles": ["cna"],
        "scope": "Microsoft products"
      }
    },
    {
      "patterns": ["(?i)^xbox$"],
      "description": "Xbox Bug Bounty",
      "bug_bounty": [
        {"url": "https://hackerone.com/xbox", "paid": true}
      ]
    }
  ]
}
```

**Inheritance rule:** Match node overrides namespace level for any field present. Absent field at match node level means inherit from namespace. Xbox inherits Microsoft's `safe_harbor` and `disclosure_policy` but has its own `bug_bounty`.

The resolver walks: check match_node first, fall back to namespace level.

## Migration Plan

### Phase 1: Schema

- Add field definitions to REGISTRY-JSON-FORMAT.md
- Document inheritance behavior
- Update disclosure type description (`registry/disclosure.md`)

### Phase 2: Populate CVE data (~513 existing CNA entries)

The existing `cve_program_role` free-text field in `data` objects maps to the new `cve` structured field. Migration is mechanical:

| Existing `cve_program_role` | New `cve.roles` |
|-----------------------------|-----------------|
| `"CNA"` | `["cna"]` |
| `"Root"` | `["root"]` |
| `"Root (reports to MITRE Top-Level Root)"` | `["root"]` |
| `"CNA-LR (reports to Red Hat Root)"` | `["cna-lr"]` |
| `"Root, CNA-LR (reports to CISA ICS Root)"` | `["root", "cna-lr"]` |
| `"Top-Level Root (reports to CVE Board)"` | `["tlr"]` |
| `"ADP (Authorized Data Publisher)"` | `["adp"]` |
| `"Secretariat (reports to CVE Board)"` | `["secretariat"]` |

The `last_assigned` field can be populated from CVE list data (find the most recent CVE assigned by each CNA).

### Phase 3: Populate other fields (new research)

Safe harbor, bug bounty, security.txt, and disclosure policy require new research per namespace. This can be done incrementally — start with the largest/most-reported-to vendors.

`security_txt` is the easiest to automate — fetch `https://{domain}/.well-known/security.txt` for all 486 disclosure namespaces and record whether it exists.

## Future: Type-Specific Fields for Other Types

This proposal establishes the pattern. Other types will accumulate their own standard fields as they mature:

| Type | Potential fields | When |
|------|-----------------|------|
| `capability` | `audit_methods`, `iac_support`, `default_state` | As capability entries grow |
| `methodology` | `output_type`, `input_types` | When data layer ships |
| `advisory` | `severity_source`, `exploit_available` | TBD |
| `entity` | `acquisition_history`, `product_count` | TBD |

Each follows the same pattern: defined in the type's section of REGISTRY-JSON-FORMAT.md, uses null vs absent convention, supports inheritance at namespace + match_node levels.

## Open Questions

1. **Should `cve.last_assigned` be auto-updated?** It could be populated from CVE list data on a schedule. If so, does it need a `_checked` timestamp?

2. **`security_txt` automation** — should we build a script to check all disclosure namespace domains for security.txt? Easy to do, high coverage quickly.

3. **Bug bounty staleness** — URLs to bug bounty programs break when programs close. Should there be a `_checked` date?

4. **Inheritance in the resolver** — does the SecID-Service resolver currently support field inheritance between namespace and match_node levels? If not, this needs implementation work.

5. **Per-field metadata** — the existing `_checked` / `_updated` convention from REGISTRY-JSON-FORMAT.md applies here. Should these new fields use it from the start?

---

*Based on design discussion about CNA tagging, disclosure researcher experience, and type-specific standard fields.*
