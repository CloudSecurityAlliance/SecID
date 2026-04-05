# Design Decisions

This document captures key design decisions and the reasoning behind them.

## Identifiers Are Just Identifiers

### The Principle

SecID separates concerns into layers:

| Layer | What it does | Status |
|-------|--------------|--------|
| **Identifiers** | Name things | Specified |
| **Registry** | Define what exists, how to resolve | Current |
| **Relationships** | Connect things | Future |
| **Overlays** | Enrich without mutating | Future |

The identifier specification defines how to write a SecID string. That's it. Everything else - relationships between identifiers, enrichments, corrections, history - is layered on top, separately.

### Why This Matters

Early drafts mixed these concerns. The registry files included:
- `replaced_by: ibmredhat` - succession tracking
- `past_names: [redhat]` - historical names
- Detailed relationship data

This felt natural ("keep everything about an entity in one place") but created problems:

**1. Scope creep in the spec**

If the identifier spec defines relationship types, we have to get them right before shipping. But we don't know what relationships people actually need yet.

**2. Registry becomes stateful**

Adding `replaced_by` means registry files track history and change over time. Now you need versioning, conflict resolution, update processes. The registry stops being a simple "what exists" definition.

**3. Premature optimization**

Designing the relationship layer requires answering hard questions:
- Directionality (one-way or bidirectional?)
- Provenance (who said this? when?)
- Conflicts (what if sources disagree?)

We could guess at answers, but we'd probably guess wrong. Better to wait until usage teaches us.

### The PURL Model

Package URL (PURL) takes the same approach. PURL defines how to write a package identifier:

```
pkg:npm/lodash@4.17.21
```

PURL doesn't define:
- How packages relate to vulnerabilities
- How to track package renames
- What metadata to attach

Those concerns are handled by other systems (OSV, GHSA, etc.) that *use* PURLs. PURL is just the identifier.

SecID follows this pattern. **SecID uses PURL grammar with `secid:` as the scheme** - just as PURL uses `pkg:`, SecID uses `secid:`. Everything after `secid:` follows PURL grammar exactly (`type/namespace/name`):

```
secid:advisory/mitre.org/cve#CVE-2024-1234
```

What you can say *about* that identifier - relationships, enrichments, history - is a separate concern.

### The Spec Is a Parser-Building Guide

**This specification is not a recipe for parsing individual SecID strings.** It is a blueprint for building a parser — a system that combines the grammar with registry data to parse, validate, and resolve SecIDs. A standalone regex cannot parse SecIDs, and that's intentional.

SecID's grammar is intentionally ambiguous without the registry. **This is a feature, not a limitation.**

No characters need to be banned from identifiers because the registry resolves every ambiguity:

| Ambiguity | How the Registry Resolves It |
|-----------|------------------------------|
| Where does the namespace end? | Shortest-to-longest matching against registry files |
| Where does the name end? | Longest match against source names in the registry |
| Is this `@` a version delimiter or part of an ID? | The pattern tree's subpath-level regex defines where the item identifier ends — `@` after the match boundary is a version delimiter |
| Is this `#` a subpath prefix or part of a name? | Registry source names can contain `#` — longest match determines the boundary |

**The spec defines components and their ordering. The registry resolves every ambiguity.** A parser built from the spec alone cannot parse a SecID string — it needs the registry data to determine where one component ends and the next begins. This means:

1. **No banned characters** — identifiers preserve upstream formats exactly (`RHSA-2026:0932`, `T1059.003`)
2. **Registry is always authoritative** — if it's not in the registry, it's not valid
3. **Parser and registry stay in sync** — by definition, since parsing requires the registry

This is the same approach DNS takes: you can't resolve a domain name without a nameserver. The format tells you what a domain name looks like; the nameserver tells you what it resolves to. SecID's spec tells you what a SecID looks like; the registry tells you how to parse and resolve it.

### Unknown SecIDs Are Solvable, Not Dead Ends

Because every SecID contains a domain name, **even a SecID with no registry entry carries enough information to bootstrap its own resolution.**

Consider encountering this SecID in the wild with no registry match:

```
secid:advisory/newvendor.com/alerts#NVA-2026-0042
```

A human or AI can:
1. Visit `newvendor.com` — the domain is right there in the identifier
2. Find their security advisory system
3. Understand the `NVA-YYYY-NNNN` ID format
4. Contribute a registry entry with pattern tree (`match_nodes`), URLs, and resolution rules

This is fundamentally different from opaque identifiers (UUIDs, sequential numbers) where an unknown ID gives you nothing to work with. Domain-name namespaces make SecIDs **self-documenting** — they carry enough context to find the source, even with zero prior knowledge.

**The goal is comprehensive registry coverage.** Ideally, every SecID encountered in the wild has a registry entry with parsing rules, URL templates, and resolution patterns. But the domain-name design means the gap between "known" and "unknown" is bridgeable by anyone.

### The Path Forward: Service, Contribution, Federation

A standard like SecID only works if the registry keeps up with the ecosystem. The design enables this through three mechanisms:

**1. Hosted service.** SecID will be implemented as a service (API + MCP server) that resolves SecIDs to URLs. This means consumers don't need to maintain local registry copies — they query the service, which always has the latest registry data. This also means building a parser is optional; most consumers just call the API.

**2. Easy contribution.** The registry is a git repository with one markdown file per namespace. Contributing a new namespace means creating a single file with the organization's domain, their ID patterns, and their URL templates. The barrier to entry is deliberately low — a pull request, not a committee approval. The future self-registration system (DNS/ACME verification) will make this even easier, including for AI agents acting on behalf of organizations.

**3. Federation.** Organizations can run their own registries that overlay or extend the canonical data. A company might maintain private namespace definitions for internal systems, proprietary resolution rules, or organizational context — all compatible with the public ecosystem. Federation means the canonical registry doesn't need to contain everything; it needs to contain the public common ground.

Together, these mean: encountering an unknown SecID is a **temporary state**. The domain name in the identifier tells you where to look. The contribution model makes it easy to add. The service propagates it to all consumers. And federation lets organizations extend the system for their own needs without waiting for the canonical registry.

### What We Gain

**Simpler spec**: The identifier specification is just grammar and types. Ship it, stabilize it, done.

**Flexibility**: Relationship and overlay layers can be designed later, informed by actual usage.

**Clean separation**: The registry defines "what exists." The data layers define "how things connect." Different concerns, different update cadences, different governance.

**No premature commitment**: We're not locked into relationship semantics we designed before understanding the problem.

### What We Defer

The relationship and overlay layers are documented as exploratory thinking (see [RELATIONSHIPS.md](../future/RELATIONSHIPS.md) and [OVERLAYS.md](../future/OVERLAYS.md)). They capture what we're considering, not what we've decided.

We'll design these layers when:
1. The registry has enough content to make relationships valuable
2. We have concrete use cases requiring queryable connections
3. Usage patterns reveal what's actually needed

### Summary

**Identifiers are just identifiers.** They name things. Everything else - connections, enrichments, history - is layered on top, designed separately, shipped when ready.

This keeps the core spec simple and lets us learn before committing to complexity we might get wrong.

---

## Type Evolution

### The Principle

Start with fewer types. Overload them with related concepts. Split only when real-world usage proves it necessary.

### Why Overload?

Creating a new type has costs:
- Documentation in multiple places
- Tooling updates (parsers, validators, resolvers)
- User mental overhead ("is this an advisory or an incident?")
- Governance decisions about edge cases

These costs are worth paying when a type is genuinely needed. They're waste when we could have used an existing type.

### Current Overloading

| Type | Core Purpose | Also Contains |
|------|--------------|---------------|
| `advisory` | Vulnerability publications | Incident reports (AIID, NHTSA, FDA adverse events) |
| `control` | Security requirements | Prescriptive benchmarks, documentation standards |

**Advisory + Incidents**: Both are publications about "something happened." Vulnerability advisories say "this software has a flaw." Incident reports say "this AI system caused harm." The resolution pattern is similar (look up by ID, get details). The consumers overlap. So incidents live in `advisory` until/unless they diverge enough to warrant separation.

**Control + Benchmarks**: A prescriptive benchmark ("test for these behaviors") is semantically a requirement. "Your model should pass HarmBench" is the same kind of statement as "your system should implement PR.AC-1." So benchmarks that define what to test live in `control`.

### When to Split

Create a new type when:

1. **Resolution patterns diverge** - Different URL structures, different APIs, different metadata
2. **Consumers diverge** - Different tools need to filter them separately
3. **Semantics drift** - The "question answered" becomes meaningfully different
4. **Volume justifies it** - Enough examples exist to define clear boundaries

### The Process

1. Put related concepts in the closest existing type
2. Document what's overloaded and why (in registry files)
3. Watch for friction - are users confused? Do tools struggle?
4. When friction exceeds the cost of a new type, split
5. Use the accumulated examples to define the new type precisely

This is data-driven type design. We let usage teach us what needs separation rather than speculating upfront.

### Case Study: The `disclosure` Split

The `disclosure` type is the first type added after the original seven. It was split from `entity` because all four "When to Split" criteria were met:

1. **Resolution patterns diverge** — Disclosure entries resolve to contact information (emails, forms, security.txt URLs), policy documents, and program descriptions. Entity entries resolve to product descriptions and capability lists. The data structures and URL patterns are fundamentally different.

2. **Consumers diverge** — A security researcher who found a vulnerability needs to know *how to report it* immediately. That's a different workflow from looking up what products an organization sells. Vulnerability disclosure tools, coordinated disclosure platforms, and security researchers are a distinct consumer group from asset inventory and product reference tools.

3. **Semantics drift** — `entity` answers "What is this organization/product?" while `disclosure` answers "How do I report a vulnerability to this organization?" These are meaningfully different questions with different urgency profiles.

4. **Volume justifies it** — Every organization with a security presence has disclosure channels: PSIRT programs, bug bounty platforms, security.txt files, disclosure policies. Bug bounty platforms (HackerOne, Bugcrowd, Intigriti) host thousands of programs. RFC 9116 (security.txt) standardizes machine-readable disclosure information.

**Additional factor: freshness requirements.** Disclosure data goes stale fast — contact emails change, reporting forms move, bug bounty programs open and close. Entity data (product names, descriptions) is relatively stable. The `_checked` / `_updated` metadata fields are especially important for disclosure entries, where a stale email address means a vulnerability report goes undelivered.

### Case Study: The `methodology` Split

The `methodology` type is the third type added after the original seven (following `disclosure` at 8 and `capability` at 9). It was created because all four "When to Split" criteria were met:

1. **Resolution patterns diverge** — Methodology entries resolve to process documents with sub-methodology subpaths (e.g., `#strm`, `#crosswalk`). The resolution tree structure supports independently referenceable sub-processes. Reference entries resolve to documents without this process-component subpath convention.

2. **Consumers diverge** — A GRC analyst asking "which methodology should I use for control mapping?" is a different workflow from a researcher citing a document. Methodology consumers need to discover, compare, and select processes — not just retrieve documents.

3. **Semantics drift** — "Follow this process to produce an output" is a fundamentally different primary purpose from "read this document" or "implement this requirement." The **duck test** — "if someone hands you this document and asks 'what do I DO with it?', is the primary answer 'follow this process'?" — cleanly separates methodologies from references and controls.

4. **Volume** — ~40-60 formally published named methodologies is small but the entries are architecturally critical: they provide process provenance for the entire future relationship layer. Without citable methodology identifiers, every relationship assertion in SecID is ungrounded.

**Additional factor: process provenance.** When the relationship layer ships, every assertion ("CCM IAM-01 maps to NIST CSF PR.AC-1") will carry a methodology reference explaining how the mapping was produced and what evidentiary weight it carries. This is the foundational use case that no existing type can serve.

---

## Why No UUIDs?

### The Problem

How do you handle name changes? Companies get acquired, products get rebranded, advisory prefixes evolve:

- Red Hat → IBM Red Hat
- VMware → Broadcom VMware
- RHSA-* → hypothetically IBMRHSA-*

If someone wrote `secid:advisory/redhat.com/errata#RHSA-2024-1234` in a paper, a database, or a tool, what happens when "redhat" becomes "ibmredhat"?

### The UUID Proposal

One solution: give every namespace a stable UUID that never changes.

```
secid:advisory/550e8400-e29b-41d4-a716-446655440000/RHSA-2024-1234
```

The human-readable name ("redhat" or "ibmredhat") becomes just a display label. The UUID is the true identifier. Names can change; UUIDs are forever.

This is how some systems handle stability. It's not wrong.

### Why We Rejected It

**Nobody would use the UUID.**

In practice, people would write:
```
secid:advisory/redhat.com/errata#RHSA-2024-1234
```

Not:
```
secid:advisory/550e8400-e29b-41d4-a716-446655440000/RHSA-2024-1234
```

The human-readable form is what gets typed, copied, shared, and remembered. The UUID would exist in the spec but sit unused in reality.

This means:
- Added complexity in the spec (now we have UUIDs to manage)
- Added complexity in tooling (resolve UUID ↔ name mappings)
- No actual benefit (people still use names, names still change)

We'd have all the costs of UUIDs with none of the benefits.

### The Better Solution

**Handle succession through relationships, not through opaque IDs.**

When a namespace is renamed:

