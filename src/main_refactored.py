# main.py

import flet as ft
import ctypes
import logging
from typing import Sequence
import diagnostics
from constants import (
    WINDOW_WIDTH_DEFAULT,
    WINDOW_HEIGHT_DEFAULT,
    WINDOW_MIN_WIDTH,
    WINDOW_MIN_HEIGHT,
    LIST_VIEW_HEIGHT
)
from ui_helpers import get_responsive_sizes
from storage_ui import (
    display_storage_diagnostics,
    display_storage_diagnostics_with_dialog
)
from memory_ui import display_memory_diagnostics
from gpu_ui import display_gpu_diagnostics, display_gpu_log_list
from system_info_ui import display_system_info

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


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


def create_tab_content(
    title: str,
    buttons: Sequence[ft.Control],
    list_view: ft.ListView,
    table_container: ft.Column
) -> ft.Column:
    """
    タブコンテンツを作成する汎用関数。

    Parameters:
        title (str): リストビューのタイトル
        buttons (list[ft.Control]): ボタンのリスト
        list_view (ft.ListView): 診断ログのリストビュー
        table_container (ft.Column): 詳細を表示するコンテナ

    Returns:
        ft.Column: タブコンテンツ
    """
    return ft.Column(
        [
            ft.Container(height=5),
            ft.Row(buttons, spacing=10),
            ft.Text(title, size=12, weight=ft.FontWeight.BOLD),
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


def main(page: ft.Page) -> None:
    """
    Fletアプリケーションのメイン関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
    """
    # 管理者権限の確認
    admin_status = is_admin()
    if admin_status:
        logger.info("アプリケーションは管理者権限で実行されています。")
        admin_text = " (管理者)"
    else:
        logger.info("アプリケーションは標準ユーザー権限で実行されています。")
        admin_text = ""

    # ページの設定
    page.title = f"PcInfo{admin_text}"
    page.padding = 20
    page.window.width = WINDOW_WIDTH_DEFAULT
    page.window.height = WINDOW_HEIGHT_DEFAULT
    page.window.min_width = WINDOW_MIN_WIDTH
    page.window.min_height = WINDOW_MIN_HEIGHT
    page.window.resizable = True

    # 選択されたログファイル名を保持する変数
    selected_storage_log = ft.Ref[str]()
    selected_memory_log = ft.Ref[str]()
    selected_gpu_log = ft.Ref[str]()

    # 各診断用の ListView と TableContainer
    memory_list_view = ft.ListView(expand=True)
    memory_table_container = ft.Column(
        controls=[ft.Text("ここにメモリ診断ログの詳細が表示されます。", size=12)],
        expand=True,
    )

    storage_list_view = ft.ListView(expand=True)
    storage_table_container = ft.Column(
        controls=[ft.Text("ここに選択されたログの詳細が表示されます。", size=12)],
        expand=True,
    )

    gpu_list_view = ft.ListView(expand=True)
    gpu_table_container = ft.Column(
        controls=[ft.Text("ここにGPU診断ログの詳細が表示されます。", size=12)],
        expand=True,
    )

    system_info_container = ft.Column(
        controls=[],
        expand=True,
    )

    # タブ1: PC情報
    tab1_content = ft.Column(
        [
            ft.Container(height=5),
            ft.ElevatedButton(
                content=ft.Text("PC構成の取得", size=12),
                on_click=lambda e: display_system_info(
                    page, system_info_container
                ),
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(
                content=system_info_container,
                expand=True,
            ),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ2: メモリ診断
    memory_buttons = [
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
    ]
    tab2_content = create_tab_content(
        "診断ログ一覧:",
        memory_buttons,
        memory_list_view,
        memory_table_container
    )

    # タブ3: ストレージ診断
    storage_buttons = [
        ft.ElevatedButton(
            content=ft.Text("診断結果の表示", size=12),
            on_click=lambda e: display_storage_diagnostics(
                page, storage_list_view, storage_table_container, selected_storage_log
            ),
        ),
        ft.ElevatedButton(
            content=ft.Text("S.M.A.R.T.の取得", size=12),
            on_click=lambda e: display_storage_diagnostics_with_dialog(page),
        ),
    ]
    tab3_content = create_tab_content(
        "診断ログ一覧:",
        storage_buttons,
        storage_list_view,
        storage_table_container
    )

    # タブ4: GPU診断
    gpu_buttons = [
        ft.ElevatedButton(
            content=ft.Text("診断結果の表示", size=12),
            on_click=lambda e: display_gpu_log_list(
                page, gpu_list_view, gpu_table_container, selected_gpu_log
            ),
        ),
        ft.ElevatedButton(
            content=ft.Text("GPU情報の取得", size=12),
            on_click=lambda e: display_gpu_diagnostics(
                page, gpu_list_view, gpu_table_container, selected_gpu_log
            ),
        ),
    ]
    tab4_content = create_tab_content(
        "診断ログ一覧:",
        gpu_buttons,
        gpu_list_view,
        gpu_table_container
    )

    # タブ構成
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="PC情報", content=tab1_content),
            ft.Tab(text="メモリ診断", content=tab2_content),
            ft.Tab(text="ストレージ診断", content=tab3_content),
            ft.Tab(text="GPU診断", content=tab4_content),
        ],
        expand=True,
    )

    page.add(tabs)


# Fletアプリケーションの実行
ft.app(target=main)
