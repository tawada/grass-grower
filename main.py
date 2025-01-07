"""Tool to automate issue handling on GitHub"""
import os
import re
import sys
from argparse import ArgumentParser, ArgumentTypeError

from routers import (add_issue, generate_code_from_issue,
                     generate_code_from_issue_and_reply, generate_readme,
                     grow_grass, update_issue)
from utils.logging_utils import log, setup_logging

# Establish a dictionary that maps actions to whether they need an issue_id
actions_needing_issue_id = {
    "generate_code_from_issue": True,
    "generate_code_from_issue_and_reply": True,
    "update_issue": True,
    "add_issue": False,
    "generate_readme": False,
    "grow_grass": False,
}

action_functions = {
    "add_issue": add_issue,
    "generate_code_from_issue": generate_code_from_issue,
    "generate_code_from_issue_and_reply": generate_code_from_issue_and_reply,
    "generate_readme": generate_readme,
    "grow_grass": grow_grass,
    "update_issue": update_issue,
}


class MissingIssueIDError(Exception):
    """Raised when the issue_id is missing"""


def parse_git_repo(value: str) -> str:
    """Parse the repository argument"""
    # Username and repository regex (simplified)
    valid_pattern = r"^[a-zA-Z0-9-]+/(?!.*\.\.)(?!.*\.$)(?!^\.)[a-zA-Z0-9_.-]{1,100}$"
    if not re.match(valid_pattern, value):
        raise ArgumentTypeError("Invalid repository format. Use 'owner/repo'.")
    return value


def parse_arguments(args=None):
    """Parse command line arguments"""
    parser = ArgumentParser(
        description="Tool to automate issue handling on GitHub")
    parser.add_argument(
        "action",
        help="Action to perform",
        choices=[
            "add_issue",
            "generate_code_from_issue",
            "generate_code_from_issue_and_reply",
            "generate_readme",
            "grow_grass",
            "update_issue",
        ],
    )
    parser.add_argument("--issue-id", type=int, help="ID of the GitHub issue")
    parser.add_argument(
        "--repo",
        help="Target GitHub repository in the format 'owner/repo'",
        default=os.getenv("DEFAULT_REPO", "tawada/grass-grower"),
        type=parse_git_repo,
    )
    parser.add_argument("--branch", help="Target branch name", default="main")
    parser.add_argument("--code-lang",
                        help="Target code language",
                        default="python")
    parsed_args = parser.parse_args(args)

    if actions_needing_issue_id[
            parsed_args.action] and not parsed_args.issue_id:
        raise MissingIssueIDError(
            "'issue_id' is required for the selected action.")

    return parsed_args


def main(args=None):
    """Main function"""
    # Set up logging
    setup_logging()

    try:
        args = parse_arguments(args)
    except MissingIssueIDError as err:
        log(f"'issue_id' is required for the selected action: {str(err)}",
            level="error")
        sys.exit(1)
    except ArgumentTypeError as err:
        log(f"Argument error: {str(err)}", level="error")
        sys.exit(1)
    except SystemExit as err:
        error_msg = str(err)
        if 'invalid choice' in error_msg:
            log(f"無効なアクションが指定されました: {error_msg}", level="error")
        elif 'unrecognized arguments' in error_msg:
            log(f"認識できない引数が指定されました: {error_msg}", level="error")
        else:
            log(f"引数解析エラー: {error_msg}", level="error")
        sys.exit(1)
    except Exception as err:
        log(f"引数解析中に予期せぬエラーが発生しました: {err}", level="error")
        sys.exit(1)

    try:
        _args = [args.repo, args.branch, args.code_lang]
        if actions_needing_issue_id[args.action]:
            _args.insert(0, args.issue_id)
        action_functions[args.action](*_args)
    except AttributeError as err:
        log(f"アクションが実装されていません: {err}", level="error")
        sys.exit(1)
    except Exception as err:
        log(f"アクション実行中に予期せぬエラーが発生しました: {err}", level="error")
        sys.exit(1)


if __name__ == "__main__":
    main(None)
