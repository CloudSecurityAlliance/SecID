# Edge Cases

This document catalogs known edge cases for domain-name namespaces and SecID parsing. Each entry describes the scenario, why it matters, and how SecID handles it (or plans to).

For design rationale, see [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md). For the full specification, see [SPEC.md](../../SPEC.md).

## Namespace Parsing

### Why Not Reverse DNS Order?

**Scenario:** Java uses reverse DNS (`com.google.android.foo`) for package names. Should SecID do the same?

**No.** Java reverses because its `.` separator also appears inside domain names, creating ambiguity about where the namespace ends. SecID uses `/` as the separator between namespace segments and between namespace and name. Domain names **cannot contain `/`** — it's not a valid DNS character. So `secid:advisory/github.com/advisories/ghsa#GHSA-xxxx` is unambiguous: you can always identify the domain portion without reversal.

| Approach | Format | Why |
|----------|--------|-----|
| **Java** | `com.google.android.foo` | `.` is ambiguous — reverse to parse left-to-right |
| **SecID** | `google.com/android/foo` | `/` cannot appear in domains — natural order works |

This keeps SecID human-readable in natural left-to-right order, matching how people already think about URLs.

### Deeply Nested Subdomains

**Scenario:** An organization uses a deeply nested subdomain like `security.teams.internal.bigcorp.com`. Does this create clutter?

**In theory yes, in practice no.** Public-facing security knowledge comes from well-known, short domains. Cloud providers use subdomains naturally (`aws.amazon.com`) without issue. We have no registry entries deeper than three labels (e.g., `aws.amazon.com`), and there's no reason to expect this will change — organizations that publish security knowledge want to be found, and short domains help with that.

If it ever became a problem, the namespace is still unambiguous and parseable. It's just long.

### Namespace/Name Boundary with Sub-Namespaces

**Scenario:** Given `secid:advisory/github.com/advisories/ghsa#GHSA-xxxx`, how does the parser know `github.com/advisories` is the namespace and `ghsa` is the name (not `github.com` as namespace with `advisories/ghsa` as name)?

**Shortest-to-longest resolution.** The parser tries progressively longer namespace matches against the registry:

1. `github.com` — exists? Yes, candidate.
2. `github.com/advisories` — exists? Yes, longer candidate (wins).
3. `github.com/advisories/ghsa` — exists? No, stop.

Longest matching namespace wins. This is deterministic and registry-driven. See [SPEC.md](../../SPEC.md) Section 4.3.

### Platform Sub-Namespace Conflicts

**Scenario:** What if a GitHub user creates an account named `advisories`, conflicting with `github.com/advisories` (GitHub's advisory database)?

**The registry is authoritative, not the platform.** `github.com/advisories` is registered in the SecID registry as GitHub's advisory database. A GitHub user named `advisories` would need a different sub-namespace path (or wouldn't get one — the registry entry already exists). First-come-first-served in the registry, with domain owner (`github.com`) having priority over sub-namespace claims.

## Domain Name Lifecycle

### Domain Name Changes and Acquisitions

**Scenario:** A company rebrands and changes its domain (e.g., `twitter.com` → `x.com`). What happens to existing SecID identifiers?

**Existing identifiers persist.** `secid:entity/twitter.com/...` remains valid. The new domain gets its own namespace (`secid:entity/x.com/...`). The equivalence relationship between old and new belongs in the **relationship layer**, not the registry:

```json
{
  "type": "succession",
  "from": "secid:entity/twitter.com/...",
  "to": "secid:entity/x.com/..."
}
```

Resolvers can follow succession links to find current resources.

### Defunct and Re-Registered Domains

**Scenario:** A domain expires and is re-registered by a different entity. Can the new owner hijack the namespace?

**No.** DNS/ACME proves ownership **at registration time** — it's not an ongoing authority check. Once a namespace is registered in SecID, the registry entry persists regardless of DNS changes. The registry is the source of truth.

If the domain genuinely changes hands (acquisition, not squatting), the new owner can request a transfer through the normal review process. The old registry entries don't automatically transfer.

### Domain vs. Subdomain Ambiguity

**Scenario:** Should AWS be `aws.amazon.com` or `amazon.com/aws`?

**Use the domain the organization actually uses.** AWS publishes security advisories from `aws.amazon.com`, not from a path under `amazon.com`. Follow the source principle: if the organization operates under a subdomain, use that subdomain.

