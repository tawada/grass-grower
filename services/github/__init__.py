import subprocess

from schemas import Issue


def create_issue(title: str, body: str) -> None:
    """issueを追加する"""

    try:
        res = subprocess.run(
            ["gh", "issue", "create", "-t", title, "-b", body],
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        print(e)
        return None
    print(res)


def get_issue() -> Issue:
    """issueを取得する"""

    try:
        res = subprocess.run(
            ["gh", "issue", "list"],
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        print(e)
        return None

    issue_row = res.stdout.decode().split("\t")
    # 先頭の1個目のissue_idを取得
    issue_id = int(issue_row[0])
    return get_issue_by_id(issue_id)


def get_issue_by_id(issue_id: int) -> Issue:
    """idからissueを取得する"""

    try:
        res = subprocess.run(
            ["gh", "issue", "view", str(issue_id)],
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        print(e)
        return None

    is_body = False
    body = ""
    for line in res.stdout.decode().splitlines():
        if is_body:
            body += line + "\n"
        elif line.startswith("title:\t"):
            title = line[len("title:\t"):]
        elif line.startswith("--"):
            is_body = True

    return Issue(
        id=issue_id,
        title=title,
        body=body,
    )


def reply_issue(issue_id: int, body: str) -> None:
    """issueに返信する"""

    try:
        res = subprocess.run(
            ["gh", "issue", "comment", str(issue_id), "-b", body],
            stdout=subprocess.PIPE,
        )
    except Exception as e:
        print(e)
        return None
    print(res)
