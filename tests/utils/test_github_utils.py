"""Test cases for Git utility functions"""

import subprocess

import pytest

from utils.github_utils import exec_git_command_and_response_bool, exists_repo, make_owner_dir


def test_exec_git_command_success(mocker):
    """Test the exec_git_command_and_response_bool function with a successful Git command"""
    mock_run = mocker.patch("subprocess.run",
                            return_value=mocker.Mock(returncode=0))
    assert exec_git_command_and_response_bool('test_repo',
                                              ['git', 'status']) is True
    mock_run.assert_called_once()


def test_exec_git_command_failure(mocker):
    """Test the exec_git_command_and_response_bool function with a failed Git command"""
    mocker.patch("subprocess.run",
                 side_effect=subprocess.CalledProcessError(1, 'git'))
    with pytest.raises(Exception):
        exec_git_command_and_response_bool('test_repo', ['git', 'status'])


def test_exists_repo_true(mocker):
    """Test the exists_repo function with a true result"""
    mocker.patch("os.path.exists", return_value=True)
    assert exists_repo("base_path", "owner/repo") is True


def test_exists_repo_false(mocker):
    """Test the exists_repo function with a false result"""
    mocker.patch("os.path.exists", return_value=False)
    assert exists_repo("base_path", "owner/repo") is False


def test_make_owner_dir_success(mocker):
    """Test the make_owner_dir function with a successful directory creation"""
    mock_makedirs = mocker.patch("os.makedirs")
    make_owner_dir("base_path", "owner/repo")
    mock_makedirs.assert_called_once_with("base_path/owner", exist_ok=True)
