---
type: weakness
namespace: owasp.org
full_name: "Open Web Application Security Project"
operator: "secid:entity/owasp.org"
website: "https://owasp.org"
status: active

sources:
  top10:
    full_name: "OWASP Top 10"
    urls:
      website: "https://owasp.org/www-project-top-ten/"
      v2021: "https://owasp.org/Top10/"
      v2017: "https://owasp.org/www-project-top-ten/2017/"
      v2013_pdf: "https://owasp.org/www-pdf-archive/OWASP_Top_10_-_2013.pdf"
    id_pattern_2021: "A0[1-9]|A10"
    id_pattern_2017_2013: "A[1-9]|A10"
    id_pattern_note: "ID format differs by version: 2021 uses zero-padded (A01-A10), 2017/2013 use non-padded (A1-A10). URLs are version-specific with name slugs — requires lookup table, not a simple template."
    versions:
      - "2021"
      - "2017"
      - "2013"
    version_required: true
    unversioned_behavior: "all_with_guidance"
    version_disambiguation: "Versions are released by year. Match the version whose release year is closest to but not after the referring document's publication date. If no date context is available, use the latest version (2021). Note: item numbering restarts with each version — A01 in one version is unrelated to A01 in another."
    examples:
      - "secid:weakness/owasp.org/top10@2021#A01"
      - "secid:weakness/owasp.org/top10@2017#A1"
      - "secid:weakness/owasp.org/top10#A01"

  llm-top10:
    full_name: "OWASP Top 10 for LLM Applications"
    urls:
      website: "https://owasp.org/www-project-top-10-for-large-language-model-applications/"
      index: "https://genai.owasp.org/llm-top-10/"
      v2_list: "https://genai.owasp.org/llm-top-10/"
      v1_list: "https://owasp.org/www-project-top-10-for-large-language-model-applications/Archive/0_1_vulns/"
      lookup: "https://genai.owasp.org/llmrisk/{id}/"
    id_pattern: "LLM\\d{2}"
    versions:
      - "2.0"
      - "1.0"
    version_required: true
    unversioned_behavior: "all_with_guidance"
    version_disambiguation: "v2.0 (2025) significantly restructured from v1.0 (2023). Match the version whose release date is closest to but not after the referring document's publication date. If no date context, use v2.0. Item numbering is reused — LLM01 in v2.0 is the same topic (Prompt Injection) but with substantially updated content; other items changed more significantly."
    examples:
      - "secid:weakness/owasp.org/llm-top10@2.0#LLM01"
      - "secid:weakness/owasp.org/llm-top10@2.0#LLM02"
      - "secid:weakness/owasp.org/llm-top10#LLM01"

  ml-top10:
    full_name: "OWASP Machine Learning Security Top 10"
    urls:
      website: "https://owasp.org/www-project-machine-learning-security-top-10/"
      index: "https://mltop10.info/"
      github: "https://github.com/OWASP/www-project-machine-learning-security-top-10"
      lookup: "https://mltop10.info/#{id}/"
    id_pattern: "ML\\d{2}"
    versions:
      - "2023"
    examples:
      - "secid:weakness/owasp.org/ml-top10#ML01"
      - "secid:weakness/owasp.org/ml-top10#ML05"
      - "secid:weakness/owasp.org/ml-top10@2023#ML01"

  agentic-top10:
    full_name: "OWASP Top 10 for Agentic Applications"
    urls:
      website: "https://genai.owasp.org/"
      index: "https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/"
      announcement: "https://genai.owasp.org/2025/12/09/owasp-top-10-for-agentic-applications-the-benchmark-for-agentic-security-in-the-age-of-autonomous-ai/"
      lookup: "https://genai.owasp.org/agentic/{id}/"
    id_pattern: "ASI\\d{2}"
    versions:
      - "2026"
    examples:
      - "secid:weakness/owasp.org/agentic-top10#ASI01"
      - "secid:weakness/owasp.org/agentic-top10#ASI06"
      - "secid:weakness/owasp.org/agentic-top10#ASI10"

  ai-exchange:
    full_name: "OWASP AI Exchange"
    urls:
      website: "https://owaspai.org"
      index: "https://owaspai.org/docs/ai_security_overview/#periodic-table-of-ai-security"
      threats: "https://owaspai.org/docs/ai_security_overview/#how-to-address-ai-security"
      lookup: "https://owaspai.org/goto/{id}/"
    id_pattern: "[A-Z]+"
    examples:
      - "secid:weakness/owasp.org/ai-exchange#DIRECTPROMPTINJECTION"
      - "secid:weakness/owasp.org/ai-exchange#DATAPOISON"
      - "secid:weakness/owasp.org/ai-exchange#MODELTHEFTUSE"

  aivss:
    full_name: "AI Vulnerability Scoring System"
    urls:
      website: "https://owasp.org/www-project-ai-vulnerability-scoring-system/"
      github: "https://github.com/OWASP/www-project-ai-vulnerability-scoring-system"
    versions:
      - "1.0"
    examples:
      - "secid:weakness/owasp.org/aivss@1.0"
