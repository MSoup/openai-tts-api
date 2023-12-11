# Text to Speech Tool

This tool is a wrapper to [openai's text to speech api](https://api.openai.com/v1/audio/speech). It stores your text to speech mp3 in an S3 bucket, generating a signed URL to the file to which you may access the file for 1 hour. Files are deleted after 7 days of inactivity. There are plans to expand this tool to be useful for all types of use cases. As of now, it is mainly used to aid in content creation.

## Prerequisites

- an AWS account
- permissions for Lambda, API Gateway and S3
- AWS CLI
- AWS SAM CLI
- Refer to the [AWS SAM Installation guide](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/prerequisites.html) for more details about

## Infrastructure

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
    "body": 
        {
            "message": "Upload file succeeded", 
            "file_url": "https://dev-bucket.s3.amazonaws.com/hello_echo.mp3?AWSAccessKeyId=AKIATVKDXKJZ6&Signature=bazFe6RVL4VcWBASzREzrUBZovk%3D&Expires=1701593603"
        }
}
```

## Developing

- When developing, run `sam build` to 'save' changes.
- Run `sam local invoke -e events/event.json` to test events against changes
- Note that the event json should be in the form

To test the lambda locally against the event.json
