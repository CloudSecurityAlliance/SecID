# Naming Collisions in the Registry

This document consolidates known acronym / short-name collisions across SecID namespaces. Each collision is also noted in the `notes:` field of the relevant namespace files. Resolution is always by **canonical DNS namespace** — the acronym alone is never authoritative.

## The 5 known collisions

### OCC

| Namespace | Organization | Domain |
|---|---|---|
| `theocc.com` | **The Options Clearing Corporation** — US-registered options and derivatives clearing | `theocc.com` |
| (no namespace) | Office of the Comptroller of the Currency — US federal bank regulator | `occ.gov` |

The OCC bank regulator publishes its guidance via Treasury / federal channels (would land under `gov/occ.json` or similar if added). Distinct from `theocc.com`. Citation: always use the full namespace, e.g. `secid:control/theocc.com/member-security`.

### BSI

| Namespace | Organization | Domain |
|---|---|---|
| `bsigroup.com` | **British Standards Institution** — UK national standards body. Publishes BS standards (BS 10012, BS 65000, BS 7799). Paywalled. | `bsigroup.com` |
| `bsi.bund.de` | **Bundesamt für Sicherheit in der Informationstechnik (BSI Germany)** — German federal cybersecurity agency. Publishes IT-Grundschutz (free!), TR series, German eID specs. | `bsi.bund.de` |

Different countries, different organizations. The German BSI's IT-Grundschutz is freely downloadable; the UK BSI's BS standards are paywalled.

### AIA

| Namespace | Organization | Domain |
|---|---|---|
| `aia-aerospace.org` | **Aerospace Industries Association** — US aerospace and defense trade association. Publishes National Aerospace Standards (NAS series). | `aia-aerospace.org` |
| (not registered) | American Institute of Architects | `aia.org` |

If/when `aia.org` is added, it must use a different namespace path to avoid confusion. The aerospace association uses the disambiguated `aia-aerospace.org` to make the distinction explicit even in its own DNS.

### CSA

| Namespace | Organization | Domain |
|---|---|---|
| `csagroup.org` | **CSA Group** (Canadian Standards Association) — Canadian national standards body. Publishes electrical/mechanical/IT standards. Paywalled. | `csagroup.org` |
| `cloudsecurityalliance.org` | **Cloud Security Alliance** — non-profit publishing the CCM, AICM, CCSK body of knowledge. | `cloudsecurityalliance.org` |

Same three-letter acronym, completely unrelated organizations. The Canadian Standards Association is sometimes referred to as just "CSA" in Canadian electrical-trade contexts; Cloud Security Alliance is "CSA" in cloud-security contexts. Always cite by full DNS.

### ISA

| Namespace | Organization | What |
|---|---|---|
| `isa.org` | **International Society of Automation** | Joint publisher with IEC of the ISA/IEC 62443 OT-cybersecurity series |
| `enx.com` match_node `isa` | **ENX's "Information Security Assessment" (VDA-ISA)** | The control catalogue underpinning TISAX in German automotive |

Same three letters, different concepts. ISA-the-organization publishes 62443; ENX uses ISA as a product name (Information Security Assessment) abbreviating an entirely different phrase. Citation: `secid:control/isa.org/62443` vs. `secid:control/enx.com/isa`.

## Resolution principle

**The acronym is never authoritative; the full SecID namespace is.** This document exists to help humans / AI agents disambiguate when they encounter ambiguous shorthand in source material.
