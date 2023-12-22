import json
import logging
import os
import boto3
from openai import OpenAI
from botocore.exceptions import ClientError

S3_BUCKET_NAME = os.getenv("daven-dev-bucket")
s3_client = boto3.client("s3")


def generate_response(statusCode: int, message: str, extras: dict = {}):
    # only response body will be shown through API gateway--the other response values are metadata
    response_body = {"message": message, "success": statusCode == 200}

    if extras:
        for k, v in extras:
            response_body[k] = v

    response = {
        "isBase64Encoded": False,
        "statusCode": statusCode,
        "headers": {},
        "multiValueHeaders": {},
        "body": "",
    }

    response["body"] = json.dumps(response_body)

    return response


def checkValidEnv(data):
    if S3_BUCKET_NAME is None:
        raise ValueError("S3 Bucket name doesn't exist. Check env variables")

    output_name = data.get("output_name")
    text_to_read = data.get("text_to_read")
    voice_type = data.get("voice_type")

    if any(val is None for val in [output_name, text_to_read, voice_type]):
        raise KeyError("Include in request body output_name, text_to_read, voice_type")


def lambda_handler(event, context):
    print(event)
    data = json.loads(event.get("body"))

    try:
        checkValidEnv(data)
    except ValueError as e:
        return generate_response(422, str(e))

    except KeyError as e:
        return generate_response(400, str(e))

    # three inputs should exist now
    output_name = data.get("output_name")
    text_to_read = data.get("text_to_read")
    voice_type = data.get("voice_type")

    try:
        binary_audio = create_audio(text_to_read, voice_type)
    except ValueError as e:
        return generate_response(422, str(e))

    file_name = f"{output_name}.mp3"

    if not upload_to_s3(
        file=binary_audio, bucket=S3_BUCKET_NAME, object_name=file_name
    ):
        return generate_response(500, "Unable to upload to S3, check permissions")

    s3_temp_url = get_signed_url(bucket_name=S3_BUCKET_NAME, object_name=file_name)

    return generate_response(200, "Upload file succeeded", {"file_url": s3_temp_url})


def create_audio(text_to_read, voice_type="alloy"):
    if voice_type not in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
        raise ValueError(
            "Invalid voice_type. It must be one of ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']"
        )

    client = OpenAI()

    response = client.audio.speech.create(
        model="tts-1", voice=voice_type, input=text_to_read
    )

    return response.read()


def upload_to_s3(file, bucket, object_name):
    """Upload a file to an S3 bucket

    :param file: bytes
    :param bucket: Bucket to upload to
    :param object_name: S3 object name
    :return: True if file was uploaded, else False
    """
    # Upload the file

    response = s3_client.put_object(Body=file, Bucket=bucket, Key=object_name)

    res = response["ResponseMetadata"]

    return res["HTTPStatusCode"] == 200


def get_signed_url(bucket_name, object_name, expiration=3600):
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except ClientError as e:
        logging.error(e)
        return None
    # The response contains the presigned URL
    return response
