# Capability Authoring Process

How we research, document, and maintain cloud service security capabilities.

## Principles

1. **One file per service.** `registry/capability/com/amazon/aws/s3.json`, not one giant AWS file.
2. **Capture everything, fill in later.** If we find a capability, list it as a match_node even if we don't have full details yet. A stub entry with a description is better than nothing.
3. **Explicit "we looked and found nothing."** Services with no security-relevant configurations get a file with `match_nodes: []` and notes explaining what we reviewed. Null means "researched, nothing found." Absent means "not yet researched."
4. **Vendor docs are the source of truth.** AWS documentation describes what AWS provides. Not Prowler, not CIS, not DISA — those are opinions about what you should do with what AWS provides.
5. **Foundation services first.** IAM, KMS, VPC, CloudTrail, CloudWatch — everything else depends on these.
6. **Cross-references, not stubs for dependencies.** When S3 references KMS, link to `secid:capability/amazon.com/aws/kms#...` — don't create a stub KMS entry. This is why we do foundation services first.

## File Structure

Each service gets its own file:

```
registry/capability/com/amazon/aws/
├── iam.json          ← Foundation: identity and access
├── kms.json          ← Foundation: encryption keys
├── vpc.json          ← Foundation: networking
├── cloudtrail.json   ← Foundation: audit logging
├── cloudwatch.json   ← Foundation: monitoring
├── s3.json           ← Storage
├── ec2.json          ← Compute
├── ebs.json          ← Block storage (separate from EC2)
├── rds.json          ← Database
├── lambda.json       ← Serverless compute
├── ...
```

The namespace is `amazon.com/aws/<service>`. The service name is the match_node name (just one per file since each file IS one service). Children are the individual capabilities.

```json
{
  "schema_version": "1.0",
  "namespace": "amazon.com/aws/s3",
  "type": "capability",
  "status": "draft",
  "status_notes": "Initial research from AWS documentation. Reviewed 2026-04-05.",

  "official_name": "Amazon Simple Storage Service",
  "common_name": "S3",
  "notes": "Object storage service. Security features include server-side encryption, bucket policies, access control lists, VPC endpoints, access logging, versioning, object lock, MFA delete, and block public access.",
  "urls": [
    {"type": "website", "url": "https://aws.amazon.com/s3/"},
    {"type": "docs", "url": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/security.html", "note": "S3 Security chapter"},
    {"type": "docs", "url": "https://docs.aws.amazon.com/AmazonS3/latest/API/", "note": "S3 API Reference"}
  ],

  "match_nodes": [
    {
      "patterns": ["(?i)^default-encryption$"],
      "description": "S3 bucket default server-side encryption",
      "weight": 100,
      "data": {
        "description": "Automatically encrypts all new objects stored in the bucket using server-side encryption.",
        "options": [
          {"value": "AES256", "name": "SSE-S3", "description": "Amazon S3 managed keys"},
          {"value": "aws:kms", "name": "SSE-KMS", "description": "AWS KMS managed keys — per-key audit trail in CloudTrail"},
          {"value": "aws:kms:dsse", "name": "DSSE-KMS", "description": "Dual-layer server-side encryption with KMS keys"}
        ],
        "default": {"value": "AES256", "since": "2023-01-05", "note": "All new buckets have SSE-S3 enabled by default since January 2023"},
        "vendor_recommendation": "Use SSE-KMS for sensitive data to enable key rotation, audit trail, and cross-account access controls",
        "audit": {
          "cli": "aws s3api get-bucket-encryption --bucket {bucket}",
          "api": "GetBucketEncryption",
          "console": "S3 → Bucket → Properties → Default encryption"
        },
        "configure": {
          "cli": "aws s3api put-bucket-encryption --bucket {bucket} --server-side-encryption-configuration '{\"Rules\":[{\"ApplyServerSideEncryptionByDefault\":{\"SSEAlgorithm\":\"aws:kms\"}}]}'",
          "api": "PutBucketEncryption",
          "console": "S3 → Bucket → Properties → Edit default encryption",
          "terraform": "aws_s3_bucket_server_side_encryption_configuration",
          "cloudformation": "AWS::S3::Bucket BucketEncryption"
        },
        "cross_references": [
          "secid:capability/amazon.com/aws/kms"
        ],
        "source": "https://docs.aws.amazon.com/AmazonS3/latest/userguide/bucket-encryption.html"
      }
    },
    {
      "patterns": ["(?i)^block-public-access$"],
      "description": "S3 Block Public Access settings",
      "weight": 100,
      "data": {
        "description": "Account-level and bucket-level settings that prevent public access to S3 resources.",
        "...": "full details"
      }
    }
  ]
}
```

## Status Values for Capability Files

| Status | Meaning |
|--------|---------|
| `stub` | File exists, service identified, no capabilities researched yet |
| `draft` | Capabilities identified and documented, needs review |
| `published` | Reviewed and verified against current AWS documentation |
| `needs-update` | AWS has released changes that aren't reflected yet |

## Research Process Per Service

### Pass 1: Service Overview (30 minutes per service)

Read the service documentation to understand what it does and what security features it provides.

**Sources (in order):**
1. Service security chapter: `docs.aws.amazon.com/<service>/latest/userguide/security.html`
2. Service best practices: `docs.aws.amazon.com/<service>/latest/userguide/best-practices.html`
3. Service FAQ security section: `aws.amazon.com/<service>/faqs/`

