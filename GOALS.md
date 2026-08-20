# Goals

What SecID is trying to achieve and how we'll know if it worked.

## Vision / North Star

SecID is the universal address book for security knowledge. Every meaningful artifact in the security ecosystem — a CVE, a CWE weakness, an ATT&CK technique, a NIST control, a regulation, a vendor advisory — has a single canonical reference that humans can read, AI agents can parse, and resolvers can convert to authoritative URLs. The fragmentation of security knowledge across dozens of databases, identifier formats, and APIs becomes navigable rather than blocking. The grammar is stable, the registry covers everything an analyst would reasonably reference, and federation lets organizations contribute their own data without a central gatekeeper.

With SecID 2.0 the handle stops being only an address. Where licensing permits, resolving a SecID returns the content itself — structured, attributed, citable at the item level. Where licensing does not permit, it returns an honest account of how to obtain the material and what it will cost. Either way the answer is complete. With SecID 3.0 that corpus becomes something anyone can sync and run themselves — for privacy, for speed, or to layer their own private data alongside the public record.

## Near-term goals (now → 2026-Q3)

- **Repair the live deploy chain.** Registry contributions are not reaching production since 2026-04-30. Until this is fixed, every other piece of work has a smaller blast radius than it should. See [FRICTION-001](../SecID-Service/FRICTION/FRICTION-001.md) and [WAITING-FOR-001](../SecID-Service/WAITING-FOR/WAITING-FOR-001.md) in SecID-Service.
- **Land the 14 new CSAF advisory entries + format metadata fields** to the live resolver once the deploy chain is repaired.
- **Complete client SDK reference implementations** in the priority languages (Python, npm/TypeScript, Go) and verify the AI-generation instructions produce working clients in Rust, Java, C#.
- **Verify type-list consistency** across all four repos (SecID, SecID-Service, SecID-Server-API, SecID-Client-SDK) on every type addition. The current process is manual and the spec note in CLAUDE.md says CI/CD does not auto-detect.
- **Ship Course 1 (Introduction)** training materials in a deliverable form (self-paced or instructor-led pilot).

## Medium-term goals (2026-Q4 → 2027-Q1)

- **First production users beyond CSA.** Identify two or three external organizations actively using SecID in their tooling (vendor advisories, internal mappings, AI agents) and capture their feedback in concrete registry/spec issues.
- **Federation ready in practice.** At least one external organization runs a public SecID resolver registered in our namespace entries. The protocol works end-to-end, not just in design docs.
- **Self-service namespace contribution model live.** Organizations prove ownership of their namespace and gain CODEOWNERS-scoped write access — see [PARTICIPATION-MODEL.md](docs/proposals/PARTICIPATION-MODEL.md).
- **Compliance test suite operational.** A canonical test suite that any resolver implementation can run to claim conformance. Catches drift between SecID-Service (Cloudflare) and SecID-Server-API (Python/TypeScript) before it ships.
- **Relationship Data Layer V1 design locked.** Format, query API, federation model, vocabulary scope — published as a proposal with at least one prototype demonstrating CCM↔NIST 800-53 mappings.
- **Enrichment Data Layer V1 design locked.** Hyperscaler remediation mapping (AWS/Azure/GCP fix actions) is the first concrete enrichment shipped.

## SecID 2.0 goals — content and the tools that produce it

Three versions, three questions: **1.0** asks *where is it* (shipped), **2.0** asks *what is it*, **3.0** asks
*can I run it myself*. Outcomes only below; the lifecycle and publishing model are deliberately unsettled
(see [docs/project/TODO.md](docs/project/TODO.md)) and will be answered by building.

- **A SecID returns the content, not just a link.** Where redistribution is permitted, resolution yields structured,
  attributed text addressable at the subpath level — an article, a control, a term — rather than a URL to a PDF.
- **What we cannot serve, we explain.** Licensed and restricted material carries metadata, acquisition instructions,
  and an access or purchase route. A source we may not redistribute is a documented state, never a silent gap.
- **Acquisition is recorded knowledge.** Whether a source needs a browser, an account, or in-country access; how fast
  it changes and in what way; whether its identifiers are stable across versions. Today this lives in people's heads.
- **We build tools that build extractors.** The deliverable is a toolchain, not a pile of one-off scripts. Most sources
  are extracted once and never again, so what compounds is the tooling that makes the next source cheap.
- **Extraction is verifiable.** A contributor submits an extractor with their data and we can confirm the two agree.
  Identifiers, structure, and normative text must match exactly; formatting need not. Where AI is in the path,
  extractions are attested against invariants rather than reproduced, and labelled as such.
- **CSA's own data consolidates.** The one-off dataset repositories migrate into the SecID data repositories or get an
  explicit disposition, so there is one way to find CSA security data rather than a dozen.
- **Coverage is global and its gaps are visible.** Measured per jurisdiction — which countries have their cyber
  authority, data protection authority, financial regulator, and CERT registered — so absence is a stated result.

### What 2.0 creates

| Repository | Purpose |
|---|---|
| `SecID-Data-{International, North-America, Latin-America, Europe, Asia, Middle-East, Africa, Oceania}` | Extracted content, sharded by the authority behind it |
| `SecID-Data-Staging` | Acquired but not yet classified; everything here has an exit |

Object storage carries what git should not: R2 for serving source originals and extraction artifacts, S3 with
requester-pays for bulk and archival access.

## SecID 3.0 goals — run it yourself

Everything in 2.0 assumes a hosted resolver. 3.0 removes that assumption.

