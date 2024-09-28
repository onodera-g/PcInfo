# storage_diagnostics.py

import sys
import subprocess
import os
import time
import ctypes
import psutil
from datetime import datetime
import glob
import re
import logging
from typing import List, Dict, Optional

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 必要に応じてレベルを調整

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)

# 正規表現パターンのコンパイル
DISK_LIST_PATTERN = re.compile(
    r"-- Disk List ---------------------------------------------------------------\n(.*?)\n----------------------------------------------------------------------------",
    re.DOTALL
)
DISK_ENTRY_PATTERN = re.compile(r"\((\d+)\)\s+(.+)")
DISK_SECTION_PATTERN = re.compile(
    r"----------------------------------------------------------------------------\n\s*\(\d+\)\s+.+?\n----------------------------------------------------------------------------\n(.*?)\n-- S\.M\.A\.R\.T\.",
    re.DOTALL
)
DISK_INFO_PATTERN = re.compile(
    r"ディスク\s+\d+:\n(?:  .+\n)+", re.MULTILINE
)


def get_base_path() -> str:
    """
    実行ファイルのディレクトリを取得します。
    PyInstallerやflet packでコンパイルされた場合でも対応します。

    Returns:
        str: 実行ファイルのディレクトリパス。
    """
    if getattr(sys, 'frozen', False):
        # PyInstallerやflet packでコンパイルされた場合
        return os.path.dirname(sys.executable)
    else:
        # 開発環境の場合
        return os.path.dirname(os.path.abspath(__file__))


def run_CrystalDiskInfo(executable_path: str, parameters: str) -> bool:
    """
    CrystalDiskInfoを管理者として実行しログを取得します。

    Parameters:
        executable_path (str): CrystalDiskInfoの実行ファイルパス。
        parameters (str): 実行時のパラメータ。

    Returns:
        bool: 実行が成功した場合はTrue、失敗した場合はFalse。
    """
    try:
        # ShellExecuteW を使用して管理者として実行
        result = ctypes.windll.shell32.ShellExecuteW(
            None,                # hwnd
            "runas",             # Operation
            executable_path,     # File
            parameters,          # Parameters
            os.path.dirname(executable_path),  # Directory
            0                    # nShowCmd (0: 非表示)
        )
        if result <= 32:
            # エラーが発生した場合
            logger.error(f"管理者としての実行に失敗しました。エラーコード: {result}")
            return False
        logger.info(f"DiskInfo32.exe を管理者として実行しました。パラメータ: {parameters}")
        return True
    except Exception as e:
        logger.exception(f"管理者として実行中にエラーが発生しました: {e}")
        return False


def get_storage_log(log_text: str) -> List[Dict[str, str]]:
    """
    CrystalDiskInfoのログから必要な情報を抽出します。

    Parameters:
        log_text (str): CrystalDiskInfoからのログテキスト。

    Returns:
        List[Dict[str, str]]: 抽出されたディスク情報のリスト。
    """
    disks = []

    # ディスクリストセクションの抽出
    disk_list_match = DISK_LIST_PATTERN.search(log_text)

    if not disk_list_match:
        logger.warning("ディスクリストのセクションが見つかりませんでした。")
        return disks

    disk_list_text = disk_list_match.group(1)
    logger.debug("ディスクリスト:\n%s", disk_list_text)
    logger.debug("-----")

    # ディスクエントリの取得
    disk_entries = DISK_ENTRY_PATTERN.findall(disk_list_text)

    if not disk_entries:
        logger.warning("ディスクエントリが見つかりませんでした。")
        return disks

    for disk_number, disk_model in disk_entries:
        logger.debug(f"解析対象ディスク {disk_number}: {disk_model}")

    # 各ディスクの詳細セクションの抽出
    disk_sections = DISK_SECTION_PATTERN.findall(log_text)

    if not disk_sections:
        logger.warning("各ディスクの詳細セクションが見つかりませんでした。")
        return disks

    for idx, section in enumerate(disk_sections, start=1):
        section = section.strip()
        if not section:
            continue

        logger.debug(f"解析中のディスクセクション {idx}:\n{section}")
        logger.debug("-----")

        # フィールドを抽出（大文字小文字無視）
        disk_info = {
            "Model": extract_field(section, r"Model\s*:\s*(.+)"),
            "Disk Size": extract_field(section, r"Disk Size\s*:\s*(.+)"),
            "Interface": extract_field(section, r"Interface\s*:\s*(.+)"),
            "Power On Hours": extract_field(section, r"Power On Hours\s*:\s*(\d+)\s*時間"),
            "Power On Count": extract_field(section, r"Power On Count\s*:\s*(\d+)\s*回"),
            "Host Writes": extract_field(section, r"Host Writes\s*:\s*([\d,\.]+)\s*GB").replace(',', '') if extract_field(section, r"Host Writes\s*:\s*([\d,\.]+)\s*GB") else "N/A",
            "Health Status": extract_field(section, r"Health Status\s*:\s*(.+)")
        }

        logger.debug(f"抽出結果: {disk_info}")

        # 欠けているフィールドがあれば警告
        missing_fields = [key for key,
                          value in disk_info.items() if value == "N/A"]
        if missing_fields:
            logger.warning(f"以下のフィールドが見つかりませんでした: {', '.join(missing_fields)}")

        disks.append(disk_info)

    return disks


