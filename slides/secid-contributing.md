---
marp: true
theme: csa
paginate: true
header: 'SecID Contributing'
footer: 'Cloud Security Alliance · secid.cloudsecurityalliance.org'
---

<!-- _class: title -->

# Contributing to SecID

**How to add, update, and improve registry entries**

Kurt Seifried · Chief Innovation Officer · Cloud Security Alliance
kseifried@cloudsecurityalliance.org · github.com/kurtseifried

github.com/CloudSecurityAlliance/SecID · CC0 (Public Domain)

---

## What You're Contributing To

**A registry of 709+ security knowledge sources across 10 types**

| Type | Count | Examples |
|------|-------|---------|
| advisory | 42 | CVE, NVD, GHSA, Red Hat, Ubuntu |
| capability | 54 | AWS S3 encryption, Azure RBAC |
| control | 32 | NIST 800-53, ISO 27001, CCM |
| disclosure | 486 | 502 CVE CNA partners |
| methodology | 18 | CVSS, SSVC, IR 8477, STRIDE |
| entity | 14 | MITRE, Red Hat, AWS |
| reference | 34 | RFCs, arXiv, DOIs |
| regulation | 12 | GDPR, HIPAA |
| ttp | 4 | ATT&CK, ATLAS, CAPEC |
| weakness | 13 | CWE, OWASP Top 10 |

Every entry is one JSON file. Adding a source = adding a file.

---

## Registry File Format

**One JSON file per namespace, containing all sources from that organization**

```json
{
  "schema_version": "1.0",
  "namespace": "mitre.org",
  "type": "advisory",
  "status": "published",
  "official_name": "MITRE Corporation",
  "urls": [
    {"type": "website", "url": "https://www.mitre.org/"}
  ],
  "match_nodes": [
    {
      "patterns": ["(?i)^cve$"],
      "description": "Common Vulnerabilities and Exposures",
      "weight": 100,
      "data": { ... },
      "children": [ ... ]
    }
  ]
}
```

---

## Namespace-to-Filesystem Algorithm

**Domain name → reverse-DNS directory path**

```
mitre.org  →  registry/advisory/org/mitre.json
nist.gov   →  registry/control/gov/nist.json
redhat.com →  registry/advisory/com/redhat.json

github.com/advisories  →  registry/advisory/com/github/advisories.json
```

**Steps:**
1. Split domain on `.` → `mitre`, `org`
2. Reverse → `org/mitre`
3. Append path portion (if any) → `org/mitre`
4. Append `.json` → `org/mitre.json`
5. Prepend `registry/{type}/` → `registry/advisory/org/mitre.json`

---

## Match Nodes — The Pattern Tree

```json
"match_nodes": [
  {
    "patterns": ["(?i)^cve$"],
    "description": "Common Vulnerabilities and Exposures",
    "weight": 100,
    "data": {
      "url": "https://www.cve.org/CVERecord?id={id}",
      "examples": ["CVE-2024-1234", "CVE-2021-44228"]
    },
    "children": [
      {
        "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
        "description": "Standard CVE ID format",
        "weight": 100,
        "data": {
          "url": "https://www.cve.org/CVERecord?id={id}",
          "examples": [
            {"input": "CVE-2021-44228", "url": "https://www.cve.org/CVERecord?id=CVE-2021-44228"}
          ]
        }
      }
    ]
  }
]
```

Parent = the source name. Children = specific ID patterns. `{id}` = variable substitution.

---

## Regex Rules

**All patterns must be:**

- **Anchored:** `^pattern$` — no partial matches
- **Case-insensitive where appropriate:** `(?i)^cve$` for source names
- **Case-sensitive for IDs:** `^CVE-\d{4}-\d{4,}$` — preserve source format
- **No catastrophic backtracking:** avoid nested quantifiers like `(a+)+`

**Test your patterns:**
```bash
# Does it match what you expect?
echo "CVE-2021-44228" | grep -P "^CVE-\d{4}-\d{4,}$"

# Does it NOT match what it shouldn't?
echo "CVE-bad" | grep -P "^CVE-\d{4}-\d{4,}$"
```

See `docs/guides/REGEX-WORKFLOW.md` for the full testing workflow.

---

## Adding a New Namespace — Step by Step

**1. Determine the type** — advisory, weakness, ttp, control, capability, methodology, disclosure, regulation, entity, reference

**2. Compute the file path:**
```
example.com → registry/{type}/com/example.json
```

**3. Check if it exists** — if so, add a source section (match_node) to it

**4. If new, start from a template:**
```bash
cp registry/advisory/_template.md registry/advisory/com/example.json
# Edit with the real data
```

