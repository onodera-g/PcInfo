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

from utils import get_base_path, get_executable_dir

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


def run_CrystalDiskInfo(executable_path: str, parameters: str) -> bool:
    """
    CrystalDiskInfoを管理者として実行しログを取得します。

    Parameters:
        executable_path (str): CrystalDiskInfoの実行ファイルパス。
        parameters (str): 実行時のパラメータ。

    Returns:
        bool: 実行が成功した場合はTrue、失敗した場合はFalse。
    """
    # 管理者権限チェック
    is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0
    if is_admin:
        logger.info("CrystalDiskInfo実行前: アプリケーションは管理者権限で実行されています。")
    else:
        logger.warning("CrystalDiskInfo実行前: アプリケーションは管理者権限で実行されていません。")

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
            # ヘッダーを追加
            f.write("=" * 80 + "\n")
            f.write(
                f"Storage Information Log - {datetime.now().strftime('%Y/%m/%d %H:%M')}\n")
            f.write("=" * 80 + "\n\n")

            for idx, disk in enumerate(disks, start=1):
                f.write(f"[ディスク {idx}]\n")
                f.write(f"  Model            : {disk['Model']}\n")
                f.write(f"  Disk Size        : {disk['Disk Size']}\n")
                f.write(f"  Interface        : {disk['Interface']}\n")
                f.write(f"  Power On Hours   : {disk['Power On Hours']}\n")
                f.write(f"  Power On Count   : {disk['Power On Count']}\n")
                f.write(f"  Host Writes      : {disk['Host Writes']}\n")
                f.write(f"  Health Status    : {disk['Health Status']}\n")
                f.write("-" * 80 + "\n\n")

            # フッターを追加
            f.write("=" * 80 + "\n")

        logger.info(f"解析済みのディスク情報が保存されました: {parsed_log_file_path}")
    except Exception as e:
        logger.exception(f"解析済み情報の保存中にエラーが発生しました: {e}")


def get_CrystalDiskInfo_log() -> tuple[bool, Optional[str]]:
    """
    DiskInfo32.exe を管理者として実行し、/CopyExit オプションでログを保存して終了します。
    タイムスタンプ付きのログファイルとして保存し、解析結果を新たなテキストファイルに保存します。

    Returns:
        tuple[bool, Optional[str]]: (成功/失敗, エラーメッセージ)
    """
    exe_dir = get_executable_dir()

    # CrystalDiskInfoフォルダの存在確認
    crystal_disk_info_dir = os.path.join(exe_dir, "CrystalDiskInfo")
    if not os.path.exists(crystal_disk_info_dir):
        error_msg = "CrystalDiskInfoが見つかりません。\nPcinfo.exeと同じディレクトリにCrystalDiskInfoのポータブル版のフォルダを配置してください。\n詳細はREADMEをご確認ください。"
        logger.error(error_msg)
        return False, error_msg

    # DiskInfo32.exe のパスを取得 (実行ファイルと同じディレクトリ)
    executable_path = os.path.join(crystal_disk_info_dir, "DiskInfo32.exe")

    if not os.path.exists(executable_path):
        error_msg = "CrystalDiskInfoが見つかりません。\nPcinfo.exeと同じディレクトリにCrystalDiskInfoのポータブル版のフォルダを配置してください。\n詳細はREADMEをご確認ください。"
        logger.error(error_msg)
        return False, error_msg

    # デフォルトのログファイルパス
    log_file_default = os.path.join(
        exe_dir, "CrystalDiskInfo", "DiskInfo.txt")

    # タイムスタンプの生成（統一形式: YYYYMMDD_HHMM）
    timestamp = datetime.now().strftime("%Y%m%d_%H%M")

    # log フォルダのパスを設定 (実行ファイルと同じディレクトリ)
    log_folder = os.path.join(exe_dir, "log")
    os.makedirs(log_folder, exist_ok=True)  # log フォルダが存在しない場合は作成

    # log フォルダ内のログファイルパスに変更（命名規則を統一）
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
        error_msg = "DiskInfo32.exeの実行に失敗しました。\n管理者権限が必要です。"
        logger.error(error_msg)
        return False, error_msg

    # DiskInfo32.exe が終了するまで待機（最大10秒）
    timeout = 10
    start_time = time.time()
    while True:
        if not any(proc.info['name'].lower() == 'diskinfo32.exe' for proc in psutil.process_iter(['name'])):
            logger.info("DiskInfo32.exe のプロセスが終了しました。")
            break
        if time.time() - start_time > timeout:
            error_msg = "DiskInfo32.exeの終了を待機中にタイムアウトしました。"
            logger.error(error_msg)
            return False, error_msg
        time.sleep(0.5)

    # DiskInfo.txt が存在するか確認
    if not os.path.exists(log_file_default):
        error_msg = f"ログファイルが生成されませんでした: {log_file_default}"
        logger.error(error_msg)
        return False, error_msg
    else:
        logger.info(f"ログファイルが見つかりました: {log_file_default}")

    # DiskInfo.txt が空でないか確認
    if os.path.getsize(log_file_default) == 0:
        error_msg = f"生成されたログファイルが空です: {log_file_default}"
        logger.error(error_msg)
        return False, error_msg
    else:
        logger.info(f"ログファイルにデータが含まれています: {log_file_default}")

    # ログファイルを log フォルダ内にコピー
    try:
        with open(log_file_default, 'r', encoding='utf-8') as src, open(path_CrystalDiskInfo_log, 'w', encoding='utf-8') as dst:
            content = src.read()
            dst.write(content)
        logger.info(f"ログファイルが保存されました: {path_CrystalDiskInfo_log}")
    except Exception as e:
        error_msg = f"ログファイルのコピー中にエラーが発生しました: {str(e)}"
        logger.exception(error_msg)
        return False, error_msg

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

    return True, None


def search_storage_log() -> List[str]:
    """
    log フォルダ内の storage_info_log_*.txt ファイルを検索し、ログファイル名のリストを返します。

    Returns:
        List[str]: ログファイル名のリスト。ファイルが存在しない場合は空リスト。
    """
    exe_dir = get_executable_dir()
    log_folder = os.path.join(exe_dir, "log")
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
    新しいログ形式（Storage Information Log形式）に対応。

    Parameters:
        log_filename (str): 解析対象のログファイル名。

    Returns:
        Optional[List[Dict[str, str]]]: パースされたディスク情報のリスト。エラー時はNone。
    """
    exe_dir = get_executable_dir()
    log_folder = os.path.join(exe_dir, "log")
    log_file_path = os.path.join(log_folder, log_filename)

    if not os.path.exists(log_file_path):
        logger.error(f"ログファイルが見つかりません: {log_file_path}")
        return None

    try:
        with open(log_file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 新しいログ形式をパース
        parsed_disks = []
        current_disk = {}
        in_section = False

        for line in content.split('\n'):
            line = line.strip()

            # セクションの開始を検出
            if line.startswith('[ディスク ') and line.endswith(']'):
                # 前のディスク情報を保存
                if current_disk:
                    parsed_disks.append(current_disk)
                current_disk = {}
                in_section = True
            # セクションの終了（区切り線）を検出
            elif line.startswith('-' * 10):
                if current_disk:
                    parsed_disks.append(current_disk)
                    current_disk = {}
                in_section = False
            # キー:値のペアを解析（セクション内のみ）
            elif in_section and ':' in line and not line.startswith('='):
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    current_disk[key] = value

        # 最後のディスク情報を保存（区切り線がない場合に備えて）
        if current_disk:
            parsed_disks.append(current_disk)

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
