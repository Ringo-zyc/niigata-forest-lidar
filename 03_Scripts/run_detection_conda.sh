#!/bin/bash
# 使用 conda 环境运行圆柱体检测

PROJECT_DIR="/Users/zyc/Downloads/Niigata_Research_Prep"
ENV_NAME="tree_detection"

cd "$PROJECT_DIR"

# 初始化 conda（如果需要）
eval "$(conda shell.bash hook)"

# 检查环境是否存在
if ! conda env list | grep -q "^$ENV_NAME "; then
    echo "正在创建 conda 环境 ($ENV_NAME) 使用 Python 3.11..."
    conda create -y -n "$ENV_NAME" python=3.11
fi

# 激活环境
echo "激活 conda 环境..."
conda activate "$ENV_NAME"

# 安装依赖
echo "正在安装依赖..."
pip install -q open3d numpy scikit-learn scipy 2>/dev/null || echo "依赖已安装"

# 确保 PLY 文件存在
if [ ! -f "$PROJECT_DIR/01_Processed/tree.ply" ]; then
    echo "正在转换点云格式..."
    /Applications/CloudCompare.app/Contents/MacOS/CloudCompare \
        -SILENT \
        -O "$PROJECT_DIR/01_Processed/tree.bin" \
        -C_EXPORT_FMT PLY \
        -SAVE_CLOUDS FILE "$PROJECT_DIR/01_Processed/tree.ply"
fi

# 运行检测脚本
echo -e "\n开始检测圆柱体...\n"
python "$PROJECT_DIR/03_Scripts/detect_cylinders_v2.py"

# 停用环境
conda deactivate

echo -e "\n完成！"
