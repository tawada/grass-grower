"""Module for the LLM service."""
from typing import Dict, List, Union

from openai import OpenAI

from utils.logging_utils import log


def generate_text(messages: List[Dict[str, str]]) -> Union[str, None]:
    """Generates text using the OpenAI API."""
    model = "gpt-4-1106-preview"
    try:
        client = OpenAI()
        log(f"Generating text with model: {model}", level="info")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        log(f"Text generated successfully: {response.choices[0].message.content[:50]}...",
            level="info")
    except ConnectionError as err:
        log(f"Failed to generate text: {err}", level="error")
        return None
    return response.choices[0].message.content
