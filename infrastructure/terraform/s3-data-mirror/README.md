# SecID S3 Binary Mirror (Terraform)

This directory contains the Terraform configuration for provisioning the public S3 binary mirror bucket for SecID.

## Purpose

The bucket archives publisher binary documents (`.pdf`, `.xlsx`, `.docx`, `.zip`) for **public government and open legal standards** (U.S. Public Laws, NIST SPs, White House EOs, EU EUR-Lex legal texts, Canadian LEGISinfo bills).

- **Strictly public government & open standards:** No corporate/vendor marketing material, no internal/commercial CSA documents, and no Tier 4 paid standards (ISO/IEC).
- **Requester Pays (`Payer = Requester`):** Callers authenticate with their own AWS account and pay AWS directly for GET requests and egress data transfer. CSA incurs $0 in egress fees.
- **Account Regional Namespace:** Compatible with [AWS Account Regional Namespaces](https://aws.amazon.com/blogs/aws/introducing-account-regional-namespaces-for-amazon-s3-general-purpose-buckets/) using the format:
  `secid-data-{account-id}-{region}-an`

## Directory Structure (ADR-014 Layout)

Objects inside the bucket follow the mechanical reverse-DNS convention from `docs/reference/DATA-HOSTING-RULES.md` §4:

```
data/<type>/<reverse-dns-namespace>/<name>/<version>/<filename>
```

Examples:
- `data/regulation/gov/govinfo/hipaa/hipaa.pdf`
- `data/regulation/gov/govinfo/cisa-2015/cisa-2015.pdf`
- `data/control/gov/nist/800-53/rev5/sp800-53r5.pdf`
- `data/reference/gov/whitehouse/ncs/2023/ncs.pdf`
- `data/regulation/ca/parl/bill-c-34/bill-c-34.pdf`

## Deployment

Requires the `cino-prod` AWS CLI profile:

```bash
terraform init
terraform plan
terraform apply
```

## Downloading from the Bucket (Requester Pays)

External callers download objects using AWS credentials with the `--request-payer requester` flag:

```bash
aws s3 cp s3://secid-data-<account-id>-<region>-an/data/regulation/gov/govinfo/hipaa/hipaa.pdf . --request-payer requester
```
