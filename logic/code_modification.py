"""A module to handle code modifications."""

import dataclasses
import os
import re

import schemas
import services.llm
from utils.logging_utils import log

from . import logic_exceptions, logic_utils


@dataclasses.dataclass
class CodeModification:
    """A class to represent a code modification."""

    file_path: str
    before_code: str
    after_code: str


def apply_modification(repo_name: str, modification: CodeModification) -> bool:
    """
    指定されたコード修正を適用する

    Args:
        repo_name: リポジトリ名
        modification: コード修正の内容

    Returns:
        bool: 修正が成功したかどうか

    Raises:
        ValueError: repo_nameまたはmodificationが無効な場合
        CodeNotModifiedError: コードの変更がない場合
    """
    if not repo_name or not isinstance(repo_name, str):
        raise ValueError("リポジトリ名は必須で、文字列である必要があります")

    if not modification or not isinstance(modification, CodeModification):
        raise ValueError("modificationは必須で、CodeModificationインスタンスである必要があります")

    if not modification.file_path:
        raise ValueError("file_pathは必須です")

    if not modification.after_code:
        raise ValueError("after_codeは必須です")

    repo_path = logic_utils.get_repo_path(repo_name)
    file_path = os.path.join(repo_path, modification.file_path)

    if os.path.exists(file_path):
        # Check if the code has already been modified
        before_code = logic_utils.get_file_content(file_path, newline="")

        # 正規表現を使用して正確な置換を行う
        pattern = re.compile(re.escape(modification.before_code))
        if not pattern.search(before_code):
            raise logic_exceptions.CodeNotModifiedError("対象のコードが見つかりませんでした")

        after_code = pattern.sub(modification.after_code, before_code, count=1)

        # 変更がない場合もエラーを発生させる
        if before_code == after_code:
            raise logic_exceptions.CodeNotModifiedError("コードに変更がありません")
    else:
        after_code = modification.after_code

    logic_utils.write_to_file(file_path, after_code, newline="")
    return True


def generate_modification_from_issue(
    repo: str,
    issue: schemas.Issue,
    code_lang: str,
):
    """Generate a modification from an issue"""
    messages = logic_utils.generate_messages_from_files(repo, code_lang)
    messages.extend(logic_utils.generate_messages_from_issue(issue))
    messages.append({
        "role":
        "system",
        "content":
        ("Propose a new code modification as JSON format from the whole code "
         "and issues. Do not duplicate output if the code has already been "
         "changed. The JSON modification includes keys such as 'file_path', "
         "'before_code', 'after_code'. 'before_code' is a part of file.\n"
         "e.g.\n```{file_path: 'path/to/file', before_code: 'def func1(aaa: "
         "int):\n\"\"\"Output an argment\"\"\"\nprint(aaa)\n', after_code: "
         "'def func1(aaa: int, bbb: int):\n\"\"\"Output two argments\"\"\"\n"
         "print(aaa)\nprint(bbb)\n'}```\n"),
    })
    openai_client = services.llm.get_openai_client()
    generated_json = services.llm.generate_json(messages, openai_client)
    return CodeModification(
        file_path=generated_json["file_path"],
        before_code=generated_json["before_code"],
        after_code=generated_json["after_code"],
    )


def verify_modification(repo: str, modification: CodeModification):
    """Verify modification"""
    repo_path = logic_utils.get_repo_path(repo)
    file_path = os.path.join(repo_path, modification.file_path)
    before_code = logic_utils.get_file_content(file_path)
    return modification.before_code in before_code


def generate_commit_message(repo, issue, modification: CodeModification):
    """Generate a commit message from an issue and a modification."""
    log(f"Generate commit message from issue and modification: {repo} {issue.id}"
        )
    messages = logic_utils.generate_messages_from_issue(issue)
    messages.append({
        "role":
        "assistant",
        "content":
        f"Before:\n{modification.before_code}\nAfter:\n{modification.after_code}",
    })
    messages.append({
        "role":
        "system",
        "content":
        "Output commit message from the issue and the modification.",
    })
    openai_client = services.llm.get_openai_client()
    commit_message: str = services.llm.generate_text(messages, openai_client)

    if not commit_message or len(commit_message) == 0:
        log("Generated commit message is empty.", level="error")
        raise ValueError("Generated commit message cannot be empty.")

    if "\n" in commit_message:
        commit_message = commit_message.split("\n")[0].strip('"')
    elif ". " in commit_message:
        commit_message = commit_message.split(". ")[0].strip('"')
    elif len(commit_message) > 72:
        commit_message = commit_message[:72]
    commit_message += f" (#{issue.id})"
    return commit_message


def generate_issue_reply_message(repo, issue, modification: CodeModification,
                                 commit_message):
    """Generate a reply message."""
    log(f"Generate issue reply message: {repo} {issue.id}")
    message = "The following changes have been completed.\n\n" + commit_message + "\n"
    message += f"`{modification.file_path}`\n"
    message += f"Before:\n```\n{modification.before_code}\n```\n"
    message += f"After:\n```\n{modification.after_code}\n```"
    return message
