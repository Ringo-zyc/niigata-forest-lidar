"""
Treeiso Wrapper for PLY Point Clouds
适配 Treeiso 算法用于 PLY 格式点云

Treeiso 原本用于 TLS (地面激光扫描) 的 LAZ 格式
此脚本将其适配为支持 PLY 格式的 UAV-LiDAR 数据
"""

import sys
import os
import numpy as np
import open3d as o3d
from datetime import datetime

# 添加 treeiso 路径
sys.path.insert(0, '/tmp/treeiso/Python')

# 导入 treeiso 核心函数
try:
    from treeiso import init_segs, intermediate_segs, final_segs, decimate_pcd
    from treeiso import PR_DECIMATE_RES1, PR_DECIMATE_RES2
    TREEISO_AVAILABLE = True
except ImportError as e:
    print(f"Warning: Failed to import treeiso: {e}")
    TREEISO_AVAILABLE = False


def load_ply(filepath):
    """加载 PLY 点云"""
    print(f"加载点云: {filepath}")
    pcd = o3d.io.read_point_cloud(filepath)
    points = np.asarray(pcd.points)
    print(f"  点数: {len(points):,}")
    return pcd, points


def run_treeiso(points, verbose=True):
    """
    运行 Treeiso 单木分离算法
    
    Args:
        points: (N, 3) numpy array
        verbose: 是否输出详细信息
    
    Returns:
        labels: 每个点的树木标签
    """
    if not TREEISO_AVAILABLE:
        raise ImportError("Treeiso 未正确安装")
    
    # 中心化点云
    pcd = points - np.mean(points, axis=0)
    
    if verbose:
        print("\n[阶段 1/3] 3D 初始分割 (cut-pursuit)...")
    
    # 降采样以加速 - 使用一致的降采样
    dec_idx_uidx, dec_inverse_idx = decimate_pcd(pcd, PR_DECIMATE_RES1)
    pcd_dec = pcd[dec_idx_uidx]
    
    if verbose:
        print(f"  降采样: {len(pcd):,} -> {len(pcd_dec):,} 点")
    
    # 初始分割
    init_labels = init_segs(pcd_dec)
    
    if verbose:
        n_init = len(np.unique(init_labels))
        print(f"  初始分割: {n_init} 个片段")
    
    if verbose:
        print("\n[阶段 2/3] 2D 中间分割...")
    
    # 中间分割 - 使用相同的降采样点
    pcd_with_init = np.concatenate([
        pcd_dec,
        init_labels[:, np.newaxis]
    ], axis=-1)
    
    intermediate_labels = intermediate_segs(pcd_with_init)
    
    if verbose:
        n_inter = len(np.unique(intermediate_labels))
        print(f"  中间分割: {n_inter} 个片段")
    
    if verbose:
        print("\n[阶段 3/3] 最终树木合并...")
    
    # 最终分割 - 使用降采样后的点
    pcd_with_inter = np.concatenate([
        pcd_dec,
        init_labels[:, np.newaxis],
        intermediate_labels[:, np.newaxis]
    ], axis=-1)
    
    final_labels = final_segs(pcd_with_inter)
    
    # 将标签映射回原始点云
    final_labels_full = final_labels[dec_inverse_idx]
    
    n_trees = len(np.unique(final_labels_full))
    if verbose:
        print(f"  最终结果: {n_trees} 棵树")
    
    return final_labels_full.astype(np.int32)


def save_results(pcd, points, labels, output_dir):
    """保存分割结果"""
    os.makedirs(output_dir, exist_ok=True)
    
    # 统计
    unique_labels = sorted(set(labels))
    n_trees = len(unique_labels)
    
    print(f"\n保存结果到: {output_dir}")
    
    # 生成彩色点云
    np.random.seed(42)
    colors = np.random.rand(max(labels) + 2, 3)
    
    point_colors = np.zeros((len(labels), 3))
    for i, label in enumerate(labels):
        point_colors[i] = colors[label]
    
    pcd_colored = o3d.geometry.PointCloud()
    pcd_colored.points = o3d.utility.Vector3dVector(points)
    pcd_colored.colors = o3d.utility.Vector3dVector(point_colors)
    
    # 保存带颜色的完整点云
    output_ply = os.path.join(output_dir, 'treeiso_labeled.ply')
    o3d.io.write_point_cloud(output_ply, pcd_colored)
    print(f"  已保存: treeiso_labeled.ply")
    
    # 保存 CSV 统计
    import pandas as pd
    tree_info = []
    for label in unique_labels:
        mask = labels == label
        tree_points = points[mask]
        tree_info.append({
            'tree_id': label,
            'n_points': len(tree_points),
            'x_center': tree_points[:, 0].mean(),
            'y_center': tree_points[:, 1].mean(),
            'z_min': tree_points[:, 2].min(),
            'z_max': tree_points[:, 2].max(),
            'height': tree_points[:, 2].max() - tree_points[:, 2].min()
        })
    
    df = pd.DataFrame(tree_info)
    csv_path = os.path.join(output_dir, 'treeiso_trees_summary.csv')
    df.to_csv(csv_path, index=False)
    print(f"  已保存: treeiso_trees_summary.csv")
    
    return df


def visualize(pcd, labels):
    """可视化分割结果"""
    np.random.seed(42)
    colors = np.random.rand(max(labels) + 2, 3)
    
    point_colors = np.zeros((len(labels), 3))
    for i, label in enumerate(labels):
        point_colors[i] = colors[label]
    
    pcd_vis = o3d.geometry.PointCloud()
    pcd_vis.points = pcd.points
    pcd_vis.colors = o3d.utility.Vector3dVector(point_colors)
    
    print("\n打开 3D 可视化窗口...")
    print("  操作: 鼠标左键旋转, 滚轮缩放, 右键平移")
    print("  按 Q 或关闭窗口继续")
    
    o3d.visualization.draw_geometries(
        [pcd_vis],
        window_name="Treeiso Result",
        width=1200,
        height=800
    )


if __name__ == "__main__":
    print("=" * 60)
    print("Treeiso 单木分离 (PLY 适配版)")
    print(f"时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    
    # 配置
    PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
    INPUT_FILE = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/Off-Ground_Good-5m.ply"
    OUTPUT_DIR = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_treeiso"
    
    # 加载
    pcd, points = load_ply(INPUT_FILE)
    
    # 运行 Treeiso
    try:
        labels = run_treeiso(points, verbose=True)
        
        # 保存
        df = save_results(pcd, points, labels, OUTPUT_DIR)
        
        print("\n" + "=" * 60)
        print(f"完成！共检测到 {len(df)} 棵树")
        print("=" * 60)
        
        print("\n前 10 棵树信息:")
        print(df.head(10))
        
        # 可视化
        visualize(pcd, labels)
        
    except Exception as e:
        print(f"\n错误: {e}")
        print("Treeiso 可能需要更多配置才能运行在此数据集上")
        import traceback
        traceback.print_exc()
