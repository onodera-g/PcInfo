# main.py

import flet as ft
import os
import diagnostics
import storage_diagnostics
import system_info
from datetime import datetime
import sys
from typing import Optional, Union, Dict, List

import logging

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 必要に応じてレベルを調整

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_base_path() -> str:
    """
    実行ファイルのディレクトリを取得します。
    PyInstallerでコンパイルされた場合でも対応します。

    Returns:
        str: 実行ファイルのディレクトリパス。
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerでコンパイルされた場合
        base_path = os.path.dirname(sys.executable)
    else:
        # 開発環境の場合
        base_path = os.path.dirname(os.path.abspath(__file__))
    logger.debug(f"Base path: {base_path}")
    return base_path


######################
#   ストレージ診断
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
    if not results:
        storage_list_view.controls.append(ft.Text("ログファイルが存在しません。"))
    else:
        for result in results:
            storage_list_view.controls.append(
                ft.ListTile(
                    title=ft.Text(result),
                    on_click=lambda e, res=result: (
                        display_storage_log_content(
                            page, res, storage_table_container
                        ),
                        setattr(selected_storage_log, 'current', res),
                        page.update()
                    ),
                    selected=(selected_storage_log.current == result),
                    selected_color=ft.colors.BLUE,
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

    storage_table_container.controls.clear()
    if not disk_data:
        storage_table_container.controls.append(
            ft.Text("ログファイルの内容を読み込めませんでした。")
        )
    else:
        label_width = 120  # ラベル部分の固定幅を調整
        base_path = get_base_path()
        icon_path = os.path.join(base_path, "icons", "disk.png")

        for idx, disk in enumerate(disk_data, start=1):
            storage_card = ft.Container(
                width=700,  # 横幅を統一
                content=ft.Card(
                    content=ft.Container(
                        content=ft.Column(
                            [
                                ft.Row([
                                    ft.Image(
                                        src=icon_path,
                                        width=24,
                                        height=24,
                                    ),
                                    ft.Text(f"ディスク {idx}",
                                            size=16, weight="bold")  # module_titleを太字に設定
                                ],
                                    vertical_alignment=ft.CrossAxisAlignment.CENTER),
                                create_label_value_row("Disk Size:", disk.get(
                                    'Disk Size', 'Unknown'), label_width),
                                create_label_value_row("Interface:", disk.get(
                                    'Interface', 'Unknown'), label_width),
                                create_label_value_row("Power On Hours:", disk.get(
                                    'Power On Hours', 'Unknown'), label_width),
                                create_label_value_row("Power On Count:", disk.get(
                                    'Power On Count', 'Unknown'), label_width),
                                create_label_value_row("Host Writes:", disk.get(
                                    'Host Writes', 'Unknown'), label_width),
                                create_label_value_row("Health Status:", disk.get(
                                    'Health Status', 'Unknown'), label_width),
                            ],
                            spacing=5  # 行間のスペースを減少
                        ),
                        padding=10
                    ),
                    elevation=3,
                    margin=ft.margin.symmetric(vertical=5),
                ),
                animate={"duration": 500,
                         "curve": ft.AnimationCurve.EASE_IN_OUT},
            )
            storage_table_container.controls.append(storage_card)
    page.update()


def display_storage_diagnostics_with_dialog(page: ft.Page) -> None:
    """
    ストレージ診断を実行し、結果をダイアログで表示する関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
    """
    # ローディングインジケーターを表示
    base_path = get_base_path()
    loading_icon_path = os.path.join(
        base_path, "icons", "circular_progress.png")

    loading_dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Image(
                src=loading_icon_path,
                width=24,
                height=24,
            ),
            ft.Text("情報を取得中...", size=16)
        ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        content=ft.ProgressBar(width=200),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.START,
        modal=False,
    )
    page.overlay.append(loading_dialog)
    loading_dialog.open = True
    page.update()

    try:
        result = storage_diagnostics.get_CrystalDiskInfo_log()  # ストレージ診断を実行
        if result:
            # 成功時のダイアログ
            success_dialog = ft.AlertDialog(
                content=ft.Text("ストレージ診断が実行され、ログが保存されました。"),
                actions=[
                    ft.TextButton(
                        "OK", on_click=lambda e: close_dialog(success_dialog, page)
                    )
                ],
                on_dismiss=lambda e: close_dialog(success_dialog, page),
            )
            page.overlay.append(success_dialog)
            success_dialog.open = True
        else:
            # 失敗時のダイアログ
            error_dialog = ft.AlertDialog(
                title=ft.Text("エラー"),
                content=ft.Text("ストレージ診断の実行に失敗しました。"),
                actions=[
                    ft.TextButton(
                        "OK", on_click=lambda e: close_dialog(error_dialog, page))
                ],
                on_dismiss=lambda e: close_dialog(error_dialog, page),
            )
            page.overlay.append(error_dialog)
            error_dialog.open = True

    finally:
        # ローディングインジケーターを閉じる
        if loading_dialog in page.overlay:
            page.overlay.remove(loading_dialog)
        page.update()

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
    base_path = get_base_path()
    loading_icon_path = os.path.join(
        base_path, "icons", "circular_progress.png")

    loading_dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Image(
                src=loading_icon_path,
                width=24,
                height=24,
            ),
            ft.Text("情報を取得中...", size=16)
        ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        content=ft.ProgressBar(width=200),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.START,
        modal=False,
    )
    page.overlay.append(loading_dialog)
    loading_dialog.open = True
    page.update()

    try:
        results = diagnostics.search_memory_log()  # 診断結果を取得
        memory_list_view.controls.clear()
        logger.debug(f"Memory Logs: {results}")  # デバッグ用
        # 成功時のダイアログ
        success_dialog = ft.AlertDialog(
            content=ft.Text("診断結果の検索が終了しました。"),
            actions=[
                ft.TextButton(
                    "OK", on_click=lambda e: close_dialog(success_dialog, page)
                )
            ],
            on_dismiss=lambda e: close_dialog(success_dialog, page),
        )
        page.overlay.append(success_dialog)
        success_dialog.open = True
        # 　リストに並べる
        if not results:
            memory_list_view.controls.append(ft.Text("ログファイルが存在しません。"))
        else:
            # リストに並べる
            for result in results:
                memory_list_view.controls.append(
                    ft.ListTile(
                        title=ft.Text(
                            f"EventID: {getattr(
                                result, 'EventCode', 'Unknown')} - {getattr(result, 'TimeGenerated', 'Unknown')}"
                        ),
                        on_click=lambda e, res=result: (
                            display_memory_log_content(
                                page, res, memory_table_container
                            ),
                            setattr(selected_memory_log, 'current', res),
                            page.update()
                        ),
                        selected=(selected_memory_log.current == result),
                        selected_color=ft.colors.BLUE,
                    )
                )
    finally:
        # ローディングインジケーターを閉じる
        if loading_dialog in page.overlay:
            page.overlay.remove(loading_dialog)
        page.update()


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
    label_width = 120  # ラベル部分の固定幅を調整

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

    base_path = get_base_path()
    memory_icon_path = os.path.join(base_path, "icons", "memory.png")

    memory_card = ft.Container(
        width=700,  # 横幅を統一
        content=ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Image(
                                src=memory_icon_path,
                                width=24,
                                height=24,
                            ),
                            ft.Text("ログの詳細", size=16, weight="bold")  # タイトルは太字
                        ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        create_label_value_row(
                            "SourceName:", f"{source_name}", label_width),
                        create_label_value_row(
                            "Event ID:", f"{event_code}", label_width),
                        create_label_value_row("Time Generated:", f"{
                                               time_generated}", label_width),
                        create_label_value_row(
                            "Message:", f"{message}", label_width),
                    ],
                    spacing=5  # 行間のスペースを減少
                ),
                padding=10
            ),
            elevation=3,
            margin=ft.margin.symmetric(vertical=5),
        ),
        animate={"duration": 500, "curve": ft.AnimationCurve.EASE_IN_OUT},
    )
    memory_table_container.controls.append(memory_card)
    page.update()


####################
#    システム情報
####################


def create_label_value_row(label: str, value: str, label_width: float = 120, value_width: Optional[float] = None) -> ft.Row:
    """
    ラベルと値を含むRowを作成するヘルパー関数。

    Parameters:
        label (str): ラベルテキスト。
        value (str): 値テキスト。
        label_width (float): ラベル部分の固定幅。
        value_width (Optional[float]): 値部分の固定幅。デフォルトはNone。

    Returns:
        ft.Row: ラベルと値を含むRowオブジェクト。
    """
    return ft.Row([
        ft.Text(label, size=14, width=label_width, weight="bold"),
        ft.Text(value, size=14, width=value_width if value_width else None)
    ],
        vertical_alignment=ft.CrossAxisAlignment.START
    )


def create_card(
    title: str, content_controls: List[ft.Control], icon_filename: str, width: float = 700, layout: str = "single_column"
) -> ft.Container:
    """
    汎用的なカードを作成するヘルパー関数。

    Parameters:
        title (str): カードのタイトル。
        content_controls (List[ft.Control]): カード内のコンテンツコントロールのリスト。
        icon_filename (str): アイコンファイル名。
        width (float): カードの横幅。
        layout (str): レイアウトタイプ（"single_column", "numbered"）。

    Returns:
        ft.Container: 作成されたカードのコンテナ。
    """
    base_path = get_base_path()
    icon_path = os.path.join(base_path, "icons", icon_filename)

    if layout == "numbered":
        content = ft.Column(
            [control for group in content_controls for control in group],
            spacing=3,  # 行間のスペースを減少
            expand=True
        )
    else:
        content = ft.Column(
            content_controls,
            spacing=5,  # 行間のスペースを減少
            expand=True
        )

    return ft.Container(
        width=width,  # 横幅を統一
        content=ft.Card(
            content=ft.Container(
                content=ft.Column(
                    [
                        ft.Row([
                            ft.Image(
                                src=icon_path,
                                width=24,
                                height=24,
                            ),
                            ft.Text(title, size=16, weight="bold")
                        ],
                            vertical_alignment=ft.CrossAxisAlignment.CENTER),
                        content
                    ],
                    spacing=5  # 行間のスペースを減少
                ),
                padding=10
            ),
            elevation=3,
            margin=ft.margin.symmetric(vertical=5),
        ),
        animate={"duration": 500, "curve": ft.AnimationCurve.EASE_IN_OUT},
    )


def display_system_info(page: ft.Page, system_info_container: ft.Column) -> None:
    """
    PC情報を取得して表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        system_info_container (ft.Column): システム情報を表示するコンテナ。
    """
    # ローディングインジケーターを表示
    base_path = get_base_path()
    loading_icon_path = os.path.join(
        base_path, "icons", "circular_progress.png")

    loading_dialog = ft.AlertDialog(
        title=ft.Row([
            ft.Image(
                src=loading_icon_path,
                width=24,
                height=24,
            ),
            ft.Text("情報を取得中...", size=16)
        ],
            vertical_alignment=ft.CrossAxisAlignment.CENTER),
        content=ft.ProgressBar(width=200),
        actions=[],
        actions_alignment=ft.MainAxisAlignment.START,
        modal=True,
    )
    page.overlay.append(loading_dialog)
    loading_dialog.open = True
    page.update()

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

        # OS情報カードの作成
        os_name, os_version = os_info
        os_card = create_card(
            title="OS",
            content_controls=[
                create_label_value_row("名称:", os_name),
                create_label_value_row("バージョン:", os_version),
            ],
            icon_filename="computer.png",
            width=700,
            layout="single_column"
        )
        system_info_container.controls.append(os_card)

        # CPU情報カードの作成
        if isinstance(cpu_info, dict):
            cpu_items_text = [
                create_label_value_row(
                    "名称:", cpu_info.get('Name', 'Unknown').strip()),
                create_label_value_row(
                    "コア数:", f"{cpu_info.get('NumberOfCores', 'Unknown')}"),
                create_label_value_row("スレッド数:", f"{cpu_info.get(
                    'NumberOfLogicalProcessors', 'Unknown')}"),
                create_label_value_row(
                    "最大クロック速度:", f"{cpu_info.get('MaxClockSpeed', 'Unknown')} MHz"),
            ]
            cpu_card = create_card(
                title="CPU",
                content_controls=cpu_items_text,
                icon_filename="chip.png",
                width=700,
                layout="single_column"
            )
            system_info_container.controls.append(cpu_card)
        else:
            cpu_card = create_card(
                title="CPU",
                content_controls=[
                    ft.Text("CPU情報の形式が不正です。", size=14, color=ft.colors.RED)],
                icon_filename="chip.png",
                width=700,
                layout="single_column"
            )
            system_info_container.controls.append(cpu_card)

        # メモリ情報カードの作成
        if isinstance(memory_modules, list) and all(isinstance(module, dict) for module in memory_modules):
            memory_pairs = [memory_modules[i:i + 2]
                            for i in range(0, len(memory_modules), 2)]
            for pair in memory_pairs:
                modules_info = []
                for module in pair:
                    module_title = f"モジュール"
                    module_items = [
                        ft.Text(module_title, size=14, weight="bold"),
                        create_label_value_row("モデル番号:", module.get(
                            'ManufacturerAndModel', 'Unknown')),
                        create_label_value_row(
                            "クロック速度:", module.get('Speed', 'Unknown')),
                        create_label_value_row(
                            "容量:", module.get('Capacity', 'Unknown')),
                    ]
                    modules_info.append(module_items)
                memory_card = create_card(
                    title="メモリー",
                    content_controls=modules_info,
                    icon_filename="memory.png",
                    width=700,
                    layout="numbered"
                )
                system_info_container.controls.append(memory_card)
        else:
            memory_card = create_card(
                title="メモリ",
                content_controls=[
                    [ft.Text("メモリ情報の形式が不正です。", size=14, color=ft.colors.RED)]
                ],
                icon_filename="memory.png",
                width=700,
                layout="numbered"
            )
            system_info_container.controls.append(memory_card)

        # マザーボード情報カードの作成
        motherboard_card = create_card(
            title="マザーボード",
            content_controls=[create_label_value_row(
                "モデル番号:", motherboard_info if motherboard_info else 'Unknown')],
            icon_filename="device_hub.png",
            width=700,
            layout="single_column"
        )
        system_info_container.controls.append(motherboard_card)

        # GPU情報カードの作成
        if isinstance(gpu_info, list) and all(isinstance(gpu, dict) for gpu in gpu_info):
            gpu_pairs = [gpu_info[i:i + 2] for i in range(0, len(gpu_info), 2)]
            for pair in gpu_pairs:
                modules_info = []
                for gpu in pair:
                    module_title = f"GPU"
                    module_items = [
                        ft.Text(module_title, size=14, weight="bold"),
                        create_label_value_row(
                            "モデル番号:", gpu.get('ModelNumber', 'Unknown')),
                        create_label_value_row(
                            "メモリ容量:", gpu.get('AdapterRAMGB', 'Unknown')),
                        create_label_value_row(
                            "ドライバーバージョン:", gpu.get('DriverVersion', 'Unknown')),
                    ]
                    modules_info.append(module_items)
                gpu_card = create_card(
                    title="GPU",
                    content_controls=modules_info,
                    icon_filename="video_library.png",
                    width=700,
                    layout="numbered"
                )
                system_info_container.controls.append(gpu_card)
        else:
            gpu_card = create_card(
                title="GPU",
                content_controls=[
                    [ft.Text("GPU情報の形式が不正です。", size=14, color=ft.colors.RED)]
                ],
                icon_filename="video_library.png",
                width=700,
                layout="numbered"
            )
            system_info_container.controls.append(gpu_card)

        # ストレージ情報カードの作成
        if isinstance(storage_devices, list) and all(isinstance(storage, dict) for storage in storage_devices):
            storage_pairs = [storage_devices[i:i + 2]
                             for i in range(0, len(storage_devices), 2)]
            for pair in storage_pairs:
                modules_info = []
                for storage in pair:
                    module_title = f"ディスク"
                    module_items = [
                        ft.Text(module_title, size=14, weight="bold"),
                        create_label_value_row(
                            "モデル番号:", storage.get('ModelNumber', 'Unknown')),
                        create_label_value_row(
                            "サイズ:", storage.get('SizeGB', 'Unknown')),
                    ]
                    modules_info.append(module_items)
                storage_card = create_card(
                    title="ストレージ",
                    content_controls=modules_info,
                    icon_filename="disk.png",
                    width=700,
                    layout="numbered"
                )
                system_info_container.controls.append(storage_card)
        else:
            storage_card = create_card(
                title="ストレージ",
                content_controls=[
                    [ft.Text("ストレージ情報の形式が不正です。", size=14, color=ft.colors.RED)]
                ],
                icon_filename="disk.png",
                width=700,
                layout="numbered"
            )
            system_info_container.controls.append(storage_card)

        # テキスト形式での情報出力
        info_text = f"--- PC情報詳細 ---\n\n"

        # OS情報
        info_text += f"OS:\n  名称: {os_name}\n  バージョン: {os_version}\n\n"

        # CPU情報
        if isinstance(cpu_info, dict):
            info_text += f"CPU:\n"
            info_text += f"  名称: {cpu_info.get('Name', 'Unknown').strip()}\n"
            info_text += f"  コア数: {cpu_info.get('NumberOfCores', 'Unknown')}\n"
            info_text += f"  スレッド数: {cpu_info.get(
                'NumberOfLogicalProcessors', 'Unknown')}\n"
            info_text += f"  最大クロック速度: {cpu_info.get(
                'MaxClockSpeed', 'Unknown')} MHz\n\n"
        else:
            info_text += "CPU情報の形式が不正です。\n\n"

        # メモリ情報
        if isinstance(memory_modules, list) and all(isinstance(module, dict) for module in memory_modules):
            for idx, module in enumerate(memory_modules, start=1):
                info_text += f"メモリ モジュール{idx}:\n"
                info_text += f"  モデル番号: {module.get(
                    'ManufacturerAndModel', 'Unknown')}\n"
                info_text += f"  クロック速度: {
                    module.get('Speed', 'Unknown')} MHz\n"
                info_text += f"  容量: {module.get('Capacity',
                                                 'Unknown')} GB\n\n"
        else:
            info_text += "メモリ情報の形式が不正です。\n\n"

        # マザーボード情報
        info_text += f"マザーボード:\n  モデル番号: {
            motherboard_info if motherboard_info else 'Unknown'}\n\n"

        # GPU情報
        if isinstance(gpu_info, list) and all(isinstance(gpu, dict) for gpu in gpu_info):
            for idx, gpu in enumerate(gpu_info, start=1):
                info_text += f"GPU{idx}:\n"
                info_text += f"  モデル番号: {gpu.get('ModelNumber', 'Unknown')}\n"
                info_text += f"  メモリ容量: {gpu.get('AdapterRAMGB',
                                                 'Unknown')} GB\n"
                info_text += f"  ドライバーバージョン: {
                    gpu.get('DriverVersion', 'Unknown')}\n\n"
        else:
            info_text += "GPU情報の形式が不正です。\n\n"

        # ストレージ情報
        if isinstance(storage_devices, list) and all(isinstance(storage, dict) for storage in storage_devices):
            for idx, storage in enumerate(storage_devices, start=1):
                info_text += f"ストレージ ディスク{idx}:\n"
                info_text += f"  モデル番号: {
                    storage.get('ModelNumber', 'Unknown')}\n"
                info_text += f"  サイズ: {storage.get('SizeGB',
                                                   'Unknown')} GB\n\n"
        else:
            info_text += "ストレージ情報の形式が不正です。\n\n"

        # テキストファイルに情報を保存
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            file_name = f"PC_info_{timestamp}.txt"
            with open(file_name, "w", encoding="utf-8") as f:
                f.write(info_text)
            logger.info(f"PC情報を '{file_name}' に保存しました。")
        except Exception as file_error:
            logger.exception("PC情報のテキストファイルへの保存中にエラーが発生しました:")
            # エラーダイアログを表示
            error_dialog = ft.AlertDialog(
                title=ft.Text("エラー"),
                content=ft.Column([
                    ft.Text("PC情報のテキストファイルへの保存中にエラーが発生しました。"),
                    ft.Text(str(file_error), color=ft.colors.RED),
                ]),
                actions=[ft.TextButton(
                    "OK", on_click=lambda e: close_dialog(error_dialog, page))],
                on_dismiss=lambda e: close_dialog(error_dialog, page),
            )
            page.overlay.append(error_dialog)
            error_dialog.open = True

        # 成功時のダイアログ
        success_dialog = ft.AlertDialog(
            content=ft.Text(f"PC情報の取得が成功しました。、'{file_name}' にログを保存しました。"),
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
            title=ft.Text("エラー"),
            content=ft.Column([
                ft.Text("PC情報の取得中にエラーが発生しました。"),
                ft.Text(str(e), color=ft.colors.RED),
            ]),
            actions=[ft.TextButton(
                "OK", on_click=lambda e: close_dialog(error_dialog, page))],
            on_dismiss=lambda e: close_dialog(error_dialog, page),
        )
        page.overlay.append(error_dialog)
        error_dialog.open = True
    finally:
        if loading_dialog in page.overlay:
            page.overlay.remove(loading_dialog)
        page.update()


def close_dialog(dialog: ft.AlertDialog, page: ft.Page) -> None:
    """
    ダイアログを閉じるための関数。

    Parameters:
        dialog (ft.AlertDialog): 閉じるダイアログオブジェクト。
        page (ft.Page): Fletのページオブジェクト。
    """
    dialog.open = False
    page.update()


def main(page: ft.Page) -> None:
    """
    Fletアプリケーションのメイン関数。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
    """
    # ページの設定
    page.title = "PcInfo"
    page.padding = 20
    page.window.width = 800     # 横幅を800に設定
    page.window.height = 1100    # 高さを1100に設定

    # 選択されたストレージ診断ログファイル名を保持する変数
    selected_storage_log = ft.Ref[str]()

    # 選択されたメモリ診断ログファイル名を保持する変数
    selected_memory_log = ft.Ref[str]()

    # メモリ診断用の ListView と TableContainer
    memory_list_view = ft.ListView(expand=True)
    memory_table_container = ft.Column(
        controls=[ft.Text("ここにメモリ診断ログの詳細が表示されます。")]
    )

    # ストレージ診断用の ListView と TableContainer
    storage_list_view = ft.ListView(expand=True)
    storage_table_container = ft.Column(
        controls=[ft.Text("ここに選択されたログの詳細が表示されます。")]
    )

    # PC情報用の Containerをft.Columnに変更
    system_info_container = ft.Column(
        controls=[]
    )

    # タブ1の内容（PC情報）
    tab1_content = ft.Column(
        [
            ft.Container(height=5),
            ft.ElevatedButton(
                "PC構成の取得",
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
    )

    # タブ2の内容（メモリ診断）
    tab2_content = ft.Column(
        [
            ft.Container(height=5),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "メモリ診断結果の表示",
                        on_click=lambda e: display_memory_diagnostics(
                            page, memory_list_view, memory_table_container, selected_memory_log
                        ),
                    ),
                    ft.ElevatedButton(
                        "Windowsメモリ診断の実行",
                        on_click=lambda e: diagnostics.run_memory_diagnostics(),
                    ),
                ],
                spacing=10
            ),
            ft.Text("診断ログ一覧:", size=16, weight="bold"),
            ft.Container(
                content=memory_list_view,
                height=150,
                width=700,
                border=ft.border.all(1.5, ft.colors.GREY),
                padding=10,
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=memory_table_container, expand=True),
        ],
    )

    # タブ3(ストレージ診断)
    tab3_content = ft.Column(
        [
            ft.Container(height=5),
            ft.Row(
                [
                    ft.ElevatedButton(
                        "診断結果の表示",
                        on_click=lambda e: display_storage_diagnostics(
                            page, storage_list_view, storage_table_container, selected_storage_log
                        ),
                    ),
                    ft.ElevatedButton(
                        "S.M.A.R.T.の取得",
                        on_click=lambda e: display_storage_diagnostics_with_dialog(
                            page),
                    ),
                ],
                spacing=10
            ),
            ft.Text("診断ログ一覧:", size=16, weight="bold"),
            ft.Container(
                content=storage_list_view,
                height=150,
                width=700,
                border=ft.border.all(1.5, ft.colors.GREY),
                padding=10,
            ),
            ft.Divider(height=20, thickness=2),
            ft.Container(content=storage_table_container, expand=True),
        ],
    )

    # タブ構成
    tabs = ft.Tabs(
        selected_index=0,
        tabs=[
            ft.Tab(text="PC情報", content=tab1_content),
            ft.Tab(text="メモリ診断", content=tab2_content),
            ft.Tab(text="ストレージ診断", content=tab3_content),
        ],
        expand=True,
    )

    # ページ構成
    page.add(tabs)


# Fletアプリケーションの実行
ft.app(target=main)
