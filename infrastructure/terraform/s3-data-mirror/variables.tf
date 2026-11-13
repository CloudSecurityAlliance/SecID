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

variable "bucket_prefix" {
  type        = string
  description = "Prefix for the S3 bucket name (will be appended with account ID, region, and -an)"
  default     = "secid-data"
}