---

# OWASP Weakness Taxonomies

OWASP produces multiple weakness taxonomies for different domains, from traditional web security to AI/ML systems. OWASP's Top 10 lists are the most widely recognized weakness taxonomies.

## Why OWASP Matters for Weaknesses

- **Practitioner-focused** - Written for developers and security teams
- **Regularly updated** - Tracks evolving threat landscape
- **Community-driven** - Open contributions and feedback
- **Free and open** - No licensing restrictions

## Evolution of OWASP AI Coverage

```
2003: OWASP Top 10 (Web)
2017: OWASP Top 10 updated
2021: OWASP Top 10 2021
2023: OWASP LLM Top 10 v1.0
2023: OWASP ML Top 10
2024: OWASP AI Exchange
2025: OWASP LLM Top 10 v2.0
2025: OWASP Agentic AI Top 10
```

---

## top10

The most critical web application security risks.

### Format

```
secid:weakness/owasp.org/top10[@YEAR]#ITEM
secid:weakness/owasp.org/top10@2021#A03     # 2021 (zero-padded)
secid:weakness/owasp.org/top10@2017#A1      # 2017 (NOT zero-padded)
secid:weakness/owasp.org/top10#A01          # No version = latest (2021)
```

ID format differs by version: 2021 uses zero-padded IDs (A01-A10), 2017 and 2013 use non-padded IDs (A1-A10). URLs are version-specific with name slugs -- each version requires a lookup table, not a simple URL template.

### 2021 Edition (current)

| ID | Name |
|----|------|
| A01 | Broken Access Control |
| A02 | Cryptographic Failures |
| A03 | Injection |
| A04 | Insecure Design |
| A05 | Security Misconfiguration |
| A06 | Vulnerable and Outdated Components |
| A07 | Identification and Authentication Failures |
| A08 | Software and Data Integrity Failures |
| A09 | Security Logging and Monitoring Failures |
| A10 | Server-Side Request Forgery (SSRF) |

### 2017 Edition (superseded)

Still widely referenced in existing documentation and certifications.

| ID | Name |
|----|------|
| A1 | Injection |
| A2 | Broken Authentication |
| A3 | Sensitive Data Exposure |
| A4 | XML External Entities (XXE) |
| A5 | Broken Access Control |
| A6 | Security Misconfiguration |
| A7 | Cross-Site Scripting (XSS) |
| A8 | Insecure Deserialization |
| A9 | Using Components with Known Vulnerabilities |
| A10 | Insufficient Logging & Monitoring |

Note: A10 2017 URL contains double-encoded ampersand (%2526) due to the & in the title.

### 2013 Edition (legacy, superseded)

Individual item pages are no longer live. Only a PDF of the full document is available.

