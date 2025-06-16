"""
日志系统模块
"""
import logging
import os
from datetime import datetime
from pathlib import Path

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
        
        # 文件处理器
        file_handler = logging.FileHandler(self.log_file, encoding='utf-8')
        file_handler.setLevel(logging.DEBUG)
        
        # 控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 格式化器
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
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
        self.info(f"======== 开始第 {cycle_number} 次循环 ========")
    
    def log_cycle_end(self, cycle_number, success=True):
        """记录循环结束"""
        status = "成功" if success else "失败"
        self.info(f"======== 第 {cycle_number} 次循环结束: {status} ========")
    
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