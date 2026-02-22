"""
ダイアログ関連のUIモジュール
"""

import flet as ft
from typing import Optional
import logging

from constants import ICON_SIZE, PROGRESS_BAR_WIDTH, ICON_CIRCULAR_PROGRESS
from utils import get_icon_path

logger = logging.getLogger(__name__)


def create_loading_dialog(page: ft.Page) -> ft.AlertDialog:
    """
    ローディングダイアログを作成する。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。

    Returns:
        ft.AlertDialog: ローディングダイアログ。
    """
    loading_icon_path = get_icon_path(ICON_CIRCULAR_PROGRESS)

    loading_dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Image(
                src=loading_icon_path,
                width=ICON_SIZE,
                height=ICON_SIZE,
            ),
            ft.Text("情報を取得中...", size=12)
        ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        content=ft.ProgressBar(width=PROGRESS_BAR_WIDTH),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.START,
        modal=True,
    )
    return loading_dialog


def show_loading_dialog(page: ft.Page) -> ft.AlertDialog:
    """
    ローディングダイアログを表示する。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。

    Returns:
        ft.AlertDialog: 表示されたローディングダイアログ。
    """
    loading_dialog = create_loading_dialog(page)
    page.overlay.append(loading_dialog)
    loading_dialog.open = True
    page.update()
    return loading_dialog


def hide_loading_dialog(page: ft.Page, loading_dialog: ft.AlertDialog) -> None:
    """
    ローディングダイアログを非表示にする。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        loading_dialog (ft.AlertDialog): 非表示にするローディングダイアログ。
    """
    if loading_dialog in page.overlay:
        page.overlay.remove(loading_dialog)
    page.update()


def show_success_dialog(page: ft.Page, message: str) -> None:
    """
    成功ダイアログを表示する。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        message (str): 表示するメッセージ。
    """
    success_dialog = ft.AlertDialog(
        content=ft.Text(message, size=12),
        actions=[
            ft.TextButton(
                "OK", on_click=lambda e: close_dialog(success_dialog, page)
            )
        ],
        on_dismiss=lambda e: close_dialog(success_dialog, page),
    )
    page.overlay.append(success_dialog)
    success_dialog.open = True
    page.update()


def show_error_dialog(page: ft.Page, title: str, message: str, error_detail: Optional[str] = None) -> None:
    """
    エラーダイアログを表示する。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        title (str): ダイアログのタイトル。
        message (str): エラーメッセージ。
        error_detail (Optional[str]): エラーの詳細（オプション）。
    """
    content_controls = [ft.Text(message, size=12)]
    if error_detail:
        content_controls.append(
            ft.Text(error_detail, color=ft.Colors.RED, size=12))

    error_dialog = ft.AlertDialog(
        title=ft.Text(title, size=12),
        content=ft.Column(content_controls) if error_detail else ft.Text(
            message, size=12),
        actions=[
            ft.TextButton(
                "OK", on_click=lambda e: close_dialog(error_dialog, page))
        ],
        on_dismiss=lambda e: close_dialog(error_dialog, page),
    )
    page.overlay.append(error_dialog)
    error_dialog.open = True
    page.update()


def close_dialog(dialog: ft.AlertDialog, page: ft.Page) -> None:
    """
    ダイアログを閉じる。

    Parameters:
        dialog (ft.AlertDialog): 閉じるダイアログオブジェクト。
        page (ft.Page): Fletのページオブジェクト。
    """
    dialog.open = False
    page.update()
