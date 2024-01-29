"""Pytest configuration file."""
import pytest

import schemas


@pytest.fixture()
def setup():
    """Setup mock functions."""

    def inner(mocker):
        setup_github()(mocker)
        setup_llm()(mocker)
        setup_routers()(mocker)

    return inner


def setup_github():
    """Setup mock functions."""

    def inner(mocker):
        mocker.patch("services.github.setup_repository", return_value=True)
        mocker.patch("services.github.create_issue", return_value=True)
        mocker.patch("services.github.get_issue_by_id",
                     return_value=schemas.Issue(id=1,
                                                title="test",
                                                body="test",
                                                comments=[]))
        mocker.patch("services.github.reply_issue", return_value=True)

    return inner


def setup_llm():
    """Setup mock functions."""

    def inner(mocker):
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

        def __init__(self):
            self.chat = MockOpenAIObject()
            self.completions = MockOpenAIObject()
            self.choices = [MockOpenAIObject()]
            self.message = MockOpenAIObject()
            self.content = "Hello, world!"
            self.model = None
            self.messages = None

        def create(self, model, messages):
            """Mock create function."""
            self.model = model
            self.messages = messages
            return MockOpenAIObject()

        def __str__(self):
            """Mock __str__ function."""
            return self.content

    def inner(mocker):
        mocker.patch("openai.OpenAI", new=MockOpenAIObject)

    return inner


def setup_routers():
    """Setup mock functions."""

    def inner(mocker):
        mocker.patch(
            "routers.enumerate_python_files",
            return_value=[{
                "filename": "test.py",
                "content": "print('Hello, world!')"
            }],
        )

    return inner
