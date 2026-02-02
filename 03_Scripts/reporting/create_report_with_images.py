"""
Create HTML report with embedded base64 images
"""
import base64
import os

PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
FIGURES_DIR = f"{PROJECT_ROOT}/04_Results/figures"

# Read and encode images
def encode_image(filename):
    filepath = os.path.join(FIGURES_DIR, filename)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            return base64.b64encode(f.read()).decode('utf-8')
    return ''

img_treeiso_opt = encode_image('treeiso_optimization_comparison.png')
img_complete = encode_image('complete_method_comparison.png')
img_journey = encode_image('optimization_journey.png')
img_radar = encode_image('method_radar_chart.png')

print("Images encoded successfully")

html_content = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>单木分离实验汇报</title>
    <style>
        @page {{ margin: 1.5cm; size: A4; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "PingFang SC", "Hiragino Sans GB", sans-serif;
            line-height: 1.6; color: #333; max-width: 900px; margin: 0 auto; padding: 20px; background: white;
        }}
        h1 {{ color: #1a5f2a; border-bottom: 3px solid #27ae60; padding-bottom: 10px; font-size: 26px; margin-top: 0; text-align: center; }}
        h2 {{ color: white; margin-top: 25px; font-size: 18px; background: linear-gradient(90deg, #27ae60, #2ecc71); padding: 8px 15px; border-radius: 5px; }}
        .header-info {{ background: #f0f9f4; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #27ae60; }}
        .header-info p {{ margin: 3px 0; font-size: 13px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 12px 0; font-size: 13px; }}
        th, td {{ border: 1px solid #ddd; padding: 8px 10px; text-align: center; }}
        th {{ background: #27ae60; color: white; font-weight: 600; }}
        tr:nth-child(even) {{ background: #f9f9f9; }}
        .good {{ background: #d4edda !important; color: #155724; font-weight: bold; }}
        .bad {{ background: #f8d7da !important; color: #721c24; }}
        .chart-container {{ text-align: center; margin: 15px 0; page-break-inside: avoid; }}
        .chart-container img {{ max-width: 100%; border: 1px solid #ddd; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1); }}
        .chart-caption {{ font-size: 12px; color: #666; margin-top: 5px; }}
        .key-point {{ background: #fff3cd; border-left: 4px solid #ffc107; padding: 10px 15px; margin: 12px 0; border-radius: 0 8px 8px 0; font-size: 14px; }}
        .conclusion-box {{ background: #e8f5e9; border: 2px solid #27ae60; padding: 15px 20px; border-radius: 10px; margin: 20px 0; }}
        .conclusion-box h3 {{ color: #1a5f2a; margin-top: 0; font-size: 16px; }}
        .future-box {{ background: #e3f2fd; border: 2px solid #2196f3; padding: 15px 20px; border-radius: 10px; margin: 20px 0; }}
        .future-box h3 {{ color: #1565c0; margin-top: 0; font-size: 16px; }}
        ul {{ padding-left: 20px; margin: 8px 0; }}
        li {{ margin: 5px 0; font-size: 14px; }}
        .two-col {{ display: flex; gap: 15px; flex-wrap: wrap; }}
        .two-col > div {{ flex: 1; min-width: 380px; }}
        .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid #ddd; font-size: 11px; color: #666; text-align: center; }}
        @media print {{ body {{ padding: 0; }} .no-print {{ display: none; }} .chart-container img {{ max-height: 250px; }} }}
    </style>
</head>
<body>

<h1>🌲 单木分离 (ITI) 实验汇报</h1>

<div class="header-info">
    <p><strong>日期</strong>: 2026年1月31日 &nbsp; | &nbsp; <strong>数据</strong>: San Juan Fault 森林点云 (98,671点) &nbsp; | &nbsp; <strong>目标</strong>: 从点云中分离单棵树木</p>
</div>

<h2>📊 实验结果对比</h2>

<table>
    <tr><th>方法</th><th>检测树数</th><th>特点</th><th>评价</th></tr>
    <tr><td>DBSCAN (eps=0.5)</td><td>155</td><td>噪声率 43.6%</td><td>碎片过多</td></tr>
    <tr class="good"><td><strong>DBSCAN (eps=0.8)</strong></td><td><strong>110</strong></td><td>噪声率 14.3%</td><td>✅ 效果较好</td></tr>
    <tr class="bad"><td>TreeISO (默认)</td><td>12</td><td>算法不适配</td><td>❌ 严重欠分割</td></tr>
    <tr class="good"><td><strong>TreeISO (优化后)</strong></td><td><strong>91</strong></td><td>预处理+调参</td><td>✅ 提升 7.6 倍</td></tr>
</table>

<h2>📈 可视化对比</h2>

<div class="two-col">
    <div class="chart-container">
        <img src="data:image/png;base64,{img_treeiso_opt}" alt="TreeISO优化前后对比">
        <div class="chart-caption">图1: TreeISO 优化前后对比</div>
    </div>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_complete}" alt="全方法对比">
        <div class="chart-caption">图2: 所有方法对比</div>
    </div>
</div>

<div class="two-col">
    <div class="chart-container">
        <img src="data:image/png;base64,{img_journey}" alt="优化历程">
        <div class="chart-caption">图3: TreeISO 优化历程</div>
    </div>
    <div class="chart-container">
        <img src="data:image/png;base64,{img_radar}" alt="方法特性雷达图">
        <div class="chart-caption">图4: 方法特性对比</div>
    </div>
</div>

<h2>🔍 关键发现</h2>

<div class="key-point">
    <strong>TreeISO 失败原因</strong>: 该算法是为<strong>地面激光扫描 (TLS)</strong> 设计的，依赖树干信息作为参考点。
    但 UAV 数据从空中扫描，主要看到树冠，缺少树干信息，导致算法假设不成立。
    <br><br>
    <strong>解决方案</strong>: 通过增强预处理（去噪）和调整参数（增强正则化），效果从 12 棵树提升至 91 棵树（7.6倍）。
</div>

<div class="conclusion-box">
    <h3>📌 本次实验结论</h3>
    <ul>
        <li>传统方法可以完成单木分离任务，但需要针对数据特点进行参数调优</li>
        <li>不同扫描平台（TLS vs UAV）产生的数据特性差异很大，不能直接套用算法</li>
        <li>传统方法在处理<strong>树冠交叠</strong>区域时仍有困难</li>
    </ul>
</div>

<div class="future-box">
    <h3>🚀 进入实验室后的研究方向</h3>
    <p>基于本次实验，我发现传统方法存在以下局限：参数需要针对每个场景手动调整、树冠交叠区域容易分割错误。</p>
    <p><strong>因此，我希望在研究中尝试基于深度学习的新方法</strong>，让模型自动学习如何分割树木，减少人工调参，提高处理复杂场景的能力。</p>
</div>

<div class="footer">
    <p>附件: 详细实验日志 | 参数对比分析 | 方法原理说明</p>
    <p class="no-print">💡 提示: 按 <strong>Cmd + P</strong> 打印为 PDF</p>
</div>

</body>
</html>'''

# Save
output_path = f"{PROJECT_ROOT}/04_Results/reports/advisor_report.html"
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(html_content)

print(f"✅ Report saved: {output_path}")
