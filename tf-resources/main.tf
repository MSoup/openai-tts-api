terraform {
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 4.16"
    }
  }
  required_version = ">= 1.2.0"
}


provider "aws" {
  region = var.aws_region
  # shared_config_files      = [var.config_location]
  # shared_credentials_files = [var.creds_location]
  profile = var.profile
}

###################################
## Outputs                       ##
###################################

output "api_endpoint" {
  description = "Base url for api"
  value       = aws_api_gateway_stage.stage.invoke_url
}

# output "http_api_logs_command" {
#   description = "Command to view http api logs with sam"
#   value       = "sam logs --cw-log-group ${aws_cloudwatch_log_group.logs.name} -t"
# }
