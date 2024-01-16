"""GitHub API service."""
import os
import subprocess
from datetime import datetime
from typing import Dict, List, Union

from schemas import Issue, IssueComment
from utils.logging_utils import exception_handler, log

DEFAULT_PATH = "downloads"


def exec_command(
        repo: str,
        command: List[str],
        capture_output: bool = False
) -> Union[None, subprocess.CompletedProcess]:
    """
    Execute a shell command within the specified git repository path.
    If capture_output is True, the function returns a subprocess.CompletedProcess object.
    Otherwise, it returns a boolean indicating success.

    Returns:
        Union[bool, subprocess.CompletedProcess]: The result of the subprocess run or success flag.
    """
    repo_path = os.path.join(DEFAULT_PATH, repo)
    try:
        complete_process = subprocess.run(
            command,
            stdout=subprocess.PIPE if capture_output else None,
            stderr=subprocess.PIPE if capture_output else None,
            cwd=repo_path,
            check=True,
        )
        return complete_process
    except subprocess.CalledProcessError as err:
        shorted_commands = " ".join(command)[:50]
        log(f"Command {shorted_commands} failed with error: {err}",
            level="error")
        return None


def exec_command_and_response_bool(repo: str,
                                   command: List[str],
                                   capture_output: bool = False) -> bool:
    """This function executes a shell command within the specified git repository path."""
    return bool(exec_command(repo, command, capture_output))


@exception_handler
def setup_repository(repo: str, branch_name: str = "main") -> bool:
    """Set up the repository to point to a specific branch."""
    path = os.path.join(DEFAULT_PATH, repo)
    # リポジトリが存在するか確認する
    if not os.path.exists(path):
        # リポジトリが存在しない場合はcloneする
        os.makedirs(path[:-len(repo) + repo.index("/")], exist_ok=True)
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
    return exec_command_and_response_bool(
        repo[:repo.index("/")],
        ["git", "clone", "git@github.com:" + repo],
    )


def pull_repository(repo: str) -> bool:
    """リポジトリをpullする"""
    return exec_command_and_response_bool(
        repo,
        ["git", "pull"],
    )


def create_issue(repo: str, title: str, body: str) -> bool:
    """Create a new issue on GitHub."""
    return exec_command_and_response_bool(
        repo,
        ["gh", "issue", "create", "-t", title, "-b", body],
    )


@exception_handler
def list_issue_ids(repo: str) -> List[int]:
    """issue idを取得する"""

    res = exec_command(
        repo,
        ["gh", "issue", "list"],
        capture_output=True,
    )
    if not res:
        return []

    issue_row = res.stdout.decode().split("\t")
    return list(map(int, issue_row))


@exception_handler
def get_issue_by_id(repo: str, issue_id: int) -> Union[Issue, None]:
    """idからissueを取得する"""

    res = exec_command(
        repo,
        ["gh", "issue", "view", str(issue_id)],
        capture_output=True,
    )
    if not res:
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

    res = exec_command(
        repo,
        ["gh", "issue", "view", str(issue_id), "-c"],
        capture_output=True,
    )
    if not res:
        return issue

    comment_attrs = [
        "author",
        "association",
        "edited",
        "status",
    ]

    is_body = False
    body = ""
    comment: Dict[str, str] = {}
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


def reply_issue(repo: str, issue_id: int, body: str) -> bool:
    """issueに返信する"""
    return exec_command_and_response_bool(
        repo,
        ["gh", "issue", "comment",
         str(issue_id), "-b", body],
    )


def checkout_branch(repo: str, branch_name: str) -> bool:
    """ブランチをチェックアウトする"""
    return exec_command_and_response_bool(
        repo,
        ["git", "checkout", branch_name],
    )


def checkout_new_branch(repo: str, branch_name: str) -> bool:
    """新しいブランチを作成する"""
    return exec_command_and_response_bool(
        repo,
        ["git", "checkout", "-b", branch_name],
    )


def commit(repo: str, message: str) -> bool:
    """コミットする"""
    return exec_command_and_response_bool(
        repo,
        ["git", "commit", "-a", "-m", message],
    )


def push_repository(repo: str, branch_name: str) -> bool:
    """リポジトリをpushする"""
    return exec_command_and_response_bool(
        repo,
        ["git", "push", "origin", branch_name],
    )


def get_datetime_of_last_commit(repo: str, branch_name: str) -> datetime:
    """最後のコミットの日時を取得する"""
    setup_repository(repo, branch_name)
    command = [
        "git", "log", "--date=iso", "--date=format:'%Y/%m/%d %H:%M:%S'",
        "--pretty=format:'%ad'", "-1"
    ]
    repo_path = os.path.join(DEFAULT_PATH, repo)
    proc = subprocess.run(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=repo_path,
        check=True,
    )
    last_commit_datetime = datetime.strptime(
        proc.stdout.decode('utf-8').strip("'"), '%Y/%m/%d %H:%M:%S')
    return last_commit_datetime
