"""GitHub API service."""

import os
import subprocess
from datetime import datetime
from typing import List

from config import config
from schemas import Issue, IssueComment
from services.github import exceptions
from utils import github_utils
from utils.logging_utils import log

DEFAULT_PATH = os.getenv('REPOSITORY_PATH', config["repository_path"])


def setup_repository(repo: str, branch_name: str = "main"):
    """リポジトリを特定のブランチに設定します。

    このメソッドは、指定されたリポジトリがローカルファイルシステムに存在するかを確認します。
    存在しない場合はGitHubからクローンし、存在する場合は最新の変更をプルします。
    その後、指定されたブランチをチェックアウトします。

    Args:
        repo (str): 'オーナー名/リポジトリ名' 形式のリポジトリ名
        branch_name (str, optional): チェックアウトするブランチ名。デフォルトは'main'

    Raises:
        exceptions.GitHubRepoNotFoundException: リポジトリが無効または見つからない場合
        exceptions.GitHubConnectionException: GitHub接続エラーの場合
        exceptions.GitException: その他のGit操作エラーの場合
    """
    try:
        if not github_utils.exists_repo(DEFAULT_PATH, repo):
            log(f"リポジトリ {repo} が存在しないため、クローンを試みます", level="info")
            clone_repository(repo)
        else:
            branch = get_branch(repo)
            default_branch = get_default_branch(repo)
            if branch != default_branch:
                log(f"ブランチを {default_branch} に切り替えます", level="info")
                checkout_branch(repo, default_branch)
            pull_repository(repo)
        checkout_branch(repo, branch_name)
    except exceptions.GitHubConnectionException as err:
        log(f"GitHubへの接続に失敗しました: {str(err)}", level="error")
        raise
    except exceptions.GitHubRepoNotFoundException as err:
        log(f"リポジトリが見つかりません: {str(err)}", level="error")
        raise
    except exceptions.GitException as err:
        log(f"Git操作でエラーが発生しました: {str(err)}", level="error")
        raise


def clone_repository(repo: str) -> bool:
    """Clone the repository."""
    github_utils.make_owner_dir(DEFAULT_PATH, repo)
    try:
        return github_utils.exec_git_command_and_response_bool(
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
        return github_utils.exec_git_command_and_response_bool(
            repo,
            ["git", "pull"],
            True,
        )
    except exceptions.GitHubRepoNotFoundException as err:
        raise exceptions.GitHubRepoNotFoundException(
            f"Invalid repository: {repo}") from err


def create_issue(repo: str, title: str, body: str) -> bool:
    """Create a new issue on GitHub."""
    return github_utils.exec_git_command_and_response_bool(
        repo,
        ["gh", "issue", "create", "-t", title, "-b", body],
    )


def list_issue_ids(repo: str) -> List[int]:
    """issue idを取得する"""

    res = github_utils.exec_git_command(
        repo,
        ["gh", "issue", "list"],
        capture_output=True,
    )
    if not res:
        return []

    issue_rows = res.stdout.decode().split("\n")
    return list(
        map(lambda line: int(line.split("\t")[0]),
            filter(lambda x: x, issue_rows)))


def get_issue_by_id(repo: str, issue_id: int) -> Issue:
    """idからissueを取得する"""

    issue = get_issue_body(repo, issue_id)
    comments = get_issue_comments(repo, issue_id)
    issue.comments = comments
    return issue


def get_issue_body_content(repo: str, issue_id: int) -> str:
    """issueの本文を取得する"""
    try:
        res = github_utils.exec_git_command(
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
    issue_body = get_issue_body_content(repo, issue_id)
    return parse_issue_body(issue_id, issue_body)


def get_issue_comments_content(repo: str, issue_id: int) -> str:
    """issueのコメントを取得する"""
    res = github_utils.exec_git_command(
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
    issue_comments = get_issue_comments_content(repo, issue_id)
    return parse_issue_comments(issue_comments)


def reply_issue(repo: str, issue_id: int, body: str) -> bool:
    """issueに返信する"""
    return github_utils.exec_git_command_and_response_bool(
        repo,
        ["gh", "issue", "comment",
         str(issue_id), "-b", body],
    )


def checkout_branch(repo: str, branch_name: str) -> bool:
    """ブランチをチェックアウトする"""
    return github_utils.exec_git_command_and_response_bool(
        repo,
        ["git", "checkout", branch_name],
    )


def checkout_new_branch(repo: str, branch_name: str) -> bool:
    """新しいブランチを作成する"""
    try:
        return github_utils.exec_git_command_and_response_bool(
            repo,
            ["git", "checkout", "-b", branch_name],
            capture_output=True,
        )
    except exceptions.GitBranchAlreadyExistsException as err:
        raise exceptions.GitBranchAlreadyExistsException(
            f"Branch already exists: {branch_name}") from err


def commit(repo: str, message: str) -> bool:
    """コミットする"""
    return github_utils.exec_git_command_and_response_bool(
        repo,
        ["git", "commit", "-a", "-m", message],
    )


def push_repository(repo: str, branch_name: str) -> bool:
    """リポジトリをpushする"""
    try:
        return github_utils.exec_git_command_and_response_bool(
            repo,
            ["git", "push", "origin", branch_name],
            capture_output=True,
        )
    except exceptions.GitHubRepoNotFoundException as err:
        raise exceptions.GitHubRepoNotFoundException(
            f"Invalid repository: {repo}") from err


def delete_branch(repo: str, branch_name: str) -> bool:
    """ブランチを削除する"""
    return github_utils.exec_git_command_and_response_bool(
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
    return github_utils.exec_git_command_and_response_bool(
        repo,
        ["gh", "pr", "-B", to_branch, "-b", body, "-t", title],
    )


def get_branch(repo: str) -> str:
    """ブランチを取得する"""
    res = github_utils.exec_git_command(
        repo,
        ["git", "branch", "--show-current"],
        capture_output=True,
    )
    return res.stdout.decode().strip()


def get_default_branch(repo: str) -> str:
    """デフォルトブランチを取得する"""
    res = github_utils.exec_git_command(
        repo,
        ["git", "symbolic-ref", "--short", "HEAD"],
        capture_output=True,
    )
    return res.stdout.decode().strip()
