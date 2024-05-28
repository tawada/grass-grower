"""Module to define data structures"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class IssueComment:
    """Data structure for an issue comment"""

    author: str
    association: str
    edited: str
    status: str
    body: str


@dataclass
class Issue:
    """Data structure for an issue"""

    id: int
    title: str
    body: str
    comments: List[IssueComment] = field(default_factory=list)
    summary: str = ""
