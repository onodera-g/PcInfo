"""PcInfoのメイン画面。診断とログ出力は各タブの既存処理へ委譲する。"""
import logging
import flet as ft
import diagnostics
from config import (
    WINDOW_WIDTH_DEFAULT, WINDOW_HEIGHT_DEFAULT, WINDOW_MIN_WIDTH, WINDOW_MIN_HEIGHT,
    DIALOG_FONT_SIZE,
)
from utils import get_base_path, is_admin
from ui_components import (
    configure_page_theme, create_action_button, create_diagnostic_tab_content,
    create_tab_content, set_status_message,
)
from dialogs import show_error_dialog
from tabs.system_info_tab import display_system_info
from tabs.storage_tab import display_storage_diagnostics, display_storage_diagnostics_with_dialog
from tabs.memory_tab import display_memory_diagnostics
from tabs.gpu_tab import display_gpu_log_list, display_gpu_diagnostics

logger = logging.getLogger(__name__)


def main(page: ft.Page) -> None:
    admin_text = " (管理者)" if is_admin() else ""
    page.title = f"PcInfo{admin_text}"
    page.padding = 20
    page.window.width = WINDOW_WIDTH_DEFAULT
    page.window.height = WINDOW_HEIGHT_DEFAULT
    page.window.min_width = WINDOW_MIN_WIDTH
    page.window.min_height = WINDOW_MIN_HEIGHT
    page.window.resizable = True
    configure_page_theme(page)

    status = ft.Text(size=DIALOG_FONT_SIZE, max_lines=1,
                     overflow=ft.TextOverflow.ELLIPSIS, color=ft.colors.ON_SURFACE_VARIANT)
    page.session.set("pcinfo_status", status)
    set_status_message(page, "PcInfoを起動しました。")

    selected_storage_log, selected_memory_log, selected_gpu_log = ft.Ref(), ft.Ref(), ft.Ref()
    memory_list_view = ft.ListView(spacing=2)
    storage_list_view = ft.ListView(spacing=2)
    gpu_list_view = ft.ListView(spacing=2)
    def details():
        return ft.Column([ft.Text("一覧からログを選択すると詳細が表示されます。",
                                  size=DIALOG_FONT_SIZE, color=ft.colors.ON_SURFACE_VARIANT)], spacing=0)
    memory_table_container, storage_table_container, gpu_table_container = details(), details(), details()
    system_info_container = ft.Column([
        ft.Text("「PC構成の取得」を押すと、構成情報を表示してログを保存します。",
                size=DIALOG_FONT_SIZE, color=ft.colors.ON_SURFACE_VARIANT),
    ], spacing=0)

    def run_memory(e):
        set_status_message(page, "Windowsメモリ診断を起動しています。")
        page.update()
        try:
            if diagnostics.run_memory_diagnostics():
                set_status_message(page, "Windowsメモリ診断を起動しました。")
                page.update()
            else:
                show_error_dialog(page, "起動できませんでした", "Windowsメモリ診断を起動できませんでした。")
        except Exception:
            logger.exception("Windowsメモリ診断の起動中にエラーが発生しました。")
            show_error_dialog(page, "起動できませんでした", "Windowsメモリ診断を起動できませんでした。")

    pc_content = ft.Column([
        ft.Container(height=4),
        create_action_button("PC構成の取得", lambda e: display_system_info(page, system_info_container), True),
        ft.Divider(height=24, thickness=1, color=ft.colors.OUTLINE_VARIANT),
        system_info_container,
    ], spacing=8, scroll=ft.ScrollMode.AUTO, expand=True)

    memory_content = create_diagnostic_tab_content([
        create_action_button("メモリ診断結果の表示", lambda e: display_memory_diagnostics(
            page, memory_list_view, memory_table_container, selected_memory_log), True),
        create_action_button("Windowsメモリ診断の実行", run_memory),
    ], memory_list_view, memory_table_container)
    storage_content = create_diagnostic_tab_content([
        create_action_button("診断結果の表示", lambda e: display_storage_diagnostics(
            page, storage_list_view, storage_table_container, selected_storage_log), True),
        create_action_button("S.M.A.R.T.の取得", lambda e: display_storage_diagnostics_with_dialog(page)),
    ], storage_list_view, storage_table_container)
    gpu_content = create_diagnostic_tab_content([
        create_action_button("診断結果の表示", lambda e: display_gpu_log_list(
            page, gpu_list_view, gpu_table_container, selected_gpu_log), True),
        create_action_button("GPU情報の取得", lambda e: display_gpu_diagnostics(
            page, gpu_list_view, gpu_table_container, selected_gpu_log)),
    ], gpu_list_view, gpu_table_container)

    tabs = ft.Tabs(
        selected_index=0, expand=True,
        divider_color=ft.colors.OUTLINE_VARIANT, indicator_color=ft.colors.PRIMARY,
        label_color=ft.colors.PRIMARY, unselected_label_color=ft.colors.ON_SURFACE_VARIANT,
        overlay_color={ft.ControlState.HOVERED: ft.colors.PRIMARY_CONTAINER},
        tabs=[
            ft.Tab(text="PC情報", content=create_tab_content("ハードウェア構成の取得・確認", pc_content)),
            ft.Tab(text="メモリ診断", content=create_tab_content("診断ログの確認・Windowsメモリ診断の実行", memory_content)),
            ft.Tab(text="ストレージ診断", content=create_tab_content("診断ログの確認・S.M.A.R.T.情報の取得", storage_content)),
            ft.Tab(text="GPU診断", content=create_tab_content("診断ログの確認・GPU情報の取得", gpu_content)),
        ],
    )
    page.add(status, tabs)


if __name__ == "__main__":
    ft.app(target=main, assets_dir=get_base_path())
