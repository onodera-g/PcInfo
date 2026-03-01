"""
定数定義モジュール
"""

# ウィンドウサイズ（デフォルト値）
WINDOW_WIDTH_DEFAULT = 800
WINDOW_HEIGHT_DEFAULT = 1100
WINDOW_MIN_WIDTH = 600
WINDOW_MIN_HEIGHT = 700

# UI要素のサイズ
LIST_VIEW_HEIGHT = 150
LABEL_WIDTH = 120
ICON_SIZE = 24
PROGRESS_BAR_WIDTH = 200

# レスポンシブデザインのスケール制限
SCALE_RATIO_MIN = 0.8
SCALE_RATIO_MAX = 1.5

# レスポンシブグリッド設定（最大4枚横並び）
# Fletのcol引数用の型定義に合わせる


def get_responsive_col_config():
    """レスポンシブグリッド設定を返す"""
    return {
        "xs": 12,   # 極小画面: 1列
        "sm": 12,   # 小画面: 1列
        "md": 6,    # 中画面: 2列
        "lg": 4,    # 大画面: 3列
        "xl": 3,    # 特大画面: 4列
        "xxl": 3    # 超特大画面: 4列
    }


# フォントサイズ倍率
FONT_SIZE_SMALL_BASE = 10
FONT_SIZE_NORMAL_BASE = 12
FONT_SIZE_LARGE_BASE = 14

# ダイアログのデフォルトフォントサイズ（固定）
DIALOG_FONT_SIZE = 12
BUTTON_FONT_SIZE = 12

# アニメーション
ANIMATION_DURATION = 500

# 区切り線の長さ
DIVIDER_LENGTH = 80

# アイコンファイル名
ICON_CIRCULAR_PROGRESS = "circular_progress.png"
ICON_DISK = "disk.png"
ICON_MEMORY = "memory.png"
ICON_COMPUTER = "computer.png"
ICON_CHIP = "chip.png"
ICON_DEVICE_HUB = "device_hub.png"
ICON_VIDEO_LIBRARY = "video_library.png"
ICON_APP = "app_icon.ico"

# ログファイル関連
LOG_FOLDER_NAME = "log"
PC_INFO_LOG_PREFIX = "PC_info_log_"
GPU_INFO_LOG_PREFIX = "gpu_info_log_"
STORAGE_INFO_LOG_PREFIX = "storage_info_log_"
TIMESTAMP_FORMAT = "%Y%m%d_%H%M"
LOG_TIMESTAMP_FORMAT = "%Y/%m/%d %H:%M"
