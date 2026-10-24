"""UI共通部品と、全タブで共有する外観・処理状態。"""
import os
from datetime import datetime
from typing import Any, Callable, List, Optional, Sequence
import flet as ft
from config import BUTTON_FONT_SIZE, LIST_VIEW_HEIGHT


def configure_page_theme(page: ft.Page) -> None:
    """OSの明暗配色に追従する。部品には配色の役割名を指定する。"""
    def make_theme(dark: bool = False) -> ft.Theme:
        return ft.Theme(
            color_scheme_seed="#0f62fe", font_family="Yu Gothic UI",
            color_scheme=ft.ColorScheme(
                primary="#78a9ff" if dark else "#0f62fe",
                on_primary="#161616" if dark else "#ffffff",
                surface="#262626" if dark else "#ffffff",
                on_surface="#f4f4f4" if dark else "#161616",
                surface_variant="#161616" if dark else "#f4f4f4",
                on_surface_variant="#c6c6c6" if dark else "#525252",
                outline="#6f6f6f" if dark else "#8d8d8d",
                outline_variant="#525252" if dark else "#d6d6d6",
                primary_container="#24334b" if dark else "#e8f0ff",
                on_primary_container="#d0e2ff" if dark else "#0043ce",
                error="#ffb3b8" if dark else "#da1e28",
            ),
        )
    page.theme_mode = ft.ThemeMode.SYSTEM
    page.theme = make_theme()
    page.dark_theme = make_theme(True)
    page.bgcolor = ft.colors.SURFACE_VARIANT


def set_status_message(page: ft.Page, message: str, error: bool = False) -> None:
    """表示用の最新1件だけを更新する。ファイルへのログ出力とは独立する。"""
    status = page.session.get("pcinfo_status")
    if status is not None:
        full_message = f"{datetime.now():%Y/%m/%d %H:%M:%S}　{message}"
        status.value = " ".join(full_message.splitlines())
        status.tooltip = full_message
        status.color = ft.colors.ERROR if error else ft.colors.ON_SURFACE_VARIANT


def create_action_button(label: str, on_click: Callable, primary: bool = False) -> ft.ElevatedButton:
    return ft.ElevatedButton(
        content=ft.Text(label, size=BUTTON_FONT_SIZE), on_click=on_click,
        style=ft.ButtonStyle(
            bgcolor={"": ft.colors.PRIMARY if primary else ft.colors.SURFACE,
                     ft.ControlState.HOVERED: ft.colors.PRIMARY_CONTAINER,
                     ft.ControlState.FOCUSED: ft.colors.PRIMARY_CONTAINER,
                     ft.ControlState.DISABLED: ft.colors.SURFACE_VARIANT},
            color={"": ft.colors.ON_PRIMARY if primary else ft.colors.PRIMARY,
                   ft.ControlState.HOVERED: ft.colors.ON_PRIMARY_CONTAINER,
                   ft.ControlState.FOCUSED: ft.colors.ON_PRIMARY_CONTAINER,
                   ft.ControlState.DISABLED: ft.colors.ON_SURFACE_VARIANT},
            elevation=0,
            padding=ft.padding.symmetric(horizontal=16, vertical=12),
            shape=ft.RoundedRectangleBorder(radius=4),
            side={"": ft.BorderSide(1, ft.colors.PRIMARY if primary else ft.colors.OUTLINE),
                  ft.ControlState.FOCUSED: ft.BorderSide(2, ft.colors.PRIMARY)},
        ),
    )


def create_label_value_row(label: str, value: str, label_width: float, font_size: int,
                           value_width: Optional[float] = None) -> ft.Row:
    return ft.Row([
        ft.Text(label, size=font_size, width=label_width, color=ft.colors.ON_SURFACE_VARIANT),
        ft.Text(value, size=font_size, width=value_width,
                expand=value_width is None, selectable=True),
    ], spacing=12, vertical_alignment=ft.CrossAxisAlignment.START)


def create_card(title: str, content_controls: Sequence[ft.Control], icon_filename: str,
                icon_size: int, font_size: int, padding: int, spacing: int,
                col: Optional[Any], layout: str = "single_column") -> ft.Container:
    controls = []
    for group in content_controls:
        if layout == "numbered" and isinstance(group, (list, tuple)):
            controls.extend(group)
        else:
            controls.append(group)
    card = ft.Container(
        content=ft.Column([
            ft.Row([
                ft.Image(src=os.path.join("icons", icon_filename).replace("\\", "/"),
                         width=icon_size, height=icon_size, color=ft.colors.ON_SURFACE),
                ft.Text(title, size=font_size + 1, weight=ft.FontWeight.W_600, expand=True),
            ], spacing=10, vertical_alignment=ft.CrossAxisAlignment.CENTER),
            ft.Divider(height=12, thickness=1, color=ft.colors.OUTLINE_VARIANT),
            ft.Column(controls, spacing=spacing),
        ], spacing=8),
        bgcolor=ft.colors.SURFACE,
        border=ft.border.all(1, ft.colors.OUTLINE_VARIANT), border_radius=4,
        padding=padding, margin=ft.margin.symmetric(vertical=6),
    )
    if col:
        card.col = col
    return card


def create_log_tile(page: ft.Page, list_view: ft.ListView, title: str, value: Any,
                    selected_log: ft.Ref, on_select: Callable, font_size: int) -> ft.ListTile:
    tile = ft.ListTile(
        title=ft.Text(title, size=font_size, max_lines=2, overflow=ft.TextOverflow.ELLIPSIS),
        tooltip=title, selected=selected_log.current == value,
        selected_color=ft.colors.ON_PRIMARY_CONTAINER,
        selected_tile_color=ft.colors.PRIMARY_CONTAINER,
        hover_color=ft.colors.SURFACE_VARIANT,
        shape=ft.RoundedRectangleBorder(radius=4),
        content_padding=ft.padding.symmetric(horizontal=12, vertical=2),
    )
    def select(e):
        on_select(value)
        selected_log.current = value
        for item in list_view.controls:
            if isinstance(item, ft.ListTile):
                item.selected = item is tile
        set_status_message(page, f"{title} を選択しました。")
        page.update()
    tile.on_click = select
    return tile


def create_diagnostic_tab_content(buttons: List[ft.ElevatedButton], list_view: ft.ListView,
                                  table_container: ft.Column) -> ft.Column:
    return ft.Column([
        ft.Container(height=4),
        ft.Row(buttons, wrap=True, spacing=8, run_spacing=8),
        ft.Text("診断ログ一覧:", size=BUTTON_FONT_SIZE, weight=ft.FontWeight.W_600),
        ft.Container(content=list_view, height=LIST_VIEW_HEIGHT, bgcolor=ft.colors.SURFACE,
                     border=ft.border.all(1, ft.colors.OUTLINE_VARIANT), border_radius=4, padding=4),
        ft.Divider(height=24, thickness=1, color=ft.colors.OUTLINE_VARIANT),
        table_container,
    ], spacing=12, scroll=ft.ScrollMode.AUTO, expand=True)


def create_tab_content(guide: str, content: ft.Column) -> ft.Column:
    """タブの短い案内を本文のスクロール領域から分ける。"""
    band = ft.Container(
        ft.Text(guide, size=BUTTON_FONT_SIZE, max_lines=1,
                overflow=ft.TextOverflow.ELLIPSIS, tooltip=guide),
        bgcolor=ft.colors.PRIMARY_CONTAINER,
        padding=ft.padding.symmetric(horizontal=12, vertical=6), expand=True,
    )
    content.expand = True
    return ft.Column([ft.Row([band]), content], spacing=12, expand=True)
