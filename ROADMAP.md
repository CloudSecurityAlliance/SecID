# SecID Implementation Roadmap

**Current Version: 0.9 (Public Draft)**

This document describes what we're building, in what order, and why.

## Version 1.0 Goal: URL Resolution

**Given a SecID string, return the URL(s) where that resource can be found.**

This is the simplest useful thing SecID can do, and it's the foundation everything else builds on.

```
secid:advisory/mitre.org/cve#CVE-2024-1234
  → https://www.cve.org/CVERecord?id=CVE-2024-1234

secid:weakness/mitre.org/cwe#CWE-79
  → https://cwe.mitre.org/data/definitions/79.html

secid:control/nist.gov/800-53@r5#AC-1
  → https://csrc.nist.gov/projects/cprt/catalog#/cprt/framework/version/SP_800_53_5_1_1/home?element=AC-1
```

### Why Start Here?

URL resolution delivers immediate value with minimal complexity:

1. **Useful on day one** - People can start using SecIDs to link to security resources
2. **Tests the registry** - Every namespace must define resolution rules, validating the data model
3. **Foundation for everything else** - Relationships, overlays, and applications all need resolution
4. **Clear success criteria** - Either the URL works or it doesn't

### How Resolution Works

**Simple case (most namespaces):** String substitution. The registry file contains a URL template:

```yaml
# registry/advisory/org/mitre.md (cve source)
urls:
  lookup: "https://www.cve.org/CVERecord?id={id}"
```

Resolution: extract `CVE-2024-1234` from the subpath, substitute into template.

**Complex case (no direct URL):** Some resources don't have predictable URLs. For these, we provide search instructions that humans and AI agents can follow:

```yaml
# Example: a resource without direct linking
resolution:
  type: search
  instructions: "Search the vendor's security portal for the advisory ID"
  search_url: "https://example.com/security/search?q={id}"
```

## Version 1.0 Deliverables (In Priority Order)

| Priority | Deliverable | Why This Order |
|----------|-------------|----------------|
| **1** | **Registry data** | Foundation - libraries need data to resolve against |
| **2** | **Python library** | Security community standard; threat intel, SIEM, AI/ML pipelines |
| **3** | **npm/TypeScript library** | Web applications, CI/CD integrations, broad developer reach |
| **4** | **REST API** | Unlocks every other language without waiting for native libraries |
| **5** | **Go library** | Cloud-native security tools (Trivy, Grype, Falco), Kubernetes ecosystem |
| **6** | **Rust library** | Memory-safe systems tools, growing security tooling adoption |
| **7** | **Java library** | Enterprise SAST/DAST tools, legacy integration |
| **8** | **C#/.NET library** | Windows/enterprise ecosystem |

### Why This Order?

**Registry first** because everything depends on it. A library without data is useless.

**Python second** because the security community runs on Python. Threat intelligence platforms, SIEM integrations, vulnerability scanners, AI/ML pipelines - Python is the lingua franca.

**npm/TypeScript third** because it covers web applications and has the broadest developer reach. Security dashboards, CI/CD integrations, and developer tools often use JavaScript/TypeScript.

**REST API fourth** because it's a force multiplier. Once the API exists, any language can consume SecID - Ruby, PHP, shell scripts, anything that can make HTTP requests. This reduces pressure to ship every native library immediately.

**Go fifth** because cloud-native security infrastructure runs on Go. Tools like Trivy, Grype, and Falco would benefit from native SecID support, and Go is common for CLI tools and microservices.

**Rust, Java, C#/.NET later** because their communities can use the REST API until native libraries ship. These are important for completeness but not blockers for adoption.

## Vision

**A SecID isn't just an identifier - it's a handle that gives you everything you need to understand and work with security knowledge.**

Today, security data is fragmented. CVEs live in one place, CWEs in another, controls in spreadsheets, regulations in PDFs. Finding information requires knowing where to look. Understanding it requires domain expertise. Connecting it requires manual effort.

SecID changes this. When you have a SecID, you can:

1. **Find it** - Get the URL or search instructions
2. **Understand it** - Read a description of what it is
3. **Read it** - Get the actual content (where licensing permits)
4. **Interpret it** - Understand what the fields mean
5. **Use it** - Know what to do with this data
6. **Connect it** - See related concepts, mitigations, and examples

