"""
メモリ診断UIモジュール
"""

import flet as ft
import logging
from typing import Union, Dict

import diagnostics
from constants import CARD_WIDTH, ICON_MEMORY, ICON_SIZE, ANIMATION_DURATION
from ui.components import create_label_value_row
from ui.dialogs import show_loading_dialog, hide_loading_dialog, show_success_dialog
from utils import get_icon_path

logger = logging.getLogger(__name__)


def display_memory_diagnostics(
    page: ft.Page,
    memory_list_view: ft.ListView,
    memory_table_container: ft.Column,
    selected_memory_log: ft.Ref[str]
) -> None:
    """
    メモリ診断ログのリストを取得し、選択されたログを詳細表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        memory_list_view (ft.ListView): メモリ診断ログのリストビュー。
        memory_table_container (ft.Column): 選択されたログの詳細を表示するコンテナ。
        selected_memory_log (ft.Ref[str]): 選択されたログファイル名を保持する参照。
    """
    loading_dialog = show_loading_dialog(page)

    try:
        results = diagnostics.search_memory_log()
        memory_list_view.controls.clear()
        logger.debug(f"Memory Logs: {results}")

        show_success_dialog(page, "診断結果の検索が終了しました。")

        if not results:
            memory_list_view.controls.append(
                ft.Text("ログファイルが存在しません。", size=12)
            )
        else:
            for result in results:
                memory_list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(
                            f"EventID: {getattr(result, 'EventCode', 'Unknown')} - "
                            f"{getattr(result, 'TimeGenerated', 'Unknown')}",
                            size=12
                        ),
                        on_click=lambda e, res=result: (
                            display_memory_log_content(
                                page, res, memory_table_container),
                            setattr(selected_memory_log, 'current', res),
                            page.update()
                        ),
                        selected=(selected_memory_log.current == result),
                        selected_color=ft.Colors.BLUE,
                    )
                )
    finally:
        hide_loading_dialog(page, loading_dialog)


def display_memory_log_content(
    page: ft.Page,
    log: Union[Dict[str, str], object],
    memory_table_container: ft.Column
) -> None:
    """
    選択したメモリ診断ログの詳細を表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        log (Union[Dict[str, str], object]): 選択されたログデータ。
        memory_table_container (ft.Column): 詳細を表示するコンテナ。
    """
    memory_table_container.controls.clear()
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

    memory_icon_path = get_icon_path(ICON_MEMORY)

    memory_card = ft.Container(
        width=CARD_WIDTH,
        content=ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Image(
                                src=memory_icon_path,
                                width=ICON_SIZE,
                                height=ICON_SIZE,
                            ),
                            ft.Text("ログの詳細", size=12,
                                    weight=ft.FontWeight.BOLD)
                        ], vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        create_label_value_row(
                            "SourceName:", f"{source_name}"),
                        create_label_value_row("Event ID:", f"{event_code}"),
                        create_label_value_row(
                            "Time Generated:", f"{time_generated}"),
                        create_label_value_row("Message:", f"{message}"),
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
    memory_table_container.controls.append(memory_card)
    page.update()
