"""Tool to automate issue handling on GitHub"""
import sys
from argparse import ArgumentParser

import routers
from utils.logging_utils import log, setup_logging

setup_logging()


def parse_arguments(args=None):
    """Parse command line arguments"""
    parser = ArgumentParser(
        description="Tool to automate issue handling on GitHub")
    parser.add_argument("action",
                        help="Action to perform",
                        choices=[
                            "add_issue", "generate_code_from_issue",
                            "generate_readme", "grow_grass", "update_issue"
                        ])
    parser.add_argument("--issue-id", type=int, help="ID of the GitHub issue")
    parser.add_argument(
        "--repo",
        help="Target GitHub repository in the format 'owner/repo'",
        default="tawada/grass-grower")
    parser.add_argument("--branch", help="Target branch name", default="main")
    return parser.parse_args(args)


if __name__ == "__main__":
    try:
        args = parse_arguments()
    except SystemExit as e:
        log(f"Error: {e}", level="error")
        sys.exit(e.code)

    # Parse repository
    try:
        owner, repo_ = args.repo.split('/')
        repo = f"{owner}/{repo_}"
    except ValueError:
        log("Invalid repository format. Use 'owner/repo'.", level="error")
        sys.exit(1)

    # Parse branch
    branch = args.branch

    if args.action == "generate_code_from_issue" and args.issue_id:
        routers.generate_code_from_issue(args.issue_id, repo, branch)
    elif args.action == "update_issue" and args.issue_id:
        routers.update_issue(args.issue_id, repo, branch)
    elif args.action == "add_issue":
        routers.add_issue(repo, branch)
    elif args.action == "generate_readme":
        routers.generate_readme(repo, branch)
    elif args.action == "grow_grass":
        routers.grow_grass(repo, branch)
    else:
        log("Invalid action.", level="error")
        sys.exit(1)
