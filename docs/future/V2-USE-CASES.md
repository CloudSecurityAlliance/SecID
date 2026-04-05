# SecID V2 Use Cases (Speculative)

Status: Research / speculation. Not commitments.

## The V2 Shift

V1 is a librarian: "the book you want is on shelf 3." V2 is the librarian who also reads you the relevant passage and explains how it connects to the other book you were reading.

**V1:** Identity + resolution. "Here's what it's called, here's where to find it."
**V2:** Identity + resolution + content + relationships. "Here's what it's called, here's where to find it, here's the actual content, and here's how it connects to everything else."

## What Changes

V2 adds two capabilities:

1. **Data federation** — for sources where we host the actual content (per [DATA-HOSTING-RULES.md](../reference/DATA-HOSTING-RULES.md)), the resolver returns the content inline instead of just a URL
2. **Relationship layer** — cross-type connections (CVE→CWE, CWE→control, technique→mitigation) enable multi-hop queries

Together these mean: one query can return a complete picture across multiple security knowledge domains with actual content, not just links.

## Use Cases by Persona

### Security Researcher / Pen Tester

**"I found a vulnerability in product X, who do I report it to and how?"**

V1 (today): Disclosure type returns CNA scope, contacts, policy URL. Agent has to follow policy URL to read the actual policy.

V2: Returns CNA scope, contacts, AND the actual disclosure policy text. Agent can draft a disclosure report that follows the vendor's specific requirements without fetching external pages.

**"Tell me everything about this CVE"**

V1: Returns 5 URLs (MITRE, NVD, Red Hat, SUSE, GitHub). Agent fetches each, parses HTML, extracts data separately.

V2: Returns structured JSON with CVE description, severity, affected products (from cvelistV5, cached/proxied), CWE mapping with full weakness description inline, ATT&CK technique mapping with technique description, all vendor advisories with patch status, which CNA assigned it, and related CVEs. One call, complete picture.

### AI Agent Doing Security Analysis

**"Is my stack affected?"**

Developer lists dependencies. Agent cross-references:
- Entity type for each product
- All advisories (structured advisory data)
- CWE for each advisory (full weakness content)
- Mitigations from CWE data
- Control framework coverage (CCM/NIST content)

Output: "3 of your 47 dependencies have open vulnerabilities. Here are the CVEs, what they mean, and which controls in your compliance framework address them."

**"Analyze this vulnerability end-to-end"**

Single query chain with content at every hop:
```
CVE-2024-1234
  → CWE-79 (full weakness description, mitigations, examples)
    → ATT&CK T1059.003 (technique description, detection, data sources)
      → NIST 800-53 SI-4 (full control text)
        → CCM LOG-01 (full control text)
```

Today this requires ~10 separate fetches with HTML parsing. V2 returns it as structured data.

### GRC / Compliance Person

**"Map GDPR Article 32 to our control framework"**

V1: Gets URLs for GDPR and NIST CSF. Agent has to fetch and parse both documents.

V2: Returns GDPR Article 32 actual text + NIST CSF PR.DS control texts. Agent does semantic comparison with both texts in hand: "GDPR Article 32(1)(a) requires pseudonymisation and encryption. NIST CSF PR.DS-1 (Data-at-rest) and PR.DS-2 (Data-in-transit) address this. Here's the specific text from each..."

**"Write me a security policy for identity management"**

```
Agent asks SecID for:
  CCM IAM-01 through IAM-16 → gets full control text
  NIST 800-53 IA family → gets full control text
  GDPR Article 25, 32 → gets actual article text
  ISO 27001 A.5 → gets control descriptions (where licensed)

Agent synthesizes a policy satisfying all four frameworks,
citing specific control IDs with actual quotes.
```

**"Generate SOC 2 evidence for vulnerability management"**

V2 provides: CCM TVM domain controls (full text), mapped to NIST 800-53 RA and SI families (full text), current CVE statistics, CNA disclosure program details, evidence template with specific control references.

