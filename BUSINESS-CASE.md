# Business Case

## Executive summary

SecID is foundational infrastructure that makes every other piece of CSA's security knowledge work — controls (CCM/AICM), assessments (CAIQ/STAR), the CNA initiative, mappings between standards, training content, and Risk Rubric — interoperable, machine-readable, and AI-navigable using a single grammar. It positions CSA as the coordination layer for security identifiers, the same way PURL became the coordination layer for software identifiers. Building it costs incremental engineering effort (one Cloudflare Worker plus a registry of YAML files); not building it costs CSA the long-term position and forces every program to reinvent ad-hoc identifier schemes.

## Business benefit categories

This project's value tags (multiple apply):

- **Brand** — owning the universal-resolver layer for security knowledge is a durable, defensible position that strengthens CSA's reputation as ecosystem infrastructure rather than just a publisher of frameworks.
- **Market position** — there is no competing system. PURL solved this for software packages; nothing solved it for security knowledge. First-mover advantage is real and the ecosystem positioning compounds with adoption.
- **Synergy** — every active CSA program (CCM, AICM, CAIQ, STAR, CNA, Risk Rubric, training content, mapping work) gains capability through SecID. Replaces ad-hoc identifier conventions and spreadsheet-based mappings with machine-readable infrastructure.
- **Research / Exploration** — the Relationship Data Layer and Enrichment Data Layer are open research questions; we need running infrastructure (which v1.0 provides) to learn what works at scale.
- **Leadership direction** — Jim has consistently emphasized "tie SecID to concrete use cases" as a quality bar; the CEO mentions SecID-style infrastructure in talks; no specific deadline mandate, but ongoing executive interest.

Not directly applicable:

- **Revenue** — SecID is not a revenue product. It supports revenue products (RiskRubric assessments, training courses, sponsored research) by making them more capable.
- **Required / Compliance** — not a legal/regulatory mandate. CSA is choosing to build this; nobody is forcing us.

## Why now

The convergence of three trends makes 2026 the right window:

1. **AI agents need precise identifiers.** Natural-language descriptions of "the CVE that's like the one Red Hat patched last quarter" don't survive the round trip through an LLM. Stable, parseable identifiers do.
2. **Security knowledge fragmentation is getting worse, not better.** Every new initiative (AI vulnerabilities, supply-chain advisories, MCP server vulnerabilities) launches its own ID scheme. Without a coordination layer, every consumer pays the integration cost N times.
3. **CSA's own work demands it.** The CNA initiative, AICM, the Risk Rubric reboot, the CAVEaT 2.0 resurrection — all want to reference each other and the rest of the ecosystem cleanly. Doing this with bespoke spreadsheets is the friction we're already paying.

## Comparable precedent

PURL (Package URL) provides the closest analogue. Built by a small group, became a de facto standard for cross-referencing software packages, now embedded in SBOM formats (CycloneDX, SPDX) and security tooling (OSV, Grype, Trivy). The investment per organization to support PURL is small; the value across the ecosystem is large. SecID applies the same shape to a different domain.

## AI Enablement

Per the CINO operating model, this section captures how AI is integral to the project — not bolted on.

**SecID is built AI-first.** The primary consumer of registry data is an AI agent, not a human:

- Registry files are written for AI parsing (YAML frontmatter + structured JSON, with prose context blocks the AI can use to disambiguate)
- The MCP server at `secid.cloudsecurityalliance.org/mcp` exposes three tools (`resolve`, `lookup`, `describe`) that any MCP-capable agent can call
- The Client-SDK project's primary deliverable is *AI-readable instructions* for generating clients in any language — explicitly chosen over traditional SDKs

**Internal AI use:**

- Registry contributions are typically authored with AI assistance (the `registry-research` skill workflow, then `registry-formalization` for YAML→JSON)
- The `registry-validation` skill is the active linting layer
- Spec, RATIONALE, DESIGN-DECISIONS, and most prose content has been co-developed in conversation with AI agents using `CLAUDE.md`, `GEMINI.md`, `AGENTS.md` behavioral contracts
- Multi-round AI critique is used on architectural decisions (see DECISIONS.md across the ecosystem)

