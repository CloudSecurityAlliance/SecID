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

`profiles` at a match_node level inherits from the namespace level. **Replace semantics — no deep merge.**

**Inheritance rules:**

| Child `profiles` state | Behavior |
|------------------------|----------|
| Module **absent** | Inherit parent's module as-is |
| Module **present** (object or array) | Child's module **replaces** parent's entirely. No field-level merge, no array append. |
| Module **`null`** | Explicitly overrides parent — means "does not apply here" |

**Why replace, not merge:** Deep merge creates ambiguity. If parent has `cve.roles: ["root", "cna"]` and child has `cve.roles: ["cna"]`, does the child add to or replace the parent's roles? With replace semantics, the answer is always: child's `cve` object is the complete `cve` for that match_node. If you need the parent's data too, copy it into the child. Simple, predictable, no surprises.

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

- MSRC inherits `safe_harbor` and `disclosure_policy` from namespace (absent in its profiles), adds `bug_bounty` and `cve`
- Xbox inherits `safe_harbor` and `disclosure_policy`, has its own `bug_bounty` (replaces, not appends), explicitly sets `cve` to `null` (Xbox doesn't assign CVEs)

**Resolver implementation note:** Inheritance is an optimization, not a prerequisite. Phase 1 can ship profiles without resolver inheritance — the data is still valuable when returned at whatever level it's found. Inheritance support is a separate resolver enhancement (Phase 2). A client that needs the full resolved profile can walk up itself: check match_node profiles, then check namespace profiles for any absent modules.

### Null vs Absent Convention

Consistent with existing SecID convention:

- **`null`** = "we looked and found nothing" (researched, confirmed absent)
- **absent key** = "not yet researched" (unknown state)
- **object/array with data** = the thing exists, here are the details

No redundant `"exists": true` booleans.

### Data Provenance Convention

**This convention applies registry-wide, not just to profiles.** Every piece of data in the registry should be traceable to its source, the process that produced it, when it was verified, and by whom.

**Provenance fields** (prefixed with `_`, consistent with existing `_checked` / `_updated` convention):

| Field | Type | Description |
|-------|------|-------------|
| `_source` | `string` | URL or reference where the raw data was obtained |
| `_process` | `string` | Script, tool, or method used to extract/transform the data. A path like `scripts/generate-cna-disclosure.py` so someone can find and re-run it. |
| `_checked` | `string` (date) | When this data was last verified |
| `_checked_by` | `string` | Who verified it. Controlled vocabulary: |

**`_checked_by` values:**

| Value | Meaning |
|-------|---------|
| `csa/automated` | CSA-maintained script scraped or verified it |
| `csa/manual` | A human at CSA researched and confirmed it |
| `vendor` | The vendor/namespace owner submitted or confirmed it |
| `community` | A community contributor submitted it |

**Why this matters:**

1. **Trust signal** — CNA roles verified against cve.org by an automated scraper are high confidence. A safe harbor URL submitted by an anonymous contributor is lower confidence until someone checks it.
2. **Reproducibility** — `_process` points to the exact script, so anyone can re-run it against `_source` to verify or refresh the data.
3. **Staleness detection** — `_checked` tells you how fresh the data is. A `_checked` date from 2 years ago on a bug bounty URL is a signal to re-verify.
4. **Vendor self-maintenance (future)** — when vendors maintain their own namespace, `_checked_by: "vendor"` means they are the authority on their own data.

**Provenance can appear at any level:** on the whole `profiles` object, on individual profile modules, or on individual fields within a module. Use the most specific level that makes sense:

```json
"profiles": {
  "cve": {
    "roles": ["cna"],
    "scope": "All Example Corp products",
    "cna_short_name": "example",
    "_source": "https://www.cve.org/PartnerInformation/ListofPartners/partner/example",
    "_process": "scripts/generate-cna-disclosure.py",
    "_checked": "2026-04-05",
    "_checked_by": "csa/automated"
  },
  "safe_harbor": {
    "url": "https://example.com/security/safe-harbor",
    "_source": "https://example.com/.well-known/security.txt",
    "_checked": "2026-04-05",
    "_checked_by": "csa/manual"
  }
}
```

**V1 vs V2 pattern:** In V1, profile modules are pointers (URLs) with provenance metadata. In V2, the data layer can cache copies of the referenced content (safe harbor text, disclosure policy text) with change detection. The registry stays lightweight; the data layer handles heavy content. The provenance fields tell you when the pointer was last verified, and when V2 arrives, when the cached copy was last refreshed.

## Disclosure Profile Modules

### `cve`

CVE program participation.

```json
"cve": {
  "roles": ["cna"],
  "cna_short_name": "example",
  "cna_partner_url": "https://www.cve.org/PartnerInformation/ListofPartners/partner/example",
  "scope": "All Example Corp products and services",
  "root": "mitre.org",
  "last_assigned": "2026-03-28"
}
```

| Field | Type | Description |
|-------|------|-------------|
| `roles` | `string[]` | CVE Program roles. Controlled vocabulary from CVE Program terminology. |
| `cna_short_name` | `string` | CNA slug/short name as used on cve.org and in CVE records (e.g., `redhat`, `Google`, `microsoft`). This is the identifier used in CVE JSON as the assigner. |
| `cna_partner_url` | `string` | URL to this org's CVE Partner page on cve.org. |
| `scope` | `string` | What products/services the CNA covers (from CVE Program data). |
| `root` | `string` | Domain of the Root CNA this org reports to. |
| `last_assigned` | `string` (date) | Date of most recent CVE assignment. Staleness indicator. Computed from CVE list data. |

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

**No `none` value.** If an organization does not participate in the CVE program, set `profiles.cve` to `null` (researched, no participation). The `roles` array only contains positive roles — `["cna", "none"]` would be nonsensical. The three states are: `null` (no participation), absent (not yet researched), or object with `roles` array (participates).

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

**This proposal defines only the five disclosure modules listed above.** These are the modules being implemented now:

| Module | Types where it applies | Notes |
|--------|----------------------|-------|
| `cve` | `disclosure`, potentially `advisory` | A CNA's advisory entry may also benefit from CVE program data |
| `safe_harbor` | `disclosure` | Disclosure-specific |
| `bug_bounty` | `disclosure` | Disclosure-specific |
| `security_txt` | `disclosure` | Disclosure-specific |
| `disclosure_policy` | `disclosure` | Disclosure-specific |

**Aspirational (not part of this proposal):** Other types may define their own profile modules in the future (e.g., capability audit/remediation, methodology input/output). Each would require its own proposal with the same level of schema definition. The `profiles` wrapper accommodates this without schema changes, but the modules themselves are not being defined or committed to here. Any future modules must individually pass the registry/data-layer boundary test — some may belong in the data layer rather than the registry.

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
      "cna_short_name": "redhat",
      "cna_partner_url": "https://www.cve.org/PartnerInformation/ListofPartners/partner/redhat",
      "root": "mitre.org",
      "last_assigned": "2026-04-04",
      "_source": "https://www.cve.org/PartnerInformation/ListofPartners/partner/redhat",
      "_process": "scripts/generate-cna-disclosure.py",
      "_checked": "2026-04-05",
      "_checked_by": "csa/automated"
    },
    "safe_harbor": null,
    "bug_bounty": [
      {
        "url": "https://hackerone.com/redhat",
        "paid": true,
        "_checked": "2026-04-05",
        "_checked_by": "csa/manual"
      }
    ],
    "security_txt": {
      "url": "https://www.redhat.com/.well-known/security.txt",
      "_checked": "2026-04-05",
      "_checked_by": "csa/automated"
    },
    "disclosure_policy": {
      "url": "https://access.redhat.com/articles/2939351",
      "stated_timeline": "coordinated disclosure",
      "_source": "https://access.redhat.com/articles/2939351",
      "_checked": "2026-04-05",
      "_checked_by": "csa/manual"
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

The existing `cve_program_role` free-text field in `data` objects maps to the new `profiles.cve` structured module. Migration is mechanical. The parenthetical "(reports to X)" maps to `profiles.cve.root`.

**Complete mapping of all observed values** (from current registry data):

| Existing `cve_program_role` | Count | `profiles.cve.roles` | `profiles.cve.root` |
|-----------------------------|-------|----------------------|----------------------|
| `"CNA"` | 498 | `["cna"]` | (from CNA data) |
| `"Root"` | 6 | `["root"]` | `"mitre.org"` |
| `"Top-Level Root (reports to CVE Board)"` | 2 | `["tlr"]` | — |
| `"Root (reports to MITRE Top-Level Root)"` | 1 | `["root"]` | `"mitre.org"` |
| `"CNA (reports to Red Hat Root)"` | 1 | `["cna"]` | `"redhat.com"` |
| `"CNA-LR (reports to Red Hat Root)"` | 1 | `["cna-lr"]` | `"redhat.com"` |
| `"CNA-LR (CNA of Last Resort, reports to MITRE Top-Level Root)"` | 1 | `["cna-lr"]` | `"mitre.org"` |
| `"Root, CNA-LR (reports to CISA ICS Root)"` | 1 | `["root", "cna-lr"]` | `"cisa.gov"` |
| `"ADP (Authorized Data Publisher)"` | 1 | `["adp"]` | — |
| `"Secretariat (reports to CVE Board)"` | 1 | `["secretariat"]` | — |

**Parsing rule:** Split on comma for multi-role entries. Extract the parenthetical "reports to X" as the `root` value, mapping the org name to its domain. Discard explanatory text in parentheses (e.g., "CNA of Last Resort" is captured by the `cna-lr` role, not duplicated in a note).

The `last_assigned` field can be populated from CVE list data (find the most recent CVE assigned by each CNA).

### Phase 3: Populate other fields (new research)

Safe harbor, bug bounty, security.txt, and disclosure policy require new research per namespace. This can be done incrementally — start with the largest/most-reported-to vendors.

`security_txt` is the easiest to automate — fetch `https://{domain}/.well-known/security.txt` for all 486 disclosure namespaces and record whether it exists.

## Open Questions

1. **Should `cve.last_assigned` be auto-updated?** It could be populated from CVE list data on a schedule. If so, does it need a `_checked` timestamp?

2. **`security_txt` automation** — should we build a script to check all disclosure namespace domains for security.txt? Easy to do, high coverage quickly.

3. **Bug bounty staleness** — URLs to bug bounty programs break when programs close. Should there be a `_checked` date?

4. **Inheritance in the resolver** — the resolver does not currently support profile inheritance. This is decoupled from the schema change: Phase 1 ships profiles without inheritance (data is returned at whatever level it's found; clients can walk up). Phase 2 adds resolver-side inheritance as a separate enhancement.

5. **Per-field metadata** — the existing `_checked` / `_updated` convention from REGISTRY-JSON-FORMAT.md applies here. Should these new fields use it from the start?

6. **CERT/CSIRT status** — considered and deferred. CERT designation is more of an entity characteristic than a disclosure field. A CERT's disclosure entry would use the same profile modules as any other org. If needed later, a `csirt` profile module could be added to the entity type.

---

*Based on design discussion about CNA tagging, disclosure researcher experience, and type-specific standard fields. The `profiles` wrapper establishes a general extension mechanism for all SecID types.*
