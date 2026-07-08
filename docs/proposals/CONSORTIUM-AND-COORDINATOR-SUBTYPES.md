# Proposal: `consortium`, `coordinator`, and `psirt` subtypes

Status: Draft / discussion
Date: 2026-07-08

## Summary

Formalize three named subtypes:

| Type | `subtype:` value | Groups |
|------|------------------|--------|
| `entity` | `consortium` | Multi-organization collaborative bodies (consortia, coalitions, alliances, foundations) |
| `disclosure` | `coordinator` | Neutral coordinated-vulnerability-disclosure bodies (CERT/CC, national CSIRTs, shared SIRTs) |
| `disclosure` | `psirt` | A vendor's own Product Security Incident Response Team program |

These are the **first** subtypes for both `entity` and `disclosure` (both are `subtypes: []` in SecID-Service's `type-registry.ts` today).

This proposal also **explicitly declines** to create `cna`, `bug-bounty`, and `security.txt` subtypes — three values floated as candidates in [TYPES-AND-SUBTYPES.md](../reference/TYPES-AND-SUBTYPES.md) — because those facts are already carried by structured fields (`cve.role`, `bug_bounty[]`, `security_txt`) from [DISCLOSURE-TYPE-FIELDS.md](DISCLOSURE-TYPE-FIELDS.md). See *Deliberately not subtypes* below.

The governing principle: **subtypes name the program/body archetype; structured fields carry the details.** A subtype earns its place only when it groups a distinction not already served by a structured field.

## Motivation

A 2024–2026 wave of multi-organization security initiatives (CoSAI, MOSAIC, ORCA, Akrites, Chainguard's Athena, the Frontier Model Forum) has no clean way to be grouped in the registry, and the large `disclosure` type (486 entries) has no way to distinguish *what kind of program* an entry is beyond its CVE-program role. Two grouping gaps:

1. **`entity` cannot say "this is a multi-stakeholder body."** The type mixes single organizations, products, and services. There is no discriminator for "collaborative body formed by many members" — the exact character shared by CoSAI, Akrites, OpenSSF, and OASIS Open.
2. **`disclosure` cannot distinguish a coordination center from a vendor PSIRT.** Today CNA-ness is structured (`cve.role`), but "is this a neutral coordinator (CERT/CC, JPCERT, a shared SIRT) vs. a single vendor's own security team?" is not.

The registry data already makes these distinctions **informally, in free text.** The disclosure `organization_type` field (free text) contains, among 486 entries:

| `organization_type` (free text) | Count | Relates to |
|---|---|---|
| `Vendor` (+ combinations) | ~350 | `psirt` |
| `CERT` / `Vendor, CERT` | 21 | `coordinator` |
| `Consortium` | 2 | `consortium` (entity) |
| `Bug Bounty Provider` (+ combinations) | ~9 | (stays a field, see below) |

So `consortium` and `coordinator` are not new concepts — they **formalize distinctions the data already draws in prose**, which also makes rollout semi-automatable (derive the subtype from `organization_type`).

## Design

Subtypes are an array of strings in a source-level match_node's `data.subtype` (the mechanism defined in [TYPES-AND-SUBTYPES.md](../reference/TYPES-AND-SUBTYPES.md)). No schema change — `data` is `additionalProperties: true`.

### `entity` → `consortium`

A multi-organization collaborative body: a consortium, coalition, alliance, or foundation formed by multiple member organizations.

- **Refines the organization form** — a consortium *is* an organization, so `consortium` composes with a future `organization`/`product`/`service` axis rather than competing with it (`["organization", "consortium"]` is valid). Adopting `consortium` now does not block that later split.
- **Examples:** CoSAI, Akrites, MOSAIC, ORCA, Athena, Frontier Model Forum, OpenSSF, OASIS Open, Linux Foundation.
- **Not a consortium:** a single company (Microsoft), a product (AWS S3), a government agency acting alone.

### `disclosure` → `coordinator`

A neutral coordinated-vulnerability-disclosure body that routes reports between finders and affected vendors — the **coordinator** role in the FIRST / ISO 29147 CVD model (reporter → vendor → coordinator → deployer).

- **Examples:** CERT/CC, national CSIRTs (JPCERT/CC, INCIBE, CISA), FIRST, and the new shared SIRTs (Akrites; Athena's aspired SIRT).
- **Composes with `cve.role`.** A national CERT that also assigns CVEs is `subtype: ["coordinator"]` **and** `cve.role: ["cna"]` (or `root`). The subtype describes the body's coordination function; `cve.role` describes its formal CVE-program standing. Different facts, no overlap.
- **Distinct from `psirt`:** a coordinator is *neutral* (sits between finders and third-party vendors); a PSIRT handles *its own* vendor's products.

#### Reversing a prior deferral — consciously

[DISCLOSURE-TYPE-FIELDS.md](DISCLOSURE-TYPE-FIELDS.md) Open Question #5 previously considered and deferred CERT/CSIRT status, noting *"CERT designation is more of an entity characteristic than a disclosure field."* This proposal overrides that lean, for two reasons:

1. **The deferral predates the subtype mechanism.** It weighed a boolean *field* (`is_cert`) and reasonably concluded a flag felt entity-ish. A `subtype` classifying the *program archetype* is a different, better-fitting tool that did not exist at the time.
2. **The coordination role is a property of the disclosure program, not just the org.** "Who coordinates the report, and how" is exactly the question the `disclosure` type answers. INCIBE already carries `organization_type: "CERT"` *inside its disclosure `data` block* — the CERT-ness is already living in disclosure data, not entity data.

An organization that is a coordinator still gets an `entity` record too (per the standards-publishing-org two-file pattern in [CLAUDE.md](../../CLAUDE.md)); `coordinator` just isn't an *entity* subtype.

### `disclosure` → `psirt`

A vendor's own Product Security Incident Response Team program — receives and coordinates vulnerability reports for that vendor's own products.

- **Examples:** Cisco PSIRT, Siemens ProductCERT, a mid-size vendor's `security@` program.
- **Not fully captured by an existing field.** Unlike `cna`, there is no structured `psirt` field; `organization_type: "Vendor"` is free text and covers many non-PSIRT cases. So `psirt` adds a discovery axis that isn't already structured.

## Deliberately not subtypes: `cna`, `bug-bounty`, `security.txt`

[TYPES-AND-SUBTYPES.md](../reference/TYPES-AND-SUBTYPES.md) lists these three as candidate disclosure subtypes. This proposal declines them because each **duplicates a structured field that already exists and is populated:**

| Candidate | Already structured as | Populated |
|-----------|-----------------------|-----------|
| `cna` | `cve.role: ["cna"]` (protected CVE-program vocabulary) | 513 match_nodes migrated (DISCLOSURE-TYPE-FIELDS Phase 2, done 2026-04-08) |
| `bug-bounty` | `bug_bounty: [{url, paid}]` array | Field defined; population deferred |
| `security.txt` | `security_txt: {url}` object | 170 found / 277 null (Phase 3, done 2026-04-08) |

Creating a parallel `subtype` for any of these introduces **two sources of truth for one fact** — the subtype and the field must then be kept in agreement forever, and any drift is a silent data bug. "Is this a CNA?" is answered losslessly by `cve.role`; a consumer wanting a CNA-discovery axis queries the field. The candidate-subtype rows in TYPES-AND-SUBTYPES.md should be re-annotated to record this decision so the values are not re-proposed.

## Cross-repo rollout (ordering matters)

Subtype values are CI-gated: `scripts/validate-subtypes.py` fails any SecID PR that uses a `subtype:` value not declared in SecID-Service's `type-registry.ts` at the pinned SHA. The rollout therefore has a strict order:

1. **SecID-Service PR** — add `consortium` (entity) and `coordinator` + `psirt` (disclosure) to `TYPE_REGISTRY` in `src/type-registry.ts`. Merge **first**.
2. **SecID PR (this proposal)** — the proposal doc. Pure docs, no `subtype:` usage, so CI is unaffected; can land independently.
3. **SecID PR (gated on step 1)** —
   a. Bump `SECID_SERVICE_PINNED_SHA` in **both** `scripts/validate-subtypes.py` and `scripts/validate-type-list.py` to the merged step-1 commit (lockstep, per the pin comment).
   b. Move the three values into the "Named subtypes in use today" tables in `docs/reference/TYPES-AND-SUBTYPES.md`; re-annotate the `cna`/`bug-bounty`/`security.txt` candidate rows with the "stays a field" decision above.
   c. Tag entries (below).

### Tagging plan

Per TYPES-AND-SUBTYPES.md, the default is tag-from-day-one, no backfill sweeps — with a carve-out for bounded, tractable sets (methodology's ~40-node sweep is the precedent).

- **From day one:** the new consortium/coordinator entries this proposal is motivated by — Akrites (`entity` + `disclosure coordinator`), CoSAI/MOSAIC/ORCA/Athena/FMF (`entity consortium`), etc.
- **Bounded targeted sweep (optional, tractable):** the **21** disclosure entries with `organization_type` containing `CERT` → `subtype: ["coordinator"]`, and the **2** with `Consortium` → their entity records get `consortium`. This is semi-automatable and small enough to review by hand.
- **`psirt`:** opportunistic — tag when an entry is touched for other reasons; no ~350-entry `Vendor` sweep.

No client-SDK changes: SDKs pass `type`/subtype values through and do not validate. SecID-Server-API's `SECID_TYPES` is the *type* list, unaffected by subtype additions.

## Alternatives considered

- **Put `coordinator`/CERT on `entity` instead** — rejected; see *Reversing a prior deferral*. The coordination role is a disclosure-program property, and CERT-ness already lives in disclosure `data`.
- **Formalize all five candidate disclosure subtypes** (`cna`, `bug-bounty`, `psirt`, `security.txt`, `coordinator`) for a uniform discovery axis — rejected; three of them duplicate structured fields and create drift risk. Single source of truth wins.
- **Free-text grouping via a non-`subtype` `data` key** (e.g., `data.grouping`) — rejected; it would pass CI without a SecID-Service change but is invisible to the resolver/MCP/clients, forfeiting the cross-source-discovery affordance that is the whole point of subtypes.

## Open questions

1. Should `coordinator` (and eventually `psirt`) be *derivable* from `organization_type` in a future normalization, letting us retire the free-text `organization_type` values in favor of structured subtypes + the `cve.role`/`bug_bounty` fields?
2. Do we want the eventual `entity` `organization`/`product`/`service` split (an ENTITY-REGULATION-CONTROL-SPLIT follow-up) in the same rollout, or keep `consortium` as the sole entity subtype until that split is designed?