**This is AI-first infrastructure** - but not AI-only. The primary consumer is AI agents that need to navigate security knowledge autonomously. When an agent receives a SecID response, it should be self-describing - the agent knows what it has, how to interpret it, and what to do with it.

**Traditional tools are first-class consumers too.** SecID identifiers work in:
- **SIEMs and SOC platforms** - Correlate alerts across vulnerability, weakness, and technique taxonomies
- **GRC tools** - Map controls to regulations to compliance evidence
- **Vulnerability scanners** - Link findings to weaknesses, techniques, and remediations
- **SBOMs and VEX documents** - Reference advisories with consistent identifiers
- **Asset inventories** - Tag systems with applicable controls and regulations
- **Policy automation** - Define rules that reference specific controls or requirements

AI agents accelerate adoption because they can consume SecID immediately without organizational buy-in. But the long-term value is infrastructure that humans, traditional tools, and AI all use together.

We're building this in layers:
- **v1.0**: URL resolution + descriptions (where to find it, what it is)
- **v1.x**: Raw content with licensing (the actual text, properly attributed)
- **v2.x**: Metadata wrapper (interpretation and usage guidance for AI)
- **Future**: Relationships and overlays (connections and enrichment)

## What We're Building (Full Stack)

SecID isn't just a spec - it's a complete system for working with security knowledge. We're building in **two parallel tracks**:

```
                    CONTENT TRACK                         DATA LAYERS
                    (what you get back)                   (connections & context)

┌─────────────────────────────────────┐     ┌─────────────────────────────────┐
│  Normalized Content (future)        │     │  Overlays (future)              │
│  - JSON container with schema       │     │  - Quality flags                │
│  - Interpretation guidance          │     │  - Cross-references             │
│  - Usage instructions for AI        │     │  - Organizational context       │
├─────────────────────────────────────┤     ├─────────────────────────────────┤
│  Raw Content (future)               │     │  Relationships (future)         │
│  - Actual control/weakness text     │     │  - CVE ↔ CWE ↔ ATT&CK           │
│  - License information              │     │  - Control → Weakness           │
│  - Source attribution               │     │  - Technique → Mitigation       │
├─────────────────────────────────────┤     └─────────────────────────────────┘
│  Description (v1.0)                 │               ↑
│  - What this thing is               │               │ Independent tracks
│  - Human/AI readable summary        │               │ (can develop in parallel)
├─────────────────────────────────────┤               │
│  URL Resolution (v1.0)              │  ← WE ARE HERE
│  - Where to find it                 │
│  - Search instructions if no URL    │
├─────────────────────────────────────┤
│  Registry (v1.0)                    │  ← WE ARE HERE
│  - Namespace definitions            │
│  - Resolution rules                 │
│  - ID patterns and examples         │
├─────────────────────────────────────┤
│  Specification (complete)           │
│  - Identifier format                │
│  - Type definitions                 │
│  - Naming conventions               │
└─────────────────────────────────────┘
```

### The Vision: AI-First Responses

A SecID isn't just an identifier - it's a handle that gives you everything you need to understand and work with that security concept. When an AI agent receives a SecID response, it should be able to:

1. **Find it** - URL or search instructions
2. **Understand it** - Description of what it is
3. **Read it** - Actual content (where licensing permits)
4. **Interpret it** - Schema, guidance on what fields mean
5. **Use it** - Instructions on what to do with this data
6. **Connect it** - Related concepts, mitigations, examples

**Example future response:**

