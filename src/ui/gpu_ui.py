# gpu_ui.py

import flet as ft
from gpu_diagnostics import (
    get_gpu_device_status,
    save_gpu_diagnostics_log,
    get_gpu_diagnostic_logs,
    read_gpu_diagnostic_log
)
import logging

logger = logging.getLogger(__name__)


def create_gpu_diagnostics_tab(page: ft.Page) -> ft.Container:
    """
    GPU診断タブを作成します。
    メモリ診断タブと同じレイアウトで、診断実行、ログリスト表示、ログ内容表示を提供します。

    Args:
        page: Fletページオブジェクト

    Returns:
        ft.Container: GPU診断タブのコンテナ
    """
    # GPU診断結果を表示するテキストエリア
    gpu_diagnostics_output = ft.TextField(
        value="",
        multiline=True,
        read_only=True,
        min_lines=15,
        max_lines=15,
        text_size=12,
        border_color=ft.colors.BLUE_GREY_700,
    )

    # ログリストを表示するリストビュー
    log_list_view = ft.ListView(
        spacing=5,
        padding=10,
        height=200,
    )

    # ログ内容を表示するテキストエリア
    log_content_view = ft.TextField(
        value="",
        multiline=True,
        read_only=True,
        min_lines=10,
        max_lines=10,
        text_size=11,
        border_color=ft.colors.BLUE_GREY_700,
    )

    def run_gpu_diagnostics(e):
        """GPU診断を実行し、結果を表示してログに保存します。"""
        try:
            logger.info("GPU診断を開始します。")
            gpu_diagnostics_output.value = "GPU診断を実行中...\n"
            page.update()

            # GPU診断実行
            gpu_status_list = get_gpu_device_status()

            if not gpu_status_list:
                gpu_diagnostics_output.value = "GPU情報の取得に失敗しました。"
                page.update()
                logger.error("GPU診断情報の取得に失敗しました。")
                return

            # 結果を画面に表示
            result_text = "=" * 60 + "\n"
            result_text += "GPU診断結果\n"
            result_text += "=" * 60 + "\n\n"

            for idx, gpu in enumerate(gpu_status_list, 1):
                result_text += f"[GPU {idx}]\n"
                result_text += f"デバイス名: {gpu.get('Name', 'Unknown')}\n"
                result_text += f"ステータス: {gpu.get('Status', 'Unknown')}\n"
                result_text += f"エラーコード: {gpu.get('ErrorCode', 'Unknown')}\n"
                result_text += f"エラー説明: {gpu.get('ErrorDescription', 'Unknown')}\n"
                result_text += f"ドライババージョン: {gpu.get('DriverVersion', 'Unknown')}\n"
                result_text += f"ドライバ日付: {gpu.get('DriverDate', 'Unknown')}\n"
                result_text += "-" * 60 + "\n\n"

            gpu_diagnostics_output.value = result_text
            page.update()

            # ログファイルに保存
            log_filepath = save_gpu_diagnostics_log(gpu_status_list)
            if log_filepath:
                logger.info(f"GPU診断ログを保存しました: {log_filepath}")
                # ログリストを更新
                update_log_list()

                # 完了ダイアログを表示
                def close_dialog(e):
                    dialog.open = False
                    page.update()

                dialog = ft.AlertDialog(
                    title=ft.Text("診断完了"),
                    content=ft.Text(f"GPU診断が完了しました。\nログファイルを保存しました。"),
                    actions=[
                        ft.TextButton("OK", on_click=close_dialog)
                    ],
                )
                page.dialog = dialog
                dialog.open = True
                page.update()
            else:
                logger.error("GPU診断ログの保存に失敗しました。")

        except Exception as ex:
            error_msg = f"GPU診断中にエラーが発生しました: {ex}"
            logger.exception(error_msg)
            gpu_diagnostics_output.value = error_msg
            page.update()

    def update_log_list():
        """ログファイル一覧を更新します。"""
        try:
            log_files = get_gpu_diagnostic_logs()
            log_list_view.controls.clear()

            if not log_files:
                log_list_view.controls.append(
                    ft.Text("ログファイルがありません。", size=12, color=ft.colors.GREY_500)
                )
            else:
                for log_file in log_files:
                    def create_on_click(filename):
                        def on_click(e):
                            display_log_content(filename)
                        return on_click

                    log_list_view.controls.append(
                        ft.TextButton(
                            text=log_file,
                            on_click=create_on_click(log_file),
                            style=ft.ButtonStyle(
                                color=ft.colors.BLUE_400,
                            )
                        )
                    )

            page.update()
            logger.debug("ログファイル一覧を更新しました。")

        except Exception as ex:
            logger.exception(f"ログファイル一覧の更新中にエラーが発生しました: {ex}")

    def display_log_content(filename: str):
        """選択されたログファイルの内容を表示します。"""
        try:
            content = read_gpu_diagnostic_log(filename)
            log_content_view.value = content
            page.update()
            logger.debug(f"ログファイルの内容を表示しました: {filename}")

        except Exception as ex:
            error_msg = f"ログファイルの読み込み中にエラーが発生しました: {ex}"
            logger.exception(error_msg)
            log_content_view.value = error_msg
            page.update()

    def refresh_log_list(e):
        """ログリストを手動更新します。"""
        update_log_list()

    # 初期ログリスト読み込み
    update_log_list()

    # GPU診断実行ボタン
    run_diagnostics_button = ft.ElevatedButton(
        text="GPU診断を実行",
        icon=ft.icons.PLAY_ARROW,
        on_click=run_gpu_diagnostics,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.BLUE_700,
        )
    )

    # ログリスト更新ボタン
    refresh_button = ft.ElevatedButton(
        text="ログリストを更新",
        icon=ft.icons.REFRESH,
        on_click=refresh_log_list,
        style=ft.ButtonStyle(
            color=ft.colors.WHITE,
            bgcolor=ft.colors.GREEN_700,
        )
    )

    # レイアウト構築
    content = ft.Column(
        controls=[
            # タイトルと実行ボタン
            ft.Row(
                controls=[
                    ft.Icon(name=ft.icons.VIDEOGAME_ASSET,
                            size=30, color=ft.colors.BLUE_400),
                    ft.Text("GPU診断", size=24, weight=ft.FontWeight.BOLD),
                ],
                alignment=ft.MainAxisAlignment.START,
            ),
            ft.Divider(height=1, color=ft.colors.GREY_400),

            # 診断実行ボタン
            ft.Container(
                content=run_diagnostics_button,
                padding=ft.padding.only(top=10, bottom=10),
            ),

            # 診断結果表示エリア
            ft.Text("診断結果:", size=16, weight=ft.FontWeight.BOLD),
            gpu_diagnostics_output,

            ft.Divider(height=2, color=ft.colors.GREY_400),

            # ログリスト表示エリア
            ft.Row(
                controls=[
                    ft.Text("診断ログ一覧:", size=16, weight=ft.FontWeight.BOLD),
                    refresh_button,
                ],
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            ),
            ft.Container(
                content=log_list_view,
                border=ft.border.all(1, ft.colors.GREY_400),
                border_radius=5,
                padding=5,
            ),

            # ログ内容表示エリア
            ft.Text("ログ内容:", size=16, weight=ft.FontWeight.BOLD),
            log_content_view,
        ],
        spacing=10,
        scroll=ft.ScrollMode.AUTO,
    )

    return ft.Container(
        content=content,
        padding=20,
    )
