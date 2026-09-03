# SecID 2.0 / 3.0 Program Plan

**The index of everything the 2.0 and 3.0 work needs.** One line per item, pointing at where the detail lives.
Nothing here is a commitment to a date; this exists so that work already thought through does not get lost.

- **1.0** — *Where is it?* Grammar, registry, URL resolution. **Shipped.**
- **2.0** — *What is it?* The content itself, and the tooling that produces it.
- **3.0** — *Can I run it myself?* Sync, caching, comprehensive local search, private deployment.

Detail for research items lives in [TODO.md](TODO.md); decisions live in [DECISIONS.md](../../DECISIONS.md);
outcomes live in [GOALS.md](../../GOALS.md) and [ROADMAP.md](../../ROADMAP.md).

## Decisions already made

| Decision | Recorded |
|---|---|
| v2.0 serves content; the registry format is unchanged | ADR-010 |
| Data shards by region, keyed by the authority behind the material | ADR-011 |
| Capability data shards by vendor, not region (`SecID-Data-Vendor`) | ADR-011 |
| Extraction equivalence is tiered; extractions are *reproduced* or *attested* | ADR-012 |
| Structured text in git; originals and extraction artifacts in R2, S3 requester-pays for bulk | ROADMAP |
| Data repositories are CC0, with per-source sub-licences | ROADMAP |
| Type list stays frozen at ten; new categories are `subtype:` | ROADMAP, TYPES-AND-SUBTYPES |
| `reference` is the catch-all, by design | CLASSIFY.md |
| Publisher packaging beats object ontology (ATT&CK precedent) | CLASSIFY.md |
| Governance is Kurt Seifried; namespace disputes resolve at the DNS registry | *(not yet written down — see W1)* |
| Vendor-published aliases are data, not relationships | *(not yet written down — see W1)* |
| Search is tiered: anonymous / gated / local | TODO "Search tiering" |
| Local-first is a first-class mode | Principle 11 |
| Verifiable, not merely asserted | Principle 12 |
| Sustainable by design | Principle 13 |
| Backward compatibility across versions is not a goal | *(not yet written down — see W1)* |

## Open questions

| Question | Blocks | Tracked in |
|---|---|---|
| Data lifecycle, versioning, refresh, publishing | v2 build sequencing | TODO "v2 — data lifecycle" |
| Does an executable type (`detection`/`check`) earn a slot? | Corpus expansion | TODO "Vocabulary survey" |
| Does an evidential type (`attestation`) earn one? | Same | Same |
| Does `cti` survive as a type, or dissolve into `entity` + `advisory` subtypes? | Same | Same |
| Where do benchmarks live — `control`, `methodology`, or `reference`? | `dataset` subtype | TYPES-AND-SUBTYPES |
| Vendor promotion threshold (entries before a vendor earns its own repo) | Vendor repo creation | ADR-011 |
| Private vocabulary naming and validation hooks | 3.0 private tier | TODO "Private types and subtypes" |
| Which facets to precompute for the free tier | Search tiering | TODO "Search tiering" |
| Ship embeddings, or generate locally? | 3.0 local search | TODO "Search tiering" |
| Data baked into images, or fetched on first run? | Distribution | TODO "Distribution formats" |

## Workstreams

### W1 — Documentation hygiene *(no dependencies; start anytime)*

A documentation sweep on 2026-08-20 found twelve state-drift items. All are objective corrections.

- ~~CLAUDE.md states **2,030 namespaces** twice in prose; actual is 2,130.~~ Numbers corrected; **the mechanism
  is still open** — `update-counts.sh` only edits between `REGISTRY-COUNTS` markers, so any prose count drifts
  silently. README.md:30 and GOALS.md carry the same exposure
- `CAPABILITY-TYPE.md` and `METHODOLOGY-TYPE.md` are marked "Research / proposal"; both types shipped
- `CONSORTIUM-AND-COORDINATOR-SUBTYPES.md` and `DISCLOSURE-TYPE-FIELDS.md` marked "Draft / discussion"; both landed
- Six proposals carry no status line at all
- `GOVERNANCE.md` does not exist but `GAPS.md` cites it as a resolution
- `CONCERNS.md` says the registry schema is unspecified; `schemas/registry-namespace.schema.json` exists
- "Resolution Instructions for Non-Deterministic Systems" is tracked in both `CONCERNS.md` and `TODO.md`
- CLAUDE.md's repository-structure listing omits `docs/proposals/` and `docs/research/`
- `AGENTS.md` names none of the ten types and does not link CLASSIFY.md
- `docs/future/V2-USE-CASES.md` describes a v2 that bundles relationships — contradicts the 2.0/3.0 split
- `.superpowers/sdd/` holds ~1.5 MB of `review-*.diff` build detritus
- `REGEX-ECMASCRIPT-MIGRATION-{PLAN,CHECKLIST}.md` describe a migration that was **cancelled**; the filenames mislead

Also in W1, three decisions from discussion that were never written down: **governance-by-DNS**, **aliases-as-data**,
and **backward compatibility is not a goal**.

**Prevention, not just correction:** a CI check that fails when a proposal is marked "Research / proposal" while its
type or subtype appears in live registry data would have caught four of the twelve.

### W2 — Documentation architecture *(before the repo split; W1 first)*

