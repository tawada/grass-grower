from unittest.mock import MagicMock

import pytest

import services.github
import services.llm
from routers.code_generator import generate_code_from_issue, generate_readme
from utils.config_loader import get_default_config


def test_generate_code_from_issue(mocker):
    """Test generate_code_from_issue function."""
    # setupフィクスチャを使用せず、必要なモックを直接設定
    issue_id = 1
    repo = "test_owner/test_repo"
    branch = "main"
    code_lang = "python"

    mock_issue = MagicMock()
    mock_issue.id = issue_id

    # OpenAIクライアントのモックを設定
    class MockOpenAIObject:

        def __init__(self):
            self.chat = self
            self.completions = self
            self.choices = [self]
            self.message = self
            self.content = "生成されたコード"

        def create(self, model, messages, response_format={"type": "text"}):
            return self

    mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "test"})
    mocker.patch("services.llm.openai", new=MockOpenAIObject())

    mock_setup = mocker.patch("services.github.setup_repository")
    mock_get_issue = mocker.patch("services.github.get_issue_by_id",
                                  return_value=mock_issue)
    mock_generate_messages = mocker.patch("logic.generate_messages_from_files",
                                          return_value=[])
    mock_generate_messages_issue = mocker.patch(
        "logic.generate_messages_from_issue", return_value=[])

    generated_code = generate_code_from_issue(issue_id, repo, branch,
                                              code_lang)

    mock_setup.assert_called_once_with(repo, branch)
    mock_get_issue.assert_called_once_with(repo, issue_id)
    assert generated_code == "生成されたコード"


def test_generate_readme_success(mocker):
    """Test generate_readme function success case."""
    repo = "test_owner/test_repo"
    branch = "main"
    code_lang = "python"

    # OpenAIクライアントのモックを設定
    class MockOpenAIObject:

        def __init__(self):
            self.chat = self
            self.completions = self
            self.choices = [self]
            self.message = self
            self.content = "生成されたREADME"

        def create(self, model, messages, response_format={"type": "text"}):
            return self

    mocker.patch.dict("os.environ", {"OPENAI_API_KEY": "test"})
    mocker.patch("services.llm.openai", new=MockOpenAIObject())

    # その他のモックを設定
    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("logic.logic_utils.get_file_content",
                 return_value="現在のREADME")
    mocker.patch("logic.logic_utils.write_to_file")
    mock_setup = mocker.patch("services.github.setup_repository")
    mock_checkout_new = mocker.patch("services.github.checkout_new_branch")
    mock_commit = mocker.patch("services.github.commit")
    mock_push = mocker.patch("services.github.push_repository")
    mock_checkout = mocker.patch("services.github.checkout_branch")

    # デフォルトのconfig pathを使用
    mocker.patch("config.config", get_default_config())

    result = generate_readme(repo, branch, code_lang)

    mock_setup.assert_called_once_with(repo, branch)
    mock_checkout_new.assert_called_once_with(repo, "update-readme")
    mock_commit.assert_called_once_with(repo, "Update README.md")
    mock_push.assert_called_once_with(repo, "update-readme")
    mock_checkout.assert_called_once_with(repo, "main")
    assert result is True


def test_generate_readme_file_not_found(mocker):
    """Test generate_readme function with FileNotFoundError."""
    repo = "test_owner/test_repo"

    mocker.patch("os.path.exists", return_value=True)
    mocker.patch("logic.logic_utils.get_file_content",
                 side_effect=FileNotFoundError)
    mocker.patch("config.config", get_default_config())

    with pytest.raises(FileNotFoundError):
        generate_readme(repo)