def extract_field(text: str, pattern: str) -> str:
    """
    指定されたパターンでテキストからフィールドを抽出します。

    Parameters:
        text (str): 対象のテキスト。
        pattern (str): 抽出するための正規表現パターン。

    Returns:
        str: 抽出されたフィールド値。見つからない場合は "N/A"。
    """
    match = re.search(pattern, text, re.IGNORECASE)
    return match.group(1).strip() if match else "N/A"


def save_storage_info(disks: List[Dict[str, str]], parsed_log_file_path: str) -> None:
    """
    抽出したディスク情報をテキストファイルとして保存します。

    Parameters:
        disks (List[Dict[str, str]]): 抽出されたディスク情報のリスト。
        parsed_log_file_path (str): 解析済みログファイルの保存パス。
    """
    try:
        with open(parsed_log_file_path, 'w', encoding='utf-8') as f:
            for idx, disk in enumerate(disks, start=1):
                f.write(f"ディスク {idx}:\n")
                f.write(f"  Model: {disk['Model']}\n")
                f.write(f"  Disk Size: {disk['Disk Size']}\n")
                f.write(f"  Interface: {disk['Interface']}\n")
                f.write(f"  Power On Hours: {disk['Power On Hours']}\n")
                f.write(f"  Power On Count: {disk['Power On Count']}\n")
                f.write(f"  Host Writes: {disk['Host Writes']}\n")
                f.write(f"  Health Status: {disk['Health Status']}\n\n")
        logger.info(f"解析済みのディスク情報が保存されました: {parsed_log_file_path}")
    except Exception as e:
        logger.exception(f"解析済み情報の保存中にエラーが発生しました: {e}")


def get_CrystalDiskInfo_log() -> bool:
    """
    DiskInfo32.exe を管理者として実行し、/CopyExit オプションでログを保存して終了します。
    タイムスタンプ付きのログファイルとして保存し、解析結果を新たなテキストファイルに保存します。

    Returns:
        bool: 処理が成功した場合はTrue、失敗した場合はFalse。
    """
    base_path = get_base_path()

    # DiskInfo32.exe のパスを取得
    executable_path = os.path.join(
        base_path, "CrystalDiskInfo", "DiskInfo32.exe")

    if not os.path.exists(executable_path):
        logger.error(f"DiskInfo32.exe が見つかりません: {executable_path}")
        return False

    # デフォルトのログファイルパス
    log_file_default = os.path.join(
        base_path, "CrystalDiskInfo", "DiskInfo.txt")

    # タイムスタンプの生成
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # log フォルダのパスを設定
    log_folder = os.path.join(base_path, "log")
    os.makedirs(log_folder, exist_ok=True)  # log フォルダが存在しない場合は作成

    # log フォルダ内のログファイルパスに変更
    path_CrystalDiskInfo_log = os.path.join(
        log_folder, f"storage_health_log_{timestamp}.txt"
    )
    path_storage_info_log = os.path.join(
        log_folder, f"storage_info_log_{timestamp}.txt"
    )

    logger.info(f"ログファイルのデフォルトパス: {log_file_default}")
    logger.info(f"ログファイルのターゲットパス: {path_CrystalDiskInfo_log}")
    logger.info(f"解析済みログファイルのパス: {path_storage_info_log}")

    # DiskInfo32.exe を管理者として /CopyExit オプションで実行
    if not run_CrystalDiskInfo(executable_path, "/CopyExit"):
        logger.error("DiskInfo32.exe の実行に失敗しました。")
        return False

    # DiskInfo32.exe が終了するまで待機（最大10秒）
    timeout = 10
    start_time = time.time()
    while True:
        if not any(proc.info['name'].lower() == 'diskinfo32.exe' for proc in psutil.process_iter(['name'])):
            logger.info("DiskInfo32.exe のプロセスが終了しました。")
            break
        if time.time() - start_time > timeout:
            logger.error("DiskInfo32.exe の終了を待機中にタイムアウトしました。")
            return False
        time.sleep(0.5)

    # DiskInfo.txt が存在するか確認
    if not os.path.exists(log_file_default):
        logger.error(f"ログファイルが見つかりません: {log_file_default}")
        return False
    else:
        logger.info(f"ログファイルが見つかりました: {log_file_default}")

    # DiskInfo.txt が空でないか確認
    if os.path.getsize(log_file_default) == 0:
        logger.error(f"ログファイルが空です: {log_file_default}")
        return False
    else:
        logger.info(f"ログファイルにデータが含まれています: {log_file_default}")

    # ログファイルを log フォルダ内にコピー
    try:
        with open(log_file_default, 'r', encoding='utf-8') as src, open(path_CrystalDiskInfo_log, 'w', encoding='utf-8') as dst:
            content = src.read()
            dst.write(content)
        logger.info(f"ログファイルが保存されました: {path_CrystalDiskInfo_log}")
    except Exception as e:
        logger.exception(f"ログファイルのコピー中にエラーが発生しました: {e}")
        return False

    # 解析済み情報を抽出
    disks = get_storage_log(content)

    if not disks:
        logger.warning("ディスク情報が見つかりませんでした。")
        # 解析後でもログファイルは削除
    else:
        # 解析結果を log フォルダ内の新たなテキストファイルに保存
        save_storage_info(disks, path_storage_info_log)

    # ログファイルを削除（読み取り後）
    try:
        os.remove(log_file_default)
        logger.info(f"元のログファイルが削除されました: {log_file_default}")
    except Exception as e:
        logger.exception(f"元のログファイルの削除中にエラーが発生しました: {e}")
        # 削除に失敗しても処理を続行

    return True


