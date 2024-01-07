from unittest.mock import patch
from services.github import add_issue

@patch('services.github.create_issue')
def test_add_issue(mock_create_issue):
    mock_create_issue.return_value = True  # Mock successful issue creation
    result = add_issue('test_owner/test_repo')
    assert result is True
    mock_create_issue.assert_called_once()
