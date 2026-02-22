"""
共通ユーティリティモジュール
"""

import os
import sys
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def get_base_path() -> str:
    """
    リソースファイル（icons等）へのパスを取得します。
    PyInstallerでコンパイルされた場合でも対応します。

    ワンファイル形式: sys._MEIPASS (一時展開フォルダ)
    ワンフォルダ形式: 実行ファイルのディレクトリ
    開発環境: src/ ディレクトリ

    Returns:
        str: リソースファイルへのベースパス。
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでコンパイルされた場合
        if hasattr(sys, '_MEIPASS'):
            # ワンファイル形式: リソースファイルは _MEIPASS に展開される
            base_path = sys._MEIPASS
        else:
            # ワンフォルダ形式
            base_path = os.path.dirname(sys.executable)
    else:
        # 開発環境の場合: このファイルは src/utils/common.py なので、src/ を返す
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger.debug(f"Base path (resources): {base_path}")
    return base_path


def get_executable_dir() -> str:
    """
    実行ファイルがあるディレクトリを取得します。
    ログファイルや CrystalDiskInfo などの永続的なデータの保存先に使用します。

    Returns:
        str: 実行ファイルのディレクトリパス。
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでコンパイルされた場合: 実行ファイルのディレクトリ
        exe_dir = os.path.dirname(sys.executable)
    else:
        # 開発環境の場合: src/ ディレクトリ
        exe_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    logger.debug(f"Executable directory: {exe_dir}")
    return exe_dir


def get_log_path(log_filename: str) -> str:
    """
    ログファイルのフルパスを取得します。
    ログファイルは実行ファイルと同じディレクトリの log/ に保存されます。

    Parameters:
        log_filename (str): ログファイル名。

    Returns:
        str: ログファイルのフルパス。
    """
    exe_dir = get_executable_dir()
    log_folder = os.path.join(exe_dir, "log")
    os.makedirs(log_folder, exist_ok=True)  # log フォルダが存在しない場合は作成
    return os.path.join(log_folder, log_filename)


def get_icon_path(icon_filename: str) -> str:
    """
    アイコンファイルのフルパスを取得します。

    Parameters:
        icon_filename (str): アイコンファイル名。

    Returns:
        str: アイコンファイルのフルパス。
    """
    base_path = get_base_path()
    return os.path.join(base_path, "icons", icon_filename)
