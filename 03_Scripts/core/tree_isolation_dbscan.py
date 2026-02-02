"""
Individual Tree Isolation using DBSCAN clustering
基于 DBSCAN 的单木分离

优化点：
- 支持 2D 投影聚类（忽略 Z 轴，解决树干断裂问题）
- 支持 3D 聚类（保留完整空间信息）
- 自动保存分离结果和统计信息
"""

import numpy as np
import open3d as o3d
from sklearn.cluster import DBSCAN
import pandas as pd
import os
from datetime import datetime


def load_point_cloud(filepath):
    """加载点云数据"""
    print(f"加载点云: {filepath}")
    pcd = o3d.io.read_point_cloud(filepath)
    points = np.asarray(pcd.points)
    print(f"  点数: {len(points):,}")
    print(f"  范围: X[{points[:,0].min():.1f}, {points[:,0].max():.1f}], "
          f"Y[{points[:,1].min():.1f}, {points[:,1].max():.1f}], "
          f"Z[{points[:,2].min():.1f}, {points[:,2].max():.1f}]")
    return pcd, points


def isolate_trees_dbscan(points, eps=0.5, min_samples=50, use_2d=True):
    """
    使用 DBSCAN 进行单木分离
    
    Args:
        points: (N, 3) numpy array
        eps: 邻域半径（米）
        min_samples: 最小点数
        use_2d: 是否使用 2D 投影聚类（推荐用于切片数据）
    
    Returns:
        labels: 每个点的聚类标签（-1 表示噪声）
        n_trees: 检测到的树木数量
    """
    mode = "2D (XY投影)" if use_2d else "3D"
    print(f"\n执行 DBSCAN [{mode}]: eps={eps}, min_samples={min_samples}")
    
    # 选择聚类数据
    if use_2d:
        # 2D 投影：只用 X, Y 坐标，忽略 Z 轴断裂
        cluster_data = points[:, :2]
    else:
        # 3D 聚类：使用完整坐标
        cluster_data = points
    
    # DBSCAN 聚类
    clustering = DBSCAN(eps=eps, min_samples=min_samples, n_jobs=-1)
    labels = clustering.fit_predict(cluster_data)
    
    # 统计结果
    n_trees = len(set(labels)) - (1 if -1 in labels else 0)
    n_noise = (labels == -1).sum()
    
    print(f"  检测到 {n_trees} 棵树")
    print(f"  噪声点: {n_noise:,} ({n_noise/len(points)*100:.1f}%)")
    
    return labels, n_trees


def save_isolated_trees(pcd, points, labels, output_dir):
    """将每棵树保存为单独的文件"""
    os.makedirs(output_dir, exist_ok=True)
    
    unique_labels = sorted(set(labels))
    tree_info = []
    
    print(f"\n保存单木点云到: {output_dir}")
    
    for label in unique_labels:
        if label == -1:  # 跳过噪声
            continue
            
        # 提取该树的点
        mask = labels == label
        tree_points = points[mask]
        
        # 创建点云对象
        tree_pcd = o3d.geometry.PointCloud()
        tree_pcd.points = o3d.utility.Vector3dVector(tree_points)
        
        # 如果原始点云有颜色，保留颜色
        if pcd.has_colors():
            colors = np.asarray(pcd.colors)[mask]
            tree_pcd.colors = o3d.utility.Vector3dVector(colors)
        
        # 保存
        filename = f"tree_{label:04d}.ply"
        filepath = os.path.join(output_dir, filename)
        o3d.io.write_point_cloud(filepath, tree_pcd)
        
        # 记录基本信息
        tree_info.append({
            'tree_id': label,
            'n_points': len(tree_points),
            'x_center': tree_points[:, 0].mean(),
            'y_center': tree_points[:, 1].mean(),
            'z_min': tree_points[:, 2].min(),
            'z_max': tree_points[:, 2].max(),
            'height': tree_points[:, 2].max() - tree_points[:, 2].min()
        })
    
    # 保存汇总信息
    df = pd.DataFrame(tree_info)
    summary_path = os.path.join(output_dir, 'isolated_trees_summary.csv')
    df.to_csv(summary_path, index=False)
    print(f"  已保存 {len(tree_info)} 棵树")
    print(f"  汇总表: {summary_path}")
    
    return df


def visualize_isolated_trees(pcd, labels, show=True):
    """可视化分割结果（每棵树不同颜色）"""
    # 生成随机颜色
    max_label = labels.max()
    np.random.seed(42)  # 固定随机种子，保证颜色一致
    colors = np.random.rand(max_label + 2, 3)
    colors[-1] = [0.2, 0.2, 0.2]  # 噪声为深灰色
    
    # 应用颜色
    point_colors = np.zeros((len(labels), 3))
    for i, label in enumerate(labels):
        if label == -1:
            point_colors[i] = colors[-1]
        else:
            point_colors[i] = colors[label]
    
    pcd_colored = o3d.geometry.PointCloud()
    pcd_colored.points = pcd.points
    pcd_colored.colors = o3d.utility.Vector3dVector(point_colors)
    
    if show:
        print("\n打开 3D 可视化窗口...")
        print("  操作: 鼠标左键旋转, 滚轮缩放, 右键平移")
        print("  按 Q 或关闭窗口退出")
        o3d.visualization.draw_geometries(
            [pcd_colored],
            window_name="Individual Tree Isolation Result",
            width=1200,
            height=800
        )
    
    return pcd_colored


def run_isolation(input_file, output_dir, eps=0.5, min_samples=50, use_2d=True, visualize=False):
    """
    单木分离主函数
    
    Args:
        input_file: 输入点云路径 (.ply)
        output_dir: 输出目录
        eps: DBSCAN 邻域半径
        min_samples: 最小点数
        use_2d: 是否使用 2D 投影
        visualize: 是否显示可视化
    
    Returns:
        DataFrame with tree information
    """
    print("=" * 60)
    print("Individual Tree Isolation (DBSCAN)")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 加载
    pcd, points = load_point_cloud(input_file)
    
    # 分离
    labels, n_trees = isolate_trees_dbscan(points, eps, min_samples, use_2d)
    
    # 保存
    df = save_isolated_trees(pcd, points, labels, output_dir)
    
    # 可视化
    if visualize:
        visualize_isolated_trees(pcd, labels)
    
    print("\n" + "=" * 60)
    print(f"完成！共检测到 {n_trees} 棵树")
    print("=" * 60)
    
    return df, labels


# 主程序
if __name__ == "__main__":
    # 配置路径
    PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
    INPUT_FILE = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/Off-Ground_Good-5m.ply"
    OUTPUT_DIR = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_dbscan"
    
    # 运行分离
    df, labels = run_isolation(
        input_file=INPUT_FILE,
        output_dir=OUTPUT_DIR,
        eps=0.5,        # 尝试: 0.3, 0.5, 0.8, 1.0
        min_samples=50, # 尝试: 30, 50, 100
        use_2d=True,    # 推荐：切片数据用 2D
        visualize=True  # 设为 False 跳过可视化
    )
    
    print("\n前 10 棵树信息:")
    print(df.head(10))
