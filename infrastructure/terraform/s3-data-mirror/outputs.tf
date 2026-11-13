output "bucket_name" {
  description = "Name of the created S3 bucket"
  value       = aws_s3_bucket.secid_data.id
}

output "bucket_arn" {
  description = "ARN of the created S3 bucket"
  value       = aws_s3_bucket.secid_data.arn
}

output "payer_status" {
  description = "Requester payment status"
  value       = aws_s3_bucket_request_payment_configuration.secid_data.payer
}
