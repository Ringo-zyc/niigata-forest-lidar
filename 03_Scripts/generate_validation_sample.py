#!/usr/bin/env python3
"""
生成分层抽样验证表 - 用于在 CloudCompare 中验证检测结果
Generates a stratified sample for validation in CloudCompare
"""
import pandas as pd
import os
import sys

def generate_validation_sample(csv_path, output_path=None, n_per_group=3):
    """
    按 DBH 大小分层抽样，生成验证用的样本表
    
    Args:
        csv_path: 检测结果 CSV 文件路径
        output_path: 输出文件路径（默认为同目录下的 validation_sample.csv）
        n_per_group: 每组抽取的样本数（默认3）
    """
    # 读取检测结果
    df = pd.read_csv(csv_path)
    
    # 标准化列名
    col_map = {
        'Radius (m)': 'radius_m',
        'Diameter_DBH (cm)': 'dbh_cm', 
        'Height (m)': 'height_m',
        'Num_Points': 'num_points',
        'X': 'x', 'Y': 'y', 'Z': 'z'
    }
    df.rename(columns=col_map, inplace=True)
    
    # 确保有必要的列
    if 'dbh_cm' not in df.columns:
        if 'radius_m' in df.columns:
            df['dbh_cm'] = df['radius_m'] * 200
        else:
            print("❌ 错误: CSV 中没有直径或半径数据")
            return None
    
    # 按 DBH 分组
    # 小树: < 30cm, 中树: 30-40cm, 大树: > 40cm
    df['size_group'] = pd.cut(
        df['dbh_cm'], 
        bins=[0, 30, 40, 999], 
        labels=['Small (<30cm)', 'Medium (30-40cm)', 'Large (>40cm)']
    )
    
    # 分层抽样
    samples = []
    for group_name in ['Small (<30cm)', 'Medium (30-40cm)', 'Large (>40cm)']:
        group_df = df[df['size_group'] == group_name]
        if len(group_df) > 0:
            n = min(n_per_group, len(group_df))
            sample = group_df.sample(n=n, random_state=42)
            samples.append(sample)
    
    if not samples:
        print("❌ 没有找到足够的样本")
        return None
        
    validation_df = pd.concat(samples)
    
    # 创建验证表格式
    result = pd.DataFrame({
        'Tree_ID': range(1, len(validation_df) + 1),
        'Size_Group': validation_df['size_group'].values,
        'X_coord': validation_df['x'].values if 'x' in validation_df.columns else ['N/A'] * len(validation_df),
        'Y_coord': validation_df['y'].values if 'y' in validation_df.columns else ['N/A'] * len(validation_df),
        'Auto_DBH_cm': validation_df['dbh_cm'].values.round(1),
        'Manual_DBH_cm': [''] * len(validation_df),  # 留空待人工填写
        'Error_cm': [''] * len(validation_df),       # 留空待计算
        'Error_percent': [''] * len(validation_df),  # 留空待计算
        'Notes': [''] * len(validation_df)           # 备注
    })
    
    # 输出路径
    if output_path is None:
        output_path = os.path.join(os.path.dirname(csv_path), 'validation_sample.csv')
    
    result.to_csv(output_path, index=False)
    
    # 打印统计信息
    print(f"\n📊 验证样本生成完成!")
    print(f"📁 保存位置: {output_path}")
    print(f"\n样本统计:")
    print(result.groupby('Size_Group').size().to_string())
    print(f"\n总计: {len(result)} 棵树")
    print("\n" + "="*60)
    print("下一步:")
    print("1. 打开 CloudCompare，加载你的点云文件")
    print("2. 根据上表中的 X_coord, Y_coord 定位每棵树")
    print("3. 使用测量工具量取树干直径")
    print("4. 将结果填入 Manual_DBH_cm 列")
    print("5. 运行 calculate_validation_stats.py 计算误差统计")
    print("="*60)
    
    return result

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # 默认路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        csv_path = os.path.join(project_dir, "01_Processed", "San Juan Fault", "Off-Ground_Good-5m_cylinders.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ 文件不存在: {csv_path}")
        print("用法: python generate_validation_sample.py <csv_path>")
        sys.exit(1)
    
    generate_validation_sample(csv_path)