1. **Both names remain valid identifiers**
   - `secid:advisory/redhat.com/errata#RHSA-2024-1234` works
   - `secid:advisory/ibmredhat.com/RHSA-2024-1234` also works

2. **The relationship layer records the change**
   ```
   ibmredhat.com renamedFrom redhat.com
   ```

3. **Resolvers follow the chain**
   - Query for `redhat` → find the rename → resolve via `ibmredhat`
   - Old references never break
   - New references use the current name

### The Tradeoffs

| Approach | Pros | Cons |
|----------|------|------|
| **UUIDs** | Theoretically stable | Nobody uses them; added complexity |
| **Relationships** | Human-readable; matches actual usage | Requires relationship layer; resolver must follow chains |

We chose relationships because:
- Identifiers stay human-readable
- Matches how people actually write and share identifiers
- Complexity is in the resolver, not in every identifier string
- Follows the "identifiers are just identifiers" principle

### PURL Precedent

Package URL (PURL) faces the same challenge. Package ecosystems rename, reorganize, get acquired. PURL doesn't use UUIDs either - it uses human-readable names and relies on the ecosystem to handle transitions.

SecID follows the same philosophy.

### Summary

UUIDs solve a real problem (name stability) but in a way that doesn't match how people actually use identifiers. Relationships solve the same problem in a way that keeps identifiers human-readable and lets the infrastructure handle succession.

**Stability through relationships, not through opaque IDs.**

---

## Namespace Transitions: Case by Case

### The Problem

What happens when organizations change? Companies get acquired, rebrand, merge, or shut down:
- Red Hat acquired by IBM
- VMware acquired by Broadcom
- Sun Microsystems absorbed into Oracle

If someone wrote `secid:advisory/redhat.com/errata#RHSA-2024:1234`, what happens when Red Hat's organizational structure changes?

### Why We Don't Pre-Design This

The temptation is to design a comprehensive namespace transition system upfront. But real-world transitions are messy and unpredictable:

**Example: IBM acquires Red Hat**

IBM acquired Red Hat, but:
- Red Hat brand continues
- Red Hat security infrastructure unchanged
- RHSA/RHBA/RHEA identifiers still work
- CVE database still at access.redhat.com

Nothing needed to change in SecID. If we'd pre-built a transition system, we'd have built for a problem that didn't materialize.

**Contrast: If IBM fully absorbed Red Hat**

If IBM killed the Red Hat brand and migrated everything to IBM infrastructure:
- Old `secid:advisory/redhat.com/*` identifiers stay valid forever (like old URLs)
- New advisories use `secid:advisory/ibm.com/*`
- Relationship layer records: `ibm/errata renamedFrom redhat/errata`
- Resolvers follow the chain

### The Approach

**Handle transitions when they happen, not before.**

1. **Old identifiers are forever** - Once a SecID exists, it exists. We don't break existing references.

2. **New structure gets new identifiers** - If an organization fundamentally changes, new namespaces reflect the new reality.

3. **Relationships connect old and new** - The relationship layer (when built) handles `renamedFrom`, `succeeds`, `aliases`.

4. **Case by case decisions** - Each transition is unique. We evaluate when it happens, with real information, not hypotheticals.

### What About Retired Standards?

A standard being retired is enrichment data, not a namespace change:
- The namespace still exists (historical references remain valid)
- The enrichment layer notes: "retired as of 2024, superseded by X"
- We might also note: "still widely used despite retirement" or "effectively replaced by Y even though not officially retired"

This is metadata about the thing, not a change to its identity.

### Why This Works

This approach mirrors how the internet handles domain changes and URL transitions. Old URLs don't disappear - they redirect, return 404, or keep working. The web is littered with historical references that still resolve.

SecID follows the same philosophy: identifiers are stable, context is layered on top.

---

## Entity Naming: Follow the Source

### The Principle

When naming entities (vendors, products, services), **use what the owner calls it**.

This applies to:
- Vendor/organization namespaces
- Product and service names within namespaces
- Acronyms and abbreviations

### Why This Matters

**Simplicity**: No need to invent naming schemes. The vendor already named their product.

**Recognizability**: Users searching for "ROSA" should find `entity/redhat.com/rosa`, not `entity/redhat.com/openshift-aws-managed-service`.

**Reduced ambiguity**: The vendor's naming is authoritative. We're not guessing.

**Less maintenance**: When the vendor changes names, we follow. We're not maintaining our own parallel naming scheme.

### How It Works

**General concepts use common names:**
```
entity/redhat.com/openshift     # The OpenShift platform generally
entity/microsoft.com/windows    # Windows generally
```

**Variants use official product names:**
```
entity/redhat.com/rosa                # "ROSA" (Red Hat OpenShift Service on AWS)
entity/redhat.com/aro                 # "ARO" (Azure Red Hat OpenShift)
entity/redhat.com/openshift-dedicated # "OpenShift Dedicated"
```

Note: `rosa` not `openshift-rosa`. Red Hat calls it "ROSA", so we call it `rosa`.

### Disambiguation

When names collide (rare), use what makes sense:
- Geographic: `company-uk` vs `company-us`
- Parent company: `subsidiary-parentco`
- Product line: whatever the vendor uses

Don't invent generic suffixes like `-product` or `-service`. Use actual names.

### The Exception

If a source genuinely has no usable names (see next section), we may need to create identifiers. But for vendors and their products, follow the source.

---

## Domain-Name Namespaces

### The Principle

Namespaces are **domain names** of the organizations that publish security knowledge. This enables self-registration, scales without a central naming authority, and provides built-in ownership verification.

### Why Domain Names?

Early versions used short names (`mitre`, `nist`, `redhat`). This worked at small scale (~100 namespaces) but created problems:

1. **Collision risk at scale** - With 10,000+ namespaces, short names would collide. Who gets `ibm`? The mainframe company or the startup?
2. **Central naming authority required** - Someone has to assign and arbitrate short names. That doesn't scale.
3. **No ownership verification** - Anyone could claim `google` in a registry contribution. No way to verify.

Domain names solve all three:

| Problem | Short Names | Domain Names |
|---------|------------|--------------|
| Collisions | Manual arbitration | DNS already solves this |
| Authority | Central committee | Domain ownership = authority |
| Verification | Trust-based | DNS TXT records / ACME challenges |
| Scale | Breaks at 10K+ | Works at any scale |

### Per-Segment Validation

Namespaces are domain names optionally followed by `/`-separated path segments (for platform sub-namespaces). Each segment between `/` must match:

`^[\p{L}\p{N}]([\p{L}\p{N}._-]*[\p{L}\p{N}])?$`

**Allowed characters per segment:**
- `a-z` (lowercase ASCII letters)
- `0-9` (ASCII digits)
- `-` (hyphen, not at start/end)
- `.` (period, as DNS label separator)
- Unicode letters (`\p{L}`) and numbers (`\p{N}`)

**`/` separates segments** within namespaces for platform sub-namespaces.

### Shortest-to-Longest Resolution

Since namespaces can contain `/`, the parser uses **shortest-to-longest matching** against the registry to determine where the namespace ends and the name begins:

```
secid:advisory/github.com/advisories/ghsa#GHSA-xxxx

Try (shortest first):
  "github.com"              → exists? Yes → candidate
  "github.com/advisories"   → exists? Yes → longer candidate (wins)
  "github.com/advisories/ghsa" → not a namespace → stop
```

**Why shortest first?** The most authoritative namespace is the shortest. `github.com` is GitHub itself; `github.com/advisories` is a team within GitHub; `github.com/someuser` is a random user. Starting from the shortest prevents namespace hijacking.

### Platform Sub-Namespaces

Projects hosted on platforms (GitHub, GitLab, etc.) use platform sub-namespaces:

```
github.com/advisories     → GitHub's own advisory database (GHSA)
github.com/llm-attacks    → Research project hosted on GitHub
github.com/thu-coai       → University research group on GitHub
github.com/ModelContextProtocol-Security/vulnerability-db  → Deep sub-namespace (org/repo)
```

Sub-namespaces can be any depth — one path segment (`github.com/advisories`) or multiple (`github.com/ModelContextProtocol-Security/vulnerability-db`). This resolves the old "GitHub projects without domains" question. No project needs its own domain — the platform's domain serves as the namespace root, with path segments for org/user/repo.

**No platform allowlist.** The registry filesystem determines namespace boundaries. If `registry/advisory/com/github/advisories.md` exists, then `github.com/advisories` is a valid namespace. No hardcoded list of "allowed platforms" needed.

### Self-Registration via DNS/ACME (Future)

**Current state:** Namespace registration is manual (pull requests reviewed by maintainers). This works at the current scale of ~150 namespaces.

**Long-term vision:** Automated self-registration where domain owners prove namespace ownership through standard mechanisms:

1. **DNS TXT record** - Add a `_secid` TXT record to verify domain ownership
2. **ACME-style challenge** - Serve a challenge file at a well-known URL
3. **Platform verification** - For sub-namespaces, serve a `.secid-verify` file in the repository

Automated registration is designed for both **human operators** and **AI agents acting on behalf of organizations**. An AI agent managing security operations for an organization should be able to register, update, and maintain that organization's namespace entries programmatically — the same way it might manage DNS records or certificate renewals today. The verification mechanisms (DNS TXT, ACME challenges) are already machine-friendly by design.

After verification, owners manage their registry paths via CODEOWNERS:
```
registry/*/com/redhat/**            @redhat-security-team
registry/*/com/github/advisories/** @github-security
```

### Filesystem Mapping

Namespace domain names are stored using a reverse-DNS directory hierarchy. The domain is split on `.`, segments are reversed, and joined with `/`:

| Namespace | Registry File |
|-----------|--------------|
| `mitre.org` | `registry/advisory/org/mitre.md` |
| `github.com/advisories` | `registry/advisory/com/github/advisories.md` |
| `aws.amazon.com` | `registry/advisory/com/amazon/aws.md` |

Sub-namespaces naturally become subdirectories under the reversed domain, consistent with how Git handles paths.

### Why Not Reverse DNS?

Java uses reverse DNS order for package names (`com.google.android`) because Java's `.` separator also appears inside domain names, making the boundary between namespace and package ambiguous. Reverse order lets the parser read left-to-right through progressively more specific segments.

SecID doesn't need this. Domain names **cannot contain `/`**, and `/` is SecID's namespace-to-name separator. This means `secid:advisory/github.com/advisories/ghsa#...` is unambiguous: the domain portion (`github.com`) is immediately recognizable because domain names have a constrained character set, and the `/` cleanly delimits segments. No reversal needed.

| Approach | Format | Why |
|----------|--------|-----|
| **Java** | `com.google.android.foo` | `.` is ambiguous → reverse to parse left-to-right |
| **SecID** | `google.com/android/foo` | `/` cannot appear in domains → natural order, no reversal |

**Deeply nested subdomains** (e.g., `security.teams.internal.bigcorp.com`) could theoretically produce long namespaces, but in practice public-facing security knowledge comes from short, well-known domains. Cloud providers already use subdomains naturally (`aws.amazon.com`) without issue.

### Domain Name Changes and Defunct Domains

Domain names can change (acquisitions, rebranding) or expire and be re-registered by someone else. SecID handles this through layered separation:

- **DNS/ACME proves ownership at registration time** - not ongoing authority. Once verified, the registry entry persists regardless of future DNS changes.
- **The registry is the source of truth** - after a namespace is registered, it exists in the registry independent of DNS. A domain expiring doesn't invalidate existing SecID identifiers.
- **Equivalence is a relationship-layer concern** - if `twitter.com` rebrands to `x.com`, the mapping between `secid:entity/twitter.com/...` and `secid:entity/x.com/...` belongs in the relationship layer, not the registry.

See [EDGE-CASES.md](../reference/EDGE-CASES.md) for more edge cases including Punycode/IDN normalization, shared platform domains, and trailing DNS dots.

### What We Considered and Rejected

| Character | Rejected Because |
|-----------|------------------|
| `_` | Not DNS-compatible. Use `-` instead. |
| `&` | Shell metacharacter, URL reserved character |
| `@` | Reserved for version separator in SecID grammar |
| `#` | Reserved for subpath separator in SecID grammar |
| Space | Filesystem problems, URL encoding required |

### Examples

```
mitre.org                ✓  Standard domain
nist.gov                 ✓  Government domain
github.com/advisories    ✓  Platform sub-namespace
字节跳动.com              ✓  Unicode domain (ByteDance)
aws.amazon.com           ✓  Subdomain
red_hat.com              ✗  Underscore not allowed in segment
```

---

## Security Tools: Entity + Control Pattern

### The Principle

Security tools that provide security checks should be documented in **both** entity and control:

| Type | What it documents | Example content |
|------|-------------------|-----------------|
| `entity` | What the tool IS | Product description, capabilities, access methods |
| `control` | What security checks it PROVIDES | Specific checks, detections, mappings |

### Why Two Files?

A security scanner is both a **thing** (software you can install, an API you can call) and a **source of security checks** (detections, validations, tests).

Consider MCPShark Smart Scan:
- As an **entity**: It's a security scanner with CLI, API, and dashboard access methods
- As a **control source**: It provides specific security checks like `agent-analysis`, `privilege-escalation-detection`, `owasp-mapping`