```json
{
  "secid": "secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12",
  "urls": {
    "lookup": "https://cloudsecurityalliance.org/artifacts/cloud-controls-matrix-v4",
    "api": "https://api.secid.dev/v1/control/cloudsecurityalliance.org/ccm/IAM-12"
  },
  "description": "Identity & Access Management control requiring multi-factor authentication for all interactive access to cloud services.",
  "content": {
    "raw": {
      "title": "IAM-12: Multi-Factor Authentication",
      "control_text": "Multi-factor authentication shall be implemented for all interactive access...",
      "implementation_guidance": "...",
      "audit_guidance": "..."
    },
    "license": "CC BY-NC-SA 4.0",
    "attribution": "Cloud Security Alliance",
    "retrieved": "2024-01-15"
  },
  "relationships": {
    "mitigates": ["secid:weakness/mitre.org/cwe#CWE-308", "secid:weakness/mitre.org/cwe#CWE-287"],
    "related_controls": ["secid:control/nist.gov/800-53@r5#IA-2"],
    "attacked_by": ["secid:ttp/mitre.org/attack#T1078"]
  },
  "meta": {
    "schema": "https://secid.dev/schemas/control/v1",
    "interpretation": "This is a technical control requiring MFA. The 'control_text' field contains the normative requirement. Check 'implementation_guidance' for how to implement, 'audit_guidance' for how to verify compliance.",
    "usage": "Use this to verify MFA requirements in cloud environments. Compare against your current authentication configuration.",
    "spec": "https://secid.dev/spec",
    "api_docs": "https://secid.dev/api"
  }
}
```

This response is **self-describing** - an AI receiving it knows what it has, how to interpret it, and what to do with it. The raw content stays raw; we add context through metadata, not transformation.

## Content Track (Parallel Development)

### Phase 1: URL + Description (v1.0)

Return where to find it and what it is:

```json
{
  "secid": "secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12",
  "urls": { "lookup": "..." },
  "description": "Identity & Access Management control requiring multi-factor authentication..."
}
```

### Phase 2: Raw Content (v1.x)

Add actual content where licensing permits:

```json
{
  "content": {
    "raw": { "title": "...", "control_text": "...", "guidance": "..." },
    "license": "CC BY-NC-SA 4.0",
    "attribution": "Cloud Security Alliance"
  }
}
```

**Why this matters:** Some sources are hard to access programmatically:
- CSA CCM/AICM are in spreadsheets
- ISO standards are behind paywalls
- Vendor advisories require authentication
- Data is buried in HTML tables or nested pages

We respect licensing - include license info, proper attribution, and only redistribute what's permitted.

### Phase 3: Content Metadata (v2.x)

Wrap raw content in a JSON container with interpretation and usage guidance:

```json
{
  "content": {
    "raw": { "title": "...", "control_text": "...", "guidance": "..." },
    "license": "CC BY-NC-SA 4.0",
    "attribution": "Cloud Security Alliance"
  },
  "meta": {
    "schema": "https://secid.dev/schemas/control/v1",
    "interpretation": "This is a technical control requiring MFA. The 'control_text' field contains the normative requirement, 'guidance' contains implementation suggestions.",
    "usage": "Use this to verify MFA requirements in cloud environments. Compare against your current authentication configuration.",
    "spec": "https://secid.dev/spec",
    "api_docs": "https://secid.dev/api"
  }
}
```

**Why this matters:** Raw data alone isn't enough for AI agents. They need:
- Schema link to understand structure
- Interpretation guidance for what fields mean
- Usage instructions for what to do with the data
- The content stays raw - we're adding context, not transforming it

## Data Layers (Independent Track)

### Relationships (Future)

Connect SecIDs to each other: CVE → CWE weakness, weakness → control mitigation, technique → weakness exploit.

**Why independent?** Relationship design benefits from real-world usage. We can ship content before relationships are fully designed.

See [RELATIONSHIPS.md](docs/future/RELATIONSHIPS.md) for exploratory thinking.

### Overlays (Future)

Add metadata without modifying sources: cross-references, quality flags, severity adjustments, organizational context.

**Why independent?** Same reason - usage will inform design. Overlays can be added to any response once the infrastructure exists.

See [OVERLAYS.md](docs/future/OVERLAYS.md) for exploratory thinking.

## Registry Seeding Strategy

### Why Start with Hundreds/Thousands of Entities?

The initial seeding serves multiple purposes:

1. **Stress test the spec**: Do our naming conventions hold up? Are there edge cases we missed?

2. **Learn the landscape**: What databases exist? How do they relate? What's the coverage?

3. **Build the graph**: Relationships need entities on both ends. More entities = richer graph.

4. **Demonstrate value**: A spec with 10 examples is theoretical. A spec with 1000 entities is useful.

