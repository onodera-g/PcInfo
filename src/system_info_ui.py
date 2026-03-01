"""
システム情報UI関連の処理モジュール
"""
import flet as ft
import logging
from typing import List, Dict, Any, Union, Tuple
import system_info
from constants import get_responsive_col_config
from ui_helpers import (
    get_responsive_sizes,
    create_label_value_row,
    create_card
)
from dialog_helpers import (
    show_loading_dialog,
    hide_loading_dialog,
    show_error_dialog
)
from log_writer import save_system_info_log

logger = logging.getLogger(__name__)


def create_os_card(
    os_info: Tuple[str, str],
    sizes: Dict[str, int]
) -> ft.Container:
    """OS情報カードを作成"""
    os_name, os_version = os_info
    return create_card(
        title="OS",
        content_controls=[
            create_label_value_row(
                "名称:", os_name,
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "バージョン:", os_version,
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
        ],
        icon_filename="computer.png",
        layout="single_column",
        icon_size=sizes['icon_size'],
        font_size=sizes['font_size_normal'],
        padding=sizes['padding'],
        spacing=sizes['spacing'],
        col=get_responsive_col_config()
    )


def create_cpu_card(
    cpu_info: Union[Dict[str, Any], str],
    sizes: Dict[str, int]
) -> ft.Container:
    """CPU情報カードを作成"""
    if isinstance(cpu_info, dict):
        cpu_name = str(cpu_info.get('Name', 'Unknown')).strip()
        stepping = cpu_info.get('Stepping', 'Unknown')
        revision = cpu_info.get('Revision', 'Unknown')

        content_controls = [
            create_label_value_row(
                "名称:", cpu_name,
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "コア数:", f"{cpu_info.get('NumberOfCores', 'Unknown')}",
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "スレッド数:", f"{cpu_info.get('NumberOfLogicalProcessors', 'Unknown')}",
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "最大クロック速度:", f"{cpu_info.get('MaxClockSpeed', 'Unknown')} MHz",
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "リビジョン:", f"{revision}",
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "ステッピング:", f"{stepping}",
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
        ]
    else:
        content_controls = [
            ft.Text("CPU情報の形式が不正です。",
                    size=sizes['font_size_normal'],
                    color=ft.Colors.RED)
        ]

    return create_card(
        title="CPU",
        content_controls=content_controls,
        icon_filename="chip.png",
        layout="single_column",
        icon_size=sizes['icon_size'],
        font_size=sizes['font_size_normal'],
        padding=sizes['padding'],
        spacing=sizes['spacing'],
        col=get_responsive_col_config()
    )


def create_memory_cards(
    memory_modules: List[Dict[str, str]],
    sizes: Dict[str, int]
) -> List[ft.Container]:
    """メモリ情報カードのリストを作成"""
    if not isinstance(memory_modules, list) or not all(isinstance(m, dict) for m in memory_modules):
        return [create_card(
            title="メモリ",
            content_controls=[
                ft.Text("メモリ情報の形式が不正です。",
                        size=sizes['font_size_normal'],
                        color=ft.Colors.RED)
            ],
            icon_filename="memory.png",
            layout="single_column",
            icon_size=sizes['icon_size'],
            font_size=sizes['font_size_normal'],
            padding=sizes['padding'],
            spacing=sizes['spacing'],
            col=get_responsive_col_config()
        )]

    memory_cards = []
    for idx, module in enumerate(memory_modules, start=1):
        module_title = f"モジュール{idx}"
        module_items = [
            ft.Text(module_title, size=sizes['font_size_normal'],
                    weight=ft.FontWeight.BOLD),
            create_label_value_row(
                "モデル番号:", module.get('ManufacturerAndModel', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "クロック速度:", module.get('Speed', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "容量:", module.get('Capacity', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
        ]
        memory_card = create_card(
            title="メモリー",
            content_controls=module_items,
            icon_filename="memory.png",
            layout="numbered",
            icon_size=sizes['icon_size'],
            font_size=sizes['font_size_normal'],
            padding=sizes['padding'],
            spacing=sizes['spacing'],
            col=get_responsive_col_config()
        )
        memory_cards.append(memory_card)

    return memory_cards


def create_motherboard_card(
    motherboard_info: Union[Dict[str, str], str],
    sizes: Dict[str, int]
) -> ft.Container:
    """マザーボード情報カードを作成"""
    if isinstance(motherboard_info, dict):
        content_controls = [
            create_label_value_row(
                "モデル番号:", motherboard_info.get('Model', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "BIOSバージョン:", motherboard_info.get('BIOSVersion', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            )
        ]
    else:
        content_controls = [
            create_label_value_row(
                "モデル番号:", str(
                    motherboard_info) if motherboard_info else 'Unknown',
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            )
        ]

    return create_card(
        title="マザーボード",
        content_controls=content_controls,
        icon_filename="device_hub.png",
        layout="single_column",
        icon_size=sizes['icon_size'],
        font_size=sizes['font_size_normal'],
        padding=sizes['padding'],
        spacing=sizes['spacing'],
        col=get_responsive_col_config()
    )


def create_gpu_cards(
    gpu_info: List[Dict[str, str]],
    sizes: Dict[str, int]
) -> List[ft.Container]:
    """GPU情報カードのリストを作成"""
    if not isinstance(gpu_info, list) or not all(isinstance(g, dict) for g in gpu_info):
        return [create_card(
            title="GPU",
            content_controls=[
                ft.Text("GPU情報の形式が不正です。",
                        size=sizes['font_size_normal'],
                        color=ft.Colors.RED)
            ],
            icon_filename="video_library.png",
            layout="single_column",
            icon_size=sizes['icon_size'],
            font_size=sizes['font_size_normal'],
            padding=sizes['padding'],
            spacing=sizes['spacing'],
            col=get_responsive_col_config()
        )]

    gpu_cards = []
    for idx, gpu in enumerate(gpu_info, start=1):
        gpu_title = f"GPU{idx}"
        module_items = [
            ft.Text(gpu_title, size=sizes['font_size_normal'],
                    weight=ft.FontWeight.BOLD),
            create_label_value_row(
                "モデル番号:", gpu.get('ModelNumber', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "メモリ容量:", gpu.get('AdapterRAMGB', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "ドライバーバージョン:", gpu.get('DriverVersion', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
        ]
        gpu_card = create_card(
            title="GPU",
            content_controls=module_items,
            icon_filename="video_library.png",
            layout="numbered",
            icon_size=sizes['icon_size'],
            font_size=sizes['font_size_normal'],
            padding=sizes['padding'],
            spacing=sizes['spacing'],
            col=get_responsive_col_config()
        )
        gpu_cards.append(gpu_card)

    return gpu_cards


def create_storage_cards(
    storage_devices: List[Dict[str, str]],
    sizes: Dict[str, int]
) -> List[ft.Container]:
    """ストレージ情報カードのリストを作成"""
    if not isinstance(storage_devices, list) or not all(isinstance(s, dict) for s in storage_devices):
        return [create_card(
            title="ストレージ",
            content_controls=[
                ft.Text("ストレージ情報の形式が不正です。",
                        size=sizes['font_size_normal'],
                        color=ft.Colors.RED)
            ],
            icon_filename="disk.png",
            layout="single_column",
            icon_size=sizes['icon_size'],
            font_size=sizes['font_size_normal'],
            padding=sizes['padding'],
            spacing=sizes['spacing'],
            col=get_responsive_col_config()
        )]

    storage_cards = []
    for idx, storage in enumerate(storage_devices, start=1):
        storage_title = f"ディスク{idx}"
        module_items = [
            ft.Text(storage_title, size=sizes['font_size_normal'],
                    weight=ft.FontWeight.BOLD),
            create_label_value_row(
                "モデル番号:", storage.get('ModelNumber', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
            create_label_value_row(
                "サイズ:", storage.get('SizeGB', 'Unknown'),
                label_width=sizes['label_width'],
                font_size=sizes['font_size_normal']
            ),
        ]
        storage_card = create_card(
            title="ストレージ",
            content_controls=module_items,
            icon_filename="disk.png",
            layout="numbered",
            icon_size=sizes['icon_size'],
            font_size=sizes['font_size_normal'],
            padding=sizes['padding'],
            spacing=sizes['spacing'],
            col=get_responsive_col_config()
        )
        storage_cards.append(storage_card)

    return storage_cards


def display_system_info(
    page: ft.Page,
    system_info_container: ft.Column
) -> None:
    """
    PC情報を取得して表示します。

    Parameters:
        page (ft.Page): Fletのページオブジェクト。
        system_info_container (ft.Column): システム情報を表示するコンテナ。
    """
    loading_dialog = show_loading_dialog(page)
    file_name = ""

    try:
        # PC情報を取得
        os_info = system_info.get_os_info()
        motherboard_info = system_info.get_motherboard_info()
        cpu_info = system_info.get_cpu_info()
        memory_modules = system_info.get_memory_speed_and_manufacturer()
        storage_devices = system_info.get_storage_info()
        gpu_info = system_info.get_gpu_info()

        # デバッグ用
        logger.debug(f"OS Info: {os_info}")
        logger.debug(f"Motherboard Info: {motherboard_info}")
        logger.debug(f"CPU Info: {cpu_info}")
        logger.debug(f"Memory Modules: {memory_modules}")
        logger.debug(f"Storage Devices: {storage_devices}")
        logger.debug(f"GPU Info: {gpu_info}")

        system_info_container.controls.clear()
        sizes = get_responsive_sizes(page)

        # 各カードを作成
        os_card = create_os_card(os_info, sizes)
        system_info_container.controls.append(
            ft.ResponsiveRow([os_card], spacing=10))

        cpu_card = create_cpu_card(cpu_info, sizes)
        system_info_container.controls.append(
            ft.ResponsiveRow([cpu_card], spacing=10))

        memory_cards = create_memory_cards(memory_modules, sizes)
        system_info_container.controls.append(
            ft.ResponsiveRow(memory_cards, spacing=10))

        motherboard_card = create_motherboard_card(motherboard_info, sizes)
        system_info_container.controls.append(
            ft.ResponsiveRow([motherboard_card], spacing=10))

        gpu_cards = create_gpu_cards(gpu_info, sizes)
        system_info_container.controls.append(
            ft.ResponsiveRow(gpu_cards, spacing=10))

        storage_cards = create_storage_cards(storage_devices, sizes)
        system_info_container.controls.append(
            ft.ResponsiveRow(storage_cards, spacing=10))

        # ログファイルに保存
        file_name, file_path = save_system_info_log(
            os_info, cpu_info, memory_modules,
            motherboard_info, gpu_info, storage_devices
        )

        # 成功ダイアログ
        success_dialog = ft.AlertDialog(
            content=ft.Text(
                f"PC情報の取得が成功しました。'{file_name}' にログを保存しました。",
                size=12
            ),
            actions=[ft.TextButton(
                "OK",
                on_click=lambda e: (
                    setattr(success_dialog, 'open', False),
                    page.update()
                )
            )],
            on_dismiss=lambda e: (
                setattr(success_dialog, 'open', False),
                page.update()
            ),
        )
        page.overlay.append(success_dialog)
        success_dialog.open = True

    except Exception as e:
        logger.exception("PC情報の取得中にエラーが発生しました。")
        show_error_dialog(
            page,
            "エラー",
            "PC情報の取得中にエラーが発生しました。",
            str(e)
        )
    finally:
        hide_loading_dialog(page, loading_dialog)
