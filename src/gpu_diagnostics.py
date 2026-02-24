# gpu_diagnostics.py

import wmi
import pythoncom
import logging
from typing import List, Dict, Optional
from datetime import datetime
import os

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def get_gpu_device_status() -> List[Dict[str, str]]:
    """
    デバイスマネージャー経由でGPUのデバイスステータス、エラーコード、ドライババージョンを取得します。

    Returns:
        List[Dict[str, str]]: GPU診断情報のリスト。各要素は以下のキーを持つ辞書:
            - Name: デバイス名
            - Status: デバイスステータス (OK, Error, Degraded, Unknown)
            - ErrorCode: エラーコード (0 = 正常)
            - ErrorDescription: エラーの説明
            - DriverVersion: ドライババージョン
            - DriverDate: ドライバの日付
    """
    try:
        pythoncom.CoInitialize()
        c = wmi.WMI()

        # Win32_VideoControllerクラスからGPU情報を取得
        video_controllers = c.Win32_VideoController()

        gpu_status_list = []

        for gpu in video_controllers:
            try:
                name = gpu.Name or "Unknown GPU"

                # Microsoft Basic Display Adapter などの仮想/基本ディスプレイアダプタを除外
                if "Microsoft Basic Display" in name or "Remote Desktop" in name or "Virtual" in name:
                    logger.debug(f"仮想/基本ディスプレイアダプタをスキップ: {name}")
                    continue

                status = gpu.Status or "Unknown"
                config_error = gpu.ConfigManagerErrorCode or 0
                driver_version = gpu.DriverVersion or "Unknown"
                driver_date = gpu.DriverDate or "Unknown"

                # エラーコードの説明を取得
                error_description = get_error_description(config_error)

                # ドライバ日付のフォーマット変換 (WMI形式からreadable形式へ)
                if driver_date != "Unknown" and len(driver_date) >= 8:
                    try:
                        # WMI形式: YYYYMMDDhhmmss.mmmmmm+zzz
                        driver_date = f"{driver_date[0:4]}/{driver_date[4:6]}/{driver_date[6:8]}"
                    except Exception as e:
                        logger.warning(f"ドライバ日付の変換に失敗しました: {e}")

                gpu_info = {
                    "Name": name,
                    "Status": status,
                    "ErrorCode": str(config_error),
                    "ErrorDescription": error_description,
                    "DriverVersion": driver_version,
                    "DriverDate": driver_date
                }

                gpu_status_list.append(gpu_info)
                logger.debug(f"GPU診断情報取得: {gpu_info}")

            except Exception as e:
                logger.exception(f"GPUデバイス情報の取得中にエラーが発生しました: {e}")
                continue

        return gpu_status_list

    except Exception as e:
        logger.exception(f"GPU診断情報の取得中に重大なエラーが発生しました: {e}")
        return []
    finally:
        pythoncom.CoUninitialize()


def get_error_description(error_code: int) -> str:
    """
    ConfigManagerErrorCodeからエラーの説明を返します。

    Args:
        error_code: エラーコード

    Returns:
        str: エラーの説明
    """
    error_descriptions = {
        0: "正常に動作しています",
        1: "デバイスが正しく構成されていません",
        2: "Windows はこのデバイスのドライバーを読み込めません",
        3: "ドライバーが破損しているか、システムのメモリやリソースが不足している可能性があります",
        4: "デバイスが正しく機能していません",
        5: "デバイスのドライバーにリソース構成情報を伝える必要があります",
        6: "このデバイスと他のデバイスが競合しています",
        7: "このデバイスの構成情報が不完全です",
        8: "デバイスドライバーが見つかりません",
        9: "ファームウェアが必要なリソースを正しく報告していません",
        10: "デバイスを開始できません",
        11: "デバイスに障害が発生しました",
        12: "このデバイスが使用できる空きリソースが不足しています",
        13: "Windows はこのデバイスのリソースを確認できません",
        14: "コンピューターを再起動するまで、このデバイスは正常に動作しません",
        15: "リソースの競合により、デバイスが正常に動作していない可能性があります",
        16: "Windows はこのデバイスを完全に識別できません",
        17: "デバイスがリソースの種類を要求しています",
        18: "このデバイスのドライバーを再インストールしてください",
        19: "VxD ローダーでエラーが発生しました",
        20: "レジストリが破損している可能性があります",
        21: "システムエラー: このデバイスのドライバーを変更してみてください",
        22: "デバイスは無効になっています",
        23: "システムエラー: このデバイスのドライバーを変更してみてください",
        24: "デバイスが存在しないか、正しく機能していないか、すべてのドライバーがインストールされていません",
        25: "Windows はこのデバイス用のドライバーをインストール中です",
        26: "Windows はこのデバイス用のドライバーをインストール中です",
        27: "デバイスのログ構成が指定されていません",
        28: "デバイスのドライバーがインストールされていません",
        29: "ファームウェアが必要なリソースを提供しなかったため、デバイスは無効になっています",
        30: "このデバイスが別のデバイスが使用している IRQ リソースを使用しています",
        31: "Windows がこのデバイスに必要なドライバーを読み込めなかったため、デバイスが正常に機能していません"
    }

    return error_descriptions.get(error_code, f"不明なエラーコード: {error_code}")


