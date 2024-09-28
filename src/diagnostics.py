# diagnostics.py
import wmi
import pythoncom  # 追加
from datetime import datetime, timedelta
import subprocess
import os
import glob


def get_memory_event_log(start_time, end_time, event_id_filter=None):
    """
    WMIを使用してSystemログから指定された期間のイベントID 1101, 1102, 1201, 1202 のログを取得します。
    :start_time: 取得開始日時（datetimeオブジェクト）
    :end_time: 取得終了日時（datetimeオブジェクト）
    :event_id_filter: 取得したいイベントIDのリスト
    :return: イベントログのリスト
    """
    try:
        pythoncom.CoInitialize()  # COMの初期化

        # WMIオブジェクトの作成
        c = wmi.WMI()

        # WMIクエリを作成
        query = f"SELECT * FROM Win32_NTLogEvent WHERE Logfile = 'System'"
        if event_id_filter:
            event_ids = " OR ".join(
                [f"EventCode = '{event_id}'" for event_id in event_id_filter])
            query += f" AND ({event_ids})"

        # クエリを実行
        logs = c.query(query)

        # 時間範囲でフィルタリング
        filtered_logs = []
        for log in logs:
            event_time = convert_time(log.TimeGenerated)
            if event_time and start_time <= event_time <= end_time:
                filtered_logs.append(log)

        return filtered_logs

    except Exception as e:
        print(f"イベントログの取得中にエラーが発生しました: {e}")
        return []
    finally:
        pythoncom.CoUninitialize()  # COMの解放


def convert_time(wmi_time):
    """
    WMIのTimeGenerated（UTC形式）をPythonのdatetimeに変換する
    """
    try:
        # WMIのTimeGeneratedは "YYYYMMDDHHMMSS.000000+000" 形式
        return datetime.strptime(wmi_time.split('.')[0], '%Y%m%d%H%M%S')
    except ValueError:
        return None


def search_memory_log():
    """
    過去7日間のメモリ診断ログ（イベントID 1101, 1102, 1201, 1202）を取得して返します。
    """
    event_ids = [1101, 1102, 1201, 1202]
    start_time = datetime.now() - timedelta(days=7)
    end_time = datetime.now()

    # イベントログを取得
    logs = get_memory_event_log(start_time, end_time, event_ids)
    return logs


def run_memory_diagnostics():
    """
    Windowsのメモリ診断ツールを実行する。再起動を要求されるため、ユーザー確認が必要。
    """
    try:
        # メモリ診断を管理者権限で実行する
        result = subprocess.run(["mdsched.exe"], check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"メモリ診断の実行に失敗しました: {e}")
        return False


def search_memory_diagnostic_logs():
    """
    メモリ診断ログフォルダ内の、過去7日間のイベントID 1101, 1102のログファイルを検索し、
    ログファイル名のリストを返します。
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    log_folder = os.path.join(current_dir, "memory_logs")  # メモリ診断ログフォルダ
    pattern = os.path.join(log_folder, "memory_diagnostic_log_*.txt")
    log_files = glob.glob(pattern)

    if not log_files:
        return []

    # 過去7日間のログファイルのみをフィルタ
    seven_days_ago = datetime.now() - timedelta(days=7)
    recent_logs = [
        log_file for log_file in log_files
        if os.path.getmtime(log_file) >= seven_days_ago.timestamp()
    ]

    # イベントID 1101, 1102のファイル名をフィルタ
    filtered_logs = [
        log_file for log_file in recent_logs
        if "1101" in log_file or "1102" in log_file
    ]

    # ログファイルを最新順にソート
    log_files_sorted = sorted(
        filtered_logs, key=os.path.getmtime, reverse=True)
    log_filenames = [os.path.basename(log_file)
                     for log_file in log_files_sorted]

    return log_filenames
