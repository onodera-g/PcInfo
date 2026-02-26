# main.py

import flet as ft
import os
import diagnostics
import storage_diagnostics
import system_info
import gpu_diagnostics
from datetime import datetime
import sys
import subprocess
from typing import Optional, Union, Dict, List, Sequence, cast
import ctypes

import logging

# 定数定義
# ウィンドウサイズ（デフォルト値）
WINDOW_WIDTH_DEFAULT = 800
WINDOW_HEIGHT_DEFAULT = 1100
WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 700

# その他の定数
LIST_VIEW_HEIGHT = 150
LABEL_WIDTH = 120
ICON_SIZE = 24
ANIMATION_DURATION = 500
PROGRESS_BAR_WIDTH = 200

# アイコンファイル名
ICON_CIRCULAR_PROGRESS = "circular_progress.png"
ICON_DISK = "disk.png"
ICON_MEMORY = "memory.png"
ICON_COMPUTER = "computer.png"
ICON_CHIP = "chip.png"
ICON_DEVICE_HUB = "device_hub.png"
ICON_VIDEO_LIBRARY = "video_library.png"
ICON_APP = "app_icon.ico"

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 必要に応じてレベルを調整

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def is_admin() -> bool:
    """
    現在のプロセスが管理者権限で実行されているかを確認します。

    Returns:
        bool: 管理者権限で実行されている場合True、そうでない場合False。
    """
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except Exception as e:
        logger.error(f"管理者権限の確認に失敗しました: {e}")
        return False


def get_base_path() -> str:
    """
    実行ファイルのディレクトリを取得します。
    PyInstallerでコンパイルされた場合でも対応します。

    ワンファイル形式の場合: sys._MEIPASS (リソースファイル用)

    Returns:
        str: 実行ファイルのディレクトリパス。
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでコンパイルされた場合
        if hasattr(sys, '_MEIPASS'):
            # ワンファイル形式: リソースファイルは _MEIPASS に展開される
            base_path = sys._MEIPASS
        else:
            # ワンフォルダ形式
            base_path = os.path.dirname(sys.executable)
    else:
        # 開発環境の場合
        base_path = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Base path (for resources): {base_path}")
    return base_path


def get_executable_dir() -> str:
    """
    実行ファイルがあるディレクトリを取得します。
    ログファイルなどの永続的なデータの保存先に使用します。

    Returns:
        str: 実行ファイルのディレクトリパス。
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでコンパイルされた場合: 実行ファイルのディレクトリ
        exe_dir = os.path.dirname(sys.executable)
    else:
        # 開発環境の場合
        exe_dir = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Executable directory (for logs): {exe_dir}")
    return exe_dir


def get_responsive_sizes(page: ft.Page) -> Dict[str, int]:
    """
    ウィンドウサイズに応じたレスポンシブなサイズを計算します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。

    Returns:
        Dict[str, int]: 各UI要素のサイズを含む辞書。
    """
    # ウィンドウ幅を取得（デフォルト値を使用）
    window_width = page.window.width or WINDOW_WIDTH_DEFAULT

    # 基準サイズ（800px）に対する比率を計算
    scale_ratio = window_width / WINDOW_WIDTH_DEFAULT

    # 最小・最大スケールを制限（0.8〜1.5倍）
    scale_ratio = max(0.8, min(1.5, scale_ratio))

    return {
        'font_size_small': int(10 * scale_ratio),      # 通常の小さい文字
        'font_size_normal': int(12 * scale_ratio),     # 通常の文字
        'font_size_large': int(14 * scale_ratio),      # 大きい文字
        'icon_size': int(24 * scale_ratio),            # アイコンサイズ
        'label_width': int(120 * scale_ratio),         # ラベル幅
        'padding': int(10 * scale_ratio),              # パディング
        'spacing': int(5 * scale_ratio),               # スペーシング
        'list_view_height': int(150 * scale_ratio),    # リストビュー高さ
    }


####################
#    共通ヘルパー関数
######################

def create_loading_dialog(page: ft.Page) -> ft.AlertDialog:
    """
    ローディングダイアログを作成する共通関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。

    Returns:
        ft.AlertDialog: ローディングダイアログ。
    """
    base_path = get_base_path()
    loading_icon_path = os.path.join(
        base_path, "icons", ICON_CIRCULAR_PROGRESS)

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


