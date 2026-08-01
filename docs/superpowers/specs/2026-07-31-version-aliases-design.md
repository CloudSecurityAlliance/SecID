# Version Aliases and Unknown-Version Handling

**Date:** 2026-07-31
**Status:** Design approved, not yet implemented
**Becomes:** ADR-009 in [DECISIONS.md](../../../DECISIONS.md)

## Problem

One release can carry more than one official version label. CSA's AI Controls Matrix
stamps `{"specification_version":"1.1.0"}` in cell A1 of every worksheet while CSA's own
artifact page, bundle ZIP, and PDF titles brand the same release "v1.1". Both labels are
in circulation and neither is wrong.

SecID cannot express this. There is no version-alias mechanism anywhere in the registry
format — the schema's only alias field, `alias_of`, is namespace-level and is unused in
all 2,130 registry files. So the string a user is most likely to type, straight off the
publisher's download page, has no defined relationship to the canonical form.

Worse, the live resolver does not validate `@version` at all:

| Query | Live status | Weight |
|---|---|---|
| `secid:control/cloudsecurityalliance.org/aicm#LOG-15` | `found` | 100 |
| `...aicm@1.1#LOG-15` | `found` | 100 |
| `...aicm@9.9#LOG-15` | `found` | 100 |

All three return identical payloads. `@9.9` has never existed. The version qualifier is
accepted, discarded, and never checked against `versions_available`. A caller who did the
right thing and pinned `@1.0.3` gets the same undifferentiated answer as one who pinned
`@1.1.0`, so pinning currently buys nothing.

### Why this matters more than a cosmetic gap

AICM 1.1.0 renumbered controls in place. Of the 242 control IDs present in both 1.0.3 and
1.1.0, **54 now designate a different control**. Only one ID (`IAM-19`) disappeared
outright, so an ID set-difference reports six changed rows and misses all 54.

| ID | 1.0.3 | 1.1.0 |
|---|---|---|
| `LOG-15` | Output Monitoring | **Input Monitoring** |
| `IAM-12` | Safeguard Logs Integrity | **Unique Identities** |
| `TVM-12` | Threat Analysis and Modelling | **Vulnerability Management Metrics** |

`SEF-09` is the clearest case: it appears in the crosswalk as *removed* ("Incident
Response") and as *added* ("Incident Records Management"). Same identifier string,
different control, one release.

CSA published no crosswalk. The 1.0.3 → 1.1.0 mapping had to be reconstructed from
specification-text similarity, and 9 rows remain flagged `review_needed`. **Once a
renumbering ships unmapped, the mapping is not fully recoverable.** A registry that makes
version pinning meaningful is the only thing that prevents the loss.

### Source-data note: use 54, not 55

The DataSets repo's prose (`aicm/VERSIONING.md`, `aicm/README.md`,
`aicm/1.1.0/README.md`) says 55 repointed IDs, 240 carried, 7 added, 3 removed, 187
unchanged, 11 `review_needed`. The committed generated artifacts
(`crosswalks/aicm-1.0.3-to-1.1.0-crosswalk.csv`, `1.1.0/aicm-1.1.0-changelog.json`) say
54, 241, 6, 2, 188, 9. Both sets are internally consistent, so this is one control
reclassified between crosswalk generations, not an arithmetic error — corroborated by
`VERSIONING.md` naming `IAM-02` as contested when the committed crosswalk does not flag
it.

**SecID cites the generated artifacts.** Values verified by recomputation from the
crosswalk CSV on 2026-07-31. Citing the stale prose would make SecID a source of the
drift it exists to prevent.

## Scope

**In scope**

- Fixed version aliases in registry data, with per-alias resolver behavior
- Unknown-version handling, including the no-substitution invariant
- Absent-version handling for sources whose item IDs are unstable across releases (D10)
- Registry data corrections for AICM, AI-CAIQ, and CCM
- Documentation corrections that this work touches

**Out of scope**

