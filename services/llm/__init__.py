"""Module for the LLM service."""
import json
import os
from typing import Dict, List, Union

import openai

from utils.logging_utils import log

MODEL_NAME = os.environ.get('OPENAI_MODEL_NAME', 'gpt-4-0125-preview')


def get_openai_client(api_key: str = None) -> openai.OpenAI:
    """Factory function to create and configure an OpenAI client."""
    return openai.OpenAI(api_key=api_key or os.environ["OPENAI_API_KEY"])


def generate_text(
    messages: List[Dict[str, str]],
    openai_client: openai.OpenAI,
) -> Union[str, None]:
    """Generates text using the OpenAI API.

    Args:
        messages (List[Dict[str, str]]): A list of message dictionaries to send to the API.
        openai_client (openai.OpenAI): An OpenAI client.

    Returns:
        Union[str, None]: The generated text, or None if an error occurs.
    """
    try:
        log(f"Generating text with model: {MODEL_NAME}", level="info")
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
        )
        generated_content = response.choices[0].message.content
        log(f"Text generated successfully: {generated_content[:50]}...",
            level="info")
        return generated_content
    except RuntimeError as err:
        log(f"Failed to generate text: {err}", level="error")
        return None


def generate_json(
    messages: List[Dict[str, str]],
    openai_client: openai.OpenAI,
    retry: int = 0,
) -> Union[str, None]:
    """Generates json using the OpenAI API.

    Args:
        messages (List[Dict[str, str]]): A list of message dictionaries to send to the API.
        openai_client (openai.OpenAI): An OpenAI client.
        retry (int, optional): The number of times to retry the request. Defaults to 0.

    Returns:
        Union[str, None]: The generated json, or None if an error occurs.

    Raises:
        ValueError: If the retry argument is negative.
        RuntimeError: If the request fails after multiple retries.
    """
    log(f"Generating json with model: {MODEL_NAME}", level="info")
    if retry < 0:
        raise ValueError("Retry must be a non-negative integer")
    for i in range(retry + 1):
        try:
            response = openai_client.chat.completions.create(
                model=MODEL_NAME,
                messages=messages,
                response_format={"type": "json_object"},
            )
            generated_content = json.loads(response.choices[0].message.content)
            log(f"Text generated successfully: {json.dumps(generated_content)[:50]}...",
                level="info")
            return generated_content
        except RuntimeError as err:
            log(f"Failed to generate json: trial {i}: {err}", level="error")
            continue
    raise RuntimeError("Failed to generate json after multiple retries")