**Future AI dependence:**

- The Relationship Data Layer expects AI-generated relationship proposals (CCM↔NIST mappings authored at scale by AI, then human-reviewed)
- The Enrichment Data Layer expects AI-generated summaries, classifications, and cross-references
- Hyperscaler remediation mapping is feasible at scale only because AI can parse vendor docs and produce structured fix actions

Without AI, SecID's registry would be an artisanal hand-curated effort that can't keep up with the security ecosystem's growth rate. With AI, the registry can scale to thousands of namespaces and millions of relationship/enrichment records.

## Operational burden assessment

Honest accounting of what running this costs.

### What ongoing work this generates

- **Registry maintenance:** namespace additions and updates as the security ecosystem evolves. Cadence: ad-hoc, AI-assisted. Estimated burden: ~2-4 hours/week ongoing (Kurt, with AI assistance)
- **Live service operations:** monitoring resolver uptime, KV state, deploy chain. Cadence: passive (Cloudflare handles edge), active when the deploy chain breaks (see FRICTION-001)
- **Spec evolution:** quarterly review of edge cases, proposed extensions; semi-annual decision cadence on whether to ship
- **External engagement:** issue triage, contribution review, federation conversations with partners. Cadence: scales with adoption; currently low

### What this replaces

- Spreadsheet-based mapping work between standards (CCM↔NIST 800-53, etc.) — **substantial** ongoing burden today, becomes machine-readable once the Relationship Layer ships
- Ad-hoc reference formats across CSA documents and tools — small per-document but adds up
- Per-program identifier schemes that would otherwise be invented for the CNA, Risk Rubric, AICM, CAVEaT 2.0

### Net assessment

The operational burden is **less than what it replaces**. The burden also concentrates the work in one place (the registry) instead of spreading it across every program that needs to reference identifiers. Burden grows linearly with adoption; value grows super-linearly (network effects).

### Resource backups

State that requires recovery is documented in [SecID-Service/BACKUP-RESOURCES.md](../SecID-Service/BACKUP-RESOURCES.md). The registry itself (the most valuable artifact) is backed up by Git on GitHub plus the org-wide `CSA-Backups-GitHub` repo.

## Risks

- **Adoption risk.** SecID could fail to attract external adoption and remain a CSA-internal tool. Mitigation: deliberately PURL-compatible grammar lowers integration cost; federation model means we don't need to convince everyone, just enough.
- **Authority risk.** A larger organization (MITRE, NIST, OASIS) could launch a competing meta-identifier system and absorb the space. Mitigation: ship first, attract early consumers, position SecID as the coordination layer that *complements* their authority rather than competing.
- **Maintenance risk.** Registry curation could fall behind reality and degrade trust in the resolver. Mitigation: AI-assisted contribution workflow, self-service namespace model (see PARTICIPATION-MODEL.md proposal).
- **Operational risk.** Live service outages erode confidence. Mitigation: Cloudflare Workers (high-uptime by default), observability KV for post-hoc diagnosis, [OPERATIONAL-RESOURCES.md](../SecID-Service/OPERATIONAL-RESOURCES.md) keeps the operational picture current.
- **Scope-creep risk.** Pressure to add features that violate the "labeling and finding" boundary (e.g., turning SecID into a vulnerability database or a mapping authority). Mitigation: explicit non-goals in README and PRINCIPLES; the three-layer separation (Registry / Relationship / Data) is built into the architecture.

## Authority

- **Approval to build:** decided by Kurt as CINO; concept reviewed by Jim and the executive team
- **Approval for spec changes (post-1.0):** consensus among contributors; breaking changes require explicit go/no-go from CINO
- **Approval for federation governance:** open question — likely a working-group structure as adoption grows
