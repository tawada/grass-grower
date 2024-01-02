import os
import openai
from openai import OpenAI

client = OpenAI()


def generate_text(messages):
    model = "gpt-4-1106-preview"
    response = client.chat.completions.create(
        model=model,
        messages=messages,
    )
    print(response.choices[0].message)
    return response.choices[0].message.content
