"""
ストレージ診断UI関連の処理モジュール
"""
import flet as ft
import os
import logging
from typing import Optional
import storage_diagnostics
from constants import get_responsive_col_config
from ui_helpers import get_base_path, get_responsive_sizes, create_label_value_row
from dialog_helpers import (
    show_loading_dialog,
    hide_loading_dialog,
    show_success_dialog,
    show_error_dialog
)

logger = logging.getLogger(__name__)


def display_storage_diagnostics(
    page: ft.Page,
    storage_list_view: ft.ListView,
    storage_table_container: ft.Column,
    selected_storage_log: ft.Ref[str]
) -> None:
    """
    ストレージ診断ログのリストを取得し、選択されたログを詳細表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        storage_list_view (ft.ListView): ストレージ診断ログのリストビュー。
        storage_table_container (ft.Column): 選択されたログの詳細を表示するコンテナ。
        selected_storage_log (ft.Ref[str]): 選択されたログファイル名を保持する参照。
    """
    results = storage_diagnostics.search_storage_log()
    storage_list_view.controls.clear()

    sizes = get_responsive_sizes(page)
    font_size = sizes['font_size_normal']

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
            )
    page.update()


def display_storage_log_content(
    page: ft.Page,
    log_filename: str,
    storage_table_container: ft.Column
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

    sizes = get_responsive_sizes(page)
    font_size = sizes['font_size_normal']
    icon_size = sizes['icon_size']
    label_width = sizes['label_width']
    padding = sizes['padding']
    spacing = sizes['spacing']

    storage_table_container.controls.clear()
    if not disk_data:
        storage_table_container.controls.append(
            ft.Text("ログファイルの内容を読み込めませんでした。", size=font_size)
        )
    else:
        base_path = get_base_path()
        icon_path = os.path.join(base_path, "icons", "disk.png")

        storage_cards = []
        for idx, disk in enumerate(disk_data, start=1):
            model_number = disk.get('Model', 'Unknown')

            storage_card = ft.Container(
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
                                    ft.Text(
                                        f"ディスク{idx}: {model_number}",
                                        size=font_size,
                                        weight=ft.FontWeight.BOLD
                                    )
                                ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                create_label_value_row(
                                    "Disk Size:",
                                    disk.get('Disk Size', 'Unknown'),
                                    label_width=label_width,
                                    font_size=font_size
                                ),
                                create_label_value_row(
                                    "Interface:",
                                    disk.get('Interface', 'Unknown'),
                                    label_width=label_width,
                                    font_size=font_size
                                ),
                                create_label_value_row(
                                    "Power On Hours:",
                                    disk.get('Power On Hours', 'Unknown'),
                                    label_width=label_width,
                                    font_size=font_size
                                ),
                                create_label_value_row(
                                    "Power On Count:",
                                    disk.get('Power On Count', 'Unknown'),
                                    label_width=label_width,
                                    font_size=font_size
                                ),
                                create_label_value_row(
                                    "Host Writes:",
                                    disk.get('Host Writes', 'Unknown'),
                                    label_width=label_width,
                                    font_size=font_size
                                ),
                                create_label_value_row(
                                    "Health Status:",
                                    disk.get('Health Status', 'Unknown'),
                                    label_width=label_width,
                                    font_size=font_size
                                ),
                            ],
                            spacing=spacing
                        ),
                        padding=padding
                    ),
                    elevation=3,
                ),
                margin=ft.margin.symmetric(vertical=spacing, horizontal=5),
                col=get_responsive_col_config()
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
    loading_dialog = show_loading_dialog(page)

    try:
        result, error_message = storage_diagnostics.get_CrystalDiskInfo_log()
        if result:
            show_success_dialog(page, "ストレージ診断が実行され、ログが保存されました。")
        else:
            show_error_dialog(
                page,
                "エラー",
                "ストレージ診断の実行に失敗しました。",
                error_message if error_message else "不明なエラーが発生しました。"
            )

    except Exception as e:
        logger.exception("ストレージ診断の実行中にエラーが発生しました。")
        show_error_dialog(page, "エラー", "ストレージ診断の実行中にエラーが発生しました。", str(e))
    finally:
        hide_loading_dialog(page, loading_dialog)