Users might want to:
1. Reference the tool itself → `secid:entity/mcpshark.sh/smart`
2. Reference a specific security check the tool provides → `secid:control/mcpshark.sh/smart#agent-analysis`

Both are valid, different use cases.

### How It Works

**Entity file** (`registry/entity/<vendor>/<tool>.md`):
- What the tool is and does
- Access methods (CLI, API, dashboard)
- Integration capabilities (CI/CD, webhooks)
- What it scans (targets, formats)

**Control file** (`registry/control/<vendor>/<tool>.md`):
- Security checks as `#subpath` identifiers
- Check descriptions and categories
- Mappings to standards (OWASP, CIS, etc.)
- Severity levels and remediation guidance

### Example: MCPShark Smart Scan

```
secid:entity/mcpshark.sh/smart                        → The Smart Scan tool itself
secid:control/mcpshark.sh/smart#agent-analysis        → Agent security assessment check
secid:control/mcpshark.sh/smart#owasp-mapping         → OWASP LLM Top 10 mapping check
secid:control/mcpshark.sh/smart#privilege-escalation-detection → Privilege escalation detector
```

### This Pattern Applies To

Any security tool with defined checks:
- **Vulnerability scanners**: Trivy, Grype, Snyk
- **SAST tools**: Semgrep, CodeQL
- **Cloud security**: Prowler, ScoutSuite
- **AI/MCP scanners**: MCPShark Smart Scan
- **Compliance scanners**: OpenSCAP, InSpec

### Related Pattern: Weakness + Control Pairing

Some frameworks define both weaknesses AND controls (like OWASP AI Exchange):

```
secid:weakness/owasp.org/ai-exchange#DIRECTPROMPTINJECTION     → The threat
secid:control/owasp.org/ai-exchange#PROMPTINJECTIONIOHANDLING  → The mitigation
```

Document in both types when the source provides both perspectives.

---

## Open Question: Sources Without Native Identifiers

### The Problem

Some valuable data sources don't have clean identifiers. Consider:

- A spreadsheet of AI weaknesses with paragraph descriptions but no IDs
- A research database with titles but no short codes
- An incident tracker with timestamps and descriptions only

How do we reference entries in these sources?

### Options Under Consideration

**Option 1: Use titles as-is**
```
weakness/aiweakdb.org/Buffer-Overflow-in-Memory-Allocation-Functions
```
- **Pro**: Exactly what the source calls it
- **Con**: Long, unwieldy, may need URL encoding, could change if source updates title

**Option 2: Slugify titles**
```
weakness/aiweakdb.org/buffer-overflow-memory-allocation
```
- **Pro**: URL-safe, readable, shorter
- **Con**: Loses precision, potential collisions, we're now transforming the source name

**Option 3: Content hash**
```
weakness/aiweakdb.org/a3f2b8c9
```
- **Pro**: Guaranteed unique, stable if content is stable
- **Con**: Meaningless to humans, changes if content changes

**Option 4: Assign sequential IDs**
```
weakness/aiweakdb.org/AIWD-001
```
- **Pro**: Short, clean, CVE-like
- **Con**: We become the ID authority, not the source. Governance burden.

**Option 5: Use row/position**
```
weakness/aiweakdb.org/row-42
```
- **Pro**: Traceable to source
- **Con**: Brittle if source reorders, position isn't meaningful

**Option 6: Namespace-defined scheme**
Each namespace documents how it creates IDs. Some might use titles, some hashes, some assigned IDs.
- **Pro**: Flexible, source-appropriate
- **Con**: Inconsistent across namespaces

### Considerations

**Is the source important enough?**
If a source has poor identifiers, maybe we shouldn't be referencing it at a granular level. Reference the source itself, not individual entries.

**Will the source improve?**
If a source might add proper IDs later, using temporary IDs creates migration headaches.

**What's the natural key?**
Most sources have *something* - titles, dates, positions. The most stable natural key is usually best.

**Who maintains the mapping?**
If we assign IDs, we're now responsible for stability. If we use source keys, the source is responsible.

### Current Thinking

1. **Prefer sources with existing IDs** - CWE, CVE, ATT&CK already solved this
2. **For important sources without IDs, use the most stable natural key** - usually title, slugified if needed
3. **Document the scheme in the namespace file** - make it explicit
4. **Accept some messiness** - relationships can help when IDs change
5. **Don't pre-solve** - wait for concrete use cases

### Not Decided

This is an open question. We'll decide when we have a concrete source that requires it, informed by the specifics of that source.

---

## Peer Identifier Schemes

### The Principle

SecID identifies things in the **security knowledge graph** - advisories, weaknesses, controls, entities, TTPs, regulations, and references.

Other identifier schemes handle their domains. We complement them, not replace them.

### Peer Schemes We Defer To

**Established schemes** - canonical, industry-standard identifiers with self-describing string formats:

| Scheme | Identifies | Example | Notes |
|--------|------------|---------|-------|
| `pkg:` | Packages | `pkg:npm/lodash@4.17.21` | PURL - the standard for packages |
| `CVSS:` | Severity scores | `CVSS:4.0/AV:N/AC:L/...` | Self-describing score vectors |
| `spdx:` | Licenses | `spdx:MIT`, `spdx:Apache-2.0` | SPDX license identifiers |
| `doi:` | Research papers | `doi:10.48550/arXiv.2303.08774` | Digital Object Identifiers |
| `swh:` | Source code | `swh:1:cnt:94a9ed...` | Software Heritage immutable refs |

Note: To be a peer scheme, it needs a **self-identifying string format**. Standards that exist but don't have their own identifier syntax (like OWASP AIVSS) are referenced as entities (`secid:entity/owasp.org/aivss`) rather than peer schemes.

### Why Not Wrap Them?

These schemes are already self-identifying. Writing `secid:package:npm/lodash` when `pkg:npm/lodash` exists would be:
- Redundant
- Confusing (two ways to say the same thing)
- Fighting established standards

Instead, use them as peers:

```yaml
advisory: secid:advisory/mitre.org/cve#CVE-2024-1234
affects: pkg:pypi/langchain@0.1.0
severity: CVSS:4.0/AV:N/AC:L/AT:P/PR:N/UI:N/VC:H/VI:H/VA:H
classified_as: secid:weakness/mitre.org/cwe#CWE-94
license: spdx:MIT
paper: doi:10.48550/arXiv.2303.08774
```

### Filling Gaps (If Needed)

If a peer scheme has gaps we need to cover, we could create a compatible namespace:

```
secid:license:spdx.org/MIT              → translates to → spdx:MIT
secid:license:spdx.org/Custom-Corp-1.0  → covers gap SPDX doesn't have
```

This approach:
- Uses the same values as the peer scheme where they exist
- Extends coverage for things the peer doesn't cover
- Maintains compatibility

We haven't needed this yet. If we do, the namespace file would document the translation.

### Deprecated Schemes

**CPE** (`cpe:2.3:a:vendor:product:...`) - Being phased out. CVE/NVD moving to PURL for affected product identification. We don't plan to support CPE.

---

## AI-First Design

### The Principle

SecID is **AI-first**. The primary consumer is AI agents that need to understand, navigate, and work with security knowledge. Human usability and traditional software integration are important but secondary.

This shapes everything about how we design responses and documentation.

### What AI-First Means

When an AI encounters a SecID like `secid:advisory/redhat.com/cve#CVE-2026-0544`, it should be able to:

1. **Look it up** - Query the registry or API
2. **Understand what it is** - Not just "a URL" but what kind of data, why it matters, how it differs from alternatives
3. **Know when to use it** - Guidance on when this source is appropriate vs others
4. **Fetch and parse it** - URLs, formats, libraries, code hints
5. **Work with the data** - Prompting hints, key fields to extract, common pitfalls

This is more than metadata. It's **instructions for AI** on how to be effective with security knowledge.

### Registry Format

Registry files use Obsidian-style format: YAML frontmatter + Markdown body.

```yaml
---
namespace: redhat.com
type: advisory
# ... structured fields
---

# Red Hat Advisory Namespace

[Rich explanatory content for AI/human consumption]

## What This Is
Red Hat CVE pages include their own severity analysis...

## When To Use This
Use this when you need Red Hat-specific impact...

## Parsing Hints
CSAF documents use the VEX profile. Key fields...
```

This format is:
- **Human-readable** - Open in any text editor or Obsidian
- **AI-readable** - Markdown is native to LLMs
- **Machine-parseable** - YAML frontmatter for structured access
- **Git-friendly** - Text diffs work well

### API Responses (Future)

The API will serve registry content in multiple ways:

1. **As-is** - Return the Markdown file directly (AI-native)
2. **JSON** - Structured format for traditional software integration

Both return the same information. JSON provides schemas and programmatic access for systems that need it.

### Not Everything Has a URL

Some SecIDs identify concepts or entities that don't have a canonical URL:
- An organization that has no website
- A defunct product
- An emerging standard not yet published

These entries still provide value through explanatory text, relationships, and context - even without a resolvable URL. We prefer URLs when available (less to maintain), but don't require them.

### Example: What AI Gets

Query: `secid:advisory/redhat.com/cve#CVE-2026-0544`

Response includes:
- **what**: "Red Hat's analysis of this CVE. Unlike the upstream CVE record, includes Red Hat severity rating, affected product matrix, and RHEL/OpenShift-specific remediation."
- **when_to_use**: "Use for Red Hat-specific impact. For canonical description, use secid:advisory/mitre.org/cve#CVE-2026-0544."
- **urls**: Links to HTML page, CSAF/VEX JSON, API endpoint
- **parsing**: "CSAF uses VEX profile. Python: `pip install csaf`. Key fields: `/vulnerabilities/[]/product_status/fixed`"
- **ai_guidance**: "Red Hat severity may differ from NVD CVSS - both are valid perspectives representing different risk contexts."

The AI can now autonomously fetch, parse, interpret, and explain this data.

### Why AI-First?

Security knowledge is complex, fragmented, and constantly evolving. Humans struggle to navigate it. Traditional software can parse it but can't understand context.

AI can do both - but only if we give it the context it needs. SecID is building the foundation for AI agents that genuinely understand security, not just process security data.

---

## Unified `secid:` Scheme

### The Decision

SecID uses a single scheme (`secid:`) with multiple types, rather than separate schemes per type.

We chose:
```
secid:advisory/mitre.org/cve#CVE-2024-1234
secid:weakness/mitre.org/cwe#CWE-79
secid:control/nist.gov/csf@2.0#PR.AC-1
```

Over alternatives like:
```
advisory:mitre/cve#CVE-2024-1234
weakness:mitre/cwe#CWE-79
control:nist/csf@2.0#PR.AC-1
```

### Why Unified?

**PURL grammar compatibility.** PURL uses `pkg:type/namespace/name`. We use `secid:type/namespace/name`. Same grammar, different scheme. This means existing PURL tooling and mental models transfer directly.

**Branding and searchability.** `secid:` is a consistent prefix. You can search a codebase for `secid:` and find all security identifier references. With type-as-scheme, you'd need to know all the schemes.

**No premature fragmentation.** We don't know yet which types will grow large enough to warrant their own scheme. Starting unified means we can split later with data, not speculation.

**Simpler tooling.** One scheme to parse, validate, and resolve. One regex pattern. One URL handler.

### Options Considered

| Option | Pros | Cons |
|--------|------|------|
| **Unified `secid:`** (chosen) | PURL compatibility, searchable, simple | Less type-specific |
| **Type-as-scheme** (`advisory:`, `weakness:`) | Shorter identifiers | Fragments tooling, multiple schemes to register |
| **Hybrid** (split later) | Flexibility | Complexity when/if we split |
| **Registry-as-scheme** (`corpid:`, `secid:`) | Federation | Loses unified search |

### Future Flexibility

If a type grows significantly beyond security scope (e.g., a generic `conference:` scheme), we can split it off. Criteria for splitting:

- Type becomes >50% non-security content
- Clear community that doesn't need security context
- Branding confusion ("why is my conference talk a security ID?")

Until then, we stay unified.

### What About Aliases?

If someone wants `advisory:mitre/cve#CVE-2024-1234` to work alongside `secid:advisory/mitre.org/cve#CVE-2024-1234`, that's an **enrichment layer concern**, not a spec concern. The enrichment database can store:

```yaml
secid:advisory/mitre.org/cve#CVE-2024-1234:
  sameAs:
    - advisory:mitre/cve#CVE-2024-1234
    - cve:CVE-2024-1234
    - https://cve.org/CVERecord?id=CVE-2024-1234
```

The spec defines one canonical form. Aliases are data.

---

## Qualifiers Are for Disambiguation, Not Metadata

### The Principle

PURL qualifiers (`?key=value`) exist for **disambiguation**—distinguishing between two otherwise-identical things. They are not a general-purpose metadata store.

### Appropriate Use

Qualifiers can appear in two positions — on the name (source-level) and on the subpath (item-level):

```
secid:advisory/nist.gov/nvd?lang=ja#CVE-2024-1234      # Source-level: Japanese NVD
secid:advisory/nist.gov/nvd#CVE-2024-1234?lang=ja      # Item-level: this CVE in Japanese
secid:advisory/nist.gov/nvd?format=json#CVE-2024-1234?lang=ja   # Both: JSON API, this CVE in Japanese
```

