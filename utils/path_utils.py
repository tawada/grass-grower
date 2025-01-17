"""Utility functions for path operations."""

import os
from typing import TextIO, cast


def safe_join(*args: str) -> str:
    """パスコンポーネントを安全に結合します。"""
    return os.path.normpath(os.path.join(*args))


def validate_path(path: str) -> None:
    """パスが存在しアクセス可能かを検証します。"""
    if not os.path.exists(path):
        raise FileNotFoundError(f"パスが存在しません: {path}")


def safe_open(file_path: str, mode: str = 'r', **kwargs) -> TextIO:
    """ファイルを安全に開き、適切なエラー処理を確保します。"""
    try:
        validate_path(os.path.dirname(file_path))
        return cast(TextIO, open(file_path, mode, **kwargs))
    except FileNotFoundError:
        raise
    except PermissionError:
        raise
    except Exception as err:
        raise IOError(f"ファイル {file_path} へのアクセス中にエラーが発生しました: {err}") from err
