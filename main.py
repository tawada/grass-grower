from argparse import ArgumentParser
import logging
import sys
from routers import (
    add_issue,
    generate_code_from_issue,
    generate_readme,
    update_issue,
)
from utils.logging_utils import (
    setup_logging,
    log,
)


setup_logging()


def parse_arguments(args=None):
    parser = ArgumentParser(description="Tool to automate issue handling on GitHub")
    parser.add_argument("action", help="Action to perform", choices=[
        "add_issue", "generate_code_from_issue", "generate_readme", "update_issue"
    ])
    parser.add_argument("--issue-id", type=int, help="ID of the GitHub issue")
    parser.add_argument("--repo", help="Target GitHub repository in the format 'owner/repo'", default="tawada/grass-grower")
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
        logging.error("Invalid repository format. Use 'owner/repo'.")
        sys.exit(1)

    if args.action == "generate_code_from_issue" and args.issue_id:
        generate_code_from_issue(repo, args.issue_id)
    elif args.action == "update_issue" and args.issue_id:
        update_issue(repo, args.issue_id)
    elif args.action == "add_issue":
        add_issue(repo)
    elif args.action == "generate_readme":
        generate_readme(repo)
    else:
        logging.error("Invalid action.")
        sys.exit(1)