####################
#    ストレージ診断
######################

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
    sizes = get_responsive_sizes(page)
    font_size = sizes['font_size_normal']
    
    if not results:
        storage_list_view.controls.append(ft.Text("ログファイルが存在しません。", size=font_size))
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

        # レスポンシブグリッド設定（最大4枚横並び）
        col_config = {"xs": 12, "sm": 12, "md": 6, "lg": 4, "xl": 3, "xxl": 3}
        
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
                                        f"ディスク{idx}: {model_number}", size=font_size, weight=ft.FontWeight.BOLD)
                                ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                create_label_value_row("Disk Size:", disk.get(
                                    'Disk Size', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Interface:", disk.get(
                                    'Interface', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Power On Hours:", disk.get(
                                    'Power On Hours', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Power On Count:", disk.get(
                                    'Power On Count', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Host Writes:", disk.get(
                                    'Host Writes', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Health Status:", disk.get(
                                    'Health Status', 'Unknown'), label_width, font_size=font_size),
                            ],
                            spacing=spacing
                        ),
                        padding=padding
                    ),
                    elevation=3,
                ),
                margin=ft.margin.symmetric(vertical=spacing, horizontal=5),
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
            # 失敗時のダイアログ（詳細なエラーメッセージを表示）
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

####################
#    メモリ診断
####################


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
        sizes = get_responsive_sizes(page)
        font_size = sizes['font_size_normal']

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
                            f"EventID: {getattr(
                                result, 'EventCode', 'Unknown')} - {getattr(result, 'TimeGenerated', 'Unknown')}", size=font_size
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
    sizes = get_responsive_sizes(page)
    font_size = sizes['font_size_normal']
    icon_size = sizes['icon_size']
    label_width = sizes['label_width']
    padding = sizes['padding']
    spacing = sizes['spacing']

    base_path = get_base_path()
    memory_icon_path = os.path.join(base_path, "icons", "memory.png")

    # レスポンシブグリッド設定（最大4枚横並び）
    col_config = {"xs": 12, "sm": 12, "md": 6, "lg": 4, "xl": 3, "xxl": 3}

    memory_card = ft.Container(
        content=ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Image(
                                src=memory_icon_path,
                                width=icon_size,
                                height=icon_size,
                            ),
                            ft.Text("ログの詳細", size=font_size,
                                    weight=ft.FontWeight.BOLD)
                        ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        create_label_value_row(
                            "SourceName:", f"{source_name}", label_width=label_width, font_size=font_size),
                        create_label_value_row(
                            "Event ID:", f"{event_code}", label_width=label_width, font_size=font_size),
                        create_label_value_row("Time Generated:", f"{
                                               time_generated}", label_width=label_width, font_size=font_size),
                        create_label_value_row(
                            "Message:", f"{message}", label_width=label_width, font_size=font_size),
                    ],
                    spacing=spacing
                ),
                padding=padding
            ),
            elevation=3,
        ),
        margin=ft.margin.symmetric(vertical=spacing, horizontal=5),
        col=col_config
    )
    
    responsive_row = ft.ResponsiveRow([memory_card], spacing=10)
    memory_table_container.controls.append(responsive_row)
    page.update()


####################
#    システム情報
####################
#    システム情報
####################