- **Sync what you need, not everything.** Clone the regions you care about plus the global bodies. Nobody should have
  to sync the world to work in their own jurisdiction.
- **Stay current without effort.** An update mechanism that is incremental, integrity-checked, and version-pinnable.
- **Comprehensive local search.** Full text over content, semantic and vector search, cross-document ranking — over the
  corpus you hold. The hosted service stays deliberately basic; this is what running your own buys you.
- **Survive outages and latency.** A caching layer, so a local resolver is fast and keeps working when upstream does not.
- **Layer your own data on top.** Private, internal, or purchased content resolving alongside public content.
- **Serve what CSA cannot publish.** Restricted material — ISO standards and similar — in identically-named private
  repositories under `CloudSecurityAlliance-Internal`, served by an internal resolver that is the same software pointed
  at different repositories, not a second system.
- **Keep the demand signal without the surveillance.** Local resolvers optionally report *misses only* — searched for,
  not found — which is what drives registry growth and reveals nothing about what an organization holds.

## Long-term goals (2027+)

- **SecID is the default cross-reference format** in security tooling, the same way PURL became default for software identification. New databases launch with SecID-compatible identifiers from day one.
- **Relationship + Enrichment layers in production** with real consumers — the CNA initiative is filing CSA-issued CVEs that reference SecIDs in their advisories; CSA mapping work is published as relationship data rather than spreadsheets; Risk Rubric labels its findings with SecIDs.
- **Multi-organization federation at scale** — MITRE, NIST, hyperscalers, and security vendors run their own resolvers; SecID becomes a coordinated identifier layer rather than a CSA-hosted service.
- **Tooling ecosystem** — IDE plugins, CLI tools, AI agents, security analytics platforms all natively understand SecID syntax.

## Success criteria

Concrete, observable signals that the project worked:

| Signal | Measure |
|---|---|
| Live resolver uptime | ≥99.5% over rolling 90 days |
| Registry coverage | 1,000+ namespaces by 2027-Q2; <5% of common security identifiers in active use that have no SecID resolver |
| External adoption | 5+ external organizations actively using SecID in production tooling, identifiable in commits, issues, or public forums |
| AI-agent integration | SecID MCP server is one of the top 50 most-used remote MCP servers (per Anthropic / Cloudflare directories) |
| Federation | 3+ organizations run public SecID resolvers registered in CSA's namespace entries |
| Compliance test suite | Used by at least one non-CSA resolver implementation |
| Stable spec | Zero breaking changes to the v1.0 grammar after 2027-Q1 |
| Relationship + Enrichment layers | First production consumer outside CSA itself |
| Content served, not just linked | Every document-bearing namespace either serves structured content or states why it cannot |
| Jurisdictional coverage | Every country with a national cyber authority has it registered; Africa, Latin America, and the Middle East no longer under-represented |
| Verified extraction | Contributed extractions pass conformance automatically; every stored extraction is labelled `reproduced` or `attested` |
| Dataset consolidation | The one-off dataset repositories are retired or have a documented disposition |
| Extractor toolchain | A new source can be taken from discovery to verified structured content without writing bespoke tooling |
| Local resolvers in use (3.0) | Organizations run their own synced resolver in production, including at least one that never queries the hosted service |
| Private tier live (3.0) | CSA serves its restricted corpus internally using the same software as the public resolver |

Goals expressed as outcomes, not procedures. An AI agent or contributor with the *intent* can adapt to changing conditions; one with only a checklist cannot.

## Stakeholder mapping

Following the CINO project goals template, organized by who benefits and what they care about.

### CSA goals

- **Foundational infrastructure for the CNA initiative.** SecID is the meta-identifier layer that makes the CSA CNA's work composable with the rest of the ecosystem (CWE, ATT&CK, vendor advisories).
- **Brand and market position.** Owning the universal-resolver layer for security knowledge is a durable position no other organization is competing for. Mirrors PURL's role for software but for security.
- **Synergy across CSA programs.** CCM/AICM, AICM-CAIQ, STAR, the CNA, Risk Rubric, training content — all benefit from referenceable, machine-readable identifiers.

### Community goals

- **Lower the cost of cross-referencing.** Researchers, vendors, and analysts spend less time writing prose to describe "this CVE in Red Hat's tracker as fixed by RHSA-XXXX" and more time doing analysis.
- **AI tooling that actually works.** Agents can navigate security knowledge with precise handles instead of guessing from natural language descriptions.
- **No new authority.** SecID doesn't try to replace MITRE, NIST, or anyone else. The community keeps its existing authorities; SecID just makes them interoperable.

### Partner goals

- **MITRE.** SecID gives a clean way to reference MITRE programs (CVE, CWE, ATT&CK, CAPEC) alongside other authorities without redefining MITRE's identifiers.
- **NIST.** Same — SecID references NIST CSF, 800-53, AI RMF using NIST's own naming.
- **Hyperscalers (AWS/Azure/GCP).** The Enrichment Layer's hyperscaler remediation mapping turns vendor-specific fix actions into machine-readable resolutions of generic SecIDs.
- **Vendors with security advisories.** Self-service namespace contribution lets vendors maintain their own SecID entries.

### Shared goals

- **Stability of v1.0.** Anyone investing in SecID tooling needs confidence the grammar won't change. The spec is frozen for v1.0.
- **Federation-ready protocol.** No single organization, including CSA, has to be the single source of truth at scale.
- **Open licensing.** CC0 on the spec, registry, and reference implementations means no licensing friction for any consumer.
