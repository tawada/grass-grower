import os
import logging
import subprocess

from schemas import Issue


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

DEFAULT_PATH = "downloads"


def setup_repository(repo: str) -> bool:
    """リポジトリをセットアップする"""
    path = DEFAULT_PATH + "/" + repo
    # リポジトリが存在するか確認する
    if not os.path.exists(path):
        # リポジトリが存在しない場合はcloneする
        return clone_repository(repo)
    else:
        # リポジトリが存在する場合はpullする
        return pull_repository(repo)


def clone_repository(repo: str) -> bool:
    """リポジトリをcloneする"""
    try:
        logger.info(f"Cloning repository: {repo}")
        res = subprocess.run(
            ["gh", "repo", "clone", repo, DEFAULT_PATH + "/" + repo],
            stdout=subprocess.PIPE,
        )
        logger.info(f"Repository cloned successfully: {res.stdout.decode().strip()}")
        return True
    except Exception as e:
        logger.error(f"Failed to clone repository: {e}")
        return False


def pull_repository(repo: str) -> bool:
    """リポジトリをpullする"""
    try:
        logger.info(f"Pulling repository: {repo}")
        res = subprocess.run(
            ["git", "pull"],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info(f"Repository pulled successfully: {res.stdout.decode().strip()}")
        return True
    except Exception as e:
        logger.error(f"Failed to pull repository: {e}")
        return False


def create_issue(repo: str, title: str, body: str) -> None:
    """Create a new issue on GitHub."""
    try:
        logger.info(f"Creating issue with title: {title}")
        res = subprocess.run(
            ["gh", "issue", "create", "-t", title, "-b", body],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info(f"Issue created successfully: {res.stdout}")
    except Exception as e:
        logger.error(f"Failed to create issue: {e}")
        return None


def get_issue(repo: str) -> Issue:
    """issueを取得する"""

    try:
        logger.info("Listing issues")
        res = subprocess.run(
            ["gh", "issue", "list"],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info("Issue listed successfully")
    except Exception as e:
        logger.error(f"Failed to list issues: {e}")
        return None

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

    try:
        logger.info(f"Replying issue with id: {issue_id}")
        res = subprocess.run(
            ["gh", "issue", "comment", str(issue_id), "-b", body],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info(f"Issue commented successfully: {res.stdout.decode().strip()}")
    except Exception as e:
        logger.error(f"Failed to get issue: {e}")
        return None


def checkout_branch(repo: str, branch_name: str) -> bool:
    """ブランチをチェックアウトする"""

    try:
        logger.info(f"Checking out to branch: {branch_name}")
        res = subprocess.run(
            ["git", "checkout", branch_name],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info(f"Branch checked out successfully: {res.stdout.decode().strip()}")
        return True
    except Exception as e:
        logger.error(f"Failed to checkout branch: {e}")
        return False


def checkout_new_branch(repo: str, branch_name: str) -> bool:
    """新しいブランチを作成する"""

    try:
        logger.info(f"Creating new branch: {branch_name}")
        res = subprocess.run(
            ["git", "checkout", "-b", branch_name],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info(f"New branch created successfully: {res.stdout.decode().strip()}")
        return True
    except Exception as e:
        logger.error(f"Failed to create new branch: {e}")
        return False


def commit(repo: str, message: str) -> bool:
    """コミットする"""

    try:
        logger.info(f"Committing changes: {message}")
        res = subprocess.run(
            ["git", "commit", "-a", "-m", message],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info(f"Changes committed successfully: {res.stdout.decode().strip()}")
        return True
    except Exception as e:
        logger.error(f"Failed to commit changes: {e}")
        return False


def push_repository(repo: str, branch_name: str) -> bool:
    """リポジトリをpushする"""

    try:
        logger.info(f"Pushing repository: {repo}")
        res = subprocess.run(
            ["git", "push", "origin", branch_name],
            stdout=subprocess.PIPE,
            cwd=DEFAULT_PATH + "/" + repo,
        )
        logger.info(f"Repository pushed successfully: {res.stdout.decode().strip()}")
        return True
    except Exception as e:
        logger.error(f"Failed to push repository: {e}")
        return False
