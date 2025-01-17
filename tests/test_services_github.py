"""Test services.github module."""

import subprocess

import pytest

import services.github
import services.github.exceptions


def test_services_github_setup_repository_exist(mocker):
    """Test services.github.setup_repository."""
    mocker.patch(
        "services.github.os.path.exists",
        return_value=True,
    )
    mocker.patch(
        "services.github.subprocess.run",
        side_effect=[
            subprocess.CompletedProcess(
                args=["git", "branch", "--show-current"],
                returncode=0,
                stdout=b"test_branch",
            ),
            subprocess.CompletedProcess(
                args=["git", "symbolic-ref", "--short", "HEAD"],
                returncode=0,
                stdout=b"test_branch",
            ),
            True,
            True,
        ],
    )
    services.github.setup_repository("test/test")


def test_services_github_setup_repository_not_exist(mocker):
    """Test services.github.setup_repository."""
    mocker.patch(
        "services.github.os.path.exists",
        return_value=False,
    )
    mocker.patch(
        "services.github.subprocess.run",
        return_value=True,
    )
    services.github.setup_repository("test/test")


def test_services_github_setup_repository_clone_fail(mocker):
    """Test services.github.setup_repository."""
    mocker.patch(
        "services.github.os.path.exists",
        return_value=False,
    )
    mocker.patch(
        "services.github.subprocess.run",
        side_effect=subprocess.CalledProcessError(402, "test"),
    )
    with pytest.raises(services.github.exceptions.CommandExecutionException):
        services.github.setup_repository("test/test")


def test_services_github_create_issue(mocker):
    """Test services.github.create_issue."""
    mocker.patch(
        "services.github.os.path.exists",
        return_value=True,
    )
    mocker.patch(
        "services.github.subprocess.run",
        return_value=True,
    )
    services.github.create_issue("test/test", "test", "test")


def test_services_github_list_issue_ids_exec_command_success(mocker):
    """Test services.github.list_issue_ids."""

    def get_mock_object():
        """Return mock object."""
        mock_object = type("MockObject", (object, ), {})
        setattr(mock_object, "stdout",
                "101\ttest\n202\ttest\n303\ttest".encode("utf-8"))
        return mock_object

    mocker.patch(
        "services.github.subprocess.run",
        return_value=get_mock_object(),
    )
    issue_ids = services.github.list_issue_ids("test/test")
    assert issue_ids == [101, 202, 303]


def test_list_issue_ids_exec_command_failed(mocker):
    """Test services.github.list_issue_ids."""
    mocker.patch(
        "services.github.subprocess.run",
        return_value=None,
    )
    issue_ids = services.github.list_issue_ids("test/test")
    assert not issue_ids


def test_get_issue_by_id(mocker):
    """Test services.github.get_issue_by_id."""

    def get_mock_object():
        """Return mock object."""
        mock_object = type("MockObject", (object, ), {})
        setattr(mock_object, "stdout",
                "title:\ttest_title\n--\nhogehoge".encode("utf-8"))
        return mock_object

    def get_mock_object2():
        """Return mock object."""
        mock_object = type("MockObject", (object, ), {})
        setattr(
            mock_object,
            "stdout",
            ("author:\ttest\n"
             "association:\ttest\n"
             "edited:\ttest\n"
             "status:\ttest\n"
             "--\n"
             "body:\ttest_body\n"
             "--").encode("utf-8"),
        )
        return mock_object

    mocker.patch(
        "services.github.subprocess.run",
        side_effect=[
            get_mock_object(),
            get_mock_object2(),
        ],
    )
    issue = services.github.get_issue_by_id("test/test", 101)
    assert issue


def test_setup_repository_exist(mocker):
    """Test services.github.setup_repository."""
    mocker.patch(
        "os.path.exists",
        return_value=True,
    )
    mocker.patch(
        "services.github.subprocess.run",
        side_effect=[
            subprocess.CompletedProcess(
                args=["git", "branch", "--show-current"],
                returncode=0,
                stdout=b"test_branch",
            ),
            subprocess.CompletedProcess(
                args=["git", "symbolic-ref", "--short", "HEAD"],
                returncode=0,
                stdout=b"test_branch2",
            ),
            True,
            True,
            True,
        ],
    )
    services.github.setup_repository("test/test")