5. **Attract contributors**: People contribute to living projects, not empty frameworks.

### Seeding Phases

**Phase 1: Core Security Infrastructure (50-100 entities)**

The foundations everything else references:

| Category | Examples | Why First |
|----------|----------|-----------|
| Vuln databases | CVE, NVD, GHSA, OSV, CNVD, EUVD | Core references |
| Weakness taxonomies | CWE, OWASP Top 10 | Vulnerability classification |
| Attack frameworks | ATT&CK, ATLAS, CAPEC | Threat modeling |
| Scoring systems | CVSS, EPSS | Severity/priority |
| Organizations | MITRE, NIST, FIRST, OWASP | Governance/authority |

*Status: Largely complete in current files*

**Phase 2: AI/ML Security Ecosystem (100-200 entities)**

Deep coverage of AI security landscape:

| Category | Examples | Why |
|----------|----------|-----|
| AI vendors | OpenAI, Anthropic, Google, Meta | Products to track |
| AI products | GPT-4, Claude, Gemini, Llama | Vulnerability targets |
| AI frameworks | LangChain, LlamaIndex, AutoGPT | Supply chain |
| AI security tools | Garak, PyRIT, Promptfoo | Testing ecosystem |
| AI standards | NIST AI RMF, ISO 42001 | Compliance landscape |
| AI research | Adversarial ML papers, jailbreak repos | Knowledge sources |

*Why prioritize AI?* This is our eventual differentiator. Deep AI coverage establishes expertise.

**Phase 3: Vendor Security Programs (200-500 entities)**

Major vendors and their security infrastructure:

| Category | Examples | Why |
|----------|----------|-----|
| Vendor PSIRTs | Microsoft, Google, Red Hat, Cisco | Advisory sources |
| Bug bounty programs | HackerOne, Bugcrowd hosted programs | Disclosure channels |
| Vendor advisories | MSRC, RHSA, DSA | Enrichment sources |
| Cloud security | AWS Security Hub, Azure Defender | Platform-specific |

*Why vendors?* Vendor advisories are a massive source of vulnerability data that often has richer context than NVD.

**Phase 4: Broader Security Ecosystem (500-1000+ entities)**

Long tail of security knowledge:

| Category | Examples | Why |
|----------|----------|-----|
| Security tools | Nmap, Metasploit, Burp Suite | Referenced in vulns |
| Security standards | PCI-DSS, HIPAA, SOC 2 | Compliance mapping |
| Threat intel | MISP, OpenCTI, threat feeds | Future: threat intelligence |
| Research groups | Google P0, Microsoft MSTIC | Attribution |
| Conferences | DEF CON, Black Hat, RSA | Community nodes |

### What We Learn From Seeding

The act of adding entities teaches us:

**Naming edge cases:**
- What about `AT&T`? → `att` (remove special chars)
- What about `CERT/CC` vs `US-CERT`? → Need aliasing strategy
- What about acquired companies? → Historical entities need tracking

**Relationship patterns:**
- Most vulns have CWE mappings... AI vulns are newer and still being classified
- GHSA cross-references CVE... except for ecosystem-specific issues
- Multiple sources may provide different severity assessments... need reconciliation tracking

**Coverage status:**
- CWE has 4 AI-specific entries (e.g., CWE-1427 for prompt injection), gaps remain
- ATT&CK and ATLAS continue expanding
- AI security taxonomies are still maturing

**Data quality observations:**
- Processing backlogs can delay enrichment data
- Cross-references between databases occasionally need correction
- Different sources may assess severity differently

This learning feeds back into spec refinement and overlay priorities.

## Concrete Deliverables

### Version 0.9: Public Draft (Current)

| Deliverable | Status | Notes |
|-------------|--------|-------|
| Specification (SPEC.md) | Complete | Open for public comment |
| Registry structure | Complete | 121 namespace definitions (YAML + JSON) |
| Type documentation | Complete | All 8 types documented |
| Design documentation | Complete | RATIONALE, DESIGN-DECISIONS, STRATEGY |
| Namespace documentation | Complete | _index.md files for advisory namespaces |

### Version 1.0: URL Resolution

