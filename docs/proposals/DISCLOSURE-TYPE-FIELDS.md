# Proposal: Disclosure Type-Specific Standard Fields

Status: Draft / discussion
Date: 2026-04-05
Updated: 2026-04-08

## Summary

Add structured fields to disclosure registry entries' `data` objects that capture the information security researchers need when reporting vulnerabilities. Five new fields: `cve`, `safe_harbor`, `bug_bounty`, `security_txt`, `disclosure_policy`.

These fields are nested objects/arrays inside the existing `data` object — no new wrapper, no schema changes required. Available in responses once populated in registry data.

## The Problem

When a researcher finds a vulnerability, they need answers to five questions:

1. **Am I legally safe?** — safe harbor statement
2. **How do I report?** — contacts, security.txt (already captured)
3. **Will I get a CVE?** — CNA status, CVE program participation
4. **Is there money?** — bug bounty program(s)
5. **What's the timeline?** — disclosure policy, stated timeline

Today, disclosure entries have `contacts` and `scope` but lack structured data for safe harbor, CVE participation, bug bounties, security.txt, and disclosure policies. The `cve_program_role` field exists in ~513 CNA-sourced entries but is a free-text string, not structured.

## Design: Structured Fields Inside `data`

The five new fields are nested objects inside the existing `data` object. The `data` object already allows arbitrary keys (`additionalProperties: true` in the JSON schema), so **no schema changes are required** to add these fields. This is purely a data population and documentation task.

```json
"data": {
  "contacts": [{"type": "email", "value": "security@example.com"}],
  "organization_type": "Vendor",

  "cve": { ... },
  "safe_harbor": { ... },
  "bug_bounty": [ ... ],
  "security_txt": { ... },
  "disclosure_policy": { ... }
}
```

Existing fields (`contacts`, `organization_type`, `urls`, `examples`) are unchanged. The new fields sit alongside them as structured nested objects.

### Response Behavior and Schema Philosophy

**The resolver doesn't change.** It returns `data` at whatever level matched, exactly as it does today. The new structured fields are inside `data`. Clients see them. No special envelope, no changes to the CSA-hosted API.

**Data that uses a documented field name should follow its specification.** The five fields defined in this proposal have documented types, expected fields, and vocabulary constraints (e.g., `cve.role` values). Data in these fields should follow the specification in this proposal. Formal JSON Schema enforcement is deferred until implementation. But `data` remains open — anyone can add fields beyond the documented ones, and the resolver returns everything.

**Client expectations:**
- **AI clients (MCP, agents):** SHOULD handle all fields, including undocumented ones. This is the primary use case — SecID is AI-first.
- **Human clients (website):** Display everything, structured fields get rich rendering.
- **Traditional API clients:** If a client can only handle documented fields, that's a client-side filtering concern. Self-hosted servers (SecID-Server-API) may offer a strict filtering option (implementation details TBD in that repo). **The CSA-hosted service does not filter — it always returns everything.**

The principle is the same as HTTP headers: fields can be added freely, schema-defined fields have guaranteed structure, clients handle what they can.

### Reserved Field Names

To prevent collisions between standardized fields and ad-hoc additions, these field names inside `data` are reserved for the schemas defined in this proposal:

`cve`, `safe_harbor`, `bug_bounty`, `security_txt`, `disclosure_policy`

Other types may reserve their own field names in future proposals. The reserved list is documented in REGISTRY-JSON-FORMAT.md. Contributors adding ad-hoc data fields to `data` should avoid these names (and check the reserved list before choosing a name).

### Null vs Absent Convention

Consistent with existing SecID convention:

- **`null`** = "we looked and found nothing" (researched, confirmed absent)
- **absent key** = "not yet researched" (unknown state)
- **object/array with data** = the thing exists, here are the details

No redundant `"exists": true` booleans.

### Field Naming Policy

- **Preserve source names** for fields sourced directly from external data: `assignerShortName`, `assignerOrgId` (from CVE 5.0 JSON `cveMetadata`). These are camelCase because that's what CVE uses.
- **Use snake_case** for SecID-defined fields: `cna_partner_url`, `last_assigned_cve`, `last_assigned_date`, `stated_timeline`, `statement_url`.

### Metadata Convention

The new fields use the **existing per-field metadata convention** from [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) — `checked`, `updated`, `note` inside objects.

**Extended provenance fields** (`source`, `process`, `checked_by`) are a registry-wide concern and will be proposed separately.

**V1 vs V2:** In V1, fields are pointers (URLs) with timestamps. In V2, the data layer can cache copies of the referenced content (safe harbor text, disclosure policy text) with change detection.

## New Fields

### `cve`

CVE program participation and posture. Serves two audiences:

- **For CVE Program participants** (CNAs, Roots, etc.): authoritative data from the CVE partner list with `role`, `assignerShortName`, `assignerOrgId`.
- **For everyone else**: what the org has said about how they handle CVE requests — captured as `posture` with optional `statement_url`.

Field names use CVE Program terminology (`assignerShortName`, `assignerOrgId`) so the mapping to CVE JSON records is obvious. SecID-defined fields use snake_case.

**CVE Program participant (CNA):**

```json
"cve": {
  "role": ["cna"],
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
  "posture": "Will request CVE from MITRE on reporter's behalf",
  "statement_url": "https://example.com/security/cve-policy"
}
```

**Non-participant that doesn't engage:**

```json
"cve": {
  "posture": "Vendor has publicly stated they do not participate in CVE",
  "statement_url": "https://example.com/blog/no-cve"
}
```

**Not researched:** `cve` field absent.
**Researched, nothing found:** `"cve": null`

#### Fields

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `role` | `string[]` | Only for CVE Program participants | CVE Program role(s). Protected vocabulary — only present for formal program participants. Array because some orgs hold multiple roles (e.g., Root + CNA-LR). When present, `assignerShortName` is expected (entries where it could not be resolved are flagged for manual follow-up). |
| `assignerShortName` | `string` | Expected when `role` is present | CNA short name as used in CVE JSON records (`cveMetadata.assignerShortName`). **Preserve source case.** May be absent if the CNA slug could not be resolved during migration — these entries are logged as warnings. |
| `assignerOrgId` | `string` (UUID) | No (strongly recommended when `role` present) | CVE Program org UUID (`cveMetadata.assignerOrgId`). Stable — survives renames and rebrands. Absent means "not yet looked up." |
| `cna_partner_url` | `string` | No | URL to this org's CVE Partner page on cve.org. |
| `scope` | `string` | No | What products/services the CNA covers (from CVE Program data). |
| `root` | `object` | No | The Root CNA this org reports to. |
| `root.assignerShortName` | `string` | When `root` present | Root CNA's short name. |
| `root.assignerOrgId` | `string` (UUID) | When `root` present | Root CNA's organization UUID. |
| `last_assigned_cve` | `string` | No | Most recent CVE ID assigned by this CNA. Staleness indicator. |
| `last_assigned_date` | `string` (date) | No | Date of that CVE's publication. |
| `posture` | `string` | No | Free text — the org's stated position on CVE participation. Especially useful for non-participants. Separate from the metadata `note` field (which is for verification notes). |
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

**`role` is present only for CVE Program participants.** If an org is not in the program, `role` is absent. The org's CVE posture (cooperates, ignores, hostile) is captured in `posture` as free text — no informal vocabulary mixed into the protected `role` field.

`role` is an array because some organizations hold multiple formal roles simultaneously (e.g., `["cna-lr", "root"]`). This avoids lossy single-role selection.

**Normalization:** Values must be unique, lowercase, and sorted alphabetically. This ensures deterministic diffs and downstream matching.

**`role` and `posture` can coexist.** A CNA might have `role: ["cna"]` and `posture: "We only assign CVEs for our own products. For third-party components, contact MITRE directly."` The role says what they are in the program; posture adds operational context. However, `posture` is most useful when `role` is absent (non-participants).

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
    "url": "https://bugcrowd.com/example-iot"
  }
]
```

| Field | Type | Description |
|-------|------|-------------|
| `url` | `string` | Link to the bug bounty program page. |
| `paid` | `boolean` (optional) | Whether the program pays monetary rewards. `true` = pays bounties. `false` = VDP, no payment. Absent = unknown. |

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

## Cross-Type Applicability

**This proposal defines only the five disclosure fields listed above.** Other types may add their own structured fields to `data` in the future (e.g., capability audit/remediation, methodology input/output). Each would require its own proposal with its own reserved field names.

## Complete Examples

### CNA with full data

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

  "match_nodes": [
    {
      "patterns": ["(?i)^cna$"],
      "description": "Red Hat Product Security CVE assignment",
      "data": {
        "contacts": [
          {"type": "email", "value": "secalert@redhat.com"}
        ],
        "organization_type": "Vendor, Open Source",

        "cve": {
          "role": ["cna", "root"],
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
      }
    }
  ]
}
```

### Non-CNA with stated CVE position

```json
{
  "schema_version": "1.0",
  "namespace": "smallvendor.com",
  "type": "disclosure",
  "status": "published",
  "official_name": "Small Vendor Inc.",

  "match_nodes": [
    {
      "patterns": ["(?i)^psirt$"],
      "description": "Small Vendor PSIRT",
      "data": {
        "contacts": [
          {"type": "email", "value": "security@smallvendor.com"}
        ],

        "cve": {
          "posture": "Will request CVE from MITRE on reporter's behalf. Typical turnaround 2-4 weeks.",
          "statement_url": "https://smallvendor.com/security/cve-policy"
        },
        "safe_harbor": {
          "url": "https://smallvendor.com/security/safe-harbor"
        },
        "bug_bounty": null,
        "security_txt": {
          "url": "https://smallvendor.com/.well-known/security.txt"
        }
      }
    }
  ]
}
```