The qualifier changes *which specific thing* you're identifying, or *how* you want to interact with it. Source-level qualifiers scope the resolution context; item-level qualifiers scope the specific item. If the same key appears in both positions, item-level takes precedence.

### Anti-Pattern: Metadata in Qualifiers

```
# DON'T DO THIS
secid:talk/defcon.org/32#hacking-iot?speaker=John%20Smith&time=2026-08-05T14:00&room=101&rating=5
```

This is tempting but wrong:

**1. Identifiers become unstable.** Speaker name spelled wrong? Time changed? Now your identifier changed.

**2. No canonical form.** Is it `speaker` or `presenter` or `talk_giver`? Everyone picks differently.

**3. Encoding nightmare.** `"Dr. José O'Brien-Smith, PhD"` in a URL qualifier is painful.

**4. Defeats the purpose.** If the identifier contains all the data, why have a data layer?

**5. Bloated identifiers.** URLs become unreadable, uncopyable, unloggable.

### The Rule

**The identifier is the minimal unique handle. Everything else goes in the data layer.**

```
# The identifier
secid:talk/defcon.org/32#smith-hacking-iot

# The data layer
secid:talk/defcon.org/32#smith-hacking-iot:
  speaker: "John Smith"
  title: "Hacking IoT: A Deep Dive"
  scheduled: "2026-08-05T14:00Z"
  room: "Mandalay Bay L"
```

The identifier doesn't change when metadata is corrected. The data layer can be updated, enriched, and queried without touching the identifier.

---

## Follow the Source for Subpaths

### The Principle

When referencing specific items within a database or framework, **use whatever identifier the source uses**.

### How It Works

If BlackHat's schedule uses `talk-2847`:
```
secid:talk/blackhat.com/2026#talk-2847
```

If their website uses URL slugs like `/briefings/smith-hacking-iot`:
```
secid:talk/blackhat.com/2026#smith-hacking-iot
```

If CVE uses `CVE-2024-1234`:
```
secid:advisory/mitre.org/cve#CVE-2024-1234
```

### Why This Matters

**Stability.** The source's identifiers are stable (or at least, the source is responsible for stability, not us).

**Traceability.** You can look at the identifier and find the source directly.

**No governance burden.** We're not inventing and maintaining a parallel ID system.

**Recognition.** Users familiar with the source recognize the identifiers.

### What If There's No Good ID?

Some sources don't have clean identifiers. See "Open Question: Sources Without Native Identifiers" above. The short answer: prefer sources with IDs, use the most stable natural key when forced, and document the scheme.

### Don't Invent When You Don't Need To

The temptation is to create our own cleaner, shorter, more consistent IDs. Resist it. The source's messy IDs are the source's problem. Our job is to point to them reliably.

---

## Preserve Source Identifier Formats

### The Principle

**Subpaths preserve the source's exact identifier format - including special characters like colons, dots, and dashes.**

If Red Hat uses `RHSA-2026:0932` with a colon, we use `RHSA-2026:0932` - not `RHSA-2026-0932`. If ATT&CK uses `T1059.003` with a dot, we use `T1059.003`. No sanitization, no normalization beyond what the source specifies.

### Why This Matters

**1. Human Recognition**

Security practitioners have spent years learning identifier formats. `RHSA-2026:0932` is immediately recognizable to anyone who works with Red Hat systems. `RHSA-2026-0932` (with dash instead of colon) looks wrong - and it is wrong, because that's not what Red Hat uses.

**2. No Translation Layer**

If we sanitized identifiers, users would need to mentally translate:
- "I see `RHSA-2026-0932` in SecID, but I need `RHSA-2026:0932` for Red Hat's website"
- "The colon became a dash... or was it the other way around?"

By preserving the source format, what you see in SecID is what you use everywhere else.

**3. No Information Loss**

What if a source legitimately uses both `FOO-2026:001` and `FOO-2026-001` for different things? Character substitution would create ambiguity. Preservation avoids this entirely.

**4. Copy-Paste Workflow**

Copy `RHSA-2026:0932` from a SecID, paste into:
- Red Hat's website search → works
- Google → works
- Vulnerability databases → works

No mental translation, no mistakes.

### Examples

| Source | Their Format | Why That Format |
|--------|--------------|-----------------|
| Red Hat errata | `RHSA-2026:0932` | Colon separates year from sequence number |
| CVE | `CVE-2024-1234` | Industry standard since 1999 |
| ATT&CK | `T1059.003` | Dot separates technique from sub-technique |
| NIST CSF | `PR.AC-1` | Dot separates function.category, dash for number |
| ISO 27001 | `A.8.1` | Annex.Section.Subsection hierarchy |

Each format makes sense for its source. We don't judge or transform - we preserve.

### What We Do Normalize

Only these components are normalized:
- **Type**: Always lowercase (`advisory` not `Advisory`)
- **Namespace**: Always lowercase (`mitre` not `MITRE`)

Names and subpaths preserve the source format exactly.

### The Registry Documents Format

Each registry file's pattern tree (`match_nodes`) documents the expected format. (See "Nested Pattern Matching" section below for the current tree structure.) For example, the errata source's subpath-level children:

```json
"children": [
  {"patterns": ["^RHSA-\\d{4}:\\d+$"], "description": "Red Hat Security Advisory (note colon separator)"},
  {"patterns": ["^RHBA-\\d{4}:\\d+$"], "description": "Red Hat Bug Advisory"},
  {"patterns": ["^RHEA-\\d{4}:\\d+$"], "description": "Red Hat Enhancement Advisory"}
]
```

The pattern matches the exact format practitioners already know.

---

## Flexible Input Resolution: Try Multiple Interpretations

### The Principle

**Resolvers try the input as-is first, then try percent-decoded. The registry determines what matches.**

Rather than mandating that users provide SecIDs in a specific encoding, we accept input in any form and try multiple interpretations against the registry.

### Why Not Mandate One Form?

In practice, people will provide SecIDs in different forms:
- Copy-pasted from a URL: `IAM-12/Auditing%20Guidelines`
- Typed by hand: `IAM-12/Auditing Guidelines`
- From a system that pre-encoded: `RHSA-2026%3A0932`
- From a system that didn't: `RHSA-2026:0932`

Mandating one form means rejecting valid input. Users shouldn't need to know whether to encode or not.

### The Resolution Strategy

1. **Try as-is** - Most inputs are already in human-readable form
2. **Try percent-decoded** (if input contains `%`) - Handles URL-encoded input

The as-is check runs first so that if a source literally uses `%20` in an identifier (unlikely but possible), it matches before decoding could misinterpret it.

### Why Not Strip Quotes or Backticks?

Tempting, but dangerous. If someone provides `secid:control/cloudsecurityalliance.org/ccm#IAM-12/"Auditing Guidelines"`, those quotes might be:
- Presentation delimiters (human wrapped it in quotes) → quotes aren't part of the ID
- Part of the identifier (source actually uses quotes) → quotes ARE part of the ID

We can't tell the difference. The registry can - if a pattern matches with quotes, they're part of the ID. If no match with quotes but a match without, the resolver doesn't find it. The user gets a "not found" and can try without quotes.

Automatically stripping characters risks misidentifying things.

### Backend Storage Is an Implementation Choice

Since resolvers handle both encoded and unencoded forms, backends can store whichever is convenient:
- **Database**: Store unencoded (string fields handle spaces)
- **Filesystem**: Store encoded (filenames need it)
- **KV store**: Either way

The resolver bridges the gap between user input and stored form.

### Registry Patterns Match Human-Readable Form

Pattern authors write what they see in the source documentation. The registry stores `^Auditing Guidelines$` (with literal space), not `^Auditing%20Guidelines$`. The resolver is responsible for getting input into the form that patterns expect.

---

## Reference System, Not Numbering Authority

### The Principle

**SecID provides a grammar and registry for referencing security knowledge. SecID does not assign identifiers—those come from their respective authorities.**

This is a deliberate, foundational constraint.

### What This Means

| SecID Does | SecID Does NOT Do |
|------------|-------------------|
| Provide a grammar (`secid:type/namespace/name#subpath`) | Assign CVE-2024-1234 (MITRE does that) |
| Maintain a registry of identifier *systems* | Assign GHSA-xxxx-yyyy (GitHub does that) |
| Define how to reference existing identifiers | Assign CWE-79 (MITRE does that) |
| Resolve identifiers to URLs | Assign AVID-2025-V001 (AVID does that) |

### The PURL Analogy

This mirrors how Package URL (PURL) works:
- PURL doesn't assign `lodash@4.17.21` — npm does
- PURL provides `pkg:npm/lodash@4.17.21` as a consistent reference

Similarly:
- SecID doesn't assign `CVE-2024-1234` — MITRE does
- SecID provides `secid:advisory/mitre.org/cve#CVE-2024-1234` as a consistent reference

### "I Have a Vulnerability and Need an ID"

If someone asks SecID to assign an identifier for their vulnerability, the answer is:

> "SecID can't help with that directly. You need to get an identifier from an appropriate authority:
> - **CVE**: Request from MITRE or a CNA
> - **GHSA**: Report through GitHub Security Advisories
> - **AVID**: Submit to the AI Vulnerability Database
> - **Your own system**: Create your own advisory namespace with your own IDs
>
> Once your advisory has an identifier from an authority, SecID provides a consistent way to reference it. If you create 'FooSec Advisories' with ID 'FSA-2025-001', we can add your namespace to the registry, and `secid:advisory/foosec.com/fsa#FSA-2025-001` becomes a valid reference."

### Why This Constraint?

**1. Separation of concerns.** Assigning identifiers and referencing identifiers are different jobs requiring different governance structures. Mixing them creates conflicts.

**2. Respect for authorities.** MITRE, NIST, OWASP, and others have earned authority in their domains through years of work. SecID complements them, not competes.

**3. Avoiding scope creep.** If SecID assigned IDs, we'd need:
   - Policies for what qualifies
   - Dispute resolution processes
   - Editorial review
   - Long-term maintenance commitments

   That's a different project.

**4. Enabling trust.** Organizations can adopt SecID knowing it won't try to become a competing authority in their domain.

### What If We Need an AI Vulnerability Database?

If the security community needs a new identifier system (e.g., for AI vulnerabilities not covered by existing authorities), that should be a separate project with its own governance. SecID would then reference it, just like we reference CVE, GHSA, and AVID.

The clean separation: SecID is the grammar and registry for referencing. Identifier assignment is someone else's job.

---

## Registry Architecture: Hierarchical, One File Per Namespace

### The Principle

The registry uses a flat, hierarchical structure where **every level is queryable** and **each namespace is a single file** containing all its sources.

### The Hierarchy

```
secid:advisory                               → registry/advisory.md
secid:advisory/redhat.com                    → registry/advisory/com/redhat.md
secid:advisory/redhat.com/cve               → section within com/redhat.md
secid:advisory/redhat.com/cve#CVE-2026-1234 → resolved URL from rules in com/redhat.md
```

Every level returns useful information:

| Query | Returns |
|-------|---------|
| `secid:advisory` | Type definition — what advisories are |
| `secid:advisory/redhat.com` | Namespace definition — what Red Hat publishes |
| `secid:advisory/redhat.com/cve` | Source definition — Red Hat CVE pages, root URL |
| `secid:advisory/redhat.com/cve#CVE-2026-1234` | Resolved URL to specific entry |

### File Structure

```
registry/
  advisory.md                      ← Type definition (what is an advisory?)
  advisory/
    org/
      mitre.md                     ← Namespace: MITRE CVE
    com/
      redhat.md                    ← Namespace: ALL Red Hat sources in ONE file
      github/                      ← GitHub platform sub-namespaces
        advisories.md              ← Namespace: GHSA
  weakness.md                      ← Type definition (what is a weakness?)
  weakness/
    org/
      mitre.md                     ← Namespace: CWE
      owasp.md                     ← Namespace: ALL OWASP taxonomies in ONE file
  control.md                       ← Type definition
  control/
    gov/
      nist.md                      ← Namespace: ALL NIST frameworks in ONE file
    org/
      iso.md                       ← Namespace: ALL ISO standards in ONE file
  entity.md                        ← Type definition
  entity/
    com/
      redhat.md                    ← Organization definition
    org/
      mitre.md                     ← Organization definition
```

### Why One File Per Namespace (No Subdirectories)

**Rejected alternative:**
```
registry/advisory/com/redhat/_index.md
registry/advisory/com/redhat/cve.md
registry/advisory/com/redhat/errata.md
```

**Why we don't do this:**

1. **Most namespaces have few sources.** Red Hat has ~4 (cve, errata, bugzilla). MITRE has ~1 (cve). Splitting into multiple files adds complexity without benefit.

2. **KV store simplicity.** The API uses a key-value store. One namespace = one key = one file. No need to reassemble multiple files.

3. **All rules in one place.** When maintaining a namespace, everything is in one file — no hunting across subdirectories.

4. **Future scaling uses reverse-DNS directory hierarchy** (`registry/advisory/com/redhat.md`), which provides natural grouping by TLD.

### Namespace File Format

Each namespace file contains:
- Frontmatter with namespace metadata
- Sections for each source with ID patterns and URL templates
- Narrative documentation

