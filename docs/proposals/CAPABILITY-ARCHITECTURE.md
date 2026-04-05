# Capability Architecture: Facts, Opinions, and Relationships

Status: Research / design
Date: 2026-04-05

## Core Insight

Security knowledge has three layers that must be kept separate:

1. **Facts** — what a product can do (capabilities)
2. **Opinions** — what various authorities say you should do with those capabilities (controls, regulations, tool checks)
3. **Connections** — how facts and opinions relate to each other (relationships)

SecID catalogs all three without privileging any single authority's opinion.

## The Capability as Neutral Ground Truth

A capability entry describes what a product feature IS and what it can DO. It includes:

- **What exists** — the feature and its configuration options
- **Vendor defaults** — what's set out of the box (this is a fact about the product)
- **Vendor recommendations** — what the vendor says about their own product (this is the vendor's opinion, but it's authoritative about their own product)
- **How to check it** — CLI/API/console commands to audit the current state
- **How to set it** — CLI/API/console/IaC commands to configure it

A capability entry does NOT include:
- Whether you MUST enable it (that's a control's opinion)
- Whether the law requires it (that's a regulation's opinion)
- What severity it has (that's a tool's assessment)
- Whether the default is good enough (that's someone's opinion)

Example:

```json
{
  "secid": "secid:capability/amazon.com/aws/s3#default-encryption",
  "content": {
    "feature": "S3 Default Server-Side Encryption",
    "description": "Automatically encrypts all new objects stored in the bucket",
    "options": [
      {"value": "AES256", "name": "SSE-S3", "description": "Amazon S3 managed keys"},
      {"value": "aws:kms", "name": "SSE-KMS", "description": "AWS KMS managed keys — per-key audit trail in CloudTrail"},
      {"value": "aws:kms:dsse", "name": "DSSE-KMS", "description": "Dual-layer server-side encryption with KMS keys"}
    ],
    "default": {
      "value": "AES256",
      "since": "2023-01-05",
      "note": "All new buckets have SSE-S3 enabled by default since January 2023"
    },
    "vendor_recommendation": "Use SSE-KMS for sensitive data to enable key rotation, audit trail, and cross-account access controls",
    "audit": {
      "cli": "aws s3api get-bucket-encryption --bucket {bucket}",
      "api": "GetBucketEncryption",
      "console": "S3 → Bucket → Properties → Default encryption"
    },
    "configure": {
      "cli": "aws s3api put-bucket-encryption --bucket {bucket} --server-side-encryption-configuration ...",
      "api": "PutBucketEncryption",
      "console": "S3 → Bucket → Properties → Edit default encryption",
      "terraform": "resource \"aws_s3_bucket_server_side_encryption_configuration\"",
      "cloudformation": "AWS::S3::Bucket BucketEncryption property"
    },
    "source": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html"
  }
}
```

## The Opinion Landscape

Multiple authorities have opinions about the same capability. These opinions are ALL legitimate — they serve different audiences, different risk tolerances, different regulatory contexts. They may conflict.

For the same S3 encryption capability:

| Authority | SecID | Says | Posture |
|-----------|-------|------|---------|
| NIST | `control/nist.gov/800-53#SC-28` | "Protect data at rest" | Abstract requirement |
| CIS | `control/cisecurity.org/aws-benchmark@3.0#2.1.1` | "Ensure default encryption is enabled" | Must enable (any option) |
| DISA | `control/disa.mil/aws-stig#V-252476` | "Must use KMS encryption" | Must use KMS specifically |
| AWS | `control/amazon.com/aws/well-architected#sec-data` | "Enable encryption, prefer KMS" | Recommendation |
| Prowler | `control/prowler.com/aws#s3_bucket_default_encryption` | "Check: is it enabled?" | Automated test (medium severity) |
| PCI-DSS | `control/pcisecuritystandards.org/pci-dss#3.4` | "Render PAN unreadable" | Applies to cardholder data |
| GDPR | `regulation/europa.eu/gdpr#art-32` | "Appropriate technical measures" | Legal requirement (EU) |
| HIPAA | `regulation/govinfo.gov/hipaa` | "Encrypt PHI" | Legal requirement (US healthcare) |

CIS says any encryption is fine. DISA says only KMS. Both are correct — for their audience. A commercial SaaS company follows CIS. A defense contractor follows DISA. A healthcare provider follows HIPAA. They all reference the same capability.

SecID's job: catalog all of these so people can find them, compare them, and apply the ones relevant to their situation.

## What Prowler (and Similar Tools) Are

Prowler, ScoutSuite, Steampipe, CloudCustodian, etc. are security tools that automate verification of controls. In SecID:

**As a product:** `secid:entity/prowler.com/prowler` — what Prowler is

