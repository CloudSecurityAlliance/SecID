# Proposal: `capability` Type (9th SecID Type)

Status: Research / proposal
Date: 2026-04-05

## Summary

Add a 9th SecID type: `capability` — identifying concrete security features provided by products and services, with their configuration options, audit commands, and remediation instructions.

## The Problem

SecID currently has 8 types. When someone asks "how do I encrypt data at rest on AWS S3?", the answer involves:

1. **A control specification** — NIST 800-53 SC-28 says "encrypt data at rest" (what you MUST do)
2. **A benchmark check** — CIS AWS Benchmark 2.1.1 says "ensure S3 encryption is enabled" (what to verify)
3. **A product capability** — S3 Default Encryption with SSE-S3/SSE-KMS/SSE-KMS-DSSE (what you CAN do)
4. **Specific commands** — `aws s3api put-bucket-encryption ...` (HOW to do it)

Items 1-2 are specifications — they live in the `control` type. Item 3-4 are fundamentally different: they describe a product feature with configuration options and actionable commands. Today there's no SecID type for this.

## Why Not Use Existing Types?

### Why not `control`?

Controls are prescriptive — they say what you MUST/SHALL/SHOULD do. They come from standards bodies and regulatory frameworks. A product capability is descriptive — it says what you CAN do. The verbs are different, the authority is different, and the data shape is different.

Practical concern: the big three cloud providers (AWS, Azure, GCP) have ~200+ services each with ~5-20 security-relevant configurations. That's 10,000-50,000+ capability entries. Mixing them into `control` alongside ~2,000 framework specifications makes the type unnavigable.

### Why not `entity`?

Entity is neutral identification — "this thing exists." It describes what something IS, not what it can DO. Adding configuration options, CLI commands, and audit procedures to entity makes it half product catalog, half security operations manual.

Entity: "AWS S3 is an object storage service."
Capability: "S3 Default Encryption automatically encrypts objects. Options: AES256, aws:kms, aws:kms:dsse. Audit: `aws s3api get-bucket-encryption`. Remediate: `aws s3api put-bucket-encryption`."

These serve different consumers with different needs.

## The Distinction

| | Entity | Control | Capability |
|--|--------|---------|-----------|
| **Actor** | Nobody (neutral) | Standards body | Product vendor |
| **Verb** | IS | MUST/SHALL/SHOULD | CAN |
| **Authority** | Descriptive | Prescriptive | Descriptive but actionable |
| **Stability** | Stable | Changes with framework versions | Changes with product releases |
| **Data shape** | Description, metadata | Requirement text, audit criteria | Configuration options, CLI/API/console/IaC commands |
| **Consumer question** | "What is this?" | "What must I do?" | "How do I do it?" |
| **V2 data volume** | 100s of entries | 1,000s of entries | 10,000s-100,000s of entries |
| **Update frequency** | Rare | Annual (framework releases) | Continuous (product updates) |

## Identifier Format

```
secid:capability/<namespace>/<service>#<feature>

secid:capability/amazon.com/aws/s3#default-encryption
secid:capability/amazon.com/aws/cloudtrail#multi-region
secid:capability/amazon.com/aws/iam#mfa-root-account
secid:capability/microsoft.com/azure/storage#encryption-at-rest
secid:capability/microsoft.com/azure/key-vault#soft-delete
secid:capability/google.com/gcp/cloud-storage#uniform-bucket-access
secid:capability/google.com/gcp/iam#workload-identity-federation
```

The namespace is the vendor domain. The name is the service (often a sub-namespace path like `aws/s3`). The subpath is the specific security feature.

## V2 Data Shape

The capability type would be the largest consumer of V2 hosted data. Each entry includes actionable information:

```json
{
  "secid": "secid:capability/amazon.com/aws/s3#default-encryption",
  "schema_version": "1.0",
  "provenance": {
    "upstream_source": {
      "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html",
      "license": "AWS Documentation License (CC BY-SA 4.0)",
      "extracted_at": "2026-04-05T00:00:00Z"
    }
  },
  "content": {
    "service": "Amazon S3",
    "feature": "Default Encryption",
    "description": "Automatically encrypts all new objects stored in the bucket using server-side encryption.",
    "configuration": {
      "setting": "ServerSideEncryptionConfiguration",
      "options": [
        {
          "value": "AES256",
          "name": "SSE-S3",
          "description": "Amazon S3 managed keys"
        },
        {
          "value": "aws:kms",
          "name": "SSE-KMS",
          "description": "AWS KMS managed keys — per-key audit trail in CloudTrail"
        },
        {
          "value": "aws:kms:dsse",
          "name": "DSSE-KMS",
          "description": "Dual-layer server-side encryption with KMS keys"
        }
      ],
      "default": "AES256 (enabled by default since January 2023)"
    },
    "audit": {
      "cli": "aws s3api get-bucket-encryption --bucket {bucket}",
      "api": "GetBucketEncryption",
      "console": "S3 → Bucket → Properties → Default encryption",
      "expected": "ServerSideEncryptionConfiguration is present"
    },
    "remediation": {
      "cli": "aws s3api put-bucket-encryption --bucket {bucket} --server-side-encryption-configuration '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"aws:kms\"}}]}'",
      "api": "PutBucketEncryption",
      "console": "S3 → Bucket → Properties → Edit default encryption → AWS-KMS",
      "iac": {
        "terraform": "resource \"aws_s3_bucket_server_side_encryption_configuration\"",
        "cloudformation": "AWS::S3::Bucket BucketEncryption property"
      }
    }
  }
}
```

