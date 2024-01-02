"""データ構造を定義するモジュール"""

from dataclasses import dataclass


@dataclass
class Issue:
    """Issueのデータ構造"""
    id: int
    title: str
    body: str
