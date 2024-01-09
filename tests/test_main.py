from main import parse_arguments


def test_parse_arguments_valid():
    args = ["add_issue", "--issue-id", "123"]
    parsed_args = parse_arguments(args)
    assert parsed_args.action == "add_issue"
    assert parsed_args.issue_id == 123


def test_parse_arguments_invalid_action():
    args = ["invalid_action"]
    try:
        parse_arguments(args)
        assert False
    except SystemExit:
        assert True
