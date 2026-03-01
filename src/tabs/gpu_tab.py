# tabs/gpu_tab.py

import flet as ft
import os
import logging
from datetime import datetime
from typing import Optional
import gpu_diagnostics
from config import DIALOG_FONT_SIZE
from utils import get_executable_dir
import utils
from ui_components import create_card, create_label_value_row
from dialogs import show_loading_dialog, hide_loading_dialog, close_dialog, show_success_dialog, show_error_dialog

logger = logging.getLogger(__name__)


def display_gpu_log_list(
    page: ft.Page, gpu_list_view: ft.ListView, gpu_table_container: ft.Column, selected_gpu_log: ft.Ref[str]
) -> None:
    """
    保存されているGPU診断ログのリストを表示します（診断は実行しない）。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        gpu_list_view (ft.ListView): GPU診断ログのリストビュー。
        gpu_table_container (ft.Column): 選択されたログの詳細を表示するコンテナ。
        selected_gpu_log (ft.Ref[str]): 選択されたログファイル名を保持する参照。
    """
    # ログファイル一覧を取得して表示
    results = gpu_diagnostics.get_gpu_diagnostic_logs()
    gpu_list_view.controls.clear()
    logger.debug(f"GPU Logs: {results}")

    # レスポンシブサイズを取得
    font_size, _, _, _, _, _ = utils.get_ui_sizes(page)

    if not results:
        gpu_list_view.controls.append(
            ft.Text("ログファイルが存在しません。", size=font_size))
    else:
        for result in results:
            gpu_list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(result, size=font_size),
                    on_click=lambda e, res=result: (
                        display_gpu_log_content(
                            page, res, gpu_table_container
                        ),
                        setattr(selected_gpu_log, 'current', res),
                        page.update()
                    ),
                )
            )
    page.update()


def display_gpu_diagnostics(
    page: ft.Page, gpu_list_view: ft.ListView, gpu_table_container: ft.Column, selected_gpu_log: ft.Ref[str]
) -> None:
    """
    GPU診断を実行し、ログを保存して、ログのリストを更新します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        gpu_list_view (ft.ListView): GPU診断ログのリストビュー。
        gpu_table_container (ft.Column): 選択されたログの詳細を表示するコンテナ。
        selected_gpu_log (ft.Ref[str]): 選択されたログファイル名を保持する参照。
    """
    # ローディングインジケーターを表示
    loading_dialog = show_loading_dialog(page)

    try:
        # GPU診断を実行してログを保存
        gpu_status_list = gpu_diagnostics.get_gpu_device_status()

        if gpu_status_list:
            log_filepath = gpu_diagnostics.save_gpu_diagnostics_log(gpu_status_list)
            if log_filepath:
                logger.info(f"GPU診断ログを保存しました: {log_filepath}")
                show_success_dialog(page, "GPU診断が完了し、ログが保存されました。")
            else:
                show_error_dialog(page, "エラー", "GPU診断ログの保存に失敗しました。", "")
        else:
            show_error_dialog(page, "エラー", "GPU情報の取得に失敗しました。", "")

        # ログファイル一覧を更新
        display_gpu_log_list(page, gpu_list_view, gpu_table_container, selected_gpu_log)

    except Exception as e:
        logger.exception("GPU診断の実行中にエラーが発生しました。")
        show_error_dialog(page, "エラー", "GPU診断の実行中にエラーが発生しました。", str(e))
    finally:
        # ローディングインジケーターを閉じる
        hide_loading_dialog(page, loading_dialog)


def display_gpu_log_content(
    page: ft.Page, log_filename: str, gpu_table_container: ft.Column
) -> None:
    """
    選択したGPU診断ログの詳細をカード形式で表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        log_filename (str): 選択されたログファイル名。
        gpu_table_container (ft.Column): 詳細を表示するコンテナ。
    """
    gpu_data = gpu_diagnostics.parse_gpu_log(log_filename)
    logger.debug(f"GPU Log Content: {gpu_data}")

    # レスポンシブサイズを取得
    font_size, icon_size, label_width, padding, spacing, col_config = utils.get_ui_sizes(page)

    gpu_table_container.controls.clear()
    if not gpu_data:
        gpu_table_container.controls.append(
            ft.Text("ログファイルの内容を読み込めませんでした。", size=font_size)
        )
    else:
        gpu_cards = []
        for idx, gpu in enumerate(gpu_data, start=1):
            device_name = gpu.get('Name', 'Unknown')

            gpu_card = create_card(
                title=f"GPU{idx}: {device_name}",
                content_controls=[
                    create_label_value_row(
                        "Status:",
                        gpu.get('Status', 'Unknown'),
                        label_width=label_width,
                        font_size=font_size
                    ),
                    create_label_value_row(
                        "Error Code:",
                        gpu.get('Error Code', 'Unknown'),
                        label_width=label_width,
                        font_size=font_size
                    ),
                    create_label_value_row(
                        "Error Description:",
                        gpu.get('Error Description', 'Unknown'),
                        label_width=label_width,
                        font_size=font_size
                    ),
                    create_label_value_row(
                        "Driver Version:",
                        gpu.get('Driver Version', 'Unknown'),
                        label_width=label_width,
                        font_size=font_size
                    ),
                    create_label_value_row(
                        "Driver Date:",
                        gpu.get('Driver Date', 'Unknown'),
                        label_width=label_width,
                        font_size=font_size
                    ),
                ],
                icon_filename="video_library.png",
                layout="single_column",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
            gpu_cards.append(gpu_card)

        responsive_row = ft.ResponsiveRow(gpu_cards, spacing=10)
        gpu_table_container.controls.append(responsive_row)
    page.update()
