# Text to Speech API

This API is a wrapper to [openai's text to speech api](https://api.openai.com/v1/audio/speech). It spins up an API Gateway with Lambda proxy integration and reveals an endpoint to which you may send `POST` requests to with some text you wish to get back as a text-to-speech audio file.

Lambda routes the text to openai, retrieves the mp3, stores it in an S3 bucket, and finally generating a signed URL to the file to which you may access for a 1 hour period.

As of now, it is mainly used to aid in content creation.

## Example Usage

```bash
curl -X POST -H "Content-Type: application/json" -d '{"output_name":"my_filename", "text_to_read":"hello world", "voice_type":"echo"}' https://5zrlvjgnaf.execute-api.us-west-2.amazonaws.com/dev/tts
```

The URL is an example. The output to `terraform apply` will provide you with the correct endpoint, to which you can append the gateway resource to (in the example, /tts).

The following parameters are required

```
output_name: string
text_to_read: string
voice_type: string - ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']
```

## Prerequisites

-   an AWS account
-   permissions for Lambda, API Gateway and S3
-   AWS CLI
-   AWS SAM CLI
-   Refer to the [AWS SAM Installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/prerequisites.html) for more details about setting up SAM
-   For local invocation, Docker is also required

## Setup

### Populate AWS credentials

Run `aws configure` to populate credentials.

By default, credentials are stored in `~/.aws/config` and `~/.aws/credentials`.

### Set api keys into AWS Secrets Manager

Because `OPENAI_API_KEY` is a sensitive key, it should be manually placed in `secrets manager`. The terraform setup reads from here to ultimately extract the key and deploy it as part of the environment variables to our lambda function.

Go to [secrets manager](https://us-west-2.console.aws.amazon.com/secretsmanager/listsecrets) (change to your region) > 'Store a new secret' > populate secret as `OPENAI_API_KEY`, and choose a unique secret name. You will use this created name to populate your terraform variables.

## Terraform Setup

### (Optional) Designate aws config/creds path

If you want to designate the location of config and credentials files outside of `~/.aws` In `main.tf`, uncomment `shared_config_files` and `shared_credentials_files` in the `provider "aws"` block (in which case you will need to also set them in a `terraform.tfvars` as well)

```
provider "aws" {
  region                     = var.aws_region
  # shared_config_files      = [var.config_location]
  # shared_credentials_files = [var.creds_location]
  profile                    = var.profile
}
```

### (Required) Populate Variables

In `tf-resources`, you will see a `variables.tf` file.

To initialize these variables, create a file, `terraform.tfvars` and populate them like so:

```
aws_region      = "us-west-2" (or whatever region you wish)
profile         = "default" (or whatever aws profile you wish to use)
s3_bucket_name  = "your_s3_bucket_name"
<...>
```

Example

```
aws_region                             = "us-west-2"
profile                                = "default"
openai_layer_abs_path                  = "/Users/daven.lu/dev/_learning/openai-tts-api/src/openai-layer.zip"
s3_bucket_name                         = "daven-dev-bucket"
source_code_path                       = "/Users/daven.lu/dev/_learning/openai-tts-api/src/text_to_voice"
secrets_manager_openai_api_secret_name = "dev/openai/daven_openai_secret"
```

## Infrastructure

Infrastructure is managed by Terraform.

API Gateway is setup with lambda proxy integration.

![infrastructure](/assets/infra.png)

API Gateway accepts a POST request with 3 parameters:

```json
{
    "output_name": <file_name>,
    "text_to_read": <text_to_read>,
    "voice_type": <one of ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']>
}
```

`output_name`: the resulting file stored in s3 will have <file_name>.mp3 as the output

`text_to_read`: the text that will be translated to speech and stored in <file_name>.mp3

`voice_type`: the voice to read the text in. Documentation about voices can be found [here](https://platform.openai.com/docs/guides/speech-to-text)

API Gateway invokes a Lambda function that handles calling openai to generate a mp3 file.

An example response:

```json
{
    "statusCode": 200,
    "body": {
        "message": "Upload file succeeded",
        "file_url": "https://dev-bucket.s3.amazonaws.com/hello_echo.mp3?AWSAccessKeyId=AKIATVKDXKJZ6&Signature=bazFe6RVL4VcWBASzREzrUBZovk%3D&Expires=1701593603"
    }
}
```

## Developing

-   When developing, run `sam build` to deploy changes.

## Motivations

https://aws.amazon.com/blogs/compute/better-together-aws-sam-cli-and-hashicorp-terraform/
