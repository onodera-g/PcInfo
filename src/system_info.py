# system_info.py

import subprocess
import json
from powershell_utils import run_powershell_command
import wmi
import pythoncom  # COM初期化のために追加
import logging
from typing import Tuple, Dict, List, Optional, Union
import os
import sys

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 必要に応じてレベルを調整

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_os_info() -> Tuple[str, str]:
    """
    PowerShellを使用してOS名とバージョンを取得します。

    Returns:
        Tuple[str, str]: OS名とバージョン。取得に失敗した場合は ("Unknown", "Unknown")。
    """
    command = "Get-CimInstance Win32_OperatingSystem | Select-Object Caption, Version | ConvertTo-Json -Compress"
    os_data = run_powershell_command(command)
    if not os_data:
        logger.error("OS情報の取得に失敗しました。")
        return "Unknown", "Unknown"

    os_name = os_data.get("Caption", "Unknown")
    os_version = os_data.get("Version", "Unknown")
    logger.debug(f"取得したOS情報 - 名称: {os_name}, バージョン: {os_version}")
    return os_name, os_version


def get_cpu_info() -> Dict[str, Union[str, int]]:
    """
    PowerShellを使用してCPU情報を取得します。

    Returns:
        Dict[str, Union[str, int]]: CPU情報。取得に失敗した場合は空辞書。
    """
    command = "Get-CimInstance Win32_Processor | Select-Object Name, NumberOfCores, NumberOfLogicalProcessors, MaxClockSpeed, Stepping, Revision | ConvertTo-Json -Compress"
    cpu_data = run_powershell_command(command)
    if not cpu_data:
        logger.error("CPU情報の取得に失敗しました。")
        return {}

    if isinstance(cpu_data, list):
        cpu_data = cpu_data[0]  # 複数CPUがある場合は最初のものを使用

    cpu_info = {
        "Name": cpu_data.get("Name", "Unknown"),
        "NumberOfCores": cpu_data.get("NumberOfCores", "Unknown"),
        "NumberOfLogicalProcessors": cpu_data.get("NumberOfLogicalProcessors", "Unknown"),
        "MaxClockSpeed": cpu_data.get("MaxClockSpeed", "Unknown"),
        "Stepping": cpu_data.get("Stepping", "Unknown"),
        "Revision": cpu_data.get("Revision", "Unknown")
    }
    logger.debug(f"取得したCPU情報: {cpu_info}")
    return cpu_info


def get_total_memory() -> str:
    """
    総メモリ容量を取得します。

    Returns:
        str: 総メモリ容量（GB）。取得に失敗した場合は "Unknown"。
    """
    command = "Get-CimInstance Win32_ComputerSystem | Select-Object TotalPhysicalMemory | ConvertTo-Json -Compress"
    cs_data = run_powershell_command(command)
    if not cs_data:
        logger.error("総メモリ容量の取得に失敗しました。")
        return "Unknown"

    total_memory_bytes = cs_data.get("TotalPhysicalMemory", 0)
    try:
        total_memory_gb = int(total_memory_bytes) / (1024 ** 3)
        total_memory = f"{total_memory_gb:.2f} GB"
        logger.debug(f"取得した総メモリ容量: {total_memory}")
        return total_memory
    except (ValueError, TypeError) as e:
        logger.exception(f"総メモリ容量の計算中にエラーが発生しました: {e}")
        return "Unknown"