**5. Fill in:** urls, match_nodes (patterns, descriptions, examples)

**6. Validate:**
```bash
python3 -c "import json; json.load(open('registry/advisory/com/example.json'))"
```

**7. Submit a PR** — one logical change, descriptive commit message

---

## What Makes a Good Entry

**Essential:**
- `namespace` matches the file path (reverse-DNS algorithm)
- `type` is one of the 10 valid types
- `match_nodes` have anchored regex patterns
- `data.url` has a working URL template with `{id}` variable
- `data.examples` include real, verifiable identifiers

**Good to have:**
- `description` explains what the source is in one sentence
- Multiple `examples` covering common ID formats
- `children` for hierarchical ID systems (subpath patterns)
- Structured `ExampleObject` entries with `{input, url}` for test fixtures

**Avoid:**
- Unanchored patterns (missing `^` or `$`)
- Patterns that match too broadly
- URLs that don't actually work

---

## Research Workflow for New Sources

**Pass 1: Identify the source (10 min)**
- What does it publish? (advisories, controls, techniques, etc.)
- Who publishes it? (organization's domain name)
- What are the identifier formats? (CVE-YYYY-NNNN, CWE-NNN, etc.)
- Where do items resolve to? (URL patterns)

**Pass 2: Document patterns (15 min)**
- Write regex patterns for the ID formats
- Build URL templates with `{id}` substitution
- Gather 3-5 real examples to test with

**Pass 3: Validate (5 min)**
- JSON parses correctly
- Patterns match the examples
- URLs work when you substitute real IDs
- Patterns DON'T match things they shouldn't

**AI agents can help with all of these.** The MCP server + registry-research skill are designed for this.

---

## Common Patterns to Follow

**Look at existing entries for your type:**

| If adding | Good reference file |
|-----------|-------------------|
| Advisory | `registry/advisory/org/mitre.json` — CVE with variable extraction |
| Weakness | `registry/weakness/org/owasp.json` — version_required, disambiguation |
| Control | `registry/control/org/iso.json` — multiple standards in one file |
| TTP | `registry/ttp/org/mitre.json` — ATT&CK with hierarchical subpath |
| Capability | `registry/capability/com/amazon/aws/iam.json` — audit/remediation commands |
| Methodology | `registry/methodology/gov/nist.json` — sub-methodologies via children |
| Disclosure | `registry/disclosure/com/redhat.json` — multi-role CNA with structured CVE data |

**Copy the structure, change the content.** Don't invent new patterns.

---

## The Contribution Process

```
1. Open an issue (optional but recommended for new sources)
      ↓
2. Fork the repo
      ↓
3. Create your file(s) following the format
      ↓
4. Validate JSON + test regex patterns
      ↓
5. Submit a PR with a descriptive commit message
      ↓
6. CSA reviews (regex safety, URL validity, format)
      ↓
7. Merge → auto-deploys to live resolver
```

**PRs that modify regex patterns:** include a note about regex safety (anchored, no backtracking).

**One logical change per PR.** "Add EUVD advisory namespace" not "add 10 random things."

---

## Participation: Beyond PRs

| Level | How | Status |
|-------|-----|--------|
| **Pull requests** | Fork, edit, submit PR — CSA reviews | Live today |
| **Self-service** | Prove security process ownership, get CODEOWNERS write access | Proposed |
| **Federation** | Run your own public resolver, register in namespace | Proposed |
| **Private resolvers** | Internal SecID servers for private data | Proposed |

**Self-service:** You maintain your own namespace files. CSA maintains the spec and infrastructure.

**Federation:** Your resolver is discoverable by other SecID clients. Same protocol, your data.

See `docs/proposals/PARTICIPATION-MODEL.md` for the full proposal.

---

## How AI Agents Help

**AI agents are first-class contributors.** The registry is designed to be AI-writable:

- **Research:** agent browses the source's website, identifies ID formats, writes patterns
- **Validation:** agent tests patterns against real examples, checks URLs
- **Formalization:** agent converts rough notes into properly formatted JSON
- **Review:** agent checks regex safety, format compliance, cross-references

**Tools available:**
- MCP server for looking up existing entries
- `skills/registry-research/` for research workflow
- `skills/registry-validation/` for validation checks
- Claude Code plugin for integrated workflow

> The human decides what to add. The AI does the mechanical work.

---

<!-- _class: closing -->

Kurt Seifried · Chief Innovation Officer · Cloud Security Alliance
kseifried@cloudsecurityalliance.org · github.com/kurtseifried

**SecID** — 709+ namespaces · 10 types · CC0 (Public Domain)
github.com/CloudSecurityAlliance/SecID · Contributions welcome!
