# Classification Guide

**How SecID decides what type something is — and how you can decide the same way.**

Classification has to be *reproducible*. The same source, handed to a different person or a different AI
session two years from now, must land in the same place. Otherwise the registry drifts and nobody notices,
because a wrong classification still resolves — it just resolves somewhere nobody thinks to look.

This guide is the procedure. [TYPES-AND-SUBTYPES.md](../reference/TYPES-AND-SUBTYPES.md) is the catalog of
what exists; `registry/<type>.md` holds each type's definition and its boundaries against neighbours.

## TL;DR

First confirm the thing is in scope at all ([Step 0](#step-0-is-it-in-scope)). Then decide
three things:

1. **Type** — one of `advisory`, `weakness`, `ttp`, `control`, `capability`, `methodology`, `disclosure`,
   `regulation`, `entity`, `reference`.
2. **Namespace** — the publisher's DNS domain (`nist.gov`, `pcisecuritystandards.org`). Verify with
   `host <domain>` when unsure.
3. **Name** — what the publisher calls it (`csf`, `pci-dss`, `ccm`, `cwe`).

Then `secid:<type>/<namespace>/<name>[@version][#subpath]`.

## Step 0: Is it in scope?

SecID covers **security and security-adjacent knowledge**. The name is a name, not a boundary.

Most material passes or fails this obviously. The hard cases are risk, severity, and assurance frameworks
from safety-critical industries — functional safety, medical devices, aviation, process control. The test:

> **A risk, severity, or assurance framework is in scope when security findings in its domain are
> *expressed through* it.**

Not *"is this a security standard?"* but *"does a security finding here have to be stated in this
framework's terms before anyone can act on it?"*

| Framework | In scope? | Why |
|---|---|---|
| ISO 26262 / ASIL | Yes | An ECU vulnerability's remediation urgency *is* an ASIL judgement |
| IEC 61508, IEC 61511 / SIL | Yes | ICS vulnerability consequence is stated in SIL terms |
| ISO 14971 | Yes | A medical device vulnerability becomes a recall decision through its risk matrix |
| DO-178C, DO-326A | Yes | Avionics software assurance; DO-326A is explicitly airworthiness security |
| ISO 9001 | No | Generic quality management; no security finding routes through it |
| A generic 5×5 risk matrix | No | No issuing authority and no stable identifier — it would also fail the pattern-breadth gate |

Three consequences worth stating plainly:

- **In scope is not the same as being a security standard.** ISO 14971 is a safety standard. It is in scope
  because medical device security findings are adjudicated in its terms.
- **The test can say no to things already registered.** Most of the safety material already held passes it:
  ISO 13849 and IEC 62061 (machinery functional safety) work like SIL, and ISO/IEC 80001 covers IT networks
  carrying medical devices. Three sit at the edge — **IEC 60601** (electrical safety), **IEC 62366**
  (usability engineering) and **ISO 13485** (quality management) — where no security finding is obviously
  expressed in their terms. They predate this test and stay for now, flagged rather than ratified: a test
  that only ever says yes is not a test.
- **Scope is not a licensing question.** Whether SecID may serve a framework's *content* is separate and
  decided later; being unable to redistribute ISO 26262 has no bearing on whether it belongs in the registry.

When the answer is genuinely unclear, [ask](#when-to-stop-and-ask) rather than guessing. Scope drift is
harder to notice than a wrong type, because both still resolve — but a wrong type resolves somewhere
plausible, while out-of-scope material makes the registry mean something different than it claims.

## Step 1 — Determine the type

| The thing is… | Type |
|---|---|
| A publication about a specific vulnerability or event (CVE, GHSA, vendor advisory, incident report) | `advisory` |
| A category of mistake, described abstractly (CWE, OWASP Top 10) | `weakness` |
| A catalog of adversary behaviour (ATT&CK, ATLAS, CAPEC) | `ttp` |
| A statement of what ought to be true — framework, benchmark, hardening guide | `control` |
| A legal obligation — statute, regulation, directive, binding order | `regulation` |
| A repeatable process for producing analysis, a score, a mapping, or a decision | `methodology` |
| A security feature of a specific product, with configuration and audit surface | `capability` |
| A programme or channel for reporting vulnerabilities | `disclosure` |
| An organization, product, or service, referenced as itself | `entity` |
| **Anything else** — paper, blog, report, spec, glossary, model card, course | `reference` |

### `reference` is the catch-all, by design

When something does not clearly fit another type, it is `reference`. This is deliberate policy, not
failure: landing in `reference` and migrating later is cheaper and more honest than force-fitting into a
wrong type or inventing a new one.

The consequence is that `reference` is heterogeneous on purpose — it holds identifier systems (arXiv, DOI),
format specifications (SARIF, CycloneDX), glossaries, papers, and courses simultaneously. That is the policy
working, not the type decaying. Use `subtype:` to discriminate within it.

**The type list is fixed.** Do not invent a type. If something genuinely needs one, it goes through the
four-criteria gate in [TYPES-AND-SUBTYPES.md](../reference/TYPES-AND-SUBTYPES.md) — and adding a type
requires coordinated changes across five repositories, so the bar is high and the default answer is a
subtype.

### Publisher packaging beats object ontology

When a publisher ships several kinds of thing inside one framework, follow the publisher.

ATT&CK is the worked case. It contains techniques, adversary groups, software, and mitigations. A group is
really an organization and a mitigation is really a control — but ATT&CK ships them inside a TTP framework,
so all of them live under `ttp`:

```
secid:ttp/mitre.org/attack#T1059.003   technique
secid:ttp/mitre.org/attack#G0007       adversary group
secid:ttp/mitre.org/attack#S0154       software
secid:ttp/mitre.org/attack#M1036       mitigation
```

This follows [principle 6](../../PRINCIPLES.md#6-follow-the-source). Splitting a publisher's framework
across four SecID types to satisfy an ontology would make every reference to it harder to construct and
harder to verify.

## Step 2 — Check for a subtype

Subtypes refine within a type without inflating the type list. Consult
[TYPES-AND-SUBTYPES.md](../reference/TYPES-AND-SUBTYPES.md) for the current vocabulary — a glossary is
`reference` with `subtype: ["glossary"]`; an incident report is `advisory` with `subtype: ["incident"]`.

Subtype values are **not** freely addable: they are declared in SecID-Service's `type-registry.ts` and CI
rejects registry data using an undeclared value (ADR-008). If the right value does not exist, propose it —
do not invent one in a registry file.

## Step 3 — Determine the namespace

The namespace is the publisher's **DNS domain**, because domains are owned, verifiable, and stable in a way
that names and acronyms are not.

- Use the canonical domain the publisher uses for the thing itself
- For US states, the state portal (`ca.gov`, `ny.gov`, `mass.gov`) — not the expanded form
- For informal groups or individual researchers, the most stable domain available (university, GitHub org,
  project site). Record the uncertainty in notes
- Namespace matching is **shortest-to-longest**, so `github.com` and `github.com/advisories` can coexist;
  the longest match wins

## Step 4 — Name, version, subpath

- **Name** — what the publisher calls the source, in the publisher's form (`csf`, not `cswp.29`). Record a
  publication number separately if one exists
- **Version** — the version string the artifact states about itself, not a marketing label
- **Subpath** — the item identifier, preserved exactly: `RHSA-2026:0932` keeps its colon, `T1059.003` keeps
  its dot, `PR.AC-1` is unchanged. Never lossy-normalise ([principle 7](../../PRINCIPLES.md#7-never-normalize-lossily))

## Boundary tests

Each type file carries the authoritative test for its own boundaries, and several are sharper than a
one-line summary can be. Use these; do not re-derive them.

| Pair | Test | Authority |
|---|---|---|
| `control` / `methodology` / `reference` | **Duck test** — hand someone the document and ask "what do I DO with it?" *Implement these requirements* → control. *Follow this process to produce an output* → methodology. *Read or cite it* → reference | [methodology.md](../../registry/methodology.md) |
| `control` / `capability` / `entity` | **Verb test** — control says MUST ("encrypt data at rest"), entity says IS (neutral description), capability says CAN, actionably ("S3 default encryption, audit with `get-bucket-encryption`") | [capability.md](../../registry/capability.md) |
| `disclosure` / `entity` / `advisory` | *What is this organization?* → entity. *What vulnerabilities were published?* → advisory. *How do I report one?* → disclosure | [disclosure.md](../../registry/disclosure.md) |
| `weakness` / `advisory` | A *category* of mistake (CWE-79) vs a *specific instance* (CVE-2024-1234) | [weakness.md](../../registry/weakness.md) |
| `weakness` / `ttp` / `control` | What's wrong vs how attackers exploit it vs how to prevent it | [ttp.md](../../registry/ttp.md) |
| `regulation` / `control` | Is compliance *mandatory by law* in some jurisdiction? Regulations are mandatory; control frameworks are voluntary unless a regulation adopts one | [regulation.md](../../registry/regulation.md) |
| everything → `reference` | The negative list — what explicitly does *not* belong in the catch-all | [reference.md](../../registry/reference.md) |

When two tests both apply, pick the **primary purpose** and note the secondary. Genuine dual membership is
allowed and sometimes correct — CVSS is both a `methodology` (the scoring process) and a `reference` (the
specification document), because people cite each separately.

When nothing applies, use `reference`.

## Worked examples

| Thing | SecID | Why |
|---|---|---|
| NIST CSF 2.0 control PR.AC-1 | `control/nist.gov/csf@2.0#PR.AC-1` | Voluntary framework stating what ought to be true |
| EU AI Act | `regulation/eu/europa/...` | Legally binding within its jurisdiction |
| CVE-2021-44228 | `advisory/mitre.org/cve#CVE-2021-44228` | A specific vulnerability record |
| CWE-79 | `weakness/mitre.org/cwe#CWE-79` | A category of mistake |
| CVSS v4.0 | `methodology/first.org/cvss@4.0` | A repeatable process producing a score |
| The CVSS v4.0 specification document | `reference/first.org/cvss@4.0` | The document, as distinct from the method |
| AWS S3 default encryption | `capability/amazon.com/aws/s3/...` | A feature of one product |
| A NIST mapping between CSF and 800-53 | `methodology/nist.gov/...` | Produces a mapping — judgement, not format |
| ISO 27001 (licensed) | `control/iso.org/27001@2022` | Type is unaffected by licensing; content is metadata-only |
| An arXiv paper | `reference/arxiv.org/2303.08774` | Catch-all: a document |

Note CVSS appearing as **both** `methodology` and `reference`. That is the cross-type pattern, not an
error: the scoring process and the document describing it are different things people cite differently.
See [registry/README.md](../../registry/README.md).

## Edge cases

1. **Spans multiple types** — pick the primary purpose; note the secondary. Cross-type entries are legitimate
   when both are genuinely cited (see CVSS above)
2. **Multiple versions** — each version is addressable via `@version`; the registry records lifecycle
3. **Publication number vs semantic name** — use the semantic name, record the publication number separately
4. **Already canonical elsewhere** — if a publisher hosts authoritative, version-tagged data (CVE, ATT&CK
   STIX), point at it. Do not duplicate
5. **Unbounded identifier space** — blog slugs, usernames, paper IDs. Declare `open_pattern: true` so the
   node is excluded from unscoped search while namespace-scoped resolution still works. Never use a
   permissive regex without declaring it

## When to stop and ask

- **Scope is unclear** → ask, and **do not register meanwhile**. This is the one case where the interim
  default is inaction: a wrongly-typed entry resolves somewhere plausible and can be moved, but
  out-of-scope material changes what the registry claims to be, and every catalogue that admits it
  makes the next admission easier to justify
- **Type cannot be determined** after working through this guide → ask, and default to `reference` meanwhile
- **Publisher naming conflicts with an existing registry entry** → ask; propose a registry update
- **Licence terms unclear** → do not host content; metadata-only with a link to the source
- **The identifier set cannot be enumerated and has no structure** → stop. A pattern that matches everything
  asserts everything is valid and degrades every query in the system

## Spotting gaps

A catalog of what exists cannot show you what is missing. To find gaps, ask which question something
answers — and notice which answers have no home:

| Question | Types answering it |
|---|---|
| What exists? | `weakness`, `advisory`, `ttp`, `entity` |
| What ought to be true? | `control`, `regulation` |
| What do I run? | *(nothing today)* |
| What was found or verified? | *(nothing today)* |
| Where is it written down? | `reference` |
| *(cross-cutting)* | `methodology`, `capability`, `disclosure` |

Two columns are empty. Machine-runnable content — Sigma rules, Semgrep rules, Nuclei templates, exploits —
answers *what do I run* and has nowhere to go. Recorded findings — certifications, malware analyses,
assessments — answer *what was found* and likewise. Both gaps were confirmed independently by mapping STIX's
object model, which leaves exactly Indicator, Malware Analysis, and Opinion homeless.

Use this frame when surveying a new vocabulary or corpus: map its object types onto the questions, and
whatever falls off the table is a real gap rather than an oversight. See
[docs/project/TODO.md](../project/TODO.md) for the standing vocabulary survey.

## Where the authoritative answers live

| Question | Source |
|---|---|
| What types exist, and what do they mean? | `registry/<type>.md` |
| What subtypes exist? | [TYPES-AND-SUBTYPES.md](../reference/TYPES-AND-SUBTYPES.md) |
| Is this subtype value legal? | SecID-Service `src/type-registry.ts` (CI-enforced) |
| Why was this decided? | [DECISIONS.md](../../DECISIONS.md), [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md) |
| How do I write the entry? | [ADD-NAMESPACE.md](ADD-NAMESPACE.md), [REGISTRY-GUIDE.md](REGISTRY-GUIDE.md) |
| How do I write the pattern? | [REGEX-WORKFLOW.md](REGEX-WORKFLOW.md) |
