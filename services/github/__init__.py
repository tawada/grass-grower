import logging
import subprocess

from schemas import Issue


logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


def create_issue(title: str, body: str) -> None:
    """Create a new issue on GitHub."""
    try:
        logger.info(f"Creating issue with title: {title}")
        res = subprocess.run(
            ["gh", "issue", "create", "-t", title, "-b", body],
            stdout=subprocess.PIPE,
        )
        logger.info(f"Issue created successfully: {res.stdout}")
    except Exception as e:
        logger.error(f"Failed to create issue: {e}")
        return None


def get_issue() -> Issue:
    """issueを取得する"""

    try:
        logger.info("Listing issues")
        res = subprocess.run(
            ["gh", "issue", "list"],
            stdout=subprocess.PIPE,
        )
        logger.info("Issue listed successfully")
    except Exception as e:
        logger.error(f"Failed to list issues: {e}")
        return None

    issue_row = res.stdout.decode().split("\t")
    # 先頭の1個目のissue_idを取得
    issue_id = int(issue_row[0])
    return get_issue_by_id(issue_id)


def get_issue_by_id(issue_id: int) -> Issue:
    """idからissueを取得する"""

    try:
        logger.info(f"Getting issue with id: {issue_id}")
        res = subprocess.run(
            ["gh", "issue", "view", str(issue_id)],
            stdout=subprocess.PIPE,
        )
        logger.info("Issue had successfully")
    except Exception as e:
        logger.error(f"Failed to get issue: {e}")
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
        logger.info(f"Replying issue with id: {issue_id}")
        res = subprocess.run(
            ["gh", "issue", "comment", str(issue_id), "-b", body],
            stdout=subprocess.PIPE,
        )
        logger.info(f"Issue commented successfully: {res.stdout}")
    except Exception as e:
        logger.error(f"Failed to get issue: {e}")
        return None
