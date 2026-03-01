# tabs/memory_tab.py

import flet as ft
import os
import logging
from datetime import datetime
from typing import Union, Dict
import diagnostics
from config import DIALOG_FONT_SIZE
from utils import get_executable_dir
import utils
from ui_components import create_card, create_label_value_row
from dialogs import show_loading_dialog, hide_loading_dialog, close_dialog, show_success_dialog, show_error_dialog

logger = logging.getLogger(__name__)


def display_memory_diagnostics(
    page: ft.Page, memory_list_view: ft.ListView, memory_table_container: ft.Column, selected_memory_log: ft.Ref[str]
) -> None:
    """
    メモリ診断ログのリストを取得し、選択されたログを詳細表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        memory_list_view (ft.ListView): メモリ診断ログのリストビュー。
        memory_table_container (ft.Column): 選択されたログの詳細を表示するコンテナ。
        selected_memory_log (ft.Ref[str]): 選択されたログファイル名を保持する参照。
    """
    # ローディングインジケーターを表示
    loading_dialog = show_loading_dialog(page)

    try:
        results = diagnostics.search_memory_log()  # 診断結果を取得
        memory_list_view.controls.clear()
        logger.debug(f"Memory Logs: {results}")  # デバッグ用

        # 成功時のダイアログ
        show_success_dialog(page, "診断結果の検索が終了しました。")

        # レスポンシブサイズを取得
        font_size, _, _, _, _, _ = utils.get_ui_sizes(page)

        # リストに並べる
        if not results:
            memory_list_view.controls.append(
                ft.Text("ログファイルが存在しません。", size=font_size))
        else:
            # リストに並べる
            for result in results:
                memory_list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(
                            f"EventID: {getattr(result, 'EventCode', 'Unknown')} - {getattr(result, 'TimeGenerated', 'Unknown')}", size=font_size
                        ),
                        on_click=lambda e, res=result: (
                            display_memory_log_content(
                                page, res, memory_table_container
                            ),
                            setattr(selected_memory_log, 'current', res),
                            page.update()
                        ),
                        selected=(selected_memory_log.current == result),
                        selected_color=ft.Colors.BLUE,
                    )
                )
    finally:
        # ローディングインジケーターを閉じる
        hide_loading_dialog(page, loading_dialog)


def display_memory_log_content(
    page: ft.Page, log: Union[Dict[str, str], object], memory_table_container: ft.Column
) -> None:
    """
    選択したメモリ診断ログの詳細を表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        log (Union[Dict[str, str], object]): 選択されたログデータ。
        memory_table_container (ft.Column): 詳細を表示するコンテナ。
    """
    memory_table_container.controls.clear()

    # デバッグ用: 取得したログデータを表示
    logger.debug(f"Memory Log Content: {log}")

    if isinstance(log, dict):
        source_name = log.get('SourceName', 'Unknown')
        event_code = log.get('EventCode', 'Unknown')
        time_generated = log.get('TimeGenerated', 'Unknown')
        message = log.get('Message', 'Unknown')
    else:
        source_name = getattr(log, 'SourceName', 'Unknown')
        event_code = getattr(log, 'EventCode', 'Unknown')
        time_generated = getattr(log, 'TimeGenerated', 'Unknown')
        message = getattr(log, 'Message', 'Unknown')

    # レスポンシブサイズを取得
    font_size, icon_size, label_width, padding, spacing, col_config = utils.get_ui_sizes(page)

    memory_card = create_card(
        title="ログの詳細",
        content_controls=[
            create_label_value_row("SourceName:", f"{source_name}", label_width, font_size),
            create_label_value_row("Event ID:", f"{event_code}", label_width, font_size),
            create_label_value_row("Time Generated:", f"{time_generated}", label_width, font_size),
            create_label_value_row("Message:", f"{message}", label_width, font_size),
        ],
        icon_filename="memory.png",
        icon_size=icon_size,
        font_size=font_size,
        padding=padding,
        spacing=spacing,
        col=col_config
    )

    responsive_row = ft.ResponsiveRow([memory_card], spacing=10)
    memory_table_container.controls.append(responsive_row)
    page.update()
