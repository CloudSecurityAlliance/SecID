# Proposal: SecID Participation Model

Status: Draft / discussion
Date: 2026-04-06

## Summary

Define three phases of participation in the SecID registry, progressing from CSA-maintained to vendor self-service to federation. Each phase builds on the previous and is designed to lower the barrier to participation while maintaining data quality.

## The Three Phases

### Phase 1: Pull Requests (current)

CSA bootstraps the registry. External contributions come via GitHub pull requests.

**How it works:**
1. Contributor forks the repo
2. Adds or updates registry files in their namespace
3. Submits a PR
4. CSA reviews and merges

**Who does it:** CSA staff, community contributors, AI agents (with human review).

**Strengths:** Simple, works today, full review control.

**Limitations:** Doesn't scale. Every update requires CSA review. Vendors have no ownership of their own data.

### Phase 2: CODEOWNERS Self-Service

Vendors maintain their own namespace files directly. CSA grants scoped write access after verifying domain ownership.

**How it works:**
1. Vendor contacts CSA and proves they own `example.com` (email verification to security contact, corporate GitHub org membership, or similar lightweight proof)
2. CSA adds them to CODEOWNERS:
   ```
   # Vendor maintains their own namespace across all types
   registry/*/com/example* @example-security-team
   ```
3. Vendor can push directly to their namespace files (or their PRs auto-approve)
4. PRs touching other namespaces still require CSA review
5. Branch protection ensures changes go through CI (JSON validation, regex safety checks)

**What vendors control:** Their own namespace files across all types — `registry/advisory/com/example.json`, `registry/disclosure/com/example.json`, `registry/entity/com/example.json`, etc.

**What CSA controls:** Spec changes, type definitions, cross-namespace concerns, schema changes, CI/CD pipeline.

**Domain verification:** Lightweight — not ACME/DNS. Options:
- Email to a known security contact (from security.txt, CNA contact, PSIRT email)
- Verification that the requester's GitHub org matches the domain
- For CNA-registered orgs: they're already verified by the CVE Program

**Strengths:** Vendors are the authority on their own data. Updates are immediate. CSA review burden drops dramatically.

**Limitations:** Requires GitHub org membership or individual accounts with repo access. Doesn't support private/internal data.

### Phase 3: Federation

Organizations run their own SecID resolver that supplements the public registry. The public resolver knows about them and can point clients to additional sources.

**How it works:**
1. Vendor runs a SecID-compatible resolver at their own domain (e.g., `secid.redhat.com`)
2. They register their resolver URL in their namespace entry:
   ```json
   {
     "namespace": "redhat.com",
     "type": "disclosure",
     "resolvers": [
       {
         "url": "https://secid.redhat.com/api/v1/resolve",
         "note": "Red Hat-maintained, includes additional product-specific data"
       }
     ]
   }
   ```
3. The public CSA resolver includes this in responses: "here's what we know, also check secid.redhat.com"
4. Clients can query both and merge results

