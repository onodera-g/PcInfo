# tabs/system_info_tab.py

import flet as ft
import os
import logging
from datetime import datetime
from typing import Optional
import system_info
from config import DIALOG_FONT_SIZE
from utils import get_executable_dir, get_ui_sizes
from ui_components import create_card, create_label_value_row
from dialogs import show_loading_dialog, hide_loading_dialog, close_dialog

logger = logging.getLogger(__name__)


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
        font_size, icon_size, label_width, padding, spacing, col_config = get_ui_sizes(
            page)

        # OS情報カードの作成
        os_name, os_version = os_info
        os_card = create_card(
            title="OS",
            content_controls=[
                create_label_value_row("名称:", os_name, label_width, font_size),
                create_label_value_row(
                    "バージョン:", os_version, label_width, font_size),
            ],
            icon_filename="computer.png",
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
                create_label_value_row(
                    "名称:", cpu_name, label_width=label_width, font_size=font_size),
                create_label_value_row(
                    "コア数:", f"{cpu_info.get('NumberOfCores', 'Unknown')}", label_width=label_width, font_size=font_size),
                create_label_value_row(
                    "スレッド数:", f"{cpu_info.get('NumberOfLogicalProcessors', 'Unknown')}", label_width=label_width, font_size=font_size),
                create_label_value_row(
                    "最大クロック速度:", f"{cpu_info.get('MaxClockSpeed', 'Unknown')} MHz", label_width=label_width, font_size=font_size),
                create_label_value_row(
                    "リビジョン:", f"{revision}", label_width=label_width, font_size=font_size),
                create_label_value_row(
                    "ステッピング:", f"{stepping}", label_width=label_width, font_size=font_size),
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
                    create_label_value_row("クロック速度:", module.get(
                        'Speed', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row("容量:", module.get(
                        'Capacity', 'Unknown'), label_width=label_width, font_size=font_size),
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
                    ft.Text("メモリ情報の形式が不正です。", size=font_size, color=ft.Colors.RED)],
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
                    create_label_value_row("モデル番号:", motherboard_info.get(
                        'Model', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row("BIOSバージョン:", motherboard_info.get(
                        'BIOSVersion', 'Unknown'), label_width=label_width, font_size=font_size)
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
                    ft.Text(gpu_title, size=font_size,
                            weight=ft.FontWeight.BOLD),
                    create_label_value_row("モデル番号:", gpu.get(
                        'ModelNumber', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row("メモリ容量:", gpu.get(
                        'AdapterRAMGB', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row("ドライバーバージョン:", gpu.get(
                        'DriverVersion', 'Unknown'), label_width=label_width, font_size=font_size),
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
                    ft.Text("GPU情報の形式が不正です。", size=font_size, color=ft.Colors.RED)],
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
                    create_label_value_row("モデル番号:", storage.get(
                        'ModelNumber', 'Unknown'), label_width=label_width, font_size=font_size),
                    create_label_value_row("サイズ:", storage.get(
                        'SizeGB', 'Unknown'), label_width=label_width, font_size=font_size),
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
                    ft.Text("ストレージ情報の形式が不正です。", size=font_size, color=ft.Colors.RED)],
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
                title=ft.Text("エラー", size=DIALOG_FONT_SIZE),
                content=ft.Column([
                    ft.Text("PC情報のテキストファイルへの保存中にエラーが発生しました。",
                            size=DIALOG_FONT_SIZE),
                    ft.Text(str(file_error), color=ft.Colors.RED,
                            size=DIALOG_FONT_SIZE),
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
                f"PC情報の取得が成功しました。'{file_name}' にログを保存しました。", size=DIALOG_FONT_SIZE),
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
            title=ft.Text("エラー", size=DIALOG_FONT_SIZE),
            content=ft.Column([
                ft.Text("PC情報の取得中にエラーが発生しました。", size=DIALOG_FONT_SIZE),
                ft.Text(str(e), color=ft.Colors.RED, size=DIALOG_FONT_SIZE),
            ]),
            actions=[ft.TextButton(
                "OK", on_click=lambda e: close_dialog(error_dialog, page))],
            on_dismiss=lambda e: close_dialog(error_dialog, page),
        )
        page.overlay.append(error_dialog)
        error_dialog.open = True
    finally:
        hide_loading_dialog(page, loading_dialog)
