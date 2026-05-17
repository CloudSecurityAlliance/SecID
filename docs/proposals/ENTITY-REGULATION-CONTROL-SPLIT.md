# Proposal: Three-Type Split — `entity` + `regulation` + `control`

Status: **Declined (regulation/control split); entity cleanup may be salvaged separately**
Date: 2026-05-14 (proposal); 2026-05-17 (decision)
Author: Kurt Seifried, with AI-assisted design
Reviewers: open — please add review notes inline or as PR comments; the decision below is explicitly open to challenge

> **Quick orientation for readers**: this proposal originally argued for a three-way type split. After analysis, we decided not to proceed with the regulation/control split. The original argument is preserved below intact, followed by the analysis that led to the decision. **If you think the decision is wrong, please challenge it — this is exactly the kind of design call worth re-examining as the project scales.**

## Summary

The `control/` registry currently conflates three distinct concepts under one namespace tree:

1. **Organizations** that publish standards/programs (ISO, UIDAI, NPCI, Visa, BSI Germany, …)
2. **Laws and regulations** that authorize, mandate, or shape those programs (Aadhaar Act 2016, PSD2, eIDAS, GDPR, HIPAA, …)
3. **The actual published standards/specs/programs** (ISO 27001, Aadhaar Auth API, UPI rulebook, Visa AIS, …)

Today all three flow into `control/<namespace>/<product>` because that's the type we started with. SecID's type system already has clean homes for #1 (`entity`) and #2 (`regulation`); only #3 should really stay in `control/`. This proposal lays out the three-type split — what changes, how to migrate, and how to preserve existing citations.

---

## Decision and Rationale (2026-05-17)

After reflection and discussion, **the regulation/control split portion of this proposal is declined**. The entity-extraction portion may be salvaged as a separate, narrower proposal.

This section documents *why* we landed here, so a future reviewer can either accept the reasoning or build a counter-case from it.

### What the original proposal got right

- **The three-way conceptual model is clean.** Organizations, legal instruments, and published specs really are three different kinds of things at the identity layer. The Aadhaar Act 2016 and the Aadhaar Authentication API are clearly different artifacts.
- **The entity-vs-publication confusion is a real bug.** "ISO the organization" and "ISO 27001 the standard" sitting in the same `control/` namespace tree is genuinely confusing. Cyber-rating providers (BitSight, SecurityScorecard, UpGuard, CyberCube) sitting in `control/` despite having no published controls is also a real misfit.
- **Cross-reference infrastructure (`publishedBy:`, `authorizedBy:`) is valuable** regardless of whether the type split happens. It enables graph queries the current registry can't answer.

### Where the analysis broke down — content straddling

The core problem with separating `regulation` from `control`: real-world content straddles the line constantly.

| Source | Current type | Contains technical control content? |
|---|---|---|
| GDPR Article 32 | regulation | Yes — encryption, pseudonymization, integrity, availability |
| HIPAA Security Rule (Technical Safeguards, 164.312) | regulation | Yes — explicit technical controls |
| NYDFS 23 NYCRR 500 | regulation | Yes — MFA, encryption, IRP requirements |
| DORA (EU Digital Operational Resilience Act) | regulation | Yes — explicit ICT risk controls |
| China Cybersecurity Law (graded protection) | regulation | Yes — technical requirements |
| NIST 800-53 | control | No — but FISMA *requires* it for federal systems |
| PCI DSS | control | No — but card-brand contracts enforce it |
| ISO 27001 | control | No — but adopted into law in several jurisdictions |

The line between "law" and "spec" is real at the document boundary, but blurs constantly *within* documents. GDPR contains both legal scaffolding (Articles 6, 7, on lawful basis) and technical control content (Article 32). Forcing the document into a single type loses information either way.

### Honest benefit/cost inventory for the split

**Candidate benefits, evaluated:**

| Benefit | Real value? |
|---|---|
| Type-level filtering ("show me only regulations") | Weak — most consumers don't think "law vs spec," they think "what applies to me?" |
| Semantic clarity in resolution responses | Weak — could be a tag/field inside a single type, no type split needed |
| AI/tool routing of legal vs technical queries | Weak — assumes the routing distinction is clean; it isn't, given content overlap |
| Authority/enforcement modeling (penalties, jurisdiction) | Misplaced — that's enrichment-layer data, not registry-layer typing |
| Mirrors how compliance practitioners think | Real but small, and fuzzier in practice than in theory |
| Citation precision | Cosmetic — `secid:regulation/eu/gdpr#article-32` reads slightly better than `secid:control/...` but resolves the same thing |