| ID | Name |
|----|------|
| A1 | Injection |
| A2 | Broken Authentication and Session Management |
| A3 | Cross-Site Scripting (XSS) |
| A4 | Insecure Direct Object References |
| A5 | Security Misconfiguration |
| A6 | Sensitive Data Exposure |
| A7 | Missing Function Level Access Control |
| A8 | Cross-Site Request Forgery (CSRF) |
| A9 | Using Components with Known Vulnerabilities |
| A10 | Unvalidated Redirects and Forwards |

### Notes

- Updated every 3-4 years
- Version matters: top10@2021#A01 (Broken Access Control) != top10@2017#A1 (Injection)
- ID format changes between versions (A01 vs A1)
- Maps to CWEs

---

## llm-top10

Security risks specific to Large Language Model applications.

### Format

```
secid:weakness/owasp.org/llm-top10[@VERSION]#ITEM
secid:weakness/owasp.org/llm-top10@2.0#LLM01
secid:weakness/owasp.org/llm-top10#LLM01           # Current version
```

### 2025 Edition (v2.0)

| ID | Name |
|----|------|
| LLM01 | Prompt Injection |
| LLM02 | Sensitive Information Disclosure |
| LLM03 | Supply Chain Vulnerabilities |
| LLM04 | Data and Model Poisoning |
| LLM05 | Insecure Output Handling |
| LLM06 | Excessive Agency |
| LLM07 | System Prompt Leakage |
| LLM08 | Vector and Embedding Weaknesses |
| LLM09 | Misinformation |
| LLM10 | Unbounded Consumption |

### Relationships

```
secid:weakness/owasp.org/llm-top10#LLM01 -> maps_to -> secid:weakness/mitre.org/cwe#CWE-1427
secid:weakness/owasp.org/llm-top10#LLM01 -> exploitedBy -> secid:ttp/mitre.org/atlas#AML.T0043
```

### Notes

- AI/ML specific weakness categories
- Maps to CWE and ATLAS
- Updated more frequently than traditional OWASP Top 10

---

## ml-top10

Security risks specific to Machine Learning systems, separate from the LLM Top 10.

### Format

```
secid:weakness/owasp.org/ml-top10[@VERSION]#ITEM
secid:weakness/owasp.org/ml-top10#ML01
secid:weakness/owasp.org/ml-top10@2023#ML01
```

### 2023 Edition

| ID | Name | Description |
|----|------|-------------|
| ML01 | Input Manipulation Attack | Adversarial examples that fool models |
| ML02 | Data Poisoning Attack | Corrupting training data |
| ML03 | Model Inversion Attack | Reconstructing training data from model |
| ML04 | Membership Inference Attack | Determining if data was in training set |
| ML05 | Model Theft | Extracting model weights or behavior |
| ML06 | AI Supply Chain Attacks | Compromising ML dependencies |
| ML07 | Transfer Learning Attack | Exploiting pre-trained model vulnerabilities |
| ML08 | Model Skewing | Biasing model behavior through data manipulation |
| ML09 | Output Integrity Attack | Manipulating model outputs |
| ML10 | Model Poisoning | Directly corrupting model parameters |

### Difference from LLM Top 10

| ML Top 10 | LLM Top 10 |
|-----------|------------|
| Broader ML systems (vision, classification, etc.) | Specifically Large Language Models |
| Focuses on model-level attacks | Focuses on application-level risks |
| More technical/research oriented | More deployment/integration oriented |

### Relationships

```
secid:weakness/owasp.org/ml-top10#ML01 -> related_to -> secid:ttp/mitre.org/atlas#AML.T0015
secid:weakness/owasp.org/ml-top10#ML02 -> related_to -> secid:weakness/owasp.org/llm-top10#LLM04
```

### Notes

- Focuses on traditional ML security (not just LLMs)
- Covers attacks at training and inference time
- Complements the LLM Top 10 for non-LLM systems

---

## agentic-top10