**As a set of checks:** `secid:control/prowler.com/aws#check_name` — what Prowler says to check

Each Prowler check is a control — it prescribes what should be verified. It's Prowler's implementation/interpretation of upstream controls (CIS, NIST, etc.), expressed as an executable check. The check itself is referenceable because people say "we failed Prowler check X" and need to look it up.

The same pattern applies to every security scanning tool:
```
secid:control/prowler.com/aws#s3_bucket_default_encryption
secid:control/nccgroup.com/scoutsuite/aws#s3-bucket-encryption
secid:control/turbot.com/steampipe/aws#s3_bucket_encryption
```

All three check the same capability. They may check it differently, with different severity, different remediation advice. That's fine — catalog them all.

## The Relationship Layer (V2)

Relationships connect everything. They flow in multiple directions:

```
capability/amazon.com/aws/s3#default-encryption
  ← "checked_by" ← control/prowler.com/aws#s3_bucket_default_encryption
  ← "required_by" ← control/cisecurity.org/aws-benchmark@3.0#2.1.1
  ← "required_by" ← control/disa.mil/aws-stig#V-252476
  ← "implements" → control/nist.gov/800-53#SC-28
  ← "satisfies" → regulation/europa.eu/gdpr#art-32
```

Traversal queries:
- "What checks exist for S3 encryption?" → follow all checked_by/required_by
- "What capability satisfies NIST SC-28 on AWS?" → follow implements from SC-28
- "Do CIS and DISA agree on S3 encryption?" → compare their postures on the same capability
- "What's the strictest posture for this capability?" → compare all opinions

## The Process for Building Capabilities

### Phase 1: Author capability entries from vendor documentation

**Source of truth:** The vendor's own documentation
**What we capture:** Facts — what exists, what it can do, how to use it
**Who does it:** CSA (us), hoping vendors eventually take ownership

Process per service:
1. Read the vendor's security documentation
2. Identify every security-relevant configuration
3. For each: what is it, what are the options, what's the default, how to audit, how to configure
4. Include vendor recommendations (they're facts about the vendor's opinion)
5. Cross-reference against Prowler/CIS/DISA check lists for completeness (did we miss any?)
6. Publish as capability entries

### Phase 2: Catalog all opinion-makers

For each capability, identify who has opinions about it:
- Framework benchmarks (CIS, DISA STIGs)
- Tool checks (Prowler, ScoutSuite, Steampipe)
- Vendor best practices (AWS Well-Architected, Azure Security Benchmark)
- Abstract requirements (NIST 800-53, CCM)
- Legal requirements (GDPR, HIPAA, state laws)

Many of these already exist in SecID as control/regulation entries. Phase 2 is ensuring completeness.

### Phase 3: Build relationships

Connect opinions to capabilities and to each other:
- "CIS 2.1.1 checks capability/amazon.com/aws/s3#default-encryption"
- "Prowler s3_bucket_default_encryption implements CIS 2.1.1"
- "NIST SC-28 is satisfied by capability/amazon.com/aws/s3#default-encryption"

### Phase 4: Serve it all

An AI agent or engineer can then:
1. Start from any point (a capability, a control, a regulation, a tool check)
2. Traverse to find all related knowledge
3. Compare opinions from different authorities
4. Make informed decisions based on their specific context

## Scale

| Type | Entries | Source |
|------|---------|--------|
| Capabilities (AWS) | ~600 | AWS documentation |
| Capabilities (Azure) | ~400 | Azure documentation |
| Capabilities (GCP) | ~300 | GCP documentation |
| Prowler checks | 938 | Prowler metadata (Apache 2.0) |
| CIS Benchmark checks | ~500 | CIS (check license) |
| DISA STIG checks | ~1000+ | DISA (public domain) |
| Abstract controls (NIST, CCM, etc.) | ~500 | Already in SecID |
| Regulations | ~100 | Already in SecID |

Total: ~4,000+ interconnected entries across capabilities, controls, and regulations.

## Principles

1. **Capabilities are neutral facts.** They describe what exists, not what should be done.
2. **Opinions are all legitimate.** CIS, DISA, NIST, vendor best practices, Prowler — all have valid perspectives. None is "the right one" universally.
3. **Opinions may conflict.** That's reality. SecID makes conflicts visible, it doesn't resolve them.
4. **The capability is the anchor.** Opinions point to capabilities. Adding a new framework means mapping it to capabilities, not to every other framework.
5. **Vendor documentation is the source of truth for capabilities.** Not tools, not benchmarks — the vendor's own docs.
6. **Tools are opinion-makers too.** Prowler, ScoutSuite, etc. are sources of checks (controls), not capabilities.
7. **Vendors will hopefully take ownership.** We author their namespace initially, they maintain it long-term.
