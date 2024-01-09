import os
import logging
import subprocess
from typing import List

from schemas import IssueComment, Issue
from utils.logging_utils import log, exception_handler


DEFAULT_PATH = "downloads"


def exec_command_with_repo(
        repo: str,
        command: List[str],
        description: str,
) -> bool:
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
        log(f"Starting: {description}: {repo}", level="info")
        shorted_commands = " ".join(command)[:50]
        log(f"Executing command: {shorted_commands} in {repo_path}", level="info")
        res = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=repo_path,
        )
        if res.returncode != 0:
            log(f"Failed: {description}: {res.stderr.decode().strip()}", level="error")
            return False
        log(f"Successfully: {description}: {res.stdout.decode().strip()}", level="info")
        return True
    except Exception as e:
        log(f"Exception during {description}: {e}", level="error")
        return False


@exception_handler
def setup_repository(repo: str) -> bool:
    """リポジトリをセットアップする"""
    path = DEFAULT_PATH + "/" + repo
    # リポジトリが存在するか確認する
    if not os.path.exists(path):
        # リポジトリが存在しない場合はcloneする
        os.makedirs(
            path[:-len(repo) + repo.index("/")], exist_ok=True
        )
        return clone_repository(repo)
    else:
        # リポジトリが存在する場合はpullする
        return pull_repository(repo)


def clone_repository(repo: str) -> bool:
    """リポジトリをcloneする"""
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


@exception_handler
def list_issues(repo: str) -> List[Issue]:
    """issueを取得する"""

    try:
        log("Listing issues", level="info")
        res = subprocess.run(
            ["gh", "issue", "list"],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        log("Issues listed successfully", level="info")
    except Exception as e:
        log(f"Failed to list issues: {e}", level="error")
        return False

    issue_row = res.stdout.decode().split("\t")
    # 先頭の1個目のissue_idを取得
    issue_id = int(issue_row[0])
    return get_issue_by_id(issue_id)


@exception_handler
def get_issue_by_id(repo: str, issue_id: int) -> Issue:
    """idからissueを取得する"""

    try:
        log(f"Getting issue with id: {issue_id}", level="info")
        res = subprocess.run(
            ["gh", "issue", "view", str(issue_id)],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        log("Issue had successfully", level="info")
    except Exception as e:
        log(f"Failed to get issue: {e}", level="error")
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
        log(f"Getting comments with id: {issue_id}", level="info")
        res = subprocess.run(
            ["gh", "issue", "view", str(issue_id), "-c"],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        log("Comments had successfully", level="info")
    except Exception as e:
        log(f"Failed to get comments: {e}", level="error")
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