## Relationship Layer Integration

The capability type becomes the anchor point for cross-type relationships:

```
secid:control/nist.gov/800-53#SC-28 (requirement: "encrypt data at rest")
    ↓ "implemented_by"
secid:capability/amazon.com/aws/s3#default-encryption (product feature)
    ↑ "checked_by"
secid:control/cisecurity.org/aws-benchmark@3.0#2.1.1 (benchmark check)
    ↑ "required_by"
secid:regulation/europa.eu/gdpr#art-32 (legal requirement for encryption)
```

This inverts the traditional N-to-N framework mapping problem. Instead of mapping every framework to every other framework, each framework maps to capabilities. Adding a new framework means mapping it to capabilities, not to every existing framework. And the question "who else requires this same thing?" is trivially answered by looking at what points to each capability.

## Scale Estimates

| Vendor | Services | Capabilities (est.) |
|--------|----------|-------------------|
| AWS | ~200+ | 3,000-5,000 |
| Azure | ~200+ | 3,000-5,000 |
| GCP | ~100+ | 1,500-3,000 |
| Other major vendors | varies | 2,000-5,000 |
| **Total** | | **10,000-20,000+** |

This is significantly larger than any other SecID type. The V2 data repo (`SecID-capability/`) would be the largest in the federation.

## Data Sources

Where capability data comes from:

| Source | Coverage | Format | License |
|--------|----------|--------|---------|
| AWS documentation | All AWS services | HTML, structured API docs | AWS Doc License (CC BY-SA 4.0) |
| Azure documentation | All Azure services | HTML, REST API specs | Microsoft Docs License (CC BY 4.0) |
| GCP documentation | All GCP services | HTML, API reference | CC BY 4.0 |
| CIS Benchmarks | Major platforms | PDF, structured checks | CIS Terms of Use (check redistribution) |
| DISA STIGs | DoD-relevant platforms | XML (XCCDF), structured | US government work (public domain) |
| Vendor security guides | Varies | PDF, HTML | Varies |

DISA STIGs are public domain (US government work) and already contain structured audit/remediation data in XCCDF XML format — excellent for automated extraction.

## Implementation Plan Overview

### Phase 1: Type Definition (SecID spec repo)
- Add `capability` to SPEC.md type list
- Create `registry/capability.md` type description
- Create `registry/capability.json` type-level JSON
- Create `registry/capability/_template.md`
- Update CLAUDE.md, README.md with 9th type

### Phase 2: Service Update (SecID-Service)
- Add `capability` to SECID_TYPES
- Update MCP tool descriptions with capability examples
- Update website "Nine Types of Security Knowledge"
- Re-upload KV, deploy

### Phase 3: Client SDK Update (SecID-Client-SDK)
- Update type lists in all SDK languages
- Add capability examples to documentation

### Phase 4: Initial Registry Entries
- Start with a few well-known capabilities as proof of concept
- AWS S3 encryption, CloudTrail logging, IAM MFA
- Validate the pattern works before scaling

### Phase 5: V2 Data Repository
- Create `CloudSecurityAlliance-DataSets/SecID-capability/`
- Build extraction pipeline for DISA STIGs (public domain, structured XML)
- Build extraction pipeline for CIS Benchmarks (if license permits)
- Build extraction pipeline from cloud provider documentation

## Why a 9th Type (Not Overloading Existing Types)

SecID's principle is "split only when usage proves it necessary." The evidence:

1. **Different consumer** — security engineers implementing controls vs. compliance teams specifying requirements
2. **Different data shape** — CLI commands and configuration options vs. requirement text
3. **Different scale** — 10,000+ capabilities vs. ~2,000 control specifications
4. **Different update cadence** — continuous product updates vs. annual framework releases
5. **Different authority** — vendor-provided (descriptive) vs. standards body (prescriptive)
6. **V2 data federation** — capability data is the largest, most frequently updated data set. Mixing it with control data in the same repo creates noise.

The 8→9 type transition follows the same pattern as 7→8 (adding disclosure): a genuinely distinct category of security knowledge that serves different consumers with different questions.

## Open Questions

1. **Where does D3FEND go?** Defensive techniques are abstract (not product-specific). Probably `control` — they're specifications of defensive approaches, not product capabilities. But needs more thought.

2. **CIS Benchmark licensing** — can we redistribute per-check data? Need to verify CIS Terms of Use before V2 data hosting.

3. **Granularity** — is "S3 default encryption" one capability, or is each encryption option (SSE-S3, SSE-KMS, DSSE-KMS) a separate capability? Probably one capability with options — mirrors how practitioners think about it.

4. **Naming overlap** — AWS calls features different things in CLI vs. console vs. API. Which naming do we follow? Probably the CLI/API name since that's most machine-friendly, with aliases.

5. **Deprecation** — cloud providers deprecate features. How do we handle `secid:capability/amazon.com/aws/ec2#classic` when EC2-Classic is retired? Same pattern as existing `historical` status.

6. **Multi-cloud** — "encryption at rest" is a capability of S3, Azure Storage, AND GCP Cloud Storage. Do we need a way to express "these are equivalent capabilities across providers"? That's a relationship layer question.