### SOC Analyst / Incident Responder

**"This alert maps to T1059.003. Tell me everything."**

V2 returns ATT&CK technique full description + detection methods + data sources + related techniques + sub-techniques + mitigations (all from STIX data, structured). Cross-references advisory→TTP relationships for CVEs that use this technique. Maps to relevant compliance controls (NIST 800-53 AU-2, SI-4) with full control text.

**"What happened with Log4Shell?"**

Requires synthesizing across sources — CVEs, advisories from multiple vendors, exploitation timeline, patches, CISA KEV status. Today impossible in one query. V2 with synthesis (Rule 3 data) returns a consolidated narrative with sources.

### Developer / DevSecOps

**"What security checks should I run for my AI application?"**

V2 returns: OWASP LLM Top 10 (full descriptions), CSA AICM controls (full text), MITRE ATLAS techniques (full descriptions). Agent maps threats to controls: "ATLAS T0043 (Prompt Injection) → CWE-1427 → AICM MDS-03" with actual descriptions at every level.

**"Where do I report this bug in an open source project?"**

V2 returns CNA scope match + contact + disclosure policy text + the project's SECURITY.md content if available. Agent can draft the report immediately.

### AI Agent Building Documents

**"I need to cite CVE-2024-1234 in a report"**

V2 returns canonical SecID, all URLs, AND the CVE description text. Agent includes both the structured reference and a human-readable summary without needing to fetch the CVE page.

**"List all NIST CSF controls in the Protect function"**

V2 returns the full control text for each PR.* control, not just IDs. Agent can include actual control language in the document.

## Patterns

### 1. Content inline eliminates the fetch-parse-hope cycle

Today's agents spend most of their tokens fetching web pages and trying to extract structured data from HTML. V2 removes that entire step for sources we host.

### 2. Cross-type queries become the killer feature

"CVE → CWE → control → regulation" chains that today require 4+ separate lookups with manual correlation become one coherent response with the relationship layer.

### 3. Relationships multiply value exponentially

Each pairwise connection (CVE→CWE, CWE→control, technique→mitigation) makes every other piece of data more useful. The value isn't linear — it's the graph.

### 4. Synthesis enables temporal queries

"What happened with Log4Shell?" requires synthesizing CVEs, advisories, timeline, patches, exploits across sources and time. Rule 3 data (synthesized content) makes this queryable.

### 5. Scope search on disclosure becomes a product

"Who covers IoT devices in the EU?" requires filtering 486 CNAs by scope text + country. With structured data hosted and searchable, this becomes a practical query.

### 6. The data becomes the documentation

Instead of "go read the GDPR," the agent has the GDPR text. Instead of "check the CCM spreadsheet," the agent has the control text. SecID becomes self-contained for the sources it covers.

## What We Don't Do

Even in V2, some things stay out of scope:

- **Vulnerability scanning** — SecID tells you about known vulnerabilities, it doesn't find new ones
- **Compliance decisions** — SecID provides the control text, it doesn't decide if you're compliant
- **Severity assessment** — SecID provides CVSS scores from sources, it doesn't compute new ones
- **Threat intelligence** — SecID references threat data, it's not a threat feed
- **Remediation** — SecID tells you what the control says to do, it doesn't do it

SecID is infrastructure. The value comes from what agents and tools build on top of it.

## Dependencies

These use cases require:

| Capability | Required For |
|-----------|-------------|
| V2 data federation (Rule 2) | Any use case that needs content inline |
| Relationship layer | Cross-type queries (CVE→CWE→control) |
| Rule 3 synthesis | Temporal queries, consolidated narratives |
| Scope search/filtering | CNA scope matching, control filtering |
| Content caching/proxy | CVE content from cvelistV5 without hosting |

The data federation (Rule 2) work is the foundation — most other capabilities build on having structured content available.
