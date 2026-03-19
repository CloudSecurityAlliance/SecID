# Versioning in Security Knowledge

This document covers how versioning actually works across security knowledge sources, what that means for SecID's design, and how the API should behave when resolving versioned and unversioned references.

## The Reality: Versioning Is Rare and Shallow

An analysis of ~100+ security knowledge sources in the SecID registry reveals that **most sources don't version at all**, and those that do have very few versions.

### Sources That Don't Version

Advisory and vulnerability databases — the bulk of what people query — are continuous, append-only streams. There are no editions. New entries are added, old entries are updated in place, and nobody tracks "CVE database version 5.0" as a meaningful concept.

- **CVE** — continuous stream. CVE "4.0" and "5.0" refer to the JSON schema version, not the database. `CVE-2024-1234` resolves to the same place regardless.
- **CWE** — continuously updated. New weaknesses added, existing ones refined. No editions.
- **GHSA** — continuous stream. Individual advisories can be versioned (git commits), but the database as a whole has no version.
- **NVD** — continuous enrichment of CVE data. No editions.
- **MITRE ATT&CK** — continuously updated. Techniques added and refined. No numbered editions (despite periodic "releases," the ID space is stable).
- **MITRE ATLAS** — same as ATT&CK.
- **MITRE CAPEC** — same.
- **Red Hat errata** — continuous stream. No errata database v1 or v2. Ever. (Speaking from direct experience writing advisories there.)
- **All vendor advisory databases** — same pattern. Vendors just publish advisories.

### Sources That Do Version

Frameworks, standards, and taxonomies version because they're **authored documents released as wholes**. But the version counts are tiny:

| Versions | Count | Examples |
|----------|-------|---------|
| 1 version | ~45 sources | Most things published once so far (AICM 1.0, EU AI Act 2024, OWASP Agentic Top 10) |
| 2 versions | ~10 sources | ISO 27001 (2013, 2022), NIST CSF (1.1, 2.0), OWASP LLM Top 10 (1.0, 2.0), CIS Controls (7.1, 8.0) |
| 3 versions | ~3 sources | OWASP Top 10 (2013, 2017, 2021) — the extreme case |

**Nobody has more than 3 versions.** The "version explosion" scenario doesn't exist in security knowledge. This is fundamentally different from software packages (npm package with 847 versions) and why PURL's version handling, while compatible, is overkill for our domain.

### Why This Matters for Design

Because versioning is rare and shallow:
- We don't need complex version-specific pattern routing (patterns don't change across versions)
- We don't need pattern ordering or weighting (the ID format stays the same; the meaning changes)
- We can afford to handle each versioned source carefully because there aren't many
- The `versions_available` array is always small (1-3 entries), so returning all of them is cheap

## Version Categories

From the API's perspective, every source falls into one of four categories:

| Category | Description | Version Impact on Resolution | Examples |
|----------|-------------|------------------------------|----------|
| **Unversioned** | Continuous database, no editions | None. Version concept doesn't apply. | CVE, CWE, GHSA, NVD, ATT&CK, Red Hat errata |
| **Version-transparent** | Has versions, but resolution doesn't change | None. Same URL regardless of version. API can ignore version. | CVE schema (4.0→5.0 doesn't change lookup URL) |
| **Version-significant, compatible** | Versions matter, but IDs generally carry forward | Version selects the edition. IDs mostly stable across versions. Cross-version lookup is reasonable with caveats. | CCM (4.0→future), ISO 27001 (2013→2022), NIST CSF (1.1→2.0), CIS Controls |
| **Version-significant, incompatible** | IDs reused with different meanings across versions | Version is essential. Unversioned lookup is ambiguous. | OWASP Top 10 (A01 means different things in 2017 vs 2021) |

The first two categories need no version logic. The last two need it, and they total maybe 15-20 sources — all with 1-3 versions.

### Registry Fields for Version Behavior

These source-level fields (defined in [REGISTRY-JSON-FORMAT.md](REGISTRY-JSON-FORMAT.md)) control how the resolver handles versions:

| Field | Purpose |
|-------|---------|
| `version_required` | `true` if unversioned references are ambiguous |
| `unversioned_behavior` | `"current"` (default), `"current_with_history"`, `"all_with_guidance"` |
| `version_disambiguation` | AI-readable instructions for determining intended version from context |
| `versions_available` | Array of `{version, release_date, status, note}` — all known versions |

See [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md) "Version Resolution Behavior" for the rationale behind these fields.

## API Response Behavior

### The Principle

**Be helpful more than correct.** The API should always return something useful along with an honest assessment of confidence. Never a bare 404. Never a silent wrong assumption. Always: here's what I have, here's how confident I am, here's what to check.

For the MCP server (AI clients), we return richer data and let the AI reason. For the REST API (software clients and humans), we do the reasoning and return a clear, ready-to-use answer. Same data, different levels of interpretation.

### Four Response Outcomes

Every SecID query resolves to exactly one of four outcomes:

#### 1. We Have That

Clean match. The SecID is well-formed, the namespace exists, the source exists, the pattern matches (if subpath provided), and we can resolve it.

```
Query:    secid:advisory/redhat.com/errata#RHSA-2026:1234
Response: Here's the URL → https://access.redhat.com/errata/RHSA-2026:1234
Status:   exact_match
```

For versioned sources where version is omitted but unambiguous:
```
Query:    secid:control/cloudsecurityalliance.org/ccm#IAM-12
Response: Here's IAM-12 from CCM v4.0 (current). Also available: v3.0.1 (superseded).
Status:   exact_match (unversioned_behavior: current_with_history)
```

For versioned sources where version is omitted and ambiguous:
```
Query:    secid:weakness/owasp.org/top10#A01
Response: A01 exists in multiple versions with different meanings:
          - 2021: Broken Access Control
          - 2017: Injection
          - 2013: Injection
          Disambiguation: [version_disambiguation text]
Status:   exact_match (unversioned_behavior: all_with_guidance)
```

This is still "we have that" — a versionless query against a version-ambiguous source is a valid question with a multi-valued answer, not an error.

#### 2. We Have That, and Here's the Correct Form

The query isn't well-formed, but we can confidently determine what was intended. We return the data AND the correction. No need for a second round trip — we want to be helpful, not force acknowledgment (software can't acknowledge, and an AI will note the correction anyway).

```
Query:    secid:advisory/redhat.com/RHSA-2026:1234
Response: Matched: secid:advisory/redhat.com/errata#RHSA-2026:1234
          URL: https://access.redhat.com/errata/RHSA-2026:1234
          Note: "RHSA-2026:1234" is a subpath identifier within the "errata" source.
                The correct form is secid:advisory/redhat.com/errata#RHSA-2026:1234
Status:   corrected_match
```

How the API determines this: the input doesn't match any source name, so traverse the pattern tree (`match_nodes`) across all sources in the namespace. `RHSA-2026:1234` matches `^RHSA-\d{4}:\d+$` in the errata node's children. High confidence — return the data with the correction.

#### 3. We Don't Have That, but Here's Related Data

The query partially matches — we recognize some components but can't resolve the full thing. We return what we know and let the client decide what to do.

```
Query:    secid:advisory/redhat.com/total_junk
Response: No source "total_junk" found under advisory/redhat.com.
          Red Hat advisory sources: errata (RHSA/RHBA/RHEA), cve, bugzilla.
          [source descriptions and pattern tree for each]
Status:   no_match_but_related
```

