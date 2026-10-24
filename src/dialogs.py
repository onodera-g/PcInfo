"""ダイアログと、画面上部へ残す処理結果の表示。"""
from typing import Optional
import flet as ft
from config import DIALOG_FONT_SIZE, ICON_SIZE, PROGRESS_BAR_WIDTH
from ui_components import set_status_message


def create_loading_dialog(page: ft.Page) -> ft.AlertDialog:
    return ft.AlertDialog(
        title=ft.Row([
            ft.ProgressRing(width=ICON_SIZE, height=ICON_SIZE, stroke_width=2),
            ft.Text("情報を取得中...", size=DIALOG_FONT_SIZE + 2),
        ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.CENTER),
        content=ft.ProgressBar(width=PROGRESS_BAR_WIDTH), actions=[], modal=True,
    )


def show_loading_dialog(page: ft.Page) -> ft.AlertDialog:
    dialog = page.session.get("pcinfo_loading")
    if dialog is None:
        dialog = create_loading_dialog(page)
        page.session.set("pcinfo_loading", dialog)
    set_status_message(page, "情報を取得しています。")
    page.open(dialog)
    return dialog


def hide_loading_dialog(page: ft.Page, loading_dialog: ft.AlertDialog) -> None:
    if loading_dialog.open:
        page.close(loading_dialog)


def show_success_dialog(page: ft.Page, message: str) -> None:
    loading = page.session.get("pcinfo_loading")
    if loading is not None:
        hide_loading_dialog(page, loading)
    set_status_message(page, message)
    dialog = ft.AlertDialog(
        content=ft.Text(message, size=DIALOG_FONT_SIZE),
        actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(dialog, page))],
    )
    dialog.on_dismiss = lambda e: remove_closed_dialog(dialog, page)
    page.open(dialog)


def show_error_dialog(page: ft.Page, title: str, message: str,
                      error_detail: Optional[str] = None) -> None:
    loading = page.session.get("pcinfo_loading")
    if loading is not None:
        hide_loading_dialog(page, loading)
    set_status_message(page, message, error=True)
    controls = [ft.Text(message, size=DIALOG_FONT_SIZE)]
    if error_detail:
        controls.append(ft.Text(error_detail, size=DIALOG_FONT_SIZE,
                                color=ft.colors.ERROR, selectable=True))
    dialog = ft.AlertDialog(
        title=ft.Text(title, size=DIALOG_FONT_SIZE + 2),
        content=ft.Column(controls, tight=True, scroll=ft.ScrollMode.AUTO),
        actions=[ft.TextButton("OK", on_click=lambda e: close_dialog(dialog, page))],
    )
    dialog.on_dismiss = lambda e: remove_closed_dialog(dialog, page)
    page.open(dialog)


def remove_closed_dialog(dialog: ft.AlertDialog, page: ft.Page) -> None:
    dialog.open = False
    if dialog in page.overlay:
        page.overlay.remove(dialog)
        page.update()


def close_dialog(dialog: ft.AlertDialog, page: ft.Page) -> None:
    page.close(dialog)
