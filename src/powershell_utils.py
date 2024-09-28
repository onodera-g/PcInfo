# powershell_utils.py

import subprocess
import json
import logging
from typing import Optional, Union, Dict, List

# ロガーの設定
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # 必要に応じてレベルを調整

handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)


def run_powershell_command(command: str, timeout: int = 60) -> Optional[Union[Dict, List]]:
    """
    PowerShellコマンドを実行し、結果をJSONとして返します。

    Parameters:
        command (str): 実行するPowerShellコマンド。
        timeout (int): コマンドのタイムアウト時間（秒）。

    Returns:
        dict or list or None: コマンドの出力をJSONとしてパースした結果。
                              エラーが発生した場合はNoneを返す。
    """
    try:
        logger.debug(f"Executing PowerShell command: {command}")
        completed_process = subprocess.run(
            ["powershell", "-Command", command],
            capture_output=True,
            text=True,
            timeout=timeout
        )
        logger.debug(f"PowerShell command return code: {
                     completed_process.returncode}")

        if completed_process.returncode != 0:
            logger.error("PowerShellコマンド実行エラー:")
            logger.error(completed_process.stderr.strip())
            return None

        try:
            result = json.loads(completed_process.stdout)
            logger.debug("JSON parsed successfully.")
            return result
        except json.JSONDecodeError as e:
            logger.error(f"JSONのデコード中にエラーが発生しました: {e}")
            logger.error(f"出力内容: {completed_process.stdout.strip()}")
            return None

    except subprocess.TimeoutExpired:
        logger.error("PowerShellコマンドがタイムアウトしました。")
        return None
    except Exception as e:
        logger.exception(f"PowerShellコマンド実行中に予期しないエラーが発生しました: {e}")
        return None
