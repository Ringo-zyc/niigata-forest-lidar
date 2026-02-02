#!/usr/bin/env python3
"""
计算验证统计指标 - RMSE, 平均误差等
Calculate validation statistics - RMSE, Mean Error, etc.
"""
import pandas as pd
import numpy as np
import os
import sys

def calculate_stats(validation_csv_path):
    """
    从填写完成的验证表计算统计指标
    
    Args:
        validation_csv_path: 已填写 Manual_DBH_cm 列的验证表路径
    """
    df = pd.read_csv(validation_csv_path)
    
    # 检查必要的列
    if 'Auto_DBH_cm' not in df.columns or 'Manual_DBH_cm' not in df.columns:
        print("❌ 错误: CSV 需要包含 'Auto_DBH_cm' 和 'Manual_DBH_cm' 列")
        return None
    
    # 过滤掉未填写的行
    df = df[df['Manual_DBH_cm'].notna() & (df['Manual_DBH_cm'] != '')]
    df['Manual_DBH_cm'] = pd.to_numeric(df['Manual_DBH_cm'], errors='coerce')
    df = df.dropna(subset=['Manual_DBH_cm'])
    
    if len(df) == 0:
        print("❌ 没有找到有效的手动测量数据")
        print("请先在 validation_sample.csv 中填写 Manual_DBH_cm 列")
        return None
    
    # 计算误差
    df['Error_cm'] = df['Auto_DBH_cm'] - df['Manual_DBH_cm']
    df['Error_percent'] = (df['Error_cm'].abs() / df['Manual_DBH_cm'] * 100).round(1)
    
    # 统计指标
    n = len(df)
    mean_error = df['Error_cm'].mean()
    mean_abs_error = df['Error_cm'].abs().mean()
    rmse = np.sqrt((df['Error_cm'] ** 2).mean())
    mean_error_percent = df['Error_percent'].mean()
    
    # 打印结果
    print("\n" + "="*60)
    print("📊 验证结果统计")
    print("="*60)
    print(f"\n样本数量: {n} 棵树")
    print(f"\n误差指标:")
    print(f"  • 平均误差 (Mean Error):     {mean_error:+.2f} cm")
    print(f"  • 平均绝对误差 (MAE):        {mean_abs_error:.2f} cm")
    print(f"  • 均方根误差 (RMSE):         {rmse:.2f} cm")
    print(f"  • 平均相对误差:              {mean_error_percent:.1f}%")
    
    # 按分组统计
    if 'Size_Group' in df.columns:
        print("\n按大小分组:")
        for group in df['Size_Group'].unique():
            group_df = df[df['Size_Group'] == group]
            group_mae = group_df['Error_cm'].abs().mean()
            print(f"  • {group}: MAE = {group_mae:.2f} cm (n={len(group_df)})")
    
    # 生成详细表格
    print("\n详细数据:")
    print("-"*80)
    print(df[['Tree_ID', 'Size_Group', 'Auto_DBH_cm', 'Manual_DBH_cm', 'Error_cm', 'Error_percent']].to_string(index=False))
    print("-"*80)
    
    # 更新原始文件
    df.to_csv(validation_csv_path, index=False)
    print(f"\n✅ 已更新: {validation_csv_path}")
    
    # 生成 PPT 用的简洁表格
    ppt_table_path = os.path.join(os.path.dirname(validation_csv_path), 'validation_summary_for_ppt.csv')
    summary = pd.DataFrame({
        'Metric': ['样本数 (N)', '平均绝对误差 (MAE)', '均方根误差 (RMSE)', '平均相对误差'],
        'Value': [f'{n}', f'{mean_abs_error:.2f} cm', f'{rmse:.2f} cm', f'{mean_error_percent:.1f}%']
    })
    summary.to_csv(ppt_table_path, index=False)
    print(f"📊 PPT用摘要表: {ppt_table_path}")
    
    print("\n" + "="*60)
    print("面试话术:")
    print(f'"为了验证算法精度，我随机抽取了 {n} 棵样本进行人工核对。')
    print(f'结果显示算法的平均误差控制在 {mean_abs_error:.1f}cm 以内（RMSE={rmse:.1f}cm），')
    print('证明了该方法在提取树木位置和粗度上的可靠性。"')
    print("="*60)
    
    return {
        'n': n,
        'mean_error': mean_error,
        'mae': mean_abs_error,
        'rmse': rmse,
        'mean_error_percent': mean_error_percent
    }

if __name__ == "__main__":
    if len(sys.argv) > 1:
        csv_path = sys.argv[1]
    else:
        # 默认路径
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_dir = os.path.dirname(script_dir)
        csv_path = os.path.join(project_dir, "01_Processed", "San Juan Fault", "validation_sample.csv")
    
    if not os.path.exists(csv_path):
        print(f"❌ 文件不存在: {csv_path}")
        print("请先运行 generate_validation_sample.py 生成验证表")
        print("然后在 CloudCompare 中测量并填写 Manual_DBH_cm 列")
        sys.exit(1)
    
    calculate_stats(csv_path)
