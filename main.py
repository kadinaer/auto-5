"""
主程序入口
自动化警信人员预警系统
"""
import sys
import os
import time
from pathlib import Path

# 添加当前目录到路径，确保能导入模块
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

try:
    from gui import AutoSystemGUI
    from config import ConfigManager
    from logger import Logger
except ImportError as e:
    print(f"导入模块失败: {e}")
    print("请确保已安装所有依赖:")
    print("pip install DrissionPage")
    sys.exit(1)

def main():
    """主函数"""
    try:
        # 创建必要的目录
        os.makedirs("logs", exist_ok=True)
        os.makedirs("downloads", exist_ok=True)
        
        # 初始化日志
        logger = Logger()
        logger.info("系统启动")
        
        # 创建并运行GUI
        app = AutoSystemGUI()
        app.run()
        
        logger.info("系统退出")
        
    except Exception as e:
        print(f"系统启动失败: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 