# Proposal: Profiles — Type-Specific Standard Fields

Status: Draft / discussion
Date: 2026-04-05
Updated: 2026-04-07

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

**Why replace, not merge:** Deep merge creates ambiguity. If parent has `cve.role: "root"` and child has `cve.role: "cna"`, does the child add to or replace the parent's role? With replace semantics, the answer is always: child's `cve` object is the complete `cve` for that match_node. If you need the parent's data too, copy it into the child. Simple, predictable, no surprises.

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
        "cve": { "role": "cna", "assignerShortName": "microsoft", "assignerOrgId": "f38d906d-7342-40ea-92c1-6c4a2c6478c8", "scope": "Microsoft products" }
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

### Phase 1 API Behavior

**Phase 1:** The resolver always includes namespace-level profiles in every response, even for deep queries. This eliminates ambiguity — the client sees exactly what exists at each level without a second request.

When querying `secid:disclosure/redhat.com/cna`, the response includes:
- The match_node result for `cna` (with its own `profiles` if present)
- The namespace-level `profiles` as `namespace_profiles` on the envelope

```json
{
  "secid_query": "secid:disclosure/redhat.com/cna",
  "status": "found",
  "results": [...],
  "namespace_profiles": {
    "cve": { "role": "cna", "assignerShortName": "redhat", ... },
    "safe_harbor": null,
    "bug_bounty": [{ "url": "https://hackerone.com/redhat", "paid": true }]
  }
}
```

This means "absent at match_node level" is unambiguously "not set here" — the client can see the namespace-level value right in the same response.

**Phase 2:** Resolver adds inheritance — merges namespace-level profiles with match_node-level profiles using replace semantics before returning. This is a backward-compatible enhancement (responses get richer; tolerant JSON consumers will not break, though strict-schema consumers should anticipate new fields).

### Null vs Absent Convention

Consistent with existing SecID convention:

- **`null`** = "we looked and found nothing" (researched, confirmed absent)
- **absent key** = "not yet researched" (unknown state)
- **object/array with data** = the thing exists, here are the details

No redundant `"exists": true` booleans.

### Boundary: `profiles` vs `data`

Profiles and the existing `data` object coexist on the same node. They serve different purposes:

- **`profiles`** — structured modules with defined schemas and controlled vocabulary (cve, safe_harbor, bug_bounty, etc.). Each module has a documented field table. Typed and machine-queryable.
- **`data`** — operational freeform details (contacts, urls, examples, organization_type). Existing field, unchanged by this proposal.

After migration, `cve_program_role` and `scope` move from `data` into `profiles.cve`. `contacts`, `organization_type`, `urls`, and `examples` stay in `data`.

### Field Naming Policy

- **Preserve source names** for fields sourced directly from external data: `assignerShortName`, `assignerOrgId` (from CVE 5.0 JSON `cveMetadata`). These are camelCase because that's what CVE uses.
- **Use snake_case** for SecID-defined fields: `cna_partner_url`, `last_assigned_cve`, `last_assigned_date`, `stated_timeline`, `statement_url`.

This is consistent with SecID's "follow the source" principle — CVE's naming is CVE's naming, we don't normalize it.

### Metadata Convention

Profile modules use the **existing per-field metadata convention** from [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) — `checked`, `updated`, `note` inside objects; `field_checked`, `field_updated`, `field_note` as suffixes for scalar fields.

**Extended provenance fields** (`source`, `process`, `checked_by`) are a useful addition but are a **registry-wide concern, not disclosure-specific**. These will be proposed separately as an extension to REGISTRY-JSON-FORMAT.md's per-field metadata convention. This proposal does not depend on them — the existing `checked`/`updated`/`note` fields are sufficient for V1.

**V1 vs V2 pattern:** In V1, profile modules are pointers (URLs) with timestamps. In V2, the data layer can cache copies of the referenced content (safe harbor text, disclosure policy text) with change detection. The registry stays lightweight; the data layer handles heavy content.

## Disclosure Profile Modules

### `cve`

CVE program participation and posture. Serves two audiences:

