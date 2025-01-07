"""Test main.py"""
import pytest

import main
from main import MissingIssueIDError


def test_parse_arguments_valid():
    """Test parse_arguments() with valid arguments"""
    args = ["add_issue", "--issue-id", "123"]
    parsed_args = main.parse_arguments(args)
    assert parsed_args.action == "add_issue"
    assert parsed_args.issue_id == 123


def test_parse_arguments_invalid_action():
    """Test parse_arguments() with invalid action"""
    args = ["invalid_action"]
    with pytest.raises(SystemExit):
        main.parse_arguments(args)


def test_parse_arguments_invalid_issue_id():
    """Test parse_arguments() with invalid issue_id"""
    args = ["update_issue"]
    with pytest.raises(MissingIssueIDError):
        main.parse_arguments(args)


def test_parse_arguments_invalid_repository():
    """Test parse_arguments() with invalid repository"""
    args = ["add_issue", "--repo", "unparsable_repository"]
    with pytest.raises(SystemExit):
        main.parse_arguments(args)


def test_main_add_issue(mocker, setup):
    """Test main() with action 'add_issue'"""
    setup(mocker)
    args = ["add_issue", "--issue-id", "123"]
    main.main(args)


def test_main_update_issue_fail_without_issue_id(mocker, setup):
    """Test main() with action 'update_issue'"""
    setup(mocker)
    args = ["update_issue"]
    with pytest.raises(SystemExit):
        main.main(args)


def test_main_update_issue_fail_invalid_issue_id(mocker, setup):
    """Test main() with action 'update_issue'"""
    setup(mocker)
    args = ["update_issue", "--issue-id", "invalid_issue_id"]
    with pytest.raises(SystemExit):
        main.main(args)


def test_main_unexpected_error(mocker):
    """Test main() with unexpected error"""
    mocker.patch("main.parse_arguments",
                 side_effect=Exception("Unexpected error"))
    with pytest.raises(SystemExit):
        main.main([])


def test_main_invalid_action(mocker):
    """Test main() with invalid action"""
    with pytest.raises(SystemExit):
        main.main(["invalid_action"])


def test_main_unrecognized_argument(mocker):
    """Test main() with unrecognized argument"""
    with pytest.raises(SystemExit):
        main.main(["add_issue", "--invalid-arg"])
