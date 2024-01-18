import pytest


@pytest.fixture()
def setup():

    def inner(mocker):
        setup_github()(mocker)
        setup_llm()(mocker)
        setup_routers()(mocker)

    return inner


def setup_github():

    def inner(mocker):
        mocker.patch('services.github.setup_repository', return_value=True)
        mocker.patch('services.github.create_issue', return_value=True)

    return inner


def setup_llm():

    def inner(mocker):
        mocker.patch("services.llm.generate_text",
                     return_value="Hello, world!")

    return inner


def setup_routers():

    def inner(mocker):
        mocker.patch("routers.enumerate_python_files",
                     return_value=[{
                         "filename": "test.py",
                         "content": "print('Hello, world!')"
                     }])

    return inner
