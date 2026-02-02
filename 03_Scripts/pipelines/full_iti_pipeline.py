"""
完整的单木分离和测量流程
Individual Tree Isolation Full Pipeline

一键运行：分离 + 测量 + 可视化
"""

import os
import sys
from datetime import datetime

# 添加脚本目录到路径
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)
if PARENT_DIR not in sys.path:
    sys.path.insert(0, PARENT_DIR)

from core.tree_isolation_dbscan import load_point_cloud, isolate_trees_dbscan, save_isolated_trees, visualize_isolated_trees
from analysis.measure_isolated_tree import batch_measure_trees


def run_full_pipeline(
    input_ply,
    output_dir,
    eps=0.5,
    min_samples=50,
    use_2d=True,
    visualize=True,
    measure_method='circle'
):
    """
    完整流程：
    1. 加载点云
    2. DBSCAN 单木分离
    3. 导出单棵树
    4. 批量测量 DBH
    5. 可视化结果
    
    Args:
        input_ply: 输入点云路径
        output_dir: 输出目录
        eps: DBSCAN 邻域半径
        min_samples: 最小点数
        use_2d: 是否使用 2D 投影（推荐）
        visualize: 是否显示 3D 可视化
        measure_method: DBH 测量方法 ('circle' 或 'ransac')
    """
    print("=" * 70)
    print("🌲 Individual Tree Isolation - Full Pipeline 🌲")
    print(f"   时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70)
    
    # 创建输出目录
    trees_dir = os.path.join(output_dir, 'isolated_trees')
    os.makedirs(trees_dir, exist_ok=True)
    os.makedirs(output_dir, exist_ok=True)
    
    # ========================================
    # Step 1: 加载
    # ========================================
    print("\n" + "─" * 50)
    print("[Step 1/4] 📂 加载点云")
    print("─" * 50)
    pcd, points = load_point_cloud(input_ply)
    
    # ========================================
    # Step 2: 分离
    # ========================================
    print("\n" + "─" * 50)
    print("[Step 2/4] 🔍 DBSCAN 单木分离")
    print("─" * 50)
    labels, n_trees = isolate_trees_dbscan(points, eps, min_samples, use_2d)
    
    # ========================================
    # Step 3: 导出
    # ========================================
    print("\n" + "─" * 50)
    print("[Step 3/4] 💾 导出单棵树")
    print("─" * 50)
    summary_df = save_isolated_trees(pcd, points, labels, trees_dir)
    
    # ========================================
    # Step 4: 测量
    # ========================================
    print("\n" + "─" * 50)
    print("[Step 4/4] 📏 批量测量 DBH")
    print("─" * 50)
    measurements_csv = os.path.join(output_dir, 'tree_measurements.csv')
    measurements_df = batch_measure_trees(trees_dir, measurements_csv, method=measure_method)
    
    # ========================================
    # 汇总报告
    # ========================================
    print("\n" + "=" * 70)
    print("📊 Pipeline 完成！结果汇总：")
    print("=" * 70)
    print(f"  📁 输入文件: {os.path.basename(input_ply)}")
    print(f"  🌲 检测树木: {n_trees} 棵")
    print(f"  📏 成功测量: {len(measurements_df)} 棵")
    
    if len(measurements_df) > 0:
        print(f"\n  📈 DBH 统计:")
        print(f"     范围: {measurements_df['dbh_cm'].min():.1f} - {measurements_df['dbh_cm'].max():.1f} cm")
        print(f"     平均: {measurements_df['dbh_cm'].mean():.1f} cm")
        print(f"     中位数: {measurements_df['dbh_cm'].median():.1f} cm")
    
    print(f"\n  📂 输出位置:")
    print(f"     单木点云: {trees_dir}")
    print(f"     测量结果: {measurements_csv}")
    print("=" * 70)
    
    # 可视化
    if visualize:
        print("\n正在生成 3D 可视化...")
        visualize_isolated_trees(pcd, labels)
    
    return {
        'n_trees': n_trees,
        'n_measured': len(measurements_df),
        'trees_dir': trees_dir,
        'measurements_csv': measurements_csv,
        'summary': summary_df,
        'measurements': measurements_df
    }


# ========================================
# 主程序
# ========================================
if __name__ == "__main__":
    # 配置
    PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
    
    # 输入文件（选择其中一个）
    INPUT_FILE = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/Off-Ground_Good-5m.ply"
    # INPUT_FILE = f"{PROJECT_ROOT}/01_Processed/StREAM Lab/tree.ply"
    
    # 输出目录
    OUTPUT_DIR = f"{PROJECT_ROOT}/04_Results/iti_pipeline_output"
    
    # 运行完整流程
    result = run_full_pipeline(
        input_ply=INPUT_FILE,
        output_dir=OUTPUT_DIR,
        eps=0.5,            # 邻域半径（米）
        min_samples=50,     # 最小点数
        use_2d=True,        # 推荐：使用 2D 投影聚类
        visualize=True,     # 完成后显示 3D 可视化
        measure_method='circle'  # 使用 2D 圆拟合测量 DBH
    )
    
    print("\n✅ 所有步骤完成！")
