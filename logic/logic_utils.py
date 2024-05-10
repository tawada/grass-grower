"""Utility functions for logic operations."""
import os

import schemas
from config import config


def enumerate_target_file_paths(repo_path: str, target_extension: list[str]):
    """Enumerate target files in the repository."""
    for file_path in enumerate_file_paths(repo_path):
        if is_target_file(file_path, target_extension):
            yield file_path


def enumerate_file_paths(repo_path: str):
    """Enumerate all files in the repository."""
    for root, dirs, files in os.walk(repo_path):
        # Limit the directories to explore
        dirs[:] = list(filter(is_target_dir, dirs))
        for file_name in files:
            yield os.path.join(root, file_name)


def is_target_dir(dir_name: str):
    """Check if the directory is not a target directory."""
    return dir_name not in config["exclude_dirs"] and not dir_name.startswith(
        ".")


def is_target_file(file_name: str, target_extension: list[str]):
    """Check if the file is a target file."""
    return file_name.endswith(tuple(target_extension))


def get_file_content(file_path: str):
    """Get the content of a file."""
    with open(file_path, "r") as file_object:
        return file_object.read()


def get_file_path(repo: str, file_name: str):
    """Get the file path in the repository."""
    return os.path.join(get_repo_path(repo), file_name)


def get_repo_path(repo: str):
    """Get repo path"""
    return os.path.join(config["repository_path"], repo)


def write_to_file(file_path: str, content: str):
    """Write content to a file."""
    with open(file_path, "w") as file_object:
        file_object.write(content)


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

    for file_path in enumerate_target_file_paths(repo_path, target_extension):
        with open(file_path, "r") as file_object:
            content = file_object.read()
        filename = file_path[len(repo_path) + 1:]
        messages.append({
            "role": "user",
            "content": f"```{filename}\n{content}```\n"
        })
    return messages


def validate_text(raw_text: str):
    """Validate text"""
    candidates = ["```markdown\n", "```\n", "```"]
    validated_text = raw_text
    for start_text in candidates:
        if raw_text.startswith(start_text):
            validated_text = raw_text[len(start_text):]
            break
    if validated_text.endswith("```"):
        validated_text = raw_text[:-len("```")]
    return validated_text