| Deliverable | Status | Success Criteria |
|-------------|--------|------------------|
| Registry data (500+ namespaces) | In progress (121 done) | Every namespace has URL resolution rules + description |
| REST API + MCP server | **Live** | [secid.cloudsecurityalliance.org](https://secid.cloudsecurityalliance.org/) — MCP server shipped first, REST API followed |
| Compliance test suite | Not started | Canonical test cases built during API development; doubles as conformance spec for third-party implementations |
| Python library (`secid`) | Not started | `pip install secid` enables parsing and resolution |
| npm/TypeScript library (`secid`) | Not started | `npm install secid` enables parsing and resolution |
| Go library | Not started | Native Go support for cloud-native tools |
| Rust library | Not started | Native Rust support for systems tools |
| Java library | Not started | Native Java support for enterprise tools |
| C#/.NET library | Not started | Native .NET support for Windows ecosystem |

### Skills

Claude Code skills support the registry workflow. Skills are built **incrementally during API development**, not as standalone deliverables — each new namespace, conversion, or test case teaches the skills what they need to cover.

| Skill | Purpose | Status |
|-------|---------|--------|
| [Registry Research](skills/registry-research/) | Research sources, create/update .md registry files, determine resolution strategy | Active |
| [Registry Formalization](skills/registry-formalization/) | Convert .md to .json, validate against JSON Schema, ensure cross-format consistency | Active |
| [Registry Validation](skills/registry-validation/) | Validate registry entries against the JSON schema and naming conventions | **Active** — first non-stub skill |
| [Compliance Testing](skills/compliance-testing/) | Run canonical test suite against resolver implementations, diagnose failures | Stub (accumulates test cases as edge cases are discovered) |
| [SecID User](skills/secid-user/) | Consuming SecID as an end user via the live service | Active (SecID-Service is live) |

### Validation Strategy: AI-Assisted

Registry quality depends on validation. Our approach uses AI as a first-class participant in the validation process.

**The workflow:**

1. **Goal discovery** - Given a SecID like `secid:advisory/redhat.com/errata#RHSA-2024:1234`, ask AI: "What would you typically want to do with this?" The most likely answer: "Find the URL for this RHSA."

2. **Codify the goal** - That answer becomes the success criterion: resolution must produce a working URL.

3. **Add resolution rules** - Create/update the registry entry with URL templates and patterns.

4. **Verify it works** - AI tests the resolution against real identifiers, confirms URLs resolve.

5. **Iterate** - If edge cases fail, refine the rules.

**Why AI-assisted?**

- **Scale**: 500+ namespaces can't be manually validated continuously
- **Consistency**: AI applies the same verification logic everywhere
- **Discovery**: AI can identify what users would expect before we build it
- **Maintenance**: AI can detect URL rot and resolution failures over time

This isn't "AI does everything" - it's AI as a team member that handles the tedious verification work that humans would skip or do inconsistently.

### Version 1.x: Raw Content

| Deliverable | Status | Success Criteria |
|-------------|--------|------------------|
| Content ingestion (CSA CCM/AICM) | Planned | Spreadsheet data extracted, licensed properly |
| Content ingestion (NIST 800-53) | Planned | Control text available via API |
| Content ingestion (CWE/ATT&CK) | Planned | Weakness/technique descriptions included |
| License tracking | Planned | Every content response includes license + attribution |
| API content endpoints | Planned | `?include=content` returns raw text |

### Version 2.x: Content Metadata + Data Layers

| Deliverable | Status | Success Criteria |
|-------------|--------|------------------|
| JSON schemas for each type | Planned | Documented, versioned schemas for controls, weaknesses, etc. |
| Metadata wrapper | Planned | Raw content wrapped with interpretation + usage guidance |
| Relationship layer | Planned | Connect CVE↔CWE↔ATT&CK, enable graph queries |
| Overlay layer | Planned | Quality flags, cross-references, organizational context |

### Future Applications

| Deliverable | Depends On | Value |
|-------------|------------|-------|
| Web interface | REST API | Browse and search security knowledge visually |
| AI-powered assistant | All of the above | Natural language queries over security knowledge |
| Knowledge graph UI | Relationships | Visualize connections between security concepts |

## Ecosystem Architecture

SecID is designed as a federated ecosystem with multiple independent components:

| Component | What It Is | Can Be Multiple? |
|-----------|------------|------------------|
| **SecID Standard** | The identifier specification (`secid:type/namespace/name#subpath`) | One canonical spec, versioned |
| **SecID Registries** | Namespace definitions, resolution rules | Yes - private registries, organizational overlays |
| **Relationship Databases** | Connections between identifiers | Yes - different sources, perspectives |
| **Enrichment Databases** | Metadata, annotations, context | Yes - organizational data, private enrichments |
| **SecID APIs** | Services that resolve and query | Yes - different providers, implementations |

**Federation means:** Organizations can run their own registries, databases, and APIs that overlay or extend the canonical data. A company might maintain private namespace definitions, internal relationship mappings, or proprietary enrichments - all compatible with the public ecosystem.

### Arbitrary URL Support

SecID identifiers are for **structured security knowledge with defined namespaces**. Arbitrary URLs are explicitly NOT part of the identifier specification (no `secid:url/...` type). However, APIs and databases can support URL queries:

| Component | SecID Identifiers | Arbitrary URLs |
|-----------|-------------------|----------------|
| **SecID Standard** | ✅ Defines these | ❌ Explicitly excluded |
| **SecID Registry** | ✅ Contains these | ❌ Not applicable |
| **Our API** | ✅ Must support | ✅ Probably will support |
| **Our Relationship DB** | ✅ Must include | ✅ Probably will include |
| **Our Enrichment DB** | ✅ Must include | ✅ Probably will include |

**Why this separation?** URLs are already globally unique identifiers - wrapping them in `secid:url/...` adds complexity without value. But APIs and databases can accept URLs as query inputs and store relationships/enrichments for arbitrary web content. This keeps the spec clean while enabling practical use cases like "what do we know about this Stack Overflow answer?"

See [SPEC.md Section 1.3](SPEC.md#13-scope-what-secid-identifies-and-what-it-doesnt) for the full rationale.

## Making SecID Easy to Consume

Our goal is to make SecID as easy to consume as possible. We're building:

| Repository | Purpose | Status |
|------------|---------|--------|
| **SecID** (this repo) | Spec, registry, operations docs | Active |
| **[SecID-Service](https://github.com/CloudSecurityAlliance/SecID-Service)** | Hosted API + MCP server | **Live** |
| **SecID-Website** | Documentation and registry browser | Planned |
| **SecID-Client-SDK** | Client libraries + AI instructions | Planned |

### SecID-Client-SDK

Reference client libraries and AI-consumable instructions:
- Python (`pip install secid`) and npm/TypeScript (`npm install secid`) for SEO and discoverability
- AI instructions for generating clients in any language
- Test fixtures extracted from the registry

### LLM-Friendly

We support the [llms.txt standard](https://llmstxt.org/) for AI-friendly content discovery. The website provides `/llms.txt` with structured links to key resources, enabling AI agents to efficiently understand SecID.

See [INFRASTRUCTURE.md](docs/reference/INFRASTRUCTURE.md) for technical details on hosting and architecture.

## Success Indicators

### v1.0 Success Criteria

| Indicator | How We'll Know |
|-----------|----------------|
| Resolution works | Given any registered SecID, we return a working URL |
| Libraries are usable | `pip install secid` and `npm install secid` work out of the box |
| Coverage is comprehensive | Major advisory sources, weakness taxonomies, and control frameworks covered |
| Community adoption | External projects start using SecID identifiers |

### Registry Quality Indicators

| Indicator | Meaning |
|-----------|---------|
| Naming conventions stable | No major spec changes needed after seeding |
| Edge cases documented | Spec handles exceptions gracefully |
| Resolution rules tested | URL templates produce valid, working links |

## Open Questions

Things we'll learn as we build v1.0:

1. **Resolution edge cases**: What happens when a vendor changes their URL structure?
2. **Deprecation**: How do we handle databases that shut down or get acquired?
3. **Search fallback**: When direct URLs aren't possible, what search instructions work best for AI agents?
4. **Update frequency**: How often do registry files need refresh?
5. **Library scope**: Should libraries include validation, or just parsing and resolution?

These will be answered empirically, not theoretically.

