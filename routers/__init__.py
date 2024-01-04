from pathlib import Path
from services import (
    generate_text,
    get_issue,
    get_issue_by_id,
    reply_issue,
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
    messages.append({"role": "user", "content": additional_message})
    return messages


def send_messages_to_system(messages, system_instruction):
    """Send messages to AI system for code generation."""
    messages.append({"role": "system", "content": system_instruction})
    generated_text = generate_text(messages)
    print(generated_text)
    return generated_text


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
    # Add any post-processing if necessary...


def update_issue():
    """Update an issue with a comment."""

    issue = get_issue()
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
    # Add any post-processing if necessary...


def generate_readme():
    """Generate README.md documentation for the entire program."""

    python_files = enumerate_python_files()
    with open("README.md", "r") as f:
        readme_content = f.read()
    readme_message = f"```Current README.md\n{readme_content}```"
    messages = prepare_messages_from_files(python_files, readme_message)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and generate README.md."
    )
    with open("README.md", "w") as f:
        f.write(generated_text)
    # Add any post-processing if necessary...
