# SecID S3 Binary Mirror (Terraform)

Terraform for the public S3 bucket that mirrors publisher binaries (`.pdf`, `.xlsx`, `.docx`, `.zip`) behind SecID. Decision record: [ADR-017](../../../DECISIONS.md#adr-017-public-s3-binary-mirror-with-account-regional-namespaces-and-requester-pays-for-public-government-and-open-legal-standards).

Bucket: **`secid-data-502869771730-us-west-2-an`** (`cino-prod` account, `us-west-2`). It is permanent: `prevent_destroy` makes Terraform refuse to delete or replace it.

## What may go in it

Only documents that are safe to mirror publicly: public government publications and open standards (US public laws, NIST SPs, White House EOs, EUR-Lex texts, Canadian bills). Kurt, 2026-11-12: *"we mirror 'Safe' stuff like gov docs, public docs, not corp stuff, e.g. no csa"*.

This is narrower than the public dataset's rule ([DATA-HOSTING-RULES.md Rule 0](../../../docs/reference/DATA-HOSTING-RULES.md)). Tier 2 (open web, no login) lets vendor material such as glossaries into the public *text* repositories, but not into this bucket.

Never: CSA documents, corporate or vendor material even when it is on the open web, Tier 3 (free login), or Tier 4 paid standards (ISO/IEC and the like).

## Who can read it, and who pays

- **Requester Pays is on.** S3 rejects anonymous requests to a Requester Pays bucket, so every request must be signed with AWS credentials and send `x-amz-request-payer: requester`. The account whose credentials signed it pays for that request and its data transfer. That is normally the reader, but for a presigned URL it is whoever presigned it.
- **What CSA still pays for:** storage (including retained versions), its own uploads, listings and downloads, and the requests [AWS bills to the bucket owner](https://docs.aws.amazon.com/AmazonS3/latest/userguide/RequesterPaysBuckets.html) (for example, denied requests from within CSA's own account or organization). External readers cannot run up CSA's transfer bill.
- **The bucket policy allows `s3:GetObject` and `s3:ListBucket` to `Principal: "*"`.** Because of Requester Pays, that means any AWS account willing to pay, not anonymous users.
- **Never turn Requester Pays off on its own.** Without it the same policy makes the bucket anonymous-public, and CSA pays all egress.
- **HTTPS only.** The policy denies every request that doesn't use TLS.
- **Only current versions are public.** Versioning is on, so an overwritten or deleted file keeps its earlier copy, but only maintainers can read old versions. This is deliberate: if something is uploaded by mistake, deleting it must actually take it out of public view. Versioning is not immutability; there is no Object Lock, so maintainers can purge a version that should never have been there.
- Public ACLs are blocked; access is by policy only. Unfinished multipart uploads are aborted after 7 days, so abandoned uploads don't accrue storage charges.

```bash
aws s3 cp --request-payer requester \
  s3://secid-data-502869771730-us-west-2-an/data/control/gov/nist/800-53/rev5/NIST.SP.800-53r5.pdf .
```

## Object layout (ADR-014)

Keys follow the same mechanical derivation as the `SecID-Data-*` repositories ([DATA-HOSTING-RULES.md §4](../../../docs/reference/DATA-HOSTING-RULES.md)): SecID type, then the publisher domain in reverse-DNS, then the source name, then the version.

```
data/<type>/<tld>/<domain>/<name>[/<version>]/<publisher-filename>
```

- The `<version>` level appears **only when the SecID has a version**. For a source the registry does not version (most statutes), files sit directly under `<name>/`, and S3 object versioning keeps earlier fetches for maintainers.
- `<publisher-filename>` is the file name as the publisher served it, unchanged, for provenance.

| SecID | Object key |
|---|---|
| `secid:control/nist.gov/800-53@rev5` | `data/control/gov/nist/800-53/rev5/NIST.SP.800-53r5.pdf` |
| `secid:reference/whitehouse.gov/national-cybersecurity-strategy@2023` | `data/reference/gov/whitehouse/national-cybersecurity-strategy/2023/<publisher-filename>.pdf` |
| `secid:regulation/govinfo.gov/hipaa` | `data/regulation/gov/govinfo/hipaa/<publisher-filename>.pdf` |
| `secid:regulation/parl.ca/bill-c-34` | `data/regulation/ca/parl/bill-c-34/<publisher-filename>.pdf` |

## Running Terraform

Needs the `cino-prod` AWS profile (`aws sso login --profile cino-prod`).

```bash
terraform init      # uses the committed .terraform.lock.hcl (aws provider 6.73.0)
terraform plan      # expected: "No changes" against the live bucket
terraform apply
```

**State is local, on purpose.** `terraform.tfstate` lives in this directory on the maintainer's machine and is gitignored. Kurt, 2026-11-13: *"the terraform state is ok, because this is a permanent s3 bucket"*. The bucket is created once and rarely changed, so a remote backend isn't worth having. If the state file is ever lost, rebuild it from the live bucket instead of re-applying:

```bash
B=secid-data-502869771730-us-west-2-an
terraform import aws_s3_bucket.secid_data "$B"
terraform import aws_s3_bucket_request_payment_configuration.secid_data "$B"
terraform import aws_s3_bucket_public_access_block.secid_data "$B"
terraform import aws_s3_bucket_policy.secid_data "$B"
terraform import aws_s3_bucket_versioning.secid_data "$B"
terraform import aws_s3_bucket_lifecycle_configuration.secid_data "$B"
terraform plan      # should again show "No changes"
```
