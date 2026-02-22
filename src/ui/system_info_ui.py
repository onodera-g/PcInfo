"""
システム情報表示UIモジュール
"""

import flet as ft
import logging
from datetime import datetime
from typing import List, Dict

import system_info
from constants import (
    CARD_WIDTH,
    ICON_COMPUTER,
    ICON_CHIP,
    ICON_MEMORY,
    ICON_DEVICE_HUB,
    ICON_VIDEO_LIBRARY,
    ICON_DISK
)
from ui.components import create_label_value_row, create_card
from ui.dialogs import show_loading_dialog, hide_loading_dialog, show_success_dialog, show_error_dialog

logger = logging.getLogger(__name__)


def display_system_info(page: ft.Page, system_info_container: ft.Column) -> None:
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

        # デバッグ用ログ
        logger.debug(f"OS Info: {os_info}")
        logger.debug(f"Motherboard Info: {motherboard_info}")
        logger.debug(f"CPU Info: {cpu_info}")
        logger.debug(f"Memory Modules: {memory_modules}")
        logger.debug(f"Storage Devices: {storage_devices}")
        logger.debug(f"GPU Info: {gpu_info}")

        # システム情報コンテナをクリア
        system_info_container.controls.clear()

        # OS情報カードの作成
        _create_os_card(system_info_container, os_info)

        # CPU情報カードの作成
        _create_cpu_card(system_info_container, cpu_info)

        # メモリ情報カードの作成
        _create_memory_cards(system_info_container, memory_modules)

        # マザーボード情報カードの作成
        _create_motherboard_card(system_info_container, motherboard_info)

        # GPU情報カードの作成
        _create_gpu_cards(system_info_container, gpu_info)

        # ストレージ情報カードの作成
        _create_storage_cards(system_info_container, storage_devices)

        # テキストファイルに保存
        file_name = _save_system_info_to_file(
            os_info, cpu_info, memory_modules, motherboard_info, gpu_info, storage_devices
        )

        show_success_dialog(page, f"PC情報の取得が成功しました。'{file_name}' にログを保存しました。")

    except Exception as e:
        logger.exception("PC情報の取得中にエラーが発生しました。")
        show_error_dialog(page, "エラー", "PC情報の取得中にエラーが発生しました。", str(e))
    finally:
        hide_loading_dialog(page, loading_dialog)


def _create_os_card(container: ft.Column, os_info: tuple) -> None:
    """OS情報カードを作成"""
    os_name, os_version = os_info
    os_card = create_card(
        title="OS",
        content_controls=[
            create_label_value_row("名称:", os_name),
            create_label_value_row("バージョン:", os_version),
        ],
        icon_filename=ICON_COMPUTER,
        width=CARD_WIDTH,
        layout="single_column"
    )
    container.controls.append(os_card)


def _create_cpu_card(container: ft.Column, cpu_info: dict) -> None:
    """CPU情報カードを作成"""
    if isinstance(cpu_info, dict):
        cpu_name = str(cpu_info.get('Name', 'Unknown')).strip()
        cpu_card = create_card(
            title="CPU",
            content_controls=[
                create_label_value_row("名称:", cpu_name),
                create_label_value_row(
                    "コア数:", f"{cpu_info.get('NumberOfCores', 'Unknown')}", label_width=120
                ),
                create_label_value_row(
                    "スレッド数:", f"{cpu_info.get('NumberOfLogicalProcessors', 'Unknown')}", label_width=120
                ),
                create_label_value_row(
                    "最大クロック速度:", f"{cpu_info.get('MaxClockSpeed', 'Unknown')} MHz", label_width=120
                ),
            ],
            icon_filename=ICON_CHIP,
            width=CARD_WIDTH,
            layout="single_column"
        )
        container.controls.append(cpu_card)
    else:
        cpu_card = create_card(
            title="CPU",
            content_controls=[
                ft.Text("CPU情報の形式が不正です。", size=12, color=ft.Colors.RED)],
            icon_filename=ICON_CHIP,
            width=CARD_WIDTH,
            layout="single_column"
        )
        container.controls.append(cpu_card)


