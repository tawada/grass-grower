"""Test main.py"""

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
    try:
        main.parse_arguments(args)
        assert False
    except SystemExit:
        assert True


def test_parse_arguments_invalid_issue_id():
    """Test parse_arguments() with invalid issue_id"""
    args = ["update_issue"]
    try:
        main.parse_arguments(args)
        assert False
    except MissingIssueIDError:
        assert True


def test_parse_arguments_invalid_repository():
    """Test parse_arguments() with invalid repository"""
    args = ["add_issue", "--repo", "unparsable_repository"]
    try:
        main.parse_arguments(args)
        assert False
    except SystemExit:
        assert True


def test_main_add_issue(mocker, setup):
    """Test main() with action 'add_issue'"""
    setup(mocker)
    args = ["add_issue", "--issue-id", "123"]
    main.main(args)


def test_main_update_issue_fail_without_issue_id(mocker, setup):
    """Test main() with action 'update_issue'"""
    setup(mocker)
    args = ["update_issue"]
    try:
        main.main(args)
        assert False
    except SystemExit:
        assert True


def test_main_update_issue_fail_invalid_issue_id(mocker, setup):
    """Test main() with action 'update_issue'"""
    setup(mocker)
    args = ["update_issue", "--issue-id", "invalid_issue_id"]
    try:
        main.main(args)
        assert False
    except SystemExit:
        assert True