**Costs:**

- Migration: ~50–100 namespace moves, backwards-compat shims for old citations
- Multi-repo lift across 4 repos (SecID, SecID-Service, SecID-Server-API, SecID-Client-SDK)
- Consumer query burden — looking in multiple types for overlapping content
- Per-entry decision burden ("is this regulation or control?") with no clean answer for straddlers
- Ongoing maintenance cost as new entries arrive that don't fit cleanly

The costs are concrete; the benefits are largely aesthetic. That's the core of the decision.

### Pattern this confirms

A pattern is emerging across recent design discussions in SecID: **before adding or splitting types, check whether the work can be done with existing types + relationship layer + per-entry fields.** Examples from this session and adjacent ones:

- **GLOSSARY-DEFINITION-COMPARISON proposal**: explicitly chose *not* to add a `definition`/`glossary` type. Glossary documents stay in `reference`; terms are subpaths; cross-source comparisons are relationship-layer data.
- **ASSERTION-CONTENT-TYPES proposal**: initially proposed `assertion + content` (2 new types). Subsequent analysis showed BoKs fit `control` (as normative knowledge specs), courses fit `reference` (as content artifacts with subpaths), and org-level compliance attestations fit relationship-layer ("AWS is compliant with TSC" rather than `assertion/aicpa.org/soc-2`). The 2-type proposal collapses toward 1 type or 0.
- **This proposal**: the regulation/control split looks elegant but doesn't pay off at user-facing layer; cross-references and optional tags can deliver the same value without the type expansion.

CLAUDE.md's principle "types are intentionally overloaded; split only when usage proves it necessary" is doing real work in these decisions. The principle isn't "never split" — it's "split when the user-facing benefit justifies the cost," and we've kept landing on "it doesn't."

### Non-type alternatives that would deliver some of the same value

Instead of splitting the type, consider these additive moves (each independent, each cheaper than a type split):

1. **Optional `enforcement` field on existing entries**: e.g., `enforcement: ["legal:FISMA", "contractual"]` on NIST 800-53, `enforcement: ["legal"]` on GDPR, `enforcement: ["voluntary", "contractual"]` on CCM. Captures the legal-vs-voluntary distinction without changing types or moving entries. Easily added later if/when consumers ask for the distinction.
2. **Cross-reference fields where they pay off**: `publishedBy:` and `authorizedBy:` are useful on their own — they enable graph queries ("everything authored by ISO," "everything authorized by PSD2") without requiring a type split. Could be added to the existing schema with no migration.
3. **`type_hint:` or `category:` field for downstream filtering**: a soft hint like `category: "legal-instrument"` vs `category: "voluntary-standard"` lives in data, not in the type system. Easier to refine and re-categorize than a type migration.

### What's still worth doing

