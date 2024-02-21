"""Pytest configuration file."""
import pytest

import schemas


@pytest.fixture()
def setup():
    """Setup mock functions."""

    def inner(mocker):
        setup_github()(mocker)
        setup_llm()(mocker)

    return inner


def setup_github():
    """Setup mock functions."""

    def inner(mocker):
        mocker.patch("services.github.setup_repository", return_value=True)
        mocker.patch("services.github.create_issue", return_value=True)
        mocker.patch("services.github.commit", return_value=True)
        mocker.patch("services.github.push_repository", return_value=True)
        mocker.patch("services.github.get_issue_by_id",
                     return_value=schemas.Issue(id=1,
                                                title="test",
                                                body="test",
                                                comments=[]))
        mocker.patch("services.github.reply_issue", return_value=True)
        mocker.patch("services.github.checkout_new_branch", return_value=True)
        mocker.patch("services.github.checkout_branch", return_value=True)
        mocker.patch("services.github.delete_branch", return_value=True)

    return inner


def setup_llm():
    """Setup mock functions."""

    def inner(mocker):
        mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "test"})
        mocker.patch("services.llm.generate_text",
                     return_value="Hello, world!")

    return inner


@pytest.fixture()
def setup_llm_detail():
    """Setup mock functions."""

    # client = OpenAI()
    # response = client.chat.completions.create(model, messages)
    # response.choices[0].message.content
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
                self.content = "{\"type\": [{\"content\": \"test\"}]}"
            return self

        def __str__(self):
            """Mock __str__ function."""
            return self.content

    def inner(mocker):
        mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "test"})
        mocker.patch("openai.OpenAI", new=MockOpenAIObject)

    return inner
