"""Router for the API."""

from typing import Union

import logic
import services.github
import services.github.exceptions
import services.llm
from logic import logic_exceptions, logic_utils
from utils.logging_utils import log

from .routers_utils import send_messages_to_system


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
        ("You are a programmer of the highest caliber."
         "Please read the code of the existing program "
         "and rewrite any one based on the issue."),
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
            ("README.md file does not exist. "
             "A new README.md will be created with generated content."),
            level="warning",
        )
        raise

    readme_message = f"```Current README.md\n{readme_content}```"
    messages = logic.generate_messages_from_files(repo, code_lang)
    messages.append({"role": "user", "content": readme_message})
    generated_text = send_messages_to_system(
        messages,
        ("You are a programmer of the highest caliber."
         "Please read the code of the existing program and generate README.md."
         ),
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
    except (PermissionError, IOError) as err:
        log(f"File operation error: {err}", level="error")
        raise
    except Exception as err:
        log(f"Unexpected error during branch checkout: {err}", level="error")
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
    new_branch = None
    try:
        # リポジトリのセットアップ
        try:
            services.github.setup_repository(repo, branch)
        except Exception as err:
            log(f"リポジトリのセットアップに失敗しました: {err}", level="error")
            raise

        # 新しいブランチの作成
        new_branch = f"update-issue-#{issue_id}"
        if new_branch != branch:
            try:
                services.github.checkout_new_branch(repo, new_branch)
            except services.github.exceptions.GitBranchAlreadyExistsException:
                log(f"ブランチ {new_branch} は既に存在します", level="warning")
                services.github.checkout_branch(repo, new_branch)
            except Exception as err:
                log(f"新しいブランチの作成に失敗しました: {err}", level="error")
                raise

        # issueの取得
        try:
            issue = services.github.get_issue_by_id(repo, issue_id)
        except Exception as err:
            log(f"Issueの取得に失敗しました: {err}", level="error")
            raise

        # コード修正の生成と検証
        try:
            modification = logic.generate_modification_from_issue(
                repo, issue, code_lang)
            is_valid = logic.verify_modification(repo, modification)
            if not is_valid:
                raise ValueError(f"無効な修正です: {modification}")
        except Exception as err:
            log(f"コード修正の生成と検証に失敗しました: {err}", level="error")
            raise

        # コミットメッセージの生成と修正の適用
        try:
            msg = logic.generate_commit_message(repo, issue, modification)
            logic.apply_modification(repo, modification)
        except logic_exceptions.CodeNotModifiedError as err:
            log(f"コードに変更がありません: {err}", level="info")
            raise
        except Exception as err:
            log(f"修正の適用に失敗しました: {err}", level="error")
            raise

        # 変更のコミット
        try:
            if not services.github.commit(repo, msg):
                raise ValueError(f"コミットに失敗しました: {msg}")
        except Exception as err:
            log(f"変更のコミットに失敗しました: {err}", level="error")
            raise

        # リポジトリへのプッシュ
        try:
            services.github.push_repository(repo, new_branch)
        except Exception as err:
            log(f"変更のプッシュに失敗しました: {err}", level="error")
            raise

        # issueへの返信
        try:
            issue_message = logic.generate_issue_reply_message(
                repo, issue, modification, msg)
            services.github.reply_issue(repo, issue.id, issue_message)
        except Exception as err:
            log(f"Issueへの返信に失敗しました: {err}", level="error")
            raise

    finally:
        # ブランチのクリーンアップ
        if new_branch and branch != new_branch:
            try:
                services.github.checkout_branch(repo, branch)
                services.github.delete_branch(repo, new_branch)
            except Exception as err:
                log(f"ブランチのクリーンアップに失敗しました: {err}", level="error")
                # クリーンアップの失敗は警告のみとし、メイン処理の結果には影響させない
