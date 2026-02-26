# SecID Project Strategy

This document captures the strategic thinking behind SecID - the political, organizational, and adoption considerations beyond technical design.

## The Legitimacy Problem

### Why This Matters

Anyone can publish a spec. The challenge is getting adoption. Security professionals are (rightly) skeptical of new standards because:

1. **Standards graveyard**: Many have tried, most have failed
2. **Hidden agendas**: Is this a vendor play? A consulting upsell?
3. **US-centric bias**: Most security standards come from US orgs
4. **Sustainability**: Will this exist in 5 years?

We need to address these concerns explicitly.

### Learning from PURL's Success

PURL succeeded because:
- **Obvious utility**: Solved a real, felt problem
- **Low barrier**: Just a string format, no infrastructure needed
- **No gatekeeper**: Anyone can create a PURL
- **Community governance**: Not owned by one company
- **Incremental adoption**: Use it for one package, then more

We're deliberately copying this playbook. **SecID uses PURL grammar with `secid:` as the scheme** - just as PURL uses `pkg:`, SecID uses `secid:`. We use the exact same proven format, just for security knowledge instead of packages.

## Learning from CVE's Success

CVE is one of the most successful security standards ever created. It's worth understanding why it works and what challenges any similar effort faces.

### What Makes CVE Work

- **Neutral identifier**: Everyone can reference CVE IDs regardless of vendor or affiliation
- **CNA model**: Distributes the assignment burden across the ecosystem
- **Steady progress**: Decades of consistent operation and improvement
- **Universal adoption**: The de facto standard for vulnerability identification

### Structural Challenges Any System Faces

CVE's experience highlights challenges inherent to any global coordination effort:

- **Governance perception**: Any system needs a home, and that home has a geographic/organizational context
- **Scope evolution**: New domains (cloud, AI, IoT) require ongoing adaptation of what's in-scope
- **Community vs control**: Balancing broad participation with consistent governance
- **Funding sustainability**: Long-term infrastructure requires stable, diverse funding

These aren't criticisms of CVE - they're realities of building global security infrastructure that any project (including SecID) must navigate.

### Our Approach

We're applying these lessons to SecID's design:
- Be transparent about governance from day one
- Keep the core spec simple and hard to capture
- Design for decentralization where possible
- Avoid single-source funding dependency

## Governance

### Current Model: BDFL

SecID uses a Benevolent Dictator For Life (BDFL) governance model. **Kurt Seifried** is the current BDFL.

This is a pragmatic choice for early-stage projects:
- Decisions can be made quickly
- Vision stays coherent
- No governance overhead while the project finds its footing

Long-term, we'll evaluate other structures as the community grows. But premature governance complexity kills more projects than it saves.

### PURL Compatibility as Governance Constraint

We deliberately constrain ourselves to be maximally compatible with Package URL (PURL). This isn't just technical - it's a governance choice.

By using PURL grammar, we:
- Inherit their battle-tested design decisions
- Avoid relitigating solved problems
- Make it easier for PURL users to adopt SecID
- Effectively accept their governance on the identifier format itself

This constraint is liberating. We don't have to debate whether `@version` should use `@` or `:` - PURL already decided. We focus our governance energy on security-specific questions, not general identifier syntax.

### Working Group (Future)

A formal SecID Working Group will be established when:
- There's sufficient community interest to warrant it
- The spec is stable enough that governance matters
- Multiple organizations want formal input

Until then, the BDFL model keeps us moving.

## Organizational Strategy

### Cloud Security Alliance Relationship

CSA is positioned as the steward because:
- **Neutral nonprofit**: Not a vendor
- **Global scope**: International chapters
- **AI focus**: Already has AI Security working groups
- **Credibility**: Established in cloud security

But we're careful about perception:

### The AI Database Must Be Separate

Critical strategic decision: The AI vulnerability database should NOT be directly under CSA. Why?

1. **Conflict of interest appearance**: CSA publishes AI controls → CSA tracks AI vulnerabilities → "CSA marks everyone as vulnerable to sell consulting"

2. **Independence**: An AI vuln database needs to be seen as neutral research, not organizational self-promotion

3. **Flexibility**: Different governance, different pace, different risk tolerance

The coordination layer (SecID) can be CSA-affiliated. The AI vuln database should be a separate project that SecID references - "just another entry in the phone book."

### MVP Strategy: Coordination First

We ship in this order:

1. **Phase 1: Coordination Layer**
   - SecID spec
   - Entity registry for existing databases
   - Relationship mappings (CVE↔GHSA↔CWE)
   - No new vulnerability data

2. **Phase 2: Community Adoption**
   - Tools using SecID identifiers
   - Community contributions to entity registry
   - Automated relationship harvesting

3. **Phase 3: AI Vulnerability Database**
   - Separate project
   - References existing SecID infrastructure
   - "Just another source" in the phone book

Why this order? Legitimacy. If we launch with "here's our new vuln database", it looks like a power grab. If we launch with "here's how to navigate existing databases better", then later add one more source, it's natural evolution.

## Geographic Neutrality

### The US-Centric Problem

Most security infrastructure is US-based:
- CVE/CWE: MITRE (US)
- NVD: NIST (US)
- ATT&CK/ATLAS: MITRE (US)
- FIRST: US-headquartered

This creates:
- **Perception issues**: "Another American standard"
- **Real issues**: US export controls, government influence

### Our Approach

1. **Explicit inclusion**: CNVD (China), EUVD (Europe) are first-class citizens from day one
2. **No US-specific dependencies**: GitHub for infrastructure, but it's global
3. **International contributors**: Actively seek non-US entity contributions
4. **Neutral language**: Spec doesn't privilege any region

We can't change where existing databases are located, but we can build a coordination layer that doesn't add US bias.

