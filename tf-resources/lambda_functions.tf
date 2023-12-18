module "lambda_function_tts" {
  source        = "terraform-aws-modules/lambda/aws"
  version       = "~> 6.0"
  timeout       = 300
  source_path   = var.source_code_path
  # source_path   = "/Users/daven.lu/dev/_learning/openai-tts-api/src/text_to_voice"
  function_name = "tts"
  handler       = "app.lambda_handler"
  runtime       = "python3.9"
  create_sam_metadata = true
  publish       = true
  architectures = [ "arm64" ]
  environment_variables = {
    "OPENAI_API_KEY" = var.openai_api_key
    S3_BUCKET_NAME = var.s3_bucket_name
  }
  # layers = [ "arn:aws:lambda:us-west-2:687391720917:layer:lambda-openai-layer:4" ]
  layers = [ aws_lambda_layer_version.lambda_openai_layer.arn ]
  allowed_triggers = {
    APIGatewayAny = {
      service    = "apigateway"
      source_arn = "${aws_api_gateway_rest_api.api.execution_arn}/*/*"
    }
  }
  policy = aws_iam_policy.lambda_s3_policy.arn
  attach_policy = true
}

resource "aws_iam_policy" "lambda_s3_policy" {
  name = "audio_artifacts_lambda_s3_policy"

    policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = [
          "s3:PutObject",
          "s3:GetObject",
          "s3:DeleteObject",
          "s3:ListBucket"
        ]
        Effect   = "Allow"
        Resource = "arn:aws:s3:::${var.s3_bucket_name}/*"
      }
    ]
  })
}

resource "aws_lambda_layer_version" "lambda_openai_layer" {
  description = "Lambda layer for Python 3.9, contains only openai and its dependencies"
  filename   = var.openai_layer_abs_path
  layer_name = "lambda-openai-layer"
  compatible_architectures = [ "arm64" ]
  compatible_runtimes = ["python3.9"]
}