def get_memory_speed_and_manufacturer() -> List[Dict[str, str]]:
    """
    メモリモジュールのメーカーとモデル番号、速度、容量を取得します。
    WMIを使用してメーカー情報を正しく取得します。

    Returns:
        List[Dict[str, str]]: メモリ情報のリスト。
    """
    with COMInitializer():
        c = wmi.WMI()
        memory_info = []

        # MemoryType のマッピング（全ての可能な値を含む）
        MEMORY_TYPE_MAPPING = {
            0: "DDR4",
            1: "Other",
            2: "DRAM",
            3: "Synchronous DRAM",
            4: "Cache DRAM",
            5: "EDO",
            6: "EDRAM",
            7: "VRAM",
            8: "SRAM",
            9: "RAM",
            10: "ROM",
            11: "FLASH",
            12: "EEPROM",
            13: "FEPROM",
            14: "EPROM",
            15: "CDRAM",
            16: "3DRAM",
            17: "SDRAM",
            18: "SGRAM",
            19: "RDRAM",
            20: "DDR",
            21: "DDR2",
            22: "DDR2 FB-DIMM",
            24: "DDR3",
            25: "LPDDR3",
            26: "DDR4",
            27: "LPDDR4",
            28: "DDR5",
            29: "LPDDR5",
            # 必要に応じて追加
        }

        for mem in c.Win32_PhysicalMemory():
            # メーカー名の取得
            manufacturer = mem.Manufacturer.strip() if mem.Manufacturer else "Unknown"
            # モデル番号の取得
            part_number = mem.PartNumber.strip() if mem.PartNumber else "Unknown"
            # MemoryType の取得とマッピング
            memory_type_code = mem.MemoryType
            memory_type = MEMORY_TYPE_MAPPING.get(memory_type_code, "Unknown")
            # 速度の取得
            speed = f"{mem.Speed} MHz" if mem.Speed else "Unknown"
            # 容量の取得（GB単位）
            try:
                capacity_gb = int(mem.Capacity) / (1024 ** 3)
                capacity = f"{capacity_gb:.2f} GB"
            except (ValueError, TypeError) as e:
                logger.exception(f"メモリ容量の計算中にエラーが発生しました: {e}")
                capacity = "Unknown"

            # メーカー名が取得できている場合はメーカー名とモデル番号を結合
            if manufacturer.lower() not in ["unknown", "(標準ディスク ドライブ)"]:
                manufacturer_and_model = f"{manufacturer} {part_number}"
            else:
                manufacturer_and_model = part_number  # メーカー名が不明または不要な場合はモデル番号のみ

            mem_info = {
                'ManufacturerAndModel': manufacturer_and_model,
                'Speed': f"{memory_type} @ {speed}",
                'Capacity': capacity
            }

            logger.debug(f"取得したメモリ情報: {mem_info}")

            memory_info.append(mem_info)

        return memory_info


def get_storage_info() -> List[Dict[str, str]]:
    """
    ストレージ情報を取得します。物理ディスクドライブのモデル番号とサイズを表示します。
    メーカー名は取得しません。

    Returns:
        List[Dict[str, str]]: ストレージ情報のリスト。
    """
    with COMInitializer():
        c = wmi.WMI()
        storage_info = []
        for disk in c.Win32_DiskDrive():
            model = disk.Model.strip() if disk.Model else "Unknown"
            try:
                size_gb = int(disk.Size) / \
                    (1024 ** 3) if disk.Size else "Unknown"
                formatted_size = f"{
                    size_gb:.2f} GB" if size_gb != "Unknown" else "Unknown"
            except (ValueError, TypeError) as e:
                logger.exception(f"ディスクサイズの計算中にエラーが発生しました: {e}")
                formatted_size = "Unknown"

            storage_info.append({
                "ModelNumber": model,
                "SizeGB": formatted_size
            })
            logger.debug(f"取得したストレージ情報: ModelNumber={
                         model}, SizeGB={formatted_size}")

        return storage_info


def get_gpu_info() -> List[Dict[str, str]]:
    """
    NVIDIA製GPUの場合、nvidia-smiを使用して正確なメモリ情報を取得します。
    それ以外の場合は従来のPowerShellコマンドを使用します。

    Returns:
        List[Dict[str, str]]: GPU情報のリスト。
    """
    try:
        logger.debug("nvidia-smiコマンドを実行します。")
        result = subprocess.run(
            ["nvidia-smi", "--query-gpu=name,memory.total,driver_version",
             "--format=csv,noheader"],
            capture_output=True, text=True, check=True
        )
        if result.returncode == 0 and result.stdout.strip():
            gpus = []
            for line in result.stdout.splitlines():
                parts = line.split(',')
                if len(parts) != 3:
                    logger.warning(f"nvidia-smiの出力形式が不正です: {line}")
                    continue
                name, memory, driver_version = parts
                try:
                    # nvidia-smiはMiB単位で出力するため、1024で割ってGiBに変換
                    memory_mib = float(memory.strip().split()[0])
                    memory_gib = memory_mib / 1024
                    gpus.append({
                        "ModelNumber": name.strip(),
                        "AdapterRAMGB": f"{memory_gib:.2f} GB",
                        "DriverVersion": driver_version.strip()
                    })
                except (ValueError, IndexError) as e:
                    logger.exception(f"nvidia-smiの出力解析中にエラーが発生しました: {e}")
                    continue
            logger.debug(f"取得したNVIDIA GPU情報: {gpus}")
            return gpus
        else:
            logger.warning("nvidia-smiコマンドの出力が不正です。PowerShellコマンドを試します。")
            return get_gpu_info_via_powershell()
    except FileNotFoundError:
        logger.warning("nvidia-smiが見つかりません。PowerShellコマンドを試します。")
        return get_gpu_info_via_powershell()
    except subprocess.CalledProcessError as e:
        logger.error("nvidia-smiコマンドの実行に失敗しました。PowerShellコマンドを試します。")
        logger.error(e)
        return get_gpu_info_via_powershell()


