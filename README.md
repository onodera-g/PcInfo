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
| **ログ保存** | 全診断結果をテキスト形式（.txt）で自動保存 | 

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

## 各タブの機能イメージ

###  PC 情報
<div align="left">
  <img src="https://github.com/user-attachments/assets/2e38adf5-b01c-46af-a96f-c5b2ea5c3e4a" width="50%" alt="PcInfo スクリーンショット">
</div>

###  メモリ診断
<div align="left">
  <img src="a" width="50%" alt="メモリ診断">
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
