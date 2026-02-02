"""
Create Japanese report with CloudCompare screenshots
"""
import base64
import os

PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
FIGURES_DIR = f"{PROJECT_ROOT}/04_Results/figures"
SCREENSHOTS_DIR = f"{PROJECT_ROOT}/02_Screenshots/San Juan Fault"

def encode_image(filepath):
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return ''

# Charts
img_treeiso_opt = encode_image(f'{FIGURES_DIR}/treeiso_optimization_comparison.png')
img_complete = encode_image(f'{FIGURES_DIR}/complete_method_comparison.png')

# CloudCompare screenshots
img_dbscan_side = encode_image(f'{SCREENSHOTS_DIR}/dbscan_侧视图.png')
img_dbscan_bottom = encode_image(f'{SCREENSHOTS_DIR}/dbscan_仰视图.png')
img_treeiso_side = encode_image(f'{SCREENSHOTS_DIR}/treeiso_optimized_侧视图.png')
img_treeiso_top = encode_image(f'{SCREENSHOTS_DIR}/treeiso_optimized_俯视图.png')

print("All images encoded")

html_content = f'''<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>個別樹木分離実験報告</title>
    <style>
        @page {{ margin: 1cm; size: A4; }}
        body {{
            font-family: "Hiragino Kaku Gothic ProN", "Yu Gothic", sans-serif;
            line-height: 1.5; color: #333; max-width: 800px; margin: 0 auto; padding: 15px; background: white; font-size: 12px;
        }}
        h1 {{ font-size: 20px; text-align: center; border-bottom: 2px solid #2e7d32; padding-bottom: 8px; margin-bottom: 15px; }}
        h2 {{ font-size: 14px; background: #2e7d32; color: white; padding: 6px 12px; margin: 20px 0 10px 0; }}
        .info {{ background: #f5f5f5; padding: 8px 12px; margin-bottom: 15px; font-size: 11px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 10px 0; font-size: 11px; }}
        th, td {{ border: 1px solid #ccc; padding: 6px 8px; text-align: center; }}
        th {{ background: #2e7d32; color: white; }}
        .good {{ background: #c8e6c9; font-weight: bold; }}
        .bad {{ background: #ffcdd2; }}
        .img-section {{ margin: 15px 0; text-align: center; page-break-inside: avoid; }}
        .img-section img {{ max-width: 100%; width: 700px; border: 1px solid #ddd; }}
        .img-caption {{ font-size: 11px; color: #666; margin-top: 5px; }}
        .two-img {{ display: flex; gap: 10px; justify-content: center; flex-wrap: wrap; }}
        .two-img .img-box {{ flex: 1; min-width: 300px; max-width: 380px; text-align: center; }}
        .two-img img {{ width: 100%; border: 1px solid #ddd; }}
        .box {{ border: 1px solid #2e7d32; padding: 10px 12px; margin: 12px 0; background: #f1f8e9; }}
        .box-blue {{ border: 1px solid #1976d2; padding: 10px 12px; margin: 12px 0; background: #e3f2fd; }}
        .footer {{ margin-top: 20px; padding-top: 10px; border-top: 1px solid #ccc; font-size: 10px; color: #666; text-align: center; }}
        @media print {{ .no-print {{ display: none; }} }}
    </style>
</head>
<body>

<h1>🌲 個別樹木分離 (ITI) 実験報告</h1>

<div class="info">
    <strong>日付</strong>: 2026年1月31日 ｜ 
    <strong>データ</strong>: San Juan Fault 森林点群 (98,671点) ｜ 
    <strong>目的</strong>: UAV-LiDAR点群から個別樹木を分離
</div>

<h2>📊 実験結果</h2>

<table>
    <tr><th>手法</th><th>検出樹木数</th><th>特徴</th><th>評価</th></tr>
    <tr><td>DBSCAN (eps=0.5)</td><td>155</td><td>ノイズ率 43.6%</td><td>断片が多い</td></tr>
    <tr class="good"><td>DBSCAN (eps=0.8)</td><td>110</td><td>ノイズ率 14.3%</td><td>✅ 推奨</td></tr>
    <tr class="bad"><td>TreeISO (デフォルト)</td><td>12</td><td>アルゴリズム不適合</td><td>❌ 過小分割</td></tr>
    <tr class="good"><td>TreeISO (最適化後)</td><td>91</td><td>前処理+調整</td><td>✅ 7.6倍改善</td></tr>
</table>

<h2>📈 分析グラフ</h2>

<div class="img-section">
    <img src="data:image/png;base64,{img_treeiso_opt}" alt="TreeISO最適化比較">
    <div class="img-caption">図1: TreeISO 最適化前後の比較</div>
</div>

<div class="img-section">
    <img src="data:image/png;base64,{img_complete}" alt="全手法比較">
    <div class="img-caption">図2: 全手法の比較</div>
</div>

<h2>🖼️ 3D可視化結果 (CloudCompare)</h2>

<p style="font-size:11px; color:#666;">各色は異なる樹木を表しています。</p>

<h3 style="font-size:13px; margin:15px 0 10px 0;">DBSCAN 分割結果 (155本)</h3>
<div class="two-img">
    <div class="img-box">
        <img src="data:image/png;base64,{img_dbscan_side}" alt="DBSCAN側視図">
        <div class="img-caption">側視図</div>
    </div>
    <div class="img-box">
        <img src="data:image/png;base64,{img_dbscan_bottom}" alt="DBSCAN仰視図">
        <div class="img-caption">仰視図</div>
    </div>
</div>

<h3 style="font-size:13px; margin:15px 0 10px 0;">TreeISO 最適化版 分割結果 (91本)</h3>
<div class="two-img">
    <div class="img-box">
        <img src="data:image/png;base64,{img_treeiso_side}" alt="TreeISO側視図">
        <div class="img-caption">側視図</div>
    </div>
    <div class="img-box">
        <img src="data:image/png;base64,{img_treeiso_top}" alt="TreeISO俯視図">
        <div class="img-caption">俯視図</div>
    </div>
</div>

<h2>🔍 主な発見</h2>

<div class="box">
    <strong>TreeISO失敗の原因</strong>: TreeISOは地上レーザースキャン（TLS）向けに設計されており、
    樹幹情報を分割の基準点として使用します。UAVデータは樹幹情報が不足するため、
    前処理とパラメータ調整が必要でした。最適化により12本→91本に改善（7.6倍）。
</div>

<div class="box-blue">
    <strong>🚀 研究室での研究方向</strong><br>
    従来手法はパラメータ調整が必要で、樹冠重複領域での精度が課題です。
    <strong>深層学習を用いた新しい手法</strong>に挑戦し、自動化と精度向上を目指したいと考えています。
</div>

<div class="footer">
    <p class="no-print">💡 <strong>Cmd + P</strong> でPDFに保存</p>
</div>

</body>
</html>'''

output_path = f"{PROJECT_ROOT}/04_Results/reports/advisor_report_ja.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Report saved: {output_path}")
