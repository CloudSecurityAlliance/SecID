# compliance-testing

**Status: Stub — not yet built.** Will be built incrementally alongside SecID-Service as the test suite accumulates.

## Purpose

Skill for **running the canonical SecID test suite against any resolver implementation**, interpreting failures, diagnosing whether problems are in the registry data or the resolver code, and suggesting fixes. This skill also serves as the **conformance specification** for third-party SecID resolver implementations.

## Audience

- Developers building or maintaining SecID resolver implementations (any language)
- AI agents running compliance checks during API development
- Third-party implementers verifying their resolver conforms to the spec
- Contributors validating that registry changes don't break resolution

## What This Skill Covers

### Test Case Format

Each test case specifies:

- **Input:** A SecID string (e.g., `secid:advisory/mitre.org/cve#CVE-2024-1234`)
- **Expected parse:** Decomposed components (type, namespace, name, version, qualifiers, subpath, item_version)
- **Expected resolution:** URL(s) the resolver should return
- **Expected outcome:** Which of the four response types applies (exact match, corrected match, related data, not found with guidance)
- **Edge case flags:** What the test exercises (encoding, versioning, special characters, etc.)

### Coverage Areas

The test suite covers all dimensions of SecID resolution:

| Area | What's Tested |
|------|--------------|
| All 8 types | advisory, weakness, ttp, control, disclosure, regulation, entity, reference |
| Percent-encoding | `RHSA-2024:1234` round-trips correctly, `%3A` decodes to `:` |
| version_required | Versioned sources return disambiguation when version omitted |
| Qualifiers | `?lang=en` and other qualifier parsing |
| Sub-namespaces | `github.com/advisories` vs. `github.com` shortest-to-longest matching |
| Case sensitivity | Source identifiers preserve original case |
| Special characters | Colons, dots, ampersands in subpath identifiers |
| Hierarchical IDs | `T1059.003` matches parent `T1059` then child `.003` |
| Wildcard convention | `/*` at various levels returns discovery responses |

### Four Response Outcomes Testing

Every test case maps to one of the four outcomes defined in PRINCIPLES.md:

1. **Exact match** — SecID resolves to a specific URL
2. **Corrected match** — Input has a minor error, resolver suggests correction
3. **Related data** — No exact match but related information available
4. **Not found (with guidance)** — Nothing matches, but response includes what was tried and what to try next

### Cross-Runtime Verification

The same test cases run against implementations in all target languages:

- JavaScript/TypeScript (SecID-Service, npm library)
- Python (pip library)
- Go (native library)
- Rust (native library)

A passing implementation produces identical results across all runtimes for the same input.

### Failure Diagnosis

When a test fails, determine the root cause:

- **Registry data bug** — Pattern doesn't match valid identifiers, URL template produces wrong URL, missing match_node for a known ID format
- **Resolver code bug** — Parser mishandles encoding, namespace matching logic incorrect, version extraction fails
- **Test case bug** — Expected output is wrong, test doesn't account for a valid edge case
- **Spec ambiguity** — The spec doesn't clearly define behavior for this case (escalate to spec discussion)

## Test Case Accumulation

Test cases are **not written up front**. They accumulate organically:

1. During API development, each new namespace or edge case produces test cases
2. Bug reports against any resolver become test cases
3. Spec clarifications produce regression tests
4. Third-party implementers contribute cases for behaviors they find ambiguous

The test suite grows as the project grows — it's a living conformance specification.

## Dependencies

- [ ] `test-cases.json` format defined (built during SecID-Service API development)
- [ ] SecID-Service as reference implementation to validate against
- [ ] Initial test cases covering core namespaces (mitre.org/cve, mitre.org/cwe, mitre.org/attack, nist.gov, etc.)
- [ ] Test runner that loads test-cases.json and executes against a resolver endpoint

These emerge naturally during API development — you can't build an API without testing it, and those tests become the conformance suite.

## What This Skill Does NOT Cover

- **Researching new sources** — See [skills/registry-research/](../registry-research/)
- **Converting .md to .json** — See [skills/registry-formalization/](../registry-formalization/)
- **Validating registry files** — See [skills/registry-validation/](../registry-validation/) (structural, pattern, consistency, and quality checks on the files themselves)
- **Consuming/using SecID as an end user** — See [skills/secid-user/](../secid-user/)

## Design Rationale

**Why a separate skill?** Research and formalization are about getting data right. Compliance testing is about verifying that code correctly interprets that data. Different expertise (debugging resolver logic vs. investigating sources), different tools (test runners vs. web research), different failure modes (code bugs vs. data gaps).

**Why also a conformance spec?** Any project that wants to build a SecID resolver needs to know: "does my implementation produce correct results?" The test suite answers that question definitively. Publishing it as a conformance spec means third-party implementations can self-certify.

## Open Questions

- What format for test-cases.json? (JSON with input/expected pairs, or something richer?)
- Should the test runner be language-agnostic (HTTP-based against the REST API) or have native harnesses per language?
- How to handle tests for namespaces that don't exist yet in the registry?
- Should there be conformance levels (basic parsing, full resolution, version handling)?
