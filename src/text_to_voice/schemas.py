"""
# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.
# SPDX-License-Identifier: MIT-0

# Start of lambda schema definition code:  src/sampleLambda/schema.py
"""

INPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Schema for payload within lambda event['body']",
    "description": "API Gateway lambda proxy integration passes 'body' into lambda as a string",
    "type": "object",
    "required": ["output_name", "text_to_read", "voice_type"],
    "properties": {
        "output_name": {
            "type": "string",
            "title": "The name that the audio file should take on",
            "examples": ["example_audio"],
            "maxLength": 30,
        },
        "text_to_read": {
            "type": "string",
            "title": "The text that the audio file contain",
            "examples": ["Hello world"],
            "maxLength": 250,
        },
        "voice_type": {
            "type": "string",
            "title": "The type of voice for the audio to be read in",
            "enum": ["alloy", "echo", "fable", "onyx", "nova", "shimmer"],
        },
    },
}

OUTPUT_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema",
    "$id": "http://example.com/example.json",
    "type": "object",
    "title": "Sample outgoing schema",
    "description": "The root schema comprises the entire JSON document.",
    "examples": [{"statusCode": 200, "body": "OK"}],
    "required": ["statusCode", "body"],
    "properties": {
        "statusCode": {
            "$id": "#/properties/statusCode",
            "type": "integer",
            "title": "The statusCode",
        },
        "body": {"type": "string", "title": "The response"},
    },
}

# End of schema definition code