- **For CVE Program participants** (CNAs, Roots, etc.): authoritative data from the CVE partner list with `role`, `assignerShortName`, `assignerOrgId`.
- **For everyone else**: what the org has said about how they handle CVE requests — captured as `note` with optional `statement_url`.

Field names use CVE Program terminology (`assignerShortName`, `assignerOrgId`) so the mapping to CVE JSON records is obvious. SecID-defined fields use snake_case.

**CVE Program participant (CNA):**

```json
"cve": {
  "role": "cna",
  "assignerShortName": "redhat",
  "assignerOrgId": "53f830b8-0a3f-465b-8143-3b8a9948e749",
  "cna_partner_url": "https://www.cve.org/PartnerInformation/ListofPartners/partner/redhat",
  "scope": "Red Hat products and open source community",
  "root": {
    "assignerShortName": "mitre",
    "assignerOrgId": "8254265b-2729-46b6-b9e3-3dfca2d5bfca"
  },
  "last_assigned_cve": "CVE-2026-3184",
  "last_assigned_date": "2026-04-03"
}
```

**Non-participant that cooperates:**

```json
"cve": {
  "note": "Will request CVE from MITRE on reporter's behalf",
  "statement_url": "https://example.com/security/cve-policy"
}
```

**Non-participant that doesn't engage:**

```json
"cve": {
  "note": "Vendor has publicly stated they do not participate in CVE",
  "statement_url": "https://example.com/blog/no-cve"
}
```

**Not researched:** `cve` field absent.
**Researched, nothing found:** `"cve": null`

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | `string` | Only for CVE Program participants | CVE Program role. Protected vocabulary — only present for formal program participants. When present, `assignerShortName` and `assignerOrgId` are required. |
| `assignerShortName` | `string` | When `role` is present | CNA short name as used in CVE JSON records (`cveMetadata.assignerShortName`). **Preserve source case.** |
| `assignerOrgId` | `string` (UUID) | When `role` is present | CVE Program org UUID (`cveMetadata.assignerOrgId`). Stable — survives renames and rebrands. |
| `cna_partner_url` | `string` | No | URL to this org's CVE Partner page on cve.org. |
| `scope` | `string` | No | What products/services the CNA covers (from CVE Program data). |
| `root` | `object` | No | The Root CNA this org reports to. |
| `root.assignerShortName` | `string` | When `root` present | Root CNA's short name. |
| `root.assignerOrgId` | `string` (UUID) | When `root` present | Root CNA's organization UUID. |
| `last_assigned_cve` | `string` | No | Most recent CVE ID assigned by this CNA. Staleness indicator. |
| `last_assigned_date` | `string` (date) | No | Date of that CVE's publication. |
| `note` | `string` | No | Free text — the org's stated position on CVE participation. Especially useful for non-participants. |
| `statement_url` | `string` | No | URL to the org's public statement about their CVE posture. |

#### `role` Vocabulary

Protected terms from the CVE Program — their terminology, not ours:

| Value | Meaning |
|-------|---------|
| `cna` | CVE Numbering Authority — assigns CVEs directly |
| `cna-lr` | CNA of Last Resort — assigns when no other CNA covers it |
| `root` | Root CNA — manages a group of CNAs |
| `tlr` | Top-Level Root |
| `adp` | Authorized Data Publisher |
| `secretariat` | CVE Secretariat |

**`role` is present only for CVE Program participants.** If an org is not in the program, `role` is absent. The org's CVE posture (cooperates, ignores, hostile) is captured in `note` as free text — no informal vocabulary mixed into the protected `role` field.

#### Data Source