def _create_memory_cards(container: ft.Column, memory_modules: List[Dict]) -> None:
    """メモリ情報カードを作成"""
    if isinstance(memory_modules, list) and all(isinstance(module, dict) for module in memory_modules):
        memory_pairs = [memory_modules[i:i + 2]
                        for i in range(0, len(memory_modules), 2)]
        for pair_idx, pair in enumerate(memory_pairs, start=1):
            modules_info = []
            for module_idx, module in enumerate(pair, start=1):
                module_title = f"モジュール{((pair_idx - 1) * 2) + module_idx}"
                module_items = [
                    ft.Text(module_title, size=12, weight=ft.FontWeight.BOLD),
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
                icon_filename=ICON_MEMORY,
                width=CARD_WIDTH,
                layout="numbered"
            )
            container.controls.append(memory_card)
    else:
        memory_card = create_card(
            title="メモリ",
            content_controls=[
                ft.Text("メモリ情報の形式が不正です。", size=12, color=ft.Colors.RED)],
            icon_filename=ICON_MEMORY,
            width=CARD_WIDTH,
            layout="single_column"
        )
        container.controls.append(memory_card)


def _create_motherboard_card(container: ft.Column, motherboard_info: str) -> None:
    """マザーボード情報カードを作成"""
    motherboard_card = create_card(
        title="マザーボード",
        content_controls=[
            create_label_value_row(
                "モデル番号:", motherboard_info if motherboard_info else 'Unknown')
        ],
        icon_filename=ICON_DEVICE_HUB,
        width=CARD_WIDTH,
        layout="single_column"
    )
    container.controls.append(motherboard_card)


def _create_gpu_cards(container: ft.Column, gpu_info: List[Dict]) -> None:
    """GPU情報カードを作成"""
    if isinstance(gpu_info, list) and all(isinstance(gpu, dict) for gpu in gpu_info):
        gpu_pairs = [gpu_info[i:i + 2] for i in range(0, len(gpu_info), 2)]
        for pair_idx, pair in enumerate(gpu_pairs, start=1):
            modules_info = []
            for gpu_idx, gpu in enumerate(pair, start=1):
                gpu_title = f"GPU{((pair_idx - 1) * 2) + gpu_idx}"
                module_items = [
                    ft.Text(gpu_title, size=12, weight=ft.FontWeight.BOLD),
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
                icon_filename=ICON_VIDEO_LIBRARY,
                width=CARD_WIDTH,
                layout="numbered"
            )
            container.controls.append(gpu_card)
    else:
        gpu_card = create_card(
            title="GPU",
            content_controls=[
                ft.Text("GPU情報の形式が不正です。", size=12, color=ft.Colors.RED)],
            icon_filename=ICON_VIDEO_LIBRARY,
            width=CARD_WIDTH,
            layout="single_column"
        )
        container.controls.append(gpu_card)


def _create_storage_cards(container: ft.Column, storage_devices: List[Dict]) -> None:
    """ストレージ情報カードを作成"""
    if isinstance(storage_devices, list) and all(isinstance(storage, dict) for storage in storage_devices):
        storage_pairs = [storage_devices[i:i + 2]
                         for i in range(0, len(storage_devices), 2)]
        for pair_idx, pair in enumerate(storage_pairs, start=1):
            modules_info = []
            for storage_idx, storage in enumerate(pair, start=1):
                storage_title = f"ディスク{((pair_idx - 1) * 2) + storage_idx}"
                module_items = [
                    ft.Text(storage_title, size=12, weight=ft.FontWeight.BOLD),
                    create_label_value_row(
                        "モデル番号:", storage.get('ModelNumber', 'Unknown')),
                    create_label_value_row(
                        "サイズ:", storage.get('SizeGB', 'Unknown')),
                ]
                modules_info.append(module_items)
            storage_card = create_card(
                title="ストレージ",
                content_controls=modules_info,
                icon_filename=ICON_DISK,
                width=CARD_WIDTH,
                layout="numbered"
            )
            container.controls.append(storage_card)
    else:
        storage_card = create_card(
            title="ストレージ",
            content_controls=[
                ft.Text("ストレージ情報の形式が不正です。", size=12, color=ft.Colors.RED)],
            icon_filename=ICON_DISK,
            width=CARD_WIDTH,
            layout="single_column"
        )
        container.controls.append(storage_card)


