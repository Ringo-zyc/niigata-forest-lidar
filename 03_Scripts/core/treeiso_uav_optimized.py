"""
Treeiso Optimized for UAV-LiDAR Data
针对 UAV 数据优化的 Treeiso 版本

优化措施（基于插件作者建议）：
1. 激进的去噪：使用 SOR (Statistical Outlier Removal)
2. 更强的正则化强度：防止稀疏点云导致的过度分割
3. 降采样优化：适应 UAV 点云密度
"""

import sys
import os
import numpy as np
import open3d as o3d
from datetime import datetime

# 添加 treeiso 路径
sys.path.insert(0, '/tmp/treeiso/Python')

print("=" * 60)
print("TreeISO Optimized for UAV-LiDAR")
print("=" * 60)

# ============================================================
# 优化参数（针对 UAV 数据调整）
# ============================================================

# 原始 TLS 参数 vs 优化后的 UAV 参数
PARAMS = {
    'TLS_default': {
        'REG_STRENGTH1': 1.0,   # 3D 初始分割正则化
        'REG_STRENGTH2': 20,    # 2D 中间分割正则化
        'MIN_NN1': 5,           # 3D 初始分割最小邻居
        'MIN_NN2': 20,          # 2D 中间分割最小邻居
        'DECIMATE_RES': 0.05,   # 降采样分辨率
    },
    'UAV_optimized': {
        'REG_STRENGTH1': 5.0,   # ↑ 增强正则化，防止过分割
        'REG_STRENGTH2': 100,   # ↑ 大幅增强 2D 正则化
        'MIN_NN1': 10,          # ↑ 增加最小邻居
        'MIN_NN2': 50,          # ↑ 增加最小邻居
        'DECIMATE_RES': 0.1,    # ↑ 更大的降采样，适应稀疏数据
    }
}

# 使用 UAV 优化参数
USE_PARAMS = 'UAV_optimized'
params = PARAMS[USE_PARAMS]

print(f"\n使用参数配置: {USE_PARAMS}")
for k, v in params.items():
    print(f"  {k}: {v}")

# ============================================================
# 预处理函数
# ============================================================

def load_and_preprocess(filepath, apply_sor=True, sor_neighbors=20, sor_std_ratio=2.0):
    """
    加载并预处理点云
    
    Args:
        filepath: 点云路径
        apply_sor: 是否应用 SOR 滤波
        sor_neighbors: SOR 邻居数
        sor_std_ratio: SOR 标准差倍数
    """
    print(f"\n[预处理] 加载点云: {filepath}")
    pcd = o3d.io.read_point_cloud(filepath)
    points_before = len(pcd.points)
    print(f"  原始点数: {points_before:,}")
    
    if apply_sor:
        print(f"\n[预处理] 应用 SOR 滤波 (Statistical Outlier Removal)")
        print(f"  参数: neighbors={sor_neighbors}, std_ratio={sor_std_ratio}")
        
        # SOR 滤波
        pcd_clean, ind = pcd.remove_statistical_outlier(
            nb_neighbors=sor_neighbors,
            std_ratio=sor_std_ratio
        )
        
        points_after = len(pcd_clean.points)
        removed = points_before - points_after
        print(f"  滤除噪声点: {removed:,} ({removed/points_before*100:.1f}%)")
        print(f"  剩余点数: {points_after:,}")
        
        return pcd_clean, np.asarray(pcd_clean.points)
    
    return pcd, np.asarray(pcd.points)


def decimate_pcd(columns, min_res):
    """降采样点云"""
    _, block_idx_uidx, block_inverse_idx = np.unique(
        np.floor(columns[:, :3] / min_res).astype(np.int32), 
        axis=0, 
        return_index=True, 
        return_inverse=True
    )
    return block_idx_uidx, block_inverse_idx


# ============================================================
# 修改后的 Treeiso 核心函数
# ============================================================

try:
    from cut_pursuit_L0 import cut_pursuit
    from scipy.spatial import cKDTree, ConvexHull
    import numpy_indexed as npi
    TREEISO_AVAILABLE = True
    print("\n✅ Treeiso 依赖加载成功")
except ImportError as e:
    print(f"\n❌ 无法加载 Treeiso 依赖: {e}")
    TREEISO_AVAILABLE = False


