# PcInfo

## 概要
Flet フレームワークを使用して作成された PC 診断ツールです。
ハードウェア構成の取得から各パーツの健康診断までをGUIで一括管理し、結果をテキストログとして出力します。

### 機能一覧

| 機能 | 内容 |
| :--- | :--- |
| **PC構成情報の取得** | OS、CPU、メモリ、ストレージ、GPU、マザーボード情報 |
| **メモリ診断** | Windowsメモリ診断の実行予約・過去ログの表示 |
| **ストレージ診断** | S.M.A.R.T.情報の取得（CrystalDiskInfo連携） |
| **GPU診断** | グラフィックカードの状態確認・ドライバ情報の取得 |
| **ログ保存** | PC構成・ストレージ・GPUの結果をテキスト形式（.txt）で自動保存 |

## システム要件

| 項目 | 要件 |
| :--- | :--- |
| **OS** | Windows 10 / 11 (64bit) |
| **権限** | **管理者権限**（ストレージS.M.A.R.T.情報取得に必要） |
| **外部依存** | [CrystalDiskInfo](https://crystalmark.info/ja/software/crystaldiskinfo/) 通常版 (ZIPファイル版) |

### CrystalDiskInfoの配置
ストレージ診断機能を使用するには、以下の構成でファイルを配置してください。

1. [CrystalDiskInfo公式サイト](https://crystalmark.info/ja/software/crystaldiskinfo/)から **通常版のZIPファイル版** をダウンロード。
2. 解凍したフォルダを「**CrystalDiskInfo**」という名前に変更。
3. `PcInfo.exe` と同じフォルダに配置。
```
├── PcInfo.exe                ← 本アプリケーション
│
└── CrystalDiskInfo/          ← このフォルダが必要
├── DiskInfo64.exe
├── DiskInfo32.exe
├── DiskInfoA64.exe
└── ...
```
**注意**: 必ず**通常版のZIPファイル版**を使用してください。インストーラー版では動作しません。

## 各タブの機能イメージ（旧版）

###  PC 情報
<div align="left">
  <img src="https://github.com/user-attachments/assets/2e38adf5-b01c-46af-a96f-c5b2ea5c3e4a" width="50%" alt="PcInfo スクリーンショット">
</div>

###  メモリ診断
<div align="left">
  <img src="https://github.com/user-attachments/assets/927687f4-de4a-4fb5-ba4d-f81292e9b2b2" width="50%" alt="メモリ診断">
</div>

###  ストレージ診断
<div align="left">
  <img src="https://github.com/user-attachments/assets/8015c5ee-9b56-4d24-bb82-7b5a2a65ada9" width="50%" alt=ストレージ診断">
</div>


###  GPU 診断
<div align="left">
  <img src="https://github.com/user-attachments/assets/236a3d82-41da-4502-985f-3458d2274950" width="50%" alt="GPU診断">
</div>

## ライセンス
このプロジェクトは MIT ライセンスの下で提供されています。詳細については LICENSE ファイルをご覧ください。
また、本ソフトウェアのS.M.A.R.T. の取得には、hiyohiyo氏が作成されたCrystalDiskInfoを使用しています。

## 画面とログ出力

4つのタブ、ボタンの順序、ログ一覧から詳細を見る操作を維持し、文字・余白・選択表示を調整しています。OSのライト／ダーク配色へ追従します。文字はウィンドウ幅に合わせて縮小せず、長い情報は折り返して表示します。

| 操作 | 出力・確認先 |
| :--- | :--- |
| PC構成の取得 | `log/PC_info_log_YYYYMMDD_HHMM.txt` を自動保存 |
| S.M.A.R.T.の取得 | `log/storage_health_log_YYYYMMDD_HHMM.txt` と `log/storage_info_log_YYYYMMDD_HHMM.txt` を保存 |
| GPU情報の取得 | `log/gpu_info_log_YYYYMMDD_HHMM.txt` を自動保存 |
| メモリ診断結果の表示 | Windowsのイベントログから過去7日分を表示 |

exe版の `log` はexeと同じフォルダ、ソース実行時は `src/log` です。別途エクスポートする操作は不要です。ログの本文形式とファイル名は従来のままです。PC構成の保存に失敗した場合は成功通知を出さず、表示結果を残して保存失敗を通知します。GPUログもexe横へ保存し、再起動後に読み込めるようにしています。

### ソースからの起動・ビルド

Windows・Python 3.12で、プロジェクトのルートからPowerShellで実行します。

```powershell
python -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
.\venv\Scripts\python.exe src\main.py
```

exeを作成する場合は、続けて次を実行します。`dist/PcInfo.exe` が生成されます。CrystalDiskInfoは同梱せず、上記の配置方法に従って別途用意してください。

```powershell
.\venv\Scripts\python.exe -m pip install pyinstaller==6.11.1 setuptools==75.6.0
.\venv\Scripts\python.exe -m PyInstaller --noconfirm --onefile --windowed --name PcInfo --icon src\icons\app_icon.ico --add-data "src\icons;icons" src\main.py
```

## 変更履歴

開発中の変更はUnreleasedへまとめ、正式リリース時に版番号と日付を確定します。mainへの反映と正式リリースは区別します。

### Unreleased

#### Changed

- 既存の4タブとボタンの順序を維持し、文字サイズ・カードの余白・ログ一覧の選択表示を調整。
- OSのライト／ダーク配色に追従し、タブの作業案内と最新の日時付き処理結果を表示。
- 自動保存するテキストログのファイル名・本文形式を維持し、Windows用exeを更新。

#### Fixed

- exe版のGPUログを一時展開先ではなく、exe横の `log` フォルダへ保存・再読込するよう修正。
- PC構成のログ保存に失敗した場合、表示結果を保持して保存失敗を通知し、成功通知を出さないよう修正。
- Flet 0.24.1に対応した配色参照を使用し、診断ログ一覧とエラー表示の実行時エラーを修正。
- 処理中・完了ダイアログの開閉を整理し、通知を閉じた後も画面操作を継続できるよう修正。

## 検証範囲

固定データで、PC構成・GPU・ストレージのテキスト出力を変更前と全文比較し、ファイル名・本文の一致を確認しています。保存失敗時の通知、診断ログの選択・詳細表示、保存済みGPUログの再読込、exe配置を想定した保存先も確認しています。

画面は800×1060と600×660の表示領域で確認し、起動中の明暗切替でも表示した詳細が保持されることを確認しています。FletのWindows画面の起動・接続・終了も確認しています。

実際のWMIによる情報取得、Windowsメモリ診断、管理者権限が必要なCrystalDiskInfoの実行は、対象のWindows環境で別途確認が必要です。