The test: **SecID owns what defines the system; everything else owns what instantiates it.** The line runs through
`registry/` itself — `registry/control.md` (what a control *is*) stays; the 242 control namespaces leave.

- Tag every document with its destination repository — SecID / Registry / Data / Service
- Archive: `docs/superpowers/`, `docs/project/csa/`, `docs/research/`, `V1-RELEASE-PLAN.md`, landed proposals
- Add a **reading path** to README (why → what → how to use → what exists → why decided → where going); keep the
  Q&A Document Map for lookup
- Decide whether `docs/parsers/` moves to the data repos — it is the prototype of per-source documentation

### W3 — Repository architecture and migration *(depends on W2 tagging)*

- Create the region repositories, `SecID-Data-Vendor`, and `SecID-Data-Staging`
- Migrate `dataset-public-laws-regulations-standards` (167 MB in git; originals already gitignored) and retire it
  behind a README pointing at successors
- Move originals and extraction images to R2; keep the existing S3 archive as requester-pays
- Break the registry out of SecID into its own repository, with the contribution tooling
- Record dispositions for the other dataset repositories: NVD/CPE/cvelistV5 upstream-only, papers later, entity crawl
  products stay whole, CSA internal content out of scope

### W4 — Content promotion *(can start in parallel with W3)*

`seed/` holds **2,610 researched rows** against 2,130 live namespaces — roughly one unpromoted source for every one
live. Dated 2026-03-06, so URLs need re-verification.

- **Start with `seed-certs.csv`** — 139 national CERTs into `disclosure` + the existing `coordinator` subtype. No
  decisions required, largest clean win, and it exercises the promotion pipeline on low-risk data
- Per-file triage for the remaining eighteen: which type, whether the *item* level is addressable or source-only,
  what the identifier shape is
- **Caution:** `seed-threatintel.csv` and `seed-malware-analysis.csv` are largely IOC feeds and sandboxes. The
  *source* is registerable; the individual URLs, hashes and IPs are not — that is the unbounded space the
  pattern-breadth gate exists to stop
- Country-tag the **327 doc-bearing `International` namespaces** that determine shard placement
- Close jurisdictional coverage gaps: **Africa** (16 namespaces, 3 countries), **Middle-East** (28, 6),
  **Latin-America** (11, essentially Brazil only)

### W5 — Vocabulary *(evidence from W4 and the survey)*

- Run the **vocabulary survey** — ~35 schemas and ontologies, what object types each defines, what has no home
- Add the 20 STIX object-type children to `reference/oasis-open.org/stix` — closed, enumerable, purely additive
- Tag the **72 untagged** company- and consortium-published entries in `control`/`methodology`
- Land the `reference` provenance subtypes: `paper`, `blog`, `presentation`, `report`; plus `format-spec` on the
  function axis. **Drop `documentation`** (duplicates `capability`); **defer `dataset`** (benchmark placement first)
- Decide the executable and evidential type questions on counted evidence

### W6 — Tooling *(depends on W3 repositories existing)*

- Tools that **build extractors**, not one-off extractions
- The conformance harness: tiered equivalence, `reproduced` vs `attested`, run against pinned R2 originals by hash
- **Sandbox contributor-supplied extractors from day one** — this is untrusted code execution triggered by pull
  request. No network, read-only input, resource caps, never `pull_request_target`, no secrets in scope
- Generalise link-rot monitoring beyond CNA data; let agents report rot via `submit_feedback`

### W7 — Distribution and 3.0 *(after W3 and W6)*

- Docker (multi-arch), locally runnable MCP server plus MCPB bundle, Terraform for Cloudflare, single static binary,
  Helm, docker-compose
- Sign images with cosign and publish an SBOM per artifact — SecID catalogues Sigstore, SLSA, in-toto, CycloneDX and
  SPDX, and should ship what it catalogues
- **Air-gapped tarball** — image, data, index, checksums, no network. The honest test of whether the corpus is
  portable, and a real capability for the government and critical-infrastructure audience
- Selective sync by region; incremental, integrity-checked, version-pinnable updates; caching layer
- Search tiering using CSA's existing audience model and the ADR-027 §9 error convention — do not invent a parallel scheme
- Private tier: identically-named repositories under `CloudSecurityAlliance-Internal`, served by the same software

## Sequencing

```
W1 documentation hygiene ──┐
                           ├──► W2 doc architecture ──► W3 repos + migration ──┬──► W6 tooling ──► W7 distribution
W4 content promotion ──────┘                                                    │
        └──► W5 vocabulary ◄─────────────────────────────────────────────────────┘
```

Three things can start immediately and block nothing: **W1** (objective corrections), **W4's `seed-certs` promotion**
(no decisions required), and the **vocabulary survey** (pure research, and it produces the evidence W5 needs).

## Explicitly not doing

- **IOCs and observables** — unbounded, no issuing authority, and catastrophic for pattern breadth
- **Software package identity** — PURL's job; SecID is deliberately PURL-compatible
- **Mirroring well-hosted upstreams** — NVD, CPE, cvelistV5 stay upstream-only
- **Individual people as records** — register the identity system (ORCID), never the individuals
- **Asserting threat attribution** — resolve the designator to what the source says; never adjudicate
- **Backward compatibility guarantees across major versions**