def init_segs_optimized(pcd):
    """优化后的初始分割"""
    pcd = pcd[:, :3] - np.mean(pcd[:, :3], axis=0)
    point_count = len(pcd)
    
    kdtree = cKDTree(pcd[:, :3])
    nn_D, nn_idx = kdtree.query(pcd, k=params['MIN_NN1'] + 1)
    indices = nn_idx[:, 1:]
    
    n_nodes = len(pcd)
    n_obs = 3
    n_edges = n_nodes * params['MIN_NN1']
    
    eu = np.repeat(np.arange(n_nodes), params['MIN_NN1'])
    ev = indices.ravel()
    
    y = pcd[:, :3] - np.mean(pcd[:, :3], axis=0)
    edge_weight = np.ones_like(eu)
    node_weight = np.ones(point_count)
    
    solution, components, in_component, energy_out, time_out = cut_pursuit(
        n_nodes=n_nodes,
        n_edges=n_edges,
        n_obs=n_obs,
        observation=y,
        eu=eu,
        ev=ev,
        edge_weight=edge_weight,
        node_weight=node_weight,
        lambda_=params['REG_STRENGTH1'],  # 使用优化后的正则化强度
        verbose=True
    )
    return in_component


def create_node_edges_optimized(points, k, max_distance=2.0):
    """创建节点边（优化版）"""
    _, centroids_idx, inverse_idx = np.unique(points[:, -1], return_index=True, return_inverse=True)
    _, v_group = npi.group_by(points[:, -1].astype(np.int32), np.arange(len(points[:, -1])))
    
    centroids = np.array([np.mean(points[idx, :3], 0) for idx in v_group])
    kdtree = cKDTree(centroids[:, :3])
    _, indices = kdtree.query(centroids[:, :3], k=k + 1)
    distance_matrix = np.zeros([len(centroids), len(centroids)]) - 1
    
    for i, v in enumerate(v_group):
        nn_idx = indices[i, 1:]
        tree = cKDTree(points[v, :3])
        distance_matrix[i, i] = 0
        for j, nv in enumerate(nn_idx):
            if distance_matrix[i, j] > 0:
                continue
            nn_dist = tree.query(points[v_group[nv], :3], k=1)
            distance_matrix[i, nv] = np.min(nn_dist)
    
    kdtree = cKDTree(points[:, :3])
    nn_D, nn_idx = kdtree.query(points[:, :3], k=k + 1)
    indices = nn_idx[:, 1:]
    
    eu = np.repeat(np.arange(len(points)), k)
    ev = indices.ravel()
    
    eu_node = inverse_idx[eu]
    ev_node = inverse_idx[ev]
    
    distance_pairs = np.transpose([eu, ev, distance_matrix[eu_node, ev_node]])
    distance_pairs = distance_pairs[distance_pairs[:, -1] < max_distance]
    distance_pairs = distance_pairs[distance_pairs[:, -1] > -1]
    
    return centroids, distance_pairs, centroids_idx, inverse_idx


def intermediate_segs_optimized(pcd):
    """优化后的中间分割"""
    pcd[:, :3] = pcd[:, :3] - np.mean(pcd[:, :3], axis=0)
    centroids, distance_pairs, centroids_idx, centroids_inverse_idx = create_node_edges_optimized(
        pcd[:, :4], k=params['MIN_NN2'], max_distance=2.0
    )
    point_count = len(pcd)
    
    n_nodes = point_count
    n_obs = 2
    n_edges = len(distance_pairs)
    
    edge_weight = 10. / ((distance_pairs[:, 2] + 0.01) / 0.01)
    node_weight = np.ones(n_nodes)
    
    solution, components, in_component, energy_out, time_out = cut_pursuit(
        n_nodes=n_nodes,
        n_edges=n_edges,
        n_obs=n_obs,
        observation=pcd[:, :2],
        eu=distance_pairs[:, 0],
        ev=distance_pairs[:, 1],
        edge_weight=edge_weight,
        node_weight=node_weight,
        lambda_=params['REG_STRENGTH2'],  # 使用优化后的正则化强度
        verbose=True
    )
    return in_component


