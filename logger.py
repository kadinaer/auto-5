"""
日志系统模块
"""
import logging
import os
from datetime import datetime
from pathlib import Path

# ANSI 颜色代码
class Colors:
    RESET = '\033[0m'
    RED = '\033[91m'         # ERROR, CRITICAL
    YELLOW = '\033[93m'      # WARNING
    GREEN = '\033[92m'       # INFO
    CYAN = '\033[96m'        # DEBUG
    PURPLE = '\033[95m'      # 特殊操作
    BOLD = '\033[1m'
    
    @classmethod
    def colorize(cls, text, color):
        """为文本添加颜色"""
        return f"{color}{text}{cls.RESET}"

class ColoredFormatter(logging.Formatter):
    """带颜色的日志格式化器"""
    
    COLORS = {
        'DEBUG': Colors.CYAN,
        'INFO': Colors.GREEN,
        'WARNING': Colors.YELLOW,
        'ERROR': Colors.RED,
        'CRITICAL': Colors.RED + Colors.BOLD,
    }
    
    def format(self, record):
        # 获取原始格式化的消息
        formatted = super().format(record)
        
        # 获取日志级别对应的颜色
        level_color = self.COLORS.get(record.levelname, Colors.RESET)
        
        # 为整行添加颜色
        colored_formatted = Colors.colorize(formatted, level_color)
        
        return colored_formatted

class Logger:
    def __init__(self, log_level="INFO"):
        self.log_dir = Path("logs")
        self.log_dir.mkdir(exist_ok=True)
        
        # 创建日志文件名（按日期）
        today = datetime.now().strftime("%Y-%m-%d")
        self.log_file = self.log_dir / f"auto_system_{today}.log"
        
        # 配置日志
        self.logger = logging.getLogger("AutoSystem")
        self.logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # 清除已有的处理器
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # 文件处理器（无颜色）
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # 控制台处理器（带颜色）
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        console_formatter = ColoredFormatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        console_handler.setFormatter(console_formatter)
        
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
    
    def info(self, message):
        """记录信息日志"""
        self.logger.info(message)
    
    def warning(self, message):
        """记录警告日志"""
        self.logger.warning(message)
    
    def error(self, message):
        """记录错误日志"""
        self.logger.error(message)
    
    def debug(self, message):
        """记录调试日志"""
        self.logger.debug(message)
    
    def critical(self, message):
        """记录严重错误日志"""
        self.logger.critical(message)
    
    def set_level(self, log_level):
        """设置日志级别"""
        level = getattr(logging, log_level.upper(), logging.INFO)
        self.logger.setLevel(level)
        # 同时更新所有处理器的级别
        for handler in self.logger.handlers:
            if isinstance(handler, logging.FileHandler):
                handler.setLevel(logging.DEBUG)  # 文件总是记录所有级别
            else:
                handler.setLevel(level)  # 控制台使用指定级别
    
    def log_operation(self, operation, result, details=""):
        """记录操作日志"""
        status = "成功" if result else "失败"
        message = f"操作: {operation} - 状态: {status}"
        if details:
            message += f" - 详情: {details}"
        
        if result:
            self.info(message)
        else:
            self.error(message)
    
    def log_download(self, file_name, file_path, success=True):
        """记录下载日志"""
        if success:
            self.info(f"文件下载成功: {file_name} -> {file_path}")
        else:
            self.error(f"文件下载失败: {file_name}")
    
    def log_cycle_start(self, cycle_number):
        """记录循环开始"""
        self.info(Colors.colorize(f"======== 开始第 {cycle_number} 次循环 ========", Colors.PURPLE + Colors.BOLD))
    
    def log_cycle_end(self, cycle_number, success=True):
        """记录循环结束"""
        status = "成功" if success else "失败"
        color = Colors.GREEN if success else Colors.RED
        self.info(Colors.colorize(f"======== 第 {cycle_number} 次循环结束: {status} ========", color + Colors.BOLD))
    
    def get_log_content(self, lines=100):
        """获取最近的日志内容"""
        try:
            if not self.log_file.exists():
                return "暂无日志记录"
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return ''.join(all_lines[-lines:]) if all_lines else "暂无日志记录"
        except Exception as e:
            return f"读取日志失败: {str(e)}"
    
    def get_colored_log_content(self, lines=100):
        """获取带颜色的日志内容（用于GUI显示）"""
        try:
            if not self.log_file.exists():
                return ["暂无日志记录"]
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                all_lines = f.readlines()
                return all_lines[-lines:] if all_lines else ["暂无日志记录"]
        except Exception as e:
            return [f"读取日志失败: {str(e)}"] 