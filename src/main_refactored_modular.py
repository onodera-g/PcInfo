"""
PcInfo - PC情報診断ツール
メインアプリケーション
"""

import flet as ft
import diagnostics
from typing import Optional

from constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    CARD_WIDTH,
    LIST_VIEW_HEIGHT
)
from ui import (
    display_system_info,
    display_storage_diagnostics,
    display_storage_diagnostics_with_dialog,
    display_memory_diagnostics
)


def main(page: ft.Page) -> None:
    """
    Fletアプリケーションのメイン関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
    """
    # ページの設定
    page.title = "PcInfo"
    page.padding = 20
    page.window.width = WINDOW_WIDTH
    page.window.height = WINDOW_HEIGHT

    # 選択されたログファイル名を保持する変数
    selected_storage_log = ft.Ref[str]()
    selected_memory_log = ft.Ref[str]()

    # メモリ診断用のUI要素
    memory_list_view = ft.ListView(expand=True)
    memory_table_container = ft.Column(
        controls=[ft.Text("ここにメモリ診断ログの詳細が表示されます。", size=12)]
    )

    # ストレージ診断用のUI要素
    storage_list_view = ft.ListView(expand=True)
    storage_table_container = ft.Column(
        controls=[ft.Text("ここに選択されたログの詳細が表示されます。", size=12)]
    )

    # PC情報用のコンテナ
    system_info_container = ft.Column(controls=[])

    # タブ1: PC情報
    tab1_content = ft.Column(
        [
            ft.Container(height=5),
            ft.ElevatedButton(
                content=ft.Text("PC構成の取得", size=12),
                on_click=lambda e: display_system_info(
                    page, system_info_container),
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=system_info_container, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ2: メモリ診断
    tab2_content = ft.Column(
        [
            ft.Container(height=5),
            ft.Row(
                [
                    ft.ElevatedButton(
                        content=ft.Text("メモリ診断結果の表示", size=12),
                        on_click=lambda e: display_memory_diagnostics(
                            page, memory_list_view, memory_table_container, selected_memory_log
                        ),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("Windowsメモリ診断の実行", size=12),
                        on_click=lambda e: diagnostics.run_memory_diagnostics(),
                    ),
                ],
                spacing=10
            ),
            ft.Text("診断ログ一覧:", size=12, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=memory_list_view,
                height=LIST_VIEW_HEIGHT,
                width=CARD_WIDTH,
                border=ft.border.all(1.5, ft.Colors.GREY),
                padding=10,
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=memory_table_container, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ3: ストレージ診断
    tab3_content = ft.Column(
        [
            ft.Container(height=5),
            ft.Row(
                [
                    ft.ElevatedButton(
                        content=ft.Text("診断結果の表示", size=12),
                        on_click=lambda e: display_storage_diagnostics(
                            page, storage_list_view, storage_table_container, selected_storage_log
                        ),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("S.M.A.R.T.の取得", size=12),
                        on_click=lambda e: display_storage_diagnostics_with_dialog(
                            page),
                    ),
                ],
                spacing=10
            ),
            ft.Text("診断ログ一覧:", size=12, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=storage_list_view,
                height=LIST_VIEW_HEIGHT,
                width=CARD_WIDTH,
                border=ft.border.all(1.5, ft.Colors.GREY),
                padding=10,
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=storage_table_container, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ構成
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="PC情報", content=tab1_content),
            ft.Tab(text="メモリ診断", content=tab2_content),
            ft.Tab(text="ストレージ診断", content=tab3_content),
        ],
        expand=True,
    )

    # ページに追加
    page.add(tabs)


# Fletアプリケーションの実行
if __name__ == "__main__":
    ft.app(target=main)
