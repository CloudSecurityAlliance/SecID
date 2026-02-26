# SecID Use Cases

Concrete examples of what SecID enables. These aren't hypothetical - they're the problems we're solving.

## Use Case 1: "What is this vulnerability, really?"

### The Problem

You see `CVE-2024-1234`. You want to know:
- What's the GHSA? (for package version info)
- What's the CWE? (for weakness type)
- What's the CVSS? (for severity)
- Is there an exploit? (for prioritization)
- What controls help? (for remediation)

Currently this requires:
1. Search NVD → get CWE, CVSS (when enrichment available)
2. Search GHSA → maybe find it, get package info
3. Search OSV → maybe find aliases
4. Search ATT&CK → different abstraction level
5. Manually correlate everything

### With SecID

```
secid:advisory/mitre.org/cve#CVE-2024-1234
    ├── aliases
    │   ├── secid:advisory/github.com/advisories/ghsa#GHSA-xxxx-yyyy-zzzz
    │   └── secid:advisory/google.com/osv#PYSEC-2024-567
    ├── classified_as
    │   └── secid:weakness/mitre.org/cwe#CWE-89
    ├── severity
    │   ├── cvss:3.1 → 8.8 (from NVD)
    │   └── epss → 0.42 (42% exploitation probability)
    ├── affects
    │   └── pkg:pypi/sqlparse@0.4.0-0.4.3
    ├── exploited_by
    │   └── secid:ttp/mitre.org/attack#T1190
    └── mitigated_by
        └── secid:control/owasp.org/asvs#V5.3.4
```

One query, complete picture.

## Use Case 2: "Show me all prompt injection vulnerabilities"

### The Problem

You're assessing LLM security. You want every known prompt injection issue.

But prompt injection spans:
- CVEs (when assigned, which is rare)
- GHSA (for package-level issues in LangChain, etc.)
- Research papers (most prompt injection is academic)
- ATLAS techniques (AML.T0043)
- OWASP LLM Top 10 (LLM01)

No single database has them all. No standard way to query across.

### With SecID

```
# Find everything classified as prompt injection
secid:weakness/mitre.org/cwe#CWE-1427  # Direct CWE for prompt injection
    └── instances
        ├── secid:advisory/mitre.org/cve#CVE-2023-29374  # LangChain
        ├── secid:advisory/mitre.org/cve#CVE-2023-36189  # LangChain
        ├── secid:advisory/github.com/advisories/ghsa#GHSA-...       # More LangChain
        └── ...

secid:weakness/owasp.org/llm-top10#LLM01  # OWASP category
    └── instances
        ├── (everything above)
        └── (additional research/incidents)

secid:ttp/mitre.org/atlas#AML.T0043  # Attack technique
    └── examples
        ├── (case studies)
        └── (related vulns)
```

Query any entry point, traverse to find everything related.

## Use Case 3: "Map our controls to OWASP LLM Top 10"

### The Problem

Auditor asks: "Show me how your controls address OWASP LLM Top 10."

You have controls documented somewhere. OWASP LLM Top 10 is documented. But the mapping between them is:
- In someone's head
- In a one-off spreadsheet
- Outdated
- Not queryable

### With SecID

```yaml
# Pre-built mapping in relationships/
mapping: "CSA AI Controls Matrix → OWASP LLM Top 10"

secid:weakness/owasp.org/llm-top10#LLM01  # Prompt Injection
    └── mitigated_by
        ├── secid:control/cloudsecurityalliance.org/aicm#INP-01  # Input validation
        │   └── strength: partial
        │   └── notes: "Helps but doesn't fully prevent"
        ├── secid:control/cloudsecurityalliance.org/aicm#INP-02  # Input sanitization
        │   └── strength: partial
        └── secid:control/cloudsecurityalliance.org/aicm#ARC-03  # Prompt isolation
            └── strength: strong

secid:weakness/owasp.org/llm-top10#LLM02  # Sensitive Information Disclosure
    └── mitigated_by
        ├── secid:control/cloudsecurityalliance.org/aicm#DAT-01  # Data classification
        ├── secid:control/cloudsecurityalliance.org/aicm#DAT-04  # Output filtering
        └── secid:control/cloudsecurityalliance.org/aicm#MOD-02  # Fine-tuning controls
```

Auditor can see exact mappings with rationale. You can generate compliance matrices automatically.

