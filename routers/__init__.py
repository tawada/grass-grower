"""Router for the API."""
import os
from datetime import datetime
from typing import List, Union

import services.github
import services.llm
from schemas import Issue
from utils.logging_utils import log

EXCLUDE_DIRS = os.environ.get('EXCLUDE_DIRS', '__pycache__,.git').split(',')


def enumerate_target_files(repo: str, code_lang: str):
    """Enumerate all target files in the directory structure."""
    target_files = []
    # downloads/リポジトリ名/以下のファイルを列挙する
    # パスをos.path.joinで結合するときに、先頭の./をつけると、絶対パスになる

    extension_dict = {
        "python": [".py"],
        "tex": [".tex"],
    }
    target_extension = extension_dict.get(code_lang, [])

    repo_path = os.path.join("downloads", repo)
    for root, dirs, files in os.walk(repo_path):
        # 探索するディレクトリを制限する
        dirs[:] = [d for d in dirs if d not in EXCLUDE_DIRS]
        for file in files:
            if file.endswith(tuple(target_extension)):
                with open(os.path.join(root, file), "r") as file_object:
                    content = file_object.read()
                    # リポジトリ名以下のパスを取得する
                    filename = os.path.join(root, file)[len(repo_path) + 1:]
                    target_files.append({
                        "filename": filename,
                        "content": content
                    })

    return target_files


def prepare_messages_from_files(target_files, additional_message):
    """Prepare messages from enumerated target files with an additional context message."""
    messages = []
    for file_info in target_files:
        message = f"```{file_info['filename']}\n{file_info['content']}```"
        messages.append({"role": "user", "content": message})
    if additional_message:
        messages.append({"role": "user", "content": additional_message})
    return messages


def prepare_messages_from_issue(messages: List, issue: Issue):
    """Prepare messages from file contents with an additional context message."""
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
    openai_client = services.llm.get_openai_client()
    generated_text = services.llm.generate_text(messages, openai_client)
    return generated_text


def add_issue(
    repo: str,
    branch: str = "main",
    code_lang: str = "python",
):
    """Add an issue to the repository."""

    prompt_generating_issue_from_code_lang = {
        "python":
        "You are a programmer of the highest caliber. Please read the code of the existing program and point out only one issue of whole code. Never refer to yourself as an AI assistant when doing so.",
        "tex":
        """Correct some files of the given paper.
概要の明確さ: 概要は研究の目的、方法、主な結果、および結論を明確に説明していますか？どのような点を改善できますか？

導入部: 研究の背景が十分に説明されており、研究の目的と重要性が明確ですか？研究問題の設定は適切ですか？

文献レビュー: 関連する研究が広範囲にわたってレビューされており、研究のギャップが明確に特定されていますか？どのように改善できるか提案してください。

研究方法: 研究方法は適切で詳細に説明されていますか？方法論の選択が研究目的に合っていますか？改善の余地はありますか？

結果: 研究結果は明確に提示され、適切に分析されていますか？図表やグラフは情報を効果的に伝えていますか？

議論: 結果の意味が深く分析され、研究の限界が考慮されていますか？結果は文献レビューで議論された以前の研究とどのように関連していますか？

結論: 研究の主な発見とその意義が明確にまとめられていますか？今後の研究に向けた提案が含まれていますか？

参考文献: 引用された文献は適切で、最新ですか？参考文献のフォーマットは一貫していますか？

文体と文法: 文章は明瞭で、文法的に正しいですか？専門用語は適切に使用されていますか？読みやすさを向上させるための提案はありますか？

全体的な印象: 論文全体として、研究の貢献とオリジナリティをどのように評価しますか？論文の強みと弱点は何ですか？"""
    }

    prompt_summarizing_issue_from_code_lang = {
        "python":
        "You are a programmer of the highest caliber. Please summarize the above GitHub issue text to one sentense as an issue title.",
        "tex":
        "You are a reviewer of the highest caliber. Please summarize the above issue text to one sentense as an issue title."
    }

    prompt_generating_issue = prompt_generating_issue_from_code_lang[code_lang]
    prompt_summarizing_issue = prompt_summarizing_issue_from_code_lang[
        code_lang]

    services.github.setup_repository(repo, branch)
    target_files = enumerate_target_files(repo, code_lang)
    messages = prepare_messages_from_files(target_files, "")
    issue_body = send_messages_to_system(
        messages,
        prompt_generating_issue,
    )
    issue_title = send_messages_to_system(
        [{
            "role": "assistant",
            "content": issue_body
        }],
        prompt_summarizing_issue,
    )
    issue_title = issue_title.strip().strip('"`').strip("'")
    services.github.create_issue(repo, issue_title, issue_body)


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

    services.github.setup_repository(repo, branch)
    issue = services.github.get_issue_by_id(repo, issue_id)
    if issue is None:
        log(f"Failed to retrieve issue with ID: {issue_id}", level="error")
        return None

    target_files = enumerate_target_files(repo, code_lang)
    messages = prepare_messages_from_files(target_files, "")
    messages = prepare_messages_from_issue(messages, issue)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and rewrite any one based on the issue.",
    )
    print(generated_text)
    return generated_text