def get_gpu_info_via_powershell() -> List[Dict[str, str]]:
    """
    PowerShellコマンドでGPU情報を取得します (NVIDIA以外の場合など)。

    Returns:
        List[Dict[str, str]]: GPU情報のリスト。取得に失敗した場合は空リスト。
    """
    command = "Get-CimInstance Win32_VideoController | Select-Object Name, AdapterRAM, DriverVersion | ConvertTo-Json -Compress"
    gpus = run_powershell_command(command)
    if not gpus:
        logger.error("PowerShellでのGPU情報の取得に失敗しました。")
        return []

    if isinstance(gpus, dict):
        gpus = [gpus]  # 単一GPUの場合もリストに変換

    formatted_gpus = []
    for gpu in gpus:
        try:
            name = gpu.get("Name", "Unknown")
            adapter_ram = gpu.get("AdapterRAM", 0)
            if adapter_ram and int(adapter_ram) > 0:
                adapter_ram_gb = int(adapter_ram) / (1024 ** 3)  # バイトをギガバイトに変換
                adapter_ram_formatted = f"{adapter_ram_gb:.2f} GB"
            else:
                adapter_ram_formatted = "Unknown"
            driver_version = gpu.get("DriverVersion", "Unknown")
            formatted_gpus.append({
                "ModelNumber": name,
                "AdapterRAMGB": adapter_ram_formatted,
                "DriverVersion": driver_version
            })
            logger.debug(f"取得したGPU情報 (PowerShell経由): {formatted_gpus[-1]}")
        except (ValueError, TypeError) as e:
            logger.exception(f"GPU情報の解析中にエラーが発生しました: {e}")
            continue
    return formatted_gpus


def get_motherboard_info() -> Dict[str, str]:
    """
    PowerShellのGet-CimInstanceコマンドレットを使用してマザーボード情報とBIOS情報を取得します。

    Returns:
        Dict[str, str]: マザーボード情報とBIOSバージョン。取得に失敗した場合はデフォルト値。
    """
    # マザーボード情報の取得
    mb_command = "Get-CimInstance Win32_BaseBoard | Select-Object Manufacturer, Product, Version | ConvertTo-Json -Compress"
    motherboard_data = run_powershell_command(mb_command)

    motherboard_model = "Unknown"
    if motherboard_data:
        if isinstance(motherboard_data, list):
            motherboard = motherboard_data[0]
        elif isinstance(motherboard_data, dict):
            motherboard = motherboard_data
        else:
            motherboard = {}

        manufacturer = motherboard.get("Manufacturer", "Unknown")
        product = motherboard.get("Product", "Unknown")
        version = motherboard.get("Version", "Unknown")
        motherboard_model = f"{manufacturer} {product} {version}".strip()
        logger.debug(f"取得したマザーボード情報: {motherboard_model}")
    else:
        logger.error("マザーボード情報の取得に失敗しました。")

    # BIOS情報の取得
    bios_command = "Get-CimInstance Win32_BIOS | Select-Object SMBIOSBIOSVersion | ConvertTo-Json -Compress"
    bios_data = run_powershell_command(bios_command)

    bios_version = "Unknown"
    if bios_data:
        if isinstance(bios_data, list):
            bios = bios_data[0]
        elif isinstance(bios_data, dict):
            bios = bios_data
        else:
            bios = {}

        bios_version = bios.get("SMBIOSBIOSVersion", "Unknown")
        logger.debug(f"取得したBIOSバージョン: {bios_version}")
    else:
        logger.error("BIOS情報の取得に失敗しました。")

    return {
        "Model": motherboard_model if motherboard_model else "Unknown",
        "BIOSVersion": bios_version
    }


class COMInitializer:
    """
    COMの初期化と解放をコンテキストマネージャーで管理するクラス。
    """

    def __enter__(self):
        pythoncom.CoInitialize()
        logger.debug("COMを初期化しました。")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        pythoncom.CoUninitialize()
        logger.debug("COMを解放しました。")


