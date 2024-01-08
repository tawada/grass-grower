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


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def enumerate_python_files(repo: str):
    """Enumerate all Python files in the directory structure."""
    python_files = []
    # downloads/リポジトリ名/以下のファイルを列挙する
    repo_path = "./downloads/" + repo
    for file in Path(repo_path).glob("**/*.py"):
        with open(file, "r") as f:
            content = f.read()
            python_files.append({"filename": str(file)[len(repo_path) - 1:], "content": content})
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


def add_issue(
    repo: str,
    branch_name: str = "main",
):
    """Add an issue to the repository."""

    setup_repository(repo, branch_name)
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


def generate_code_from_issue(
    issue_id: int,
    repo: str,
    branch_name: str = "main",
) -> Union[str, None]:
    """Generate code from an issue and return the generated code.

    Args:
    - issue_id (int): The identifier for the issue to generate code from.

    Returns:
    - str: The generated code based on the issue, or none if the issue cannot be retrieved.
    """
    setup_repository(repo, branch_name)
    issue = get_issue_by_id(repo, issue_id)
    if issue is None:
        logger.error(f"Failed to retrieve issue with ID: {issue_id}")
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


def update_issue(
    issue_id: int,
    repo: str,
    branch_name: str = "main",
):
    """Update an issue with a comment."""

    setup_repository(repo, branch_name)
    issue = get_issue_by_id(repo, issue_id)

    if issue is None:
        logger.error(f"Failed to retrieve issue with ID: {issue_id}")
        return

    python_files = enumerate_python_files(repo)
    messages = prepare_messages_from_files(python_files, "")
    messages = prepare_messages_from_issue(messages, issue)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and make additional comments on the issue."
    )
    reply_issue(repo, issue.id, generated_text)


def summarize_issue(
    issue_id: int,
    repo: str,
    branch_name: str = "main",
):
    setup_repository(repo, branch_name)
    issue = get_issue_by_id(repo, issue_id)
    if issue is None or issue.summary:
        logger.error(f"Failed to retrieve issue or issue already summarized with ID: {issue_id}")
        return None
    
    messages = prepare_messages_from_issue([], issue)
    
    # Message to the system for summarization instruction
    system_instruction = "Please summarize the following issue and its discussion succinctly."
    
    issue.summary = send_messages_to_system(messages, system_instruction)
    
    # Persist the summary back to the issue as a comment
    reply_issue(repo, issue.id, f"Summary:\n{issue.summary}")


def generate_readme(
    repo: str,
    branch_name: str = "main",
):
    """Generate README.md documentation for the entire program."""

    setup_repository(repo, branch_name)
    python_files = enumerate_python_files(repo)

    # Initialize readme_content as empty string to handle the case when file doesn't exist
    readme_content = ""

    try:
        repo_path = "./downloads/" + repo
        with open(repo_path + "/README.md", "r") as f:
            readme_content = f.read()
    except FileNotFoundError:
        logger.error(
            "README.md file does not exist. A new README.md will be created with generated content."
        )
        # Not returning from the function here, as we might still want to generate a new README.md
    except OSError as e:
        # Catching any other OS-related errors (like file permission issues) 
        # and displaying the error message to the user.
        logger.error(f"Error while reading README.md: {e}")
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
        logger.error(f"Error to checkout a new branch: {e}")
        return False

    # Attempt to write the README.md file.
    try:
        with open(repo_path + "/README.md", "w") as f:
            f.write(generated_text)
    except OSError as e:
        logger.error(f"Error while writing to README.md: {e}")
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
