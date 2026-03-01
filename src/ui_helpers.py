"""
UI関連のヘルパー関数モジュール
"""
import flet as ft
import os
import sys
from typing import Optional, Dict, Sequence
import logging
from constants import (
    WINDOW_WIDTH_DEFAULT,
    ICON_SIZE,
    LABEL_WIDTH,
    SCALE_RATIO_MIN,
    SCALE_RATIO_MAX,
    FONT_SIZE_SMALL_BASE,
    FONT_SIZE_NORMAL_BASE,
    FONT_SIZE_LARGE_BASE,
    LIST_VIEW_HEIGHT
)

logger = logging.getLogger(__name__)


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
            base_path = sys._MEIPASS
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
    # ウィンドウ幅を取得（デフォルト値を使用）
    window_width = page.window.width or WINDOW_WIDTH_DEFAULT

    # 基準サイズに対する比率を計算
    scale_ratio = window_width / WINDOW_WIDTH_DEFAULT

    # 最小・最大スケールを制限
    scale_ratio = max(SCALE_RATIO_MIN, min(SCALE_RATIO_MAX, scale_ratio))

    return {
        'font_size_small': int(FONT_SIZE_SMALL_BASE * scale_ratio),
        'font_size_normal': int(FONT_SIZE_NORMAL_BASE * scale_ratio),
        'font_size_large': int(FONT_SIZE_LARGE_BASE * scale_ratio),
        'icon_size': int(ICON_SIZE * scale_ratio),
        'label_width': int(LABEL_WIDTH * scale_ratio),
        'padding': int(10 * scale_ratio),
        'spacing': int(5 * scale_ratio),
        'list_view_height': int(LIST_VIEW_HEIGHT * scale_ratio),
    }


def create_label_value_row(
    label: str,
    value: str,
    label_width: float = LABEL_WIDTH,
    value_width: Optional[float] = None,
    font_size: int = 12
) -> ft.Row:
    """
    ラベルと値を含むRowを作成するヘルパー関数。

    Parameters:
        label (str): ラベルテキスト。
        value (str): 値テキスト。
        label_width (float): ラベル部分の固定幅。
        value_width (Optional[float]): 値部分の固定幅。デフォルトはNone。
        font_size (int): フォントサイズ。

    Returns:
        ft.Row: ラベルと値を含むRowオブジェクト。
    """
    return ft.Row([
        ft.Text(label, size=font_size, width=label_width,
                weight=ft.FontWeight.BOLD),
        ft.Text(value, size=font_size,
                width=value_width if value_width else None, expand=True)
    ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )


def create_card(
    title: str,
    content_controls: Sequence[ft.Control],
    icon_filename: str,
    layout: str = "single_column",
    icon_size: int = ICON_SIZE,
    font_size: int = 12,
    padding: int = 10,
    spacing: int = 5,
    col: Optional[Dict[str, int]] = None
) -> ft.Container:
    """
    汎用的なカードを作成するヘルパー関数。

    Parameters:
        title (str): カードのタイトル。
        content_controls (Sequence[ft.Control]): カード内のコンテンツコントロールのリスト。
        icon_filename (str): アイコンファイル名。
        layout (str): レイアウトタイプ（"single_column", "numbered"）。
        icon_size (int): アイコンサイズ。
        font_size (int): フォントサイズ。
        padding (int): パディング。
        spacing (int): スペーシング。
        col (Optional[Dict[str, int]]): ResponsiveRowのcolumn設定（レスポンシブ対応用）。

    Returns:
        ft.Container: カードを含むコンテナ（レスポンシブ対応）。
    """
    base_path = get_base_path()
    icon_path = os.path.join(base_path, "icons", icon_filename)

    if layout == "numbered":
        # numberedレイアウトの場合、content_controlsはList[List[Control]]形式
        flattened_controls = []
        for group in content_controls:
            if isinstance(group, (list, tuple)):
                flattened_controls.extend(group)
            else:
                flattened_controls.append(group)
        content = ft.Column(
            flattened_controls,
            spacing=int(spacing * 0.6),  # numberedの場合は少し狭く
        )
    else:
        content = ft.Column(
            list(content_controls),
            spacing=spacing,
        )

    card = ft.Container(
        content=ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Image(
                                src=icon_path,
                                width=icon_size,
                                height=icon_size,
                            ),
                            ft.Text(title, size=font_size,
                                    weight=ft.FontWeight.BOLD)
                        ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        content
                    ],
                    spacing=spacing
                ),
                padding=padding
            ),
            elevation=3,
        ),
        margin=ft.margin.symmetric(vertical=spacing, horizontal=5),
    )

    # colパラメータが指定されている場合は、ResponsiveRow用の設定を追加
    if col:
        card.col = col

    return card