## Migration Plan

### Phase 1: Documentation

No schema changes are required — `data` already allows arbitrary keys. This phase is documentation only:

- Add field definitions to REGISTRY-JSON-FORMAT.md
- Add reserved field names list (`cve`, `safe_harbor`, `bug_bounty`, `security_txt`, `disclosure_policy`)
- Update disclosure type description (`registry/disclosure.md`)
- Document schema philosophy (schema-defined fields must conform, open extension allowed) in API-RESPONSE-FORMAT.md

### Phase 2: Populate CVE data (~513 existing CNA entries)

The existing `cve_program_role` free-text field in `data` maps to the new structured `cve` object. Migration is mechanical.

**Complete mapping of all observed values** (from current registry data):

| Existing `cve_program_role` | Count | `cve.role` | `cve.root.assignerShortName` |
|-----------------------------|-------|------------|------------------------------|
| `"CNA"` | 498 | `["cna"]` | (from CNA partner data) |
| `"Root"` | 6 | `["root"]` | `"mitre"` |
| `"Top-Level Root (reports to CVE Board)"` | 2 | `["tlr"]` | — |
| `"Root (reports to MITRE Top-Level Root)"` | 1 | `["root"]` | `"mitre"` |
| `"CNA (reports to Red Hat Root)"` | 1 | `["cna"]` | `"redhat"` |
| `"CNA-LR (reports to Red Hat Root)"` | 1 | `["cna-lr"]` | `"redhat"` |
| `"CNA-LR (CNA of Last Resort, reports to MITRE Top-Level Root)"` | 1 | `["cna-lr"]` | `"mitre"` |
| `"Root, CNA-LR (reports to CISA ICS Root)"` | 1 | `["cna-lr", "root"]` | `"icscert"` |
| `"ADP (Authorized Data Publisher)"` | 1 | `["adp"]` | — |
| `"Secretariat (reports to CVE Board)"` | 1 | `["secretariat"]` | — |

**Note on multi-role orgs:** `role` is an array, so multi-role entries like "Root, CNA-LR" map directly to `["cna-lr", "root"]` (alphabetically sorted) — no information loss.

