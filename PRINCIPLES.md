# SecID Design Principles

These are the foundational principles that guide every design decision in SecID. When in doubt about how something should work, refer back to these.

## 1. Labeling and Finding

**SecID is about labeling and finding security knowledge. That's it.**

SecID provides a grammar for referencing security knowledge and a registry for resolving those references. It does not assign identifiers (those come from their authorities), does not store vulnerability data (that's the data layer), and does not track relationships between identifiers (that's the relationship layer).

Three layers, cleanly separated:

| Layer | Contains | Example |
|-------|----------|---------|
| **Registry** | Identity, resolution, disambiguation | "CVE IDs look like CVE-YYYY-NNNNN, resolve at cve.org" |
| **Relationship** | Equivalence, succession, mapping | "This DOI = this arXiv paper" |
| **Data** | Enrichment, metadata | "This CVE affects Linux, severity high" |

If you're debating whether something belongs in the registry, ask: "Is this about finding the thing, or about describing the thing?" If the latter, it belongs elsewhere.

## 2. AI-First, Human-Legible

**The primary consumer is AI agents. But humans must be able to read, write, and understand everything.**

AI-first does not mean AI-only. It means:

- **Structure data for machine reasoning.** Include context, parsing hints, descriptions, and disambiguation guidance. An AI agent receiving a SecID response should understand what it has, how to interpret it, and what to do with it — without external documentation.
- **Keep everything human-readable.** Identifiers use domain names practitioners recognize. Subpaths preserve source formats humans know. Registry files are YAML/JSON that anyone can read. Documentation is plain markdown.
- **Optimize for the common case.** Most queries will come from software and AI agents. Design for that first, then ensure humans aren't left behind.

The test: can a security practitioner read a SecID and understand what it refers to? Can an AI agent parse it and resolve it without special instructions? Both must be true.

## 3. Helpful Over Correct

**We want to be helpful more than we want the client to be correct.**

When someone sends a malformed or imprecise query, we don't return an error — we return something useful. The system should always try to figure out what was intended and provide the best answer it can, along with guidance on the correct form.

This applies differently to the two interfaces:

### REST API (Software and Humans)

The API must do the thinking. Software can't reason about fuzzy matches, and humans shouldn't have to re-query. When the input is imprecise:

- **Try to resolve it anyway.** Match against alternate names, traverse the pattern tree across all sources in the namespace, check for common mistakes.
- **Return the data AND the correction.** Don't force a second round trip. Give them what they asked for (if we can figure it out) plus guidance on the correct form.
- **Never return a bare error.** Always include context: what we looked for, what we found, what's available.

### MCP Server (AI Clients)

The MCP server provides data and context, not decisions. AI clients are smart enough to reason for themselves:

- **Return richer data.** Full registry entries, all sources in a namespace, disambiguation instructions.
- **Don't make the decision for them.** The AI has context we don't (the document it's working with, surrounding references, publication dates). Give it the information to make its own choice.
- **Include reasoning guidance.** The `version_disambiguation` field is the template: instructions that help the AI figure out the answer using context it has access to.

### The "AI on Both Ends" Pattern

For complex cases (version ambiguity, fuzzy matches), the best answers come from cooperation between a smart server and a smart client. The server provides reasoning guidance ("versions are released by year, match the version closest to the document's publication date"). The client applies it to the local context it has. Neither side alone can resolve the ambiguity.

## 4. Four Response Outcomes

Every query resolves to exactly one of four outcomes. Each outcome can contain one or more pieces of data.

### Outcome 1: Exact Match

We have exactly what was asked for. Return the data.

```
secid:advisory/redhat.com/errata#RHSA-2026:1234
→ Status: exact_match
→ Data: URL, source info
```

This includes valid multi-valued responses — a versionless query against a version-ambiguous source returns all matching versions. That's still an exact match; the query has multiple correct answers.

### Outcome 2: Corrected Match

We figured out what was intended. Return the data AND the correct form.

```
secid:advisory/redhat.com/RHSA-2026:1234
→ Status: corrected_match
→ Data: URL, source info
→ Correction: "The correct form is secid:advisory/redhat.com/errata#RHSA-2026:1234"
```

The data comes first. The correction is additional guidance, not a blocker.

### Outcome 3: Partial Match / Related Data

We recognize part of the query but can't fully resolve it. Return what we know.

```
secid:advisory/redhat.com/total_junk
→ Status: related_data
→ Data: Red Hat advisory sources (errata, cve, bugzilla) with descriptions and patterns

secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12
→ Status: related_data
→ Data: IAM-12 from v4.0 (nearest version), available versions list
→ Note: "Version 4.1 not found. Nearest: 4.0 (current)."
```

This also covers exploration queries (`/*`) which return everything available at that level.

### Outcome 4: Not Found

Nothing matches. Be clear about what we looked for and why it failed.

```
secid:advisory/totallyinvented.com/whatever
→ Status: not_found
→ Detail: "No namespace 'totallyinvented.com' in the registry."

secid:frobnicate/mitre.org/cve#CVE-2024-1234
→ Status: not_found
→ Detail: "'frobnicate' is not a valid type. Valid types: advisory, weakness, ttp, control, disclosure, regulation, entity, reference."
```

Even "not found" should be helpful — tell them what went wrong and what the valid options are.

## 5. Honest Uncertainty

**Say what you know, say what you don't know, and say what the risks are.**

When the system isn't sure, it should say so explicitly rather than guessing silently:

- **Version not found:** "We don't have v4.1. Here's v4.0. We can't confirm whether IAM-12 exists unchanged in v4.1."
- **Fuzzy match:** "We think you meant `errata#RHSA-2026:1234`. If not, here's what redhat.com has."
- **Ambiguous reference:** "A01 means different things in different versions. Here are all of them with instructions for determining which one."

This builds trust. A system that's always confident is unreliable. A system that tells you when it's uncertain is one you can depend on.

## 6. Follow the Source

**Use names and formats the source uses. Preserve identifiers exactly.**

- `RHSA-2026:0932` stays `RHSA-2026:0932` — don't sanitize the colon
- `T1059.003` stays `T1059.003` — don't replace the dot
- The source calls it "CWE" → the registry calls it `cwe`
- The source calls it "Cloud Controls Matrix" → the name is `ccm` because that's what practitioners use

What practitioners know is what SecID uses. If someone has to mentally translate between the source's identifier and SecID's representation, we've failed.

## 7. Never Normalize Lossily

**If you can't reverse the transformation, don't do it.**

Data that passes through SecID must never be silently altered in a way that destroys information:

- **No lowercasing input.** Lowercasing is lossy — you can't recover the original case. Use case-insensitive regex flags (`(?i)`) instead of normalizing the input.
- **No stripping characters.** If the input has special characters, preserve them. The registry patterns determine what matches, not a sanitization step.
- **No mangling identifiers.** `RHSA-2026:0932` stays exactly as-is. Don't replace the colon with a dash, don't remove dots from `T1059.003`, don't "clean" anything.
- **Percent-decoding is acceptable** for matching purposes because it's reversible — the original encoded form can always be reconstructed. Try both encoded and decoded forms during resolution.
- **The original input is always preserved in the response.** Even when the system corrects or interprets the input, the response includes what was actually submitted.

This principle applies everywhere: API input handling, registry pattern matching, storage, and display. When in doubt, keep the original.

## 8. PURL Grammar Compatibility

**Same grammar as Package URL, different scheme.**

```
PURL:   pkg:type/namespace/name@version?qualifiers#subpath
SecID:  secid:type/namespace/name@version?qualifiers#subpath[@item_version][?qualifiers]
```

SecID extends PURL with item-level versioning and item-level qualifiers, but the base grammar is identical. Existing PURL mental models and tooling transfer directly. Don't break this compatibility without extraordinary reason.

## 9. Progressive Resolution

**Try the most specific interpretation first, then progressively loosen.**

When resolving a query:

1. Exact match (namespace + source name + pattern)
2. Pattern match across sources (input matches an id_pattern somewhere in the namespace)
3. Alternate name / common name match
4. Namespace exists but nothing specific matches → return namespace info
5. Nothing matches → not found with guidance

This ensures the most specific answer wins, but we always try to return something before giving up. The cost of an extra regex check is trivial. The cost of a useless error response is a frustrated user.

## 10. The Wildcard Convention

`/*` at any level returns everything available at that level:

```
secid:advisory/*                              → All advisory namespaces
secid:advisory/redhat.com/*                   → All Red Hat advisory sources
secid:*                                       → All types
```

This is intuitive (everyone knows what `*` means) and solves the discovery problem without a separate API. If someone doesn't know what's available, they can explore.

## Applying These Principles

When making a design decision, check it against these principles in order:

1. Is this about labeling and finding? (If not, it belongs in another layer.)
2. Does it work for AI agents AND humans? (If not, adjust.)
3. Is the system being helpful? (If it returns an error where it could return guidance, fix it.)
4. Are we being honest about what we know? (If we're guessing silently, add uncertainty signals.)
5. Are we following the source? (If we're mangling identifiers, stop.)
6. Are we preserving data? (If a transformation is lossy, don't do it.)
7. Are we staying PURL-compatible? (If we're breaking grammar, we need a very good reason.)
