"""GitHub API service."""
import os
import subprocess
from datetime import datetime
from typing import List

from config import config
from schemas import Issue, IssueComment
from services.github import exceptions, github_utils

DEFAULT_PATH = config["repository_path"]


def setup_repository(repo: str, branch_name: str = "main"):
    """Set up the repository to point to a specific branch."""
    # リポジトリが存在するか確認する
    if not github_utils.exists_repo(DEFAULT_PATH, repo):
        # リポジトリが存在しない場合はcloneする
        clone_repository(repo)
    else:
        # リポジトリが存在する場合はpullする
        pull_repository(repo)
    # リポジトリのブランチを指定する
    checkout_branch(repo, branch_name)


def clone_repository(repo: str) -> bool:
    """Clone the repository."""
    github_utils.make_owner_dir(DEFAULT_PATH, repo)
    try:
        return github_utils.exec_command_and_response_bool(
            repo[:repo.index("/")],
            ["git", "clone", "git@github.com:" + repo],
            True,
        )
    except exceptions.GitHubRepoNotFoundException as err:
        raise exceptions.GitHubRepoNotFoundException(
            f"Invalid repository: {repo}") from err


def pull_repository(repo: str) -> bool:
    """リポジトリをpullする"""
    try:
        return github_utils.exec_command_and_response_bool(
            repo,
            ["git", "pull"],
            True,
        )
    except exceptions.GitHubRepoNotFoundException as err:
        raise exceptions.GitHubRepoNotFoundException(
            f"Invalid repository: {repo}") from err


def create_issue(repo: str, title: str, body: str) -> bool:
    """Create a new issue on GitHub."""
    return github_utils.exec_command_and_response_bool(
        repo,
        ["gh", "issue", "create", "-t", title, "-b", body],
    )


def list_issue_ids(repo: str) -> List[int]:
    """issue idを取得する"""

    res = github_utils.exec_command(
        repo,
        ["gh", "issue", "list"],
        capture_output=True,
    )
    if not res:
        return []

    issue_row = res.stdout.decode().split("\t")
    return list(map(int, issue_row))


def get_issue_by_id(repo: str, issue_id: int) -> Issue:
    """idからissueを取得する"""

    issue = get_issue_body(repo, issue_id)
    comments = get_issue_comments(repo, issue_id)
    issue.comments = comments
    return issue


def exec_get_issue_body(repo: str, issue_id: int) -> str:
    """issueの本文を取得する"""
    try:
        res = github_utils.exec_command(
            repo,
            ["gh", "issue", "view", str(issue_id)],
            capture_output=True,
        )
    except exceptions.GitHubRepoNotFoundException as err:
        raise exceptions.GitHubRepoNotFoundException(
            f"Invalid repository: {repo}") from err
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


def exec_get_issue_comments(repo: str, issue_id: int) -> str:
    """issueのコメントを取得する"""
    res = github_utils.exec_command(
        repo,
        ["gh", "issue", "view", str(issue_id), "-c"],
        capture_output=True,
    )
    return res.stdout.decode()


def parse_issue_comments(issue_comments: str) -> List[IssueComment]:
    """issueのコメントをパースする"""
    comment_attrs = [
        "author",
        "association",
        "edited",
        "status",
    ]
    if not issue_comments:
        return []
    parsed_comments = parse_github_text(issue_comments, comment_attrs)
    comments: List[IssueComment] = [
        IssueComment(**comment) for comment in parsed_comments
    ]
    return comments


def parse_github_text(target_text: str,
                      attrs: list[str]) -> list[dict[str, str]]:
    """Parse the text of a GitHub issue or pull request."""
    items: list[dict[str, str]] = []
    fields = split_text_by_borderlines(target_text)
    for idx, field_body in enumerate(fields):
        if idx % 2 == 0:
            # attribute field
            parse_attribute_field(items, field_body, attrs)
        else:
            # body field
            parse_body_field(items, field_body)
    return items


def parse_attribute_field(items: list[dict[str, str]], field_body: str,
                          attrs: list[str]):
    """Parse the attribute field."""
    item = make_dict_from_field_body(field_body, attrs)
    if item:
        items.append(item)


def parse_body_field(items: list[dict[str, str]], field_body: str):
    """Parse the body field."""
    if items:
        items[-1]["body"] = field_body


def make_dict_from_field_body(
    field_body: str,
    attrs: list[str],
) -> dict[str, str]:
    """Make a dictionary from the field body."""
    item = {}
    for line in field_body.splitlines():
        key_value = line.split(":\t")
        if len(key_value) == 2 and key_value[0] in attrs:
            item[key_value[0]] = key_value[1].strip()
    return item


def split_text_by_borderlines(text: str) -> List[str]:
    """Split the text by borderlines."""
    # A borderline starts with "--".
    return text.split("\n--\n")


def get_issue_comments(repo: str, issue_id: int) -> List[IssueComment]:
    """issueのコメントを取得する"""
    issue_comments = exec_get_issue_comments(repo, issue_id)
    return parse_issue_comments(issue_comments)


def reply_issue(repo: str, issue_id: int, body: str) -> bool:
    """issueに返信する"""
    return github_utils.exec_command_and_response_bool(
        repo,
        ["gh", "issue", "comment",
         str(issue_id), "-b", body],
    )


def checkout_branch(repo: str, branch_name: str) -> bool:
    """ブランチをチェックアウトする"""
    return github_utils.exec_command_and_response_bool(
        repo,
        ["git", "checkout", branch_name],
    )


def checkout_new_branch(repo: str, branch_name: str) -> bool:
    """新しいブランチを作成する"""
    try:
        return github_utils.exec_command_and_response_bool(
            repo,
            ["git", "checkout", "-b", branch_name],
            capture_output=True,
        )
    except exceptions.GitBranchAlreadyExistsException as err:
        raise exceptions.GitBranchAlreadyExistsException(
            f"Branch already exists: {branch_name}") from err


def commit(repo: str, message: str) -> bool:
    """コミットする"""
    return github_utils.exec_command_and_response_bool(
        repo,
        ["git", "commit", "-a", "-m", message],
    )


def push_repository(repo: str, branch_name: str) -> bool:
    """リポジトリをpushする"""
    try:
        return github_utils.exec_command_and_response_bool(
            repo,
            ["git", "push", "origin", branch_name],
            capture_output=True,
        )
    except exceptions.GitHubRepoNotFoundException as err:
        raise exceptions.GitHubRepoNotFoundException(
            f"Invalid repository: {repo}") from err


def delete_branch(repo: str, branch_name: str) -> bool:
    """ブランチを削除する"""
    return github_utils.exec_command_and_response_bool(
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
    return github_utils.exec_command_and_response_bool(
        repo,
        ["gh", "pr", "-B", to_branch, "-b", body, "-t", title],
    )


def get_branch(repo: str) -> str:
    """ブランチを取得する"""
    res = github_utils.exec_command(
        repo,
        ["git", "branch", "--show-current"],
        capture_output=True,
    )
    return res.stdout.decode().strip()


def get_default_branch(repo: str) -> str:
    """デフォルトブランチを取得する"""
    res = github_utils.exec_command(
        repo,
        ["git", "symbolic-ref", "--short", "HEAD"],
        capture_output=True,
    )
    return res.stdout.decode().strip()
