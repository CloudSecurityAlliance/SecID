# Design: SecID Overview Slide Deck

**Date:** 2026-03-09
**Status:** Approved
**Format:** HTML (reveal.js via CDN), self-contained single file
**Location:** `slides/secid-overview.html`

## Purpose

A dual-audience slide deck for internal CSA briefings and external community presentations. Primary goal: transfer the mental model of what SecID is, how it works, and why it matters. Secondary goal: SEO when published (SlideShare, Speaker Deck, SecID-Website).

## Audience

Both CSA leadership (justify investment, show ecosystem enablement) and external security community (practitioners, tool builders, potential contributors). Must be factually bulletproof — people will look for errors.

## Narrative Arc

Problem-first: Pain → What SecID is → How it works (mental model) → What it enables → Try/Integrate/Contribute

## Core Narratives

1. **Identify AND find** — SecID labels things and tells you where to find them. Finding eliminates ambiguity.
2. **PURL grammar + DNS namespaces** — familiar building blocks, DNS aids discovery, no new concepts.
3. **Registry links to everything** — easy to verify what you're talking about.
4. **Multiple views** — same CVE at Red Hat vs NIST vs MITRE. Same regulation in different languages. No ambiguity about which view.
5. **Human Directed, Agent Native, Human Legible** — the canonical CINO principle. API, MCP server, docs, SDKs.
6. **Easier to contribute than to keep your own notes** — file an issue, submit markdown notes, or go all the way with structured JSON.
7. **Phone book, not a new authority** — CVE stays CVE, ATT&CK stays ATT&CK. SecID connects them, doesn't compete.
8. **Cross-type query** — from one CVE to CWE to ATT&CK to controls in one traversal. The query nobody can do today.
9. **Why now / AI moment** — AI agents need structured, reliable access to security knowledge. MCP server makes this native.
10. **CAVEaT resurrection** — CAVEaT stalled partly because there was no identifier infrastructure. SecID unblocks it and other CSA programs.
11. **Federation** — organizations run private registries referencing the public one. Same model that made DNS and CVE's CNA program successful.

## Factual Corrections to Maintain

- CVE records CAN contain links — but it's ad-hoc with no centralized discovery
- AI agents CAN click through websites — but we want resolution to be fast, reliable, and structured
- "Human Directed, Agent Native, Human Legible" is the canonical slogan (not "AI-first, human-legible")
- Mention discoverability explicitly as the core pain point

## Slide-by-Slide Outline

### Slide 1: Title
**SecID: Label It. Find It. Use It.**
*A universal identifier for security knowledge*
Cloud Security Alliance | secid.cloudsecurityalliance.org

### Slide 2: The Problem
Security knowledge exists — discovering and navigating it is the hard part.

- CVE records can contain links, but it's ad-hoc — no centralized way to discover all views of a vulnerability across MITRE, NVD, Red Hat, GitHub
- Discoverability across databases (CVE → CWE → ATT&CK → NIST controls) is painful and fragile
- AI agents can click through websites, but we need resolution to be fast, reliable, and structured
- No one system makes it easy to discover connections between advisories, weaknesses, techniques, controls, and regulations

*Key message: The problem isn't that the knowledge doesn't exist — it's that there's no easy way to discover it, to navigate across it, and to link and enrich it.*

### Slide 3: What SecID Is
SecID is a phone book for security knowledge. It doesn't replace CVE, CWE, or ATT&CK — it connects them.

- One consistent format: `secid:advisory/mitre.org/cve#CVE-2024-1234`
- A registry that tells you where to find it (URLs, APIs, lookup patterns)
- Not a new authority — the identifiers come from their sources. SecID just indexes them.

### Slide 4: Mental Model Diagram
The "transfer your mental model" slide. Diagram showing:

