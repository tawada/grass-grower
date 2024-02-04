"""Tool to automate issue handling on GitHub"""
import sys
from argparse import ArgumentParser

import routers
from utils.logging_utils import log, setup_logging

# Establish a dictionary that maps actions to whether they need an issue_id
actions_needing_issue_id = {
    "generate_code_from_issue": True,
    "update_issue": True,
    "add_issue": False,
    "generate_readme": False,
    "grow_grass": False,
}


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
            "generate_readme",
            "grow_grass",
            "update_issue",
        ],
    )
    parser.add_argument("--issue-id", type=int, help="ID of the GitHub issue")
    parser.add_argument(
        "--repo",
        help="Target GitHub repository in the format 'owner/repo'",
        default="tawada/grass-grower",
    )
    parser.add_argument("--branch", help="Target branch name", default="main")
    parsed_args = parser.parse_args(args)

    # Check to parse repository
    if len(parsed_args.repo.split("/")) != 2:
        print("Invalid repository format. Use 'owner/repo'.")
        sys.exit(2)

    if actions_needing_issue_id[
            parsed_args.action] and not parsed_args.issue_id:
        print("'issue_id' is required for the selected action.")
        sys.exit(2)
    return parsed_args


def main(args=None):
    """Main function"""
    try:
        args = parse_arguments(args)
    except SystemExit as err:
        log(f"Argument parsing error: {err}", level="error")
        sys.exit(1)

    try:
        _args = [args.repo, args.branch]
        if actions_needing_issue_id[args.action]:
            _args.insert(0, args.issue_id)
        getattr(routers, args.action)(*_args)
    except AttributeError as err:
        log(f"Action not implemented: {err}", level="error")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main(None)