## Use Case 4: "What's the AI security landscape?"

### The Problem

New to AI security. Want to understand:
- What databases track AI vulnerabilities?
- What frameworks exist for AI threats?
- What standards apply?
- Who are the key players?

Currently: Read a bunch of blog posts, hope you find the right ones.

### With SecID

Browse the entity registry:

```
secid:entity/mitre.org/atlas         # AI attack framework
secid:entity/owasp.org/llm-top10     # AI risk categories
secid:entity/cloudsecurityalliance.org/aicm            # AI controls
secid:entity/nist.gov/ai-rmf         # AI risk management

secid:entity/openai.com/gpt-4        # GPT-4 model
secid:entity/openai.com/chatgpt      # ChatGPT service
secid:entity/anthropic.com/claude    # Claude model
secid:entity/google.com/gemini       # Gemini model

# Each entity has:
# - What it is
# - What it contains
# - How to access it
# - Common misconceptions
# - Relationships to other entities
```

The entity files ARE the learning resource. Reading about ATLAS teaches you what it is, why it matters, and how it relates to everything else.

## Use Case 5: "Track AI security issues that need rapid coordination"

### The Problem

You discover a jailbreak technique that affects all LLMs. Traditional vulnerability tracking is challenging because:
- No specific software version affected (affects model classes)
- Behavioral pattern rather than code defect
- Rapid disclosure pace in AI research community

Researchers need a way to track and coordinate on these issues while the broader ecosystem adapts.

### With SecID (Future AI Vuln DB)

```
secid:advisory/ai-vuln-db/JB-2024-0042
    ├── name: "DAN 15.0 Jailbreak"
    ├── description: "Persona-based jailbreak effective against GPT-4, Claude, Gemini"
    ├── classified_as
    │   ├── secid:weakness/owasp.org/llm-top10#LLM01
    │   └── secid:ttp/mitre.org/atlas#AML.T0051
    ├── affects
    │   ├── secid:entity/openai.com/gpt-4
    │   ├── secid:entity/anthropic.com/claude-3
    │   └── secid:entity/google.com/gemini
    ├── discovered: 2024-03-15
    ├── references
    │   ├── https://jailbreakchat.com/...
    │   └── https://arxiv.org/...
    └── status: "unpatched"
```

Tracked, classified, queryable - complementing CVE for issues that benefit from faster coordination.

## Use Case 6: "Get severity data from multiple sources"

### The Problem

CVE-2024-9999 published. NVD enrichment is pending. You need:
- CVSS score for prioritization
- CWE for understanding
- Affected versions for patching

Meanwhile, the vendor has published their own advisory with this information.

### With SecID Overlays

```yaml
# overlays/enrichment/CVE-2024-9999.yaml
overlay_type: enrich
target: secid:advisory/mitre.org/cve#CVE-2024-9999
source: "secid:advisory/acme/SA-2024-042"

adds:
  cvss_v3_1:
    score: 9.8
    vector: "CVSS:3.1/AV:N/AC:L/PR:N/UI:N/S:U/C:H/I:H/A:H"
    source: "vendor"

  cwe: "CWE-502"

  affected_versions:
    - ">=1.0.0 <1.5.3"
    - ">=2.0.0 <2.1.1"

  fixed_versions:
    - "1.5.3"
    - "2.1.1"

rationale: "Supplementing with vendor advisory data"
confidence: "high"
```

Get actionable data immediately from vendor sources while official enrichment completes.

## Use Case 7: "Cross-reference everything for this package"

### The Problem

You use `langchain`. You want EVERY security issue:
- CVEs
- GHSAs
- Security advisories
- Related vulnerabilities in dependencies
- Relevant attack techniques

### With SecID

```
pkg:pypi/langchain
    └── vulnerabilities
        ├── secid:advisory/mitre.org/cve#CVE-2023-29374
        │   └── classified_as: secid:weakness/mitre.org/cwe#CWE-94
        ├── secid:advisory/mitre.org/cve#CVE-2023-36189
        │   └── classified_as: secid:weakness/mitre.org/cwe#CWE-1427
        ├── secid:advisory/github.com/advisories/ghsa#GHSA-...
        └── secid:advisory/github.com/advisories/ghsa#GHSA-...

    └── dependencies (from SBOM)
        ├── pkg:pypi/openai
        │   └── vulnerabilities: [...]
        ├── pkg:pypi/tiktoken
        │   └── vulnerabilities: [...]
        └── ...

    └── relevant_techniques
        ├── secid:ttp/mitre.org/atlas#AML.T0043  # Prompt injection
        ├── secid:ttp/mitre.org/atlas#AML.T0054  # Plugin compromise
        └── ...
```

