"""Module for the LLM service."""
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
