"""routers_utils.py: This module contains utility functions for the routers module."""

import services.llm


def send_messages_to_system(messages, system_instruction):
    """Send messages to AI system for code generation."""
    messages.append({"role": "system", "content": system_instruction})
    openai_client = services.llm.get_openai_client()
    generated_text = services.llm.generate_text(messages, openai_client)
    return generated_text