**`resolvers` is an array** — a namespace may have multiple resolvers (vendor's own, sector CERT, regional resolver).

**Internal resolvers:** Organizations can also run internal resolvers (e.g., `secid.internal.redhat.com`) that are NOT registered in the public registry. These are configured in the client (SDK config file, plugin `--base-url` flag, or MCP server config). They supplement the public data with private information:
- Draft advisories not yet published
- Internal control mappings
- Private capability configurations
- Organizational context and risk assessments

**The chain:**
```
Client SDK / Plugin
  → queries internal resolver (secid.internal.example.org)
  → internal resolver also queries public resolver (secid.cloudsecurityalliance.org)
  → merges results
  → returns to client
```

Or the client queries both independently and merges client-side.

**Strengths:** Vendors fully own their data. Private data stays private. No dependency on CSA for updates. Ecosystem scales without central bottleneck.

**Limitations:** Requires vendors to run infrastructure. Federation protocol needs definition. Trust model (which resolvers do you trust?) is a client-side decision.

## Implementation Status

| Phase | Status | What's needed |
|-------|--------|---------------|
| **Phase 1: PRs** | Live | Nothing — working today |
| **Phase 2: CODEOWNERS** | Not started | Define verification process, set up CODEOWNERS, document the workflow |
| **Phase 3: Federation** | Designed, not implemented | Add `resolvers` field to namespace schema, update resolver to include it in responses, document the protocol |

## Phase 2 Implementation Details

### Verification Process

When a vendor requests self-service access:

1. They open a GitHub issue requesting write access to their namespace
2. CSA verifies domain ownership via one of:
   - Email exchange with a known security contact (security.txt, CNA contact list)
   - Confirming the requester belongs to the organization's GitHub org
   - For CNAs: cross-reference with CVE partner list (already verified by CVE Program)
3. CSA adds their team to CODEOWNERS
4. Vendor gets a brief onboarding (JSON schema, validation, CI checks)

### CODEOWNERS Structure

```
# Type definitions and shared infrastructure — CSA only
SPEC.md                          @CloudSecurityAlliance/secid-maintainers
CLAUDE.md                        @CloudSecurityAlliance/secid-maintainers
registry/*.md                    @CloudSecurityAlliance/secid-maintainers
registry/*.json                  @CloudSecurityAlliance/secid-maintainers
docs/                            @CloudSecurityAlliance/secid-maintainers
scripts/                         @CloudSecurityAlliance/secid-maintainers

# Vendor-maintained namespaces
registry/*/com/redhat*           @RedHatProductSecurity
registry/*/com/microsoft*        @microsoft-security
registry/*/com/google*           @google-security
```

### CI Checks for Self-Service PRs

Even vendor-maintained namespaces go through CI:
- JSON schema validation
- Regex pattern safety (anchored, no catastrophic backtracking)
- Namespace-to-filesystem path consistency
- No changes outside their CODEOWNERS scope

## Phase 3 Implementation Details

### `resolvers` Field

Added to namespace-level JSON:

```json
{
  "namespace": "redhat.com",
  "resolvers": [
    {
      "url": "https://secid.redhat.com/api/v1/resolve",
      "note": "Red Hat-maintained resolver with additional product data"
    }
  ]
}
```

The field is optional. Most namespaces won't have it (CSA is the only resolver). Vendors add it when they stand up their own resolver.

### Resolver Behavior

When the CSA resolver returns results for a namespace that has `resolvers`:

```json
{
  "secid_query": "secid:advisory/redhat.com/cve#CVE-2026-1234",
  "status": "found",
  "results": [...],
  "additional_resolvers": [
    {
      "url": "https://secid.redhat.com/api/v1/resolve",
      "note": "Red Hat-maintained resolver with additional product data"
    }
  ]
}
```

The client decides whether to query additional resolvers. The CSA resolver does NOT proxy to them — it just tells the client they exist.

### Client Configuration for Internal Resolvers

SDK config file (`~/.config/secid/config.json` or `.secid.json` in project root):

```json
{
  "resolvers": [
    "https://secid.cloudsecurityalliance.org/api/v1/resolve",
    "https://internal-secid.example.org/api/v1/resolve"
  ]
}
```

Plugin: `python3 server.py --base-url https://internal-secid.example.org`

The client queries all configured resolvers and merges results.

## Relationship to Profiles

The `profiles` proposal (disclosure-type fields) intersects with the participation model:

- **Phase 1:** CSA researches and populates profiles (safe harbor, bug bounty, CNA status)
- **Phase 2:** Vendors maintain their own profiles via CODEOWNERS — they're the authority on their own safe harbor, disclosure policy, etc. `checked_by: "vendor"` in provenance metadata.
- **Phase 3:** Vendors serve profiles from their own resolver with real-time data

## Open Questions

1. **Verification for non-CNA orgs** — CNAs are easy (cross-reference CVE partner list). For orgs not in the CVE Program, what's sufficient proof? Email to security@ address listed on their website?

2. **Revoking access** — if a vendor's security team changes, how do we handle CODEOWNERS updates? Annual re-verification?

3. **Federation trust** — should the CSA resolver indicate trust level for additional resolvers? Or is that purely a client-side decision?

4. **Conflict resolution** — if a vendor's resolver returns different data than the CSA registry for the same SecID, which wins? Probably the vendor for their own namespace, CSA for cross-references.

5. **Internal resolver discovery** — beyond manual config, is there a DNS-based discovery mechanism? (e.g., `_secid.example.com TXT "resolver=https://secid.example.com/"`) This is future work but worth considering.

---

*Based on design discussion about bootstrapping, vendor self-service, and federation. The three phases are designed to be incremental — each works without the next, but together they create a scalable ecosystem.*
