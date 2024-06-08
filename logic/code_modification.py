"""A module to handle code modifications."""
import dataclasses
import os

import schemas
import services.llm
from utils.logging_utils import log

from . import logic_utils


@dataclasses.dataclass
class CodeModification:
    """A class to represent a code modification."""

    file_path: str
    before_code: str
    after_code: str


def apply_modification(repo_name: str, modification: CodeModification) -> bool:
    """
    Apply modification

    Args:
        repo_name: The name of the repository.
        modification: The modification to apply.

    Returns:
        True if the modification was applied successfully.

    Raises:
        RuntimeError: If the code has no changes.
    """
    repo_path = logic_utils.get_repo_path(repo_name)
    file_path = os.path.join(repo_path, modification.file_path)
    with open(file_path, "r", newline="") as file_object:
        before_code = file_object.read()
    after_code = before_code.replace(modification.before_code,
                                     modification.after_code)
    if before_code == after_code:
        raise RuntimeError("Code has no changes")
    with open(file_path, "w", newline="") as file_object:
        file_object.write(after_code)
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
        "Propose a new code modification as JSON format from the whole code and issues. Do not duplicate output if the code has already been changed. The JSON modification includes keys such as 'file_path', 'before_code', 'after_code'. 'before_code' is a part of file.\ne.g.\n```{file_path: 'path/to/file', before_code: 'def func1(aaa: int):\n\"\"\"Output an argment\"\"\"\nprint(aaa)\n', after_code: 'def func1(aaa: int, bbb: int):\n\"\"\"Output two argments\"\"\"\nprint(aaa)\nprint(bbb)\n'}```\n",
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
    with open(file_path, "r") as file_object:
        before_code = file_object.read()
    return modification.before_code in before_code


def generate_commit_message(repo, issue, modification: CodeModification):
    """Generate a commit message from an issue and a modification."""
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
    message = "The following changes have been completed.\n\n" + commit_message + "\n"
    message += f"`{modification.file_path}`\nBefore:\n```\n{modification.before_code}\n```\nAfter:\n```\n{modification.after_code}\n```"
    return message
