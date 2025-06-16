"""
GUI界面模块
"""
import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, filedialog
import threading
import time
from config import ConfigManager
from logger import Logger
from website_handler import WebsiteHandler

class AutoSystemGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("自动化警信人员预警系统")
        self.root.geometry("900x800")
        self.root.minsize(800, 650)  # 设置最小窗口大小
        
        # 初始化组件
        self.config = ConfigManager()
        self.logger = Logger(self.config.get("log_level", "INFO"))
        self.website_handler = WebsiteHandler(self.config, self.logger)
        
        # 状态变量
        self.is_running = False
        self.cycle_count = 0
        
        self.setup_ui()
        self.load_config_to_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="自动化警信人员预警系统", 
                               font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 配置区域
        config_frame = ttk.LabelFrame(main_frame, text="系统配置", padding="10")
        config_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 配置grid列权重，确保输入框能够正常显示
        config_frame.columnconfigure(1, weight=1)
        
        # 重点人网站配置
        ttk.Label(config_frame, text="重点人网站账号1用户名:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.zdr_username_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.zdr_username_var, width=30).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(config_frame, text="重点人网站账号1密码:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.zdr_password_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.zdr_password_var, show="*", width=30).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(config_frame, text="重点人网站账号2用户名:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.zdr_username2_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.zdr_username2_var, width=30).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(config_frame, text="重点人网站账号2密码:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.zdr_password2_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.zdr_password2_var, show="*", width=30).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 警信网站配置
        ttk.Label(config_frame, text="警信网站身份证号:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.jx_id_card_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.jx_id_card_var, width=30).grid(row=4, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(config_frame, text="警信网站密码:").grid(row=5, column=0, sticky=tk.W, pady=2)
        self.jx_password_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.jx_password_var, show="*", width=30).grid(row=5, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(config_frame, text="警信群聊名称:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.jx_group_name_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.jx_group_name_var, width=30).grid(row=6, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 运行模式配置
        ttk.Label(config_frame, text="运行模式:").grid(row=7, column=0, sticky=tk.W, pady=2)
        self.run_mode_var = tk.StringVar()
        mode_combo = ttk.Combobox(config_frame, textvariable=self.run_mode_var, 
                                 values=["新浏览器", "连接已有浏览器", "无头模式"],
                                 state="readonly", width=27)
        mode_combo.grid(row=7, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 循环间隔配置
        ttk.Label(config_frame, text="循环间隔(分钟):").grid(row=8, column=0, sticky=tk.W, pady=2)
        self.cycle_minutes_var = tk.StringVar()
        ttk.Entry(config_frame, textvariable=self.cycle_minutes_var, width=30).grid(row=8, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 按钮区域
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=10)
        
        ttk.Button(button_frame, text="保存配置", command=self.save_config).pack(side=tk.LEFT, padx=(0, 10))
        
        self.start_button = ttk.Button(button_frame, text="开始运行", command=self.start_system)
        self.start_button.pack(side=tk.LEFT, padx=(0, 10))
        
        self.stop_button = ttk.Button(button_frame, text="停止运行", command=self.stop_system, state="disabled")
        self.stop_button.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(button_frame, text="立即执行一次", command=self.execute_once).pack(side=tk.LEFT)
        
        # 状态区域
        status_frame = ttk.LabelFrame(main_frame, text="运行状态", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 配置状态区域的列权重
        status_frame.columnconfigure(1, weight=1)
        
        ttk.Label(status_frame, text="当前状态:").grid(row=0, column=0, sticky=tk.W)
        self.status_var = tk.StringVar(value="未运行")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, foreground="red")
        self.status_label.grid(row=0, column=1, sticky=tk.W, padx=(10, 0))
        
        ttk.Label(status_frame, text="循环次数:").grid(row=0, column=2, sticky=tk.W, padx=(20, 0))
        self.cycle_count_var = tk.StringVar(value="0")
        ttk.Label(status_frame, textvariable=self.cycle_count_var).grid(row=0, column=3, sticky=tk.W, padx=(10, 0))
        
        # 日志区域
        log_frame = ttk.LabelFrame(main_frame, text="运行日志", padding="10")
        log_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, state="disabled")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        
        # 日志按钮
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.pack(pady=(5, 0))
        
        ttk.Button(log_button_frame, text="刷新日志", command=self.refresh_log).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_button_frame, text="清空日志", command=self.clear_log).pack(side=tk.LEFT)
        
        # 启动日志刷新
        self.refresh_log()
        self.root.after(5000, self.auto_refresh_log)
    
    def load_config_to_ui(self):
        """加载配置到界面"""
        self.zdr_username_var.set(self.config.get("zdr_username", ""))
        self.zdr_password_var.set(self.config.get("zdr_password", ""))
        self.zdr_username2_var.set(self.config.get("zdr_username2", ""))
        self.zdr_password2_var.set(self.config.get("zdr_password2", ""))
        self.jx_id_card_var.set(self.config.get("jx_id_card", ""))
        self.jx_password_var.set(self.config.get("jx_password", ""))
        self.jx_group_name_var.set(self.config.get("jx_group_name", "情指值班通知"))
        self.run_mode_var.set(self.config.get("run_mode", "新浏览器"))
        self.cycle_minutes_var.set(str(self.config.get("cycle_minutes", 30)))
    
    def save_config(self):
        """保存配置"""
        try:
            cycle_minutes = int(self.cycle_minutes_var.get())
            if cycle_minutes <= 0:
                messagebox.showerror("错误", "循环间隔必须是正整数")
                return
        except ValueError:
            messagebox.showerror("错误", "循环间隔必须是数字")
            return
        
        self.config.update({
            "zdr_username": self.zdr_username_var.get(),
            "zdr_password": self.zdr_password_var.get(),
            "zdr_username2": self.zdr_username2_var.get(),
            "zdr_password2": self.zdr_password2_var.get(),
            "jx_id_card": self.jx_id_card_var.get(),
            "jx_password": self.jx_password_var.get(),
            "jx_group_name": self.jx_group_name_var.get(),
            "run_mode": self.run_mode_var.get(),
            "cycle_minutes": cycle_minutes
        })
        
        if self.config.save_config():
            messagebox.showinfo("成功", "配置保存成功")
            self.logger.info("配置保存成功")
        else:
            messagebox.showerror("错误", "配置保存失败")
    
    def start_system(self):
        """开始系统运行"""
        if not self.validate_config():
            return
        
        self.is_running = True
        self.update_status("正在运行", "green")
        self.start_button.config(state="disabled")
        self.stop_button.config(state="normal")
        
        threading.Thread(target=self.worker_loop, daemon=True).start()
        self.logger.info("系统开始运行")
    
    def stop_system(self):
        """停止系统运行"""
        self.is_running = False
        self.update_status("已停止", "red")
        self.start_button.config(state="normal")
        self.stop_button.config(state="disabled")
        
        if self.website_handler:
            self.website_handler.close_browser()
        
        self.logger.info("系统已停止")
    
    def execute_once(self):
        """立即执行一次"""
        if not self.validate_config():
            return
        threading.Thread(target=self.execute_cycle, daemon=True).start()
    
    def validate_config(self):
        """验证配置"""
        if not self.zdr_username_var.get():
            messagebox.showerror("错误", "请输入重点人网站账号1用户名")
            return False
        if not self.zdr_password_var.get():
            messagebox.showerror("错误", "请输入重点人网站账号1密码")
            return False
        
        # 验证第二个账号：如果输入了用户名，则密码也必须输入
        if self.zdr_username2_var.get() and not self.zdr_password2_var.get():
            messagebox.showerror("错误", "请输入重点人网站账号2密码")
            return False
        if self.zdr_password2_var.get() and not self.zdr_username2_var.get():
            messagebox.showerror("错误", "请输入重点人网站账号2用户名")
            return False
        
        if not self.jx_id_card_var.get():
            messagebox.showerror("错误", "请输入警信网站身份证号")
            return False
        if not self.jx_password_var.get():
            messagebox.showerror("错误", "请输入警信网站密码")
            return False
        return True
    
    def worker_loop(self):
        """工作循环"""
        while self.is_running:
            self.cycle_count += 1
            self.cycle_count_var.set(str(self.cycle_count))
            
            self.execute_cycle()
            
            if not self.is_running:
                break
            
            # 等待循环间隔
            cycle_minutes = int(self.cycle_minutes_var.get())
            for i in range(cycle_minutes * 60):
                if not self.is_running:
                    break
                time.sleep(1)
    
    def execute_cycle(self):
        """执行一次完整循环"""
        try:
            self.logger.log_cycle_start(self.cycle_count)
            
            mode = self.run_mode_var.get()
            if not self.website_handler.init_browser(mode):
                return False
            
            try:
                # 处理重点人网站（包括所有配置的账号）
                if not self.website_handler.handle_zdr_website():
                    return False
                
                # 获取所有下载的文件路径，传递给警信网站
                download_dir = self.config.ensure_download_dir()
                from pathlib import Path
                import os
                
                # 获取今天下载的所有文件
                today = time.strftime("%Y-%m-%d")
                files_to_upload = []
                
                try:
                    download_path = Path(download_dir)
                    if download_path.exists():
                        for file in download_path.glob("重点人_*.txt"):
                            # 检查文件是否是今天创建的
                            file_stat = os.stat(file)
                            file_date = time.strftime("%Y-%m-%d", time.localtime(file_stat.st_mtime))
                            if file_date == today:
                                files_to_upload.append(str(file))
                except Exception as e:
                    self.logger.warning(f"获取上传文件列表失败: {str(e)}")
                
                # 处理警信网站
                if not self.website_handler.handle_jx_website(files_to_upload):
                    return False
                
                self.logger.log_cycle_end(self.cycle_count, True)
                return True
                
            finally:
                self.website_handler.close_browser()
                
        except Exception as e:
            self.logger.error(f"执行循环失败: {str(e)}")
            return False
    
    def update_status(self, status, color="black"):
        """更新状态显示"""
        self.status_var.set(status)
        self.status_label.config(foreground=color)
    
    def refresh_log(self):
        """刷新日志显示"""
        try:
            log_content = self.logger.get_log_content(100)
            self.log_text.config(state="normal")
            self.log_text.delete(1.0, tk.END)
            self.log_text.insert(tk.END, log_content)
            self.log_text.config(state="disabled")
            self.log_text.see(tk.END)
        except Exception as e:
            print(f"刷新日志失败: {e}")
    
    def auto_refresh_log(self):
        """自动刷新日志"""
        if hasattr(self, 'log_text'):
            self.refresh_log()
            self.root.after(5000, self.auto_refresh_log)
    
    def clear_log(self):
        """清空日志显示"""
        self.log_text.config(state="normal")
        self.log_text.delete(1.0, tk.END)
        self.log_text.config(state="disabled")
    
    def run(self):
        """运行GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_running:
            if messagebox.askokcancel("确认", "系统正在运行，确定要退出吗？"):
                self.stop_system()
                time.sleep(1)
                self.root.destroy()
        else:
            self.root.destroy()

if __name__ == "__main__":
    app = AutoSystemGUI()
    app.run() 