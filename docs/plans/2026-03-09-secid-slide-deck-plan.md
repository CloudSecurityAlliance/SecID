# SecID Overview Slide Deck Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a 12-slide reveal.js HTML presentation explaining SecID for internal CSA and external community briefings.

**Architecture:** Single self-contained HTML file using reveal.js 5.2.1 via jsDelivr CDN. No build step. All diagrams are styled HTML/CSS (no external images except optional MCP screenshot). Clean, professional styling with minimal custom CSS.

**Tech Stack:** reveal.js 5.2.1 (CDN), HTML5, inline CSS

**Design doc:** `docs/plans/2026-03-09-secid-slide-deck-design.md`

---

### Task 1: Create slides directory and scaffold HTML file

**Files:**
- Create: `slides/secid-overview.html`

**Step 1: Create the directory**

```bash
mkdir -p slides
```

**Step 2: Write the scaffold HTML file**

Create `slides/secid-overview.html` with reveal.js boilerplate:

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SecID: Label It. Find It. Use It.</title>
    <meta name="description" content="SecID — A universal identifier for security knowledge. Cloud Security Alliance.">
    <meta name="author" content="Cloud Security Alliance">

    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reset.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.min.css">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/theme/white.min.css">

    <style>
        :root {
            --r-heading-color: #1a1a2e;
            --r-main-color: #333;
            --r-link-color: #2563eb;
            --r-heading-font: system-ui, -apple-system, sans-serif;
            --r-main-font: system-ui, -apple-system, sans-serif;
            --r-code-font: 'SF Mono', 'Fira Code', monospace;
        }
        .reveal h1 { font-size: 2.2em; }
        .reveal h2 { font-size: 1.6em; color: var(--r-heading-color); }
        .reveal h3 { font-size: 1.2em; }
        .reveal .subtitle { font-size: 0.9em; color: #666; margin-top: 0.5em; }
        .reveal .key-message {
            background: #f0f4ff;
            border-left: 4px solid #2563eb;
            padding: 0.8em 1.2em;
            margin: 1em 0;
            font-style: italic;
            font-size: 0.85em;
            text-align: left;
        }
        .reveal code {
            background: #f3f4f6;
            padding: 0.15em 0.4em;
            border-radius: 4px;
            font-size: 0.85em;
        }
        .reveal pre code {
            background: #1a1a2e;
            color: #e2e8f0;
            padding: 1em;
            border-radius: 8px;
            font-size: 0.55em;
            line-height: 1.5;
        }
        .reveal table {
            font-size: 0.7em;
            margin: 0.5em auto;
        }
        .reveal table th {
            background: #1a1a2e;
            color: white;
            padding: 0.5em 1em;
        }
        .reveal table td {
            padding: 0.4em 1em;
            border-bottom: 1px solid #e5e7eb;
        }
        .reveal ul { text-align: left; font-size: 0.85em; }
        .reveal li { margin-bottom: 0.4em; }
        .reveal .diagram-box {
            background: #f8fafc;
            border: 2px solid #e2e8f0;
            border-radius: 12px;
            padding: 1em 1.5em;
            margin: 0.5em auto;
            max-width: 700px;
            text-align: center;
        }
        .reveal .diagram-box .layer-label {
            font-weight: bold;
            font-size: 0.75em;
            color: #64748b;
            text-transform: uppercase;
            letter-spacing: 0.05em;
        }
        .reveal .diagram-box .layer-content {
            font-size: 0.8em;
            color: #334155;
            margin: 0.3em 0;
        }
        .reveal .diagram-arrow {
            font-size: 1.5em;
            color: #2563eb;
            margin: 0.2em 0;
        }
        .reveal .cta-step {
            display: flex;
            align-items: baseline;
            gap: 0.5em;
            margin: 0.6em 0;
            font-size: 0.85em;
            text-align: left;
        }
        .reveal .cta-number {
            background: #2563eb;
            color: white;
            border-radius: 50%;
            width: 1.5em;
            height: 1.5em;
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: bold;
            font-size: 0.9em;
            flex-shrink: 0;
        }
        .reveal .org-name {
            font-size: 0.7em;
            color: #666;
            margin-top: 1em;
        }
    </style>
</head>
<body>
    <div class="reveal">
        <div class="slides">
            <!-- Slides will be added in subsequent tasks -->
        </div>
    </div>

    <script src="https://cdn.jsdelivr.net/npm/reveal.js@5.2.1/dist/reveal.min.js"></script>
    <script>
        Reveal.initialize({
            hash: true,
            slideNumber: true,
            transition: 'fade',
            transitionSpeed: 'fast',
            center: true,
            width: 1200,
            height: 700
        });
    </script>
</body>
</html>
```

**Step 3: Verify it opens in a browser**

```bash
open slides/secid-overview.html
```

Expected: blank reveal.js presentation loads with no errors.

**Step 4: Commit**

```bash
git add slides/secid-overview.html
git commit -m "Scaffold reveal.js slide deck for SecID overview"
```

---

### Task 2: Add slides 1-3 (Title, Problem, What SecID Is)

**Files:**
- Modify: `slides/secid-overview.html` (inside `<div class="slides">`)

**Step 1: Add the three opening slides**

Replace the `<!-- Slides will be added in subsequent tasks -->` comment with slides 1-3.

**Slide 1 — Title:**
```html
<section>
    <h1>SecID</h1>
    <h2>Label It. Find It. Use It.</h2>
    <p class="subtitle">A universal identifier for security knowledge</p>
    <p class="org-name">Cloud Security Alliance &bull; secid.cloudsecurityalliance.org</p>
</section>
```

**Slide 2 — The Problem:**
```html
<section>
    <h2>The Problem</h2>
    <p class="subtitle">Security knowledge exists &mdash; discovering and navigating it is the hard part</p>
    <ul>
        <li>CVE records can contain links, but it&rsquo;s ad-hoc &mdash; no centralized way to <strong>discover</strong> all views of a vulnerability across MITRE, NVD, Red Hat, GitHub</li>
        <li>Navigating from CVE &rarr; CWE &rarr; ATT&amp;CK &rarr; NIST controls is painful and fragile</li>
        <li>AI agents can browse websites, but we need resolution to be <strong>fast, reliable, and structured</strong></li>
        <li>No one system makes it easy to discover connections between advisories, weaknesses, techniques, controls, and regulations</li>
    </ul>
    <div class="key-message">
        The problem isn&rsquo;t that the knowledge doesn&rsquo;t exist &mdash; it&rsquo;s that there&rsquo;s no easy way to <strong>discover</strong> it, to <strong>navigate</strong> across it, and to <strong>link and enrich</strong> it.
    </div>
</section>
```

**Slide 3 — What SecID Is:**
```html
<section>
    <h2>What SecID Is</h2>
    <p class="subtitle">A phone book for security knowledge</p>
    <ul>
        <li><strong>One consistent format</strong> to reference anything:<br>
            <code>secid:advisory/mitre.org/cve#CVE-2024-1234</code></li>
        <li><strong>A registry</strong> that tells you where to find it &mdash; URLs, APIs, lookup patterns</li>
        <li><strong>Not a new authority</strong> &mdash; identifiers come from their sources. SecID indexes them.</li>
    </ul>
    <div class="key-message">
        We don&rsquo;t replace CVE, CWE, or ATT&amp;CK &mdash; we connect them.
    </div>
</section>
```

**Step 2: Open in browser, verify all 3 slides render**

```bash
open slides/secid-overview.html
```

Expected: 3 slides, arrow-key navigation works, text readable, key-message boxes styled.

**Step 3: Commit**

```bash
git add slides/secid-overview.html
git commit -m "Add title, problem, and what-SecID-is slides"
```

---

### Task 3: Add slide 4 (Mental Model Diagram)

**Files:**
- Modify: `slides/secid-overview.html` (add after slide 3)

**Step 1: Add the diagram slide**

This is the most important slide — it transfers the mental model. Uses styled HTML boxes and arrows rather than ASCII art or images.

```html
<section>
    <h2>How It Works</h2>
    <div class="diagram-box" style="background: #eef2ff; border-color: #818cf8;">
        <div class="layer-label">Sources</div>
        <div class="layer-content">MITRE &bull; NIST &bull; OWASP &bull; Red Hat &bull; ISO &bull; GitHub &bull; ...</div>
        <div style="font-size:0.7em; color:#64748b;">publish security knowledge</div>
    </div>
    <div class="diagram-arrow">&darr;</div>
    <div class="diagram-box" style="background: #f0fdf4; border-color: #4ade80;">
        <div class="layer-label">SecID Registry</div>
        <div class="layer-content" style="font-size:0.7em;">
            <code>advisory</code> &bull; <code>weakness</code> &bull; <code>ttp</code> &bull; <code>control</code> &bull; <code>regulation</code> &bull; <code>entity</code> &bull; <code>reference</code>
        </div>
        <div style="font-size:0.7em; color:#64748b;">namespace (DNS) + patterns + URLs</div>
    </div>
    <div class="diagram-arrow">&darr;</div>
    <div class="diagram-box" style="background: #fff7ed; border-color: #fb923c;">
        <div class="layer-label">Consumers</div>
        <div class="layer-content" style="font-size:0.75em;">
            Humans (website) &bull; Software (API, SDKs) &bull; AI Agents (MCP server)
        </div>
    </div>
    <div class="key-message">Sources &rarr; Registry &rarr; Consumers. Three layers, one identifier format.</div>
</section>
```

**Step 2: Open in browser, verify diagram renders clearly**

```bash
open slides/secid-overview.html
```

Expected: 3 colored boxes with arrows between them, all text readable, no overflow.

**Step 3: Commit**

```bash
git add slides/secid-overview.html
git commit -m "Add mental model diagram slide"
```

---

### Task 4: Add slides 5-7 (Design, Multiple Views, Cross-Type Query)

**Files:**
- Modify: `slides/secid-overview.html` (add after slide 4)

**Step 1: Add three content slides**

**Slide 5 — Why This Design:**
```html
<section>
    <h2>Familiar Building Blocks</h2>
    <p class="subtitle">No new concepts to learn</p>
    <table>
        <thead>
            <tr><th>Design Choice</th><th>Why</th></tr>
        </thead>
        <tbody>
            <tr>
                <td><strong>Package URL grammar</strong></td>
                <td>Millions of developers already know <code>pkg:type/namespace/name@version</code></td>
            </tr>
            <tr>
                <td><strong>DNS namespaces</strong></td>
                <td><code>mitre.org</code>, <code>nist.gov</code> &mdash; globally unique, self-registering, aids discovery</td>
            </tr>
            <tr>
                <td><strong>Registry with URLs</strong></td>
                <td>Given a SecID, get back URLs where that thing lives. Like DNS for security knowledge.</td>
            </tr>
        </tbody>
    </table>
    <div class="key-message">
        The innovation is applying proven infrastructure to security knowledge &mdash; not inventing new infrastructure.
    </div>
</section>
```

**Slide 6 — Multiple Views:**
```html
<section>
    <h2>Multiple Views of the Same Thing</h2>
    <p class="subtitle">One CVE, many perspectives</p>
    <pre><code>secid:advisory/mitre.org/cve#CVE-2024-1234      &rarr; cve.org (canonical record)
secid:advisory/mitre.org/nvd#CVE-2024-1234      &rarr; nvd.nist.gov (CVSS, CPE enrichment)
secid:advisory/redhat.com/cve#CVE-2024-1234     &rarr; Red Hat (affected products, patches)
secid:advisory/github.com/advisories/ghsa#...    &rarr; GitHub (affected repos, PRs)</code></pre>
    <p style="font-size:0.8em;">Same vulnerability. Different context. All findable. No ambiguity about which view.</p>
    <p style="font-size:0.75em; color:#666;">Also applies to: regulations in different languages, frameworks across versions, standards across jurisdictions.</p>
</section>
```

**Slide 7 — Cross-Type Query:**
```html
<section>
    <h2>The Cross-Type Query</h2>
    <p class="subtitle">From one CVE to a complete security picture</p>
    <pre><code>CVE-2021-44228 (Log4Shell)
  &rarr; CWE-502  (Deserialization weakness)
    &rarr; T1190   (Exploit Public-Facing Application)
      &rarr; NIST CSF PR.IP-12  (Implementation protection)
        &rarr; CCM IAM-12  (Cloud control)</code></pre>
    <p style="font-size:0.85em;"><strong>Today:</strong> 5 databases, manual navigation, hope you don&rsquo;t miss a connection.</p>
    <p style="font-size:0.85em;"><strong>With SecID:</strong> one traversal across the security knowledge graph.</p>
    <div class="key-message">This is the query nobody can do today. SecID makes it possible.</div>
</section>
```

**Step 2: Open in browser, verify slides 5-7 render**

```bash
open slides/secid-overview.html
```

Expected: table on slide 5, code blocks on slides 6-7, key messages visible.

**Step 3: Commit**

```bash
git add slides/secid-overview.html
git commit -m "Add design, multiple views, and cross-type query slides"
```

---

### Task 5: Add slides 8-9 (Agent Native, CSA Programs)

**Files:**
- Modify: `slides/secid-overview.html` (add after slide 7)

**Step 1: Add two slides**

**Slide 8 — Human Directed. Agent Native. Human Legible:**
```html
<section>
    <h2>Human Directed. Agent Native. Human Legible.</h2>
    <ul>
        <li><strong>Human Directed</strong> &mdash; humans set goals, make strategic decisions, exercise judgment</li>
        <li><strong>Agent Native</strong> &mdash; outputs designed for AI agents to consume and act on. MCP server = native tool access.</li>
        <li><strong>Human Legible</strong> &mdash; structured so humans can verify the critical parts</li>
    </ul>
    <table>
        <thead>
            <tr><th>Audience</th><th>Interface</th></tr>
        </thead>
        <tbody>
            <tr><td>Humans</td><td>secid.cloudsecurityalliance.org &mdash; interactive resolver</td></tr>
            <tr><td>Software</td><td>REST API + SDKs (Python, npm, Go, Rust, Java, C#)</td></tr>
            <tr><td>AI Agents</td><td>MCP Server &mdash; native tool access to the full registry</td></tr>
        </tbody>
    </table>
</section>
```

**Slide 9 — What SecID Enables at CSA:**
```html
<section>
    <h2>What SecID Enables at CSA</h2>
    <p class="subtitle">Infrastructure for the next generation of security programs</p>
    <table>
        <thead>
            <tr><th>Program</th><th>What SecID Unblocks</th></tr>
        </thead>
        <tbody>
            <tr><td><strong>CAVEaT 2.0</strong></td><td>CVE &rarr; Control mapping becomes machine-readable. Original stalled partly due to no identifier infrastructure.</td></tr>
            <tr><td><strong>Security Controls Catalog</strong></td><td>Unified identifiers across CCM, AICM, and third-party frameworks</td></tr>
            <tr><td><strong>STAR</strong></td><td>Vendor/product/control assessment tracking with stable references</td></tr>
            <tr><td><strong>Mapping Pipeline</strong></td><td>All cross-framework mapping claims reference SecIDs</td></tr>
            <tr><td><strong>Valid-AI-ted</strong></td><td>Regulation identifiers across jurisdictions for compliance</td></tr>
        </tbody>
    </table>
    <div class="key-message">SecID is infrastructure. These programs are the products built on it.</div>
</section>
```

**Step 2: Open in browser, verify slides 8-9 render**

```bash
open slides/secid-overview.html
```

Expected: bullet list + table on slide 8, table with 5 rows on slide 9.

**Step 3: Commit**

```bash
git add slides/secid-overview.html
git commit -m "Add agent-native and CSA programs slides"
```

---

### Task 6: Add slides 10-12 (Contribute, Federation, CTA)

**Files:**
- Modify: `slides/secid-overview.html` (add after slide 9)

**Step 1: Add final three slides**

**Slide 10 — Easy to Contribute:**
```html
<section>
    <h2>Easy to Contribute</h2>
    <p class="subtitle">We meet you where you are</p>
    <table>
        <thead>
            <tr><th>Effort</th><th>What You Do</th></tr>
        </thead>
        <tbody>
            <tr><td><strong>Minimal</strong></td><td>File a GitHub issue: &ldquo;this source is missing&rdquo;</td></tr>
            <tr><td><strong>Some</strong></td><td>Submit a markdown file with your research notes</td></tr>
            <tr><td><strong>Full</strong></td><td>Submit a structured JSON registry file, ready to merge</td></tr>
        </tbody>
    </table>
    <p style="font-size:0.8em;">AI agents can contribute too &mdash; automated research, verification, and freshness checks.</p>
    <div class="key-message">Contributing is less work than keeping your own notes. If you found it, telling us is easier than bookmarking it.</div>
</section>
```

**Slide 11 — Federation:**
```html
<section>
    <h2>Federation</h2>
    <p class="subtitle">Your data, your rules</p>
    <ul>
        <li>Organizations run <strong>private registries</strong> that reference the public one</li>
        <li>Domain owners manage their own namespaces via <strong>DNS verification</strong></li>
        <li>Private standards stay private; public references stay public</li>
        <li>Same identifier format everywhere &mdash; public, organizational, personal</li>
    </ul>
    <div class="key-message">SecID scales because it doesn&rsquo;t require centralization. The same model that made DNS and CVE&rsquo;s CNA program successful.</div>
</section>
```

**Slide 12 — Call to Action:**
```html
<section>
    <h2>Try It &rarr; Integrate It &rarr; Contribute</h2>
    <div style="max-width: 600px; margin: 0 auto;">
        <div class="cta-step">
            <span class="cta-number">1</span>
            <span><strong>Try it:</strong> secid.cloudsecurityalliance.org &mdash; paste any CVE, CWE, or ATT&amp;CK ID</span>
        </div>
        <div class="cta-step">
            <span class="cta-number">2</span>
            <span><strong>Integrate it:</strong> REST API, MCP server, SDKs for Python, npm, Go, Rust, Java, C#</span>
        </div>
        <div class="cta-step">
            <span class="cta-number">3</span>
            <span><strong>Contribute:</strong> Found something missing? Add it &mdash; easier than keeping your own notes</span>
        </div>
    </div>
    <p style="margin-top: 1.5em;">
        <code>github.com/CloudSecurityAlliance/SecID</code>
    </p>
    <p class="org-name">Cloud Security Alliance</p>
</section>
```

**Step 2: Open in browser, verify all 12 slides render and navigate**

```bash
open slides/secid-overview.html
```

Expected: 12 slides total, arrow navigation through all, CTA steps have numbered circles.

**Step 3: Commit**

```bash
git add slides/secid-overview.html
git commit -m "Add contribute, federation, and call-to-action slides"
```

---

### Task 7: Final review and polish

**Files:**
- Modify: `slides/secid-overview.html` (if needed)

**Step 1: Full run-through in browser**

```bash
open slides/secid-overview.html
```

Check all 12 slides for:
- [ ] Text fits on screen (no overflow/scroll)
- [ ] Code blocks are readable
- [ ] Tables render cleanly
- [ ] Key message boxes are consistently styled
- [ ] Diagram boxes and arrows align properly
- [ ] No HTML entity rendering issues
- [ ] Slide numbers show in corner

**Step 2: Test presenter view**

Press `S` in the browser to open speaker notes view. Verify it works (even though we have no speaker notes — just confirm the feature loads).

**Step 3: Fix any issues found**

Adjust font sizes, spacing, or content if anything overflows or looks wrong.

**Step 4: Commit final polish (if changes were made)**

```bash
git add slides/secid-overview.html
git commit -m "Polish slide deck styling and layout"
```

---

### Task 8: Commit design doc

**Files:**
- Existing: `docs/plans/2026-03-09-secid-slide-deck-design.md`
- Existing: `docs/plans/2026-03-09-secid-slide-deck-plan.md`

**Step 1: Commit both plan documents**

```bash
git add docs/plans/2026-03-09-secid-slide-deck-design.md docs/plans/2026-03-09-secid-slide-deck-plan.md
git commit -m "Add design doc and implementation plan for SecID slide deck"
```