```
SOURCES (publish security knowledge)
  MITRE, NIST, OWASP, Red Hat, ISO, ...
        │
        ▼
SecID REGISTRY
  7 types: advisory, weakness, ttp, control, regulation, entity, reference
  Each entry: namespace (DNS) + patterns + URLs
        │
        ▼
CONSUMERS
  Humans (website) | Software (API, SDKs) | AI Agents (MCP server)
```

Key message: Sources → Registry → Consumers. Three layers, one identifier format.

### Slide 5: Why This Design — Familiar Building Blocks
No new concepts to learn.

- **Package URL grammar** — millions of developers already know `pkg:type/namespace/name@version`
- **DNS namespaces** — `mitre.org`, `nist.gov` — globally unique, self-registering, aids discovery
- **Registry with URLs** — given a SecID, get back the URLs. Like DNS for security knowledge.

### Slide 6: Multiple Views of the Same Thing
One CVE, many perspectives:

```
secid:advisory/mitre.org/cve#CVE-2024-1234     → cve.org
secid:advisory/mitre.org/nvd#CVE-2024-1234     → nvd.nist.gov
secid:advisory/redhat.com/cve#CVE-2024-1234    → Red Hat's view
secid:advisory/github.com/advisories/ghsa#...   → GitHub's view
```

Same vulnerability. Different context. All findable. No ambiguity.
Also applies to: regulations in different languages, frameworks across versions.

### Slide 7: The Cross-Type Query
From one CVE to a complete security picture:

```
CVE-2021-44228 (Log4Shell)
  → CWE-502 (Deserialization weakness)
    → T1190 (Exploit Public-Facing Application)
      → NIST CSF PR.IP-12 (Implementation protection)
        → CCM IAM-12 (Cloud control)
```

Today: 5 databases, manual navigation. With SecID: one traversal.

### Slide 8: Human Directed. Agent Native. Human Legible.
The three-part principle:

- **Human Directed** — humans set goals, make strategic decisions, exercise judgment
- **Agent Native** — outputs designed for AI agents to consume and act on. MCP server = native tool access.
- **Human Legible** — structured so humans can verify the critical parts

| Audience | Interface |
|---|---|
| Humans | secid.cloudsecurityalliance.org |
| Software | REST API + SDKs |
| AI Agents | MCP Server |

Screenshot opportunity: AI agent using MCP to resolve a SecID.

### Slide 9: What SecID Enables at CSA

| Program | What SecID unblocks |
|---|---|
| CAVEaT 2.0 | CVE → Control mapping, machine-readable. Original stalled partly due to no identifier infrastructure. |
| Security Controls Catalog | Unified identifiers across CCM, AICM, third-party frameworks |
| STAR | Vendor/product/control assessment tracking |
| Mapping Pipeline | All cross-framework claims reference SecIDs |
| Valid-AI-ted | Regulation identifiers across jurisdictions |

### Slide 10: Easy to Contribute
Multiple ways in:

| Effort | What you do |
|---|---|
| Minimal | File a GitHub issue |
| Some | Submit a markdown file with research notes |
| Full | Submit a structured JSON registry file |

AI agents can contribute too. We meet you where you are.

### Slide 11: Federation
Your data, your rules. SecID is federated by design.

- Organizations run private registries referencing the public one
- Domain owners manage their own namespaces via DNS verification
- Private standards stay private; public references stay public
- Same identifier format everywhere

Key message: Scales because it doesn't require centralization. Same model as DNS and CVE's CNA program.

### Slide 12: Call to Action
**Try it → Integrate it → Contribute**

1. Try: secid.cloudsecurityalliance.org
2. Integrate: API and SDKs at github.com/CloudSecurityAlliance/SecID-Client-SDK
3. Contribute: found something missing? Add it — easier than keeping your own notes.

## Implementation Notes

- reveal.js via CDN (no build step, self-contained HTML)
- View locally with `open slides/secid-overview.html` or `python3 -m http.server`
- CSA branding can be applied via CSS overrides
- Diagrams as styled HTML/CSS within slides (no external image dependencies)
- ~12 slides, ~15-20 minute talk
