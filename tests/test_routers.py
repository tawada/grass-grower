from unittest.mock import patch
from routers import add_issue


@patch('routers.enumerate_python_files')
@patch('services.llm.generate_text')
@patch('services.github.setup_repository')
@patch('services.github.create_issue')
def test_add_issue(
    mock_create_issue,
    mock_setup_repository,
    mock_generate_text,
    mock_enumerate_python_files,
):
    """Test add_issue() function."""
    mock_enumerate_python_files.return_value = [{
        "filename":
        "test.py",
        "content":
        "print('Hello, world!')"
    }]
    mock_generate_text.return_value = "Hello, world!"
    mock_setup_repository.return_value = True
    mock_create_issue.return_value = True
    add_issue('test_owner/test_repo')
    assert True