- Cross-release control mapping (`1.0.3 LOG-15` → `1.1.0 LOG-16`) — Relationship layer
- Tracking aliases (`v1` → latest `1.y.z`) — deferred, see [Deferred](#deferred)
- An explicit `@*` version wildcard — deferred; omitting the version already does this (D10)
- Alias chains — deferred

## Decisions

### D1 — The registry layer owns label aliases

Version aliases are one authority labelling one artifact two ways. That is
disambiguation, which the registry already owns. Cross-release *control* mapping is
equivalence and succession, which belongs to the Relationship layer.

This split is independently validated by two mature systems. MITRE ATT&CK keeps a revoked
technique ID resolvable and puts its successor in a `revoked-by` **relationship**. Library
authority control distinguishes MARC `4XX` "see from" (a variant label of the same entity)
from `5XX` "see also" (a different, related entity). Same line, drawn a century apart.

### D2 — Aliases nest inside `versions_available[]`

Colocated with the version they describe, so they cannot drift from it, and no second
keying scheme is needed.

Nesting also encodes the target implicitly: `1.1` sits under `1.1.0`, so that is what it
means. This is why a *tracking* alias cannot live here — its target moves, and nesting it
under `1.1.0` would become false the moment `1.1.1` ships. Tracks therefore need a
separate source-level field if they are ever built (see [Deferred](#deferred)), which is a
feature of this shape rather than a limitation of it.

### D3 — `on_match` selects behavior per alias, and is required

Two behaviors, chosen per alias rather than per namespace, so one framework can mix them:

- **`"resolve"`** — return full data inline. `status: found`. One request.
- **`"redirect"`** — return `results: []` with the canonical SecID in `message`.
  `status: corrected`. The caller must re-request.

Data-less is the entire point of `redirect`: it is what makes the correction explicit and
gives it any chance of changing client behavior. A redirect that carries data forces
nothing.

`on_match` is **required, not defaulted**. It decides whether a caller receives data, and
a silent default would let a contributor who omits the field accidentally select a
behavior.

**Deliberate tension with PRINCIPLES #3** ("Helpful over correct — always return something
useful. Never a bare error"): `redirect` returns no results. This is an argued exception,
not an oversight. The message carries the canonical SecID, which is actionable guidance
rather than a dead end. Recorded here so a future reader does not assume the principle was
missed.

### D4 — Six rules for alias data

1. **Immutable once published.** An alias is never re-pointed to a different version. If a
   publisher reuses a label for a new release, the alias is *removed*, not moved. This is
   the entire mitigation for retroactive wrongness.
2. **Never chains.** An alias names a concrete `version` in the same array. Exactly one
   hop. A resolver must not follow an alias to another alias.
3. **Labels unique within a source, including against real version strings.** `1.1` cannot
   alias two versions, and cannot be an alias at all if `1.1` is itself a real version.
   Machine-checkable; the validator must reject violations.
4. **Curated, never derived.** No prefix matching, no `v`-stripping, no semver inference.
5. **`on_match` carries the signalling**, not the label's shape.
6. **Unrecognized `on_match` values are ignored** — the alias entry is skipped, never
   guessed at. This is what lets `track` or any future value ship without breaking
   deployed resolvers.

Rule 4 is not a style preference. CSA canonicalizes in **opposite directions** across its
two flagship frameworks:

| Case | Canonical | Alias |
|---|---|---|
| AICM | `1.1.0` | `1.1` (3-part canonical, 2-part alias) |
| CCM 4.1 | `4.1` | `4.1.0` (2-part canonical, 3-part alias) |

No rule derives both. And rule 3 has a live trap: CCM `4.0` is a **genuine release** —
`4.0.13`'s metadata records that it "supersedes CCM 4.0 through 4.0.12" — so `4.0` must
never be registered as an alias of `4.0.13`.

### D5 — Resolution order; real versions win

For `name@version`:

1. Exact match against a real `version` string → resolve. `status: found`.
2. Exact match against an alias `label` → resolve to that alias's version, one hop.
   `on_match` selects `found` or `corrected`. Unrecognized `on_match` → skip entry.
3. No match, and `versions_available` is populated → unknown version, see D6.
4. `versions_available` absent or `null` → resolve as today, no version enforcement.

Step 4 is what keeps this safe for most of the registry. Per the null-vs-absent
convention, absent means "not yet researched", so the registry cannot claim a version is
invalid where versions were never documented.

### D6 — Unknown versions fail loudly, and never substitute

**The invariant: the resolver never returns item data from a version the caller did not
ask for.**

| Query | Behavior |
|---|---|
| `aicm@9.9` (no subpath) | `status: related` — return the version list. Harmless and useful. |
| `aicm@9.9#LOG-15` (subpath) | `status: not_found`, `results: []`. No substitution. |

Loud failure is chosen deliberately over a plausible-looking answer. A wrong version is a
wrong control, which is worse than a failure — a failure gets reported and fixed, a wrong
control gets cited.

This **supersedes** the behavior currently specified at
[`docs/reference/VERSIONING.md`](../../reference/VERSIONING.md) lines 138-146, which
returns `no_match_but_related` plus "Nearest: Here's IAM-12 from v4.0" with a soft
"cross-version compatibility is uncertain" note. That documented behavior is the bug this
design exists to prevent, and its example is self-refuting: `IAM-12` is one of the 54
renumbered AICM IDs.

Callers who want cross-version comparison either name each version explicitly, or omit the
version entirely to receive all of them (D10), and process the results themselves. The
resolver does not infer across versions and never picks one on the caller's behalf.

### D7 — `not_found` message contents

The message must carry everything needed to act:

- Which version was requested and that it is unknown
- The known versions with status, release date, and aliases
- How to list versions: `describe` the source without a version
- How to report a genuinely missing version, **with a source URL required**
- `did_you_mean` — suggestion only

```json
{
  "secid_query": "secid:control/cloudsecurityalliance.org/aicm@9.9#LOG-15",
  "status": "not_found",
  "results": [],
  "message": "Version \"9.9\" is not a known version of aicm. Known versions: 1.1.0 (current, 2026-06-22; aliases: 1.1, v1.1), 1.0.3 (superseded, 2025-11-10), 0.0.2 (draft). To list all versions and aliases, describe the source without a version: secid:control/cloudsecurityalliance.org/aicm. If 9.9 is a real release we are missing, report it — MCP clients: use the submit_feedback tool and include a source URL for the release. Humans and REST clients: https://github.com/CloudSecurityAlliance/SecID/issues",
  "did_you_mean": ["1.1.0"]
}
```

**`did_you_mean` is never auto-resolved.** Auto-correcting a version is the one correction
SecID must not make, for the reason in D6.

**This reverses the MCP-only feedback policy.** `API-RESPONSE-FORMAT.md:384` currently
states intake is MCP-only and that "there is no web-form submission link in the response",
and the `submit_feedback` tool description instructs agents not to tell users to open an
issue. The reversal is deliberate: raw API and data consumers include humans, who
previously had no channel at all. Both documents must be updated to match.

**Feedback category gap:** `submit_feedback`'s enum is
`missing-namespace | correction | suggestion`. A missing version is not a missing
namespace — the namespace resolves. Use `correction` for now; a `missing-version` category
would be cleaner and is a small SecID-Service change.

### D8 — `version_matched_alias` lives in `results[].data`

Next to `version`, where version data already lives. Keeps the response envelope stable.
The canonical form is already in `results[].secid`, so a client comparing query against
result detects the alias regardless of this field.

**Required whenever an alias was matched.** Optional would let implementations omit it and
make alias resolution genuinely invisible, which is the one substantive objection to
resolving transparently.

### D9 — Enforcement applies wherever `versions_available` is populated

No per-source opt-in flag. Measured blast radius as of 2026-07-31:

| Category | Source nodes |
|---|---|
| `versions_available` populated — **enforcement applies** | 375 |
| `versions_available: null` | 5 |
| `versions_available` absent | 1,688 |
| Populated with more than one version | 28 |

**Risk:** 347 of the 375 populated sources list exactly one version. Where that single
entry means "current release only, history not enumerated" rather than "this is the only
release", enforcement converts working historical-version queries into `not_found`. The
implementation plan must audit those 347 before enabling enforcement. This is a stated,
accepted risk with a mitigation task, not an unknown.

### D10 — Omitting the version is how a caller asks for all of them

An unversioned query is the mechanism for "give me everything and let me decide". SecID
already has it: `unversioned_behavior: "all_with_guidance"` returns **all** matching
versions plus the `version_disambiguation` text, and `version_required: true` stops the
resolver silently returning one.

AICM is currently configured to do the opposite. It carries `version_required: false` and
`unversioned_behavior: "current_with_history"`, so `aicm#LOG-15` returns a single control
at weight 100 with no ambiguity signal — the answer silently changes as releases ship. A
caller who asked in May 2026 and again in July 2026 got two different controls from an
identical query, with nothing in the response to indicate it.

**AICM and AI-CAIQ change to `version_required: true` and
`unversioned_behavior: "all_with_guidance"`.**

This is a behavior change to a currently-working query, and it is the most consequential
part of this design — unversioned control references are the common case, not the edge
case.

**Subpath asymmetry.** For the framework as a whole, "current" is a reasonable reading:
"AICM" does sensibly mean today's AICM. For a control *inside* it, "current" is precisely
the failure mode. But `unversioned_behavior` is one source-level field and cannot vary by
subpath presence, so the resolver applies the same subpath-dependent split D6 already
establishes for *unknown* versions:

| Query | Behavior |
|---|---|
| `aicm` (no subpath, no version) | Current version, with the others listed |
| `aicm#LOG-15` (subpath, no version) | All versions plus `version_disambiguation` |

Absent-version and unknown-version handling are therefore symmetric: item-level queries
never get a silently chosen version, and namespace-level queries stay convenient.

## Data model

```json
"versions_available": [
  {
    "version": "1.1.0",
    "release_date": "2026-06-22",
    "status": "current",
    "note": "247 controls across 18 domains. Control IDs renumbered from 1.0.3.",
    "aliases": [
      { "label": "1.1",  "on_match": "resolve",
        "note": "CSA's artifact page, bundle ZIP, and PDF titles brand this release v1.1." },
      { "label": "v1.1", "on_match": "resolve" }
    ]
  }
]
```

**Alias object**

| Field | Type | Required | Description |
|---|---|---|---|
| `label` | string | yes | The alias exactly as the publisher writes it. Never normalized (PRINCIPLES #7). |
| `on_match` | string | yes | `"resolve"` or `"redirect"`. Unrecognized values cause the entry to be ignored. |
| `note` | string | no | Where the label appears, or why it exists. |

`versions_available[]` entry fields are unchanged (`version`, `release_date`, `status`,
`note`) plus the new optional `aliases` array.

## Resolver behavior

**Alias hit, `on_match: "resolve"`**

```json
{
  "secid_query": "secid:control/cloudsecurityalliance.org/aicm@1.1#LOG-15",
  "status": "found",
  "results": [{
    "secid": "secid:control/cloudsecurityalliance.org/aicm@1.1.0#LOG-15",
    "weight": 100,
    "data": {
      "version": "1.1.0",
      "version_matched_alias": "1.1",
      "note": "No per-control web page exists. Download the bundle and open the controls sheet."
    }
  }]
}
```

Input is echoed in `secid_query`, canonical form appears in `results[].secid`. Nothing is
lossily normalized.

**Alias hit, `on_match: "redirect"`**

```json
{
  "secid_query": "secid:control/example.org/framework@old-label#X-01",
  "status": "corrected",
  "results": [],
  "message": "\"old-label\" is a superseded label for version 2.0. Request secid:control/example.org/framework@2.0#X-01"
}
```

**Edge cases**

| Case | Behavior |
|---|---|
| Alias points to a nonexistent version | Structurally impossible — nesting encodes the target (D2), so there is no separate pointer to dangle |
| Alias label equals a real version string | Validator rejects (D4 rule 3 — the CCM `4.0` trap) |
| Same label on two version entries | Validator rejects |
| Alias chain | Structurally prevented; resolver never follows more than one hop |
| Unrecognized `on_match` | Entry ignored |
| Unversioned query | Mechanism unchanged, still governed by `unversioned_behavior`. AICM's configured value changes — see D10 |
| `versions_available` absent or null | No enforcement; resolve as today |

Aliases and `unversioned_behavior` are orthogonal by design: aliases answer "which version
did you name", `unversioned_behavior` answers "you named none".

## Schema and validation

Add `$defs/VersionEntry` and `$defs/VersionAlias` to
[`schemas/registry-namespace.schema.json`](../../../schemas/registry-namespace.schema.json),
following the existing `$defs/Tags` precedent from PR #131. `match_nodes[].data` stays
`additionalProperties: true` — that openness is deliberate and is not changed here.

**Consequence: the `$defs` alone enforce nothing.** `versions_available` lives inside
`match_nodes[].data`, and because `data` is `additionalProperties: true`, a `$ref` there is
not reachable by the schema validator. This is the same situation the `Tags` `$def` already
documents: `Tags` *is* enforced at the top-level `tags` property via `$ref`, but explicitly
not inside `data.tags`. So the `$defs` here are the documented shape, and a dedicated
script — `scripts/validate-version-aliases.py` — does the actual enforcement, walking
`match_nodes` and validating each `versions_available` entry against the `$def`. Without
that script the rules in D4 are documentation, not constraints.

`skills/registry-validation` gains checks for:

- D4 rule 3: label uniqueness within a source, including collision with real version strings
- Alias targets resolving to a version entry in the same array
- `on_match` present on every alias entry
- `version` present on every `versions_available` entry

Rule 3 is the check that matters most, because the CCM `4.0` case shows the failure is
plausible rather than hypothetical.

## Registry data changes

**AICM** (`registry/control/org/cloudsecurityalliance.json`)

- Add `1.1.0` — current, released 2026-06-22, 247 controls, aliases `1.1` and `v1.1`
- Mark `1.0.3` superseded, add `release_date: 2025-11-10`, note it is the last release
  carrying NIST AI 600-1 mappings
- Add `0.0.2` as a pre-release draft
- Set `version_required: true` and `unversioned_behavior: "all_with_guidance"` per D10,
  replacing today's `false` / `current_with_history`
- Add `version_disambiguation` recording the renumbering (text below)
- Replace the **19** phantom references — 16 `aicm@1.0` and 3 `aicm-caiq@1.0` — spanning
  six files: `README.md`, `SPEC.md`, `docs/explanation/RATIONALE.md`,
  `registry/regulation.md`, `registry/control.md`, and
  `registry/control/org/cloudsecurityalliance.md`. There is no 1.0 release; the lineage is
  `0.0.2` → `1.0.3` → `1.1.0`. Note these appear in user-facing docs (`README.md`,
  `SPEC.md`), so the wrong version is currently SecID's most visible AICM example.

```
"version_disambiguation": "AICM control IDs are NOT stable across releases. Between 1.0.3
and 1.1.0, CSA renumbered controls in place: 54 of the 242 control IDs present in both
releases designate a DIFFERENT control (LOG-15 was Output Monitoring in 1.0.3, is Input
Monitoring in 1.1.0). Only one ID (IAM-19) disappeared, so an ID set-difference does not
detect this. Always cite AICM controls with an explicit version. Never migrate a reference
between versions by string match — use the published crosswalk."
```

**AI-CAIQ** (same file) — versions in lockstep with AICM, and question IDs derive from
control IDs, so `LOG-15.1` moved too. Add `1.1.0` (current) and `1.0.2` (superseded).
The existing `1.0` entry is phantom, like AICM's. Same D10 change as AICM.

**CCM** (same file) — separate defect from AICM's: SecID lists `4.0`, a real release with
no extraction, and omits `4.0.13`, which does have one. Add `4.0.13`. Add `4.1.0` as an
alias of `4.1`, and `CCM v3` as an alias of `3.0.1` — a closed major track that has
collapsed onto a fixed version. **Do not** alias `4.0` to `4.0.13`; they are distinct
releases.

**Crosswalk as a citable reference** — give the crosswalk CSV and
`aicm-1.1.0-changelog.json` `reference`-type registry entries so
`version_disambiguation` can point at them by SecID. This is identity and resolution, so
it is registry work, and it makes the renumbering lesson shareable through data
immediately rather than waiting on the Relationship layer.

**Blocked, and deferred for that reason.** A `reference` entry needs a resolvable URL.
These artifacts currently exist only as local files in the DataSets working tree — which is
not a git repository — and the only distribution path its README names is an `s3://` URI.
Until they are published at an agreed canonical location, `version_disambiguation` states
plainly that CSA publishes no crosswalk, which is accurate, rather than citing something a
consumer cannot fetch.

## Documentation changes

Correctness fixes this work depends on or exposes:

| File | Change |
|---|---|
| `DECISIONS.md` | Add ADR-009. Correct ADR-006's claim that "CI verifies they don't drift" — no such check exists |
| `docs/reference/VERSIONING.md` | Remove the "Nearest:" substitution at lines 138-146 per D6. Fix the stale example using CCM 4.1 as a nonexistent version |
| `docs/reference/REGISTRY-JSON-FORMAT.md` | Document `aliases`. Drop "target format for v1.0+" framing — JSON is live |
| `docs/reference/REGISTRY-FORMAT.md` | Badly stale: says "Current Format: YAML + Markdown", "will migrate to JSON", "Seven pilot `.json` files already exist". Reality is 2,130 JSON files at 100% coverage, deployed to KV |
| `docs/reference/API-RESPONSE-FORMAT.md` | Update line 384 for the GitHub-issues reversal. Document `did_you_mean` |
| `CLAUDE.md` | "YAML+Markdown is authoritative for contributions" no longer reflects reality |
| `SPEC.md` §5.1 | Document version aliases and unknown-version behavior |
| `docs/project/TODO.md` | Record the deferred items below |

**ADR-006's phantom drift check.** All three workflows — `update-registry.yml`,
`validate-registry.yml`, `validate-subtypes.yml` — trigger only on `registry/**/*.json`.
Nothing watches `.md`. The AICM entry is the proof: `.md` says `versions: ["1.0"]` while
`.json` says `1.0.3`, unflagged. An ADR documenting a safeguard nobody built is worse than
no ADR, because reviewers trust it.

The stale-format docs caused a real design error during this brainstorm — an earlier draft
proposed a breaking YAML migration for a format that is already legacy. They are logged as
a **separate cleanup PR**, not folded in here, to keep the alias change reviewable.

**Status vocabulary drift** (recorded, not fixed here): `PRINCIPLES.md` and
`docs/reference/VERSIONING.md` use `exact_match` / `corrected_match` /
`no_match_but_related`; `API-RESPONSE-FORMAT.md` and the live API use `found` / `corrected`
/ `related` / `not_found`. This spec uses the live API vocabulary throughout.

## Cross-repo impact

| Repo | Change |
|---|---|
| **SecID** | Registry data, schema `$defs`, validation, docs, ADR-009 |
| **SecID-Service** | Alias resolution, version enforcement, `did_you_mean`, `version_matched_alias`; optional `missing-version` feedback category |
| **SecID-Server-API** | Same resolver behavior for the self-hosted path |
| **SecID-Client-SDK** | Optional strict mode that warns or refuses on alias hits, for callers writing durable references |

Registry data alone changes none of the three live failing queries — the resolver does not
gate on `versions_available` today. **SecID-Service work is required for any of this to
take effect.**

**Strict mode** is the npm-lockfile and Docker-digest pattern: permissive at read time,
strict at write time. It is where the "teach the client" goal is actually met. Empirically,
HTTP redirects did not get the web to update its links — clients auto-follow and nothing
changes. Maven removing `LATEST` and admission controllers rejecting non-digest images
worked because they *reject*. Validation is the effective lever, not runtime redirects.

## Testing

Registry-side, runnable in this repo:

- Schema validation of the new `$defs` against every populated `versions_available`
- Validator rejects: duplicate labels, label colliding with a real version, alias pointing
  at a missing version, alias entry missing `on_match`
- Assert no `aicm@1.0` or `aicm-caiq@1.0` references remain anywhere in the repo
- Assert AICM's renumbering count is 54, matching the generated crosswalk

Service-side, for the SecID-Service PR:

- `aicm@1.1#LOG-15` → `found`, `results[].secid` carries `@1.1.0`, `version_matched_alias: "1.1"`
- `aicm@1.1.0#LOG-15` → `found`, no `version_matched_alias`
- `aicm@9.9#LOG-15` → `not_found`, `results: []`, message lists known versions, `did_you_mean` present
- `aicm@9.9` → `related` with the version list
- `aicm#LOG-15` → all versions plus `version_disambiguation`, no single silently chosen
  version (D10)
- `aicm` → current version with the others listed (D10 subpath asymmetry)
- A `redirect`-kind alias → `corrected` with `results: []`
- A source with `versions_available` absent → unchanged behavior (regression guard for the 1,688)

## Deferred

Recorded in `docs/project/TODO.md` so they are findable rather than folklore. None has a
current requirement; none should be built speculatively.

1. **Alias chains.** One hop only. Revisit only on a concrete need.
2. **Same label on multiple versions.** Currently a hard validator error (D4 rule 3). If a
   need appears, the natural shape is resolving to all matching versions with
   disambiguation — which is what `unversioned_behavior: "all_with_guidance"` already
   does, so the mechanism exists.
3. **Tracking aliases** (`v1` → latest `1.y.z`). Would be a source-level `version_tracks`
   field, *not* an `aliases[]` entry, because nesting fixes the target (D2). Recorded so
   the next person does not rediscover this the hard way. Note the precedent that a track
   collapses into a fixed alias once its major line closes — `CCM v3` → `3.0.1`.
   Deliberately not built: moving pointers are the hazard this design exists to address.
   Maven removed `LATEST` and Debian warns against `stable` for the same reason.
4. **`@*` version wildcard.** `PRINCIPLES.md` #10 defines `/*` at path levels only, and
   `SPEC.md` does not mention wildcards at all. An explicit version wildcard is unnecessary
   for now: omitting the version already returns all versions (D10), and `describe` returns
   the version list. Extending frozen grammar would need its own ADR.
5. **`missing-version` feedback category** in `submit_feedback`.
6. **A human feedback channel** distinct from URLs embedded in machine responses.

## Prior art

The decision rule this design follows, which the ecosystem converged on independently:
**if the loose form should never be used again, redirect; if it is legitimately reachable,
serve the data and declare the canonical form.** That is the HTTP `301` versus
`rel="canonical"` rule, and it generalizes. CSA's `v1.1` is on CSA's own download page, so
it is legitimately reachable — hence `on_match: "resolve"` as the normal case and
`"redirect"` reserved for labels that should be retired.

| System | Mechanism | Lesson |
|---|---|---|
| HTTP | `301` vs `Content-Location` / `rel=canonical` | Intent decides which |
| DNS | `CNAME` | Resolve server-side, keep the chain visible in the answer |
| npm | dist-tags plus lockfile | Loose request, exact record |
| Go modules | `@v1.1` partial query | Accept partial, write full canonical semver to `go.mod` |
| Docker | mutable tags vs immutable digests | Do not break `:1.1`; enforce pinning at the policy layer |
| Maven | `LATEST` / `RELEASE` | Removed — irreproducible labels caused too much pain |
| Ubuntu / Debian | `jammy` ≡ `22.04` | Co-equal labels, both recorded. The *moving* pointer is the hazard |
| MARC authority | `4XX` see-from vs `5XX` see-also | Variant labels are not related entities |
| ATT&CK | `revoked` + `revoked-by` | Keep IDs resolvable; successors live in relationships |
| CVE / CWE / CPE | `REJECTED`, deprecation pointers | Never break a published identifier |

DOI is the one true redirect, and it is a different problem: it redirects an identifier to
a *location*, not to another identifier.
