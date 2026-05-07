# Goals

What SecID is trying to achieve and how we'll know if it worked.

## Vision / North Star

SecID is the universal address book for security knowledge. Every meaningful artifact in the security ecosystem — a CVE, a CWE weakness, an ATT&CK technique, a NIST control, a regulation, a vendor advisory — has a single canonical reference that humans can read, AI agents can parse, and resolvers can convert to authoritative URLs. The fragmentation of security knowledge across dozens of databases, identifier formats, and APIs becomes navigable rather than blocking. The grammar is stable, the registry covers everything an analyst would reasonably reference, and federation lets organizations contribute their own data without a central gatekeeper.

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
