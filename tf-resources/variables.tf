variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "us-west-2"
}

variable "config_location" {
  description = "location of config file for aws provider"
  type        = string
  default     = "~/.aws/config"

}

variable "creds_location" {
  description = "location of credentials file for aws provider"
  type        = string
  default     = "~/.aws/credentials"
}

variable "source_code_path" {
  description = "directory where your app.py handler file resides"
  type        = string
}

variable "profile" {
  description = "AWS profile"
  type        = string
  default     = "default"
}

variable "openai_api_key" {
  description = "API Key for openai"
  type        = string
}

variable "secrets_manager_openai_api_secret_name" {
  description = "The secret name you set up in secrets manager for the openai api key"
  type        = string
}

variable "s3_bucket_name" {
  description = "S3 Bucket used to Store Audio artifacts"
  type        = string
}

variable "openai_layer_abs_path" {
  description = "absolute layer filepath - includes .zip"
  type        = string
}

