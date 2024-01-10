import os
import logging
from pathlib import Path
from typing import Union, List
from schemas import Issue
from services.github import (
    setup_repository,
    checkout_branch,
    checkout_new_branch,
    commit,
    create_issue,
    get_issue_by_id,
    reply_issue,
    push_repository,
)
from services.llm import (
    generate_text,
)
from utils.logging_utils import (
    setup_logging,
    log,
)


def enumerate_python_files(repo: str):
    """Enumerate all Python files in the directory structure."""
    python_files = []
    # downloads/リポジトリ名/以下のファイルを列挙する
    # パスをos.path.joinで結合するときに、先頭の./をつけると、絶対パスになる
    repo_path = os.path.join("downloads",  repo)
    EXCLUDE_DIRS = ["__pycache__", ".git"]
    for root, dirs, files in os.walk(repo_path):
        # 探索するディレクトリを制限する
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith(".py"):
                with open(os.path.join(root, file), "r") as f:
                    content = f.read()
                    # リポジトリ名以下のパスを取得する
                    filename = os.path.join(root, file)[len(repo_path) + 1:]
                    python_files.append({"filename": filename, "content": content})

    return python_files


def prepare_messages_from_files(python_files, additional_message):
    """Prepare messages from enumerated Python files with an additional context message."""
    messages = []
    for file_info in python_files:
        message = f"```{file_info['filename']}\n{file_info['content']}```"
        messages.append({"role": "user", "content": message})
    if additional_message:
        messages.append({"role": "user", "content": additional_message})
    return messages


def prepare_messages_from_issue(messages: List, issue: Issue):
    """Prepare messages from enumerated Python files with an additional context message."""
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


def send_messages_to_system(messages, system_instruction):
    """Send messages to AI system for code generation."""
    messages.append({"role": "system", "content": system_instruction})
    generated_text = generate_text(messages)
    return generated_text


def add_issue(repo: str):
    """Add an issue to the repository."""

    setup_repository(repo)
    python_files = enumerate_python_files(repo)
    messages = prepare_messages_from_files(python_files, "")
    issue_body = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber. Please read the code of the existing program and point out only one issue of whole code. Never refer to yourself as an AI assistant when doing so."
    )
    issue_title = send_messages_to_system(
        [{"role": "assistant", "content": issue_body}],
        "You are a programmer of the highest caliber. Please summarize the above GitHub issue text to one sentense as an issue title."
    )
    issue_title = issue_title.strip().strip('"`').strip("'")
    create_issue(repo, issue_title, issue_body)


def generate_code_from_issue(repo: str, issue_id: int) -> Union[str, None]:
    """Generate code from an issue and return the generated code.

    Args:
    - issue_id (int): The identifier for the issue to generate code from.

    Returns:
    - str: The generated code based on the issue, or none if the issue cannot be retrieved.
    """
    setup_repository(repo)
    issue = get_issue_by_id(repo, issue_id)
    if issue is None:
        log(f"Failed to retrieve issue with ID: {issue_id}", level="error")
        return None

    python_files = enumerate_python_files(repo)
    messages = prepare_messages_from_files(python_files, "")
    messages = prepare_messages_from_issue(messages, issue)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and rewrite any one based on the issue."
    )
    print(generated_text)
    return generated_text


def update_issue(repo: str, issue_id: int):
    """Update an issue with a comment."""

    setup_repository(repo)
    issue = get_issue_by_id(repo, issue_id)

    if issue is None:
        log(f"Failed to retrieve issue with ID: {issue_id}", level="error")
        return

    python_files = enumerate_python_files(repo)
    messages = prepare_messages_from_files(python_files, "")
    messages = prepare_messages_from_issue(messages, issue)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and make additional comments on the issue."
    )
    reply_issue(repo, issue.id, generated_text)


def summarize_issue(repo: str, issue_id: int):
    setup_repository(repo)
    issue = get_issue_by_id(repo, issue_id)
    if issue is None or issue.summary:
        log(f"Failed to retrieve issue or issue already summarized with ID: {issue_id}", level="error")
        return None
    
    messages = prepare_messages_from_issue([], issue)
    
    # Message to the system for summarization instruction
    system_instruction = "Please summarize the following issue and its discussion succinctly."
    
    issue.summary = send_messages_to_system(messages, system_instruction)
    
    # Persist the summary back to the issue as a comment
    reply_issue(repo, issue.id, f"Summary:\n{issue.summary}")


def generate_readme(repo: str):
    """Generate README.md documentation for the entire program."""

    setup_repository(repo)
    python_files = enumerate_python_files(repo)

    # Initialize readme_content as empty string to handle the case when file doesn't exist
    readme_content = ""

    try:
        repo_path = "./downloads/" + repo
        with open(repo_path + "/README.md", "r") as f:
            readme_content = f.read()
    except FileNotFoundError:
        log(
            "README.md file does not exist. A new README.md will be created with generated content.",
            level="warning"
        )
        # Not returning from the function here, as we might still want to generate a new README.md
    except OSError as e:
        # Catching any other OS-related errors (like file permission issues) 
        # and displaying the error message to the user.
        log(f"Error while reading README.md: {e}", level="error")
        return  # Exit the function as we cannot proceed without the existing README.md content

    readme_message = f"```Current README.md\n{readme_content}```"
    messages = prepare_messages_from_files(python_files, readme_message)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and generate README.md."
    )

    # Checkout to the a new branch
    try:
        checkout_new_branch(repo, "update-readme")
    except Exception as e:
        log(f"Error to checkout a new branch: {e}", level="error")
        return False

    # Attempt to write the README.md file.
    try:
        with open(repo_path + "/README.md", "w") as f:
            f.write(generated_text)
    except OSError as e:
        log(f"Error while writing to README.md: {e}", level="error")
        checkout_branch(repo, "main")
        return False
    
    # Commit the changes
    res = commit(repo, "Update README.md")
    if not res:
        return False
    res = push_repository(repo, "update-readme")
    if not res:
        return False
    checkout_branch(repo, "main")
    return True