def get_pc_info_logs(log_dir: str = "log") -> List[str]:
    """
    PC情報ログファイルの一覧を取得します。

    Args:
        log_dir: ログファイルが保存されているディレクトリ

    Returns:
        List[str]: ログファイル名のリスト（新しい順）
    """
    try:
        if getattr(sys, 'frozen', False):
            # PyInstallerでコンパイルされた場合
            script_dir = os.path.dirname(sys.executable)
        else:
            # 開発環境の場合
            script_dir = os.path.dirname(os.path.abspath(__file__))

        log_path = os.path.join(script_dir, log_dir)

        if not os.path.exists(log_path):
            logger.warning(f"ログディレクトリが存在しません: {log_path}")
            return []

        # PC情報ログファイルのみを抽出
        log_files = [
            f for f in os.listdir(log_path)
            if f.startswith("PC_info_log_") and f.endswith(".txt")
        ]

        # 更新日時の新しい順にソート
        log_files.sort(
            key=lambda x: os.path.getmtime(os.path.join(log_path, x)),
            reverse=True
        )

        logger.debug(f"PC情報ログファイル一覧: {log_files}")
        return log_files

    except Exception as e:
        logger.exception(f"PC情報ログファイル一覧の取得中にエラーが発生しました: {e}")
        return []


def read_pc_info_log(filename: str, log_dir: str = "log") -> str:
    """
    PC情報ログファイルの内容を読み込みます。

    Args:
        filename: ログファイル名
        log_dir: ログファイルが保存されているディレクトリ

    Returns:
        str: ログファイルの内容。読み込みに失敗した場合はエラーメッセージ。
    """
    try:
        if getattr(sys, 'frozen', False):
            script_dir = os.path.dirname(sys.executable)
        else:
            script_dir = os.path.dirname(os.path.abspath(__file__))

        log_path = os.path.join(script_dir, log_dir, filename)

        if not os.path.exists(log_path):
            error_msg = f"ログファイルが見つかりません: {filename}"
            logger.warning(error_msg)
            return error_msg

        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.debug(f"PC情報ログを読み込みました: {filename}")
        return content

    except Exception as e:
        error_msg = f"ログファイルの読み込み中にエラーが発生しました: {e}"
        logger.exception(error_msg)
        return error_msg


def parse_pc_info_log(filename: str, log_dir: str = "log") -> Dict[str, any]:
    """
    PC情報ログファイルを解析して構造化データを返します。

    Args:
        filename: ログファイル名
        log_dir: ログファイルが保存されているディレクトリ

    Returns:
        Dict[str, any]: 解析されたPC情報
    """
    try:
        content = read_pc_info_log(filename, log_dir)
        if not content or "ログファイル" in content:
            return {}

        parsed_data = {
            'OS': {},
            'CPU': {},
            'Memory': [],
            'Motherboard': {},
            'GPU': [],
            'Storage': []
        }

        current_section = None
        current_item = {}

        for line in content.split('\n'):
            line = line.strip()

            # セクションの開始を検出
            if line.startswith('[') and line.endswith(']'):
                # 前のアイテムを保存
                if current_section and current_item:
                    if current_section in ['Memory', 'GPU', 'Storage']:
                        parsed_data[current_section].append(current_item)
                    else:
                        parsed_data[current_section] = current_item

                # 新しいセクション
                section_name = line[1:-1].strip()
                if 'メモリ' in section_name:
                    current_section = 'Memory'
                elif section_name == 'GPU' or section_name.startswith('GPU'):
                    current_section = 'GPU'
                elif 'ストレージ' in section_name:
                    current_section = 'Storage'
                elif section_name == 'OS':
                    current_section = 'OS'
                elif section_name == 'CPU':
                    current_section = 'CPU'
                elif 'マザーボード' in section_name:
                    current_section = 'Motherboard'
                else:
                    current_section = None

                current_item = {}

            # キー:値のペアを解析
            elif ':' in line and not line.startswith('=') and not line.startswith('-'):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    current_item[key] = value

        # 最後のアイテムを保存
        if current_section and current_item:
            if current_section in ['Memory', 'GPU', 'Storage']:
                parsed_data[current_section].append(current_item)
            else:
                parsed_data[current_section] = current_item

        logger.debug(f"PC情報ログを解析しました: {parsed_data}")
        return parsed_data

    except Exception as e:
        logger.exception(f"PC情報ログの解析中にエラーが発生しました: {e}")
        return {}


if __name__ == "__main__":
    # テスト用の実行ブロック（必要に応じて削除またはコメントアウト）
    os_name, os_version = get_os_info()
    cpu_info = get_cpu_info()
    total_memory = get_total_memory()
    memory_info = get_memory_speed_and_manufacturer()
    storage_info = get_storage_info()
    gpu_info = get_gpu_info()
    motherboard_info = get_motherboard_info()

    logger.info(f"OS: {os_name}, バージョン: {os_version}")
    logger.info(f"CPU情報: {cpu_info}")
    logger.info(f"総メモリ: {total_memory}")
    logger.info(f"メモリ情報: {memory_info}")
    logger.info(f"ストレージ情報: {storage_info}")
    logger.info(f"GPU情報: {gpu_info}")
    logger.info(f"マザーボード情報: {motherboard_info}")