def search_storage_log() -> List[str]:
    """
    log フォルダ内の storage_info_log_*.txt ファイルを検索し、ログファイル名のリストを返します。

    Returns:
        List[str]: ログファイル名のリスト。ファイルが存在しない場合は空リスト。
    """
    base_path = get_base_path()
    log_folder = os.path.join(base_path, "log")
    pattern = os.path.join(log_folder, "storage_info_log_*.txt")
    log_files = glob.glob(pattern)

    if not log_files:
        logger.info("ログファイルが見つかりませんでした。")
        return []

    # ログファイルを最新順にソート
    log_files_sorted = sorted(log_files, key=os.path.getmtime, reverse=True)
    log_filenames = [os.path.basename(log_file)
                     for log_file in log_files_sorted]
    logger.debug(f"見つかったログファイル: {log_filenames}")
    return log_filenames


def get_storage_info(log_filename: str) -> Optional[List[Dict[str, str]]]:
    """
    指定されたストレージ診断ログファイルの内容を辞書形式で返します。

    Parameters:
        log_filename (str): 解析対象のログファイル名。

    Returns:
        Optional[List[Dict[str, str]]]: パースされたディスク情報のリスト。エラー時はNone。
    """
    base_path = get_base_path()
    log_folder = os.path.join(base_path, "log")
    log_file_path = os.path.join(log_folder, log_filename)

    if not os.path.exists(log_file_path):
        logger.error(f"ログファイルが見つかりません: {log_file_path}")
        return None

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # ログ内容をパースして辞書に変換
        disks = DISK_INFO_PATTERN.findall(content)

        parsed_disks = []
        for disk in disks:
            disk_dict = {}
            lines = disk.strip().split('\n')
            for line in lines:
                if ':' in line:
                    key, value = line.strip().split(':', 1)
                    # 'ディスク 1' や 'ディスク 2' のキーを除外
                    if key.strip().startswith("ディスク"):
                        continue
                    disk_dict[key.strip()] = value.strip()
            parsed_disks.append(disk_dict)

        logger.debug(f"パースされたディスク情報: {parsed_disks}")
        return parsed_disks
    except Exception as e:
        logger.exception(f"ログファイルの読み込み中にエラーが発生しました: {e}")
        return None


if __name__ == "__main__":
    # テスト用の実行ブロック（必要に応じて削除またはコメントアウト）
    success = get_CrystalDiskInfo_log()
    if success:
        logger.info("ストレージ診断が正常に完了しました。")
    else:
        logger.error("ストレージ診断中にエラーが発生しました。")
