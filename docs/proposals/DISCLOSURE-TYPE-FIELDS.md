# Proposal: Profiles — Type-Specific Standard Fields

Status: Draft / discussion
Date: 2026-04-05

## Summary

Add a `profiles` object to registry entries that holds structured, type-specific data modules. Each module has a defined schema, can appear at both the namespace level and the match_node level, and inherits from parent to child. The `profiles` wrapper provides a clean extension point for future modules without polluting the top-level namespace.

Initial modules for the `disclosure` type: `cve`, `safe_harbor`, `bug_bounty`, `security_txt`, `disclosure_policy`.

## The Problem

When a researcher finds a vulnerability, they need answers to five questions:

1. **Am I legally safe?** — safe harbor statement
2. **How do I report?** — contacts, security.txt (already captured)
3. **Will I get a CVE?** — CNA status, CVE program participation
4. **Is there money?** — bug bounty program(s)
5. **What's the timeline?** — disclosure policy, stated timeline

Today, disclosure entries have `contacts` and `scope` but lack structured data for safe harbor, CVE participation, bug bounties, security.txt, and disclosure policies. The `cve_program_role` field exists in ~513 CNA-sourced entries but is a free-text string, not structured.

## Design: The `profiles` Wrapper

`profiles` is a top-level object on registry entries (alongside `match_nodes`, `urls`, etc.) that contains named data modules. The same `profiles` key appears at both the namespace level and inside match_nodes.

```json
{
  "namespace": "example.com",
  "type": "disclosure",
  "status": "published",
  "official_name": "Example Corp",
  "urls": [...],

  "profiles": {
    "cve": { ... },
    "safe_harbor": { ... },
    "bug_bounty": [ ... ],
    "security_txt": { ... },
    "disclosure_policy": { ... }
  },

  "match_nodes": [
    {
      "patterns": ["(?i)^psirt$"],
      "description": "Example Corp PSIRT",
      "profiles": {
        "bug_bounty": [{ "url": "https://hackerone.com/example", "paid": true }]
      }
    }
  ]
}
```

**Why a wrapper object:**

- Clean extension point — new modules are added inside `profiles`, not as new top-level fields
- Consistent key at every level (`profiles` at namespace, `profiles` at match_node, `profiles` at children)
- Easy to enumerate — "what profiles does this entry have?" is `Object.keys(entry.profiles)`
- Separates identity/resolution fields (`namespace`, `type`, `urls`, `match_nodes`) from descriptive profiles
- Room to grow — future modules for any type go here

### Inheritance

`profiles` at a match_node level inherits from the namespace level. Child overrides parent per-module.

```json
{
  "namespace": "microsoft.com",
  "type": "disclosure",

  "profiles": {
    "safe_harbor": { "url": "https://www.microsoft.com/en-us/msrc/bounty-safe-harbor" },
    "disclosure_policy": { "url": "https://www.microsoft.com/en-us/msrc/cvd", "stated_timeline": "90 days" }
  },

  "match_nodes": [
    {
      "patterns": ["(?i)^msrc$"],
      "description": "Microsoft Security Response Center",
      "profiles": {
        "bug_bounty": [{ "url": "https://www.microsoft.com/en-us/msrc/bounty", "paid": true }],
        "cve": { "roles": ["cna"], "scope": "Microsoft products" }
      }
    },
    {
      "patterns": ["(?i)^xbox$"],
      "description": "Xbox Bug Bounty",
      "profiles": {
        "bug_bounty": [{ "url": "https://hackerone.com/xbox", "paid": true }],
        "cve": null
      }
    }
  ]
}
```

