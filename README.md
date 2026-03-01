# PcInfo
## 概要
このプロジェクトは、Flet フレームワークを使用して作成された PC 診断ツールです。システム情報、メモリ診断、ストレージ診断（S.M.A.R.T. データを含む）、GPU診断を収集し、グラフィカルインターフェイスで表示します。

## プロジェクト構造

```
src/
  main_refactored.py         # メインアプリケーション（リファクタリング版）
  main.py                    # メインアプリケーション（旧版）
  constants.py               # 定数定義
  ui_helpers.py              # UI関連ヘルパー関数
  dialog_helpers.py          # ダイアログ処理
  log_writer.py              # ログファイル出力
  storage_ui.py              # ストレージ診断UI
  memory_ui.py               # メモリ診断UI
  gpu_ui.py                  # GPU診断UI
  system_info_ui.py          # システム情報UI
  diagnostics.py             # メモリ診断処理
  storage_diagnostics.py     # ストレージ診断処理
  gpu_diagnostics.py         # GPU診断処理
  system_info.py             # システム情報取得
  powershell_utils.py        # PowerShellユーティリティ
  CrystalDiskInfo/           # CrystalDiskInfoツール（同梱）
  icons/                     # アイコンファイル
  log/                       # ログファイル出力先
```

## 機能
### 1. PC 情報
「PC構成の取得」ボタンをクリックして、OS、CPU、メモリモジュール、ストレージデバイスなどのシステム情報を取得し表示します。
また、取得した情報をテキスト形式で出力します。

[![](https://img.youtube.com/vi/4Sf7aIXsAHA/0.jpg)](https://www.youtube.com/watch?v=4Sf7aIXsAHA)


### 2. メモリ診断
「メモリ診断結果の表示」ボタンをクリックして、システムのメモリ診断ログを取得します。
また、「Windowsメモリ診断の実行」ボタンをクリックして、Windows メモリ診断ツールを実行することもできます。

![2](https://github.com/user-attachments/assets/a3d65f02-efd5-4884-b2d1-3102dafef196)

### 3. ストレージ診断
「診断結果の表示」ボタンをクリックして、保存されたストレージ診断ログを表示します。
新しい S.M.A.R.T. データを取得するには、「S.M.A.R.T. の取得」ボタンをクリックします。CrystalDiskInfo がバックグラウンドで実行され、新しいログが表示されます。

![3](https://github.com/user-attachments/assets/3ec21212-1875-4850-ac90-d8a9eae53a65)

## トラブルシューティング
### DiskInfo32.exe が見つからない場合
DiskInfo32.exe が見つからない場合、CrystalDiskInfo が正しい場所にインストールされているか、プロジェクト内の CrystalDiskInfo ディレクトリに DiskInfo32.exe が存在することを確認してください。

## ライセンス
このプロジェクトは MIT ライセンスの下で提供されています。詳細については LICENSE ファイルをご覧ください。

また、本ソフトウェアのS.M.A.R.T. の取得には、hiyohiyo氏が作成されたCrystalDiskInfoを使用しています。
当該ソフトウェアはMITライセンスで提供されており、本ソフトウェアに複製する形で同梱させていただいております。この場を借りてお礼申し上げます。
当該ソフトウェアを使用する機能について、内容や削除の要請があった場合には、直ちに対応いたします。

