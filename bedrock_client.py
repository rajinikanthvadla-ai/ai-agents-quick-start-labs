import os

import boto3
from dotenv import load_dotenv

load_dotenv()

DEFAULT_MODEL_ID = "amazon.nova-lite-v1:0"


def _create_bedrock_client():
    region = os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION") or "us-east-1"
    profile = os.getenv("AWS_PROFILE")

    if profile:
        session = boto3.Session(profile_name=profile, region_name=region)
    else:
        session = boto3.Session(region_name=region)

    return session.client("bedrock-runtime")


def ask_bedrock(prompt, system_prompt=None, max_tokens=700, temperature=0.2):
    """Send one prompt to Amazon Bedrock and return the text response."""
    model_id = os.getenv("BEDROCK_MODEL_ID", DEFAULT_MODEL_ID)
    client = _create_bedrock_client()

    request = {
        "modelId": model_id,
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}],
            }
        ],
        "inferenceConfig": {
            "maxTokens": max_tokens,
            "temperature": temperature,
        },
    }

    if system_prompt:
        request["system"] = [{"text": system_prompt}]

    response = client.converse(**request)
    return response["output"]["message"]["content"][0]["text"]
