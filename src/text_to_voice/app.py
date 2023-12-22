import json
import logging
import os
import boto3
from openai import OpenAI
from botocore.exceptions import ClientError

S3_BUCKET_NAME = os.getenv("daven-dev-bucket")
s3_client = boto3.client("s3")


def checkValidEnv(data):
    if S3_BUCKET_NAME is None:
        raise ValueError("S3 Bucket name doesn't exist. Check env variables")

    output_name = data.get("output_name")
    text_to_read = data.get("text_to_read")
    voice_type = data.get("voice_type")

    if any(val is None for val in [output_name, text_to_read, voice_type]):
        raise KeyError("Request body requires a output_name and text_to_read")


def lambda_handler(event, context):
    print(event)
    data = json.loads(event.get("body"))

    checkValidEnv(data)

    output_name = data.get("output_name")
    text_to_read = data.get("text_to_read")
    voice_type = data.get("voice_type")

    binary_audio = create_audio(text_to_read, voice_type)
    file_name = f"{output_name}.mp3"

    response = {
        "isBase64Encoded": False,
        "statusCode": 200,
        "headers": {},
        "multiValueHeaders": {},
        "body": "",
    }

    response_body = {
        "message": "",
    }

    if not upload_to_s3(
        file=binary_audio, bucket=S3_BUCKET_NAME, object_name=file_name
    ):
        response["statusCode"] = 500
        response_body["message"] = "Unable to upload to S3. Check permissions"
        response["body"] = json.dumps(response_body)
        return response

    s3_temp_url = get_signed_url(bucket_name=S3_BUCKET_NAME, object_name=file_name)

    response_body["message"] = "Upload file succeeded"
    response_body["file_url"] = s3_temp_url
    response["body"] = json.dumps(response_body)

    return response


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
