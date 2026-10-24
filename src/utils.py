# utils.py
"""
ユーティリティ関数（パス取得、権限確認、レスポンシブサイズ計算など）
"""
import os
import sys
import ctypes
import logging
from typing import Dict, Tuple
import flet as ft

# ロガーの設定
logger = logging.getLogger(__name__)


def is_admin() -> bool:
    """
    現在のプロセスが管理者権限で実行されているかを確認します。

    Returns:
        bool: 管理者権限で実行されている場合True、そうでない場合False。
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logger.error(f"管理者権限の確認に失敗しました: {e}")
        return False


def get_base_path() -> str:
    """
    実行ファイルのディレクトリを取得します。
    PyInstallerでコンパイルされた場合でも対応します。

    ワンファイル形式の場合: sys._MEIPASS (リソースファイル用)

    Returns:
        str: 実行ファイルのディレクトリパス。
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでコンパイルされた場合
        if hasattr(sys, '_MEIPASS'):
            # ワンファイル形式: リソースファイルは _MEIPASS に展開される
            base_path = sys._MEIPASS  # type: ignore
        else:
            # ワンフォルダ形式
            base_path = os.path.dirname(sys.executable)
    else:
        # 開発環境の場合
        base_path = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Base path (for resources): {base_path}")
    return base_path


def get_executable_dir() -> str:
    """
    実行ファイルがあるディレクトリを取得します。
    ログファイルなどの永続的なデータの保存先に使用します。

    Returns:
        str: 実行ファイルのディレクトリパス。
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでコンパイルされた場合: 実行ファイルのディレクトリ
        exe_dir = os.path.dirname(sys.executable)
    else:
        # 開発環境の場合
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Executable directory (for logs): {exe_dir}")
    return exe_dir


def get_responsive_sizes(page: ft.Page) -> Dict[str, int]:
    """
    ウィンドウサイズに応じたレスポンシブなサイズを計算します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。

    Returns:
        Dict[str, int]: 各UI要素のサイズを含む辞書。
    """
    # ウィンドウを狭めても本文を縮小せず、カードの列数と折り返しで調整する。
    return {
        'font_size_small': 12,
        'font_size_normal': 14,
        'font_size_large': 15,
        'icon_size': 24,
        'label_width': 152,
        'padding': 16,
        'spacing': 8,
        'list_view_height': 150,
    }


def get_ui_sizes(page: ft.Page) -> Tuple[int, int, int, int, int, Dict[str, int]]:
    """
    UIサイズをまとめて取得するヘルパー関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。

    Returns:
        tuple: (font_size, icon_size, label_width, padding, spacing, col_config)
    """
    sizes = get_responsive_sizes(page)
    font_size = sizes['font_size_normal']
    icon_size = sizes['icon_size']
    label_width = sizes['label_width']
    padding = sizes['padding']
    spacing = sizes['spacing']
    col_config = {"xs": 12, "sm": 12, "md": 12, "lg": 6, "xl": 6, "xxl": 6}

    return font_size, icon_size, label_width, padding, spacing, col_config