Version miss (requested version doesn't exist):
```
Query:    secid:control/cloudsecurityalliance.org/ccm@4.1#IAM-12
Response: Version 4.1 not found for CCM.
          Available versions: 4.0 (current, 2021-06-01), 3.0.1 (superseded).
          Nearest: Here's IAM-12 from v4.0.
          Note: Cross-version compatibility is uncertain — IDs may have changed.
Status:   no_match_but_related
```

Wildcard exploration:
```
Query:    secid:advisory/redhat.com/*
Response: Red Hat advisory namespace contains:
          - errata: RHSA (security), RHBA (bugfix), RHEA (enhancement)
          - cve: Red Hat's CVE analysis pages
          - bugzilla: Bug tracking with CVE aliases
          [full source details for each]
Status:   exploration
```

#### 4. We Definitely Don't Have That

Nothing matches. The namespace doesn't exist, or the type is invalid, or we've exhausted all fuzzy matching and come up empty.

```
Query:    secid:advisory/totallyinvented.com/whatever
Response: No namespace "totallyinvented.com" in the registry.
Status:   not_found
```

```
Query:    secid:frobnicate/mitre.org/cve#CVE-2024-1234
Response: "frobnicate" is not a valid type.
          Valid types: advisory, weakness, ttp, control, disclosure, regulation, entity, reference.
Status:   not_found
```

### Resolution Algorithm for Graceful Matching

When a query doesn't match exactly, the API tries progressively looser matches before giving up:

1. **Exact resolution** — namespace exists, source name matches, pattern matches → Outcome 1
2. **Pattern matching across sources** — source name doesn't match, but the input matches an `id_pattern` in one of the namespace's sources → Outcome 2 (corrected match)
3. **Alternate name matching** — input matches a source's `alternate_names` or `common_name` → Outcome 2 or 3 depending on whether a subpath was included
4. **Namespace exists but nothing matches** — return namespace info → Outcome 3
5. **Nothing matches** → Outcome 4

This order ensures the most specific match wins, and we always return the most helpful response possible.

### Version-Specific Resolution

When a version is included in the query:

1. **Version exists in `versions_available`** — resolve using that version's patterns/URLs
2. **Version doesn't exist, but similar versions do** — return nearest match (most recent version before the requested one) with a note. The `versions_available` array makes this easy since it includes release dates and status.
3. **Version doesn't exist and nothing is close** — likely a typo. Return available versions.

When version is omitted:

1. **`unversioned_behavior: "current"`** (default) — resolve to current version silently
2. **`unversioned_behavior: "current_with_history"`** — resolve to current, note other versions exist
3. **`unversioned_behavior: "all_with_guidance"`** — return all versions with `version_disambiguation` instructions

### API vs MCP Server

The same registry data powers both interfaces. The difference is how much interpretation the server does:

| Behavior | REST API (software clients and humans) | MCP Server (AI clients) |
|----------|------------------------|------------------------|
| Exact match | Return URL | Return URL + full registry context |
| Corrected match | Return data + correction | Return data + correction + full source info |
| Fuzzy/related | Do the matching, return best guess | Return the namespace data, let AI reason |
| Version miss | Find nearest, explain | Return versions_available + disambiguation, let AI reason |
| Exploration (`/*`) | Return structured summary | Return full registry entries |

The API provides ready-to-use answers for software clients and humans — it does the reasoning so they don't have to. The MCP server provides data and context for AI clients — letting them reason with their own knowledge of the situation.

## The Mapping Connection

When a version is requested that we don't have (e.g., CCM 4.1 when we have 4.0), the ideal long-term answer includes cross-version mapping: "IAM-12 in v4.0 became IAM-12.A and IAM-12.B in v4.1." This mapping data belongs in the **relationship layer**, not the registry. The registry signals that version compatibility may be an issue; the relationship layer provides the actual mapping.

This dovetails with the broader security mapping problem (e.g., CCM 4.0 → 4.1 mapping, ISO 27001:2013 → 2022 mapping). Those mappings are valuable independent of SecID and will be maintained separately. SecID's role is to provide stable identifiers for both sides of the mapping.

## Document Map

| Topic | Read This |
|-------|-----------|
| Version resolution field definitions | [REGISTRY-JSON-FORMAT.md](REGISTRY-JSON-FORMAT.md) "Version Resolution Fields" |
| Why versioning works the way it does | [DESIGN-DECISIONS.md](../explanation/DESIGN-DECISIONS.md) "Why Each Component Does or Doesn't Support Versioning" and "Version Resolution Behavior" |
| Contributor guidance for version fields | [REGISTRY-GUIDE.md](../guides/REGISTRY-GUIDE.md) "Version Requirements and Disambiguation" |
| Grammar and parsing | [SPEC.md](../../SPEC.md) "Versionless References" |
