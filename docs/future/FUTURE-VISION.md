# SecID Future Vision: AI-Native Security Knowledge Infrastructure

> **This document explores where SecID could go.** These are possibilities, not commitments. We're sharing this vision to spark discussion and invite collaboration.

---

## The Big Picture

SecID starts as an identifier scheme. But identifiers are just the foundation.

**The vision**: SecID becomes the identity layer for a federated, AI-native security knowledge graph where:

- **Anyone can contribute** - Public registries, organizational overlays, personal research
- **Multiple perspectives coexist** - Disagreements are data, not errors
- **AI is a first-class participant** - Not just consuming knowledge, but building it

---

## Three Principles

Everything follows from these:

1. **Stable identifiers** - PURL grammar gives us references that don't break
2. **Federated data** - Layer public, organizational, and personal knowledge
3. **Conflicts are features** - Different contexts produce different truths; preserve both

---

## What SecID Provides Today

Stable, canonical identifiers for security knowledge:

```
secid:advisory/mitre.org/cve#CVE-2024-1234
secid:weakness/mitre.org/cwe#CWE-79
secid:control/nist.gov/800-53@r5#AC-1
secid:ttp/mitre.org/attack#T1059.003
```

**Current capability**: Given an identifier, resolve to URL(s) where the resource lives.

This is useful. But it's just the beginning.

---

## The Evolution: Federated Knowledge

### Multiple Sources, One Identifier

The same SecID can resolve against multiple data sources:

```
┌─────────────────────────────────────────────────────────────┐
│                     SecID Identifier                        │
│           secid:entity/glossary/model-context-protocol      │
└─────────────────────────────────────────────────────────────┘
                            │
          ┌─────────────────┼─────────────────┐
          ▼                 ▼                 ▼
    ┌──────────┐      ┌──────────┐      ┌──────────┐
    │  Public  │      │   Org    │      │ Personal │
    │ Registry │      │ Registry │      │ Registry │
    ├──────────┤      ├──────────┤      ├──────────┤
    │ canonical│      │ our risk │      │ my notes │
    │ url, desc│      │ assessment│     │ research │
    └──────────┘      └──────────┘      └──────────┘
```

### What Each Layer Contributes

| Layer | Contains | Example |
|-------|----------|---------|
| **Public** | Canonical data, URLs, shared definitions | Official docs, Wikipedia links |
| **Organization** | Your team's assessments, policies, incidents | "We rate this HIGH for our environment" |
| **Personal** | Your research, notes, discoveries | Links to conversations, repos, papers |

### Merged Response

```json
{
  "secid": "secid:entity/glossary/model-context-protocol",
  "sources": {
    "public": {
      "description": "Protocol for LLM-tool integration",
      "canonical_url": "https://modelcontextprotocol.io/"
    },
    "acme-corp": {
      "risk_level": "HIGH",
      "assessment": "Tool injection risks significant for our deployment"
    },
    "personal": {
      "notes": "Need to investigate auth layer requirements",
      "research_links": ["https://github.com/..."]
    }
  }
}
```

---

## The Key Insight: Conflicts Are Valuable

### The Old Way (Loses Information)

Most systems try to resolve conflicts:
- Pick one authoritative source
- Merge into single "truth"
- Hide disagreements

### The Better Way (Preserves Context)

Conflicts are **signals worth keeping**:

```json
{
  "secid": "secid:advisory/mitre.org/cve#CVE-2024-XXXX",
  "severity": {
    "mitre": { "score": "CRITICAL", "rationale": "Remote code execution" },
    "redhat": { "score": "MEDIUM", "rationale": "Requires NFS exposure to untrusted networks" }
  }
}
```

**Why both are valid**: MITRE scores based on worst-case. Red Hat scores based on their hardening guidelines that assume NFS isn't internet-exposed. Different threat models, different answers.

**For AI**: "There are two perspectives on severity. MITRE rates CRITICAL assuming worst-case exposure. Red Hat rates MEDIUM because their deployment guidelines limit the attack surface. Your actual risk depends on your configuration."

**For humans**: Dashboard shows both ratings with context, not a false single answer.

---

## AI as First-Class Participant

### AI Isn't Just a Consumer

In this vision, AI is:

1. **A user** - Queries the knowledge graph
2. **A contributor** - Proposes new connections
3. **A synthesizer** - Explains multiple perspectives intelligently
4. **A maintainer** - Identifies gaps, staleness, inconsistencies

### What This Enables

**Research Partner**
```
"What do we know about MCP security?"

AI traverses graph, finds:
- Your previous research (3 conversations, 1 repo)
- Organization assessment (HIGH risk)
- Related weaknesses (LLM01 - Prompt Injection)
- Gap: No mapping to ATLAS techniques yet
```

**Knowledge Builder**
```
"Based on our conversation, I propose:
- New edge: MCP → vulnerable-to → AML.T0043
- Evidence: This conversation
- Source: personal

Create this entry?"
```