def save_gpu_diagnostics_log(gpu_status_list: List[Dict[str, str]], log_dir: str = "log") -> Optional[str]:
    """
    GPU診断結果をログファイルに保存します。

    Args:
        gpu_status_list: GPU診断情報のリスト
        log_dir: ログファイルを保存するディレクトリ

    Returns:
        Optional[str]: 保存されたログファイルのパス。保存に失敗した場合はNone。
    """
    try:
        # ログディレクトリの作成
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, log_dir)
        os.makedirs(log_path, exist_ok=True)

        # ログファイル名の生成 (統一形式: gpu_info_log_YYYYMMDD_HHMM.txt)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M")
        log_filename = f"gpu_info_log_{timestamp}.txt"
        log_filepath = os.path.join(log_path, log_filename)

        # ログファイルに書き込み
        with open(log_filepath, 'w', encoding='utf-8') as f:
            f.write("=" * 80 + "\n")
            f.write(
                f"GPU Information Log - {datetime.now().strftime('%Y/%m/%d %H:%M')}\n")
            f.write("=" * 80 + "\n\n")

            if not gpu_status_list:
                f.write("GPU情報の取得に失敗しました。\n")
            else:
                for idx, gpu in enumerate(gpu_status_list, 1):
                    f.write(f"[GPU {idx}]\n")
                    f.write(
                        f"  Name             : {gpu.get('Name', 'Unknown')}\n")
                    f.write(
                        f"  Status           : {gpu.get('Status', 'Unknown')}\n")
                    f.write(
                        f"  Error Code       : {gpu.get('ErrorCode', 'Unknown')}\n")
                    f.write(
                        f"  Error Description: {gpu.get('ErrorDescription', 'Unknown')}\n")
                    f.write(
                        f"  Driver Version   : {gpu.get('DriverVersion', 'Unknown')}\n")
                    f.write(
                        f"  Driver Date      : {gpu.get('DriverDate', 'Unknown')}\n")
                    f.write("\n")

            f.write("=" * 80 + "\n")

        logger.info(f"GPU診断ログを保存しました: {log_filepath}")
        return log_filepath

    except Exception as e:
        logger.exception(f"GPU診断ログの保存中にエラーが発生しました: {e}")
        return None


def get_gpu_diagnostic_logs(log_dir: str = "log") -> List[str]:
    """
    GPU診断ログファイルの一覧を取得します。

    Args:
        log_dir: ログファイルが保存されているディレクトリ

    Returns:
        List[str]: ログファイル名のリスト（新しい順）
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, log_dir)

        if not os.path.exists(log_path):
            logger.warning(f"ログディレクトリが存在しません: {log_path}")
            return []

        # GPU診断ログファイルのみを抽出
        log_files = [
            f for f in os.listdir(log_path)
            if f.startswith("gpu_info_log_") and f.endswith(".txt")
        ]

        # 更新日時の新しい順にソート
        log_files.sort(
            key=lambda x: os.path.getmtime(os.path.join(log_path, x)),
            reverse=True
        )

        logger.debug(f"GPU診断ログファイル一覧: {log_files}")
        return log_files

    except Exception as e:
        logger.exception(f"GPU診断ログファイル一覧の取得中にエラーが発生しました: {e}")
        return []


def read_gpu_diagnostic_log(filename: str, log_dir: str = "log") -> str:
    """
    GPU診断ログファイルの内容を読み込みます。

    Args:
        filename: ログファイル名
        log_dir: ログファイルが保存されているディレクトリ

    Returns:
        str: ログファイルの内容。読み込みに失敗した場合はエラーメッセージ。
    """
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        log_path = os.path.join(script_dir, log_dir, filename)

        if not os.path.exists(log_path):
            error_msg = f"ログファイルが見つかりません: {filename}"
            logger.warning(error_msg)
            return error_msg

        with open(log_path, 'r', encoding='utf-8') as f:
            content = f.read()

        logger.debug(f"GPU診断ログを読み込みました: {filename}")
        return content

    except Exception as e:
        error_msg = f"ログファイルの読み込み中にエラーが発生しました: {e}"
        logger.exception(error_msg)
        return error_msg


def parse_gpu_log(filename: str, log_dir: str = "log") -> List[Dict[str, str]]:
    """
    GPU診断ログファイルを解析してGPU情報のリストを返します。

    Args:
        filename: ログファイル名
        log_dir: ログファイルが保存されているディレクトリ

    Returns:
        List[Dict[str, str]]: GPU情報のリスト
    """
    try:
        content = read_gpu_diagnostic_log(filename, log_dir)
        if not content or "ログファイル" in content:
            return []

        gpu_list = []
        current_gpu = {}
        in_section = False

        for line in content.split('\n'):
            line = line.strip()

            # セクションの開始を検出
            if line.startswith('[GPU ') and line.endswith(']'):
                if current_gpu:
                    gpu_list.append(current_gpu)
                current_gpu = {}
                in_section = True
            # セクションの終了（区切り線または終了マーカー）を検出
            elif line.startswith('-' * 10) or line.startswith('=' * 10):
                if current_gpu:
                    gpu_list.append(current_gpu)
                    current_gpu = {}
                in_section = False
            # キー:値のペアを解析（セクション内のみ）
            elif in_section and ':' in line:
                parts = line.split(':', 1)
                if len(parts) == 2:
                    key = parts[0].strip()
                    value = parts[1].strip()
                    current_gpu[key] = value

        # 最後のGPU情報を保存（区切り線がない場合に備えて）
        if current_gpu:
            gpu_list.append(current_gpu)

        logger.debug(f"GPU診断ログを解析しました: {gpu_list}")
        return gpu_list

    except Exception as e:
        logger.exception(f"GPU診断ログの解析中にエラーが発生しました: {e}")
        return []