def _save_system_info_to_file(
    os_info: tuple,
    cpu_info: dict,
    memory_modules: List[Dict],
    motherboard_info: str,
    gpu_info: List[Dict],
    storage_devices: List[Dict]
) -> str:
    """システム情報をテキストファイルに保存"""
    info_text = f"--- PC情報詳細 ---\n\n"

    # OS情報
    os_name, os_version = os_info
    info_text += f"OS:\n  名称: {os_name}\n  バージョン: {os_version}\n\n"

    # CPU情報
    if isinstance(cpu_info, dict):
        cpu_name = str(cpu_info.get('Name', 'Unknown')).strip()
        info_text += f"CPU:\n"
        info_text += f"  名称: {cpu_name}\n"
        info_text += f"  コア数: {cpu_info.get('NumberOfCores', 'Unknown')}\n"
        info_text += f"  スレッド数: {cpu_info.get('NumberOfLogicalProcessors', 'Unknown')}\n"
        info_text += f"  最大クロック速度: {cpu_info.get('MaxClockSpeed', 'Unknown')} MHz\n\n"
    else:
        info_text += "CPU情報の形式が不正です。\n\n"

    # メモリ情報
    if isinstance(memory_modules, list) and all(isinstance(module, dict) for module in memory_modules):
        for idx, module in enumerate(memory_modules, start=1):
            info_text += f"メモリ モジュール{idx}:\n"
            info_text += f"  モデル番号: {module.get('ManufacturerAndModel', 'Unknown')}\n"
            info_text += f"  クロック速度: {module.get('Speed', 'Unknown')} \n"
            info_text += f"  容量: {module.get('Capacity', 'Unknown')} \n\n"
    else:
        info_text += "メモリ情報の形式が不正です。\n\n"

    # マザーボード情報
    info_text += f"マザーボード:\n  モデル番号: {motherboard_info if motherboard_info else 'Unknown'}\n\n"

    # GPU情報
    if isinstance(gpu_info, list) and all(isinstance(gpu, dict) for gpu in gpu_info):
        for idx, gpu in enumerate(gpu_info, start=1):
            info_text += f"GPU{idx}:\n"
            info_text += f"  モデル番号: {gpu.get('ModelNumber', 'Unknown')}\n"
            info_text += f"  メモリ容量: {gpu.get('AdapterRAMGB', 'Unknown')} \n"
            info_text += f"  ドライバーバージョン: {gpu.get('DriverVersion', 'Unknown')}\n\n"
    else:
        info_text += "GPU情報の形式が不正です。\n\n"

    # ストレージ情報
    if isinstance(storage_devices, list) and all(isinstance(storage, dict) for storage in storage_devices):
        for idx, storage in enumerate(storage_devices, start=1):
            info_text += f"ストレージ ディスク{idx}:\n"
            info_text += f"  モデル番号: {storage.get('ModelNumber', 'Unknown')}\n"
            info_text += f"  サイズ: {storage.get('SizeGB', 'Unknown')} \n\n"
    else:
        info_text += "ストレージ情報の形式が不正です。\n\n"

    # ファイルに保存
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_name = f"PC_info_{timestamp}.txt"
    with open(file_name, "w", encoding="utf-8") as f:
        f.write(info_text)
    logger.info(f"PC情報を '{file_name}' に保存しました。")

    return file_name
