# 🌲 UAV-LiDAR 単木検出と樹木情報の自動計測

<div align="center">

![Version](https://img.shields.io/badge/Version-2.2-green)
![Python](https://img.shields.io/badge/Python-3.11+-blue)
![License](https://img.shields.io/badge/License-Academic-orange)

**UAV搭載LiDAR点群データに基づいた森林調査自動化ツール**

[中文](README.md) | [English](README_EN.md)

[クイックスタート](#-クイックスタート) • [機能特徴](#-機能特徴) • [プロジェクト構成](#-プロジェクト構成) • [使用ガイド](#-使用ガイド) • [検証ツール](#-検証ツール)

</div>

---

## 📋 プロジェクト概要

本プロジェクトは、生のLiDAR点群データから単木パラメータ抽出までの完全なワークフローを実現しました：
- 🌳 **単木検出**: RANSAC円柱フィッティングに基づく樹幹認識
- 📏 **DBH抽出**: 胸高直径（Diameter at Breast Height）の自動計測
- 📍 **空間定位**: 各樹木のUTM座標出力
- 📊 **可視化**: 2D分布図 + 3D重ね合わせ図 + インタラクティブプレビュー
- ✅ **検証ツール**: 層化抽出法 + RMSE統計

**研究方向**: UAV搭載レーザ（RCヘリ含む）点群データによる単木識別と樹木情報の自動計測

---

## 🚀 クイックスタート

```bash
# 1. プロジェクトディレクトリへ移動
cd /Users/zyc/Downloads/Niigata_Research_Prep

# 2. GUIを起動（推奨）
./03_Scripts/run.sh

# 3. GUIで操作:
#    - 入力点群データ (.ply) を選択
#    - パラメータを調整（またはデフォルト値を使用）
#    - "検知開始" をクリック
```

---

## ✨ 機能特徴

| 機能 | 説明 | ツール |
|------|------|------|
| **GUIインターフェース** | タブデザイン、検出＋可視化の一体化 | `tools/gui_app.py` |
| **コマンドライン検出** | 画面なしでのバッチ処理 | `core/detect_cylinders_v2.py` |
| **3D可視化** | Matplotlib静的画像 + Open3D対話型 | `tools/visualize_forest.py` |
| **精度検証** | 層化抽出 + RMSE/MAE計算 | `tools/generate_validation_sample.py` |
| **バイオマス分析** | 直径階分布、炭素蓄積量推定 | `analysis/analyze_forest_data.py` |

---

## 📁 プロジェクト構成

```
Niigata_Research_Prep/
├── 00_Raw_Data/                    # 生LiDARデータ (.laz)
│
├── 01_Processed/                   # 前処理済み点群
│
├── 02_Screenshots/                 # 学習プロセスのスクリーンショット
│
├── 03_Scripts/                     # 🐍 コアスクリプト
│   ├── run.sh                     # 統一エントリーポイント
│   ├── core/                      # コアアルゴリズム
│   │   ├── tree_utils.py          # RANSACアルゴリズム中核
│   │   └── detect_cylinders_v2.py # CLI検出スクリプト
│   ├── pipelines/                 # 完全なパイプライン
│   ├── tools/                     # ツールと可視化
│   │   ├── gui_app.py             # GUIメインプログラム
│   │   └── visualize_forest.py    # 可視化生成
│   ├── analysis/                  # データ分析
│   └── experiments/               # 実験比較
│
├── 04_Results/                     # 出力結果
│   ├── figures/                   # 図表 (.png)
│   └── tables/                    # データ表 (.csv)
│
├── docs/                           # 📚 プロジェクト核心ドキュメント
│   ├── technical/                 # 技術文書と構造
│   ├── reports/                   # 📅 レポートと計画
│   ├── research_master_guideline.html  # 🏆 研究マスターガイドライン（入口）
│   └── career_skill_mapping.md         # スキル・キャリアマッピング
│
└── README.md                       # メインドキュメント（中国語）
```

---

## 🔧 使用ガイド

### 方法 1: GUI（推奨）

```bash
./03_Scripts/run.sh
```

**🌲 検出タブ**:
1. 入力点群ファイル (`.ply`) を選択
2. 出力CSVパスを設定
3. RANSACパラメータを調整（任意）
4. "検知開始" をクリック
5. "自動可視化" をチェックすると、完了後に自動で画像を生成します

**🎨 可視化タブ**:
1. 点群ファイルと結果ディレクトリを選択
2. "可視化チャート生成" をクリック
3. "対話型3Dプレビュー" をクリックしてOpen3Dウィンドウを開く

### 方法 2: コマンドライン

```bash
```bash
# 検出
python 03_Scripts/core/detect_cylinders_v2.py

# 可視化
python 03_Scripts/tools/visualize_forest.py <path_to_ply>
```

---

## ⚙️ パラメータ説明

| パラメータ | デフォルト | 説明 |
|------------|------------|------|
| Distance Threshold | 0.06 m | 点から円柱軸までの最大距離 |
| Min Points | 50 | 1つの円柱を構成する最小点数 |
| Min Radius | 0.03 m | 最小半径 (3 cm) |
| Max Radius | 0.8 m | 最大半径 (80 cm) |
| Min Height | 1.0 m | 最小高さ |
| Max Iterations | 100 | 最大検出本数 |

---

## ✅ 検証ツール

### 1. 層化抽出検証テーブルの生成

```bash
python 03_Scripts/tools/generate_validation_sample.py
```

出力: `validation_sample.csv` (DBHサイズごとに層化抽出された9本)

### 2. CloudCompareでの検証

座標を使用して各樹木を特定し、手動で直径を測定して `Manual_DBH_cm` 列に記入します。

### 3. 誤差統計の計算

```bash
python 03_Scripts/analysis/calculate_validation_stats.py
```

出力: RMSE, MAE, 平均誤差などの指標

---

## 📊 出力フォーマット

### CSV カラム

| カラム名 | 単位 | 説明 |
|----------|------|------|
| Radius (m) | m | 樹木半径 |
| Diameter_DBH (cm) | cm | 胸高直径 |
| Height (m) | m | 推定高さ（点群密度により過大評価の可能性あり）|
| Num_Points | 個 | 点群数 |
| X, Y, Z | m | UTM座標 |

---

## 🏗 技術スタック

- **点群処理**: Open3D, CloudCompare
- **アルゴリズム**: RANSAC, PCA (scikit-learn)
- **可視化**: Matplotlib, Open3D
- **GUI**: Tkinter
- **データ分析**: Pandas, NumPy

---

## 📄 ライセンス

学術研究用途に限る。