def run_treeiso_optimized(points, verbose=True):
    """运行优化后的 Treeiso"""
    if not TREEISO_AVAILABLE:
        raise ImportError("Treeiso 未正确安装")
    
    pcd = points - np.mean(points, axis=0)
    
    if verbose:
        print("\n[阶段 1/3] 3D 初始分割 (优化后)...")
        print(f"  正则化强度: {params['REG_STRENGTH1']}")
    
    dec_idx_uidx, dec_inverse_idx = decimate_pcd(pcd, params['DECIMATE_RES'])
    pcd_dec = pcd[dec_idx_uidx]
    
    if verbose:
        print(f"  降采样: {len(pcd):,} -> {len(pcd_dec):,} 点")
    
    init_labels = init_segs_optimized(pcd_dec)
    
    if verbose:
        n_init = len(np.unique(init_labels))
        print(f"  初始分割: {n_init} 个片段")
    
    if verbose:
        print(f"\n[阶段 2/3] 2D 中间分割 (优化后)...")
        print(f"  正则化强度: {params['REG_STRENGTH2']}")
    
    pcd_with_init = np.concatenate([
        pcd_dec,
        init_labels[:, np.newaxis]
    ], axis=-1)
    
    intermediate_labels = intermediate_segs_optimized(pcd_with_init)
    
    if verbose:
        n_inter = len(np.unique(intermediate_labels))
        print(f"  中间分割: {n_inter} 个片段")
    
    # 跳过最终合并阶段（对 UAV 数据来说中间分割已经足够）
    if verbose:
        print(f"\n[阶段 3/3] 跳过最终合并（UAV 优化）...")
        print(f"  直接使用中间分割结果")
    
    final_labels_full = intermediate_labels[dec_inverse_idx]
    n_trees = len(np.unique(final_labels_full))
    
    if verbose:
        print(f"  最终结果: {n_trees} 棵树")
    
    return final_labels_full.astype(np.int32)


def save_results(pcd, points, labels, output_dir):
    """保存结果"""
    import pandas as pd
    os.makedirs(output_dir, exist_ok=True)
    
    unique_labels = sorted(set(labels))
    n_trees = len(unique_labels)
    
    print(f"\n保存结果到: {output_dir}")
    
    np.random.seed(42)
    colors = np.random.rand(max(labels) + 2, 3)
    
    point_colors = np.zeros((len(labels), 3))
    for i, label in enumerate(labels):
        point_colors[i] = colors[label]
    
    pcd_colored = o3d.geometry.PointCloud()
    pcd_colored.points = o3d.utility.Vector3dVector(points)
    pcd_colored.colors = o3d.utility.Vector3dVector(point_colors)
    
    output_ply = os.path.join(output_dir, 'treeiso_uav_optimized.ply')
    o3d.io.write_point_cloud(output_ply, pcd_colored)
    print(f"  已保存: treeiso_uav_optimized.ply")
    
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
    csv_path = os.path.join(output_dir, 'treeiso_uav_optimized_summary.csv')
    df.to_csv(csv_path, index=False)
    print(f"  已保存: treeiso_uav_optimized_summary.csv")
    
    return df


def visualize(points, labels):
    """可视化"""
    np.random.seed(42)
    colors = np.random.rand(max(labels) + 2, 3)
    
    point_colors = np.zeros((len(labels), 3))
    for i, label in enumerate(labels):
        point_colors[i] = colors[label]
    
    pcd_vis = o3d.geometry.PointCloud()
    pcd_vis.points = o3d.utility.Vector3dVector(points)
    pcd_vis.colors = o3d.utility.Vector3dVector(point_colors)
    
    print("\n打开 3D 可视化窗口...")
    o3d.visualization.draw_geometries(
        [pcd_vis],
        window_name="TreeISO UAV Optimized Result",
        width=1200,
        height=800
    )


# ============================================================
# 主程序
# ============================================================

if __name__ == "__main__":
    PROJECT_ROOT = "/Users/zyc/Downloads/Niigata_Research_Prep"
    INPUT_FILE = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/Off-Ground_Good-5m.ply"
    OUTPUT_DIR = f"{PROJECT_ROOT}/01_Processed/San Juan Fault/isolated_trees_treeiso_uav"
    
    # 1. 预处理（激进去噪）
    pcd, points = load_and_preprocess(
        INPUT_FILE,
        apply_sor=True,
        sor_neighbors=30,  # 更大的邻域
        sor_std_ratio=1.5  # 更严格的阈值
    )
    
    # 2. 运行优化后的 Treeiso
    try:
        labels = run_treeiso_optimized(points, verbose=True)
        
        # 3. 保存结果
        df = save_results(pcd, points, labels, OUTPUT_DIR)
        
        print("\n" + "=" * 60)
        print(f"完成！共检测到 {len(df)} 棵树")
        print("=" * 60)
        
        print("\n前 10 棵树信息:")
        print(df.head(10))
        
        # 4. 可视化
        visualize(points, labels)
        
    except Exception as e:
        print(f"\n错误: {e}")
        import traceback
        traceback.print_exc()
