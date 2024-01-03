from pathlib import Path

from services import (
    generate_text,
    get_issue,
    reply_issue,
)


def update_issue():
    """issueにコメントを追加する"""

    issue = get_issue()
    if issue is None:
        print("issueが取得できませんでした")
        return
    print(issue)

    messages = []

    # 既存の拡張子.pyのファイルをすべて列挙する
    for file in Path(".").glob("**/*.py"):
        with open(file, "r") as f:
            message = "```" + file.name + "\n"
            message += f.read() + "```"
            messages.append(
                {
                    "role": "user",
                    "content": message,
                }
            )

    # issueをpromptに追加する
    message = "```" + issue.title + "\n"
    message += issue.body + "```\n"
    messages.append(
        {
            "role": "user",
            "content": message,
        }
    )

    message = "You are a programmer of the highest caliber.Please read the code of the existing program and make additional comments on the issue."
    messages.append(
        {
            "role": "system",
            "content": message,
        }
    )

    generated_text = generate_text(messages)
    print(generated_text)

    reply_issue(issue.id, generated_text)


def generate_readme():
    """プログラム全体を見てREADME.mdを生成する"""

    messages = []

    # 既存の拡張子.pyのファイルをすべて列挙する
    for file in Path(".").glob("**/*.py"):
        with open(file, "r") as f:
            message = "```" + str(file) + "\n"
            message += f.read() + "```"
            messages.append(
                {
                    "role": "user",
                    "content": message,
                }
            )
    with open("README.md", "r") as f:
        message = "```Current README.md\n"
        message += f.read() + "```"
        messages.append(
            {
                "role": "user",
                "content": message,
            }
        )
    message = "You are a programmer of the highest caliber.Please read the code of the existing program and generate README.md."
    messages.append(
        {
            "role": "system",
            "content": message,
        }
    )
    generated_text = generate_text(messages)
    print(generated_text)

    with open("README.md", "w") as f:
        f.write(generated_text)
