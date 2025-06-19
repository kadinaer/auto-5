"""
配置管理模块
"""
import json
import os
from pathlib import Path
from tkinter import filedialog, messagebox

class ConfigManager:
    def __init__(self):
        # 在根目录生成默认配置文件
        self.default_config_file = "default_config.json"
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
        # 当前使用的配置（内存中）
        self.config = self.default_config.copy()
        # 生成默认配置文件
        self.create_default_config_file()
    
    def create_default_config_file(self):
        """在根目录创建默认配置文件"""
        try:
            if not os.path.exists(self.default_config_file):
                with open(self.default_config_file, 'w', encoding='utf-8') as f:
                    json.dump(self.default_config, f, ensure_ascii=False, indent=4)
                print(f"已创建默认配置文件: {self.default_config_file}")
        except Exception as e:
            print(f"创建默认配置文件失败: {e}")
    
    def import_config(self):
        """导入配置文件"""
        try:
            file_path = filedialog.askopenfilename(
                title="选择配置文件",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir=os.getcwd()
            )
            
            if not file_path:
                return False, "未选择文件"
            
            with open(file_path, 'r', encoding='utf-8') as f:
                imported_config = json.load(f)
            
            # 验证导入的配置是否包含必要的字段
            for key in self.default_config.keys():
                if key not in imported_config:
                    imported_config[key] = self.default_config[key]
            
            self.config = imported_config
            return True, f"配置导入成功: {os.path.basename(file_path)}"
            
        except json.JSONDecodeError:
            return False, "配置文件格式错误，请检查JSON格式"
        except Exception as e:
            return False, f"导入配置失败: {str(e)}"
    
    def export_config(self):
        """导出配置文件"""
        try:
            file_path = filedialog.asksaveasfilename(
                title="保存配置文件",
                defaultextension=".json",
                filetypes=[("JSON文件", "*.json"), ("所有文件", "*.*")],
                initialdir=os.getcwd(),
                initialfile="config.json"
            )
            
            if not file_path:
                return False, "未选择保存位置"
            
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            
            return True, f"配置导出成功: {os.path.basename(file_path)}"
            
        except Exception as e:
            return False, f"导出配置失败: {str(e)}"
    
    def get(self, key, default=None):
        """获取配置值"""
        return self.config.get(key, default)
    
    def set(self, key, value):
        """设置配置值（仅在内存中）"""
        self.config[key] = value
    
    def update(self, config_dict):
        """批量更新配置（仅在内存中）"""
        self.config.update(config_dict)
    
    def ensure_download_dir(self):
        """确保下载目录存在"""
        download_path = Path(self.config.get("download_path", "./downloads"))
        download_path.mkdir(parents=True, exist_ok=True)
        return str(download_path)

    def set_download_path(self, path):
        """设置下载目录并保存到配置"""
        self.config['download_path'] = path
        self.save_config()

    def get_download_path(self):
        """获取下载目录"""
        return self.config.get('download_path', './downloads')

    def save_config(self):
        """保存当前配置到默认配置文件"""
        try:
            with open(self.default_config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
        except Exception as e:
            print(f"保存配置失败: {e}") 