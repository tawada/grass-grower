"""Tool to automate issue handling on GitHub"""
import sys
from argparse import ArgumentParser

import routers
from utils.logging_utils import log, setup_logging


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

    # Establish a dictionary that maps actions to whether they need an issue_id
    actions_needing_issue_id = {
        "generate_code_from_issue": True,
        "update_issue": True,
        "add_issue": False,
        "generate_readme": False,
        "grow_grass": False,
    }

    if actions_needing_issue_id[
            parsed_args.action] and not parsed_args.issue_id:
        print("'issue_id' is required for the selected action.")
        sys.exit(2)
    return parsed_args


def main():
    """Main function"""
    try:
        args = parse_arguments()
    except SystemExit as err:
        log(f"Argument parsing error: {err}", level="error")
        sys.exit(1)

    if args.action == "generate_code_from_issue":
        routers.generate_code_from_issue(args.issue_id, args.repo, args.branch)
    elif args.action == "update_issue":
        routers.update_issue(args.issue_id, args.repo, args.branch)
    elif args.action == "add_issue":
        routers.add_issue(args.repo, args.branch)
    elif args.action == "generate_readme":
        routers.generate_readme(args.repo, args.branch)
    elif args.action == "grow_grass":
        routers.grow_grass(args.repo, args.branch)
    else:
        log("Invalid action.", level="error")
        sys.exit(1)


if __name__ == "__main__":
    setup_logging()
    main()
