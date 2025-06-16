"""
配置管理模块
"""
import json
import os
from pathlib import Path

class ConfigManager:
    def __init__(self):
        self.config_file = "config.json"
        self.default_config = {
            "zdr_username": "",
            "zdr_password": "",
            "zdr_username2": "",
            "zdr_password2": "",
            "jx_id_card": "",
            "jx_password": "",
            "jx_group_name": "情指值班通知",
            "run_mode": "新浏览器",  # 新浏览器/连接已有浏览器/无头模式
            "cycle_minutes": 30,
            "download_path": "./downloads",
            "log_level": "INFO"
        }
        self.config = self.load_config()
    
    def load_config(self):
        """加载配置文件"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                # 补充缺失的配置项
                for key, value in self.default_config.items():
                    if key not in config:
                        config[key] = value
                return config
            else:
                return self.default_config.copy()
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return self.default_config.copy()
    
    def save_config(self):
        """保存配置文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            return False
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值"""
        self.config[key] = value
    
    def update(self, config_dict):
        """批量更新配置"""
        self.config.update(config_dict)
    
    def ensure_download_dir(self):
        """确保下载目录存在"""
        download_path = Path(self.config.get("download_path", "./downloads"))
        download_path.mkdir(parents=True, exist_ok=True)
        return str(download_path) 