**Extract:**
- List of security-relevant features (encryption, access control, logging, networking)
- For each feature: what it does, what the options are, what the default is
- Vendor recommendations ("AWS recommends...")
- Recent changes (new defaults, deprecated options)

**Output:** Draft list of match_nodes with descriptions

### Pass 2: API Reference Scan (30-60 minutes per service)

Systematically scan API operations for security-relevant parameters.

**Source:** `docs.aws.amazon.com/<service>/latest/APIReference/`

**What to look for:**
- Operations with `Encryption`, `Kms`, `Key`, `Policy`, `Permission`, `Auth`, `Access`, `Security`, `Log`, `Audit`, `Vpc`, `Subnet`, `Secret`, `Token`, `Certificate`, `Tls`, `Ssl` in their name or parameters
- `Put*`, `Create*`, `Update*` operations that accept security-relevant configuration
- Any operation that changes the security posture of a resource

**Output:** Additional capabilities not found in Pass 1

### Pass 3: Cross-Reference Check (15 minutes per service)

Check existing tools/benchmarks for capabilities we might have missed.

**Sources:**
- Prowler checks for this service: `prowler/providers/aws/services/<service>/`
- CIS AWS Benchmark section for this service (if available)
- AWS Security Hub checks for this service

**This is NOT the source of truth** — it's a completeness check. If Prowler checks something we didn't find in the docs, we go back to the docs to understand what the underlying capability is.

**Output:** Any capabilities missed in Pass 1-2

### Pass 4: Structure and Write (30 minutes per service)

Structure the findings into a registry JSON file.

**For each capability:**
1. Write neutral description (what it IS, not what you should do)
2. List configuration options with descriptions
3. Document defaults (current and historical if recently changed)
4. Include vendor recommendation (labeled as such)
5. Write audit command (CLI, API, console path)
6. Write configure command (CLI, API, console, Terraform, CloudFormation)
7. Note cross-references to other services (IAM, KMS, VPC)
8. Include source URL (specific doc page)

### Pass 5: Human Review

Validate against actual AWS environment:
- Do the CLI commands work?
- Are the options accurate?
- Are the defaults current?
- Did we miss anything?

## Wave Plan

### Wave 1: Foundation Services (do first — everything depends on these)

| Service | Est. Capabilities | Priority | Dependencies |
|---------|-------------------|----------|--------------|
| IAM | 30+ | Highest | None |
| KMS | 10+ | Highest | IAM |
| VPC | 20+ | Highest | IAM |
| CloudTrail | 10+ | Highest | IAM, KMS, S3 |
| CloudWatch | 15+ | Highest | IAM |

### Wave 2: Core Services (most commonly audited)

| Service | Est. Capabilities | Dependencies |
|---------|-------------------|--------------|
| S3 | 15+ | IAM, KMS, VPC |
| EC2 | 20+ | IAM, VPC, KMS |
| EBS | 5+ | IAM, KMS |
| RDS | 15+ | IAM, KMS, VPC |
| Lambda | 10+ | IAM, KMS, VPC |
| ECS/EKS | 15+ | IAM, KMS, VPC |

### Wave 3: Data Services

| Service | Est. Capabilities | Dependencies |
|---------|-------------------|--------------|
| DynamoDB | 8+ | IAM, KMS |
| ElastiCache | 8+ | IAM, KMS, VPC |
| Redshift | 10+ | IAM, KMS, VPC |
| Elasticsearch/OpenSearch | 10+ | IAM, KMS, VPC |

### Wave 4: Application/Edge Services

| Service | Est. Capabilities | Dependencies |
|---------|-------------------|--------------|
| API Gateway | 10+ | IAM, KMS, VPC |
| CloudFront | 10+ | IAM, KMS |
| ALB/NLB | 8+ | IAM, VPC |
| WAF | 5+ | IAM |
| Route 53 | 5+ | IAM |

### Wave 5: Security Services

| Service | Est. Capabilities | Dependencies |
|---------|-------------------|--------------|
| GuardDuty | 5+ | IAM |
| SecurityHub | 5+ | IAM |
| Config | 8+ | IAM, S3 |
| Inspector | 5+ | IAM |
| Macie | 5+ | IAM, S3 |

### Wave 6: Everything Else

Remaining ~200 services. Many will have minimal security surface (IAM-only). These get stub files with explicit "reviewed, no service-specific security capabilities beyond IAM" notes.

## Applying to Other Providers

The same process applies to Azure, GCP, DigitalOcean, OpenShift, etc. Each gets its own namespace directory:

```
registry/capability/com/amazon/aws/     ← AWS services
registry/capability/com/microsoft/azure/ ← Azure services
registry/capability/com/google/gcp/     ← GCP services
registry/capability/com/digitalocean/   ← DigitalOcean services
registry/capability/com/redhat/openshift/ ← OpenShift capabilities
```

The research process is the same — vendor docs first, API scan second, tool cross-reference third. The wave ordering may differ per provider (Azure's foundation services are different from AWS's).

## Maintenance

Cloud services change constantly. Capabilities need periodic refresh:

- **New features:** AWS announces new security features → add capability entries
- **Changed defaults:** AWS changes a default → update the default field with dates
- **Deprecated features:** AWS deprecates a feature → mark status as deprecated
- **Re-review cadence:** Major services (S3, EC2, IAM) quarterly. Minor services annually.

Monitor sources:
- AWS What's New: https://aws.amazon.com/new/
- AWS Security Blog: https://aws.amazon.com/blogs/security/
- Prowler releases (may add checks for new features before we do)
