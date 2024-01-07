import os
import logging
import subprocess
from typing import List

from schemas import Issue


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_PATH = "downloads"


def exec_command_with_repo(
        repo: str,
        command: List[str],
        description: str,
):
    """リポジトリを指定してコマンドを実行する"""
    repo_path = DEFAULT_PATH + "/" + repo
    try:
        logger.info(f"Starting: {description}: {repo}")
        res = subprocess.run(
            command,
            stdout=subprocess.PIPE,
            cwd=repo_path,
        )
        if res.returncode != 0:
            logger.error(f"Failed: {description}: {res.stdout.decode().strip()}")
            return False
        logger.info(f"Successfully: {description}: {res.stdout.decode().strip()}")
        return True
    except Exception as e:
        logger.error(f"Failed: {description}: {e}")
        return False




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


def list_issues(repo: str) -> List[Issue]:
    """issueを取得する"""

    res = exec_command_with_repo(
        repo,
        ["gh", "issue", "list"],
        "Listing issues",
    )
    issue_row = res.stdout.decode().split("\t")
    # 先頭の1個目のissue_idを取得
    issue_id = int(issue_row[0])
    return get_issue_by_id(issue_id)


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

    return Issue(
        id=issue_id,
        title=title,
        body=body,
    )


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
