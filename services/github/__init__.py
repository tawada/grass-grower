"""GitHub API service."""
import os
import subprocess
from datetime import datetime
from typing import List, Union

from schemas import Issue, IssueComment
from services.github import exceptions
from utils.logging_utils import exception_handler, log

DEFAULT_PATH = "downloads"


def exec_command(repo: str,
                 command: List[str],
                 capture_output: bool = False) -> subprocess.CompletedProcess:
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
        log(f"Command {shorted_commands} failed with error ({err.returncode}): {err}",
            level="exception")
        raise


def exec_command_and_response_bool(repo: str,
                                   command: List[str],
                                   capture_output: bool = False) -> bool:
    """This function executes a shell command within the specified git repository path."""
    return bool(exec_command(repo, command, capture_output))


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
    try:
        return exec_command_and_response_bool(
            repo[:repo.index("/")],
            ["git", "clone", "git@github.com:" + repo],
            True,
        )
    except subprocess.CalledProcessError as err:
        exception, error_message = exceptions.parse_exception(err)
        if exception == ValueError:
            raise ValueError(f"Invalid repository: {repo}") from err
        raise exception(error_message) from err


def pull_repository(repo: str) -> bool:
    """リポジトリをpullする"""
    try:
        return exec_command_and_response_bool(
            repo,
            ["git", "pull"],
            True,
        )
    except subprocess.CalledProcessError as err:
        exception, error_message = exceptions.parse_exception(err)
        if exception == ValueError:
            raise ValueError(f"Invalid repository: {repo}") from err
        raise exception(error_message) from err


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

    issue = get_issue_body(repo, issue_id)
    comments = get_issue_comments(repo, issue_id)
    issue.comments = comments
    return issue


def exec_get_issue_body(repo: str, issue_id: int) -> str:
    """issueの本文を取得する"""
    try:
        res = exec_command(
            repo,
            ["gh", "issue", "view", str(issue_id)],
            capture_output=True,
        )
    except subprocess.CalledProcessError as err:
        err_msg = "Could not resolve to an issue or pull request with the number of"
        if err.stderr and err_msg in err.stderr.decode():
            log(f"{err_msg} {issue_id}", level="error")
            raise ValueError(f"{err_msg} {issue_id}") from err
        raise Exception("Failed to get issue body") from err
    return res.stdout.decode()


def parse_issue_body(issue_id: int, issue_body: str) -> Issue:
    """issueの本文をパースする"""
    body_attrs = ["title"]
    parsed_body = parse_github_text(issue_body, body_attrs)[0]
    issue = Issue(id=issue_id, comments=[], **parsed_body)
    return issue


def get_issue_body(repo: str, issue_id: int) -> Issue:
    """issueの本文を取得する"""
    issue_body = exec_get_issue_body(repo, issue_id)
    return parse_issue_body(issue_id, issue_body)


def excec_get_issue_comments(repo: str, issue_id: int) -> str:
    """issueのコメントを取得する"""
    res = exec_command(
        repo,
        ["gh", "issue", "view", str(issue_id), "-c"],
        capture_output=True,
    )
    if not res:
        raise Exception("Failed to get issue body")
    return res.stdout.decode()


def parse_issue_comments(issue_comments: str) -> List[IssueComment]:
    """issueのコメントをパースする"""
    comment_attrs = [
        "author",
        "association",
        "edited",
        "status",
    ]
    parsed_comments = parse_github_text(issue_comments, comment_attrs)
    comments: List[IssueComment] = [
        IssueComment(**comment) for comment in parsed_comments
    ]
    return comments


def parse_github_text(target_text: str,
                      attrs: list[str]) -> list[dict[str, str]]:
    """Parse the text of a GitHub issue or pull request."""
    items = []
    item = {"body": ""}
    is_attribute_field = True
    for line in target_text.splitlines():
        if line.startswith("--"):
            if not is_attribute_field:
                # body field is finished
                items.append(item)
                item = {"body": ""}
            # switch between attribute field and body field
            is_attribute_field ^= True
        elif is_attribute_field:
            # attribute field
            idx = line.find(":\t")
            key = line[:idx]
            if idx != -1 and key in attrs:
                value = line[idx + 2:].strip()
                item[key] = value
        else:
            # body field
            item["body"] += line + "\n"
    if item["body"]:
        # add the last item
        items.append(item)
    return items


def get_issue_comments(repo: str, issue_id: int) -> List[IssueComment]:
    """issueのコメントを取得する"""
    issue_comments = excec_get_issue_comments(repo, issue_id)
    return parse_issue_comments(issue_comments)


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
    try:
        return exec_command_and_response_bool(
            repo,
            ["git", "push", "origin", branch_name],
        )
    except subprocess.CalledProcessError as err:
        exception, error_message = exceptions.parse_exception(err)
        if exception == ValueError:
            raise ValueError(f"Invalid repository: {repo}") from err
        raise exception(error_message) from err


def delete_branch(repo: str, branch_name: str) -> bool:
    """ブランチを削除する"""
    return exec_command_and_response_bool(
        repo,
        ["git", "branch", "-D", branch_name],
    )


def get_datetime_of_last_commit(repo: str, branch_name: str) -> datetime:
    """最後のコミットの日時を取得する"""
    setup_repository(repo, branch_name)
    command = [
        "git",
        "log",
        "--date=iso",
        "--date=format:'%Y/%m/%d %H:%M:%S'",
        "--pretty=format:'%ad'",
        "-1",
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
        proc.stdout.decode("utf-8").strip("'"), "%Y/%m/%d %H:%M:%S")
    return last_commit_datetime


def pull_request(
    repo: str,
    to_branch: str,
    title: str,
    body: str,
) -> bool:
    """プルリクエストを作成する"""
    return exec_command_and_response_bool(
        repo,
        ["gh", "pr", "-B", to_branch, "-b", body, "-t", title],
    )
