"""This module provides functions to generate a modification from an issue and a codebase."""
import os

import schemas
import services
import services.llm

EXCLUDE_DIRS = os.environ.get('EXCLUDE_DIRS', '__pycache__,.git').split(',')


def apply_modification(repo, modification):
    """Apply modification"""
    repo_path = get_repo_path(repo)
    file_path = os.path.join(repo_path, modification['filepath'])
    with open(file_path, "r") as file_object:
        before_code = file_object.read()
    after_code = before_code.replace(
        modification['before_code'],
        modification['after_code'])
    with open(file_path, "w") as file_object:
        file_object.write(after_code)
    return True


def generate_modification_from_issue(
    repo: str,
    issue: schemas.Issue,
    code_lang: str,
):
    """Generate a modification from an issue"""
    messages = generate_messages_from_files(repo, code_lang)
    messages.extend(generate_messages_from_issue(issue))
    messages.append({
        "role":
        "system",
        "content":
        "Output code modification as JSON format from the whole code and issues. The JSON modification includes keys such as 'filepath', 'before_code', 'after_code'. 'before_code' is a part of file.\ne.g.\n```{filepath: 'path/to/file', before_code: 'def func1(aaa: int):\n\"\"\"Output an argment\"\"\"\nprint(aaa)\n', after_code: 'def func1(aaa: int, bbb: int):\n\"\"\"Output two argments\"\"\"\nprint(aaa)\nprint(bbb)\n'}```\n"
    })
    openai_client = services.llm.get_openai_client()
    generated_json = services.llm.generate_json(messages, openai_client)
    return generated_json


def velify_modification(repo: str, modification):
    """Velify modification"""
    repo_path = get_repo_path(repo)
    file_path = os.path.join(repo_path, modification['filepath'])
    with open(file_path, "r") as file_object:
        before_code = file_object.read()
    return modification['before_code'] in before_code


def generate_commit_message(repo, issue, modification):
    """Generate a commit message from an issue and a modification."""
    messages = generate_messages_from_issue(issue)
    messages.append({
        "role":
        "assistant",
        "content":
        f"Before:\n{modification['before_code']}\nAfter:\n{modification['after_code']}"
    })
    messages.append({
        "role":
        "system",
        "content":
        "Output commit message from the issue and the modification."
    })
    openai_client = services.llm.get_openai_client()
    commit_message = services.llm.generate_text(messages, openai_client)
    if "\n" in commit_message:
        commit_message = commit_message.split("\n")[0].strip("\"")
    commit_message += f" (#{issue.id})"
    return commit_message


def generate_messages_from_issue(issue: schemas.Issue):
    """Generate LLM messages from issue"""
    messages = []
    messages.append({
        "role": "user",
        "content": f"```{issue.title}\n{issue.body}```\n"
    })
    for comment in issue.comments:
        messages.append({
            "role": "user",
            "content": f"```issue comment\n{comment.body}```\n"
        })
    return messages


def generate_messages_from_files(repo: str, code_lang: str):
    """Generate LLM messages from files"""

    extension_dict = {
        "python": [".py"],
        "tex": [".tex"],
    }
    target_extension = extension_dict[code_lang]

    messages = []
    repo_path = get_repo_path(repo)
    for root, dirs, files in os.walk(repo_path):
        # 探索するディレクトリを制限する
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if not file.endswith(tuple(target_extension)):
                continue
            with open(os.path.join(root, file), "r") as file_object:
                content = file_object.read()
            filename = os.path.join(root, file)[len(repo_path) + 1:]
            messages.append({
                "role": "user",
                "content": f"```{filename}\n{content}```\n"
            })
    return messages


def generate_issue_reply_message(repo, issue, modification, commit_message):
    """Generate a reply message."""
    message = commit_message + "\n"
    message += f"`{modification['filepath']}`\nBefore:\n```{modification['before_code']}```\nAfter:\n```{modification['after_code']}```"
    return message


def get_repo_path(repo: str):
    """Get repo path"""
    return os.path.join("downloads", repo)
