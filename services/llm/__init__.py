"""Module for the LLM service."""
import json
import os
from typing import Dict, List

import openai

from config import config
from utils.logging_utils import log

from . import llm_exceptions

MODEL_NAME = config["openai_model_name"]


def get_openai_client(api_key: str = None) -> openai.OpenAI:
    """Factory function to create and configure an OpenAI client."""
    try:
        if api_key is None:
            api_key = os.environ["OPENAI_API_KEY"]
        return openai.OpenAI(api_key=api_key)
    except KeyError as err:
        log(
            ("OPENAI_API_KEY is not set in environment variables. "
             "Please set it to use LLM functionalities."),
            level="error",
        )
        raise llm_exceptions.NotFoundAPIKeyException(
            "API key must be provided as an argument or in the environment"
        ) from err


@llm_exceptions.retry_handler(0)
def generate_text(
    messages: List[Dict[str, str]],
    openai_client: openai.OpenAI,
) -> str:
    """Generates text using the OpenAI API.

    Args:
        messages (List[Dict[str, str]]): A list of message dictionaries to send to the API.
        openai_client (openai.OpenAI): An OpenAI client.

    Returns:
        Union[str, None]: The generated text, or None if an error occurs.
    """
    return generate_response(messages,
                             openai_client,
                             response_format={"type": "text"})


@llm_exceptions.retry_handler(3)
def generate_json(
    messages: List[Dict[str, str]],
    openai_client: openai.OpenAI,
) -> dict[str, str]:
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
    try:
        generated_json = generate_and_parse_json(
            messages,
            openai_client,
        )
        log(
            f"Text generated successfully: {json.dumps(generated_json)[:50]}...",
            level="info",
        )
        return generated_json
    # except llm_exceptions.LLMJSONParseException:
    #     raise
    except RuntimeError as err:
        log(
            f"Failed to generate json: {err}: ",
            level="error",
        )
        raise llm_exceptions.UnknownLLMException(
            "An unknown error occurred while generating the response") from err


def generate_and_parse_json(
    messages: list[dict[str, str]],
    openai_client: openai.OpenAI,
) -> dict:
    """Generates json using the OpenAI API and parses the response."""
    generated_content = generate_response(
        messages, openai_client, response_format={"type": "json_object"})
    return parse_json_response(generated_content)


def parse_json_response(generated_content: str) -> dict:
    """Parses the json response from a string.

    Handles JSONDecodeError by logging an error message and returning
    an empty dict or raising a more specific exception.
    """
    try:
        return json.loads(generated_content)
    except json.JSONDecodeError as err:
        log(f"Failed to parse JSON response: {err}", level="error")
        raise llm_exceptions.LLMJSONParseException("Invalid JSON response.")


def generate_response(
    messages: List[Dict[str, str]],
    openai_client: openai.OpenAI,
    response_format: Dict[str, str] = {"type": "text"},
) -> str:
    """Generates a response using the OpenAI API.

    Args:
        messages (List[Dict[str, str]]): A list of message dictionaries to send to the API.
        openai_client (openai.OpenAI): An OpenAI client.
        response_format (Dict[str, str], optional): The format of the response.
        Can be {"type": "text"} or {"type": "json_object"}. Defaults to {"type": "text"}.

    Returns:
        str: The generated response

    Raises:
        ValueError: If the retry argument is negative.
        RuntimeError: If the request fails after multiple retries.
    """
    log(f"Generating response with model: {MODEL_NAME}", level="info")
    try:
        response = openai_client.chat.completions.create(
            model=MODEL_NAME,
            messages=messages,
            response_format=response_format,
        )
        generated_content = response.choices[0].message.content
        log(
            f"Response generated successfully: {generated_content[:50]}...",
            level="info",
        )
        return generated_content
    except RuntimeError as err:
        log(f"Failed to generate response: {err}", level="error")
        raise
