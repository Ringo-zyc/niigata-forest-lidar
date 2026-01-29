#!/usr/bin/env python3
"""
使用 RANSAC 从点云中检测圆柱体（树木）
"""
import open3d as o3d
import numpy as np
import csv
import os
from scipy.spatial import KDTree
from sklearn.decomposition import PCA

# 配置参数
INPUT_FILE = "/Users/zyc/Downloads/Niigata_Research_Prep/01_Processed/tree.ply"
OUTPUT_CSV = "/Users/zyc/Downloads/Niigata_Research_Prep/04_Results/tree_cylinders.csv"

# RANSAC 参数
DISTANCE_THRESHOLD = 0.06  # 点到圆柱体的最大距离
MIN_POINTS = 50           # 一个圆柱体的最少点数
MIN_RADIUS = 0.03         # 最小半径 (m)
MAX_RADIUS = 0.8          # 最大半径 (m)
MIN_HEIGHT = 1.0          # 最小高度 (m)
MAX_ITERATIONS = 100      # 最多检测多少个圆柱体

# Import shared logic from local module
import sys
try:
    from tree_utils import detect_cylinders
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from tree_utils import detect_cylinders

def detect_cylinders_wrapper(pcd):
    """Wrapper to call shared detection with global constants"""
    points = np.asarray(pcd.points)
    
    # Use print as the logging callback
    return detect_cylinders(
        points=points,
        min_points=MIN_POINTS,
        distance_threshold=DISTANCE_THRESHOLD,
        min_radius=MIN_RADIUS,
        max_radius=MAX_RADIUS,
        min_height=MIN_HEIGHT,
        max_iterations=MAX_ITERATIONS,
        log_callback=print
    )

def save_results(cylinders, output_path):
    """保存结果到 CSV"""
    if not cylinders:
        print("\n⚠️  未检测到任何圆柱体")
        print("提示：可能需要调整参数 MIN_RADIUS, MAX_RADIUS, MIN_HEIGHT, DISTANCE_THRESHOLD")
        return
    
    # 按直径排序
    cylinders.sort(key=lambda x: x['diameter'], reverse=True)
    
    with open(output_path, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['Radius (m)', 'Diameter_DBH (cm)', 'Height (m)', 'Num_Points', 'X', 'Y', 'Z'])
        for cyl in cylinders:
            writer.writerow([
                f"{cyl['radius']:.4f}",
                f"{cyl['diameter']:.2f}",
                f"{cyl['height']:.2f}",
                cyl['num_points'],
                f"{cyl['center'][0]:.4f}",
                f"{cyl['center'][1]:.4f}",
                f"{cyl['center'][2]:.4f}"
            ])
    
    print(f"\n✅ 成功！检测到 {len(cylinders)} 棵树")
    print(f"结果已保存到: {output_path}")

def main():
    # 检查文件
    if not os.path.exists(INPUT_FILE):
        print(f"❌ 文件不存在: {INPUT_FILE}")
        return
    
    # 加载点云
    print(f"正在加载点云: {INPUT_FILE}")
    pcd = o3d.io.read_point_cloud(INPUT_FILE)
    
    if len(pcd.points) == 0:
        print("❌ 点云为空")
        return
    
    print(f"✅ 成功加载 {len(pcd.points)} 个点\n")
    
    # 检测圆柱体
    cylinders = detect_cylinders_wrapper(pcd)
    
    # 保存结果
    save_results(cylinders, OUTPUT_CSV)

if __name__ == "__main__":
    main()
