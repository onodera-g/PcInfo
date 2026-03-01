# ui_components.py
"""
UI共通コンポーネント（カード、ラベル、診断タブレイアウトなど）
"""
import os
from typing import Optional, Sequence, Any, List
import flet as ft
from utils import get_base_path
from config import BUTTON_FONT_SIZE, LIST_VIEW_HEIGHT


def create_label_value_row(
    label: str, 
    value: str, 
    label_width: float, 
    font_size: int, 
    value_width: Optional[float] = None
) -> ft.Row:
    """
    ラベルと値を含むRowを作成するヘルパー関数。

    Parameters:
        label (str): ラベルテキスト。
        value (str): 値テキスト。
        label_width (float): ラベル部分の固定幅。
        font_size (int): フォントサイズ。
        value_width (Optional[float]): 値部分の固定幅。デフォルトはNone。

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
    icon_size: int, 
    font_size: int, 
    padding: int, 
    spacing: int,
    col: Optional[Any],
    layout: str = "single_column"
) -> ft.Container:
    """
    汎用的なカードを作成するヘルパー関数。

    Parameters:
        title (str): カードのタイトル。
        content_controls (List[ft.Control]): カード内のコンテンツコントロールのリスト。
        icon_filename (str): アイコンファイル名。
        icon_size (int): アイコンサイズ。
        font_size (int): フォントサイズ。
        padding (int): パディング。
        spacing (int): スペーシング。
        col (Optional[Any]): ResponsiveRowのcolumn設定（レスポンシブ対応用）。
        layout (str): レイアウトタイプ（"single_column", "numbered"）。デフォルトは"single_column"。

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


def create_diagnostic_tab_content(
    buttons: List[ft.ElevatedButton],
    list_view: ft.ListView,
    table_container: ft.Column
) -> ft.Column:
    """
    診断タブの共通レイアウトを作成する関数。
    
    Parameters:
        buttons (List[ft.ElevatedButton]): タブ上部に配置するボタンのリスト。
        list_view (ft.ListView): 診断ログ一覧を表示するListView。
        table_container (ft.Column): 選択されたログの詳細を表示するコンテナ。
    
    Returns:
        ft.Column: タブコンテンツのColumn。
    """
    return ft.Column(
        [
            ft.Container(height=5),
            ft.Row(buttons, spacing=10),
            ft.Text("診断ログ一覧:", size=BUTTON_FONT_SIZE, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=list_view,
                height=LIST_VIEW_HEIGHT,
                expand=True,
                border=ft.border.all(1.5, ft.Colors.GREY),
                padding=10,
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=table_container, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO
    )