- **Entity-vs-publication cleanup** (Phase 1 of the original proposal): extract org-only records (BitSight, SecurityScorecard, ISO-the-org) into `entity/`. This is the strongest single piece of the proposal and could move forward as a much narrower revision. Scope: ~10–20 namespaces that are clearly orgs-not-controls, not all ~166 entries.
- **Cross-reference field design** (Phase 0's schema work): even without a type split, adding `publishedBy:` and `authorizedBy:` cross-reference fields to the existing `control/` schema would close the queryability gap. The schema work isn't wasted if we recover this piece.

### Invitation to challenge this decision

This decision was made on 2026-05-17 based on the current state of SecID (~166 control namespaces, ~50–100 candidate regulations, ~10 types). A future reviewer might reasonably reach a different conclusion if:

- **Scale changes the math**: at 5,000+ namespaces, the type split's organizational value might dominate the migration cost. We're not there yet, but the inflection point exists.
- **A use case emerges that the current model can't serve**: e.g., a legal AI agent that needs strict legal-vs-spec distinction, or a compliance product that monetizes the difference.
- **The straddling problem gets resolved differently**: if a new pattern emerges for documents-that-are-both (split-by-section? virtual-cross-references?), the regulation/control distinction at the document level might be clean enough to justify.
- **A simpler migration path is found**: the cost calculus changes if migration becomes cheaper (e.g., automated namespace rewriting with full citation compatibility).
- **The data itself argues otherwise**: if a thorough analysis of the actual ~50–100 candidate regulations finds 90%+ are unambiguously laws-not-specs, the straddling-content concern weakens.

If you believe the decision is wrong, please open a PR with a counter-argument. This proposal is preserved as a record of our thinking, not as a closed door.

---

## Original proposal (preserved for context)

> The remainder of this document is the original proposal as written on 2026-05-14, before the decision-and-rationale section above was added. It is preserved intact so future readers can see the original argument and the structure we considered. The phasing and migration plan below describe what *would have* happened if the proposal had been accepted in full.

## The Problem

Currently each namespace file in `registry/control/` carries:

- **Organization-identity metadata** at the file root: `official_name`, `common_name`, `notes`, `urls`, alternate names
- **A list of `match_nodes`** — each match_node is actually a standard/spec/program (the control proper)

That makes the file simultaneously an org record *and* a controls catalogue. Consequences:

- **No graph queries across types.** "Show me everything authorized by PSD2" needs entity-of-publisher → regulation cross-references that don't exist as structured fields.
- **License posture conflation.** An organization's identity record is freely citable (you can always reference *that* UIDAI exists). Its published documents may be paywalled. Single-record treatment merges these and forces the license metadata to describe the lesser-permissive case.
- **Citation ambiguity.** `secid:control/iso.org` could mean "ISO the organization" (which is identity) or "any ISO standard" (which is a control class). Without explicit type separation, the resolver has to guess.
- **Mixed publishing relationships are hidden.** A control can have a publishing entity *and* an authorizing regulation *and* sometimes a parent entity (e.g., NSCC, FICC, DTC are all subsidiaries of DTCC). These relationships are encoded in `notes:` text today instead of as queryable fields.
- **Org-only namespaces are awkward.** Some namespaces we've added (cyber-rating providers like BitSight, SecurityScorecard) have no real published spec — they're just organizations with proprietary internal methodologies. They sit in `control/` only because that's where namespaces go, not because they catalogue any control.

## Conceptual Model

The clean three-way split:

| Type | What it represents | Examples |
|---|---|---|
| `entity` | An organization that exists. The legal/operational identity. | UIDAI, ISO, Banco Central do Brasil, Visa Inc., BSI Germany, NPCI |
| `regulation` | A law or binding regulatory instrument. | Aadhaar Act 2016, PSD2 (Directive 2015/2366), GDPR, eIDAS, DPDP Act 2023, HIPAA |
| `control` | A published standard, specification, or program — a normative artefact an organization adopts. | ISO/IEC 27001:2022, Aadhaar Authentication API, UPI rulebook, Visa AIS, BSI IT-Grundschutz, SPID |

Relationships flow:

```
regulation ──authorizes──> entity ──publishes──> control
       └─────────────applies-to──────────────────┘
```

Example: the Aadhaar identity citation chain:

| SecID | Type | What |
|---|---|---|
| `secid:regulation/in/parliament/aadhaar-act-2016` | `regulation` | The Aadhaar (Targeted Delivery of Financial and Other Subsidies, Benefits and Services) Act, 2016 |
| `secid:entity/in/gov/uidai` | `entity` | UIDAI — the statutory authority created by the Aadhaar Act |
| `secid:control/in/gov/uidai/auth-api` | `control` | Aadhaar Authentication API specification (a deliverable from UIDAI) |

With explicit `authorizedBy:` on the entity record and `publishedBy:` on the control, a resolver can answer "everything under Aadhaar" by traversing the graph.

## Why Not Keep Conflating?

It worked for the first ~50 entries. With 235+ controls across 166 namespaces and growing, the friction points are visible:

- Some namespaces have no published spec at all (BitSight, UpGuard, CyberCube — proprietary scorers) but sit in `control/` because we needed somewhere to put them. They're really `entity/` records.
- Some namespaces are dominated by their authorising regulation (EPC for SEPA — PSD2-derived; UIDAI for Aadhaar — Act-derived). The regulation has independent identity.
- Some namespaces include both standards-publisher and operator roles (Bank of Thailand publishes PromptPay operational rules *and* is a regulator). These are *two* concerns the current model can't disentangle.

A different organization of the same data unlocks:

- **Cross-type queries** ("everything authorized by PSD2"; "all controls published by ISO")
- **Per-type license metadata** (entity identity is always free to cite; published controls may be paywalled)
- **Stable citation chains** (you can cite the entity persistently even when the controls list churns)
- **Cleaner deprecation** (a regulation can be repealed without invalidating the entity; an entity can dissolve without invalidating the regulations that bind successor entities)

## Scope

The migration covers:

- **~166 organizations** currently catalogued under `control/` get extracted into `entity/` records
- **~50–100 major regulations** that authorize or shape current control programs get added as `regulation/` records (some `regulation/` entries already exist — they stay)
- **~235 controls** stay in `control/` but get trimmed of org-identity fields and gain explicit `publishedBy:` and (where relevant) `authorizedBy:` cross-references
- **SecID schemas** (`registry-namespace.schema.json` + new type-specific schemas) get updates to support cross-type references

This is multi-week work. It needs phasing.

## Phasing

### Phase 0 — Schema design (≈ 1 week, no migration)

**Goal:** decide the structural shape so all subsequent phases are mechanical.

- Define the JSON Schema for `entity/<path>.json` records. Inherit most fields from the current namespace schema (`official_name`, `common_name`, `notes`, `urls`); drop `match_nodes`; add `authorizedBy:`, `subsidiaryOf:`, `succeeds:`, `succeededBy:`.
- Define the JSON Schema for `regulation/<path>.json`. Some `regulation/` files exist already — confirm the shape works for the migration. Add `appliesTo:` (entity/control SecIDs).
- Update `control/` namespace schema to *deprecate* org-identity fields (keep them temporarily for backwards-compat) and add required `publishedBy:` (entity SecID) and optional `authorizedBy:` (regulation SecID).
- Decide path conventions for `entity/` and `regulation/` records (likely mirror DNS-canonical the way `control/` does today).
- Decide citation-compatibility approach: existing `secid:control/x/y` URIs keep resolving; the resolver internally follows the publishing chain. No external breakage.

Deliverable: updated `schemas/` directory + a short ADR (`docs/adr/`) capturing the cross-reference field design.

### Phase 1 — Entity records (≈ 1 week, additive only)

**Goal:** create `entity/` records for every namespace, without yet touching `control/`.

- For each of the ~166 `control/<path>.json` files, generate a sibling `entity/<path>.json` with the org-identity fields lifted out. Match the path 1:1 (e.g., `control/in/gov/uidai.json` → `entity/in/gov/uidai.json`).
- Cyber-rating namespaces (BitSight, SecurityScorecard, UpGuard, CyberCube) become entity-only — they shouldn't have been in `control/` at all, since they don't catalogue any controls. Their `control/` files get a deprecation flag (`status: deprecated, succeeded_by: entity/...`).
- This is largely scriptable: a Python migration walks `registry/control/`, splits each file, writes the entity file, leaves the control file in place.

Deliverable: ~166 new `entity/` files. Existing citations unaffected.

### Phase 2 — Regulation records (≈ 1–2 weeks, research-heavy)

**Goal:** identify and document the major regulations behind current control programs.

This is the slowest phase because it requires actual legal knowledge per source:

- For each entity, identify the regulation(s) that create/authorize/bind it (where applicable). UIDAI ← Aadhaar Act; Banco Central do Brasil ← Brazilian central bank law; EPC ← PSD2; UK OBIE ← CMA Retail Banking Market Investigation Order 2017; ENISA ← Cybersecurity Act 2019; etc.
- Many existing `regulation/` entries already exist (GDPR, AI Act, PSD2, etc. were added in prior PRs). Audit and reuse rather than duplicate.
- Estimate: ~50–100 new `regulation/` records spanning EU directives, US federal acts, India statutes, financial-regulator acts in each major jurisdiction, healthcare regulations (HIPAA family), and identity-system acts.

Deliverable: ~50–100 new `regulation/` records with `appliesTo:` cross-references back to the relevant entities/controls.

### Phase 3 — Cross-reference backfill (≈ 1 week, mostly mechanical)

**Goal:** add `publishedBy:` and `authorizedBy:` to existing `control/` records.

- For each `control/<path>.json`, set `publishedBy: entity/<path>` (almost always the same path, just different type).
- For each control with a clear regulatory basis, set `authorizedBy: regulation/<...>`. This is partly mechanical (when `notes` text mentions the regulation explicitly) and partly judgment.
- Strip the org-identity fields from `control/` namespace files now that they live in `entity/`. Keep deprecation aliases until V2.

Deliverable: 235+ updated `control/` records with explicit cross-references.

### Phase 4 — Tooling & docs (≈ 1 week)

**Goal:** make the new shape discoverable and self-policing.

- Update SecID's `CLAUDE.md`, `README.md`, and `SPEC.md` with the three-type model.
- Add a validator (extending the existing schema validation) that flags `control/` records missing `publishedBy:`, or `entity/` records with broken `authorizedBy:` references.
- Update the resolver design notes for how to traverse cross-references.
- Document conventions for joint-publication cases (ISO/IEC 27001 → published by both ISO *and* IEC; ISA/IEC 62443 → both ISA and IEC; ISO/SAE 21434 → both ISO and SAE).

Deliverable: docs + validator + a clear path for future contributions.

### Phase 5 — Companion dataset-repo migration (separate effort, not blocking)

The `dataset-private-laws-regulations-standards` and `dataset-public-laws-regulations-standards` directory layouts mirror SecID's namespace paths today. If SecID grows `entity/` and refines `regulation/`, the dataset repos can mirror those too — but that's a separate plan since dataset content is independent of the registry.

## Migration Approach: Citation Compatibility

Existing citations (`secid:control/iso.org/27001@2022` etc.) must keep resolving forever. The resolver does the work:

- A citation `secid:control/iso.org/27001@2022` continues to resolve to the ISO 27001 control record.
- That record's `publishedBy: secid:entity/org/iso` enriches the response with publisher identity.
- A citation `secid:entity/org/iso` resolves to ISO the organization (a new identity that didn't exist before).
- A citation `secid:regulation/in/parliament/aadhaar-act-2016` resolves to the Aadhaar Act record.

No existing user breaks. New users gain three-way query capability.

## Risks

- **Effort.** Realistically ~5 weeks of focused work to do all four phases cleanly. Half-done is worse than not-started (creates ambiguity about which type to use).
- **Regulation accuracy.** Mis-citing a law or applying the wrong jurisdiction to a control is worse than no citation. Phase 2 needs careful review.
- **Joint-publication corner cases.** ISO/IEC, ISO/SAE, ISA/IEC, NIST-CISA joint publications. The schema needs `publishedBy:` as an array, not a scalar.
- **Subsidiary relationships.** DTCC has DTC, NSCC, FICC subsidiaries. NSPK runs Mir and SBP. Need `subsidiaryOf:`/`operates:` relationships in entity records.
- **Deprecation churn.** Some entries we've created (cyber-rating providers) shouldn't have been in `control/` at all. Migration is the right time to redirect them, but it adds review burden.

## Open Questions

1. **Do we want one `entity/` record per organization, or per legal-entity-subsidiary?** DTCC as a single entity vs. DTC + NSCC + FICC + DTCC-the-parent as four. Both are defensible; need to pick.
2. **Joint publications**: schema makes `publishedBy:` an array (cleaner) or a primary + secondary (more searchable)?
3. **Regulation scope**: should we add only regulations that *authorize* current controls, or also major regulations that *apply to* the cybersecurity domain at large (GDPR, AI Act, etc., regardless of whether we have a specific control record they back)?
4. **`succeeds:` / `succeededBy:` chains for replaced regulations**: how far back? PSD1 → PSD2 → PSD3 is one example; eIDAS 1 → eIDAS 2 is another.
5. **Joint regulator namespaces**: e.g., a control authored by both FCA and PRA in the UK. Multiple authorising entities? Multiple authorising regulations?
6. **What about controls with no authorising regulation?** Industry consortia like FIX Trading Community publish protocols without statutory basis. Leave `authorizedBy:` empty? Use a "industry-driven" marker?

## Recommendation

Proceed in the order above (Phase 0 → 4). Phase 0 alone is worth doing immediately even if Phases 1–4 are deferred — it captures the design and prevents further drift in new entries.

Phase 1 is the highest-leverage execution step: it's largely scriptable and unlocks the entity-namespace immediately, even before regulations are wired in.

For the dataset repos, the directory-layout mirror should follow SecID's lead — once `entity/` is established in SecID, the private and public dataset repos can grow `entity/` and `regulation/` directories the same way they have `control/` today.

---

## Related Existing Work

- The `control` registry — current state, all org-conflated content lives here
- Some `regulation/` records exist already (GDPR, PSD2, AI Act, DPDP, etc. from earlier PRs)
- `entity/` is fresh — nothing currently lives there
- See also: `docs/proposals/CAPABILITY-ARCHITECTURE.md`, `docs/proposals/METHODOLOGY-ARCHITECTURE.md` — similar architectural splits that have already gone through this kind of design exercise
