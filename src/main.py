# main.py

import flet as ft
import diagnostics
from typing import Optional
import logging

# 共通モジュールからインポート
from config import (
    WINDOW_WIDTH_DEFAULT, WINDOW_HEIGHT_DEFAULT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    DIALOG_FONT_SIZE, BUTTON_FONT_SIZE
)
from utils import is_admin
from ui_components import create_diagnostic_tab_content

# タブモジュールからインポート
from tabs.system_info_tab import display_system_info
from tabs.storage_tab import (
    display_storage_diagnostics,
    display_storage_diagnostics_with_dialog
)
from tabs.memory_tab import display_memory_diagnostics
from tabs.gpu_tab import display_gpu_log_list, display_gpu_diagnostics

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def main(page: ft.Page) -> None:
    """
    Fletアプリケーションのメイン関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
    """
    # 管理者権限の確認とログ記録
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

    # メモリ診断用のコンポーネント
    memory_list_view = ft.ListView(expand=True)
    memory_table_container = ft.Column(
        controls=[ft.Text("ここにメモリ診断ログの詳細が表示されます。", size=DIALOG_FONT_SIZE)],
        expand=True,
    )

    # ストレージ診断用のコンポーネント
    storage_list_view = ft.ListView(expand=True)
    storage_table_container = ft.Column(
        controls=[ft.Text("ここに選択されたログの詳細が表示されます。", size=DIALOG_FONT_SIZE)],
        expand=True,
    )

    # GPU診断用のコンポーネント
    gpu_list_view = ft.ListView(expand=True)
    gpu_table_container = ft.Column(
        controls=[ft.Text("ここにGPU診断ログの詳細が表示されます。", size=DIALOG_FONT_SIZE)],
        expand=True,
    )

    # PC情報用のコンテナ
    system_info_container = ft.Column(
        controls=[],
        expand=True,
    )

    # タブ1の内容（PC情報）
    tab1_content = ft.Column(
        [
            ft.Container(height=5),
            ft.ElevatedButton(
                content=ft.Text("PC構成の取得", size=BUTTON_FONT_SIZE),
                on_click=lambda e: display_system_info(
                    page, system_info_container),
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(
                content=system_info_container,
                expand=True,
            ),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ2の内容（メモリ診断）
    memory_buttons = [
        ft.ElevatedButton(
            content=ft.Text("メモリ診断結果の表示", size=BUTTON_FONT_SIZE),
            on_click=lambda e: display_memory_diagnostics(
                page, memory_list_view, memory_table_container, selected_memory_log
            ),
        ),
        ft.ElevatedButton(
            content=ft.Text("Windowsメモリ診断の実行", size=BUTTON_FONT_SIZE),
            on_click=lambda e: diagnostics.run_memory_diagnostics(),
        ),
    ]
    tab2_content = create_diagnostic_tab_content(
        buttons=memory_buttons,
        list_view=memory_list_view,
        table_container=memory_table_container
    )

    # タブ3(ストレージ診断)
    storage_buttons = [
        ft.ElevatedButton(
            content=ft.Text("診断結果の表示", size=BUTTON_FONT_SIZE),
            on_click=lambda e: display_storage_diagnostics(
                page, storage_list_view, storage_table_container, selected_storage_log
            ),
        ),
        ft.ElevatedButton(
            content=ft.Text("S.M.A.R.T.の取得", size=BUTTON_FONT_SIZE),
            on_click=lambda e: display_storage_diagnostics_with_dialog(page),
        ),
    ]
    tab3_content = create_diagnostic_tab_content(
        buttons=storage_buttons,
        list_view=storage_list_view,
        table_container=storage_table_container
    )

    # タブ4(GPU診断)
    gpu_buttons = [
        ft.ElevatedButton(
            content=ft.Text("診断結果の表示", size=BUTTON_FONT_SIZE),
            on_click=lambda e: display_gpu_log_list(
                page, gpu_list_view, gpu_table_container, selected_gpu_log
            ),
        ),
        ft.ElevatedButton(
            content=ft.Text("GPU情報の取得", size=BUTTON_FONT_SIZE),
            on_click=lambda e: display_gpu_diagnostics(
                page, gpu_list_view, gpu_table_container, selected_gpu_log
            ),
        ),
    ]
    tab4_content = create_diagnostic_tab_content(
        buttons=gpu_buttons,
        list_view=gpu_list_view,
        table_container=gpu_table_container
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

    # ページ構成
    page.add(tabs)


# Fletアプリケーションの実行
ft.app(target=main)
