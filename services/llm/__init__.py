"""Module for the LLM service."""
from typing import Dict, List, Union

from openai import OpenAI

from utils.logging_utils import log


def generate_text(messages: List[Dict[str, str]]) -> Union[str, None]:
    """Generates text using the OpenAI API.

    Args:
        messages (List[Dict[str, str]]): A list of message dictionaries to send to the API.

    Returns:
        Union[str, None]: The generated text, or None if an error occurs.
    """
    model = "gpt-4-1106-preview"
    try:
        client = OpenAI()
        log(f"Generating text with model: {model}", level="info")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        generated_content = response.choices[0].message.content
        log(f"Text generated successfully: {generated_content[:50]}...",
            level="info")
        return generated_content
    except RuntimeError as err:
        log(f"Failed to generate text: {err}", level="error")
        return None
