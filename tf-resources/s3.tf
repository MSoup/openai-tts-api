resource "aws_s3_bucket" "audio_artifacts_bucket" {
  bucket = "${var.s3_bucket_name}"
}
