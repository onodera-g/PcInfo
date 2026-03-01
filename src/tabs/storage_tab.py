# tabs/storage_tab.py

import flet as ft
import os
import logging
from datetime import datetime
from typing import Optional
import storage_diagnostics
from config import DIALOG_FONT_SIZE
from utils import get_executable_dir
import utils
from ui_components import create_card, create_label_value_row
from dialogs import show_loading_dialog, hide_loading_dialog, close_dialog, show_success_dialog, show_error_dialog

logger = logging.getLogger(__name__)


def display_storage_diagnostics(
    page: ft.Page, storage_list_view: ft.ListView, storage_table_container: ft.Column, selected_storage_log: ft.Ref[str]
) -> None:
    """
    ストレージ診断ログのリストを取得し、選択されたログを詳細表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        storage_list_view (ft.ListView): ストレージ診断ログのリストビュー。
        storage_table_container (ft.Column): 選択されたログの詳細を表示するコンテナ。
        selected_storage_log (ft.Ref[str]): 選択されたログファイル名を保持する参照。
    """
    results = storage_diagnostics.search_storage_log()  # 診断結果を取得
    storage_list_view.controls.clear()

    # レスポンシブサイズを取得
    font_size, _, _, _, _, _ = utils.get_ui_sizes(page)

    if not results:
        storage_list_view.controls.append(
            ft.Text("ログファイルが存在しません。", size=font_size))
    else:
        for result in results:
            storage_list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(result, size=font_size),
                    on_click=lambda e, res=result: (
                        display_storage_log_content(
                            page, res, storage_table_container
                        ),
                        setattr(selected_storage_log, 'current', res),
                        page.update()
                    ),
                    selected=(selected_storage_log.current == result),
                    selected_color=ft.Colors.BLUE,
                )
            )  # クリックで詳細を表示する
    page.update()


def display_storage_log_content(
    page: ft.Page, log_filename: str, storage_table_container: ft.Column
) -> None:
    """
    選択したログファイルの内容を詳細表示する

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        log_filename (str): 選択されたログファイル名。
        storage_table_container (ft.Column): 詳細を表示するコンテナ。
    """
    disk_data = storage_diagnostics.get_storage_info(log_filename)
    logger.debug(f"Storage Log Content: {disk_data}")

    # レスポンシブサイズを取得
    font_size, icon_size, label_width, padding, spacing, col_config = utils.get_ui_sizes(
        page)

    storage_table_container.controls.clear()
    if not disk_data:
        storage_table_container.controls.append(
            ft.Text("ログファイルの内容を読み込めませんでした。", size=font_size)
        )
    else:
        storage_cards = []
        for idx, disk in enumerate(disk_data, start=1):
            model_number = disk.get('Model', 'Unknown')

            storage_card = create_card(
                title=f"ディスク{idx}: {model_number}",
                content_controls=[
                    create_label_value_row(
                        "Disk Size:",
                        disk.get('Disk Size', 'Unknown'),
                        label_width,
                        font_size
                    ),
                    create_label_value_row(
                        "Interface:",
                        disk.get('Interface', 'Unknown'),
                        label_width,
                        font_size
                    ),
                    create_label_value_row(
                        "Power On Hours:",
                        disk.get('Power On Hours', 'Unknown'),
                        label_width,
                        font_size
                    ),
                    create_label_value_row(
                        "Power On Count:",
                        disk.get('Power On Count', 'Unknown'),
                        label_width,
                        font_size
                    ),
                    create_label_value_row(
                        "Host Writes:",
                        disk.get('Host Writes', 'Unknown'),
                        label_width,
                        font_size
                    ),
                    create_label_value_row(
                        "Health Status:",
                        disk.get('Health Status', 'Unknown'),
                        label_width,
                        font_size
                    ),
                ],
                icon_filename="disk.png",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
            storage_cards.append(storage_card)

        responsive_row = ft.ResponsiveRow(storage_cards, spacing=10)
        storage_table_container.controls.append(responsive_row)
    page.update()


def display_storage_diagnostics_with_dialog(page: ft.Page) -> None:
    """
    ストレージ診断を実行し、結果をダイアログで表示する関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
    """
    # ローディングインジケーターを表示
    loading_dialog = show_loading_dialog(page)

    try:
        result, error_message = storage_diagnostics.get_CrystalDiskInfo_log()  # ストレージ診断を実行
        if result:
            # 成功時のダイアログ
            show_success_dialog(page, "ストレージ診断が実行され、ログが保存されました。")
        else:
            # 失敗時のダイアログ(詳細なエラーメッセージを表示)
            show_error_dialog(
                page,
                "エラー",
                "ストレージ診断の実行に失敗しました。",
                error_message if error_message else "不明なエラーが発生しました。"
            )

    except Exception as e:
        # エラーダイアログを表示
        logger.exception("ストレージ診断の実行中にエラーが発生しました。")
        show_error_dialog(page, "エラー", "ストレージ診断の実行中にエラーが発生しました。", str(e))
    finally:
        # ローディングインジケーターを閉じる
        hide_loading_dialog(page, loading_dialog)
