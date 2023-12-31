import json
import logging
import os
import boto3
from openai import OpenAI
from botocore.exceptions import ClientError

from aws_lambda_powertools.utilities.data_classes import APIGatewayProxyEvent
from aws_lambda_powertools.utilities.typing import LambdaContext
from aws_lambda_powertools.utilities.validation import SchemaValidationError, validate

import schemas


# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Initialize the resources once per Lambda execution environment by using global scope.
_LAMBDA_S3_RESOURCE = {
    "resource": boto3.resource("s3"),
    "bucket_name": os.getenv("S3_BUCKET_NAME"),
    "client": boto3.client("s3"),
}


class LambdaS3Class:
    """
    AWS S3 Resource Class
    """

    def __init__(self, lambda_s3_resource):
        """
        Initialize an S3 Resource
        """
        self.resource = lambda_s3_resource["resource"]
        self.client = lambda_s3_resource["client"]
        self.bucket_name = lambda_s3_resource["bucket_name"]
        self.bucket = self.resource.Bucket(self.bucket_name)


class OpenAIClass:
    """
    OpenAI
    """

    def __init__(self, openai_resource):
        self.resource = openai_resource["resource"]


def lambda_handler(event: APIGatewayProxyEvent, context: LambdaContext):
    # Deserialize json string
    data = json.loads(event.get("body"))

    # Initialize classes
    s3_class = LambdaS3Class(_LAMBDA_S3_RESOURCE)
    openai_class = OpenAIClass({"resource": OpenAI})

    try:
        # Validate event.data payload
        # Check existing OPENAI_API_KEY
        # Check S3 bucket existence
        checkValidEnv(data, s3=s3_class)
    except ValueError as e:
        return generate_response(422, str(e))
    except SchemaValidationError as e:
        return generate_response(400, str(e))
    except ClientError as e:
        return generate_response(500, "Access forbidden or bucket does not exist.")
    except EnvironmentError as e:
        return generate_response(500, str(e))

    # three inputs should exist now
    output_name = data.get("output_name")
    text_to_read = data.get("text_to_read")
    voice_type = data.get("voice_type")

    try:
        binary_audio = create_audio(
            API=openai_class, text_to_read=text_to_read, voice_type=voice_type
        )
    except ValueError as e:
        return generate_response(422, str(e))

    file_name = f"{output_name}.mp3"

    try:
        upload_to_s3(file=binary_audio, s3=s3_class, object_name=file_name)
    except ClientError as e:
        print(e)
        return generate_response(500, "Unable to upload to S3, check permissions")

    s3_temp_url = get_signed_url(s3=s3_class, object_name=file_name)

    additional_data = {"file_url": s3_temp_url}

    return generate_response(200, "Upload file succeeded", extras=additional_data)


def create_audio(API: OpenAIClass, text_to_read: str, voice_type: str = "alloy"):
    if voice_type not in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
        raise ValueError(
            "Invalid voice_type. It must be one of ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']"
        )

    client = API.resource()

    response = client.audio.speech.create(
        model="tts-1", voice=voice_type, input=text_to_read
    )

    return response.read()


def upload_to_s3(file: bytes, s3: LambdaS3Class, object_name: str):
    """Upload a file to an S3 bucket

    :param file: bytes
    :param s3: s3_resource_class
    :param object_name: S3 object name
    :return: S3.object
    """
    # Upload the file

    response = s3.bucket.put_object(
        Key=object_name,
        Body=file,
    )

    return response


def get_signed_url(s3: LambdaS3Class, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    try:
        response = s3.client.generate_presigned_url(
            "get_object",
            Params={"Bucket": s3.bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
    # The response contains the presigned URL
    return response


def generate_response(statusCode: int, message: str, extras: dict = {}):
    """
    Helper to construct a response body

    :param statusCode: int, 200 default
    :param message: str
    :param extras: dictionary of k,v to append to response body
    :return: Http Response

    """
    # only response body will be shown through API gateway--the other response values are metadata
    response_body = {"message": message, "success": statusCode == 200}

    if extras:
        for k, v in extras.items():
            response_body[k] = v

    response = {
        "isBase64Encoded": False,
        "statusCode": statusCode,
        "headers": {"content-type": "application/json"},
        "multiValueHeaders": {},
        "body": "",
    }

    response["body"] = json.dumps(response_body)

    return response


def checkValidEnv(data, s3):
    """
    Validates lambda environment:
    :param data: dict, event["data"] payload, deserialized
    :param s3: LambdaS3Class
    """
    # Validate incoming payload
    validate(event=data, schema=schemas.INPUT_SCHEMA)

    # Validate env variables
    if not OPENAI_API_KEY:
        raise EnvironmentError("OPENAI_API_KEY not found")
    if not _LAMBDA_S3_RESOURCE["bucket_name"]:
        raise EnvironmentError("bucket_name env var not found")

    # Validate existing S3 bucket
    s3.client.head_bucket(Bucket=s3.bucket_name)
