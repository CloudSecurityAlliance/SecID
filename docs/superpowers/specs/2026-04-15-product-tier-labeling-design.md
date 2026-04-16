# Product Tier Labeling Design

**Date:** 2026-04-15
**Status:** Draft
**Scope:** Entity type — labeling product tiers/flavours using `@version`
**Affects:** Entity registry entries, entity type documentation

## Problem

Cloud and SaaS products are sold in tiered plans (Zendesk Team vs Enterprise, Google Workspace Business vs Enterprise, Cloudflare Free vs Business). Security capabilities vary dramatically by tier — audit logs, SSO, sandbox environments, and other security features are frequently gated behind higher-priced plans.

SecID currently has no way to label "Zendesk Enterprise" as distinct from "Zendesk Team." The entity type identifies organizations and products but not product tiers. Without tier labeling:

- The relationship/data layer can't map capabilities to specific tiers
- Security assessments can't express "your score ceiling is 90 because of your tier"
- There's no stable identifier for "the Enterprise edition of this product"

## Approach: Tiers as `@version` on Entity Entries

Product tiers are versions/editions of a product. For SaaS products, the tier is the primary meaningful version — everyone on "Zendesk Enterprise" is on the same Zendesk Enterprise. SaaS tiers don't have user-facing version numbers, though their entitlements do change over time (features added, removed, renamed). Those changes are tracked at the data/enrichment layer via `_checked`/`_updated` metadata and lifecycle dates in `versions_available`, not as separate identities.

Use the existing `@version` mechanism in the SecID grammar. No grammar changes, no new types, no new fields.

### Regex Dialect Decision (logged in spec)

For this design (and as a general registry direction), regex patterns are canonicalized to **ECMAScript `RegExp`** syntax because SecID-Service executes in Cloudflare Workers (TypeScript/JavaScript runtime).

- **Single canonical pattern set in registry:** do not store parallel regex-by-engine variants (`ecmascript`, `pcre`, `python`, etc.) in registry files.
- **Cross-runtime support via tooling:** non-JS consumers use generated/translated validators from canonical ECMAScript patterns.
- **Validation order:** required compile check in JS runtime; optional compatibility checks in Python/Go/Rust as secondary gates.
- **Portable subset discipline:** keep patterns simple and anchored; avoid engine-specific constructs when possible.

This keeps one source of truth aligned with production runtime behavior while still supporting non-JS clients through tooling.

### `@version` is opaque

SecID `@version` strings are opaque identifiers, not comparable or sortable by clients. The registry documents what versions exist and their relationships via `versions_available` and `version_disambiguation`. Clients must not assume SemVer, lexicographic ordering, or any internal structure. This is already true for existing uses (OWASP uses years, NIST uses `1.1`/`2.0`) and extends naturally to tier names.

### Tier token aliasing via regex

Vendors use varied formats for tier names ("Enterprise Plus", "enterprise-plus", "E+"). The canonical tier token is defined in `versions_available`. The per-source regex patterns provide aliases that match common input variants — the same mechanism SecID already uses everywhere (e.g., OWASP Top 10 matches `top10`, `top-10`, and `owasp-top-10`).

Example: for a canonical token `enterprise-plus`, the version-matching regex accepts variants:

```
/^enterprise[_-]?plus$/i
```

This matches `enterprise-plus`, `enterprise_plus`, `enterpriseplus`, `Enterprise-Plus` — all resolve to the canonical `enterprise-plus`. To pick the canonical token: when a vendor has a URL slug or API identifier for the tier, prefer that (follow the source). Otherwise, use lowercase with hyphens for word separators — the same convention entity product names already follow (e.g., `openshift-container-platform`, `directory-server`).

### Three levels, all independently valid

```
secid:entity/zendesk.com                        → Zendesk Inc. (the company)
secid:entity/zendesk.com/zendesk                → Zendesk (the product, all tiers)
secid:entity/zendesk.com/zendesk@enterprise     → Zendesk Enterprise (specific tier)
```

Each level is meaningful on its own:

