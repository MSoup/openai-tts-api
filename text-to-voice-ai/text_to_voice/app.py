from openai import OpenAI
from s3_api import get_signed_url, upload_file as upload_to_s3

S3_BUCKET_NAME = "msoup-dev-bucket"

def lambda_handler(event, context):
    data = event.get("body")
    output_name = data.get("output_name") 
    text_to_read = data.get("text_to_read")
    voice_type = data.get("voice_type")

    if not (output_name and text_to_read):
       raise KeyError("API requires a output_name and text_to_read")
    
    binary_audio = create_audio(text_to_read, voice_type)
    file_name = f"{output_name}.mp3"

    upload_to_s3(file=binary_audio, bucket=S3_BUCKET_NAME, object_name=file_name)
    s3_temp_url = get_signed_url(bucket_name=S3_BUCKET_NAME, object_name=file_name)
    # Upload to s3 before returning
    return {
        "statusCode": 200,
        "body": 
            {
                "message": "Upload file succeeded",
                "file_url": s3_temp_url
            }
    }

def create_audio(text_to_read, voice_type="alloy"):
    if voice_type not in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
        raise ValueError("Invalid voice_type. It must be one of ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer']")
    
    client = OpenAI()

    response = client.audio.speech.create(
        model="tts-1",
        voice=voice_type,
        input=text_to_read
    )

    return response.read()