from argparse import ArgumentParser
import logging
import sys
from routers import (
    add_issue,
    generate_code_from_issue,
    generate_readme,
    update_issue,
)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("debug.log"),  # Log to a file
        logging.StreamHandler()            # Log to standard output
    ]
)

if __name__ == "__main__":
    parser = ArgumentParser(description="Tool to automate issue handling on GitHub")
    parser.add_argument("action", help="Action to perform", choices=[
        "add_issue", "generate_code_from_issue", "generate_readme", "update_issue"
    ])
    parser.add_argument("--issue-id", type=int, help="ID of the GitHub issue")
    parser.add_argument("--repo", help="Target GitHub repository in the format 'owner/repo'", default="tawada/grass-grower")
    parser.add_argument("--branch", help="Target branch name", default="main")

    args = parser.parse_args()

    # Parse repository
    try:
        owner, repo_ = args.repo.split('/')
        repo = f"{owner}/{repo_}"
    except ValueError:
        logging.error("Invalid repository format. Use 'owner/repo'.")
        sys.exit(1)

    # Parse branch
    branch = args.branch

    if args.action == "generate_code_from_issue" and args.issue_id:
        generate_code_from_issue(args.issue_id, repo, branch)
    elif args.action == "update_issue" and args.issue_id:
        update_issue(args.issue_id, repo, branch)
    elif args.action == "add_issue":
        add_issue(repo, branch)
    elif args.action == "generate_readme":
        generate_readme(repo, branch)
    else:
        logging.error("Invalid action.")
        sys.exit(1)
