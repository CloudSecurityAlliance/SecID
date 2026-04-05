# ADR-001: Use Marp for Presentation Slides

**Status:** Accepted
**Date:** 2026-04-05
**Context:** SecID v1.0 released. Need presentation materials for multiple audiences (executives, practitioners, developers, contributors). Need consistent delivery across website, PDF downloads, and potentially PowerPoint.

## Decision

Use [Marp](https://marp.app/) (Markdown Presentation Ecosystem) for all SecID presentation slides, integrated with the existing Astro website via astro-marp.

## Context

SecID needs slide decks for:
- **Overview** — 5-minute "what is SecID" for executives/general audience
- **Technical deep dive** — API contract, MCP server, code examples for developers
- **Contributing** — how to add namespaces, capabilities, sources for the community
- **CSA integration** — how SecID fits with CCM, AICM, STAR, CAIQ for CSA members

Currently we have one markdown slide deck (`slides/secid-overview.md`) manually converted to PDF. No website integration, no consistent tooling, no theme.

## Options Considered

### Option A: Reveal.js + Astro
- **Pros:** Rich features (fragments, transitions, plugins), widely used, good Astro integration
- **Cons:** Heavier, more complex, requires JS knowledge to customize, overkill for reference decks

### Option B: Marp + Astro
- **Pros:** Markdown-native (write slides the same way we write everything else), outputs HTML + PDF + PPTX from same source, VS Code live preview, MIT licensed, CSS themes, code highlighting built in
- **Cons:** Less interactive than reveal.js, Mermaid diagram support is workaround-based not native

### Option C: Google Slides / PowerPoint
- **Pros:** Familiar, WYSIWYG, easy collaboration
- **Cons:** Not version-controlled, not markdown, can't integrate with website, binary files in git, drift from spec

### Option D: Plain HTML pages (no slide format)
- **Pros:** Simplest, just Astro pages
- **Cons:** Not presentable in meeting/conference context, can't download as PDF/PPTX

## Rationale

Marp wins because:

1. **Markdown-first** — slides are written in the same format as everything else in SecID. Version-controlled, diffable, reviewable in PRs.

2. **Multi-output** — same `.md` file produces HTML (website), PDF (download), and PPTX (for those who need it). Edit once, publish everywhere.

3. **Consistent theming** — one CSS theme file branded for CSA, applied to all decks.

4. **Low barrier** — anyone who can write markdown can write slides. VS Code extension provides live preview.

5. **Git-native** — slide source lives in the repo, changes tracked, no binary blobs.

6. **Astro integration** — astro-marp renders slides as website pages alongside the existing site.

We don't need reveal.js's rich interactivity. Our decks are reference material — text, code examples, diagrams, tables. Marp handles all of these well.

## Implementation

### Pipeline

```
slides/<deck>.md (Marp markdown with --- page breaks)
  ↓ astro-marp
website: /slides/<deck> (browsable HTML)
  ↓ marp-cli (build step)
slides/<deck>.pdf (downloadable PDF)
```

### Website integration

Add `/slides` route to the Astro site with an index listing all available decks. Each deck is a page. Link from the main navigation.

### Theme

Create a CSA-branded Marp theme (`slides/theme/csa.css`) with:
- CSA colors and logo
- Consistent typography
- Code block styling matching the main site
- Header/footer with SecID branding

### Planned decks

| Deck | Audience | Slides | Priority |
|------|----------|--------|----------|
| Overview | Executives, general | ~12 | High |
| Technical | Developers, integrators | ~20 | High |
| Contributing | Community | ~12 | Medium |
| CSA Integration | CSA members, CCSK students | ~15 | Medium |

### File structure

```
slides/
├── theme/
│   └── csa.css           # CSA-branded Marp theme
├── overview.md           # Executive overview deck
├── technical.md          # Developer/integrator deck
├── contributing.md       # Community contribution guide
├── csa-integration.md    # CSA-specific use cases
├── overview.pdf          # Generated PDF (gitignored or committed)
├── technical.pdf
├── ...
```

## Consequences

- All presentation content is markdown in git — reviewable, diffable, versionable
- PDF generation can be automated in CI
- Website gets a `/slides` section for free
- Non-technical team members may need to learn minimal Marp syntax (just `---` for page breaks and `<!-- _class: -->` for styling)
- Mermaid diagrams require workaround (render separately, embed as images) until Marp adds native support
- Slide design is constrained by CSS — no drag-and-drop layout like PowerPoint
