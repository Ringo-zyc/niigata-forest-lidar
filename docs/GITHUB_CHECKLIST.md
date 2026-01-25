# GitHub 发布检查表

1. **初始化仓库**
   ```bash
   cd /Users/zyc/Downloads/Niigata_Research_Prep
   git init
   git add .
   git commit -m "Initial commit - Niigata forest analysis"
   ```

2. **命名建议**
   - 仓库名：`niigata-forest-lidar` 或 `grad-forest-pipeline`
   - 默认分支：`main`
   - `README.md` 保留中文版，可新增 `README_en.md`

3. **上传前自检**
   - [ ] 运行 `./run_tree_detection.sh`、`./run_forest_analysis.sh`
   - [ ] `04_Results/` 含最新图表 & CSV
   - [ ] `docs/PROJECT_STRUCTURE.md`、`docs/GITHUB_CHECKLIST.md` 存在
   - [ ] 无敏感数据（若有，可放入 `00_Raw_Data/.gitignore`）

4. **推送**
   ```bash
   git remote add origin git@github.com:<username>/<repo>.git
   git push -u origin main
   ```

5. **发布建议**
   - 在 GitHub Releases 中上传关键图 (`forest_pointcloud_cylinders.png`)
   - README 中添加 “成果展示” 小节，并嵌入 `docs/PROJECT_STRUCTURE.md` 链接
   - 使用仓库标签：`LiDAR`, `Forest`, `RANSAC`, `Python`

> 复制此检查表到其它项目即可复用，确保研究内容一致的目录和命名规范。