| Organization | Domain | Not This |
|-------------|--------|----------|
| AWS | `aws.amazon.com` | `amazon.com/aws` |
| Azure | `azure.microsoft.com` or `microsoft.com` | Depends on where they publish |
| GitHub | `github.com` | `microsoft.com/github` |

The test: where does the organization publish its security content?

## Internationalization

### Punycode vs. Unicode (IDN Resolution)

**Scenario:** An Internationalized Domain Name (IDN) has two representations: Unicode (`münchen.de`) and Punycode (`xn--mnchen-3ya.de`). Are these the same namespace?

**Yes — handled via try-both resolution + alias stubs.** This follows the same pattern as flexible input resolution for percent-encoding ([SPEC.md](../../SPEC.md) Section 8.3): try the input form first, then try the other form.

**Standards:** Punycode encoding is defined in [RFC 3492](https://www.rfc-editor.org/rfc/rfc3492). Internationalized Domain Names in Applications (IDNA2008) is defined in [RFC 5890](https://www.rfc-editor.org/rfc/rfc5890)–[5893](https://www.rfc-editor.org/rfc/rfc5893). These are mature, widely-implemented standards.

**Detecting Punycode input:** Punycode-encoded domain labels always start with the ASCII Compatible Encoding (ACE) prefix `xn--`. Detection is trivial — check whether any label in the domain starts with `xn--`. If so, convert to Unicode using any IDNA library:

| Language | Library |
|----------|---------|
| Python | `idna` package (`pip install idna`), or built-in `encodings.idna` |
| JavaScript | `URL` API (built-in), or `punycode` module |
| Go | `golang.org/x/net/idna` |
| Rust | `idna` crate |
| Java | `java.net.IDN` (built-in since Java 6) |

**Resolution order for IDN namespaces:**

1. **Try namespace as-is** — look up the input form in the registry
2. **If not found and input contains `xn--` labels (Punycode)** — convert to Unicode, try again
3. **If not found and input is Unicode** — convert to Punycode, try again

**Registry structure:** Only one form holds the actual records (the canonical form). The other form gets an **alias stub** — a minimal registry entry that points to the canonical namespace:

```yaml
# registry/advisory/de/xn--mnchen-3ya.md (alias stub)
---
type: advisory
namespace: xn--mnchen-3ya.de
alias_of: münchen.de
---
# This is the Punycode form of münchen.de. See münchen.de for all records.
```

```yaml
# registry/advisory/de/münchen.md (canonical — has all the actual records)
---
type: advisory
namespace: münchen.de
full_name: "Stadt München Security Advisories"
sources:
  advisories:
    ...
---
```

When a resolver hits an alias stub (a namespace entry with `alias_of` and no sources/rules), it follows the redirect to the canonical namespace and resolves there. The client gets back the result from the canonical entry.

**Why Unicode as canonical form:** Practitioners in non-Latin-script countries should see their organization's name in their own script. `字节跳动.com` is recognizable; `xn--5tzq62dl23a.com` is not. The whole point of Unicode namespace support is human readability. The Punycode form exists as an alias for systems that can't handle Unicode input.

**Why alias stubs instead of just try-both?** A resolver that tries both forms will find the canonical entry either way. But the alias stub serves two purposes:
1. **Confirms the Punycode form is known** — without a stub, a resolver can't distinguish "this Punycode namespace doesn't exist" from "this Punycode namespace exists but you need the Unicode form." The stub makes intent explicit.
2. **Works for simple resolvers** — a basic file-lookup resolver that doesn't know about IDN conversion still finds the stub and can follow the `alias_of` pointer.

### Unicode Normalization Forms (NFC vs. NFD)

**Scenario:** The same Unicode character can be encoded differently. The letter `ü` can be a single codepoint (U+00FC, NFC) or a base letter plus combining mark (U+0075 U+0308, NFD). Are these the same namespace?

**Yes.** DNS uses IDNA2008 which requires NFC normalization. SecID follows the same rule: **normalize namespaces to NFC form** before registry lookup. This ensures that `münchen.de` is always the same bytes regardless of how the input was encoded.

Resolvers SHOULD normalize Unicode input to NFC before looking up namespaces. This is a simple normalization step (most standard libraries provide it), unlike Punycode conversion which requires the alias stub mechanism because the two forms look completely different.

## Filesystem and Transport

### Case Sensitivity

**Scenario:** Is `GitHub.com` the same namespace as `github.com`?

**Yes.** [SPEC.md](../../SPEC.md) Section 8.1 specifies that namespaces are always normalized to lowercase. DNS is case-insensitive, and SecID follows the same rule. `GitHub.com`, `GITHUB.COM`, and `github.com` all normalize to `github.com`.

On case-sensitive filesystems (Linux), the registry file must be lowercase: `registry/advisory/com/github.md`.

### Trailing Dots in DNS

**Scenario:** In DNS, `mitre.org.` (with trailing dot) is the fully qualified domain name (FQDN). Is it different from `mitre.org`?

**No.** Strip trailing dots during normalization. `mitre.org.` and `mitre.org` are the same namespace. The registry uses the form without trailing dot.

### Very Long SecID Strings

**Scenario:** A long domain + long name + long subpath produces a very long SecID string. Is there a length limit?

**No formal limit currently specified.** In practice, domain names max at 253 characters, and the longest current namespace is `cloudsecurityalliance.org` (27 characters). Combined with type, name, and subpath, real-world SecIDs stay well under 200 characters.

If length limits become necessary (e.g., for database column constraints), they should be specified as implementation guidance, not grammar rules.

### Shared Platform Domains (github.io, gitlab.io)

**Scenario:** Domains like `github.io` are shared — many organizations host sites there (e.g., `jailbreakbench.github.io`, `trustllmbenchmark.github.io`). How does ownership work?

**Each `*.github.io` site is a separate namespace.** `jailbreakbench.github.io` is a distinct domain controlled by whoever owns the `jailbreakbench` GitHub organization. It's not a sub-namespace of `github.io` — it's a subdomain with its own DNS record.

This is different from platform sub-namespaces (`github.com/advisories`), which share the `github.com` domain. The `github.io` sites are independent domains that happen to use GitHub Pages for hosting.

| Namespace | Type | Ownership |
|-----------|------|-----------|
| `github.com` | Platform domain | GitHub (Microsoft) |
| `github.com/advisories` | Platform sub-namespace | GitHub's advisory team |
| `jailbreakbench.github.io` | Independent subdomain | JailbreakBench team |
| `trustllmbenchmark.github.io` | Independent subdomain | TrustLLM team |

## Registration and Governance

### Wildcard or Bulk Namespace Claims

**Scenario:** Can someone register `*.github.com` or claim all possible sub-namespaces under a domain?

**No.** Each namespace is registered individually. The domain owner (`github.com`) has priority for their own domain and can object to sub-namespace registrations, but they don't automatically own all possible sub-namespaces. `github.com/advisories` must be explicitly registered.

### Multiple Types for the Same Namespace

**Scenario:** `mitre.org` appears in `advisory/`, `weakness/`, `ttp/`, and `entity/`. Is this a conflict?

**No, this is expected.** A single organization often publishes multiple types of security knowledge. MITRE maintains CVE (advisory), CWE (weakness), ATT&CK (ttp), and exists as an organization (entity). Each type directory has its own `mitre.org.md` file. The namespace is the same; the type provides disambiguation.

### Self-Registration and AI Agents

**Scenario:** Can an AI agent register and maintain a namespace on behalf of an organization?

**Yes, by design.** The self-registration mechanisms (DNS TXT records, ACME challenges, challenge files) are all machine-friendly. An AI agent managing security operations for an organization can perform domain verification, submit registry entries, and maintain namespace content — just as AI agents already manage DNS records, certificates, and CI/CD pipelines.

This is a future feature (namespace registration is currently manual via pull requests), but the verification protocols are designed with both human and AI agent workflows in mind. See [REGISTRY-GUIDE.md](../guides/REGISTRY-GUIDE.md) for the planned self-registration process.

## See Also

- [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md) - Design rationale (includes "Why Not Reverse DNS" and "Domain Name Changes" sections)
- [SPEC.md](../../SPEC.md) - Full specification (Section 4: Namespaces, Section 8: Parsing)
- [REGISTRY-GUIDE.md](../guides/REGISTRY-GUIDE.md) - Registry contribution guide (includes self-registration roadmap)