Security risks specific to AI agents - autonomous systems that can plan, act, use tools, and make decisions with limited human oversight. Released December 2025.

### Format

```
secid:weakness/owasp.org/agentic-top10#ASIXX
secid:weakness/owasp.org/agentic-top10#ASI01
secid:weakness/owasp.org/agentic-top10#ASI06
```

### The 10 Risks (2026 Edition)

| ID | Name | Description |
|----|------|-------------|
| ASI01 | Agent Goal Hijack | Attacker alters agent's objectives through malicious content |
| ASI02 | Tool Misuse and Exploitation | Agent uses legitimate tools in unsafe ways |
| ASI03 | Identity and Privilege Abuse | Agent escalates privileges or impersonates |
| ASI04 | Agentic Supply Chain Vulnerabilities | Runtime dependencies (MCP servers, plugins) compromised |
| ASI05 | Unexpected Code Execution | Agent executes unintended code |
| ASI06 | Memory and Context Poisoning | Corrupting agent's persistent memory or context |
| ASI07 | Insecure Inter-Agent Communication | Attacks on agent-to-agent protocols |
| ASI08 | Cascading Failures | Failures propagating through agent chains |
| ASI09 | Human-Agent Trust Exploitation | Social engineering through agent interfaces |
| ASI10 | Rogue Agents | Agents acting outside intended bounds |

### Why Agentic AI Needs Its Own Top 10

Agentic systems introduce unique risks not covered by LLM Top 10:

| Characteristic | Risk Implication |
|----------------|------------------|
| **Autonomy** | Agents act without human approval per action |
| **Tool use** | Agents can execute code, call APIs, modify files |
| **Chaining** | Multiple agents collaborate, amplifying risks |
| **Persistence** | Agents maintain state across sessions |
| **Goal pursuit** | Agents may find unexpected ways to achieve objectives |

### Key Principle: Least Agency

> Only grant agents the minimum autonomy required to perform safe, bounded tasks.

### Real-World Incidents

- Agent-mediated data exfiltration
- Remote code execution via tool misuse
- Memory poisoning attacks
- Supply chain compromise (first malicious MCP server found September 2025)

### Relationship to LLM Top 10

| LLM Top 10 | Agentic Top 10 |
|------------|----------------|
| LLM as component | LLM + tools + autonomy |
| Output risks | Action risks |
| Single-turn focus | Multi-turn, persistent focus |
| Human in loop assumed | Minimal human oversight |

### Supporting Resources

| Resource | Description |
|----------|-------------|
| State of Agentic Security 1.0 | Current landscape analysis |
| Agentic Security Solutions Landscape | Tool comparison |
| Practical Guide to Securing Agentic Applications | Implementation guidance |
| OWASP FinBot CTF | Reference application |

### Notes

- Released December 10, 2025
- Developed by 100+ industry experts
- Critical for MCP, LangChain, AutoGPT, CrewAI security
- Complements LLM Top 10, doesn't replace it

---

## ai-exchange

Comprehensive AI security knowledge base with a "Periodic Table of AI Security" organizing threats and controls.

### Format

```
secid:weakness/owasp.org/ai-exchange#THREATID
secid:weakness/owasp.org/ai-exchange#DIRECTPROMPTINJECTION
secid:weakness/owasp.org/ai-exchange#DATAPOISON
```

### Resolution

The lookup URL `https://owaspai.org/goto/{id}/` redirects to the detailed page for each threat or control.

### Threat Categories

#### Prompt Injection

| ID | Name |
|----|------|
| DIRECTPROMPTINJECTION | Direct prompt injection |
| INDIRECTPROMPTINJECTION | Indirect prompt injection |

#### Model Attacks

| ID | Name |
|----|------|
| EVASION | Evasion (adversarial examples) |
| RUNTIMEMODELPOISON | Model poisoning at runtime (reprogramming) |
| DEVMODELPOISON | Development-time model poisoning |
| SUPPLYMODELPOISON | Supply-chain model poisoning |