## Funding and Sustainability

### What We Need

- **Minimal**: Spec maintenance, GitHub hosting (essentially free)
- **Moderate**: Community management, documentation, tooling
- **Ambitious**: Full-time maintainers, API infrastructure, AI database

### Funding Philosophy

Avoid single-source dependency:
- Not 100% government (reduces geographic/political concerns)
- Not 100% corporate (reduces capture risk)
- Not 100% volunteer (ensures sustainability)

Ideal mix:
- Foundation grants for infrastructure
- Corporate sponsorship (multiple) for specific features
- Community contributions for content
- CSA for organizational home

### What We're NOT Doing

- **Paid tiers**: The spec is free forever
- **Certification revenue**: Not a compliance checkbox
- **Consulting upsell**: No hidden monetization

If SecID becomes a revenue vehicle, it's already failed.

## Adoption Path

### Phase 1: Be Useful to AI

Our first adopters are AI systems:
- LLMs doing security research
- AI-powered vulnerability management
- Automated threat intelligence

Why? Because AI doesn't have institutional inertia. An LLM will use whatever format is most useful for reasoning about security relationships.

If we can show "GPT/Claude can better answer security questions with SecID", human adoption follows.

### Phase 2: Tool Integration

Target integrations:
- OSV (already uses similar concepts)
- GHSA (structured data, cross-references CVE)
- Vulnerability scanners
- SBOM tools

The pitch: "Your tool already tracks CVEs. Add SecID IDs to also track CWEs, ATT&CK techniques, controls - same format."

### Phase 3: Database Adoption

Hardest but most valuable:
- Get databases to publish SecID identifiers
- Get CNAs to include SecID in advisories
- Get NVD to cross-reference

This takes years. We build toward it but don't depend on it for initial value.

## Competitive Landscape

### Potential Objections

**"This duplicates OSV"**
No. OSV is a vulnerability database with a schema. SecID is a coordination layer that references OSV (and CVE, and GHSA, and everything else).

**"This competes with CVE"**
No. We explicitly use CVE as the primary vulnerability identifier. We're adding navigation, not replacement.

**"STIX already does this"**
STIX is a data exchange format focused on threat intel. SecID is an identifier scheme focused on security knowledge navigation. They're complementary - SecID identifiers can appear in STIX objects.

**"Another standard to ignore"**
Fair concern. Our answer: we're not asking you to change your data. Use the same CVEs, GHSAs, CWEs you already use. SecID just gives you a consistent way to reference and link them.

### Why We Might Fail

Being honest about risks:

1. **No adoption**: People don't see the value
2. **Fragmentation**: Forks and variants dilute the standard
3. **Capture**: A vendor or government takes control
4. **Neglect**: Maintainers move on, spec rots
5. **Irrelevance**: AI solves this differently

We can mitigate but not eliminate these risks.

## Entity Registration Philosophy

### Wikidata as Legitimacy Check

For entity registration, we use Wikidata/Wikipedia as soft validation:
- If something has a Wikidata entry, it's "notable enough" to exist
- Wikidata IDs are included in entity files for cross-reference
- This isn't a hard requirement, but helps filter spam

Why not our own registration process?
- Creates gatekeeping
- Requires governance infrastructure
- Slows contributions

Better: "If it's on Wikipedia, it probably exists. If not, explain why it should."

### Collect First, Classify Later

We don't require entities to be fully categorized before adding them. Pattern:

1. Add entity with basic info (name, URLs)
2. Declare ecosystem participation as discovered
3. Add relationships over time
4. Enrich documentation iteratively

This keeps the barrier low. A minimal entity file is still useful.

## The AI Vulnerability Database (Future)

### Why It's Needed

Some AI security issues don't fit traditional vulnerability models:
- Prompt injection attacks (no specific software version, affects model classes)
- Jailbreak techniques (behavioral patterns rather than code defects)
- Model poisoning (training-time attacks across the ML pipeline)
- Agent permission bypasses (architectural patterns)

These issues need tracking. CVE coverage for AI is limited, and CWE has only 4 AI-specific entries. SecID can complement existing efforts by providing a coordination layer while the ecosystem evolves.

### Complementing Existing Efforts

Rather than competing with CVE, an AI-focused database would:
- Cover issues that don't yet fit CVE's current scope
- Feed discoveries back to CVE/CWE as appropriate entries
- Provide faster iteration for a rapidly evolving domain
- Coordinate with (not replace) existing tracking efforts

### The Approach

A separate database that:
- Uses SecID identifiers (`secid:advisory/ai-vuln-db/PI-2024-001`)
- Cross-references ATLAS, OWASP LLM Top 10, CWE (where available)
- Coordinates with CVE for issues that fit traditional models
- Ships when the coordination layer is established

This is Phase 3. We build toward it but don't launch with it.

## Success Metrics

How we'll know if this is working:

### Year 1
- [ ] Spec published and stable
- [ ] 50+ entities documented
- [ ] 3+ tools experimentally using SecID
- [ ] Community contributions from non-founders

### Year 2
- [ ] 500+ entities
- [ ] Major tool integration (OSV, GHSA, or equivalent)
- [ ] AI systems demonstrably using SecID for reasoning
- [ ] International contributors (non-US)

### Year 3
- [ ] Industry recognition (referenced in other standards)
- [ ] Sustainable governance established
- [ ] AI vulnerability database launched
- [ ] Self-sustaining community

## Open Strategic Questions

Things we haven't decided:

1. **Formal incorporation**: Does SecID need its own legal entity?
2. **Trademark**: Should we protect the name?
3. **Certification**: Should there be "SecID compliant" designation?
4. **Commercial use**: Any restrictions on for-profit tools?

These will be decided as the project matures.