`assignerShortName` and `assignerOrgId` come from CVE JSON records (`cveMetadata` fields). Pre-extracted data with 457 CNAs (org IDs, last CVE, dates) is available from the [cvelistV5 repository](https://github.com/CVEProject/cvelistV5). The extraction script should be added to `SecID/scripts/` for reproducibility.

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

`profiles.security_txt` is the canonical location for this data. One existing entry uses `urls[].type="security_txt"` as a general URL entry — that can coexist, but `profiles.security_txt` is the structured, queryable representation.

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

## Complete Example

A fully populated disclosure entry for a CVE Program participant:

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
      "role": "cna",
      "assignerShortName": "redhat",
      "assignerOrgId": "53f830b8-0a3f-465b-8143-3b8a9948e749",
      "cna_partner_url": "https://www.cve.org/PartnerInformation/ListofPartners/partner/redhat",
      "scope": "Red Hat products and the open source community",
      "root": {
        "assignerShortName": "mitre",
        "assignerOrgId": "8254265b-2729-46b6-b9e3-3dfca2d5bfca"
      },
      "last_assigned_cve": "CVE-2026-3184",
      "last_assigned_date": "2026-04-03",
      "checked": "2026-04-05",
      "note": "Red Hat is both a Root CNA and a CNA. Root scope covers open source community."
    },
    "safe_harbor": null,
    "bug_bounty": [
      {
        "url": "https://hackerone.com/redhat",
        "paid": true,
        "checked": "2026-04-05"
      }
    ],
    "security_txt": {
      "url": "https://www.redhat.com/.well-known/security.txt",
      "checked": "2026-04-05"
    },
    "disclosure_policy": {
      "url": "https://access.redhat.com/articles/2939351",
      "stated_timeline": "coordinated disclosure",
      "checked": "2026-04-05"
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

A disclosure entry for a non-CNA with a stated CVE position:

```json
{
  "schema_version": "1.0",
  "namespace": "smallvendor.com",
  "type": "disclosure",
  "status": "published",
  "official_name": "Small Vendor Inc.",

  "profiles": {
    "cve": {
      "note": "Will request CVE from MITRE on reporter's behalf. Typical turnaround 2-4 weeks.",
      "statement_url": "https://smallvendor.com/security/cve-policy"
    },
    "safe_harbor": {
      "url": "https://smallvendor.com/security/safe-harbor"
    },
    "bug_bounty": null,
    "security_txt": {
      "url": "https://smallvendor.com/.well-known/security.txt"
    }
  },

  "match_nodes": [...]
}
```

## Migration Plan

### Phase 1: Schema (hard dependency — must complete before any data migration)

- **Update JSON Schema** (`schemas/registry-namespace.schema.json`): add `profiles` to MatchNode properties. Top-level already allows additional properties (`additionalProperties: true` at line 113). MatchNode has `additionalProperties: false` (line 185) — this is the only hard blocker.
- Add `profiles` wrapper definition to REGISTRY-JSON-FORMAT.md
- Define initial disclosure modules (cve, safe_harbor, bug_bounty, security_txt, disclosure_policy)
- Document Phase 1 API behavior (namespace_profiles in every response)
- Update disclosure type description (`registry/disclosure.md`)

### Phase 2: Populate CVE data (~513 existing CNA entries)

The existing `cve_program_role` free-text field in `data` objects maps to the new `profiles.cve` structured module. Migration is mechanical. The parenthetical "(reports to X)" maps to `profiles.cve.root`.

**Complete mapping of all observed values** (from current registry data):

| Existing `cve_program_role` | Count | `profiles.cve.role` | `profiles.cve.root.assignerShortName` |
|-----------------------------|-------|---------------------|---------------------------------------|
| `"CNA"` | 498 | `"cna"` | (from CNA partner data) |
| `"Root"` | 6 | `"root"` | `"mitre"` |
| `"Top-Level Root (reports to CVE Board)"` | 2 | `"tlr"` | — |
| `"Root (reports to MITRE Top-Level Root)"` | 1 | `"root"` | `"mitre"` |
| `"CNA (reports to Red Hat Root)"` | 1 | `"cna"` | `"redhat"` |
| `"CNA-LR (reports to Red Hat Root)"` | 1 | `"cna-lr"` | `"redhat"` |
| `"CNA-LR (CNA of Last Resort, reports to MITRE Top-Level Root)"` | 1 | `"cna-lr"` | `"mitre"` |
| `"Root, CNA-LR (reports to CISA ICS Root)"` | 1 | `"root"` | `"icscert"` |
| `"ADP (Authorized Data Publisher)"` | 1 | `"adp"` | — |
| `"Secretariat (reports to CVE Board)"` | 1 | `"secretariat"` | — |

**Note on multi-role orgs:** The "Root, CNA-LR" entry has two roles. Since `role` is now a single string, use the primary role (`"root"`) at the namespace level, with additional roles at the match_node level via separate match_nodes for each role (which is how the current entries already work — Red Hat has separate match_nodes for its Root, CNA-LR, and CNA roles).

**Parsing rules:**
- Use the primary role for the namespace-level `profiles.cve.role`
- Extract the parenthetical "reports to X" → `root.assignerShortName`, mapping org name to CVE partner slug
- Look up `assignerOrgId` and `root.assignerOrgId` from [cvelistV5](https://github.com/CVEProject/cvelistV5) extracted data (457 CNAs with UUIDs). Extraction script should be added to `SecID/scripts/` for reproducibility.
- Extract `last_assigned_cve` and `last_assigned_date` from the same data

**After migration, remove from `data`:** `cve_program_role`, `scope` (now in `profiles.cve`). **Leave in `data`:** `contacts`, `organization_type`, `urls`, `examples`.

### Phase 3: Populate other fields (new research)

Safe harbor, bug bounty, security.txt, and disclosure policy require new research per namespace. This can be done incrementally — start with the largest/most-reported-to vendors.

`security_txt` is the easiest to automate — fetch `https://{domain}/.well-known/security.txt` for all 486 disclosure namespaces and record whether it exists.

## Open Questions

1. **Should `last_assigned_cve` / `last_assigned_date` be auto-updated?** The data comes from the CVE list and could be refreshed on a schedule. A `checked` timestamp on the `cve` module would indicate when it was last refreshed.

2. **`security_txt` automation** — should we build a script to check all disclosure namespace domains for security.txt? Easy to do, high coverage quickly.

3. **Bug bounty staleness** — URLs to bug bounty programs break when programs close. Should there be a `checked` date? (Probably yes — added to the examples.)

4. **Multi-scope orgs** — Red Hat has three CNA roles (Root, CNA-LR, CNA), each with a different scope. The namespace-level `profiles.cve` carries the primary role. Match_node-level `profiles.cve` overrides with role-specific scope via replace semantics (which is how the existing entries are already structured).

5. **MITRE has two `assignerOrgId` values** — `50d0f415-c707-4733-9afc-8f6c0e9b3f82` (older, last used 2022) and `8254265b-2729-46b6-b9e3-3dfca2d5bfca` (current). The migration script should use the most recently active UUID.

6. **CERT/CSIRT status** — considered and deferred. CERT designation is more of an entity characteristic than a disclosure field. A CERT's disclosure entry would use the same profile modules as any other org. If needed later, a `csirt` profile module could be added to the entity type.

7. **Formal JSON Schema for modules** — field tables are documented here. Formal JSON Schema constraints (for roles vocabulary, UUID format, date format) will be defined when we implement and discover what validation is needed in practice. Premature schema rigidity risks not matching real-world data patterns.

## Resolved Issues

Issues raised by review feedback and resolved in this revision:

| Issue | Resolution |
|-------|-----------|
| Schema dependency misstated (top-level already open) | Fixed — only MatchNode `additionalProperties: false` is the blocker |
| security_txt migration note described non-existent data | Removed — no scalar `security_txt` fields exist in current disclosure entries |
| Phase 1 inheritance ambiguity | Fixed — Phase 1 includes `namespace_profiles` in every response |
| Mixed camelCase/snake_case naming | Codified — CVE-sourced names preserve CVE casing, SecID-defined use snake_case |
| `requests` mixed into CVE Program roles | Fixed — `role` is strictly CVE Program vocabulary; non-participant posture goes in `note` |
| Local file path not reproducible | Fixed — references cvelistV5 GitHub repo, extraction script goes in `scripts/` |
| Backward compat claim too broad | Added caveat — tolerant consumers OK, strict-schema consumers should anticipate new fields |

---

*Based on design discussion about CNA tagging, disclosure researcher experience, and type-specific standard fields. The `profiles` wrapper establishes a general extension mechanism for all SecID types.*
