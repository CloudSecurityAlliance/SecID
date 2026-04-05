# Capability Type (`capability`)

Identifiers for **concrete security features provided by products and services** — the specific, configurable, auditable security mechanisms that implement abstract control requirements.

## Purpose

Track and reference the actual security capabilities that products provide:

**Cloud Provider Security Features:**
- AWS S3 default encryption, CloudTrail multi-region logging, IAM MFA
- Azure Storage encryption at rest, Key Vault soft delete, NSG rules
- GCP Cloud Storage uniform bucket access, VPC Service Controls

**Product Security Configurations:**
- Specific settings that can be enabled, configured, audited, and mandated
- Each has CLI commands, API calls, console paths, and IaC references

## Why Capability Is Separate from Control and Entity

| Type | Identifies | Verb | Authority |
|------|-----------|------|-----------|
| `control` | Security requirements/specifications | MUST/SHALL/SHOULD | Standards bodies |
| `entity` | Products and services (neutral) | IS | Descriptive |
| `capability` | Product security features | CAN (actionable) | Product vendors |

**Control** says "encrypt data at rest" (NIST SC-28). **Capability** says "S3 Default Encryption with SSE-S3/SSE-KMS options, audit with `aws s3api get-bucket-encryption`." Control specifies what you must do. Capability tells you what you can do and exactly how.

## Identifier Format

```
secid:capability/<namespace>/<service>#<feature>

secid:capability/amazon.com/aws/s3#default-encryption
secid:capability/amazon.com/aws/cloudtrail#multi-region
secid:capability/amazon.com/aws/iam#mfa-root-account
secid:capability/microsoft.com/azure/storage#encryption-at-rest
secid:capability/google.com/gcp/cloud-storage#uniform-bucket-access
```

## Namespaces

### Cloud Providers

| Namespace | Services | Description |
|-----------|----------|-------------|
| `amazon.com/aws` | `s3`, `cloudtrail`, `iam`, `ec2`, ... | AWS service security features |
| `microsoft.com/azure` | `storage`, `key-vault`, `active-directory`, ... | Azure service security features |
| `google.com/gcp` | `cloud-storage`, `iam`, `compute`, ... | GCP service security features |

## Relationships

Capabilities connect to controls and entities:

```json
{
  "from": "secid:capability/amazon.com/aws/s3#default-encryption",
  "to": "secid:control/nist.gov/800-53#SC-28",
  "type": "implements",
  "description": "S3 default encryption implements data-at-rest encryption requirement"
}
```

```json
{
  "from": "secid:control/cisecurity.org/aws-benchmark@3.0#2.1.1",
  "to": "secid:capability/amazon.com/aws/s3#default-encryption",
  "type": "checks",
  "description": "CIS benchmark check verifies this capability is properly configured"
}
```

## V2 Data

Capability entries in V2 include actionable data:
- Configuration options (settings, values, defaults)
- Audit commands (CLI, API, console path)
- Remediation commands (CLI, API, console, IaC)
- Expected values for compliance

## Notes

- Capabilities are the largest SecID type by volume — cloud providers have thousands of security-relevant features
- Capabilities change frequently as products evolve — update cadence is much faster than controls
- The capability type enables the "last mile" of compliance: from abstract requirement to exact CLI command
