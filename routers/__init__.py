from pathlib import Path
from typing import Union
from services.github import (
    create_issue,
    get_issue,
    get_issue_by_id,
    reply_issue,
)
from services.llm import (
    generate_text,
)


def enumerate_python_files():
    """Enumerate all Python files in the directory structure."""
    python_files = []
    for file in Path(".").glob("**/*.py"):
        with open(file, "r") as f:
            content = f.read()
            python_files.append({"filename": str(file), "content": content})
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


def send_messages_to_system(messages, system_instruction):
    """Send messages to AI system for code generation."""
    messages.append({"role": "system", "content": system_instruction})
    generated_text = generate_text(messages)
    print(generated_text)
    return generated_text


def add_issue():
    """Add an issue to the repository."""

    python_files = enumerate_python_files()
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
    create_issue(issue_title, issue_body)


def generate_code_from_issue(issue_id: int):
    """Generate code from an issue."""

    issue = get_issue_by_id(issue_id)
    if issue is None:
        print("Issue could not be retrieved.")
        return

    python_files = enumerate_python_files()
    issue_message = f"```{issue.title}\n{issue.body}```\n"
    messages = prepare_messages_from_files(python_files, issue_message)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and rewrite any one based on the issue."
    )
    return generated_text


def update_issue(issue_id: Union[int, None] = None):
    """Update an issue with a comment."""

    if issue_id is None:
        issue = get_issue()
    else:
        issue = get_issue_by_id(issue_id)

    if issue is None:
        print("Issue could not be retrieved.")
        return

    python_files = enumerate_python_files()
    issue_message = f"```{issue.title}\n{issue.body}```\n"
    messages = prepare_messages_from_files(python_files, issue_message)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and make additional comments on the issue."
    )
    reply_issue(issue.id, generated_text)


def generate_readme():
    """Generate README.md documentation for the entire program."""

    python_files = enumerate_python_files()

    # Initialize readme_content as empty string to handle the case when file doesn't exist
    readme_content = ""

    try:
        with open("README.md", "r") as f:
            readme_content = f.read()
    except FileNotFoundError:
        print(
            "README.md file does not exist. A new README.md will be created with generated content."
        )
        # Not returning from the function here, as we might still want to generate a new README.md
    except OSError as e:
        # Catching any other OS-related errors (like file permission issues) 
        # and displaying the error message to the user.
        print(f"Error while reading README.md: {e}")
        return  # Exit the function as we cannot proceed without the existing README.md content

    readme_message = f"```Current README.md\n{readme_content}```"
    messages = prepare_messages_from_files(python_files, readme_message)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and generate README.md."
    )

    # Attempt to write the README.md file.
    try:
        with open("README.md", "w") as f:
            f.write(generated_text)
    except OSError as e:
        print(f"Error while writing to README.md: {e}")
