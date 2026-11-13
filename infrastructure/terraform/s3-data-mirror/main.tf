terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source = "hashicorp/aws"
      # `bucket_namespace` (below) arrived in provider 6.37.0; 5.100 rejects it as
      # an unsupported argument. Pinned within 6.x, with the exact build in the
      # committed .terraform.lock.hcl.
      version = "~> 6.73"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  # Refuse to plan or apply in any other account, whatever profile is active.
  allowed_account_ids = [var.account_id]
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  # S3 Account Regional Namespace convention:
  # {prefix}-{account-id}-{region}-an
  bucket_name = "${var.bucket_prefix}-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.region}-an"
}

# 1. Bucket creation with Account Regional Namespace convention.
# A name ending in -an makes S3 require the x-amz-bucket-namespace: account-regional
# header on CreateBucket; `bucket_namespace` is what sends it.
resource "aws_s3_bucket" "secid_data" {
  bucket           = local.bucket_name
  bucket_namespace = "account-regional"

  # Permanent bucket: `terraform destroy` or a change that forces replacement
  # must fail instead of deleting it.
  lifecycle {
    prevent_destroy = true
  }

  tags = {
    Project     = "SecID"
    ManagedBy   = "Terraform"
    Environment = "Production"
    Purpose     = "Public Binary Gov Document Mirror - Requester Pays"
    Repository  = "https://github.com/CloudSecurityAlliance/SecID"
  }
}

# 2. Requester Pays: Egress and request costs billed to caller
#
# Owner pinning (CINO-Engineering DEC-035 §3): resources that accept
# expected_bucket_owner send ExpectedBucketOwner, so S3 refuses the call if the
# bucket is not owned by var.account_id.
resource "aws_s3_bucket_request_payment_configuration" "secid_data" {
  bucket                = aws_s3_bucket.secid_data.id
  expected_bucket_owner = var.account_id
  payer                 = "Requester"
}

# 2b. ACLs disabled: the bucket owner owns every object (DEC-035 §2).
resource "aws_s3_bucket_ownership_controls" "secid_data" {
  bucket = aws_s3_bucket.secid_data.id

  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

# 3. Allow public bucket policy while blocking legacy ACLs
resource "aws_s3_bucket_public_access_block" "secid_data" {
  bucket = aws_s3_bucket.secid_data.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

# 4. Public read policy. Principal "*" grants read to anyone, but a Requester Pays
# bucket rejects anonymous (unsigned) requests, so in practice only signed requests
# that send x-amz-request-payer: requester succeed, and the caller pays.
# Turning Requester Pays off would make this policy anonymous-public with CSA
# paying egress: change both together or not at all.
#
# Only current versions are readable: no s3:GetObjectVersion / s3:ListBucketVersions.
# If something is uploaded by mistake, deleting it must take it out of public view;
# public version access would leave it readable by versionId.
resource "aws_s3_bucket_policy" "secid_data" {
  bucket = aws_s3_bucket.secid_data.id
  # Publish the read grant only after Requester Pays is configured, so a failure
  # between the two cannot leave the bucket anonymous-public. depends_on orders the
  # API calls but cannot wait out AWS's propagation delay of several minutes: a
  # from-scratch rebuild must be staged (README, "Rebuilding from scratch").
  depends_on = [
    aws_s3_bucket_public_access_block.secid_data,
    aws_s3_bucket_request_payment_configuration.secid_data,
  ]

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Sid       = "AllowPublicRequesterPaysRead"
        Effect    = "Allow"
        Principal = "*"
        Action = [
          "s3:GetObject",
          "s3:ListBucket"
        ]
        Resource = [
          aws_s3_bucket.secid_data.arn,
          "${aws_s3_bucket.secid_data.arn}/*"
        ]
      },
      {
        # TLS only: documents must not be readable or replaceable in transit.
        Sid       = "DenyInsecureTransport"
        Effect    = "Deny"
        Principal = "*"
        Action    = "s3:*"
        Resource = [
          aws_s3_bucket.secid_data.arn,
          "${aws_s3_bucket.secid_data.arn}/*"
        ]
        Condition = {
          Bool = { "aws:SecureTransport" = "false" }
        }
      }
    ]
  })
}

# 5. Versioning: an overwrite or delete keeps the earlier copy, recoverable by
# maintainers. This is not immutability: anyone with s3:DeleteObjectVersion in the
# account can still remove versions (no Object Lock, so a mistaken upload can be purged).
resource "aws_s3_bucket_versioning" "secid_data" {
  bucket                = aws_s3_bucket.secid_data.id
  expected_bucket_owner = var.account_id
  versioning_configuration {
    status = "Enabled"
  }
}

# 6. Abandoned multipart uploads of large binaries are billable until removed.
# This rule only aborts incomplete uploads; it never expires objects or versions.
resource "aws_s3_bucket_lifecycle_configuration" "secid_data" {
  bucket                = aws_s3_bucket.secid_data.id
  expected_bucket_owner = var.account_id
  depends_on            = [aws_s3_bucket_versioning.secid_data]

  rule {
    id     = "abort-incomplete-multipart-uploads"
    status = "Enabled"

    filter {}

    abort_incomplete_multipart_upload {
      days_after_initiation = 7
    }
  }
}