**Perspective Synthesizer**
```
"This CVE has three severity ratings:
- MITRE: CRITICAL (worst-case assumption)
- Red Hat: MEDIUM (hardened deployment assumption)
- Your notes: 'Actually HIGH in our environment due to legacy configs'

Real-world risk depends on deployment context."
```

**Context Loader**
```
When you start a conversation about MCP, AI automatically loads:
- Your previous research
- Org assessments
- Related security data
- Open questions from last session
```

### Multi-Agent Collaboration

Multiple AI agents share the knowledge graph as common ground:

- **Research Agent**: Adds findings to graph
- **Code Review Agent**: Queries graph for known issues
- **Report Writer Agent**: Synthesizes from graph

All reference the same SecIDs → coherent collaboration across agents.

---

## Knowledge Graph Integration

### SecID as Node Identity

```yaml
node:
  secid: secid:entity/glossary/model-context-protocol
  properties:
    type: protocol
    vendor: Anthropic
    status: emerging
```

### Edges Reference SecIDs

```yaml
edge:
  from: secid:entity/glossary/model-context-protocol
  to: secid:weakness/owasp.org/llm-top10@2.0#LLM01
  relationship: vulnerable-to
  properties:
    attack_vector: tool-injection
```

### Portable Queries

SecID becomes a **portable query** that works against any compliant knowledge graph:

```
GET secid:entity/glossary/model-context-protocol

Returns:
- All nodes tagged with this SecID (from all configured sources)
- All edges where this SecID is source or target
- Merged with provenance tracking
```

---

## Expanding What Can Be Referenced

### Concepts as Entities

General knowledge concepts get a `glossary` namespace:

```
secid:entity/glossary/model-context-protocol
secid:entity/glossary/prompt-injection
secid:entity/glossary/retrieval-augmented-generation
secid:entity/glossary/agent-to-agent-protocol
```

In documentation: `[MCP](secid:entity/glossary/model-context-protocol)` - a stable link that resolves to current information.

### Definitions as Entities

Different organizations define the same terms differently. Make this explicit:

```
secid:entity/mitre.org/vulnerability      # MITRE's definition
secid:entity/redhat.com/vulnerability     # Red Hat's operational definition
secid:entity/nist.gov/vulnerability       # NIST's definition
```

Now when someone says "vulnerability," you can ask: whose definition?

---

## Technical Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     Client / API                            │
│  ┌─────────────────────────────────────────────────────────┐│
│  │           Merge & Conflict Preservation                 ││
│  │         (maintains provenance, surfaces conflicts)      ││
│  └─────────────────────────────────────────────────────────┘│
│              │              │              │                │
│              ▼              ▼              ▼                │
│       ┌──────────┐   ┌──────────┐   ┌──────────┐          │
│       │  Public  │   │   Org    │   │ Personal │          │
│       │ Registry │   │ Registry │   │ Registry │          │
│       │ (GitHub) │   │ (GitHub) │   │ (local)  │          │
│       └──────────┘   └──────────┘   └──────────┘          │
└─────────────────────────────────────────────────────────────┘
```

Each registry is text files (YAML frontmatter + Markdown):
- **Git-friendly** - Version controlled, PR-based contributions
- **AI-readable** - Structured data with rich context
- **Human-readable** - Works in any editor, renders on GitHub

---

## What This Enables

### For Security Practitioners
- Query any security concept with a stable identifier
- Get context from multiple sources automatically
- Build on public knowledge with your own assessments

### For Organizations
- Maintain private overlays on public security data
- Share assessments across teams with consistent terminology
- AI-assisted knowledge management

### For the Security Community
- Federated knowledge without central control
- Multiple perspectives preserved, not flattened
- Lower barrier to contribution

### For AI Systems
- Stable references that persist across conversations
- Rich context beyond training data cutoffs
- Explicit handling of uncertainty and disagreement

---

## Summary

**Today**: SecID is an identifier scheme with a registry.

**Tomorrow**: SecID becomes the identity layer for federated security knowledge graphs.

**The mechanism**:
1. Identifier schema (PURL grammar) ✓
2. Overlay data from multiple sources (public → org → personal)
3. Conflicts preserved as signals, not resolved away
4. AI as contributor, not just consumer

**The outcome**: AI-native security knowledge infrastructure where:
- References are stable across time and context
- Perspectives are layered and traceable
- Disagreements inform rather than confuse
- AI and humans collaborate on knowledge building

---

## Get Involved

This vision is ambitious. We can't build it alone.

**Ways to contribute**:
- **Feedback**: Open an issue with questions or suggestions
- **Registry contributions**: Add namespace definitions
- **Tool building**: Create libraries, integrations, visualizations
- **Research**: Explore knowledge graph applications for security

**What we're exploring**:
- Multi-registry merge semantics
- Conflict resolution UX patterns
- AI agent integration protocols
- Knowledge graph query languages

If this vision resonates, we'd love to hear from you.

---

*SecID is a project of the Cloud Security Alliance. This document represents exploratory thinking about future directions.*
