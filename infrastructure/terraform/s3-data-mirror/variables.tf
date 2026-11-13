variable "aws_region" {
  type        = string
  description = "AWS region for the S3 bucket"
  default     = "us-west-2"
}

variable "aws_profile" {
  type        = string
  description = "AWS CLI profile name for authentication"
  default     = "cino-prod"
}

variable "account_id" {
  type        = string
  description = "The only AWS account this module may run against (cino-prod). Pins the provider (allowed_account_ids) and the bucket owner (expected_bucket_owner), per CINO-Engineering DEC-035."
  default     = "502869771730"
}

variable "bucket_prefix" {
  type        = string
  description = "Prefix for the S3 bucket name (will be appended with account ID, region, and -an)"
  default     = "secid-data"
}