#### Data Attacks

| ID | Name |
|----|------|
| DATAPOISON | Training/fine-tune data poisoning |
| DEVDATALEAK | Training data leaks |

#### Information Disclosure

| ID | Name |
|----|------|
| DISCLOSUREUSEOUTPUT | Data disclosure in model output |
| MODELINVERSIONANDMEMBERSHIP | Model inversion / Membership inference |
| LEAKINPUT | Model input leak |

#### Model Theft

| ID | Name |
|----|------|
| MODELTHEFTUSE | Model theft through use (input-output harvesting) |
| RUNTIMEMODELTHEFT | Direct model theft at runtime |
| DEVMODELLEAK | Model theft at development-time |

#### Output & Resource

| ID | Name |
|----|------|
| INSECUREOUTPUT | Model output contains injection |
| AIRESOURCEEXHAUSTION | AI resource exhaustion (model DoS) |

### Complete Threat List

| ID | Category |
|----|----------|
| `DIRECTPROMPTINJECTION` | Prompt Injection |
| `INDIRECTPROMPTINJECTION` | Prompt Injection |
| `EVASION` | Model Attack |
| `RUNTIMEMODELPOISON` | Model Attack |
| `DEVMODELPOISON` | Model Attack |
| `SUPPLYMODELPOISON` | Model Attack |
| `DATAPOISON` | Data Attack |
| `DEVDATALEAK` | Data Attack |
| `DISCLOSUREUSEOUTPUT` | Information Disclosure |
| `MODELINVERSIONANDMEMBERSHIP` | Information Disclosure |
| `LEAKINPUT` | Information Disclosure |
| `MODELTHEFTUSE` | Model Theft |
| `RUNTIMEMODELTHEFT` | Model Theft |
| `DEVMODELLEAK` | Model Theft |
| `INSECUREOUTPUT` | Output Handling |
| `AIRESOURCEEXHAUSTION` | Resource Exhaustion |

### Relationship to Controls

Each threat maps to controls in `secid:control/owasp.org/ai-exchange`. Example:

```
secid:weakness/owasp.org/ai-exchange#DIRECTPROMPTINJECTION
  -> mitigated_by ->
secid:control/owasp.org/ai-exchange#PROMPTINJECTIONIOHANDLING
```

### Notes

- Part of the "Periodic Table of AI Security"
- Maps to MITRE ATLAS, CWE, and other frameworks
- Continuously updated with emerging threats
- Controls documented in control/owasp.org/ai-exchange

---

## aivss

The AI Vulnerability Scoring System (AIVSS) extends CVSS concepts to score AI/ML-specific vulnerabilities.

### Format

```
secid:weakness/owasp.org/aivss@1.0
```

### Why AIVSS Exists

Traditional CVSS doesn't capture AI-specific risk factors:

| CVSS Limitation | AI Reality |
|-----------------|------------|
| Binary exploitability | AI attacks have probabilistic success |
| Static attack vector | AI attacks adapt and evolve |
| Single impact type | AI failures cascade across systems |
| Fixed temporal metrics | AI vulnerabilities change with model updates |

### AIVSS Metric Groups

| Group | Metrics |
|-------|---------|
| **Base** | Attack complexity, privilege required, user interaction |
| **AI-Specific** | Model access level, attack transferability |
| **Impact** | Confidentiality, integrity, availability, safety |
| **Temporal** | Exploit maturity, remediation level |

### AI-Specific Factors

| Factor | Description |
|--------|-------------|
| **Model Access** | Black-box, gray-box, white-box |
| **Transferability** | Does attack work across models? |
| **Detectability** | How easily can attack be detected? |
| **Reversibility** | Can the impact be undone? |

### Notes

- Under active development
- Complements CVSS for AI vulnerabilities
- Used by security teams assessing AI risks
- Maps to OWASP AI Top 10 risks