| Level | Identifies | Use case |
|-------|-----------|----------|
| Company | The organization | "Who operates this?" |
| Product | The product/service regardless of tier | Relationship mappings that apply to ALL tiers |
| Tier | A specific edition/flavour | Relationship mappings that are tier-specific |

The unversioned product form (`secid:entity/zendesk.com/zendesk`) is not incomplete or ambiguous — it's a valid reference meaning "the product across all tiers." This is important for the relationship layer, where some capability mappings apply universally (e.g., "Zendesk supports email") while others are tier-gated (e.g., "audit logs require Enterprise").

### No `version_required`

Unlike OWASP Top 10 (where A01 means different things in 2017 vs 2021), an unversioned product reference is not ambiguous. `secid:entity/zendesk.com/zendesk` is simply "Zendesk." Whether a tier is needed is a decision for the relationship/data layer, not the identity layer.

## Examples

### SaaS with bundled tiers

```
secid:entity/zendesk.com/zendesk@team               → Zendesk Team
secid:entity/zendesk.com/zendesk@growth              → Zendesk Growth
secid:entity/zendesk.com/zendesk@professional        → Zendesk Professional
secid:entity/zendesk.com/zendesk@enterprise          → Zendesk Enterprise
secid:entity/zendesk.com/zendesk@enterprise-plus     → Zendesk Enterprise Plus

secid:entity/google.com/workspace@business-starter   → Google Workspace Business Starter
secid:entity/google.com/workspace@enterprise         → Google Workspace Enterprise
secid:entity/google.com/workspace@enterprise-plus    → Google Workspace Enterprise Plus

secid:entity/cloudflare.com/cloudflare@free          → Cloudflare Free
secid:entity/cloudflare.com/cloudflare@pro           → Cloudflare Pro
secid:entity/cloudflare.com/cloudflare@business      → Cloudflare Business
secid:entity/cloudflare.com/cloudflare@enterprise    → Cloudflare Enterprise
```

### A la carte services (no tiers)

```
secid:entity/aws.amazon.com/s3                       → AWS S3 (no tiers, no @version)
secid:entity/aws.amazon.com/cloudtrail               → AWS CloudTrail
```

For a la carte products, there are no tiers to label. The capability is either enabled or not. The entity has no `versions_available`.

### On-prem with temporal versions

```
secid:entity/redhat.com/openshift@4.14               → OpenShift 4.14
secid:entity/redhat.com/rhel@9                       → RHEL 9
```

### Hybrid: flavour + temporal version (rare)

When a product has both a tier/flavour AND a temporal version, use `@` twice — flavour first, then version:

```
secid:entity/redhat.com/openshift@plus@4.14                    → OpenShift Plus, version 4.14
secid:entity/redhat.com/openshift@container-platform@4.14      → OCP 4.14
```

The SecID parser captures everything after the first `@` up to `#`, `?`, or end of string as the version. The second `@` is just a character within the version string. The per-source regex in the registry parses the internal structure:

```json
{
  "patterns": ["^([a-z-]+)(?:@(\\d+\\.\\d+))?$"],
  "description": "Product flavour with optional temporal version"
}
```

This compound form is expected to be rare. The vast majority of uses are single-component: `@enterprise` (SaaS) or `@4.14` (on-prem).

**Caveat:** The compound `@flavour@version` form means clients that treat `@version` as an atomic/comparable value will see an opaque string they can't sort or compare. This is acceptable because SecID versions are already opaque and non-comparable (see "`@version` is opaque" above). Clients must use `versions_available` metadata for ordering, not string comparison. The compound form is a last resort for the rare hybrid case — do not use it when a single component suffices.

## Two product worlds

| Product type | `@version` means | Temporal version? | Examples |
|---|---|---|---|
| SaaS with tiers | Plan/flavour | No user-facing versions; entitlements change over time (tracked at data layer) | `zendesk@enterprise`, `workspace@business-plus` |
| On-prem/versioned | Temporal version | Yes | `openshift@4.14`, `rhel@9` |
| A la carte cloud | Not used | No | `aws.amazon.com/s3` (no `@version`) |
| Hybrid (rare) | Compound: flavour@version | Yes | `openshift@plus@4.14` |

