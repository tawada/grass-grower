"""
アプリケーション全体のロギング設定を管理するモジュール。
アプリケーション起動時に自動的にロギングを設定します。
"""

from loguru import logger


def setup_logging():
    """プロジェクトのロギング設定"""
    logger.remove()  # デフォルトハンドラーを削除
    logger.add(
        "debug.log",  # ログファイルパス
        rotation="100 MB",  # 100MBごとに新しいファイルを作成
        retention="10 days",  # 10日以上経過したログを削除
        level="INFO",
    )
    logger.add(
        sink=lambda msg: print(msg, flush=True),
        format="{time} - {level} - {message}",
        level="INFO",
    )


setup_logging()  # モジュールのインポート時に即座に初期化