Complete security picture for dependency decisions.

## Use Case 8: "Understand coverage across vulnerability databases"

### The Problem

You want to understand which vulnerability types are well-tracked across the ecosystem and where emerging areas might need attention.

### With SecID Analysis

```
# Query: Compare coverage across databases by weakness type

secid:weakness/mitre.org/cwe#CWE-1427  # Prompt Injection
    └── cve_count: 12
    └── ghsa_count: 45
    └── atlas_references: 3
    └── coverage_note: "Emerging area, coverage expanding"

secid:weakness/mitre.org/cwe#CWE-1426  # Improper AI Output Validation
    └── cve_count: 3
    └── ghsa_count: 18
    └── coverage_note: "New weakness type, tracking growing"

secid:weakness/mitre.org/cwe#CWE-502   # Deserialization
    └── cve_count: 2,847
    └── ghsa_count: 312
    └── coverage_note: "Mature, well-tracked"
```

Data-driven insights into ecosystem coverage by vulnerability type.

## Use Case 9: "Generate a threat model"

### The Problem

Building an LLM application. Need threat model covering:
- Relevant attack techniques
- Applicable weaknesses
- Recommended controls
- Known vulnerabilities in your stack

### With SecID

```
# Input: I'm building with LangChain + OpenAI + Pinecone

# Output threat model:

Components:
  - pkg:pypi/langchain → 15 known vulns
  - secid:entity/openai.com/api → prompt injection exposure
  - secid:entity/pinecone.io/vector-db → embedding manipulation risk

Relevant Threats:
  - secid:ttp/mitre.org/atlas#AML.T0043 (Prompt Injection)
      └── your_exposure: HIGH (direct user input to LLM)
  - secid:ttp/mitre.org/atlas#AML.T0054 (Plugin Compromise)
      └── your_exposure: MEDIUM (using tools)
  - secid:ttp/mitre.org/atlas#AML.T0048 (Embedding Manipulation)
      └── your_exposure: MEDIUM (RAG with Pinecone)

Applicable Weaknesses:
  - secid:weakness/owasp.org/llm-top10#LLM01 through LLM10

Recommended Controls:
  - secid:control/cloudsecurityalliance.org/aicm#INP-01 (Input Validation)
  - secid:control/cloudsecurityalliance.org/aicm#OUT-01 (Output Validation)
  - secid:control/cloudsecurityalliance.org/aicm#RAG-01 (RAG Security)
```

Threat modeling becomes a query, not a research project.

## Use Case 10: "Keep AI security research organized"

### The Problem

AI security research is scattered:
- Papers on arXiv
- Jailbreaks on GitHub/Reddit
- Vendor disclosures
- Conference talks
- Blog posts

No central index. No way to track what's been tried.

### With SecID

```
# Research paper example (using reference type)
secid:reference/arxiv.org/1908.07125
    ├── title: "Universal Adversarial Triggers"
    ├── demonstrates
    │   └── secid:ttp/mitre.org/atlas#AML.T0043
    ├── affects
    │   ├── secid:entity/openai.com/gpt-2
    │   └── secid:entity/google.com/bert
    └── related_to
        └── secid:weakness/mitre.org/cwe#CWE-1427

# Jailbreak technique (future: could be tracked via AI vuln database)
secid:advisory/ai-vuln-db/JB-2024-0015
    ├── name: "DAN Jailbreak"
    ├── versions: ["DAN 1.0", "DAN 5.0", "DAN 11.0", ...]
    ├── demonstrates
    │   └── secid:ttp/mitre.org/atlas#AML.T0051
    └── affects
        ├── secid:entity/openai.com/gpt-3.5
        └── secid:entity/openai.com/gpt-4 (partial)
```

Research becomes navigable, not just searchable.

---

## Common Thread

All these use cases share the same pattern:

1. **Single identifier format** across all security knowledge
2. **Relationships** that connect disparate databases
3. **Overlays** that fill gaps without modifying sources
4. **Entity registry** that defines what exists

SecID doesn't replace existing databases. It makes them work together.

