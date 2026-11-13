terraform {
  required_version = ">= 1.5.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = ">= 5.0"
    }
  }
}

provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile
}

data "aws_caller_identity" "current" {}
data "aws_region" "current" {}

locals {
  # S3 Account Regional Namespace convention:
  # {prefix}-{account-id}-{region}-an
  bucket_name = "${var.bucket_prefix}-${data.aws_caller_identity.current.account_id}-${data.aws_region.current.region}-an"
}

# 1. Bucket creation with Account Regional Namespace convention
resource "aws_s3_bucket" "secid_data" {
  bucket           = local.bucket_name
  bucket_namespace = "account-regional"

  tags = {
    Project     = "SecID"
    ManagedBy   = "Terraform"
    Environment = "Production"
    Purpose     = "Public Binary Gov Document Mirror - Requester Pays"
    Repository  = "https://github.com/CloudSecurityAlliance/SecID"
  }
}

# 2. Requester Pays: Egress and request costs billed to caller
resource "aws_s3_bucket_request_payment_configuration" "secid_data" {
  bucket = aws_s3_bucket.secid_data.id
  payer  = "Requester"
}

# 3. Allow public bucket policy while blocking legacy ACLs
resource "aws_s3_bucket_public_access_block" "secid_data" {
  bucket = aws_s3_bucket.secid_data.id

  block_public_acls       = true
  ignore_public_acls      = true
  block_public_policy     = false
  restrict_public_buckets = false
}

# 4. Public Read Policy for Authenticated AWS Requesters (Requester Pays)
resource "aws_s3_bucket_policy" "secid_data" {
  bucket     = aws_s3_bucket.secid_data.id
  depends_on = [aws_s3_bucket_public_access_block.secid_data]

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
      }
    ]
  })
}

# 5. Versioning enabled for immutability and provenance tracking
resource "aws_s3_bucket_versioning" "secid_data" {
  bucket = aws_s3_bucket.secid_data.id
  versioning_configuration {
    status = "Enabled"
  }
}