- MSRC inherits `safe_harbor` and `disclosure_policy` from the namespace, adds `bug_bounty` and `cve`
- Xbox inherits `safe_harbor` and `disclosure_policy`, adds its own `bug_bounty`, explicitly sets `cve` to `null` (Xbox doesn't assign CVEs)
- Resolver walks: merge namespace-level profiles with match_node-level profiles, child overrides parent

### Null vs Absent Convention

Consistent with existing SecID convention:

- **`null`** = "we looked and found nothing" (researched, confirmed absent)
- **absent key** = "not yet researched" (unknown state)
- **object/array with data** = the thing exists, here are the details

No redundant `"exists": true` booleans.

## Disclosure Profile Modules

### `cve`

CVE program participation.

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

`null` means "researched, no bug bounty program found."

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

## Cross-Type Modules

The `profiles` wrapper is not limited to disclosure. Modules can be reused across types where they make sense, and each type can define its own modules.

| Module | Types where it applies | Notes |
|--------|----------------------|-------|
| `cve` | `disclosure`, `advisory` | A CNA's advisory entry also benefits from CVE program data |
| `safe_harbor` | `disclosure` | Disclosure-specific |
| `bug_bounty` | `disclosure` | Disclosure-specific |
| `security_txt` | `disclosure` | Disclosure-specific |
| `disclosure_policy` | `disclosure` | Disclosure-specific |
| `audit` | `capability` (future) | Audit commands, expected values |
| `remediation` | `capability` (future) | CLI/API/IaC remediation commands |
| `output_type` | `methodology` (future) | What the methodology produces |

New modules are added to the schema documentation as types mature. The `profiles` wrapper doesn't need to change — just the set of defined modules grows.

## Complete Example

A fully populated disclosure entry:

```json
{
  "schema_version": "1.0",
  "namespace": "redhat.com",
  "type": "disclosure",
  "status": "published",
  "official_name": "Red Hat, Inc.",
  "urls": [
    {"type": "website", "url": "https://www.redhat.com/"},
    {"type": "security", "url": "https://access.redhat.com/security/"}
  ],

  "profiles": {
    "cve": {
      "roles": ["root", "cna"],
      "scope": "Red Hat products and the open source community",
      "root": "mitre.org",
      "last_assigned": "2026-04-04",
      "url": "https://www.cve.org/PartnerInformation/ListofPartners/partner/Red%20Hat"
    },
    "safe_harbor": null,
    "bug_bounty": [
      {"url": "https://hackerone.com/redhat", "paid": true}
    ],
    "security_txt": {
      "url": "https://www.redhat.com/.well-known/security.txt"
    },
    "disclosure_policy": {
      "url": "https://access.redhat.com/articles/2939351",
      "stated_timeline": "coordinated disclosure"
    }
  },

  "match_nodes": [
    {
      "patterns": ["(?i)^cna$"],
      "description": "Red Hat Product Security CVE assignment",
      "data": {
        "contacts": [
          {"type": "email", "value": "secalert@redhat.com"}
        ]
      }
    }
  ]
}
```

## Migration Plan

### Phase 1: Schema

- Add `profiles` wrapper definition to REGISTRY-JSON-FORMAT.md
- Define initial disclosure modules (cve, safe_harbor, bug_bounty, security_txt, disclosure_policy)
- Document inheritance behavior
- Update disclosure type description (`registry/disclosure.md`)

### Phase 2: Populate CVE data (~513 existing CNA entries)

The existing `cve_program_role` free-text field in `data` objects maps to the new `profiles.cve` structured module. Migration is mechanical:

| Existing `cve_program_role` | New `profiles.cve.roles` |
|-----------------------------|--------------------------|
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

## Open Questions

1. **Should `cve.last_assigned` be auto-updated?** It could be populated from CVE list data on a schedule. If so, does it need a `_checked` timestamp?

2. **`security_txt` automation** — should we build a script to check all disclosure namespace domains for security.txt? Easy to do, high coverage quickly.

3. **Bug bounty staleness** — URLs to bug bounty programs break when programs close. Should there be a `_checked` date?

4. **Inheritance in the resolver** — does the SecID-Service resolver currently support field inheritance between namespace and match_node levels? If not, this needs implementation work.

5. **Per-field metadata** — the existing `_checked` / `_updated` convention from REGISTRY-JSON-FORMAT.md applies here. Should these new fields use it from the start?

6. **CERT/CSIRT status** — considered and deferred. CERT designation is more of an entity characteristic than a disclosure field. A CERT's disclosure entry would use the same profile modules as any other org. If needed later, a `csirt` profile module could be added to the entity type.

---

*Based on design discussion about CNA tagging, disclosure researcher experience, and type-specific standard fields. The `profiles` wrapper establishes a general extension mechanism for all SecID types.*