```yaml
---
namespace: redhat.com
full_name: "Red Hat"
website: "https://redhat.com"
type: vendor
status: active
---

# Red Hat (Advisory Namespace)

Red Hat provides multiple advisory and vulnerability tracking systems.

## Sources

### cve

Red Hat CVE pages with Red Hat-specific severity analysis.

| Field | Value |
|-------|-------|
| id_pattern | `CVE-\d{4}-\d{4,}` |
| url_template | `https://access.redhat.com/security/cve/{id}` |
| example | `secid:advisory/redhat.com/cve#CVE-2025-10725` |

### errata

Red Hat Errata advisories (RHSA, RHBA, RHEA).

| Field | Value |
|-------|-------|
| id_pattern | `RH[SBEA]A-\d{4}:\d+` |
| url_template | `https://access.redhat.com/errata/{id}` |
| example | `secid:advisory/redhat.com/errata#RHSA-2025:1234` |
```

### KV Store Design

The API uses a simple key-value lookup:

```
Request: secid:advisory/redhat.com/cve#CVE-2025-1234

1. Parse: type=advisory, namespace=redhat.com, name=cve, subpath=CVE-2025-1234
2. KV lookup: key="advisory/redhat.com" → returns redhat.md content
3. Find "cve" section, get id_pattern and url_template
4. Validate subpath against id_pattern
5. Apply url_template: https://access.redhat.com/security/cve/CVE-2025-1234
```

For type queries:
```
Request: secid:advisory

1. Parse: type=advisory (no namespace)
2. KV lookup: key="advisory" → returns advisory.md content
3. Return type definition
```

### Regex Patterns: PCRE2 Safe Subset

ID patterns use **PCRE2** syntax with a safe subset for compatibility.

#### Why PCRE2, Not PCRE (PCRE1)?

PCRE2 is the successor to the original PCRE library. We chose PCRE2 because:

| Aspect | PCRE1 | PCRE2 |
|--------|-------|-------|
| **Maintenance** | Deprecated since 2017 | Actively maintained |
| **Security** | Had various CVEs over time | Improved security, better fuzzing |
| **API** | Complex, inconsistent | Cleaner, more consistent API |
| **Unicode** | Bolt-on support | Native Unicode support (UTF-8/16/32) |
| **JIT** | Optional, separate | Built-in JIT compiler |
| **Memory** | Static limits | Dynamic memory management |
| **Backtracking** | Harder to control | Better ReDoS protection |

**Key reasons for SecID:**

1. **Industry convergence** - Python 3.11+ uses PCRE2 internally, PHP 7.3+ uses PCRE2, many modern tools default to it
2. **ReDoS protection** - Better backtracking limits prevent regex denial-of-service attacks
3. **Future-proof** - PCRE1 is end-of-life; specifying PCRE2 aligns with where implementations are going
4. **Unicode-native** - Security identifiers increasingly include international characters

#### The Safe Subset

We use a **safe subset** of PCRE2 for maximum compatibility:

- **Works in**: Python `re`, JavaScript, Go `regexp`, Rust `regex`, Java `Pattern`
- **Avoid**: lookahead/lookbehind, backreferences, possessive quantifiers, recursive patterns
- **Goal**: Simple patterns that work everywhere, no regex DoS risk

Most patterns are straightforward:
```
CVE-\d{4}-\d{4,}
CWE-\d+
T\d{4}(\.\d{3})?
RH[SBEA]A-\d{4}:\d+
GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}
```

The safe subset will be formally defined after stress-testing with real-world patterns. The principle: if a pattern requires advanced PCRE2 features, it's probably too complex for an ID pattern.

### Enrichment and Relationship Data

Enrichment and relationship data live in **separate repositories**, not in the SecID registry:

```
secid-registry/           ← This repo: identifiers and resolution
  registry/
    advisory/redhat.md

secid-data/               ← Separate repo: enrichment data
  advisory/
    redhat/
      cve/
        CVE-2025-1234.md  ← Enrichment for specific CVE

secid-relationships/      ← Separate repo: relationship data
  ...
```

**Why separate?**

1. **Different update cadences.** Registry changes rarely; enrichment data changes constantly.
2. **Different governance.** Registry is curated; enrichment may be community-contributed.
3. **Different sizes.** Registry is small (~hundreds of files); enrichment could be millions.
4. **Clean separation.** Follows "identifiers are just identifiers" principle.

---

## JSON Schema: AI-First Data Modeling

### The Principle

Traditional data formats optimized for software that needed deterministic, single values. The JSON schema for SecID takes an AI-first approach:

- **Provide options with context** rather than forcing single "canonical" choices
- **Let AI reason** about which option fits the current need
- **Include metadata** that aids decision-making

### Example: Multiple URLs with Context

Instead of one lookup URL:
```json
"lookup_url": "https://cve.org/CVERecord?id={id}"
```

We provide multiple with context:
```json
"urls": [
  {"type": "lookup", "url": "https://cve.org/CVERecord?id={id}", "note": "Human-readable page"},
  {"type": "lookup", "url": "https://cveawg.mitre.org/api/cve/{id}", "format": "json", "note": "API, richer data"}
]
```

An AI can now reason: "Need machine-readable data? Use the JSON API. Building a link for a human? Use the HTML page."

### Pattern Selection Rules

We use different patterns based on data characteristics:

| Situation | Pattern | Example |
|-----------|---------|---------|
| Fixed, small set of categories | Named fields | `official_name`, `common_name`, `alternate_names` |
| Open-ended, numerous categories | Arrays with type/context | `urls`, `match_nodes` |
| Identity/classification | Singular values | `namespace`, `type`, `status` |

**Why named fields for names?** An AI reads `official_name` and immediately knows what it is. Arrays with type (like `{"type": "official", "value": "..."}`) require understanding a schema to interpret. Named fields are self-documenting.

**Why arrays for URLs?** 70+ URL types exist. Multiple URLs of the same type are common (primary and fallback endpoints). Context helps AI choose appropriately.

---

## JSON Schema: Null vs Absent Convention

### The Principle

Distinguish between "no data exists" and "not yet researched" to track completeness:

| State | Representation | Meaning |
|-------|----------------|---------|
| Has data | `"field": "value"` | We have the information |
| No data exists | `"field": null` | We looked, nothing to find |
| Not researched | field absent | We haven't looked yet |

For arrays:
- `[]` (empty array) = we looked, there are none
- `null` = we looked, not applicable to this source
- absent = not yet researched

### Why This Matters

This convention enables:

1. **Completeness tracking** - An absent field signals work to be done
2. **Contribution guidance** - Contributors know what needs research
3. **Quality assessment** - Systems can calculate how complete an entry is
4. **Honest representation** - We don't pretend to have data we don't have

### Example

```json
{
  "official_name": "Example Corporation",
  "common_name": null,
  "alternate_names": [],
  "wikidata": null,
  "wikipedia": []
}
```

This says: "The official name is 'Example Corporation'. We looked for a common name but they don't have one. We searched for alternate names and found none. We checked Wikidata - not applicable. We checked Wikipedia - no articles exist."

Compare to all fields being absent - that would mean "we haven't researched this entity at all."

---

## JSON Schema: Status Values and Progression

### The Principle

Registry entry status reflects **documentation completeness and review state**, not the state of the external source.

### Status Values

| Status | Meaning | Field Requirements |
|--------|---------|-------------------|
| `proposed` | Suggested, minimal info | namespace, type, status, official_name required |
| `draft` | Being worked on | Any fields, actively researching |
| `pending` | Awaiting review | All fields present (value, `null`, or `[]`) - nothing absent |
| `published` | Reviewed and approved | Same as pending, but reviewed |

### Key Insight: "Published" Means "Reviewed"

`published` doesn't mean "complete" - it means "reviewed." Empty arrays and `null` values are valid and valuable:

```json
{
  "status": "published",
  "status_notes": "Vendor has no public security page - urls intentionally empty",
  "urls": []
}
```

This is a **feature, not a bug**. Empty values show:
- We looked and couldn't find anything
- This exposes gaps in the security ecosystem
- It invites contribution ("want to add this vendor's security page when they create one?")

### Status Notes

The optional `status_notes` field provides context:

```json
"status": "draft",
"status_notes": "Waiting for vendor response about official URL"
```

```json
"status": "pending",
"status_notes": "All fields complete, ready for maintainer review"
```

### Why This Progression?

1. **proposed → draft**: Encourages early contribution without quality gates
2. **draft → pending**: Self-service; contributor ensures all fields addressed
3. **pending → published**: Quality gate; maintainer review required

This balances open contribution with quality control.

---

## JSON Schema: ID Patterns Design

> **Note:** This section describes the original flat `id_patterns` design. The flat structure has been superseded by the unified nested pattern tree (`match_nodes`). See the "Nested Pattern Matching" section below for the current design. This section is preserved for historical context.

### The Principle

`id_patterns` is **always an array**, even for single patterns. This provides consistency and avoids having both `id_pattern` (string) and `id_patterns` (array) fields.

### Basic Pattern

```json
"id_patterns": [
  {"pattern": "CVE-\\d{4}-\\d{4,}", "description": "Standard CVE ID format"}
]
```

### Multiple ID Types

Sources with multiple ID types use the `type` field:

```json
"id_patterns": [
  {"pattern": "T\\d{4}(\\.\\d{3})?", "type": "technique", "description": "ATT&CK technique"},
  {"pattern": "TA\\d{4}", "type": "tactic", "description": "ATT&CK tactic"},
  {"pattern": "M\\d{4}", "type": "mitigation", "description": "ATT&CK mitigation"}
]
```

### Pattern-Specific URLs

When different ID patterns need different lookup URLs, include `url` in the pattern:

```json
"id_patterns": [
  {"pattern": "ALAS-\\d{4}-\\d+", "type": "al1", "description": "Amazon Linux 1", "url": "https://alas.aws.amazon.com/{id}.html"},
  {"pattern": "ALAS2-\\d{4}-\\d+", "type": "al2", "description": "Amazon Linux 2", "url": "https://alas.aws.amazon.com/AL2/{id}.html"}
]
```

This merged the earlier `id_routing` concept into `id_patterns` - simpler than having two separate structures.

### Format Patterns, Not Validity Checks

These are **format patterns**, not validity checks. A pattern like `CVE-\d{4}-\d{4,}` tells you "this looks like a CVE ID" - whether that specific CVE actually exists is only known when you try to resolve it.

We never know if an ID is valid; we only know if it has a valid format.

### Independent Patterns, Not Chained

All patterns in `id_patterns` are tested independently against the subpath. There is no ordering, priority, or conditional chaining between patterns. All matching patterns contribute resolution URLs.

**What chaining would look like (not supported):** "If pattern A matches, extract a group, then test pattern B against that group." For example, matching `RHSA-2024:1234` with a first pattern, extracting `RHSA`, then routing to a second pattern based on that prefix.

**Why we don't support it:** Independent matching is simple and predictable — each pattern either matches or it doesn't. Chaining adds ordering semantics, conditional logic, and debugging complexity. The current model handles real-world sources (Red Hat errata, ATT&CK techniques, Amazon Linux variants) well with independent patterns.

**May revisit if:** Real-world usage demonstrates sources with ID formats that can't be practically expressed as independent patterns. Until then, complexity stays out.

---

## JSON Schema: Descriptions and Known Values

### The Principle

**Describe classes of objects, not instances.** The registry explains what kinds of things exist, not every individual thing.

### The Rule of Thumb

Ask: "Is this an object or a class of objects?"

- **Classes of objects** → Always describe (what is RHSA vs RHBA vs RHEA?)
- **Unique/important individual objects** → Sometimes describe (ISO 27001 vs 42001 deserve titles as hints)
- **Every instance** → Never describe (not every CVE or RHSA)

### Why This Matters

Descriptions answer the disambiguation question: "I see `IAM-12` in a SecID - what is IAM?" Without this, users need external knowledge or extra lookups.

This is different from enrichment. Enrichment tells you *about* a specific thing ("CVE-2024-1234 affects Linux kernel"). Descriptions tell you *what kind of thing* you're looking at ("IAM means Identity & Access Management, a control domain").

### Source-Level Description

Sources have a `description` field explaining what they contain:

```json
"sources": {
  "errata": {
    "official_name": "Red Hat Security Advisories",
    "description": "Red Hat publishes three types of errata: RHSA (Security Advisory) for security fixes, RHBA (Bug Advisory) for bug fixes, and RHEA (Enhancement Advisory) for new features. Most security work focuses on RHSA."
  }
}
```

This explains the class structure within the source - critical for understanding what you're referencing.

### Pattern-Level Known Values

For patterns with finite, stable value sets, `known_values` enumerates them:

```json
"id_patterns": [
  {
    "pattern": "[A-Z]{2,3}",
    "type": "domain",
    "description": "Control domain. Contains multiple controls.",
    "known_values": {
      "IAM": "Identity & Access Management",
      "DSP": "Data Security & Privacy Lifecycle Management",
      "GRC": "Governance, Risk & Compliance"
    }
  }
]
```

This answers: "I see `#IAM` - what does IAM mean?"

### When to Use Known Values

**Good candidates:**
- Control framework domains (IAM, DSP, GRC)
- Advisory type prefixes (RHSA, RHBA, RHEA)
- ISO standard numbers with their titles (27001, 42001)
- Finite category codes

**Not good candidates:**
- Open-ended sets (individual CVEs)
- Growing sets (specific controls like IAM-01, IAM-02...)
- Self-explanatory values (years, sequential numbers)

