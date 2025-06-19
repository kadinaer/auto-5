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
        self.root.title("auto_5警信")
        self.root.geometry("1200x800")  # 横向扩展窗口宽度
        self.root.minsize(1100, 650)  # 增加最小窗口宽度
        
        # 初始化组件
        self.config = ConfigManager()
        self.logger = Logger(self.config.get("log_level", "INFO"))
        self.website_handler = WebsiteHandler(self.config, self.logger)
        
        # 状态变量
        self.is_running = False
        self.is_paused = False
        self.cycle_count = 0
        
        self.setup_ui()
        self.load_config_to_ui()
    
    def setup_ui(self):
        """设置用户界面"""
        # 创建主框架
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # 标题
        title_label = ttk.Label(main_frame, text="auto_5警信", 
                               font=("Microsoft YaHei", 16, "bold"))
        title_label.pack(pady=(0, 20))
        
        # 配置区域 - 使用水平分栏布局
        config_main_frame = ttk.LabelFrame(main_frame, text="系统配置", padding="10")
        config_main_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 创建左右两列的配置布局
        left_config_frame = ttk.Frame(config_main_frame)
        left_config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 20))
        
        right_config_frame = ttk.Frame(config_main_frame)
        right_config_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 左侧配置：重点人网站配置
        zdr_group = ttk.LabelFrame(left_config_frame, text="重点人网站配置", padding="10")
        zdr_group.pack(fill=tk.X, pady=(0, 10))
        zdr_group.columnconfigure(1, weight=1)
        
        ttk.Label(zdr_group, text="账号1用户名:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.zdr_username_var = tk.StringVar()
        ttk.Entry(zdr_group, textvariable=self.zdr_username_var, width=25).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(zdr_group, text="账号1密码:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.zdr_password_var = tk.StringVar()
        ttk.Entry(zdr_group, textvariable=self.zdr_password_var, show="*", width=25).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(zdr_group, text="账号2用户名:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.zdr_username2_var = tk.StringVar()
        ttk.Entry(zdr_group, textvariable=self.zdr_username2_var, width=25).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(zdr_group, text="账号2密码:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.zdr_password2_var = tk.StringVar()
        ttk.Entry(zdr_group, textvariable=self.zdr_password2_var, show="*", width=25).grid(row=3, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 下载目录配置
        download_group = ttk.LabelFrame(left_config_frame, text="下载设置", padding="10")
        download_group.pack(fill=tk.X)
        download_group.columnconfigure(1, weight=1)
        
        ttk.Label(download_group, text="下载目录:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.download_path_var = tk.StringVar()
        download_path_entry = ttk.Entry(download_group, textvariable=self.download_path_var, width=20)
        download_path_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 5), pady=2)
        ttk.Button(download_group, text="选择", command=self.choose_download_path).grid(row=0, column=2, pady=2)
        
        # 右侧配置：警信网站配置
        jx_group = ttk.LabelFrame(right_config_frame, text="警信网站配置", padding="10")
        jx_group.pack(fill=tk.X, pady=(0, 10))
        jx_group.columnconfigure(1, weight=1)
        
        ttk.Label(jx_group, text="身份证号:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.jx_id_card_var = tk.StringVar()
        ttk.Entry(jx_group, textvariable=self.jx_id_card_var, width=25).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(jx_group, text="密码:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.jx_password_var = tk.StringVar()
        ttk.Entry(jx_group, textvariable=self.jx_password_var, show="*", width=25).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(jx_group, text="群聊名称:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.jx_group_name_var = tk.StringVar()
        ttk.Entry(jx_group, textvariable=self.jx_group_name_var, width=25).grid(row=2, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 系统设置配置
        system_group = ttk.LabelFrame(right_config_frame, text="系统设置", padding="10")
        system_group.pack(fill=tk.X)
        system_group.columnconfigure(1, weight=1)
        
        ttk.Label(system_group, text="运行模式:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.run_mode_var = tk.StringVar()
        mode_combo = ttk.Combobox(system_group, textvariable=self.run_mode_var, 
                                 values=["新浏览器", "连接已有浏览器", "无头模式"],
                                 state="readonly", width=22)
        mode_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        ttk.Label(system_group, text="循环间隔(分钟):").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.cycle_minutes_var = tk.StringVar()
        ttk.Entry(system_group, textvariable=self.cycle_minutes_var, width=25).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(10, 0), pady=2)
        
        # 按钮区域 - 横向排列以充分利用空间
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(pady=15)
        
        # 配置管理按钮组
        config_manage_frame = ttk.LabelFrame(button_frame, text="配置管理", padding="5")
        config_manage_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        ttk.Button(config_manage_frame, text="导入配置", command=self.import_config, width=12).pack(side=tk.LEFT, padx=2)
        ttk.Button(config_manage_frame, text="导出配置", command=self.export_config, width=12).pack(side=tk.LEFT, padx=2)
        
        # 系统控制按钮组
        control_frame = ttk.LabelFrame(button_frame, text="系统控制", padding="5")
        control_frame.pack(side=tk.LEFT, padx=(0, 20))
        
        self.start_button = ttk.Button(control_frame, text="启动", command=self.start_system, width=10)
        self.start_button.pack(side=tk.LEFT, padx=2)
        
        self.pause_button = ttk.Button(control_frame, text="暂停", command=self.pause_system, state="disabled", width=10)
        self.pause_button.pack(side=tk.LEFT, padx=2)
        
        self.stop_button = ttk.Button(control_frame, text="停止", command=self.stop_system, state="disabled", width=10)
        self.stop_button.pack(side=tk.LEFT, padx=2)
        
        # 立即执行按钮组
        execute_frame = ttk.LabelFrame(button_frame, text="立即执行", padding="5")
        execute_frame.pack(side=tk.LEFT)
        
        ttk.Button(execute_frame, text="执行一次", command=self.execute_once, width=12).pack()
        
        # 状态区域 - 更好的布局
        status_frame = ttk.LabelFrame(main_frame, text="运行状态", padding="10")
        status_frame.pack(fill=tk.X, pady=(0, 10))
        
        # 状态信息水平排列
        status_info_frame = ttk.Frame(status_frame)
        status_info_frame.pack(fill=tk.X)
        
        # 左侧状态组
        left_status_frame = ttk.Frame(status_info_frame)
        left_status_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        ttk.Label(left_status_frame, text="当前状态:", font=("Microsoft YaHei", 9, "bold")).pack(side=tk.LEFT)
        self.status_var = tk.StringVar(value="未运行")
        self.status_label = ttk.Label(left_status_frame, textvariable=self.status_var, foreground="red", font=("Microsoft YaHei", 9))
        self.status_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # 右侧循环次数组
        right_status_frame = ttk.Frame(status_info_frame)
        right_status_frame.pack(side=tk.RIGHT)
        
        ttk.Label(right_status_frame, text="循环次数:", font=("Microsoft YaHei", 9, "bold")).pack(side=tk.LEFT)
        self.cycle_count_var = tk.StringVar(value="0")
        ttk.Label(right_status_frame, textvariable=self.cycle_count_var, font=("Microsoft YaHei", 9)).pack(side=tk.LEFT, padx=(10, 0))
        
        # 日志显示区域
        log_frame = ttk.Frame(main_frame)
        log_frame.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        ttk.Label(log_frame, text="系统日志:", font=('Arial', 10, 'bold')).pack(anchor=tk.W)
        
        # 创建带滚动条的文本框
        log_text_frame = ttk.Frame(log_frame)
        log_text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.log_text = tk.Text(log_text_frame, height=15, state=tk.DISABLED, 
                               wrap=tk.WORD, font=('Consolas', 9))
        
        # 为不同日志级别配置颜色标签
        self.log_text.tag_configure("DEBUG", foreground="#00CED1")    # 深天蓝色
        self.log_text.tag_configure("INFO", foreground="#228B22")     # 森林绿
        self.log_text.tag_configure("WARNING", foreground="#FF8C00")  # 暗橙色
        self.log_text.tag_configure("ERROR", foreground="#DC143C")    # 深红色
        self.log_text.tag_configure("CRITICAL", foreground="#8B0000", font=('Consolas', 9, 'bold'))  # 暗红色加粗
        
        log_scrollbar = ttk.Scrollbar(log_text_frame, orient=tk.VERTICAL, command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=log_scrollbar.set)
        
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        log_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        # 启动日志刷新
        self.auto_refresh_log()
        
        # 日志操作按钮框架
        log_button_frame = ttk.Frame(log_frame)
        log_button_frame.pack(pady=(8, 0), fill=tk.X)
        
        ttk.Button(log_button_frame, text="刷新日志", command=self.refresh_log, width=12).pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(log_button_frame, text="清空日志", command=self.clear_log, width=12).pack(side=tk.LEFT)
        
        # 在右侧添加日志级别选择
        ttk.Label(log_button_frame, text="日志级别:").pack(side=tk.RIGHT, padx=(20, 5))
        self.log_level_var = tk.StringVar(value="INFO")
        log_level_combo = ttk.Combobox(log_button_frame, textvariable=self.log_level_var, 
                                      values=["DEBUG", "INFO", "WARNING", "ERROR"], 
                                      state="readonly", width=8)
        log_level_combo.pack(side=tk.RIGHT)
        log_level_combo.bind("<<ComboboxSelected>>", self.on_log_level_change)
        
        # 初始化按钮状态
        self.update_button_states("stopped")
    
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
        self.download_path_var.set(self.config.get_download_path())
    
    def import_config(self):
        """导入配置文件"""
        success, message = self.config.import_config()
        if success:
            # 更新界面显示
            self.load_config_to_ui()
            messagebox.showinfo("成功", message)
            self.logger.info(f"配置导入: {message}")
        else:
            messagebox.showerror("错误", message)
            self.logger.error(f"配置导入失败: {message}")
    
    def export_config(self):
        """导出配置文件"""
        # 先保存当前界面的配置到内存
        if not self.save_ui_to_config():
            return
        
        success, message = self.config.export_config()
        if success:
            messagebox.showinfo("成功", message)
            self.logger.info(f"配置导出: {message}")
        else:
            messagebox.showerror("错误", message)
            self.logger.error(f"配置导出失败: {message}")
    
    def save_ui_to_config(self):
        """将界面数据保存到配置（内存中）"""
        try:
            cycle_minutes = int(self.cycle_minutes_var.get())
            if cycle_minutes <= 0:
                messagebox.showerror("错误", "循环间隔必须是正整数")
                return False
        except ValueError:
            messagebox.showerror("错误", "循环间隔必须是数字")
            return False
        
        self.config.update({
            "zdr_username": self.zdr_username_var.get(),
            "zdr_password": self.zdr_password_var.get(),
            "zdr_username2": self.zdr_username2_var.get(),
            "zdr_password2": self.zdr_password2_var.get(),
            "jx_id_card": self.jx_id_card_var.get(),
            "jx_password": self.jx_password_var.get(),
            "jx_group_name": self.jx_group_name_var.get(),
            "run_mode": self.run_mode_var.get(),
            "cycle_minutes": cycle_minutes,
            "download_path": self.download_path_var.get()
        })
        return True
    
    def start_system(self):
        """启动或恢复系统运行"""
        if not self.validate_config():
            return
        
        # 将当前界面配置保存到内存中
        if not self.save_ui_to_config():
            return
        
        if self.is_paused:
            # 恢复运行
            self.is_paused = False
            self.update_status("正在运行", "green")
            self.update_button_states("running")
            self.logger.info("系统恢复运行")
        else:
            # 首次启动
            self.is_running = True
            self.is_paused = False
            self.cycle_count = 0
            self.cycle_count_var.set("0")
            self.update_status("正在运行", "green")
            self.update_button_states("running")
            
            threading.Thread(target=self.worker_loop, daemon=True).start()
            self.logger.info("系统启动运行")
    
    def pause_system(self):
        """暂停系统运行"""
        if self.is_running and not self.is_paused:
            self.is_paused = True
            self.update_status("已暂停", "orange")
            self.update_button_states("paused")
            self.logger.info("系统已暂停")
    
    def stop_system(self):
        """停止系统运行"""
        self.is_running = False
        self.is_paused = False
        self.update_status("已停止", "red")
        self.update_button_states("stopped")
        
        if self.website_handler:
            self.website_handler.close_browser()
        
        self.logger.info("系统已停止")
    
    def execute_once(self):
        """立即执行一次"""
        if not self.validate_config():
            return
        
        # 将当前界面配置保存到内存中
        if not self.save_ui_to_config():
            return
        
        # 临时设置状态，避免与主循环冲突
        self.logger.info("开始立即执行...")
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
            # 检查是否暂停
            if self.is_paused:
                time.sleep(1)
                continue
            
            self.cycle_count += 1
            self.cycle_count_var.set(str(self.cycle_count))
            
            self.execute_cycle()
            
            if not self.is_running:
                break
            
            # 等待循环间隔，期间可以响应暂停
            cycle_minutes = int(self.cycle_minutes_var.get())
            
            # 计算并显示下次循环时间
            import datetime
            next_cycle_time = datetime.datetime.now() + datetime.timedelta(minutes=cycle_minutes)
            self.logger.info(f"第{self.cycle_count}次循环已完成，下次循环时间: {next_cycle_time.strftime('%Y-%m-%d %H:%M:%S')}")
            
            for i in range(cycle_minutes * 60):
                if not self.is_running:
                    break
                if self.is_paused:
                    # 暂停期间跳出等待循环
                    break
                time.sleep(1)
        
        # 工作循环结束，确保状态正确
        if not self.is_paused:
            self.update_status("已停止", "red")
            self.update_button_states("stopped")
    
    def execute_cycle(self):
        """执行一次完整循环"""
        try:
            self.logger.log_cycle_start(self.cycle_count)
            
            mode = self.run_mode_var.get()
            if not self.website_handler.init_browser(mode):
                return False
            
            try:
                # 处理重点人网站（包括所有配置的账号）
                downloaded_files = self.website_handler.handle_zdr_website()
                if not downloaded_files:
                    self.logger.warning("重点人网站未下载到任何文件")
                    return False
                
                self.logger.info(f"重点人网站共下载了 {len(downloaded_files)} 个文件")
                
                # 处理警信网站，传递实际下载的文件列表
                if not self.website_handler.handle_jx_website(downloaded_files):
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
    
    def update_button_states(self, state):
        """更新按钮状态"""
        if state == "stopped":
            # 未运行状态：只能启动
            self.start_button.config(state="normal", text="启动")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="disabled")
        elif state == "running":
            # 运行状态：可以暂停和停止
            self.start_button.config(state="disabled")
            self.pause_button.config(state="normal")
            self.stop_button.config(state="normal")
        elif state == "paused":
            # 暂停状态：可以恢复和停止
            self.start_button.config(state="normal", text="恢复")
            self.pause_button.config(state="disabled")
            self.stop_button.config(state="normal")
    
    def refresh_log(self):
        """刷新日志显示（支持颜色）"""
        try:
            if hasattr(self, 'logger') and self.logger:
                # 获取日志行列表
                log_lines = self.logger.get_colored_log_content(100)
                
                self.log_text.config(state="normal")
                self.log_text.delete(1.0, tk.END)
                
                # 逐行处理日志，根据级别添加颜色
                for line in log_lines:
                    line = line.strip()
                    if not line:
                        continue
                    
                    # 提取日志级别
                    log_level = "INFO"  # 默认级别
                    if " - DEBUG - " in line:
                        log_level = "DEBUG"
                    elif " - INFO - " in line:
                        log_level = "INFO"
                    elif " - WARNING - " in line:
                        log_level = "WARNING"
                    elif " - ERROR - " in line:
                        log_level = "ERROR"
                    elif " - CRITICAL - " in line:
                        log_level = "CRITICAL"
                    
                    # 插入带颜色标签的文本
                    self.log_text.insert(tk.END, line + "\n", log_level)
                
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
    
    def on_log_level_change(self, event=None):
        """日志级别变更处理"""
        new_level = self.log_level_var.get()
        self.logger.set_level(new_level)
        self.logger.info(f"日志级别已设置为: {new_level}")
        self.refresh_log()
    
    def run(self):
        """运行GUI"""
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()
    
    def on_closing(self):
        """窗口关闭事件"""
        if self.is_running or self.is_paused:
            status_text = "运行" if self.is_running and not self.is_paused else "暂停"
            if messagebox.askokcancel("确认", f"系统正在{status_text}，确定要退出吗？"):
                self.stop_system()
                time.sleep(1)
                self.root.destroy()
        else:
            self.root.destroy()

    def choose_download_path(self):
        """选择下载目录"""
        path = filedialog.askdirectory(title="选择下载目录")
        if path:
            self.download_path_var.set(path)
            self.config.set_download_path(path)
            self.logger.info(f"下载目录已设置为: {path}")

if __name__ == "__main__":
    app = AutoSystemGUI()
    app.run() 