**Parsing rules:**
- For multi-role entries, split on comma **only at the top level** — commas appear inside parenthetical explanatory text. The `partner-details.json` `Program Role` field is already an array, so prefer using that structured source over string splitting.
- Extract the parenthetical "reports to X" → `root.assignerShortName`, mapping org name to CVE partner slug
- Look up `assignerOrgId` and `root.assignerOrgId` from [cvelistV5](https://github.com/CVEProject/cvelistV5) extracted data (457 CNAs with UUIDs). Extraction script should be added to `SecID/scripts/` for reproducibility.
- Extract `last_assigned_cve` and `last_assigned_date` from the same data

**Migration should emit a warning list** for entries where `role` is present but `assignerOrgId` could not be found — these need manual follow-up.

**After migration, remove from `data`:** `cve_program_role` (replaced by `cve` object). **Move `scope` into `cve.scope`:** All existing `scope` fields in CNA-sourced entries are CNA scope (they were all generated by `scripts/generate-cna-disclosure.py` from CVE partner data). This is deterministic — every entry with `cve_program_role` has its `scope` from the CVE partner list. **Leave in `data`:** `contacts`, `organization_type`, `urls`, `examples`.

### Phase 3: Populate other fields (new research)

Safe harbor, bug bounty, security.txt, and disclosure policy require new research per namespace. This can be done incrementally — start with the largest/most-reported-to vendors.

`security_txt` is the easiest to automate — fetch `https://{domain}/.well-known/security.txt` for all 486 disclosure namespaces and record whether it exists.

## Implementation Status

### Phase 1: Documentation — not started

Field definitions need to be added to REGISTRY-JSON-FORMAT.md. Reserved field names list needs documenting.

### Phase 2: CVE data migration — DONE (2026-04-08)

**Script:** `scripts/migrate-disclosure-cve-fields.py`

**Data sources:**
- `working-data/cna/partner-details.json` — slug mapping and partner metadata
- `seed/cve-cna-partners-raw.json` — slug extraction from CVE partner URLs
- `~/GitHub/cveproject/cvelistV5/latest_cve_per_cna.csv` — assignerOrgId, last CVE, dates (457 CNAs)

**Results:**
- 485 files modified, 513 match_nodes migrated
- 0 JSON parse errors
- `cve_program_role` and `scope` removed from all `data` objects
- Structured `cve` object added with: `role` (array), `assignerShortName`, `assignerOrgId`, `cna_partner_url`, `scope`, `root` reference, `last_assigned_cve`, `last_assigned_date`
- 22 nodes with `role` but no resolved CNA slug (manual follow-up needed)
- Live resolver updated — structured CVE data serving at secid.cloudsecurityalliance.org

**Bug fix (2026-04-08):** Initial migration mapped all nodes in a namespace to the same CNA slug. For multi-CNA namespaces (Google with 6 CNAs, Broadcom with 4, Cisco with 2, etc.) this produced incorrect `assignerShortName` and `assignerOrgId` on most nodes. Fixed with per-node slug resolution using a reverse map from the generate script's `make_node_name()` logic, plus namespace-specific overrides for generic node names.

**Commits:**
- `b757b1d` — Fixed migration script (per-node CNA slug resolution)
- `a8e3603` — Re-migrated data with correct per-node slugs
- `ac1eb9f` — Fixed Thales slug (THA-PSIRT), relaxed assignerShortName to "expected"
- `99db3c4` — Fixed 2 assignerShortName case mismatches (hillstone, netgear)

### Phase 3: Other fields — not started

| Field | Approach | Effort |
|-------|----------|--------|
| `security_txt` | Automate — fetch `/.well-known/security.txt` for all 486 domains | Low — script |
| `safe_harbor` | Manual research per vendor, starting with top 20 | Medium |
| `bug_bounty` | Manual research per vendor, starting with top 20 | Medium |
| `disclosure_policy` | Manual research per vendor, starting with top 20 | Medium |

## Open Questions

1. **Should `last_assigned_cve` / `last_assigned_date` be auto-updated?** The data comes from the CVE list and could be refreshed on a schedule. A `checked` timestamp on the `cve` object would indicate when it was last refreshed.

2. **`security_txt` automation** — should we build a script to check all disclosure namespace domains for security.txt? Easy to do, high coverage quickly.

3. **Bug bounty staleness** — URLs to bug bounty programs break when programs close. `checked` dates on bounty entries help detect this.

4. **MITRE has two `assignerOrgId` values** — `50d0f415-c707-4733-9afc-8f6c0e9b3f82` (older, last used 2022) and `8254265b-2729-46b6-b9e3-3dfca2d5bfca` (current). The migration script should use the most recently active UUID.

5. **CERT/CSIRT status** — considered and deferred. CERT designation is more of an entity characteristic than a disclosure field.

## Resolved Issues

Issues raised across eight rounds of review feedback:

| Issue | Resolution |
|-------|-----------|
| Schema hard dependency claimed | Removed — `data` already allows arbitrary keys, no schema change needed |
| Phase 1/Phase 2 response shape complexity | Dropped — no special envelope. Fields are in `data`, resolver returns `data` normally. |
| `profiles` wrapper adds unnecessary complexity | Dropped — fields go directly in `data` |
| Mixed camelCase/snake_case naming | Policy: CVE-sourced names preserve CVE casing, SecID-defined use snake_case |
| `requests` mixed into CVE Program roles | `role` is strictly CVE Program vocabulary; non-participant posture goes in `posture` |
| Multi-role lossy with single role | `role` is an array — no information loss |
| Naive comma splitting in parsing | Prefer structured source data from partner-details.json |
| Missing UUID migration handling | Migration emits warning list for manual follow-up |
| Scope migration ambiguity | All existing scope fields are CNA scope (generated by same script) — deterministic |
| Module boundary / key collision risk | Reserved field names list documented |
| Inheritance wording confusion | Dropped inheritance language — resolver returns data at matched level |
| Local file path not reproducible | References cvelistV5 GitHub repo |
| Backward compat concern | Not applicable — resolver doesn't change, fields are in `data`, returned as-is |
| `cve.note` conflicts with metadata `note` convention | Renamed to `posture` — `note` stays metadata-only, `posture` is domain data |
| Phase 1 response shape ambiguous | Removed all response shape discussion — resolver doesn't change |
| Strict/full mode as dependency | Not a dependency of this proposal. Strict filtering is a self-hosted server option, mentioned for completeness but not required for implementation. |
| `role` and `posture` interaction | Documented: can coexist, but `posture` most useful for non-participants |
| `role` array normalization missing | Added: unique, lowercase, sorted alphabetically |
| bug_bounty.paid forces false certainty | Made optional — absent means unknown |

**Deferred (not blocking this proposal):**

| Issue | Plan |
|-------|------|
| Formal JSON Schema for new fields | Define when implementing — light schema for `role` enum + UUID/date formats recommended |
| Extended provenance fields (source, process, checked_by) | Separate registry-wide proposal |
| Schema-based filtering for traditional API clients | Potential self-hosted server feature, separate from this proposal |

---

*Based on design discussion about CNA tagging, disclosure researcher experience, and structured disclosure data. Eight rounds of review feedback incorporated.*
