"""Router for the API."""
from typing import Union

import logic
import services.github
import services.github.exceptions
import services.llm
from logic import logic_utils
from utils.logging_utils import log


def send_messages_to_system(messages, system_instruction):
    """Send messages to AI system for code generation."""
    messages.append({"role": "system", "content": system_instruction})
    openai_client = services.llm.get_openai_client()
    generated_text = services.llm.generate_text(messages, openai_client)
    return generated_text


def generate_code_from_issue(
    issue_id: int,
    repo: str,
    branch: str = "main",
    code_lang: str = "python",
) -> Union[str, None]:
    """Generate code from an issue and return the generated code.

    Args:
    - issue_id (int): The identifier for the issue to generate code from.

    Returns:
    - str: The generated code based on the issue, or none if the issue cannot be retrieved.
    """

    # Setup the repository and get the issue
    services.github.setup_repository(repo, branch)
    # Get the issue
    issue = services.github.get_issue_by_id(repo, issue_id)

    messages = logic.generate_messages_from_files(repo, code_lang)
    messages.extend(logic.generate_messages_from_issue(issue))
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and rewrite any one based on the issue.",
    )
    print(generated_text)
    return generated_text


def generate_readme(
    repo: str,
    branch: str = "main",
    code_lang: str = "python",
) -> bool:
    """Generate README.md documentation for the entire program."""

    services.github.setup_repository(repo, branch)
    file_path = logic_utils.get_file_path(repo, "README.md")

    try:
        readme_content = logic_utils.get_file_content(file_path)
    except FileNotFoundError:
        log(
            "README.md file does not exist. A new README.md will be created with generated content.",
            level="warning",
        )
        raise

    readme_message = f"```Current README.md\n{readme_content}```"
    messages = logic.generate_messages_from_files(repo, code_lang)
    messages.append({"role": "user", "content": readme_message})
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and generate README.md.",
    )

    # Checkout to the a new branch
    try:
        services.github.checkout_new_branch(repo, "update-readme")
    except services.github.exceptions.GitBranchAlreadyExistsException as err:
        log(f"Error while checking out a new branch: {err}", level="error")
        raise
    except FileNotFoundError as err:
        log(f"Error while checking out a new branch: {err}", level="error")
        raise
    except Exception as err:
        log(f"Error to checkout a new branch: {err}", level="error")
        raise

    validated_text = logic.validate_text(generated_text)
    try:
        logic_utils.write_to_file(file_path, validated_text)
    except OSError as err:
        log(f"Error while writing to README.md: {err}", level="error")
        services.github.checkout_branch(repo, "main")

    # Commit the changes
    services.github.commit(repo, "Update README.md")
    services.github.push_repository(repo, "update-readme")
    services.github.checkout_branch(repo, "main")
    return True


def generate_code_from_issue_and_reply(
    issue_id: int,
    repo: str,
    branch: str = "main",
    code_lang: str = "python",
):
    """Generate code from an issue and reply the generated code to the repository."""

    # Checkout to the branch
    services.github.setup_repository(repo, branch)

    new_branch = f"update-issue-#{issue_id}"
    if new_branch != branch:
        # Checkout to the a new branch
        services.github.checkout_new_branch(repo, new_branch)

    issue = services.github.get_issue_by_id(repo, issue_id)

    modification = logic.generate_modification_from_issue(
        repo, issue, code_lang)
    is_valid = logic.verify_modification(repo, modification)
    try:
        if not is_valid:
            raise ValueError(f"Invalid modification {modification}")

        msg = logic.generate_commit_message(repo, issue, modification)
        logic.apply_modification(repo, modification)
        success = services.github.commit(repo, msg)
        if not success:
            log(str(modification), level="info")
            raise ValueError(f"Failed to commit {msg}")
        services.github.push_repository(repo, new_branch)
        issue_message = logic.generate_issue_reply_message(
            repo, issue, modification, msg)
        services.github.reply_issue(repo, issue.id, issue_message)
    finally:
        if branch != new_branch:
            services.github.checkout_branch(repo, branch)
            services.github.delete_branch(repo, new_branch)
