import os
import logging
import subprocess
from typing import List

from schemas import IssueComment, Issue


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_PATH = "downloads"


def exec_command_with_repo(
        repo: str,
        command: List[str],
        description: str,
):
    """
    Execute a shell command within the specified git repository path.
    
    Args:
        repo (str): The GitHub repository to which the command is applied.
        command (List[str]): A list of strings representing the command and its arguments.
        description (str): A brief description of the command for logging purposes.
    
    Returns:
        bool: True if the command was successful, False otherwise.
    """
    repo_path = os.path.join(DEFAULT_PATH, repo)
    try:
        logger.info(f"Starting: {description}: {repo}")
        shorted_commands = " ".join(command)[:50]
        logger.info(f"Executing command: {shorted_commands} in {repo_path}")
        res = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=repo_path,
        )
        if res.returncode != 0:
            logger.error(f"Failed: {description}: {res.stderr.decode().strip()}")
            return False
        logger.info(f"Successfully: {description}: {res.stdout.decode().strip()}")
        return True
    except Exception as e:
        logger.error(f"Exception during {description}: {e}")
        return False


def setup_repository(repo: str, branch_name: str = "main") -> bool:
    """Set up the repository to point to a specific branch."""
    path = os.path.join(DEFAULT_PATH, repo)
    # リポジトリが存在するか確認する
    if not os.path.exists(path):
        # リポジトリが存在しない場合はcloneする
        os.makedirs(
            path[:-len(repo) + repo.index("/")], exist_ok=True
        )
        ret = clone_repository(repo)
    else:
        # リポジトリが存在する場合はpullする
        ret = pull_repository(repo)
    if ret:
        # リポジトリのブランチを指定する
        return checkout_branch(repo, branch_name)
    return False


def clone_repository(repo: str) -> bool:
    """Clone the repository."""
    return exec_command_with_repo(
        repo[:repo.index("/")],
        ["git", "clone", "git@github.com:" + repo],
        "Cloning repository",
    )


def pull_repository(repo: str) -> bool:
    """リポジトリをpullする"""
    return exec_command_with_repo(
        repo,
        ["git", "pull"],
        "Pulling repository",
    )
 

def create_issue(repo: str, title: str, body: str) -> None:
    """Create a new issue on GitHub."""
    return exec_command_with_repo(
        repo,
        ["gh", "issue", "create", "-t", title, "-b", body],
        f"Creating issue with title: {title}",
    )


def list_issue_ids(repo: str) -> List[int]:
    """issue idを取得する"""

    res = exec_command_with_repo(
        repo,
        ["gh", "issue", "list"],
        "Listing issues",
    )
    issue_row = res.stdout.decode().split("\t")
    return list(map(int, issue_row))


def get_issue_by_id(repo: str, issue_id: int) -> Issue:
    """idからissueを取得する"""

    try:
        logger.info(f"Getting issue with id: {issue_id}")
        res = subprocess.run(
            ["gh", "issue", "view", str(issue_id)],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info("Issue had successfully")
    except Exception as e:
        logger.error(f"Failed to get issue: {e}")
        return None

    is_body = False
    body = ""
    for line in res.stdout.decode().splitlines():
        if is_body:
            body += line + "\n"
        elif line.startswith("title:\t"):
            title = line[len("title:\t"):]
        elif line.startswith("--"):
            is_body = True

    issue = Issue(
        id=issue_id,
        title=title,
        body=body,
    )

    try:
        logger.info(f"Getting comments with id: {issue_id}")
        res = subprocess.run(
            ["gh", "issue", "view", str(issue_id), "-c"],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info("Comments had successfully")
    except Exception as e:
        logger.error(f"Failed to get comments: {e}")
        return None

    comment_attrs = [
        "author", "association", "edited", "status",
    ]

    is_body = False
    body = ""
    comment = {}
    for line in res.stdout.decode().splitlines():
        if is_body and line.startswith("--"):
            issue.comments.append(IssueComment(**comment, body=body))
            comment = {}
            body = ""
            is_body = False
        elif is_body:
            body += line + "\n"
        elif line.startswith("--"):
            is_body = True
        else:
            for attr in comment_attrs:
                if line.startswith(attr + ":\t"):
                    comment[attr] = line[len(attr + ":\t"):].strip()

    return issue


def reply_issue(repo: str, issue_id: int, body: str) -> None:
    """issueに返信する"""
    return exec_command_with_repo(
        repo,
        ["gh", "issue", "comment", str(issue_id), "-b", body],
        f"Replying issue with id: {issue_id}",
    )


def checkout_branch(repo: str, branch_name: str) -> bool:
    """ブランチをチェックアウトする"""
    return exec_command_with_repo(
        repo,
        ["git", "checkout", branch_name],
        f"Checking out to branch: {branch_name}",
    )


def checkout_new_branch(repo: str, branch_name: str) -> bool:
    """新しいブランチを作成する"""
    return exec_command_with_repo(
        repo,
        ["git", "checkout", "-b", branch_name],
        f"Creating new branch: {branch_name}",
    )


def commit(repo: str, message: str) -> bool:
    """コミットする"""
    return exec_command_with_repo(
        repo,
        ["git", "commit", "-a", "-m", message],
        f"Committing changes: {message}",
    )


def push_repository(repo: str, branch_name: str) -> bool:
    """リポジトリをpushする"""
    return exec_command_with_repo(
        repo,
        ["git", "push", "origin", branch_name],
        f"Pushing repository: {repo}",
    )