def create_label_value_row(label: str, value: str, label_width: float = LABEL_WIDTH, value_width: Optional[float] = None, font_size: int = 12) -> ft.Row:
    """
    ラベルと値を含むRowを作成するヘルパー関数。

    Parameters:
        label (str): ラベルテキスト。
        value (str): 値テキスト。
        label_width (float): ラベル部分の固定幅。
        value_width (Optional[float]): 値部分の固定幅。デフォルトはNone。
        font_size (int): フォントサイズ。

    Returns:
        ft.Row: ラベルと値を含むRowオブジェクト。
    """
    return ft.Row([
        ft.Text(label, size=font_size, width=label_width,
                weight=ft.FontWeight.BOLD),
        ft.Text(value, size=font_size,
                width=value_width if value_width else None, expand=True)
    ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )


def create_card(
    title: str, content_controls: Sequence[ft.Control], icon_filename: str, layout: str = "single_column",
    icon_size: int = ICON_SIZE, font_size: int = 12, padding: int = 10, spacing: int = 5,
    col: Optional[Dict[str, int]] = None
) -> ft.Container:
    """
    汎用的なカードを作成するヘルパー関数。

    Parameters:
        title (str): カードのタイトル。
        content_controls (List[ft.Control]): カード内のコンテンツコントロールのリスト。
        icon_filename (str): アイコンファイル名。
        layout (str): レイアウトタイプ（"single_column", "numbered"）。
        icon_size (int): アイコンサイズ。
        font_size (int): フォントサイズ。
        padding (int): パディング。
        spacing (int): スペーシング。
        col (Optional[Dict[str, int]]): ResponsiveRowのcolumn設定（レスポンシブ対応用）。

    Returns:
        ft.Container: カードを含むコンテナ（レスポンシブ対応）。
    """
    base_path = get_base_path()
    icon_path = os.path.join(base_path, "icons", icon_filename)

    if layout == "numbered":
        # numberedレイアウトの場合、content_controlsはList[List[Control]]形式
        flattened_controls = []
        for group in content_controls:
            if isinstance(group, (list, tuple)):
                flattened_controls.extend(group)
            else:
                flattened_controls.append(group)
        content = ft.Column(
            flattened_controls,
            spacing=int(spacing * 0.6),  # numberedの場合は少し狭く
        )
    else:
        content = ft.Column(
            list(content_controls),
            spacing=spacing,
        )

    card = ft.Container(
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
                            ft.Text(title, size=font_size,
                                    weight=ft.FontWeight.BOLD)
                        ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        content
                    ],
                    spacing=spacing
                ),
                padding=padding
            ),
            elevation=3,
        ),
        margin=ft.margin.symmetric(vertical=spacing, horizontal=5),
    )
    
    # colパラメータが指定されている場合は、ResponsiveRow用の設定を追加
    if col:
        card.col = col
    
    return card


