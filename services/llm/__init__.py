import logging
from openai import OpenAI


client = OpenAI()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def generate_text(messages: str) -> str:
    model = "gpt-4-1106-preview"
    try:
        logger.info(f"Generating text with model: {model}")
        response = client.chat.completions.create(
            model=model,
            messages=messages,
        )
        logger.info(f"Text generated successfully: {response.choices[0].message.content[:50]}...")
    except Exception as e:
        logger.error(f"Failed to generate text: {e}")
        return ""
    return response.choices[0].message.content
