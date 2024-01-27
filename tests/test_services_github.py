"""Test services.github module."""
import subprocess

import services.github


def test_services_github_setup_repository_exist(mocker):
    """Test services.github.setup_repository."""
    mocker.patch(
        "services.github.os.path.exists",
        return_value=True,
    )
    mocker.patch(
        "services.github.subprocess.run",
        return_value=True,
    )
    services.github.setup_repository("test/test")
    assert True


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
    assert True


def test_services_github_setup_repository_clone_fail(mocker):
    """Test services.github.setup_repository."""
    mocker.patch(
        "services.github.os.path.exists",
        return_value=False,
    )
    mocker.patch(
        "services.github.subprocess.run",
        return_value=subprocess.CalledProcessError,
    )
    services.github.setup_repository("test/test")
    assert True


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
    assert True


def test_services_github_list_issue_ids_exec_command_success(mocker):
    """Test services.github.list_issue_ids."""

    def get_mock_object():
        """Return mock object."""
        mock_object = type("MockObject", (object, ), {})
        setattr(mock_object, "stdout", "101\t202\t303".encode("utf-8"))
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