def display_system_info(page: ft.Page, system_info_container: ft.Column) -> None:
    """
    PC情報を取得して表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        system_info_container (ft.Column): システム情報を表示するコンテナ。
    """
    # ローディングインジケーターを表示
    loading_dialog = show_loading_dialog(page)
    file_name = ""  # ファイル名の初期化

    try:
        # PC情報を取得
        os_info = system_info.get_os_info()
        motherboard_info = system_info.get_motherboard_info()
        cpu_info = system_info.get_cpu_info()
        memory_modules = system_info.get_memory_speed_and_manufacturer()
        storage_devices = system_info.get_storage_info()
        gpu_info = system_info.get_gpu_info()

        # デバッグ用: 取得した情報をログに記録
        logger.debug(f"OS Info: {os_info}")
        logger.debug(f"Motherboard Info: {motherboard_info}")
        logger.debug(f"CPU Info: {cpu_info}")
        logger.debug(f"Memory Modules: {memory_modules}")
        logger.debug(f"Storage Devices: {storage_devices}")
        logger.debug(f"GPU Info: {gpu_info}")

        # システム情報コンテナをクリア
        system_info_container.controls.clear()

        # レスポンシブサイズを取得
        sizes = get_responsive_sizes(page)
        font_size = sizes['font_size_normal']
        icon_size = sizes['icon_size']
        label_width = sizes['label_width']
        padding = sizes['padding']
        spacing = sizes['spacing']

        # レスポンシブグリッド設定
        # 全カード共通: 最大4枚を1行に表示（xs/sm: 1列, md: 2列, lg: 3列, xl/xxl: 4列）
        col_config = {"xs": 12, "sm": 12, "md": 6, "lg": 4, "xl": 3, "xxl": 3}

        # OS情報カードの作成
        os_name, os_version = os_info
        os_card = create_card(
            title="OS",
            content_controls=[
                create_label_value_row(
                    "名称:", os_name, label_width=label_width, font_size=font_size),
                create_label_value_row(
                    "バージョン:", os_version, label_width=label_width, font_size=font_size),
            ],
            icon_filename="computer.png",
            layout="single_column",
            icon_size=icon_size,
            font_size=font_size,
            padding=padding,
            spacing=spacing,
            col=col_config
        )
        
        # ResponsiveRowに追加
        responsive_row = ft.ResponsiveRow([os_card], spacing=10)
        system_info_container.controls.append(responsive_row)

        # CPU情報カードの作成
        if isinstance(cpu_info, dict):
            cpu_name = str(cpu_info.get('Name', 'Unknown')).strip()
            stepping = cpu_info.get('Stepping', 'Unknown')
            revision = cpu_info.get('Revision', 'Unknown')

            cpu_items_text = [
                create_label_value_row("名称:", cpu_name, label_width=label_width, font_size=font_size),
                create_label_value_row(
                    "コア数:", f"{cpu_info.get('NumberOfCores', 'Unknown')}",
                    label_width=label_width, font_size=font_size
                ),
                create_label_value_row("スレッド数:", f"{cpu_info.get(
                    'NumberOfLogicalProcessors', 'Unknown')}",
                    label_width=label_width, font_size=font_size
                ),
                create_label_value_row(
                    "最大クロック速度:", f"{cpu_info.get(
                        'MaxClockSpeed', 'Unknown')} MHz",
                    label_width=label_width, font_size=font_size
                ),
                create_label_value_row(
                    "リビジョン:", f"{revision}",
                    label_width=label_width, font_size=font_size
                ),
                create_label_value_row(
                    "ステッピング:", f"{stepping}",
                    label_width=label_width, font_size=font_size
                ),
            ]
            cpu_card = create_card(
                title="CPU",
                content_controls=cpu_items_text,
                icon_filename="chip.png",
                layout="single_column",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
        else:
            cpu_card = create_card(
                title="CPU",
                content_controls=[
                    ft.Text("CPU情報の形式が不正です。", size=font_size, color=ft.Colors.RED)],
                icon_filename="chip.png",
                layout="single_column",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
        
        responsive_row = ft.ResponsiveRow([cpu_card], spacing=10)
        system_info_container.controls.append(responsive_row)

        # メモリ情報カードの作成
        if isinstance(memory_modules, list) and all(isinstance(module, dict) for module in memory_modules):
            memory_cards = []
            for idx, module in enumerate(memory_modules, start=1):
                module_title = f"モジュール{idx}"
                module_items = [
                    ft.Text(module_title, size=font_size,
                            weight=ft.FontWeight.BOLD),
                    create_label_value_row("モデル番号:", module.get(
                        'ManufacturerAndModel', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row(
                        "クロック速度:", module.get('Speed', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row(
                        "容量:", module.get('Capacity', 'Unknown'), label_width=label_width, font_size=font_size),
                ]
                memory_card = create_card(
                    title="メモリー",
                    content_controls=module_items,
                    icon_filename="memory.png",
                    layout="numbered",
                    icon_size=icon_size,
                    font_size=font_size,
                    padding=padding,
                    spacing=spacing,
                    col=col_config
                )
                memory_cards.append(memory_card)
            
            responsive_row = ft.ResponsiveRow(memory_cards, spacing=10)
            system_info_container.controls.append(responsive_row)
        else:
            memory_card = create_card(
                title="メモリ",
                content_controls=[
                    ft.Text("メモリ情報の形式が不正です。", size=font_size, color=ft.Colors.RED)
                ],
                icon_filename="memory.png",
                layout="single_column",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
            responsive_row = ft.ResponsiveRow([memory_card], spacing=10)
            system_info_container.controls.append(responsive_row)

        # マザーボード情報カードの作成
        if isinstance(motherboard_info, dict):
            motherboard_card = create_card(
                title="マザーボード",
                content_controls=[
                    create_label_value_row(
                        "モデル番号:", motherboard_info.get('Model', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row(
                        "BIOSバージョン:", motherboard_info.get('BIOSVersion', 'Unknown'), label_width=label_width, font_size=font_size)
                ],
                icon_filename="device_hub.png",
                layout="single_column",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
        else:
            motherboard_card = create_card(
                title="マザーボード",
                content_controls=[
                    create_label_value_row("モデル番号:", str(
                        motherboard_info) if motherboard_info else 'Unknown', label_width=label_width, font_size=font_size)
                ],
                icon_filename="device_hub.png",
                layout="single_column",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
        responsive_row = ft.ResponsiveRow([motherboard_card], spacing=10)
        system_info_container.controls.append(responsive_row)

        # GPU情報カードの作成
        if isinstance(gpu_info, list) and all(isinstance(gpu, dict) for gpu in gpu_info):
            gpu_cards = []
            for idx, gpu in enumerate(gpu_info, start=1):
                gpu_title = f"GPU{idx}"
                module_items = [
                    ft.Text(gpu_title, size=font_size, weight=ft.FontWeight.BOLD),
                    create_label_value_row(
                        "モデル番号:", gpu.get('ModelNumber', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row(
                        "メモリ容量:", gpu.get('AdapterRAMGB', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row(
                        "ドライバーバージョン:", gpu.get('DriverVersion', 'Unknown'), label_width=label_width, font_size=font_size),
                ]
                gpu_card = create_card(
                    title="GPU",
                    content_controls=module_items,
                    icon_filename="video_library.png",
                    layout="numbered",
                    icon_size=icon_size,
                    font_size=font_size,
                    padding=padding,
                    spacing=spacing,
                    col=col_config
                )
                gpu_cards.append(gpu_card)
            
            responsive_row = ft.ResponsiveRow(gpu_cards, spacing=10)
            system_info_container.controls.append(responsive_row)
        else:
            gpu_card = create_card(
                title="GPU",
                content_controls=[
                    ft.Text("GPU情報の形式が不正です。", size=font_size, color=ft.Colors.RED)
                ],
                icon_filename="video_library.png",
                layout="single_column",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
            responsive_row = ft.ResponsiveRow([gpu_card], spacing=10)
            system_info_container.controls.append(responsive_row)

        # ストレージ情報カードの作成
        if isinstance(storage_devices, list) and all(isinstance(storage, dict) for storage in storage_devices):
            storage_cards = []
            for idx, storage in enumerate(storage_devices, start=1):
                storage_title = f"ディスク{idx}"
                module_items = [
                    ft.Text(storage_title, size=font_size,
                            weight=ft.FontWeight.BOLD),
                    create_label_value_row(
                        "モデル番号:", storage.get('ModelNumber', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row(
                        "サイズ:", storage.get('SizeGB', 'Unknown'), label_width=label_width, font_size=font_size),
                ]
                storage_card = create_card(
                    title="ストレージ",
                    content_controls=module_items,
                    icon_filename="disk.png",
                    layout="numbered",
                    icon_size=icon_size,
                    font_size=font_size,
                    padding=padding,
                    spacing=spacing,
                    col=col_config
                )
                storage_cards.append(storage_card)
            
            responsive_row = ft.ResponsiveRow(storage_cards, spacing=10)
            system_info_container.controls.append(responsive_row)
        else:
            storage_card = create_card(
                title="ストレージ",
                content_controls=[
                    ft.Text("ストレージ情報の形式が不正です。", size=font_size, color=ft.Colors.RED)
                ],
                icon_filename="disk.png",
                layout="single_column",
                icon_size=icon_size,
                font_size=font_size,
                padding=padding,
                spacing=spacing,
                col=col_config
            )
            responsive_row = ft.ResponsiveRow([storage_card], spacing=10)
            system_info_container.controls.append(responsive_row)

        # テキスト形式での情報出力
        info_text = "=" * 80 + "\n"
        info_text += f"PC Information Log - {datetime.now().strftime('%Y/%m/%d %H:%M')}\n"
        info_text += "=" * 80 + "\n\n"

        # OS情報
        info_text += f"[OS]\n"
        info_text += f"  名称             : {os_name}\n"
        info_text += f"  バージョン       : {os_version}\n"
        info_text += "-" * 80 + "\n\n"

        # CPU情報
        if isinstance(cpu_info, dict):
            cpu_name = str(cpu_info.get('Name', 'Unknown')).strip()
            stepping = cpu_info.get('Stepping', 'Unknown')
            revision = cpu_info.get('Revision', 'Unknown')
            info_text += f"[CPU]\n"
            info_text += f"  名称             : {cpu_name}\n"
            info_text += f"  コア数           : {cpu_info.get('NumberOfCores', 'Unknown')}\n"
            info_text += f"  スレッド数       : {cpu_info.get('NumberOfLogicalProcessors', 'Unknown')}\n"
            info_text += f"  最大クロック速度 : {cpu_info.get('MaxClockSpeed', 'Unknown')} MHz\n"
            info_text += f"  リビジョン       : {revision}\n"
            info_text += f"  ステッピング     : {stepping}\n"
            info_text += "-" * 80 + "\n\n"
        else:
            info_text += "[CPU]\n  取得に失敗しました\n"
            info_text += "-" * 80 + "\n\n"

        # メモリ情報
        if isinstance(memory_modules, list) and all(isinstance(module, dict) for module in memory_modules):
            for idx, module in enumerate(memory_modules, start=1):
                info_text += f"[メモリ モジュール{idx}]\n"
                info_text += f"  モデル番号       : {module.get('ManufacturerAndModel', 'Unknown')}\n"
                info_text += f"  クロック速度     : {module.get('Speed', 'Unknown')}\n"
                info_text += f"  容量             : {module.get('Capacity', 'Unknown')}\n"
                info_text += "-" * 80 + "\n\n"
        else:
            info_text += "[メモリ]\n  取得に失敗しました\n"
            info_text += "-" * 80 + "\n\n"

        # マザーボード情報
        if isinstance(motherboard_info, dict):
            info_text += f"[マザーボード]\n"
            info_text += f"  モデル番号       : {motherboard_info.get('Model', 'Unknown')}\n"
            info_text += f"  BIOSバージョン   : {motherboard_info.get('BIOSVersion', 'Unknown')}\n"
            info_text += "-" * 80 + "\n\n"
        else:
            info_text += f"[マザーボード]\n"
            info_text += f"  モデル番号       : {motherboard_info if motherboard_info else 'Unknown'}\n"
            info_text += "-" * 80 + "\n\n"

        # GPU情報
        if isinstance(gpu_info, list) and all(isinstance(gpu, dict) for gpu in gpu_info):
            for idx, gpu in enumerate(gpu_info, start=1):
                info_text += f"[GPU{idx}]\n"
                info_text += f"  モデル番号       : {gpu.get('ModelNumber', 'Unknown')}\n"
                info_text += f"  メモリ容量       : {gpu.get('AdapterRAMGB', 'Unknown')}\n"
                info_text += f"  ドライバーバージョン: {gpu.get('DriverVersion', 'Unknown')}\n"
                info_text += "-" * 80 + "\n\n"
        else:
            info_text += "[GPU]\n  取得に失敗しました\n"
            info_text += "-" * 80 + "\n\n"

        # ストレージ情報
        if isinstance(storage_devices, list) and all(isinstance(storage, dict) for storage in storage_devices):
            for idx, storage in enumerate(storage_devices, start=1):
                info_text += f"[ストレージ ディスク{idx}]\n"
                info_text += f"  モデル番号       : {storage.get('ModelNumber', 'Unknown')}\n"
                info_text += f"  サイズ           : {storage.get('SizeGB', 'Unknown')}\n"
                info_text += "-" * 80 + "\n\n"
        else:
            info_text += "[ストレージ]\n  取得に失敗しました\n"
            info_text += "-" * 80 + "\n\n"

        # フッター
        info_text += "=" * 80 + "\n"

        # テキストファイルに情報を保存
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M")
            file_name = f"PC_info_log_{timestamp}.txt"

            # log フォルダのパスを設定 (実行ファイルと同じディレクトリに保存)
            log_folder = os.path.join(get_executable_dir(), "log")
            os.makedirs(log_folder, exist_ok=True)  # log フォルダが存在しない場合は作成
            file_path = os.path.join(log_folder, file_name)

            with open(file_path, "w", encoding="utf-8") as f:
                f.write(info_text)
            logger.info(f"PC情報を '{file_path}' に保存しました。")
        except Exception as file_error:
            logger.exception("PC情報のテキストファイルへの保存中にエラーが発生しました:")
            # エラーダイアログを表示
            error_dialog = ft.AlertDialog(
                title=ft.Text("エラー", size=12),
                content=ft.Column([
                    ft.Text("PC情報のテキストファイルへの保存中にエラーが発生しました。", size=12),
                    ft.Text(str(file_error), color=ft.Colors.RED, size=12),
                ]),
                actions=[ft.TextButton(
                    "OK", on_click=lambda e: close_dialog(error_dialog, page))],
                on_dismiss=lambda e: close_dialog(error_dialog, page),
            )
            page.overlay.append(error_dialog)
            error_dialog.open = True

        # 成功時のダイアログ
        success_dialog = ft.AlertDialog(
            content=ft.Text(
                f"PC情報の取得が成功しました。'{file_name}' にログを保存しました。", size=12),
            actions=[ft.TextButton(
                "OK", on_click=lambda e: close_dialog(success_dialog, page))],
            on_dismiss=lambda e: close_dialog(success_dialog, page),
        )
        page.overlay.append(success_dialog)
        success_dialog.open = True

    except Exception as e:
        # エラーダイアログを表示
        logger.exception("PC情報の取得中にエラーが発生しました。")
        error_dialog = ft.AlertDialog(
            title=ft.Text("エラー", size=12),
            content=ft.Column([
                ft.Text("PC情報の取得中にエラーが発生しました。", size=12),
                ft.Text(str(e), color=ft.Colors.RED, size=12),
            ]),
            actions=[ft.TextButton(
                "OK", on_click=lambda e: close_dialog(error_dialog, page))],
            on_dismiss=lambda e: close_dialog(error_dialog, page),
        )
        page.overlay.append(error_dialog)
        error_dialog.open = True
    finally:
        hide_loading_dialog(page, loading_dialog)


####################
#    GPU診断
####################


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
    sizes = get_responsive_sizes(page)
    font_size = sizes['font_size_normal']

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
            log_filepath = gpu_diagnostics.save_gpu_diagnostics_log(
                gpu_status_list)
            if log_filepath:
                logger.info(f"GPU診断ログを保存しました: {log_filepath}")
                show_success_dialog(page, "GPU診断が完了し、ログが保存されました。")
            else:
                show_error_dialog(page, "エラー", "GPU診断ログの保存に失敗しました。", "")
        else:
            show_error_dialog(page, "エラー", "GPU情報の取得に失敗しました。", "")

        # ログファイル一覧を更新
        display_gpu_log_list(page, gpu_list_view,
                             gpu_table_container, selected_gpu_log)

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
    sizes = get_responsive_sizes(page)
    font_size = sizes['font_size_normal']
    icon_size = sizes['icon_size']
    label_width = sizes['label_width']
    padding = sizes['padding']
    spacing = sizes['spacing']

    gpu_table_container.controls.clear()
    if not gpu_data:
        gpu_table_container.controls.append(
            ft.Text("ログファイルの内容を読み込めませんでした。", size=font_size)
        )
    else:
        base_path = get_base_path()
        icon_path = os.path.join(base_path, "icons", "video_library.png")

        # レスポンシブグリッド設定（最大4枚横並び）
        col_config = {"xs": 12, "sm": 12, "md": 6, "lg": 4, "xl": 3, "xxl": 3}
        
        gpu_cards = []
        for idx, gpu in enumerate(gpu_data, start=1):
            device_name = gpu.get('Name', 'Unknown')

            gpu_card = ft.Container(
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
                                        f"GPU{idx}: {device_name}", size=font_size, weight=ft.FontWeight.BOLD)
                                ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                create_label_value_row("Status:", gpu.get(
                                    'Status', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Error Code:", gpu.get(
                                    'Error Code', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Error Description:", gpu.get(
                                    'Error Description', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Driver Version:", gpu.get(
                                    'Driver Version', 'Unknown'), label_width, font_size=font_size),
                                create_label_value_row("Driver Date:", gpu.get(
                                    'Driver Date', 'Unknown'), label_width, font_size=font_size),
                            ],
                            spacing=spacing
                        ),
                        padding=padding
                    ),
                    elevation=3,
                ),
                margin=ft.margin.symmetric(vertical=spacing, horizontal=5),
                col=col_config
            )
            gpu_cards.append(gpu_card)
        
        responsive_row = ft.ResponsiveRow(gpu_cards, spacing=10)
        gpu_table_container.controls.append(responsive_row)
    page.update()


def main(page: ft.Page) -> None:
    """
    Fletアプリケーションのメイン関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
    """
    # 管理者権限の確認とログ記録
    admin_status = is_admin()
    if admin_status:
        logger.info("アプリケーションは管理者権限で実行されています。")
        admin_text = " (管理者)"
    else:
        logger.info("アプリケーションは標準ユーザー権限で実行されています。")
        admin_text = ""

    # ページの設定
    page.title = f"PcInfo{admin_text}"
    page.padding = 20
    page.window.width = WINDOW_WIDTH_DEFAULT
    page.window.height = WINDOW_HEIGHT_DEFAULT
    page.window.min_width = WINDOW_MIN_WIDTH
    page.window.min_height = WINDOW_MIN_HEIGHT
    page.window.resizable = True  # ウィンドウのリサイズを有効化

    # 選択されたストレージ診断ログファイル名を保持する変数
    selected_storage_log = ft.Ref[str]()

    # 選択されたメモリ診断ログファイル名を保持する変数
    selected_memory_log = ft.Ref[str]()

    # 選択されたGPU診断ログファイル名を保持する変数
    selected_gpu_log = ft.Ref[str]()

    # メモリ診断用の ListView と TableContainer
    memory_list_view = ft.ListView(expand=True)
    memory_table_container = ft.Column(
        controls=[ft.Text("ここにメモリ診断ログの詳細が表示されます。", size=12)],
        expand=True,
    )

    # ストレージ診断用の ListView と TableContainer
    storage_list_view = ft.ListView(expand=True)
    storage_table_container = ft.Column(
        controls=[ft.Text("ここに選択されたログの詳細が表示されます。", size=12)],
        expand=True,
    )

    # GPU診断用の ListView と TableContainer
    gpu_list_view = ft.ListView(expand=True)
    gpu_table_container = ft.Column(
        controls=[ft.Text("ここにGPU診断ログの詳細が表示されます。", size=12)],
        expand=True,
    )

    # PC情報用の Containerをft.Columnに変更
    system_info_container = ft.Column(
        controls=[],
        expand=True,
    )

    # タブ1の内容（PC情報）
    tab1_content = ft.Column(
        [
            ft.Container(height=5),
            ft.ElevatedButton(
                content=ft.Text("PC構成の取得", size=12),
                on_click=lambda e: display_system_info(
                    page, system_info_container
                ),
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(
                content=system_info_container,
                expand=True,
            ),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ2の内容（メモリ診断）
    tab2_content = ft.Column(
        [
            ft.Container(height=5),
            ft.Row(
                [
                    ft.ElevatedButton(
                        content=ft.Text("メモリ診断結果の表示", size=12),
                        on_click=lambda e: display_memory_diagnostics(
                            page, memory_list_view, memory_table_container, selected_memory_log
                        ),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("Windowsメモリ診断の実行", size=12),
                        on_click=lambda e: diagnostics.run_memory_diagnostics(),
                    ),
                ],
                spacing=10
            ),
            ft.Text("診断ログ一覧:", size=12, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=memory_list_view,
                height=LIST_VIEW_HEIGHT,
                expand=True,  # 幅を親コンテナに合わせる
                border=ft.border.all(1.5, ft.Colors.GREY),
                padding=10,
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=memory_table_container, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ3(ストレージ診断)
    tab3_content = ft.Column(
        [
            ft.Container(height=5),
            ft.Row(
                [
                    ft.ElevatedButton(
                        content=ft.Text("診断結果の表示", size=12),
                        on_click=lambda e: display_storage_diagnostics(
                            page, storage_list_view, storage_table_container, selected_storage_log
                        ),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("S.M.A.R.T.の取得", size=12),
                        on_click=lambda e: display_storage_diagnostics_with_dialog(
                            page),
                    ),
                ],
                spacing=10
            ),
            ft.Text("診断ログ一覧:", size=12, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=storage_list_view,
                height=LIST_VIEW_HEIGHT,
                expand=True,  # 幅を親コンテナに合わせる
                border=ft.border.all(1.5, ft.Colors.GREY),
                padding=10,
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=storage_table_container, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ4(GPU診断)
    tab4_content = ft.Column(
        [
            ft.Container(height=5),
            ft.Row(
                [
                    ft.ElevatedButton(
                        content=ft.Text("診断結果の表示", size=12),
                        on_click=lambda e: display_gpu_log_list(
                            page, gpu_list_view, gpu_table_container, selected_gpu_log
                        ),
                    ),
                    ft.ElevatedButton(
                        content=ft.Text("GPU情報の取得", size=12),
                        on_click=lambda e: display_gpu_diagnostics(
                            page, gpu_list_view, gpu_table_container, selected_gpu_log
                        ),
                    ),
                ],
                spacing=10
            ),
            ft.Text("診断ログ一覧:", size=12, weight=ft.FontWeight.BOLD),
            ft.Container(
                content=gpu_list_view,
                height=LIST_VIEW_HEIGHT,
                expand=True,  # 幅を親コンテナに合わせる
                border=ft.border.all(1.5, ft.Colors.GREY),
                padding=10,
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=gpu_table_container, expand=True),
        ],
        scroll=ft.ScrollMode.AUTO
    )

    # タブ構成
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="PC情報", content=tab1_content),
            ft.Tab(text="メモリ診断", content=tab2_content),
            ft.Tab(text="ストレージ診断", content=tab3_content),
            ft.Tab(text="GPU診断", content=tab4_content),
        ],
        expand=True,
    )

    # ページ構成
    page.add(tabs)


# Fletアプリケーションの実行
ft.app(target=main)
