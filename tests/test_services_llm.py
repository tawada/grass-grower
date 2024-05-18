"""Test services.llm module."""
import pytest

import services.llm
from services.llm import llm_exceptions


def test_services_llm_generate_text(
    mocker,
    setup_llm_detail,
):
    """Test llm.generate_text() function."""
    setup_llm_detail(mocker)
    openai_client = services.llm.get_openai_client()
    services.llm.generate_text([{"text": "Hello, world!"}], openai_client)


def test_services_llm_get_openai_client_failed_key_error(mocker):
    """Test llm.get_openai_client() function."""
    mocker.patch.dict("os.environ", {}, clear=True)
    with pytest.raises(llm_exceptions.NotFoundAPIKeyException):
        services.llm.get_openai_client()


def test_services_llm_generate_json(
    mocker,
    setup_llm_detail,
):
    """Test llm.generate_json() function."""
    setup_llm_detail(mocker)
    openai_client = services.llm.get_openai_client()
    services.llm.generate_json([{"text": "Hello, world!"}], openai_client)


def test_services_llm_generate_json_fail_invalid_response(
    mocker,
    setup_llm_detail,
):
    """Test llm.generate_json() function."""
    setup_llm_detail(mocker)

    mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "test"})

    class MockOpenAIObject:
        """Mock OpenAI class."""

        def __init__(self, api_key=None):
            self.api_key = api_key
            self.chat = self
            self.completions = self
            self.choices = [self]
            self.message = self
            self.content = "Hello, world!"
            self.model = None
            self.messages = None

        def create(
            self,
            model,
            messages,
            response_format={"type": "text"},
        ):
            """Mock create function."""
            self.model = model
            self.messages = messages
            if response_format["type"] == "json_object":
                self.content = "not json"
            return self

        def __str__(self):
            """Mock __str__ function."""
            return self.content

    mocker.patch("openai.OpenAI", new=MockOpenAIObject)

    openai_client = services.llm.get_openai_client()
    with pytest.raises(llm_exceptions.LLMJSONParseException):
        services.llm.generate_json([{"text": "Hello, world!"}], openai_client)
