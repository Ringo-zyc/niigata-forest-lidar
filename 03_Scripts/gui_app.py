import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import open3d as o3d
import numpy as np
import csv
import os
import threading
import sys

# Import shared logic from local module
try:
    from tree_utils import detect_cylinders
except ImportError:
    # Handle case if run from outside directory without PYTHONPATH
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from tree_utils import detect_cylinders

try:
    from visualize_forest import run_visualization, run_interactive_visualization
except ImportError:
    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    from visualize_forest import run_visualization, run_interactive_visualization


# ================= GUI 类 =================

class TreeDetectionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("LiDAR 树木检测工具 v2.1")
        self.root.geometry("850x1000")
        
        # Style configuration
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('TNotebook.Tab', padding=[20, 10], font=('Arial', 12, 'bold'))
        
        # Create Notebook (Tabs)
        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Create Frames for Tabs
        self.tab_detect = tk.Frame(self.notebook)
        self.tab_visualize = tk.Frame(self.notebook)
        
        self.notebook.add(self.tab_detect, text='🌲 树木检测')
        self.notebook.add(self.tab_visualize, text='🎨 结果可视化')
        
        # Initialize Tabs
        self.setup_detection_tab()
        self.setup_visualization_tab()
        
        # Common Log Area (Bottom)
        tk.Label(root, text="运行日志:", font=("Arial", 10, "bold")).pack(anchor="w", padx=10, pady=(0, 0))
        self.log_area = scrolledtext.ScrolledText(root, height=12, font=("Courier", 9))
        self.log_area.pack(fill="both", expand=True, padx=10, pady=5)

    def log(self, msg):
        """添加日志消息"""
        self.log_area.insert(tk.END, msg + "\n")
        self.log_area.see(tk.END)
        self.root.update()

    # ================= 标签页 1: 树木检测 =================
    def setup_detection_tab(self):
        frame = self.tab_detect
        
        # Variables
        self.det_input_path = tk.StringVar()
        self.det_output_path = tk.StringVar()
        self.entries = {}
        
        # 1. File Selection
        frame_file = tk.LabelFrame(frame, text="第1步：选择输入和输出路径", padx=10, pady=10)
        frame_file.pack(fill="x", padx=10, pady=5)
        
        # Input
        tk.Label(frame_file, text="输入文件 (PLY/LAZ):").pack(anchor="w")
        f_input = tk.Frame(frame_file)
        f_input.pack(fill="x", pady=2)
        tk.Entry(f_input, textvariable=self.det_input_path, width=50).pack(side="left", fill="x", expand=True)
        tk.Button(f_input, text="浏览...", command=self.det_browse_input).pack(side="left", padx=5)
        
        # Output
        tk.Label(frame_file, text="输出CSV文件:").pack(anchor="w")
        f_output = tk.Frame(frame_file)
        f_output.pack(fill="x", pady=2)
        tk.Entry(f_output, textvariable=self.det_output_path, width=50).pack(side="left", fill="x", expand=True)
        tk.Button(f_output, text="浏览...", command=self.det_browse_output).pack(side="left", padx=5)
        
        # 2. Parameters
        frame_param1 = tk.LabelFrame(frame, text="第2步：RANSAC 参数调整", padx=10, pady=10)
        frame_param1.pack(fill="x", padx=10, pady=5)
        
        params_col1 = [
            ("Distance Threshold (m)", "0.06", "点到圆柱轴的最大距离"),
            ("Min Points", "50", "一个圆柱体最少点数"),
        ]
        params_col2 = [
            ("Min Radius (m)", "0.03", "圆柱最小半径"),
            ("Max Radius (m)", "0.8", "圆柱最大半径"),
        ]
        
        for i, (lbl, default, tooltip) in enumerate(params_col1):
            tk.Label(frame_param1, text=lbl, fg="blue").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            e = tk.Entry(frame_param1, width=12)
            e.insert(0, default)
            e.grid(row=i, column=1, sticky="w", padx=5)
            tk.Label(frame_param1, text=tooltip, font=("Arial", 8), fg="gray").grid(row=i, column=2, sticky="w", padx=5)
            self.entries[lbl] = e
            
        for i, (lbl, default, tooltip) in enumerate(params_col2):
            tk.Label(frame_param1, text=lbl, fg="blue").grid(row=i, column=3, sticky="e", padx=5, pady=5)
            e = tk.Entry(frame_param1, width=12)
            e.insert(0, default)
            e.grid(row=i, column=4, sticky="w", padx=5)
            tk.Label(frame_param1, text=tooltip, font=("Arial", 8), fg="gray").grid(row=i, column=5, sticky="w", padx=5)
            self.entries[lbl] = e
            
        # 3. Advanced Parameters
        frame_param2 = tk.LabelFrame(frame, text="第3步：高级参数", padx=10, pady=10)
        frame_param2.pack(fill="x", padx=10, pady=5)
        
        params_adv = [
            ("Min Height (m)", "1.0", "圆柱最小高度"),
            ("Max Iterations", "100", "最多检测多少个圆柱体"),
        ]
        
        for i, (lbl, default, tooltip) in enumerate(params_adv):
            tk.Label(frame_param2, text=lbl, fg="blue").grid(row=i, column=0, sticky="e", padx=5, pady=5)
            e = tk.Entry(frame_param2, width=12)
            e.insert(0, default)
            e.grid(row=i, column=1, sticky="w", padx=5)
            tk.Label(frame_param2, text=tooltip, font=("Arial", 8), fg="gray").grid(row=i, column=2, sticky="w", padx=5)
            self.entries[lbl] = e
            
        # Auto Visualize Checkbox
        self.auto_vis_var = tk.BooleanVar(value=True) # Default to True for better UX
        tk.Checkbutton(frame, text="检测完成后自动切换到可视化", variable=self.auto_vis_var).pack(anchor="w", padx=20)
        
        # Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", padx=10, pady=10)
        
        self.btn_run_det = tk.Button(btn_frame, text="▶ 开始检测", command=self.start_detection_thread, 
                                  bg="green", fg="white", font=("Arial", 12, "bold"), padx=20, pady=10)
        self.btn_run_det.pack(side="left", padx=5)
        
        tk.Button(btn_frame, text="重置参数", command=self.reset_params, padx=15, pady=10).pack(side="left", padx=5)
        
    def det_browse_input(self):
        f = filedialog.askopenfilename(filetypes=[("Point Cloud Files", "*.ply *.laz"), ("All Files", "*.*")])
        if f: 
            self.det_input_path.set(f)
            # Auto set output path
            dir_name = os.path.dirname(f)
            base_name = os.path.splitext(os.path.basename(f))[0]
            self.det_output_path.set(os.path.join(dir_name, f"{base_name}_cylinders.csv"))
            # Auto set Visualization tab inputs too
            self.vis_input_pcd.set(f)
            
    def det_browse_output(self):
        f = filedialog.asksaveasfilename(filetypes=[("CSV Files", "*.csv")], defaultextension=".csv")
        if f: self.det_output_path.set(f)
        
    def reset_params(self):
        defaults = {
            "Distance Threshold (m)": "0.06",
            "Min Points": "50",
            "Min Radius (m)": "0.03",
            "Max Radius (m)": "0.8",
            "Min Height (m)": "1.0",
            "Max Iterations": "100",
        }
        for key, val in defaults.items():
            if key in self.entries:
                self.entries[key].delete(0, tk.END)
                self.entries[key].insert(0, val)
        self.log("✅ 参数已重置")

    def start_detection_thread(self):
        threading.Thread(target=self.run_detection_process, daemon=True).start()

    def run_detection_process(self):
        inp = self.det_input_path.get()
        out = self.det_output_path.get()
        
        if not inp or not os.path.exists(inp):
            self.log("❌ 错误：无效的输入文件")
            return
        if not out:
            self.log("❌ 错误：请指定输出路径")
            return
            
        self.btn_run_det.config(state="disabled")
        self.log("\n" + "="*50)
        self.log("🚀 开始检测...")
        
        try:
             # Get params
            dist_thresh = float(self.entries["Distance Threshold (m)"].get())
            min_pts = int(self.entries["Min Points"].get())
            min_r = float(self.entries["Min Radius (m)"].get())
            max_r = float(self.entries["Max Radius (m)"].get())
            min_h = float(self.entries["Min Height (m)"].get())
            max_iter = int(self.entries["Max Iterations"].get())
            
            pcd = o3d.io.read_point_cloud(inp)
            points = np.asarray(pcd.points)
            self.log(f"✅ 加载点云: {len(points)} 点")
            
            cylinders = detect_cylinders(
                points, min_pts, dist_thresh, min_r, max_r, min_h, max_iter, self.log
            )
            
            if cylinders:
                cylinders.sort(key=lambda x: x['diameter'], reverse=True)
                os.makedirs(os.path.dirname(out), exist_ok=True)
                with open(out, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(['Radius (m)', 'Diameter_DBH (cm)', 'Height (m)', 'Num_Points', 'X', 'Y', 'Z'])
                    for cyl in cylinders:
                        writer.writerow([f"{cyl['radius']:.4f}", f"{cyl['diameter']:.2f}", 
                                       f"{cyl['height']:.2f}", cyl['num_points'],
                                       f"{cyl['center'][0]:.4f}", f"{cyl['center'][1]:.4f}", f"{cyl['center'][2]:.4f}"])
                
                self.log(f"✅ 成功检测 {len(cylinders)} 棵树")
                self.log(f"💾 结果已保存: {out}")
                
                 # Update Visualization Tab inputs
                self.vis_input_pcd.set(inp)
                self.vis_output_dir.set(os.path.dirname(out))
                
                if self.auto_vis_var.get():
                     self.log("🔄 自动切换到可视化模式...")
                     self.root.after(100, lambda: self.notebook.select(self.tab_visualize))
                     # We need to pass the exact out_csv to the visualization function
                     # But start_visualization_thread reads from UI variables.
                     # UI variables are already set above:
                     # self.vis_output_dir.set(os.path.dirname(out))
                     # However, setup_visualization_tab logic searches for CSV in directory.
                     # Since we just wrote to 'out', it should find it if names match logic.
                     # 'out' comes from det_output_path.
                     
                     self.root.after(200, self.start_visualization_thread)
            else:
                self.log("⚠️ 未检测到树木")
                
        except Exception as e:
            self.log(f"❌ 错误: {e}")
            import traceback
            self.log(traceback.format_exc())
            
        finally:
            self.btn_run_det.config(state="normal")
            self.log("\n检测流程结束")

    # ================= 标签页 2: 结果可视化 =================
    def setup_visualization_tab(self):
        frame = self.tab_visualize
        
        self.vis_input_pcd = tk.StringVar()
        self.vis_output_dir = tk.StringVar()
        
        # 1. Inputs
        grp = tk.LabelFrame(frame, text="可视化设置", padx=10, pady=10)
        grp.pack(fill="x", padx=10, pady=10)
        
        # PCD File
        tk.Label(grp, text="点云文件 (PLY/LAZ):").pack(anchor="w")
        f1 = tk.Frame(grp)
        f1.pack(fill="x", pady=2)
        tk.Entry(f1, textvariable=self.vis_input_pcd, width=50).pack(side="left", fill="x", expand=True)
        tk.Button(f1, text="浏览...", command=self.vis_browse_pcd).pack(side="left", padx=5)
        
        # Output Dir
        tk.Label(grp, text="结果保存目录 (包含CSV的文件夹):").pack(anchor="w", pady=(10,0))
        f2 = tk.Frame(grp)
        f2.pack(fill="x", pady=2)
        tk.Entry(f2, textvariable=self.vis_output_dir, width=50).pack(side="left", fill="x", expand=True)
        tk.Button(f2, text="浏览...", command=self.vis_browse_dir).pack(side="left", padx=5)
        
        # Info
        tk.Label(grp, text="注意: 将会在该目录下寻找 tree_positions.csv 或 tree_positions_vis.csv", 
                 fg="gray", font=("Arial", 9)).pack(anchor="w", pady=5)
        
        # 2. Action
        
        # 2. Action Buttons
        btn_frame = tk.Frame(frame)
        btn_frame.pack(fill="x", pady=10)
        
        self.btn_run_vis = tk.Button(btn_frame, text="🎨 生成可视化图表", command=self.start_visualization_thread,
                                     bg="#4a90e2", fg="white", font=("Arial", 12, "bold"), padx=15, pady=8)
        self.btn_run_vis.pack(side="left", padx=20)
        
        self.btn_open3d = tk.Button(btn_frame, text="👀 交互式 3D 预览（Open3D）", command=self.start_interactive_vis,
                                   bg="#f39c12", fg="white", font=("Arial", 12, "bold"), padx=15, pady=8)
        self.btn_open3d.pack(side="left", padx=20)
        self.btn_open3d.config(state="disabled") # Disabled until processing done or CSV selected
        
        # 3. Image Preview Area (Simplified)
        preview_frame = tk.LabelFrame(frame, text="图表预览", padx=5, pady=5)
        preview_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # Labels to hold images
        self.lbl_img1 = tk.Label(preview_frame, text="运行后图表将显示在这里")
        self.lbl_img1.pack(pady=5)
        self.lbl_img2 = tk.Label(preview_frame)
        self.lbl_img2.pack(pady=5)
        
    def vis_browse_pcd(self):
        f = filedialog.askopenfilename(filetypes=[("Point Cloud Files", "*.ply *.laz"), ("All Files", "*.*")])
        if f: self.vis_input_pcd.set(f)
        
    def vis_browse_dir(self):
        d = filedialog.askdirectory()
        if d: 
            self.vis_output_dir.set(d)
            self.btn_open3d.config(state="normal")
        
    def start_visualization_thread(self):
        threading.Thread(target=self.run_visualization_process, daemon=True).start()
        
    def start_interactive_vis(self):
        threading.Thread(target=self.run_interactive_process, daemon=True).start()
        
    def run_interactive_process(self):
        """Runs Open3D visualization"""
        pcd_path = self.vis_input_pcd.get()
        results_dir = self.vis_output_dir.get()
        
        if not pcd_path or not os.path.exists(pcd_path):
             messagebox.showerror("Error", "无效的点云文件")
             return
             
        # Find CSV
        csv_path = None
        possible_csv = os.path.join(results_dir, "tree_positions.csv")
        if os.path.exists(possible_csv):
            csv_path = possible_csv
        else:
             import glob
             candidates = glob.glob(os.path.join(results_dir, "*cylinders*.csv"))
             if candidates: csv_path = candidates[0]
             
        if not csv_path:
             messagebox.showerror("Error", "未找到结果CSV文件")
             return
             
        self.log(f"🚀 启动 Open3D: {pcd_path} + {csv_path}")
        try:
            run_interactive_visualization(pcd_path, csv_path)
        except Exception as e:
            self.log(f"❌ 3D 预览错误: {e}")

    def run_visualization_process(self):
        pcd_path = self.vis_input_pcd.get()
        results_dir = self.vis_output_dir.get()
        
        if not pcd_path or not os.path.exists(pcd_path):
            self.log("❌ 错误: 无效的点云文件路径")
            return
        if not results_dir:
            self.log("❌ 错误: 请指定结果目录")
            return
            
        self.btn_run_vis.config(state="disabled")
        self.log("\n" + "="*50)
        self.log("🎨 开始可视化...")
        
        # Try to find CSV file
        csv_path = None
        # Option 1: User explicitly generated/selected output directory implies we look for standard name
        possible_csv = os.path.join(results_dir, "tree_positions.csv")
        if os.path.exists(possible_csv):
            csv_path = possible_csv
        else:
             # Check if there's any csv with 'cylinders' in name in that dir
             import glob
             candidates = glob.glob(os.path.join(results_dir, "*cylinders*.csv"))
             if candidates:
                 csv_path = candidates[0]
                 self.log(f"📋 自动找到 CSV: {os.path.basename(csv_path)}")

        try:
            outputs = run_visualization(pcd_path, results_dir=results_dir, csv_path=csv_path)
            self.log("✅ 可视化完成!")
            for path in outputs:
                self.log(f"🖼️ {path}")
            
            # --- Update GUI Preview ---
            self.update_previews(outputs)
            self.btn_open3d.config(state="normal") # Enable 3D button
                
        except Exception as e:
            self.log(f"❌ 可视化错误: {e}")
            import traceback
            self.log(traceback.format_exc())
        finally:
            self.btn_run_vis.config(state="normal")
            self.log("可视化流程结束")
            
    def update_previews(self, image_paths):
        """Show preview info and open images externally"""
        try:
            def show_info():
                # Just update labels with path info instead of embedding images
                if len(image_paths) > 0 and os.path.exists(image_paths[0]):
                    self.lbl_img1.config(text=f"✅ 已生成: {os.path.basename(image_paths[0])}")
                if len(image_paths) > 1 and os.path.exists(image_paths[1]):
                    self.lbl_img2.config(text=f"✅ 已生成: {os.path.basename(image_paths[1])}")
                
                # Open the folder containing the images
                if image_paths:
                    folder = os.path.dirname(image_paths[0])
                    if sys.platform == 'darwin':
                        os.system(f'open "{folder}"')
                    elif sys.platform == 'win32':
                        os.startfile(folder)
            
            self.root.after(100, show_info)
            
        except Exception as e:
            self.log(f"⚠️ 预览错误: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    TreeDetectionApp(root)
    root.mainloop()