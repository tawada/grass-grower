"""データ構造を定義するモジュール"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class IssueComment:
    """IssueCommentのデータ構造"""
    author: str
    association: str
    edited: str
    status: str
    body: str


@dataclass
class Issue:
    """Issueのデータ構造"""
    id: int
    title: str
    body: str
    comments: List[IssueComment] = field(default_factory=list)
    summary: str = ""