def update_issue(
    issue_id: int,
    repo: str,
    branch: str = "main",
    code_lang: str = "python",
):
    """Update an issue with a comment."""

    services.github.setup_repository(repo, branch)
    issue = services.github.get_issue_by_id(repo, issue_id)

    if issue is None:
        log(f"Failed to retrieve issue with ID: {issue_id}", level="error")
        return

    target_files = enumerate_target_files(repo, code_lang)
    messages = prepare_messages_from_files(target_files, "")
    messages = prepare_messages_from_issue(messages, issue)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and make additional comments on the issue.",
    )
    services.github.reply_issue(repo, issue.id, generated_text)


def summarize_issue(
    issue_id: int,
    repo: str,
    branch: str = "main",
) -> bool:
    """Summarize an issue and add the summary as a comment to the issue."""
    services.github.setup_repository(repo, branch)
    issue = services.github.get_issue_by_id(repo, issue_id)
    if issue is None or issue.summary:
        log(
            f"Failed to retrieve issue or issue already summarized with ID: {issue_id}",
            level="error",
        )
        return False

    messages = prepare_messages_from_issue([], issue)

    # Message to the system for summarization instruction
    system_instruction = (
        "Please summarize the following issue and its discussion succinctly.")

    issue.summary = send_messages_to_system(messages, system_instruction)

    # Persist the summary back to the issue as a comment
    return services.github.reply_issue(repo, issue.id,
                                       f"Summary:\n{issue.summary}")


def generate_readme(
    repo: str,
    branch: str = "main",
    code_lang: str = "python",
) -> bool:
    """Generate README.md documentation for the entire program."""

    services.github.setup_repository(repo, branch)
    target_files = enumerate_target_files(repo, code_lang)

    # Initialize readme_content as empty string to handle the case when file doesn't exist
    readme_content = ""

    try:
        repo_path = "./downloads/" + repo
        with open(repo_path + "/README.md", "r") as file_object:
            readme_content = file_object.read()
    except FileNotFoundError:
        log(
            "README.md file does not exist. A new README.md will be created with generated content.",
            level="warning",
        )
        return False
    except OSError as err:
        # Catching any other OS-related errors (like file permission issues)
        # and displaying the error message to the user.
        log(f"Error while reading README.md: {err}", level="error")
        return False

    readme_message = f"```Current README.md\n{readme_content}```"
    messages = prepare_messages_from_files(target_files, readme_message)
    generated_text = send_messages_to_system(
        messages,
        "You are a programmer of the highest caliber.Please read the code of the existing program and generate README.md.",
    )

    # Checkout to the a new branch
    try:
        services.github.checkout_new_branch(repo, "update-readme")
    except FileNotFoundError as err:
        log(f"Error while checking out a new branch: {err}", level="error")
        return False
    except Exception as err:
        log(f"Error to checkout a new branch: {err}", level="error")
        return False

    # Attempt to write the README.md file.
    try:
        with open(repo_path + "/README.md", "w") as file_object:
            file_object.write(generated_text)
    except OSError as err:
        log(f"Error while writing to README.md: {err}", level="error")
        services.github.checkout_branch(repo, "main")
        return False

    # Commit the changes
    res = services.github.commit(repo, "Update README.md")
    if not res:
        return False
    res = services.github.push_repository(repo, "update-readme")
    if not res:
        return False
    services.github.checkout_branch(repo, "main")
    return True


def grow_grass(repo: str, branch: str = "main", code_lang: str = "python"):
    """Grow grass on GitHub contributions graph."""
    # 最後のコミットの日付を取得する
    last_commit_datetime = services.github.get_datetime_of_last_commit(
        repo, branch)
    if last_commit_datetime.date() == datetime.now().date():
        return
    # add_issueする
    add_issue(repo, branch, code_lang)
