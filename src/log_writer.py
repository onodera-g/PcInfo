"""
ログファイル出力関連の処理モジュール
"""
import os
import logging
from datetime import datetime
from typing import List, Dict, Any, Tuple, Union
from constants import (
    LOG_FOLDER_NAME,
    PC_INFO_LOG_PREFIX,
    TIMESTAMP_FORMAT,
    LOG_TIMESTAMP_FORMAT,
    DIVIDER_LENGTH
)
from ui_helpers import get_executable_dir

logger = logging.getLogger(__name__)


def create_log_folder() -> str:
    """
    ログフォルダを作成し、パスを返します。

    Returns:
        str: ログフォルダのパス
    """
    log_folder = os.path.join(get_executable_dir(), LOG_FOLDER_NAME)
    os.makedirs(log_folder, exist_ok=True)
    return log_folder


def generate_log_filename(prefix: str) -> Tuple[str, str]:
    """
    タイムスタンプ付きのログファイル名を生成します。

    Parameters:
        prefix (str): ログファイル名のプレフィックス

    Returns:
        Tuple[str, str]: (ファイル名, フルパス)
    """
    timestamp = datetime.now().strftime(TIMESTAMP_FORMAT)
    filename = f"{prefix}{timestamp}.txt"
    log_folder = create_log_folder()
    filepath = os.path.join(log_folder, filename)
    return filename, filepath


def create_divider(char: str = "=") -> str:
    """区切り線を作成"""
    return char * DIVIDER_LENGTH + "\n"


def format_log_header() -> str:
    """ログファイルのヘッダーを作成"""
    header = create_divider()
    header += f"PC Information Log - {datetime.now().strftime(LOG_TIMESTAMP_FORMAT)}\n"
    header += create_divider()
    header += "\n"
    return header


def format_section(title: str, items: List[Tuple[str, str]]) -> str:
    """
    セクション形式でログを整形します。

    Parameters:
        title (str): セクションタイトル
        items (List[Tuple[str, str]]): (ラベル, 値)のタプルのリスト

    Returns:
        str: 整形されたセクション文字列
    """
    section = f"[{title}]\n"
    for label, value in items:
        section += f"  {label:<18}: {value}\n"
    section += create_divider("-")
    section += "\n"
    return section


def save_system_info_log(
    os_info: Tuple[str, str],
    cpu_info: Union[Dict[str, Any], str],
    memory_modules: List[Dict[str, str]],
    motherboard_info: Union[Dict[str, str], str],
    gpu_info: List[Dict[str, str]],
    storage_devices: List[Dict[str, str]]
) -> Tuple[str, str]:
    """
    システム情報をログファイルに保存します。

    Parameters:
        os_info: OS情報のタプル
        cpu_info: CPU情報の辞書
        memory_modules: メモリモジュール情報のリスト
        motherboard_info: マザーボード情報
        gpu_info: GPU情報のリスト
        storage_devices: ストレージデバイス情報のリスト

    Returns:
        Tuple[str, str]: (ファイル名, フルパス)

    Raises:
        Exception: ログファイルの保存に失敗した場合
    """
    info_text = format_log_header()

    # OS情報
    os_name, os_version = os_info
    info_text += format_section("OS", [
        ("名称", os_name),
        ("バージョン", os_version)
    ])

    # CPU情報
    if isinstance(cpu_info, dict):
        cpu_name = str(cpu_info.get('Name', 'Unknown')).strip()
        stepping = cpu_info.get('Stepping', 'Unknown')
        revision = cpu_info.get('Revision', 'Unknown')
        info_text += format_section("CPU", [
            ("名称", cpu_name),
            ("コア数", str(cpu_info.get('NumberOfCores', 'Unknown'))),
            ("スレッド数", str(cpu_info.get('NumberOfLogicalProcessors', 'Unknown'))),
            ("最大クロック速度", f"{cpu_info.get('MaxClockSpeed', 'Unknown')} MHz"),
            ("リビジョン", str(revision)),
            ("ステッピング", str(stepping))
        ])
    else:
        info_text += "[CPU]\n  取得に失敗しました\n"
        info_text += create_divider("-") + "\n"

    # メモリ情報
    if isinstance(memory_modules, list) and all(isinstance(m, dict) for m in memory_modules):
        for idx, module in enumerate(memory_modules, start=1):
            info_text += format_section(f"メモリ モジュール{idx}", [
                ("モデル番号", module.get('ManufacturerAndModel', 'Unknown')),
                ("クロック速度", module.get('Speed', 'Unknown')),
                ("容量", module.get('Capacity', 'Unknown'))
            ])
    else:
        info_text += "[メモリ]\n  取得に失敗しました\n"
        info_text += create_divider("-") + "\n"

    # マザーボード情報
    if isinstance(motherboard_info, dict):
        info_text += format_section("マザーボード", [
            ("モデル番号", motherboard_info.get('Model', 'Unknown')),
            ("BIOSバージョン", motherboard_info.get('BIOSVersion', 'Unknown'))
        ])
    else:
        info_text += format_section("マザーボード", [
            ("モデル番号", motherboard_info if motherboard_info else 'Unknown')
        ])

    # GPU情報
    if isinstance(gpu_info, list) and all(isinstance(g, dict) for g in gpu_info):
        for idx, gpu in enumerate(gpu_info, start=1):
            info_text += format_section(f"GPU{idx}", [
                ("モデル番号", gpu.get('ModelNumber', 'Unknown')),
                ("メモリ容量", gpu.get('AdapterRAMGB', 'Unknown')),
                ("ドライバーバージョン", gpu.get('DriverVersion', 'Unknown'))
            ])
    else:
        info_text += "[GPU]\n  取得に失敗しました\n"
        info_text += create_divider("-") + "\n"

    # ストレージ情報
    if isinstance(storage_devices, list) and all(isinstance(s, dict) for s in storage_devices):
        for idx, storage in enumerate(storage_devices, start=1):
            info_text += format_section(f"ストレージ ディスク{idx}", [
                ("モデル番号", storage.get('ModelNumber', 'Unknown')),
                ("サイズ", storage.get('SizeGB', 'Unknown'))
            ])
    else:
        info_text += "[ストレージ]\n  取得に失敗しました\n"
        info_text += create_divider("-") + "\n"

    # フッター
    info_text += create_divider()

    # ファイルに保存
    filename, filepath = generate_log_filename(PC_INFO_LOG_PREFIX)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(info_text)

    logger.info(f"PC情報を '{filepath}' に保存しました。")
    return filename, filepath