## Registry Entry Changes

Entity registry entries for tiered products add `versions_available` and `version_disambiguation` to their match_node data. These fields already exist in the JSON schema (used by OWASP Top 10, etc.).

### Example: Zendesk entity entry

```json
{
  "schema_version": "1.0",
  "namespace": "zendesk.com",
  "type": "entity",
  "status": "draft",
  "official_name": "Zendesk, Inc.",
  "common_name": "Zendesk",
  "urls": [
    {"type": "website", "url": "https://www.zendesk.com"}
  ],
  "match_nodes": [
    {
      "patterns": ["^zendesk$"],
      "description": "Zendesk customer service platform",
      "weight": 100,
      "data": {
        "official_name": "Zendesk",
        "description": "Customer service and support platform. Offered in tiered plans with different security capabilities per tier.",
        "urls": [
          {"type": "website", "url": "https://www.zendesk.com/pricing/"}
        ],
        "versions_available": [
          {"version": "team", "status": "current", "note": "Basic plan. Limited reporting."},
          {"version": "growth", "status": "current", "note": "Growing teams."},
          {"version": "professional", "status": "current", "note": "Mid-tier."},
          {"version": "enterprise", "status": "current", "note": "Full security features including audit logs, SSO, sandbox."},
          {"version": "enterprise-plus", "status": "current", "note": "Highest tier. Enhanced security and compliance."}
        ],
        "version_disambiguation": "Tiers ordered by price: Team < Growth < Professional < Enterprise < Enterprise Plus. Tier names follow Zendesk's own naming. Higher tiers generally include more features, but the relationship layer defines exactly which capabilities each tier provides — do not assume strict supersets."
      }
    },
    {
      "patterns": ["^sell$"],
      "description": "Zendesk Sell — CRM and sales platform",
      "weight": 100,
      "data": {
        "official_name": "Zendesk Sell",
        "description": "CRM and sales automation platform. Separate product with its own tier structure.",
        "versions_available": [
          {"version": "team", "status": "current"},
          {"version": "growth", "status": "current"},
          {"version": "professional", "status": "current"},
          {"version": "enterprise", "status": "current"}
        ]
      }
    }
  ]
}
```

## What does NOT change

- **SecID grammar (SPEC.md)** — `@version` already exists, no syntax changes
- **Parser behavior** — version is already "everything after `@` up to `#`/`?`/end"
- **Resolver behavior** — unversioned resolves normally, versioned resolves with the tier
- **Capability entries** — unchanged, no tier awareness at the identity layer
- **No new types** — entity with existing fields
- **No new JSON schema fields** — `versions_available` and `version_disambiguation` already defined

## Relationship layer context (out of scope, noted for future)

The identity layer labels tiers. The relationship/data layer (separate design, likely in a private CSA registry) will:

- Map capabilities to entity tiers (`secid:capability/zendesk.com/zendesk#audit-logs` requires `secid:entity/zendesk.com/zendesk@enterprise`)
- Use the unversioned entity (`secid:entity/zendesk.com/zendesk`) for mappings that apply to all tiers
- Implement fail-open vs fail-closed policy for new tiers (relationship-layer decision)
- Support score capping ("your ceiling is 90 because of your tier")
- This data is politically sensitive (not vendor-neutral) and likely private/internal to CSA

## Implementation

This is a documentation and convention change, not a code change:

1. **Update entity type documentation** (`registry/entity.md`) — add a section on product tiers as versions
2. **Update VERSIONING.md** — add a section explaining that `@version` covers both temporal versions and product flavours/tiers
3. **Create example entity entries** — Zendesk, Google Workspace, Cloudflare as proof-of-concept tier-labeled entities
4. **Update regex docs** (`docs/guides/REGEX-WORKFLOW.md`, `docs/reference/REGISTRY-JSON-FORMAT.md`) — record ECMAScript as canonical registry dialect and conversion/validation expectations for other runtimes
5. **Add validation tooling task** — JS compile checks required for all registry patterns; optional Python/Go/Rust compatibility checks
6. **Update CLAUDE.md** — document the convention for entity tiers and ECMAScript-first regex policy