### Why This Is Registry Data, Not Enrichment

This walks a line. Technically, "what is IAM" could be considered enrichment. We include it because:

1. **Critical for finding** - You can't effectively use `secid:control/cloudsecurityalliance.org/ccm@4.0#IAM-12` without knowing what IAM means
2. **Class-level, not instance-level** - We describe the category (IAM domain), not every control (IAM-12 details)
3. **Stable** - These category names rarely change; they're not dynamic enrichment
4. **Aids disambiguation** - Helps distinguish IAM (controls) from IAM (cloud services) from IAM (other)

The test: "Does someone need this to understand what a SecID points to, before they even try to resolve it?" If yes, it belongs in the registry.

---

## JSON Schema: Lookup Tables for Non-Derivable URLs

### The Problem

Most sources have predictable URL structures. Given `CVE-2024-1234`, the URL is always `https://cve.org/CVERecord?id=CVE-2024-1234` — simple template substitution.

But some sources have URLs that **can't be computed from the identifier alone**. The OWASP LLM Top 10 is the motivating example:

| ID | URL Slug | Pattern? |
|----|----------|----------|
| LLM01 | `llm01-prompt-injection` | No year prefix |
| LLM02 | `llm022025-sensitive-information-disclosure` | Has `2025` prefix |
| LLM03 | `llm032025-supply-chain` | Has `2025` prefix |

LLM01's slug is `llm01-prompt-injection` (no year), while LLM02-10 all include `2025`. And the human-readable slug portion (`prompt-injection`, `sensitive-information-disclosure`) can't be derived from the ID `LLM01` — you'd have to know the title and know exactly how OWASP slugified it.

No URL template can express this. `https://genai.owasp.org/llmrisk/{id}-{slug}/` would require knowing `{slug}`, which is the whole problem.

### The Solution: `lookup_table`

When URLs can't be computed from a pattern template, map each ID directly to its URL:

```json
{
  "pattern": "^LLM\\d{2}$",
  "lookup_table": {
    "LLM01": {"url": "https://genai.owasp.org/llmrisk/llm01-prompt-injection/", "title": "Prompt Injection"},
    "LLM02": {"url": "https://genai.owasp.org/llmrisk/llm022025-sensitive-information-disclosure/", "title": "Sensitive Information Disclosure"}
  },
  "provenance": {
    "method": "Searched genai.owasp.org listing page, verified each URL loads.",
    "date": "2026-02-22",
    "source_url": "https://genai.owasp.org/llm-top-10/"
  }
}
```

### Why Not Just Use `known_values`?

`known_values` maps IDs to descriptions — it helps disambiguation ("what is LLM01?"). But it doesn't provide URLs. A source can have both: `known_values` for descriptions and `lookup_table` for resolution. They serve different purposes.

### Why Provenance Is Required

Lookup tables are manually assembled data. Unlike URL templates (which are verifiable by construction), lookup table entries can be wrong — a typo in a URL, a stale slug, a URL that worked when entered but later changed.

The `provenance` object records:
- **How** the URLs were found (scraped a listing page, checked each one manually, used an API)
- **When** they were last verified
- **Where** the source data came from

This lets reviewers re-verify the data and future maintainers know where to check when URLs break. Without provenance, a lookup table is unverifiable claims about URLs.

### When to Use

