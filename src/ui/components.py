"""
UI コンポーネントモジュール
"""

import flet as ft
from typing import Optional, List

from constants import (
    LABEL_WIDTH,
    ICON_SIZE,
    CARD_WIDTH,
    ANIMATION_DURATION
)
from utils import get_icon_path


def create_label_value_row(
    label: str,
    value: str,
    label_width: float = LABEL_WIDTH,
    value_width: Optional[float] = None
) -> ft.Row:
    """
    ラベルと値を含むRowを作成する。

    Parameters:
        label (str): ラベルテキスト。
        value (str): 値テキスト。
        label_width (float): ラベル部分の固定幅。
        value_width (Optional[float]): 値部分の固定幅。デフォルトはNone。

    Returns:
        ft.Row: ラベルと値を含むRowオブジェクト。
    """
    return ft.Row([
        ft.Text(label, size=12, width=label_width, weight=ft.FontWeight.BOLD),
        ft.Text(value, size=12, width=value_width if value_width else None)
    ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )


def create_card(
    title: str,
    content_controls: List[ft.Control],
    icon_filename: str,
    width: float = CARD_WIDTH,
    layout: str = "single_column"
) -> ft.Container:
    """
    汎用的なカードを作成する。

    Parameters:
        title (str): カードのタイトル。
        content_controls (List[ft.Control]): カード内のコンテンツコントロールのリスト。
        icon_filename (str): アイコンファイル名。
        width (float): カードの横幅。
        layout (str): レイアウトタイプ（"single_column", "numbered"）。

    Returns:
        ft.Container: 作成されたカードのコンテナ。
    """
    icon_path = get_icon_path(icon_filename)

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
            spacing=3,
            expand=True
        )
    else:
        content = ft.Column(
            list(content_controls),
            spacing=5,
            expand=True
        )

    return ft.Container(
        width=width,
        content=ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Image(
                                src=icon_path,
                                width=ICON_SIZE,
                                height=ICON_SIZE,
                            ),
                            ft.Text(title, size=12, weight=ft.FontWeight.BOLD)
                        ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        content
                    ],
                    spacing=5
                ),
                padding=10
            ),
            elevation=3,
            margin=ft.margin.symmetric(vertical=5),
        ),
        animate=ANIMATION_DURATION,
    )
