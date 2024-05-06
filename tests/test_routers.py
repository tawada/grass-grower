"""Test routers.py module."""
from datetime import datetime, timedelta

import routers


def test_add_issue(
    mocker,
    setup,
):
    """Test add_issue() function."""
    setup(mocker)
    mocker.patch("builtins.open", mocker.mock_open(read_data="test"))
    mocker.patch(
        "logic.logic_utils.os.walk",
        return_value=[
            ("test_dir", ["test_dir2"], ["test_file.py"]),
            ("test_dir/test_dir2", [], ["test_file2.py"]),
        ],
    )
    routers.add_issue("test_owner/test_repo", "python")


def test_update_issue(
    mocker,
    setup,
):
    """Test update_issue() function."""
    setup(mocker)

    mocker.patch("builtins.open", mocker.mock_open(read_data="test"))
    routers.update_issue(1, "test_owner/test_repo", "main", "python")


def test_generate_code_from_issue(mocker, setup):
    """Test generate_code_from_issue() function."""
    setup(mocker)
    mocker.patch("builtins.open", mocker.mock_open(read_data="test"))
    routers.generate_code_from_issue(1, "test_owner/test_repo", "main",
                                     "python")


def test_summarize_issue(mocker, setup):
    """Test summarize_issue() function."""
    setup(mocker)
    routers.summarize_issue(1, "test_owner/test_repo", "main")


def test_generate_readme(mocker, setup):
    """Test generate_readme() function."""
    setup(mocker)
    mocker.patch("builtins.open", mocker.mock_open(read_data="test"))
    routers.generate_readme("test_owner/test_repo", "main", "python")


def test_generate_readme_failed(mocker, setup):
    """Test generate_readme() function."""
    setup(mocker)
    mocker.patch("builtins.open", mocker.mock_open(read_data="test"))
    routers.generate_readme("test_owner/test_repo", "main", "python")


def test_grow_grass_now(mocker, setup):
    """Test grow_grass() function."""
    setup(mocker)
    mocker.patch("services.github.get_datetime_of_last_commit",
                 return_value=datetime.now())
    routers.grow_grass("test_owner/test_repo", "main", "python")


def test_grow_grass_yesterday(mocker, setup):
    """Test grow_grass() function."""
    setup(mocker)
    mocker.patch(
        "services.github.get_datetime_of_last_commit",
        return_value=datetime.now() - timedelta(days=1),
    )
    mocker.patch("builtins.open", mocker.mock_open(read_data="test"))
    mocker.patch(
        "services.llm.generate_json",
        return_value={
            "file_path": "test_file_path",
            "before_code": "test",
            "after_code": "test_after_code",
        },
    )
    mocker.patch("services.github.list_issue_ids", return_value=[1])
    routers.grow_grass("test_owner/test_repo", "main", "python")


def test_generate_code_from_issue_and_reply(mocker, setup):
    """Test generate_code_from_issue_and_reply() function."""
    setup(mocker)
    mocker.patch("builtins.open", mocker.mock_open(read_data="test"))
    mocker.patch(
        "services.llm.generate_json",
        return_value={
            "file_path": "test_file_path",
            "before_code": "test",
            "after_code": "test_after_code",
        },
    )

    routers.generate_code_from_issue_and_reply(1, "test_owner/test_repo",
                                               "main", "python")