| Situation | Use This |
|-----------|----------|
| Consistent, computable URL pattern | `url` template with `{id}`, `{version}`, variables |
| Inconsistent slugs or non-derivable paths | `lookup_table` |
| Most IDs follow a pattern but some exceptions exist | Both — `url` as fallback, `lookup_table` for exceptions |
| Very large or open-ended set | `url` template (lookup tables don't scale to thousands of entries) |

### The Fallback Relationship

If a pattern has both a `url` template and a `lookup_table`, the lookup table takes priority for IDs it contains. The template serves as a fallback for IDs not in the table. This handles the common case where most entries follow a pattern but a few are inconsistent.

---

## Scope: Labeling and Finding

### The Principle

**SecID is about labeling and finding things. That's it.**

The registry contains:
- **Identity** - What is this thing called?
- **Resolution** - How do I find/access it?
- **Disambiguation** - How do I tell similar things apart?

The registry does NOT contain:
- **Enrichment** - Metadata about the thing (authors, categories, relationships)
- **Judgments** - Quality assessments, trust scores, recommendations
- **Relationships** - How things connect to each other

### Why This Constraint?

Enrichment and relationships belong in separate data layers that reference SecIDs:

1. **Different governance** - Who decides what's "high quality"? Different stakeholders have different opinions
2. **Different update cadences** - Labels change rarely; enrichment data changes constantly
3. **Different controversiality** - "This is called X" is factual; "This is good/bad" is judgment
4. **Scope creep prevention** - Without this constraint, everything becomes registry data

### What We Explicitly Excluded

During JSON schema design, we considered and rejected:

**Relationship fields:**
- `operators[]` - Who operates this source is a relationship, not identity. You don't need to know who operates CVE to find or use CVE.
- `superseded_by` - "X was replaced by Y" is a relationship and a judgment. Belongs in data layer.
- `deprecated_by` - Same as superseded_by, at source level.

**Temporal enrichment:**
- `deprecated_date` - When something happened is enrichment.
- `established` - When source was created is enrichment.
- `publication_date` - Enrichment layer.

**Catalog data:**
- `versions[]` (as simple list) - Replaced by version-level children in the pattern tree for resolution. A catalog of "what versions exist" is enrichment; resolution routing is identity.

**Cross-reference identifiers:**
- `doi`, `isbn`, `issn`, `asin` - These are identifier systems, not fields. They become namespaces (`secid:reference/doi.org/...`). Equivalence between identifiers belongs in the relationship layer.

**Other enrichment:**
- `authors` - Enrichment layer.
- `category` - Enrichment layer (too detailed).
- `issues_type`, `issues_namespace` - Enrichment layer.

### What We Kept for Disambiguation

Some fields walk the line between "finding" and "enrichment." We kept:
- `wikidata[]` - Stable identifiers that help disambiguate entities with similar names
- `wikipedia[]` - Direct access to context that aids disambiguation

These help answer "which MITRE do you mean?" - a finding/disambiguation question, not enrichment.

---

## Disambiguation: Wikidata and Wikipedia

### The Principle

Entities can be ambiguous. "MITRE" could mean the corporation, the MITRE ATT&CK project, or historical organizations. We use external identifiers for disambiguation.

### Why Both Wikidata and Wikipedia?

| Field | Purpose | Characteristics |
|-------|---------|-----------------|
| `wikidata` | Stable disambiguation | Language-neutral, stable Q-numbers, links to all Wikipedia versions |
| `wikipedia` | Direct human context | Human-readable, immediate access, fallback when no Wikidata exists |

### Why Arrays?

Both fields are arrays because entities can map to multiple entries:
- **Mergers** - A merged company might have both old and new Wikidata entries
- **Multiple aspects** - MITRE has entries for the corporation and for specific projects
- **Historical** - Name changes create multiple relevant entries
- **Languages** - Wikipedia pages in different languages can be substantially different

```json
"wikidata": ["Q1116236"],
"wikipedia": ["https://en.wikipedia.org/wiki/Mitre_Corporation"]
```

### Not Every Wikipedia Has Wikidata

Some Wikipedia articles lack corresponding Wikidata entries. Some Wikidata entries have minimal Wikipedia coverage. Having both fields handles these gaps.

---

## Version Resolution: Patterns Over Catalogs

> **Note:** This section describes the original `version_patterns` design. In the current design, version patterns are version-level children in the `match_nodes` tree. See the "Nested Pattern Matching" section below. The reasoning here still applies — the nesting just changed.

### The Problem

Some sources have different URL structures for different versions. CSA CCM v4.0 might be at one URL, CCM v3.0.1 at another. How do we handle this?

### Options Considered

**Option A: Simple version list**
```json
"versions": ["4.0", "3.0.1", "2.1"]
```
Problem: This catalogs what exists but doesn't help with resolution. It's enrichment, not identity.

**Option B: Structured versions with per-version URLs**
```json
"versions": [
  {"version": "4.0", "url": "https://example.com/v4"},
  {"version": "3.0.1", "url": "https://example.com/legacy/v3.0.1"}
]
```
Problem: Still a catalog. Needs updating every time a new version releases.

**Option C: Version patterns with regex routing (chosen)**
```json
"version_patterns": [
  {"pattern": "4\\..*", "url": "https://example.com/v{version}"},
  {"pattern": "3\\..*", "url": "https://example.com/legacy/v{version}"}
]
```
This routes based on the version in the SecID itself (`@4.0.1` → matches `4\..*`).

### Why Patterns?

The version is already in the SecID: `secid:control/cloudsecurityalliance.org/ccm@4.0.1#IAM-12`

Using regex patterns:
1. **Resolution, not catalog** - Routes to the right URL without maintaining a list
2. **Handles future versions** - Pattern `4\..*` works for 4.0, 4.1, 4.2... without updates
3. **Explicit routing** - Clear which URL structure applies to which version range
4. **Consistent with pattern tree** - Same pattern-based routing concept used throughout `match_nodes`

### When to Use

Most sources don't need `version_patterns`. Use the `{version}` placeholder in regular URLs when the pattern is predictable:
```json
"urls": [{"type": "bulk_data", "url": "https://example.com/releases/v{version}"}]
```

Only add `version_patterns` when major versions have incompatible URL structures.

---

## Item-Level Versioning (`#subpath@item_version`)

### The Problem

Some security knowledge sources are git-backed databases where individual items change over time. GitHub Security Advisories (GHSA) are stored in a git repository — the advisory content can be updated, corrected, or enriched after initial publication. The CVE list repository on GitHub has the same characteristic. A GHSA ID identifies the advisory, but not *which revision* of it.

Source-level versioning (`name@version`) handles frameworks that release as a whole: CCM @4.0, OWASP Top 10 @2021. But GHSA doesn't release "version 2.0" of its entire database — individual advisories are updated independently.

### Why Not Qualifiers?

Qualifiers (`?key=value`) are defined as "context that doesn't change identity." But a different revision of an advisory IS meaningfully different content — it might have a corrected severity, updated affected versions, or additional references. This changes what the identifier points to, which means it affects identity.

Additionally, `@version` is the established convention for versioning in the SecID grammar (inherited from PURL). Using `?revision=abc123` would be inconsistent.

### The Solution

Extend the `@` convention to items in the subpath:

```
secid:advisory/github.com/advisories/ghsa#GHSA-cxpw-2g23-2vgw@a1b2c3d
```

The grammar becomes: `secid:type/namespace/name[@version][?qualifiers][#subpath[@item_version][?qualifiers]]`

- `@version` (source version) pins the source as a whole: `ccm@4.0`
- `@item_version` (item version) pins a specific item revision: `#GHSA-xxxx@commit`

### Why This Doesn't Break Parsing

The registry's subpath-level patterns define the item ID boundary. The pattern `^GHSA-[a-z0-9]{4}-[a-z0-9]{4}-[a-z0-9]{4}$` does not include `@`. So in `GHSA-cxpw-2g23-2vgw@a1b2c3d`, the parser:

1. Matches `GHSA-cxpw-2g23-2vgw` against the pattern ✓
2. Sees `@` follows the match boundary
3. Extracts `a1b2c3d` as the item version

If a source's IDs legitimately contained `@`, their pattern would include it, and the parser would know it's not a version delimiter. **The registry resolves the ambiguity.**

### The Key Principle

**The spec teaches you how to build a parser. The registry makes it work.** Item-level versioning is the strongest example of this — without the registry's pattern tree, there's no way to distinguish `@` as a version delimiter from `@` as part of an identifier. With the registry, it's unambiguous.

### When to Use

| Scenario | Use Item Version | Use Source Version |
|----------|------------------|--------------------|
| Git-backed databases (GHSA, CVE list repo) | `#GHSA-xxxx@commit` | — |
| Advisory revisions | `#RHSA-2026:3102@rev2` | — |
| Framework editions | — | `ccm@4.0` |
| Annual releases | — | `top10@2021` |
| Version already in the ID | Neither — it's part of the ID | arXiv `2303.08774v2` |

---

## Why Each Component Does or Doesn't Support Versioning

### The Question

SecID has six grammar components: `secid:type/namespace/name@version?qualifiers#subpath@item_version?qualifiers`. Why do only `name` and `subpath` support versioning?

### The Decision Table

| Component | Versioned? | Rationale |
|-----------|-----------|-----------|
| `secid:` (scheme) | No | Protocol-level changes, not per-identifier. If the grammar itself changes incompatibly, use `secid2:`. Versioning the scheme per-identifier would break every consumer. |
| `type` | No | Categories don't version — they refine or split. `advisory@2` would break every existing identifier using that type. If a type needs rethinking, create a new type. |
| `namespace` | No | Domain names are stable identifiers. Organization changes (acquisitions, rebrands) create new namespaces + relationship records. Also: `namespace@version` would be syntactically ambiguous with `name@version` since namespaces can contain `/` path segments. |
| `name` | **Yes** (`@version`) | Frameworks and databases release as versioned wholes. OWASP Top 10 `@2021`, CCM `@4.0`, ISO 27001 `@2022`. The source publishes a complete artifact at a version — this is the natural versioning unit. |
| `?qualifiers` (both positions) | No | Metadata modifiers that add context, not artifacts with release cycles. `?lang=en` or `?format=json` are view preferences, not versionable things. Qualifiers can appear on both name (source-level) and subpath (item-level) but neither position versions. |
| `#subpath` | **Yes** (`@item_version`) | Individual items within a source can have independent revision histories. A GHSA advisory changes over time (`@a1b2c3d`), a Red Hat erratum gets revisions (`@rev2`). |

### The Underlying Principle

**Versioning exists exactly where artifacts have independent release cycles.** Names version because sources are published artifacts (CCM 4.0 is a release). Subpaths version because items within sources can change independently (a GHSA advisory is updated via git commits). Everything else — scheme, type, namespace, qualifiers — either doesn't change, changes via replacement rather than versioning, or represents metadata rather than artifacts.

---

## Version Resolution Behavior

### The Problem

When version is omitted from a SecID, what should happen? The naive answer — "return the current/latest version" — is wrong for some sources.

Consider:
- `secid:advisory/mitre.org/cve#CVE-2024-1234` — CVE IDs are globally unique. Version is irrelevant. Just resolve it.
- `secid:control/cloudsecurityalliance.org/ccm#IAM-12` — CCM 4.0 is current. Return that, but note that v3.0.1 exists (older docs may reference it).
- `secid:weakness/owasp.org/top10#A01` — **Genuinely ambiguous.** A01 in 2021 is "Broken Access Control." A01 in 2017 was "Injection." These are completely different weaknesses sharing the same identifier.

### Three Resolution Behaviors

The registry declares per-source how the resolver should behave when version is omitted:

| Behavior | When Version Omitted | Use When |
|----------|---------------------|----------|
| `current` (default) | Return the current/latest version. No ambiguity. | IDs are unique across all versions, or the source doesn't meaningfully version (CVE, CWE, GHSA). |
| `current_with_history` | Return the current version, but include a note that other versions exist and may be relevant. | The current version is a sensible default, but older versions are still actively referenced (CCM, ISO 27001). |
| `all_with_guidance` | Return **all matching versions** with disambiguation instructions. | Item identifiers are reused across versions with different meanings. Returning just one would be misleading (OWASP Top 10). |

### Disambiguation Guidance

For `all_with_guidance` sources, the registry includes a `version_disambiguation` field — AI-readable instructions that help a client determine which version was intended based on context it has access to. Example for OWASP Top 10:

> "Versions are released by year. Match the version whose release year is closest to but not after the referring document's publication date. If no date context is available, use the latest version (2021). Note: item numbering restarts with each version — A01 in one version is unrelated to A01 in another."

This is the **"AI on both ends" pattern**: the registry (server side) provides reasoning guidance, and the AI client (consumer side) applies it to the local context it has — publication dates, surrounding references, document age. Neither side alone can resolve the ambiguity, but together they can.

### Why Grammar Keeps Version Optional

The grammar makes `@version` syntactically optional everywhere. The registry makes it semantically required for specific sources via `version_required: true`. This separation is deliberate:

1. **The grammar shouldn't encode source-specific constraints.** Whether version matters depends on the source, not the syntax.
2. **Versionless references are valid questions.** "What does `top10#A01` mean?" is a legitimate query — the answer is "it means different things in different versions, here's how to determine which one."
3. **Graceful degradation.** A client that doesn't understand version requirements still gets useful information back (all versions with guidance), rather than an error.

### The Full Spectrum

```
# Version irrelevant — just resolve it
secid:advisory/mitre.org/cve#CVE-2024-1234           → URL to CVE record
                                                        (unversioned_behavior: current)

# Version significant — sensible default, history noted
secid:control/cloudsecurityalliance.org/ccm#IAM-12    → URL to v4.0 IAM-12
                                                        + note: "v3.0.1 also exists"
                                                        (unversioned_behavior: current_with_history)

# Version ambiguous — all versions with disambiguation guidance
secid:weakness/owasp.org/top10#A01                    → 2021: Broken Access Control
                                                        + 2017: Injection
                                                        + 2013: Injection
                                                        + guidance for determining which
                                                        (unversioned_behavior: all_with_guidance)
```

### Registry Fields

See [REGISTRY-JSON-FORMAT.md](../reference/REGISTRY-JSON-FORMAT.md) for the source-level fields that control this behavior: `version_required`, `unversioned_behavior`, `version_disambiguation`, and `versions_available`.

### Further Reading

See [VERSIONING.md](../reference/VERSIONING.md) for the empirical analysis of how versioning works across security knowledge sources (spoiler: it's rare and shallow), the four API response outcomes, and the full resolution algorithm for graceful version handling.

---

## Nested Pattern Matching (Replacing Flat id_patterns)

### The Problem

The original design had three separate matching concepts at three levels:

1. **Source name** — literal key lookup in the `sources` object
2. **Version patterns** — `version_patterns` array, matches `@version`
3. **ID patterns** — `id_patterns` array, matches `#subpath`

Each had a different schema, different field names, different documentation. But they all do the same thing: match a portion of the string, return data if matched, optionally go deeper.

Literal key lookup for source names also creates a problem: names can contain `@`, `#`, and other characters that the parser needs to handle. Making names regex-matchable means the registry patterns determine boundaries — consistent with the principle that SecID parsing requires registry access.

### The Decision: Unified Pattern Tree

All matching uses a single recursive structure. Each node in the tree has:

- **One or more patterns** (regex, OR alternatives) to match against the current portion of the string
- **Result data** (URLs, descriptions, etc.) to return if matched at this level
- **Optional children** — more specific patterns to match the next portion
- **Optional weight** — for ordering when multiple patterns match

The resolver walks the SecID string left to right, handing each portion to the next level:

1. Match name against name-level patterns. The remaining string passes to children.
2. Match version against version-level patterns (if `@` present). The remaining string passes to children.
3. Match subpath against subpath-level patterns (if `#` present). The remaining string passes to children.
4. At each level, the node returns its data. If nothing remains to match, stop.

**No backtracking, no lookahead across levels.** Each regex only sees its portion of the string. Just chop and pass.

### Node Structure

```json
{
  "patterns": ["(?i)^errata$"],
  "description": "Red Hat Errata advisory system",
  "weight": 100,
  "data": {
    "official_name": "Red Hat Errata",
    "urls": [
      {"type": "website", "url": "https://access.redhat.com/errata/"}
    ]
  },
  "children": [
    {
      "patterns": ["^RHSA-\\d{4}:\\d+$"],
      "description": "Red Hat Security Advisory",
      "weight": 100,
      "data": {
        "type": "security",
        "url": "https://access.redhat.com/errata/{id}"
      }
    },
    {
      "patterns": ["^RHBA-\\d{4}:\\d+$"],
      "description": "Red Hat Bug Advisory",
      "weight": 100,
      "data": {
        "type": "bugfix",
        "url": "https://access.redhat.com/errata/{id}"
      }
    },
    {
      "patterns": ["^RHEA-\\d{4}:\\d+$"],
      "description": "Red Hat Enhancement Advisory",
      "weight": 100,
      "data": {
        "type": "enhancement",
        "url": "https://access.redhat.com/errata/{id}"
      }
    }
  ]
}
```

### Full Example: Red Hat

```json
{
  "namespace": "redhat.com",
  "type": "advisory",
  "match_nodes": [
    {
      "patterns": ["(?i)^errata$"],
      "description": "Red Hat Errata",
      "weight": 100,
      "data": {
        "official_name": "Red Hat Errata",
        "alternate_names": ["RHSA", "RHBA", "RHEA", "Red Hat Security Advisory"],
        "description": "Security fixes (RHSA), bug fixes (RHBA), and enhancements (RHEA).",
        "urls": [{"type": "website", "url": "https://access.redhat.com/errata/"}]
      },
      "children": [
        {
          "patterns": ["^RHSA-\\d{4}:\\d+$"],
          "weight": 100,
          "data": {"type": "security", "url": "https://access.redhat.com/errata/{id}"}
        },
        {
          "patterns": ["^RHBA-\\d{4}:\\d+$"],
          "weight": 100,
          "data": {"type": "bugfix", "url": "https://access.redhat.com/errata/{id}"}
        },
        {
          "patterns": ["^RHEA-\\d{4}:\\d+$"],
          "weight": 100,
          "data": {"type": "enhancement", "url": "https://access.redhat.com/errata/{id}"}
        }
      ]
    },
    {
      "patterns": ["(?i)^cve$"],
      "description": "Red Hat CVE Database",
      "weight": 100,
      "data": {
        "official_name": "Red Hat CVE Database",
        "urls": [{"type": "website", "url": "https://access.redhat.com/security/"}]
      },
      "children": [
        {
          "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
          "weight": 100,
          "data": {"url": "https://access.redhat.com/security/cve/{id}"}
        }
      ]
    },
    {
      "patterns": ["(?i)^bugzilla$"],
      "description": "Red Hat Bugzilla",
      "weight": 100,
      "data": {
        "official_name": "Red Hat Bugzilla",
        "urls": [{"type": "website", "url": "https://bugzilla.redhat.com"}]
      },
      "children": [
        {
          "patterns": ["^\\d+$"],
          "weight": 100,
          "data": {"type": "primary", "url": "https://bugzilla.redhat.com/show_bug.cgi?id={id}"}
        },
        {
          "patterns": ["^CVE-\\d{4}-\\d{4,}$"],
          "weight": 50,
          "data": {"type": "alias", "url": "https://bugzilla.redhat.com/show_bug.cgi?id={id}"}
        }
      ]
    }
  ]
}
```

### Weight

Patterns can optionally carry a `weight` field (integer, 0-200, default 0).

- **0** = no weight / neutral (default, most patterns)
- **100** = standard / preferred match
- **Higher** = more preferred

Weight is returned with results, not used for ordering by the server. The consumer decides how to use weights. The general convention is to prefer the "heaviest" result, but the API doesn't enforce this.

**When to use weight:** When two patterns at the same level can both match the same input. Example: Bugzilla accepts both numeric IDs (weight 100, canonical) and CVE aliases (weight 50, redirects). Both are valid, but the numeric ID is the canonical form.

**When not needed:** Most patterns don't overlap at the same level. If siblings are mutually exclusive (RHSA, RHBA, RHEA), weight is irrelevant and should be omitted.

### Key Properties

1. **Every level returns data.** Query `secid:advisory/redhat.com/errata` → returns errata info. Query `secid:advisory/redhat.com/errata#RHSA-2026:1234` → returns the specific advisory. No special cases for "incomplete" queries.

2. **Mutual exclusivity is checkable.** At each level, you can validate that sibling patterns don't overlap. `^RHSA-` and `^RHBA-` and `^RHEA-` clearly don't conflict. When they do overlap, weight disambiguates.

3. **All matching nodes traversed.** The resolver doesn't stop at the first match — it traverses all matching nodes to completion. Multiple matches are all returned (with weights).

4. **Case sensitivity per-pattern.** Use `(?i)` prefix in the regex for case-insensitive matching. Convention: name-level patterns use `(?i)`, subpath patterns match canonical case. No lossy normalization of the input.

5. **Chop and pass.** Each regex only sees its portion of the string. The resolver splits at grammar boundaries (`@`, `#`) and hands each piece to the appropriate tree level. No backtracking, no lookahead across levels.

6. **Multiple patterns per node.** A node can have multiple regex alternatives (OR). All share the same children and result data. Used when a source is known by multiple names.

### Why This Replaces Three Concepts

| Old Concept | New Equivalent |
|-------------|----------------|
| Source name (literal key in `sources`) | Name-level pattern node |
| `version_patterns` | Version-level children (between name and subpath) |
| `id_patterns` | Subpath-level children |
| `item_version_patterns` | Deeper children within subpath nodes |

One schema, one matching algorithm, any depth. The tree naturally mirrors the SecID grammar: `name[@version][#subpath[@item_version]]`.

### Migration

The current flat `sources` / `id_patterns` / `version_patterns` structure will be migrated to the nested tree when we build the API. The data is the same — it just needs restructuring. Existing YAML+Markdown registry files continue to work as-is during the transition; the JSON format is the one that changes.

---

## Identifier Systems Are Namespaces, Not Fields

### The Problem

Documents often have multiple identifiers: a DOI, an ISBN, an arXiv ID. How do we handle this in the registry?

### Initial Approach (Rejected)

Early drafts had identifier fields on reference entries:

```json
{
  "type": "reference",
  "namespace": "nist.gov",
  "title": "AI RMF",
  "doi": "10.6028/NIST.AI.100-1",
  "isbn": "978-0-...",
  "issn": null,
  "asin": null
}
```

Problems:
1. **Doesn't scale** - Why DOI/ISBN but not arXiv ID, OCLC number, Library of Congress number?
2. **Cross-references** - "This SecID also has DOI X" is a relationship
3. **Wrong model** - DOI, ISBN, etc. are identifier systems with their own resolution

### The Insight

DOI, ISBN, ISSN, arXiv, IETF RFCs are **identifier systems** - they assign IDs and provide resolution. They're peers to SecID, not fields within it.

### The Solution: Namespaces

Standard identifier systems become namespaces in the `reference` type:

```
secid:reference/doi.org/10.6028/NIST.AI.100-1
secid:reference/isbn.org/978-0-13-468599-1
secid:reference/arxiv.org/2303.08774
secid:reference/ietf.org/9110
```

The registry has namespace definitions (`registry/reference/org/doi.md`) that define:
- How to recognize IDs (id_pattern)
- How to resolve them (urls)

### Equivalence Is a Relationship

If a document has both a DOI and a human-readable reference:
```
secid:reference/nist.gov/ai-rmf
secid:reference/doi.org/10.6028/NIST.AI.100-1
```

The fact that these point to the same document is an **equivalence relationship**, belonging in the relationship layer:
```
secid:reference/nist.gov/ai-rmf  sameAs  secid:reference/doi.org/10.6028/NIST.AI.100-1
```

### Layers Clarified

| Layer | Contains | Example |
|-------|----------|---------|
| **Registry** | Identity, resolution, disambiguation | Namespace definitions, URL templates |
| **Relationship** | Equivalence, succession, hierarchy | "A sameAs B", "A supersedes B" |
| **Data** | Enrichment, metadata, attributes | "A is about topic X", "A has author Y" |

This keeps the registry focused on its core job: labeling and finding things.

## All Repositories Are Public

### The Decision

All SecID repositories are public.

### Why

**No secrets exist.** SecID-Service is a Cloudflare Worker that reads public registry data and returns URLs. SecID-Website is a static site. There are no databases, no authentication systems, no API keys baked into application code. The only credential is a Cloudflare deploy token used by CI/CD, which lives in GitHub Actions secrets — never in the repo.

**The attack surface doesn't benefit from obscurity.** Knowing that we use a Cloudflare Worker with path-based routing (`/api/*`, `/mcp/*`, `/*`) tells an attacker nothing useful. The infrastructure is a CDN edge function serving public data. There are no internal networks, no database connection strings, no admin endpoints to discover.

**Consistency with project philosophy.** SecID is CC0, AI-first, and designed to be self-hostable. Making the service code public but hiding how it's deployed contradicts that. Someone who wants to run their own SecID infrastructure needs the operations repo to do it.

**Transparency builds trust.** For a project that aims to be industry infrastructure for security knowledge, hiding infrastructure decisions would undermine credibility. If the deployment is sound, showing it proves that. If it has weaknesses, hiding the config doesn't fix them.

### What This Means

| Repo | Visibility | Contains |
|------|-----------|----------|
| SecID | Public | Spec, registry data, design docs, operations documentation |
| SecID-Service | Public | Cloudflare Worker (API + MCP server) |
| SecID-Website | Public | Cloudflare Pages documentation site |
| SecID-Client-SDK | Public | Client libraries |

## Operations Documentation Lives in This Repo

### The Decision

Infrastructure and operations documentation (bootstrap runbook, DNS decisions, routing config, CI/CD pipeline design) lives in `docs/operations/` within this repo, not in a separate SecID-Operations repository.

### Why

**It's documentation, not code.** The operations content is markdown files describing decisions and procedures — DNS records chosen, routing layout, bootstrap steps, CI/CD design. There's no Terraform, no scripts, no build artifacts that need their own lifecycle. Documentation belongs with documentation.

**Fewer repos reduces overhead.** Five repos where four are empty is worse than one repo with good organization. Each repo needs its own README, its own issue tracker, its own contributor onboarding. That overhead isn't justified for a handful of markdown files.

**One place for the full picture.** This repo already has `docs/reference/INFRASTRUCTURE.md` describing the multi-repo architecture. Operations docs are the natural companion — *what* the architecture is and *how* it's deployed, in the same place. Contributors don't have to cross-reference between repos to understand how things work.

**Extraction is easy if needed later.** If operations ever grows to include real infrastructure-as-code (Terraform, Pulumi), CI/CD scripts with their own tests, or monitoring configuration that needs its own release cycle, splitting out a separate repo is straightforward. Starting merged and splitting later is cheaper than starting split and merging.

### What This Means

Operations documentation lives at `docs/operations/` alongside the existing docs hierarchy:

```
docs/
├── reference/        # Technical specs (formats, versioning, edge cases)
├── explanation/       # Why decisions were made
├── guides/            # Task-oriented how-tos
├── future/            # Aspirational (not commitments)
├── project/           # Internal tracking
└── operations/        # Infrastructure, DNS, deployment, CI/CD
```

If operations outgrows documentation into actual IaC code with its own build/test/release needs, it gets extracted into a separate repo at that point.

## Licensing: CC0 for Content, Apache 2.0 for Code

### The Decision

| Repo | License | Rationale |
|------|---------|-----------|
| **SecID** (spec, registry, docs) | CC0 1.0 | Content. Maximum adoption, zero barriers to use. |
| **SecID-Website** (documentation site) | CC0 1.0 | Content. Same rationale — it's rendered documentation. |
| **SecID-Service** (API + MCP server) | Apache 2.0 | Code. Industry-standard for open-source software. |
| **SecID-Client-SDK** (libraries) | Apache 2.0 | Code. Industry-standard, expected by package registries. |

### Why CC0 for Content

SecID's spec and registry data exist to be adopted as widely as possible. Any licensing friction — even attribution requirements — reduces adoption. CC0 (public domain dedication) removes all restrictions: anyone can use, copy, modify, and redistribute without permission, attribution, or notice.

This is the right choice for:
- The specification (standards should be freely implementable)
- Registry data (factual data about where security knowledge lives)
- Documentation (removing barriers to understanding)

### Why Apache 2.0 for Code

CC0 is unusual for software and creates practical issues:

**Patent protection.** Apache 2.0 includes an explicit patent grant — contributors license any patents they hold that cover their contributions. CC0 has no patent clause. For code that organizations will depend on in production, patent protection matters.

**Legal team familiarity.** Enterprise legal teams routinely approve Apache 2.0 dependencies. CC0 for software is uncommon enough that it triggers additional review, slowing adoption.

**Ecosystem expectations.** Package registries (PyPI, npm, crates.io) and their users expect standard software licenses. Apache 2.0 is one of the most widely used and understood.

**Attribution is reasonable for code.** Unlike a spec (where attribution requirements impede adoption), attribution for a library is normal and expected. Apache 2.0's attribution requirement (keep the LICENSE and NOTICE files) is minimal.

### Why Not MIT?

Apache 2.0 and MIT are both permissive. Apache 2.0 adds:
- Explicit patent grant (MIT is silent on patents)
- Clear contribution terms
- NOTICE file mechanism for attribution

For infrastructure software that organizations depend on, the patent clarity is worth the slightly longer license text.

## SPF Record on Service Subdomains

### The Decision

Every SecID subdomain that hosts services (not email) gets an SPF record denying all email:

```
secid.cloudsecurityalliance.org    TXT    "v=spf1 -all"
```

### Why

The subdomain `secid.cloudsecurityalliance.org` hosts a Cloudflare Worker and Pages site. It will never send email. Without an explicit SPF `-all` record, an attacker could send spoofed email appearing to come from `secid.cloudsecurityalliance.org` — which could be used for phishing attacks targeting CSA's reputation.

`v=spf1 -all` tells mail servers: "this domain sends no email; reject anything claiming to come from it." This is a low-effort, high-value hardening step that should be applied at domain creation time, not retrofitted later.

## Content Type Qualifier for Resolution Results

### Decision

Resolution results include an optional `content_type` field containing the MIME type of the resource at the URL. The `?content_type=` qualifier filters results by format.

### The Problem

A single security resource often has multiple representations at the same provider:

| Resource | Representations |
|----------|----------------|
| CVE at MITRE | Web page (text/html at cve.org), GitHub blob view (text/html), raw JSON data (application/json) |
| GDPR | 24 EU language versions |
| RFCs | HTML, plain text, PDF, XML |
| NIST CSF controls | HTML page, PDF, OSCAL/JSON export |

Without content type information, an AI agent that wants machine-readable data has to guess from the URL. And without a query mechanism, it gets everything and has to filter client-side.

### Solution

1. **`content_type` field on resolution results** — each result carries the MIME type of the URL:

```json
{"secid": "...", "weight": 100, "url": "https://www.cve.org/CVERecord?id=CVE-2021-44228", "content_type": "text/html"}
{"secid": "...", "weight": 50, "url": "https://raw.githubusercontent.com/.../CVE-2021-44228.json", "content_type": "application/json"}
```

2. **`?content_type=` qualifier** — filters results to a specific format:

```
secid:advisory/mitre.org/cve#CVE-2021-44228?content_type=application/json
```

Returns only `application/json` results. If none exist, returns `not_found` with a message listing available content types. This is strict — silent fallback to a different format would break AI agents that expect to parse the response as JSON.

### Why `content_type` and MIME Types

- **`content_type`** not `media_type` — we're web-based, `Content-Type` is what HTTP servers return, what developers think about. Underscore matches SecID field naming convention (`secid_query`, `not_found`).
- **Full MIME types** (`application/json`) not shorthand (`json`) — MIME types are an existing standard with no ambiguity. No mapping table to maintain, no case sensitivity questions.
- **Values come from the server response** — the registry stores what the HTTP `Content-Type` header actually returns. CI can verify this by fetching each URL and checking.

### Why Strict (No Fallback)

If `?content_type=application/json` silently returns `text/html` when JSON isn't available, the qualifier is meaningless and clients can't trust it. Returning `not_found` with guidance ("Available: text/html. Remove ?content_type to see all.") is more useful — the client knows to adjust its query or update the registry.

### This Is Why Qualifiers Exist

The `?qualifiers` component of the SecID grammar (`secid:type/namespace/name[@version]?qualifiers#subpath`) was always in the spec but had no defined vocabulary. `content_type` is the first concrete qualifier, and it demonstrates the pattern: qualifiers modify resolution behavior without changing what's being identified. The same resource, different representation.

Future qualifiers follow the same pattern — and `lang` is the second one implemented.

## Language Qualifier (`?lang=`)

### The Problem

EU regulations like GDPR are published in 24 official languages. Without language selection, resolving `secid:regulation/europa.eu/gdpr#art-32` would either return 24 URLs (one per language) or force a single default. Neither is helpful — an AI agent working with German compliance needs the German text, not 24 results to filter through.

### The Design

The `lang` qualifier uses ISO 639-1 codes (`en`, `de`, `fr`, etc.) and follows the same strict pattern as `content_type`:

- `?lang=de` → return only the German URL, with `lang: "de"` on the result
- No `?lang=` → use the source's declared default (usually English), apply a +1 weight nudge
- `?lang=xx` (unavailable) → `not_found` with available languages listed

### Why Per-Child, Not Per-Source

Language availability is declared on child nodes (the URL-bearing pattern nodes), not on source-level match_nodes. This is because language availability is a property of the URL template — some sources might have language-specific URLs for articles but not for annexes. In practice, most children under the same source share the same lang config, but the model correctly represents that it's the URL that has language variants.

### Why `url_transform`

EUR-Lex uses uppercase language codes in URLs: `/legal-content/EN/TXT/HTML/...`. Rather than storing uppercase codes and transforming them back for the API response, the registry stores standard lowercase ISO 639-1 codes and declares a `url_transform: "uppercase"` to handle the URL substitution. The API consumer always gets standard lowercase codes.

### Why Strict (No Fallback)

Same reasoning as `content_type`: if `?lang=de` silently returned English, the qualifier would be untrustworthy. Returning `not_found` with available languages lets the client adjust its query. The default language behavior (no `?lang=` → English with +1 nudge) ensures the common case works without any qualifier.

---

## Per-Field Metadata (`_checked` / `_updated` / `_note`)

### The Principle

Registry data includes facts that can go stale: URLs, email addresses, policy descriptions, and negative findings (null values meaning "we checked and they don't have this"). Git history tracks when files were committed, but not when someone last verified the real-world facts are still accurate.

Three per-field metadata fields capture this:

- **`_updated`** — when the value last materially changed
- **`_checked`** — when someone last verified it's still correct
- **`_note`** — what was observed during verification

Together they tell you freshness, stability, and context.

### Why Three Fields

`_checked` alone would lose the distinction between "first recorded today" and "stable for years, just re-verified." A URL with `_updated: 2025-06-01` and `_checked: 2026-03-06` tells you it's been stable for 9 months *and* was just confirmed — that's highly trustworthy.

`_updated` alone would require touching the field every time you verify, even when nothing changed, creating misleading git diffs and losing the "how long has this been stable?" signal.

`_note` records *what was observed*, not just *when*. A null `security_txt` with `_note: "redirects to homepage"` tells you why it's null. A positive `security_txt` with `_note: "RFC 9116 compliant, missing Canonical field"` records validation detail. Without `_note`, the next person re-checking has no context for what the previous verifier found.

### Why Not File-Level

A single file can contain data of varying freshness. A Cisco entity file might have a PSIRT URL verified last week and a product URL from a year ago. File-level timestamps hide this granularity.

### Why Not a Scheduling System

Check frequency depends on the consumer's needs and the data type — null values might warrant weekly re-checks while established URLs need monthly. This is an operational concern, not a data modeling concern. The registry records facts ("this was true on this date"); automation decides when to re-verify.

See [docs/proposals/TIMESTAMP-FIELDS.md](../proposals/TIMESTAMP-FIELDS.md) for the full proposal.

