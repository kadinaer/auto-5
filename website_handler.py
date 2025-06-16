"""
网站操作处理器模块
"""
import time
import os
import re
from datetime import datetime, date
from pathlib import Path
from DrissionPage import Chromium, ChromiumOptions
from logger import Logger
from config import ConfigManager

class WebsiteHandler:
    def __init__(self, config_manager: ConfigManager, logger: Logger):
        self.config = config_manager
        self.logger = logger
        self.browser = None
        self.tab = None
        self.zd_flag_time = None  # 上次检查的时间
        self.downloaded_files = []  # 已下载的文件列表
    
    def init_browser(self, mode="新浏览器"):
        """初始化浏览器"""
        try:
            if mode == "无头模式":
                options = ChromiumOptions()
                options.headless()
                self.browser = Chromium(options)
            elif mode == "连接已有浏览器":
                # 连接已存在的浏览器
                self.browser = Chromium()
            else:  # 新浏览器
                self.browser = Chromium()
            
            self.tab = self.browser.latest_tab
            self.logger.info(f"浏览器初始化成功 - 模式: {mode}")
            return True
        except Exception as e:
            self.logger.error(f"浏览器初始化失败: {str(e)}")
            return False
    
    def close_browser(self):
        """关闭浏览器"""
        try:
            if self.browser:
                self.browser.quit()
                self.browser = None
                self.tab = None
                self.logger.info("浏览器已关闭")
        except Exception as e:
            self.logger.error(f"关闭浏览器失败: {str(e)}")
    
    def wait_for_page_load(self, loading_selector="t:div@@id=loading_manage", timeout=30):
        """等待页面加载完成"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                try:
                    loading_element = self.tab.ele(loading_selector, timeout=1)
                    if loading_element:
                        style = loading_element.attr('style')
                        if style and 'display: none' in style:
                            self.logger.debug("页面加载完成")
                            return True
                    else:
                        self.logger.debug("加载元素不存在，认为页面已加载")
                        return True
                except:
                    self.logger.debug("加载元素不存在，认为页面已加载")
                    return True
                time.sleep(1)
            
            self.logger.warning("页面加载超时")
            return False
        except Exception as e:
            self.logger.error(f"等待页面加载失败: {str(e)}")
            return False
    
    def handle_zdr_website(self):
        """处理重点人网站（所有账号）"""
        try:
            all_files = []
            
            # 处理第一个账号
            username1 = self.config.get("zdr_username")
            password1 = self.config.get("zdr_password")
            
            if username1 and password1:
                self.logger.info("开始处理重点人网站账号1...")
                files1 = self.handle_single_zdr_account(username1, password1, "账号1")
                if files1:
                    all_files.extend(files1)
            else:
                self.logger.error("重点人网站账号1用户名或密码未配置")
                return False
            
            # 处理第二个账号（如果配置了）
            username2 = self.config.get("zdr_username2")
            password2 = self.config.get("zdr_password2")
            
            if username2 and password2:
                self.logger.info("开始处理重点人网站账号2...")
                # 关闭当前浏览器，为第二个账号重新初始化
                self.close_browser()
                time.sleep(2)
                
                # 重新初始化浏览器
                mode = self.config.get("run_mode", "新浏览器")
                if not self.init_browser(mode):
                    self.logger.error("为账号2重新初始化浏览器失败")
                    return False
                
                files2 = self.handle_single_zdr_account(username2, password2, "账号2")
                if files2:
                    all_files.extend(files2)
            else:
                self.logger.info("重点人网站账号2未配置，跳过")
            
            self.logger.info(f"总共处理了 {len(all_files)} 个文件")
            return True
            
        except Exception as e:
            self.logger.error(f"处理重点人网站失败: {str(e)}")
            return False
    
    def handle_single_zdr_account(self, username, password, account_label):
        """处理单个重点人网站账号"""
        try:
            # 1-0 打开重点人网址
            self.logger.info(f"正在访问重点人网站 ({account_label})...")
            self.tab.get("http://35.0.40.55/kfkj_zdr/Views/Login/Index.html")
            time.sleep(3)
            
            # 1-1 输入用户名密码
            self.logger.info(f"正在输入登录信息 ({account_label})...")
            username_input = self.tab.ele("t:input@@id=username")
            password_input = self.tab.ele("t:input@@id=password")
            
            if not username_input or not password_input:
                self.logger.error(f"找不到用户名或密码输入框 ({account_label})")
                return []
            
            username_input.clear()
            username_input.input(username)
            password_input.clear()
            password_input.input(password)
            
            # 1-2 点击登录按钮
            login_btn = self.tab.ele("t:span@@tx():登录")
            if not login_btn:
                self.logger.error(f"找不到登录按钮 ({account_label})")
                return []
            
            login_btn.click()
            self.logger.info(f"已点击登录按钮 ({account_label})")
            
            # 1-3 等待页面加载
            time.sleep(5)
            if not self.wait_for_page_load():
                self.logger.warning(f"页面加载等待超时，继续执行 ({account_label})")
            
            # 1-4 点击我的情报
            my_intel_btn = self.tab.ele("t:div@@class=main-nav-text@@tx():我的情报")
            if not my_intel_btn:
                self.logger.error(f"找不到'我的情报'按钮 ({account_label})")
                return []
            
            my_intel_btn.click()
            self.logger.info(f"已点击'我的情报' ({account_label})")
            time.sleep(3)
            
            # 1-5 点击未接收
            unreceived_btn = self.tab.ele("t:a@@id=165d41e5ea5745b596cff61066478125@@tx():未接收")
            if not unreceived_btn:
                self.logger.error(f"找不到'未接收'按钮 ({account_label})")
                return []
            
            unreceived_btn.click()
            self.logger.info(f"已点击'未接收' ({account_label})")
            time.sleep(3)
            
            # 1-6 遍历概况界面
            return self.process_intelligence_table(account_label)
            
        except Exception as e:
            self.logger.error(f"处理重点人网站账号失败 ({account_label}): {str(e)}")
            return []
    
    def process_intelligence_table(self, account_label=""):
        """处理情报表格"""
        try:
            # 获取表格
            table = self.tab.ele("//table[@id='gridTable']")
            if not table:
                self.logger.error(f"找不到情报表格 ({account_label})")
                return []
            
            # 获取所有行
            rows = table.eles("tag:tr")
            if not rows:
                self.logger.warning(f"表格中没有数据行 ({account_label})")
                return []
            
            today = date.today()
            new_files = []
            
            # 遍历每一行
            for row in rows[1:]:  # 跳过表头
                cells = row.eles("tag:td")
                if not cells:
                    continue
                
                # 获取第一个时间戳
                first_cell_text = cells[0].text
                time_match = re.search(r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}', first_cell_text)
                
                if time_match:
                    time_str = time_match.group()
                    try:
                        file_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                        
                        # 检查是否是今天的数据
                        if file_time.date() == today:
                            # 检查是否比上次检查时间新
                            if not self.zd_flag_time or file_time > self.zd_flag_time:
                                # 保存行内容为txt文件
                                row_content = "\t".join([cell.text for cell in cells])
                                file_name = f"重点人_{account_label}_{time_str.replace(':', '-').replace(' ', '_')}.txt"
                                file_path = Path(self.config.ensure_download_dir()) / file_name
                                
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(row_content)
                                
                                new_files.append((time_str, str(file_path), row))
                                self.logger.info(f"保存情报信息 ({account_label}): {file_name}")
                    
                    except ValueError as e:
                        self.logger.warning(f"时间格式解析失败 ({account_label}): {time_str} - {e}")
            
            # 1-7 下载文件
            downloaded_files = []
            if new_files:
                downloaded_files = self.download_files(new_files, account_label)
            else:
                self.logger.info(f"没有新的情报需要下载 ({account_label})")
            
            return downloaded_files
                
        except Exception as e:
            self.logger.error(f"处理情报表格失败 ({account_label}): {str(e)}")
            return []
    
    def download_files(self, new_files, account_label=""):
        """下载文件"""
        try:
            download_count = 0
            downloaded_file_paths = []
            
            for time_str, txt_file_path, row in new_files:
                # 查找下载按钮
                download_btn = row.ele("t:a@@tx():下载")
                if download_btn:
                    try:
                        download_btn.click()
                        self.logger.info(f"点击下载按钮 ({account_label}): {time_str}")
                        time.sleep(2)  # 等待下载开始
                        
                        # 记录下载操作
                        self.downloaded_files.append(time_str)
                        downloaded_file_paths.append(txt_file_path)
                        download_count += 1
                        
                    except Exception as e:
                        self.logger.error(f"下载文件失败 ({account_label}) {time_str}: {str(e)}")
                else:
                    self.logger.warning(f"找不到下载按钮 ({account_label}): {time_str}")
            
            # 更新最后检查时间
            if new_files:
                latest_time = max([datetime.strptime(f[0], '%Y-%m-%d %H:%M:%S') for f in new_files])
                self.zd_flag_time = latest_time
                self.logger.info(f"更新最后检查时间 ({account_label}): {latest_time}")
            
            self.logger.info(f"本次下载文件数量 ({account_label}): {download_count}")
            return downloaded_file_paths
            
        except Exception as e:
            self.logger.error(f"下载文件失败 ({account_label}): {str(e)}")
            return []
    
    def handle_jx_website(self, files_to_upload):
        """处理警信网站"""
        try:
            if not files_to_upload:
                self.logger.info("没有需要上传的文件")
                return True
            
            # 2-0 打开警信网址
            self.logger.info("正在访问警信网站...")
            self.tab.get("https://10.2.120.214:10242/#/login")
            time.sleep(3)
            
            # 处理不安全的HTTPS警告
            try:
                # 输入 thisunsafe
                self.tab.actions.type("thisunsafe")
                time.sleep(2)
            except:
                self.logger.debug("无需处理HTTPS警告或已处理")
            
            # 2-1 输入身份证号和密码
            id_card = self.config.get("jx_id_card")
            password = self.config.get("jx_password")
            
            if not id_card or not password:
                self.logger.error("警信网站身份证号或密码未配置")
                return False
            
            self.logger.info("正在输入警信登录信息...")
            id_input = self.tab.ele("//input[@type='userName']")
            pwd_input = self.tab.ele("//input[@type='password']")
            
            if not id_input or not pwd_input:
                self.logger.error("找不到身份证号或密码输入框")
                return False
            
            id_input.clear()
            id_input.input(id_card)
            pwd_input.clear()
            pwd_input.input(password)
            
            # 2-2 点击登录
            login_btn = self.tab.ele("t:span@@tx():登录")
            if not login_btn:
                self.logger.error("找不到登录按钮")
                return False
            
            login_btn.click()
            self.logger.info("已点击登录按钮")
            time.sleep(5)
            
            # 检查是否成功登录到主页
            if "home/chat" not in self.tab.url:
                self.logger.error("登录后未跳转到正确页面")
                return False
            
            # 2-3 点击对应群聊
            group_name = self.config.get("jx_group_name", "情指值班通知")
            group_chat = self.tab.ele(f"t:div@@class=chat-name-text@@tx():{group_name}")
            if not group_chat:
                self.logger.error(f"找不到群聊: {group_name}")
                return False
            
            group_chat.click()
            self.logger.info(f"已点击群聊: {group_name}")
            time.sleep(2)
            
            # 2-4 上传文件
            return self.upload_files(files_to_upload)
            
        except Exception as e:
            self.logger.error(f"处理警信网站失败: {str(e)}")
            return False
    
    def upload_files(self, files_to_upload):
        """上传文件到警信"""
        try:
            upload_count = 0
            
            for file_path in files_to_upload:
                if not os.path.exists(file_path):
                    self.logger.warning(f"文件不存在: {file_path}")
                    continue
                
                # 2-4 点击发送文件
                send_file_btn = self.tab.ele("t:i@@class=icon iconfont icon-wenjian")
                if not send_file_btn:
                    self.logger.error("找不到发送文件按钮")
                    continue
                
                send_file_btn.click()
                self.logger.info("已点击发送文件按钮")
                time.sleep(2)
                
                # 处理文件上传
                try:
                    # 尝试查找文件输入框并上传文件
                    file_input = self.tab.ele("//input[@type='file']", timeout=5)
                    if file_input:
                        # 使用DrissionPage的文件上传功能
                        file_input.set.files(file_path)
                        time.sleep(2)
                        
                        # 2-5 点击确认发送
                        confirm_btn = self.tab.ele("//div[@class='el-message-box el-message-box--center']/div[@class='el-message-box__btns']/button[@class='el-button el-button--default el-button--small el-button--primary ']", timeout=5)
                        if not confirm_btn:
                            # 尝试其他可能的确认按钮选择器
                            confirm_btn = self.tab.ele("t:button@@tx():确定")
                            if not confirm_btn:
                                confirm_btn = self.tab.ele("t:button@@tx():发送")
                        
                        if confirm_btn:
                            confirm_btn.click()
                            self.logger.info(f"文件上传成功: {os.path.basename(file_path)}")
                            upload_count += 1
                            time.sleep(3)  # 等待上传完成
                        else:
                            self.logger.error("找不到确认发送按钮")
                    else:
                        self.logger.error("找不到文件输入框")
                        
                except Exception as e:
                    self.logger.error(f"上传文件失败 {file_path}: {str(e)}")
            
            self.logger.info(f"本次上传文件数量: {upload_count}")
            return upload_count > 0
            
        except Exception as e:
            self.logger.error(f"上传文件失败: {str(e)}")
            return False 