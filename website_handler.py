"""
网站操作处理器模块
"""
import time
import os
import re
from datetime import datetime, date, timedelta
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
            all_downloaded_files = []
            
            # 处理第一个账号
            username1 = self.config.get("zdr_username")
            password1 = self.config.get("zdr_password")
            
            if username1 and password1:
                self.logger.info("开始处理重点人网站账号1...")
                files1 = self.handle_single_zdr_account(username1, password1, "账号1")
                if files1:
                    all_downloaded_files.extend(files1)
            else:
                self.logger.error("重点人网站账号1用户名或密码未配置")
                return []
            
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
                    return all_downloaded_files
                
                files2 = self.handle_single_zdr_account(username2, password2, "账号2")
                if files2:
                    all_downloaded_files.extend(files2)
            else:
                self.logger.info("重点人网站账号2未配置，跳过")
            
            self.logger.info(f"总共下载了 {len(all_downloaded_files)} 个文件")
            # 将下载的文件列表存储到实例变量中，供后续使用
            self.latest_downloaded_files = all_downloaded_files
            return all_downloaded_files
            
        except Exception as e:
            self.logger.error(f"处理重点人网站失败: {str(e)}")
            return []
    
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
            
            # 1-5 点击未接收（带重试机制）
            click_success = self.click_unreceived_button_with_retry(account_label)
            if not click_success:
                return []
            
            # 1-6 遍历概况界面
            self.logger.info(f"开始处理情报表格 ({account_label})")
            return self.process_intelligence_table(account_label)
            
        except Exception as e:
            self.logger.error(f"处理重点人网站账号失败 ({account_label}): {str(e)}")
            import traceback
            self.logger.error(f"详细错误信息 ({account_label}): {traceback.format_exc()}")
            return []
    
    def click_unreceived_button_with_retry(self, account_label="", max_retries=3, retry_interval=10):
        """点击'未接收'按钮（带重试机制）"""
        for retry_count in range(max_retries):
            try:
                if retry_count > 0:
                    self.logger.info(f"第 {retry_count + 1}/{max_retries} 次尝试点击'未接收'按钮 ({account_label})")
                    # 重试前重新访问页面或刷新
                    try:
                        # 先尝试刷新页面
                        self.tab.refresh()
                        time.sleep(5)
                        
                        # 重新点击"我的情报"
                        my_intel_btn = self.tab.ele("t:div@@class=main-nav-text@@tx():我的情报", timeout=10)
                        if my_intel_btn:
                            my_intel_btn.click()
                            self.logger.info(f"重试时重新点击'我的情报' ({account_label})")
                            time.sleep(3)
                        else:
                            self.logger.warning(f"重试时未找到'我的情报'按钮 ({account_label})")
                    except Exception as refresh_e:
                        self.logger.warning(f"重试前刷新页面失败: {refresh_e} ({account_label})")
                else:
                    self.logger.info(f"开始查找'未接收'按钮 ({account_label})")
                
                # 等待页面稳定
                time.sleep(5)
                
                unreceived_btn = None
                
                # 尝试多种选择器查找"未接收"按钮
                selectors = [
                    "t:a@@id=165d41e5ea5745b596cff61066478125@@tx():未接收",
                    "//a[@id='165d41e5ea5745b596cff61066478125' and contains(text(), '未接收')]",
                    "//a[contains(text(), '未接收')]",
                    "t:a@@tx():未接收"
                ]
                
                for i, selector in enumerate(selectors):
                    try:
                        self.logger.debug(f"尝试选择器 {i+1}/{len(selectors)}: {selector} ({account_label})")
                        unreceived_btn = self.tab.ele(selector, timeout=10)
                        if unreceived_btn:
                            self.logger.info(f"找到'未接收'按钮，使用选择器: {selector} ({account_label})")
                            
                            # 检查元素是否可见和可点击
                            try:
                                is_displayed = unreceived_btn.states.is_displayed
                                is_enabled = unreceived_btn.states.is_enabled
                                bounds = unreceived_btn.rect.location
                                self.logger.info(f"'未接收'按钮状态: 可见={is_displayed}, 可用={is_enabled}, 位置={bounds} ({account_label})")
                                
                                if not is_displayed:
                                    self.logger.warning(f"'未接收'按钮不可见，尝试滚动到视图中 ({account_label})")
                                    unreceived_btn.scroll.to_view()
                                    time.sleep(2)
                                
                            except Exception as state_e:
                                self.logger.warning(f"检查按钮状态失败: {state_e} ({account_label})")
                            
                            break
                    except Exception as e:
                        self.logger.debug(f"选择器 {selector} 失败: {e} ({account_label})")
                        continue
                
                if not unreceived_btn:
                    self.logger.warning(f"找不到'未接收'按钮，尝试查找页面中所有链接 ({account_label})")
                    try:
                        all_links = self.tab.eles("tag:a")
                        self.logger.info(f"页面中共找到 {len(all_links)} 个链接 ({account_label})")
                        
                        for i, link in enumerate(all_links[:20]):  # 只显示前20个
                            try:
                                link_text = link.text.strip()
                                link_id = link.attr('id') or 'no-id'
                                link_href = link.attr('href') or 'no-href'
                                self.logger.info(f"链接 {i+1}: text='{link_text}', id={link_id}, href={link_href} ({account_label})")
                                
                                if '未接收' in link_text:
                                    self.logger.info(f"发现包含'未接收'的链接，使用链接 {i+1} ({account_label})")
                                    unreceived_btn = link
                                    break
                            except Exception as link_e:
                                self.logger.debug(f"分析链接 {i+1} 失败: {link_e} ({account_label})")
                    except Exception as e:
                        self.logger.warning(f"查找所有链接失败: {e} ({account_label})")
                
                if not unreceived_btn:
                    if retry_count < max_retries - 1:
                        self.logger.warning(f"第 {retry_count + 1}/{max_retries} 次未找到'未接收'按钮，{retry_interval}秒后重试 ({account_label})")
                        time.sleep(retry_interval)
                        continue
                    else:
                        self.logger.error(f"所有尝试后仍未找到'未接收'按钮 ({account_label})")
                        return False
                
                # 尝试点击按钮
                self.logger.info(f"准备点击'未接收'按钮 ({account_label})")
                
                # 等待一段时间确保页面稳定
                time.sleep(3)
                
                click_success = False
                try:
                    # 先尝试普通点击
                    unreceived_btn.click()
                    self.logger.info(f"成功点击'未接收'按钮 ({account_label})")
                    click_success = True
                    
                except Exception as click_e:
                    self.logger.warning(f"普通点击失败: {click_e}，尝试其他点击方式 ({account_label})")
                    
                    try:
                        # 尝试JavaScript点击
                        self.tab.run_js("arguments[0].click();", unreceived_btn)
                        self.logger.info(f"JavaScript点击'未接收'按钮成功 ({account_label})")
                        click_success = True
                    except Exception as js_e:
                        self.logger.warning(f"JavaScript点击也失败: {js_e} ({account_label})")
                        click_success = False
                
                if click_success:
                    time.sleep(5)  # 等待页面响应
                    
                    # 验证点击是否成功（通过检查页面变化）
                    try:
                        # 检查是否进入了iframe页面或URL是否发生变化
                        current_url = self.tab.url
                        self.logger.info(f"点击后页面URL: {current_url} ({account_label})")
                        
                        # 等待iframe加载
                        time.sleep(3)
                        iframe_found = False
                        try:
                            # 尝试查找目标iframe来验证页面是否正确加载
                            iframe = self.tab.get_frame('iframe165d41e5ea5745b596cff61066478125')
                            if iframe:
                                iframe_found = True
                                self.logger.info(f"验证成功：找到目标iframe，点击'未接收'按钮成功 ({account_label})")
                            else:
                                # 尝试其他iframe查找方式
                                iframe_elem = self.tab.ele("//iframe[contains(@id, '165d41e5ea5745b596cff61066478125')]", timeout=5)
                                if iframe_elem:
                                    iframe_found = True
                                    self.logger.info(f"验证成功：找到目标iframe元素，点击'未接收'按钮成功 ({account_label})")
                        except Exception as verify_e:
                            self.logger.debug(f"验证iframe时出错: {verify_e} ({account_label})")
                        
                        if iframe_found:
                            return True
                        else:
                            if retry_count < max_retries - 1:
                                self.logger.warning(f"点击后未找到预期的iframe，可能点击未生效，{retry_interval}秒后重试 ({account_label})")
                                time.sleep(retry_interval)
                                continue
                            else:
                                self.logger.error(f"点击'未接收'按钮后未进入预期页面 ({account_label})")
                                return False
                                
                    except Exception as verify_e:
                        self.logger.warning(f"验证点击结果失败: {verify_e} ({account_label})")
                        # 如果验证失败但没有其他错误，假设点击成功
                        return True
                else:
                    if retry_count < max_retries - 1:
                        self.logger.warning(f"第 {retry_count + 1}/{max_retries} 次点击失败，{retry_interval}秒后重试 ({account_label})")
                        time.sleep(retry_interval)
                        continue
                    else:
                        self.logger.error(f"所有尝试后仍无法点击'未接收'按钮 ({account_label})")
                        return False
                        
            except Exception as e:
                self.logger.error(f"第 {retry_count + 1}/{max_retries} 次尝试点击'未接收'按钮时发生异常: {e} ({account_label})")
                import traceback
                self.logger.error(f"详细错误: {traceback.format_exc()} ({account_label})")
                
                if retry_count < max_retries - 1:
                    self.logger.info(f"{retry_interval}秒后重试 ({account_label})")
                    time.sleep(retry_interval)
                    continue
                else:
                    self.logger.error(f"重试机制耗尽，点击'未接收'按钮最终失败 ({account_label})")
                    return False
        
        return False
    
    def process_intelligence_table(self, account_label=""):
        """处理情报表格 - 使用DrissionPage的iframe处理方式"""
        try:
            # 等待页面完全加载
            self.logger.info(f"开始处理情报表格 ({account_label})")
            self.logger.info(f"等待页面加载，当前URL: {self.tab.url} ({account_label})")
            time.sleep(3)
            
            # 根据DrissionPage文档，获取iframe对象
            self.logger.info(f"开始查找目标iframe ({account_label})")
            
            # 首先尝试直接通过ID获取iframe
            iframe = None
            try:
                iframe = self.tab.get_frame('iframe165d41e5ea5745b596cff61066478125')
                if iframe:
                    self.logger.info(f"通过get_frame方法成功找到iframe ({account_label})")
            except Exception as e:
                self.logger.debug(f"get_frame方法失败: {e} ({account_label})")
            
            # 如果get_frame失败，使用普通元素方式获取
            if not iframe:
                iframe_selectors = [
                    "//iframe[@id='iframe165d41e5ea5745b596cff61066478125']",
                    "iframe#iframe165d41e5ea5745b596cff61066478125",
                    "//iframe[contains(@id, '165d41e5ea5745b596cff61066478125')]"
                ]
                
                for i, selector in enumerate(iframe_selectors):
                    self.logger.debug(f"尝试iframe选择器 {i+1}/{len(iframe_selectors)}: {selector} ({account_label})")
                    
                    for attempt in range(3):  # 尝试3次
                        try:
                            self.logger.debug(f"选择器 {i+1} 第{attempt+1}次尝试 ({account_label})")
                            iframe_elem = self.tab.ele(selector, timeout=10)
                            if iframe_elem:
                                # 将普通元素包装为iframe对象
                                iframe = self.tab.get_frame(iframe_elem)
                                if iframe:
                                    self.logger.info(f"成功找到并包装iframe，使用选择器: {selector} ({account_label})")
                                    iframe_id = iframe_elem.attr('id')
                                    iframe_src = iframe_elem.attr('src')
                                    iframe_style = iframe_elem.attr('style')
                                    self.logger.info(f"iframe详情: id={iframe_id}, src={iframe_src}, style={iframe_style} ({account_label})")
                                    break
                            else:
                                self.logger.debug(f"选择器 {selector} 未找到iframe ({account_label})")
                        except Exception as e:
                            self.logger.debug(f"选择器 {selector} 第{attempt+1}次尝试失败: {e} ({account_label})")
                            if attempt < 2:  # 不是最后一次尝试
                                time.sleep(2)  # 等待2秒后重试
                    
                    if iframe:
                        break
            
            # 如果还是没找到，详细分析页面状态
            if not iframe:
                self.logger.warning(f"使用预定义选择器未找到iframe，开始详细分析页面 ({account_label})")
                
                try:
                    all_iframes = self.tab.eles("tag:iframe")
                    self.logger.info(f"页面中共找到 {len(all_iframes)} 个iframe ({account_label})")
                    
                    for i, frame in enumerate(all_iframes):
                        frame_id = frame.attr('id') or 'no-id'
                        frame_src = frame.attr('src') or 'no-src'
                        frame_style = frame.attr('style') or 'no-style'
                        frame_class = frame.attr('class') or 'no-class'
                        self.logger.info(f"iframe {i+1}: id={frame_id}, src={frame_src}, style={frame_style}, class={frame_class} ({account_label})")
                        
                        # 尝试使用这个iframe如果它的id包含目标字符串
                        if '165d41e5ea5745b596cff61066478125' in frame_id:
                            self.logger.info(f"发现目标iframe，使用iframe {i+1} ({account_label})")
                            iframe = self.tab.get_frame(frame)
                            break
                
                except Exception as e:
                    self.logger.error(f"分析页面iframe时出错: {e} ({account_label})")
                
                # 延迟重试
                if not iframe:
                    self.logger.warning(f"仍未找到iframe，等待10秒后重试 ({account_label})")
                    time.sleep(10)
                    
                    try:
                        iframe_elem = self.tab.ele("//iframe[contains(@id, '165d41e5ea5745b596cff61066478125')]", timeout=15)
                        if iframe_elem:
                            iframe = self.tab.get_frame(iframe_elem)
                            if iframe:
                                self.logger.info(f"延迟重试成功找到iframe ({account_label})")
                    except Exception as e:
                        self.logger.error(f"延迟重试查找iframe失败: {e} ({account_label})")
            
            if not iframe:
                self.logger.error(f"最终未能找到情报页面iframe ({account_label})")
                return []
            
            # 等待iframe内容加载
            self.logger.info(f"等待iframe内容加载 ({account_label})")
            time.sleep(8)
            
            # 在iframe内查找表格
            self.logger.info(f"开始在iframe内查找数据表格 ({account_label})")
            table = None
            table_selectors = [
                "//table[@id='gridTable']", 
                "//table[contains(@class, 'ui-jqgrid-btable')]", 
                "#gridTable",
                "table[id*='grid']",
                "table[class*='jqgrid']"
            ]
            
            for i, selector in enumerate(table_selectors):
                try:
                    self.logger.debug(f"尝试在iframe内查找表格，选择器 {i+1}/{len(table_selectors)}: {selector} ({account_label})")
                    table = iframe.ele(selector, timeout=5)
                    if table:
                        self.logger.info(f"在iframe内找到表格，使用选择器: {selector} ({account_label})")
                        table_id = table.attr('id') or 'no-id'
                        table_class = table.attr('class') or 'no-class'
                        self.logger.info(f"表格详情: id={table_id}, class={table_class} ({account_label})")
                        break
                except Exception as e:
                    self.logger.debug(f"iframe内表格选择器 {selector} 失败: {e} ({account_label})")
                    continue
            
            if not table:
                self.logger.warning(f"使用预定义选择器未找到表格，尝试查找iframe中所有表格 ({account_label})")
                try:
                    # 使用iframe对象查找所有表格
                    all_tables = iframe.eles("tag:table")
                    self.logger.info(f"iframe中共找到 {len(all_tables)} 个表格 ({account_label})")
                    
                    for i, table_elem in enumerate(all_tables):
                        table_id = table_elem.attr('id') or 'no-id'
                        table_class = table_elem.attr('class') or 'no-class'
                        self.logger.info(f"iframe表格 {i+1}: id={table_id}, class={table_class} ({account_label})")
                        
                        # 如果表格ID或class包含grid相关字符串，尝试使用它
                        if 'grid' in table_id.lower() or 'grid' in table_class.lower():
                            self.logger.info(f"发现可能的数据表格，使用iframe表格 {i+1} ({account_label})")
                            table = table_elem
                            break
                            
                except Exception as e:
                    self.logger.error(f"查找iframe中所有表格时出错: {e} ({account_label})")
            
            if not table:
                self.logger.error(f"未找到iframe中的情报表格 ({account_label})")
                return []
            
            # 获取表格行 - 直接使用最有效的方法
            self.logger.info(f"开始获取表格数据行 ({account_label})")
            
            # 根据之前的成功经验，直接使用详细分析方法，避免浪费时间在失效的选择器上
            rows = None
            
            # 首先尝试一个最可能成功的简单选择器
            try:
                simple_rows = table.eles("tag:tr")
                if simple_rows and len(simple_rows) > 1:  # 至少有header行和数据行
                    # 快速过滤出数据行
                    data_rows = []
                    for row in simple_rows:
                        if hasattr(row, 'attr'):
                            row_class = row.attr('class') or ''
                            if 'jqgfirstrow' not in row_class and 'jqgrow' in row_class:
                                data_rows.append(row)
                    
                    if data_rows:
                        rows = data_rows
                        self.logger.info(f"快速方法找到 {len(rows)} 行数据 ({account_label})")
            except Exception as e:
                self.logger.debug(f"快速方法失败: {e} ({account_label})")
            
            # 如果快速方法失败，尝试备用快速方法
            if not rows:
                self.logger.debug(f"快速方法未找到数据行，尝试备用方法 ({account_label})")
                try:
                    # 备用方法：直接查找包含jqgrow类的行
                    backup_rows = table.eles("//tr[contains(@class, 'jqgrow') and not(contains(@class, 'jqgfirstrow'))]")
                    if backup_rows:
                        rows = backup_rows
                        self.logger.info(f"备用方法找到 {len(rows)} 行数据 ({account_label})")
                except Exception as e:
                    self.logger.debug(f"备用方法失败: {e} ({account_label})")
            
            if not rows:
                self.logger.info(f"所有快速方法都失败，使用详细分析方法 ({account_label})")
                
                # 详细分析表格结构
                try:
                    # 查看所有tr元素
                    all_trs = table.eles("tag:tr")
                    self.logger.debug(f"表格中共找到 {len(all_trs)} 个tr元素 ({account_label})")
                    
                    if all_trs:
                        data_rows = []
                        for i, tr in enumerate(all_trs):
                            # 只处理有attr方法的对象
                            if not hasattr(tr, 'attr'):
                                continue
                            tr_class = tr.attr('class') or 'no-class'
                            tr_id = tr.attr('id') or 'no-id'
                            tr_role = tr.attr('role') or 'no-role'
                            cells = tr.eles("tag:td")
                            cell_count = len(cells)
                            
                            # 判断是否为数据行：有足够的单元格且不是jqgfirstrow
                            if cell_count >= 8 and 'jqgfirstrow' not in tr_class:
                                data_rows.append(tr)
                                # 只在调试模式下输出详细信息
                                self.logger.debug(f"tr {i+1}: class='{tr_class}', id='{tr_id}', role='{tr_role}', cells={cell_count} ({account_label})")
                                # 获取第一个和最后一个单元格的文本作为示例
                                try:
                                    if cells and hasattr(cells[0], 'text'):
                                        first_cell_text = cells[0].text.strip()
                                    else:
                                        first_cell_text = str(cells[0]) if cells else ''
                                    if len(cells) > 7 and hasattr(cells[7], 'text'):
                                        time_cell_text = cells[7].text.strip()
                                    else:
                                        time_cell_text = str(cells[7]) if len(cells) > 7 else ''
                                    self.logger.debug(f"tr {i+1} 数据示例: 首格='{first_cell_text}', 时间='{time_cell_text}' ({account_label})")
                                except Exception as cell_e:
                                    self.logger.debug(f"获取单元格文本失败: {cell_e} ({account_label})")
                                    pass
                        if data_rows:
                            rows = data_rows
                            self.logger.info(f"详细分析找到 {len(rows)} 行数据 ({account_label})")
                        else:
                            self.logger.error(f"详细分析后仍未找到有效的数据行 ({account_label})")
                    
                except Exception as e:
                    self.logger.error(f"分析表格结构时出错: {e} ({account_label})")
                
                if not rows:
                    self.logger.error(f"经过详细分析仍未找到表格数据行 ({account_label})")
                    return []
            
            # 无论通过哪种方法找到数据行，都显示一些基本信息
            if rows:
                self.logger.info(f"成功获取到 {len(rows)} 行数据，开始处理 ({account_label})")
                # 显示第一行数据作为验证
                try:
                    first_row = rows[0]
                    cells = first_row.eles("tag:td")
                    if len(cells) >= 8:
                        first_cell = cells[0].text.strip() if hasattr(cells[0], 'text') and cells[0].text else str(cells[0])
                        time_cell = cells[7].text.strip() if hasattr(cells[7], 'text') and cells[7].text else str(cells[7])
                        self.logger.info(f"首行数据示例: 序号='{first_cell}', 时间='{time_cell}' ({account_label})")
                except Exception as e:
                    self.logger.debug(f"获取首行示例数据失败: {e} ({account_label})")
            
            today = date.today()
            new_files = []
            self.logger.info(f"开始处理 {len(rows)} 行数据，查找今天的记录 ({account_label})")
            self.logger.info(f"今天的日期: {today} ({account_label})")
            
            # 先统计所有数据的日期分布
            date_distribution = {}
            for i, row in enumerate(rows):
                try:
                    cells = row.eles("tag:td")
                    if len(cells) >= 8:
                        time_cell = cells[7]
                        time_text = ""
                        if hasattr(time_cell, 'text') and time_cell.text:
                            time_text = time_cell.text.strip()
                        elif hasattr(time_cell, 'inner_text'):
                            time_text = time_cell.inner_text.strip()
                        else:
                            # 最后尝试获取元素的文本内容
                            try:
                                time_text = str(time_cell.text or "").strip()
                            except:
                                time_text = ""
                        if time_text:
                            try:
                                file_time = datetime.strptime(time_text, '%Y-%m-%d %H:%M:%S')
                                date_key = file_time.date()
                                date_distribution[date_key] = date_distribution.get(date_key, 0) + 1
                            except ValueError:
                                pass
                except Exception:
                    pass
            
            # 显示数据日期分布
            if date_distribution:
                self.logger.info(f"数据日期分布: ({account_label})")
                for date_key, count in sorted(date_distribution.items(), reverse=True):
                    self.logger.info(f"  {date_key}: {count}条记录 ({account_label})")
            
            # 遍历每一行
            for i, row in enumerate(rows):
                try:
                    self.logger.debug(f"处理第 {i+1}/{len(rows)} 行数据 ({account_label})")
                    
                    # 获取所有td单元格
                    cells = row.eles("tag:td")
                    if len(cells) < 8:
                        self.logger.debug(f"第 {i+1} 行列数不足({len(cells)})，跳过 ({account_label})")
                        continue
                    
                    # 创建时间在第8列
                    time_cell = cells[7]
                    # 情报名称在第6列（索引5）
                    name_cell = cells[5] if len(cells) > 5 else None
                    
                    # 类型安全获取文本
                    time_text = ""
                    if hasattr(time_cell, 'text') and time_cell.text:
                        time_text = time_cell.text.strip()
                    elif hasattr(time_cell, 'inner_text'):
                        time_text = time_cell.inner_text.strip()
                    else:
                        # 最后尝试获取元素的文本内容
                        try:
                            time_text = str(time_cell.text or "").strip()
                        except:
                            time_text = ""
                    
                    intel_name = ""
                    if name_cell:
                        if hasattr(name_cell, 'text') and name_cell.text:
                            intel_name = name_cell.text.strip()
                        elif hasattr(name_cell, 'inner_text'):
                            intel_name = name_cell.inner_text.strip()
                        else:
                            try:
                                intel_name = str(name_cell.text or "").strip()
                            except:
                                intel_name = "未知情报"
                    else:
                        intel_name = "未知情报"
                    
                    # 对时间文本进行更严格的验证
                    if not time_text or len(time_text) < 10:  # 有效的时间至少应该有10个字符 (YYYY-MM-DD)
                        self.logger.debug(f"第 {i+1} 行时间字段为空或过短({time_text})，跳过 ({account_label})")
                        continue
                    
                    # 检查时间文本是否包含数字和分隔符
                    if not any(char.isdigit() for char in time_text) or '-' not in time_text:
                        self.logger.debug(f"第 {i+1} 行时间字段格式异常({time_text})，跳过 ({account_label})")
                        continue
                    
                    self.logger.debug(f"第 {i+1} 行时间: {time_text} ({account_label})")
                    
                    try:
                        file_time = datetime.strptime(time_text, '%Y-%m-%d %H:%M:%S')
                        
                        # 检查是否是今天的数据
                        if file_time.date() == today:
                            self.logger.info(f"发现今天的数据: {time_text} ({account_label})")
                            
                            # 检查是否比上次检查时间新
                            if not self.zd_flag_time or file_time > self.zd_flag_time:
                                self.logger.info(f"发现新的情报数据: {time_text} ({account_label})")
                                self.logger.info(f"情报名称: {intel_name} ({account_label})")
                                
                                # 只保存创建时间和情报名称，保存到根目录
                                file_name = f"重点人_{account_label}_{time_text.replace(':', '-').replace(' ', '_')}.txt"
                                file_path = Path("./") / file_name
                                with open(file_path, 'w', encoding='utf-8') as f:
                                    f.write(f"创建时间: {time_text}\n")
                                    f.write(f"情报名称: {intel_name}\n")
                                new_files.append((time_text, str(file_path), row))
                                self.logger.info(f"保存情报信息 ({account_label}): {file_name}")
                            else:
                                self.logger.debug(f"数据 {time_text} 不是新数据，跳过 ({account_label})")
                        else:
                            self.logger.debug(f"数据 {time_text} (日期: {file_time.date()}) 不是今天的数据，跳过 ({account_label})")
                    except ValueError as e:
                        self.logger.warning(f"时间格式解析失败 ({account_label}): {time_text} - {e}")
                        # 尝试其他时间格式
                        alternative_formats = [
                            '%Y/%m/%d %H:%M:%S',
                            '%m/%d/%Y %H:%M:%S', 
                            '%Y-%m-%d',
                            '%Y/%m/%d'
                        ]
                        parsed_success = False
                        for fmt in alternative_formats:
                            try:
                                file_time = datetime.strptime(time_text, fmt)
                                self.logger.info(f"使用备用格式成功解析时间: {time_text} -> {file_time} ({account_label})")
                                parsed_success = True
                                break
                            except ValueError:
                                continue
                        
                        if not parsed_success:
                            self.logger.debug(f"所有时间格式都无法解析: {time_text} ({account_label})")
                            continue
                except Exception as e:
                    self.logger.warning(f"处理第{i+1}行数据失败 ({account_label}): {str(e)}")
                    continue
            
            # 下载文件
            self.logger.info(f"发现 {len(new_files)} 个新文件需要下载 ({account_label})")
            
            # 如果没有找到新文件，提供有用的信息
            if len(new_files) == 0:
                if date_distribution:
                    latest_date = max(date_distribution.keys())
                    self.logger.info(f"没有找到今天({today})的新数据，最新数据日期是: {latest_date} ({account_label})")
                    if latest_date == today - timedelta(days=1):
                        self.logger.info(f"最新数据是昨天的，这可能是正常情况 ({account_label})")
                else:
                    self.logger.warning(f"表格中没有找到任何有效的时间数据 ({account_label})")
            
            downloaded_files = []
            if new_files:
                downloaded_files = self.download_files(new_files, account_label)
            else:
                self.logger.info(f"没有新的情报需要下载 ({account_label})")
            
            self.logger.info(f"情报表格处理完成，共下载 {len(downloaded_files)} 个文件 ({account_label})")
            return downloaded_files
                
        except Exception as e:
            self.logger.error(f"处理情报表格失败 ({account_label}): {str(e)}")
            import traceback
            self.logger.error(f"详细错误信息 ({account_label}): {traceback.format_exc()}")
            return []
    
    def download_files(self, new_files, account_label=""):
        """下载文件"""
        try:
            download_count = 0
            downloaded_file_paths = []
            # 获取自定义下载目录
            download_dir = Path(self.config.get("download_path", "./downloads"))
            download_dir.mkdir(parents=True, exist_ok=True)
            
            self.logger.info(f"开始下载 {len(new_files)} 个文件 ({account_label})")
            
            for file_index, (time_str, txt_file_path, row) in enumerate(new_files):
                try:
                    self.logger.info(f"处理第 {file_index+1}/{len(new_files)} 个文件: {time_str} ({account_label})")
                    
                    # 根据HTML分析，下载按钮的结构是：
                    # <a style="color:blue;cursor: pointer;" onclick="downloadfiles('RWLB...','/.../...')">下载</a>
                    download_btn = None
                    download_selectors = [
                        "a[onclick*='downloadfiles']",  # 最直接的选择器
                        "//a[contains(@onclick, 'downloadfiles')]",  # XPath版本
                        "a:contains('下载')",  # 包含"下载"文本的链接
                        "//a[text()='下载']",  # XPath查找文本为"下载"的链接
                        "a[onclick]",  # 所有有onclick属性的链接
                        ".download-btn",
                        "[onclick*='download']",
                        "a[title*='下载']"
                    ]
                    
                    self.logger.debug(f"开始查找下载按钮 ({account_label})")
                    for i, selector in enumerate(download_selectors):
                        try:
                            self.logger.debug(f"尝试下载按钮选择器 {i+1}/{len(download_selectors)}: {selector} ({account_label})")
                            download_btn = row.ele(selector, timeout=2)
                            if download_btn:
                                btn_text = download_btn.text.strip()
                                btn_onclick = download_btn.attr('onclick') or ''
                                btn_href = download_btn.attr('href') or ''
                                self.logger.info(f"找到下载按钮，选择器: {selector}, 文本: '{btn_text}', onclick: {btn_onclick[:100]} ({account_label})")
                                break
                            else:
                                self.logger.debug(f"选择器 {selector} 未找到下载按钮 ({account_label})")
                        except Exception as e:
                            self.logger.debug(f"选择器 {selector} 失败: {e} ({account_label})")
                            continue
                    
                    # 如果没找到下载按钮，智能查找和等待
                    if not download_btn:
                        self.logger.info(f"使用预定义选择器未找到下载按钮，开始智能查找 ({account_label})")
                        
                        # 第一步：增加更多下载按钮选择器
                        extended_selectors = [
                            # 基于HTML分析的更精确选择器
                            "//a[@style*='color:blue' and @onclick*='downloadfiles']",
                            "//a[@style*='cursor: pointer' and @onclick*='downloadfiles']",
                            "//a[contains(@onclick, 'downloadfiles') and contains(text(), '下载')]",
                            # 通用下载选择器
                            "a[style*='cursor: pointer']",
                            "//a[contains(text(), '下载') and @onclick]",
                            "//a[@onclick and not(@href)]",  # 有onclick但没有href的链接
                            "//td[last()]//a",  # 最后一列的链接（通常是操作列）
                            "//td[position()=7]//a",  # 第7列的链接（下载列）
                        ]
                        
                        # 尝试扩展选择器
                        for i, selector in enumerate(extended_selectors):
                            try:
                                self.logger.debug(f"尝试扩展选择器 {i+1}/{len(extended_selectors)}: {selector} ({account_label})")
                                download_btn = row.ele(selector, timeout=1)
                                if download_btn:
                                    btn_text = download_btn.text.strip()
                                    btn_onclick = download_btn.attr('onclick') or ''
                                    self.logger.info(f"扩展选择器找到下载按钮: {selector}, 文本: '{btn_text}' ({account_label})")
                                    break
                            except Exception as e:
                                self.logger.debug(f"扩展选择器 {selector} 失败: {e} ({account_label})")
                                continue
                        
                        # 第二步：如果仍未找到，分析行内所有链接
                        if not download_btn:
                            self.logger.debug(f"扩展选择器也未找到，分析行内所有链接 ({account_label})")
                            try:
                                all_links = row.eles("tag:a")
                                self.logger.debug(f"行内共找到 {len(all_links)} 个链接 ({account_label})")
                                
                                # 智能分析链接，按优先级排序
                                potential_downloads = []
                                
                                for j, link in enumerate(all_links):
                                    try:
                                        link_text = link.text.strip()
                                        link_onclick = link.attr('onclick') or ''
                                        link_href = link.attr('href') or ''
                                        link_style = link.attr('style') or ''
                                        
                                        # 计算下载可能性分数
                                        score = 0
                                        reasons = []
                                        
                                        if 'downloadfiles' in link_onclick:
                                            score += 100
                                            reasons.append("包含downloadfiles函数")
                                        if '下载' in link_text:
                                            score += 50
                                            reasons.append("文本包含'下载'")
                                        if 'download' in link_onclick.lower():
                                            score += 30
                                            reasons.append("onclick包含download")
                                        if 'color:blue' in link_style:
                                            score += 20
                                            reasons.append("蓝色链接样式")
                                        if 'cursor: pointer' in link_style or 'cursor:pointer' in link_style:
                                            score += 15
                                            reasons.append("指针样式")
                                        if link_onclick and not link_href:
                                            score += 10
                                            reasons.append("有onclick无href")
                                        
                                        if score > 0:
                                            potential_downloads.append({
                                                'link': link,
                                                'score': score,
                                                'text': link_text,
                                                'onclick': link_onclick[:50],
                                                'reasons': reasons,
                                                'index': j + 1
                                            })
                                            
                                        self.logger.debug(f"链接 {j+1}: 文本='{link_text}', 分数={score}, 原因={reasons} ({account_label})")
                                        
                                    except Exception as link_e:
                                        self.logger.debug(f"分析链接 {j+1} 失败: {link_e} ({account_label})")
                                        continue
                                
                                # 按分数排序，选择最可能的下载链接
                                if potential_downloads:
                                    potential_downloads.sort(key=lambda x: x['score'], reverse=True)
                                    best_candidate = potential_downloads[0]
                                    
                                    if best_candidate['score'] >= 50:  # 高可信度
                                        download_btn = best_candidate['link']
                                        self.logger.info(f"智能选择下载链接 {best_candidate['index']}: 分数={best_candidate['score']}, 原因={best_candidate['reasons']} ({account_label})")
                                    else:
                                        # 低可信度时记录候选项但不自动选择
                                        self.logger.warning(f"找到可能的下载链接但可信度较低: 分数={best_candidate['score']}, 链接={best_candidate['index']}, 原因={best_candidate['reasons']} ({account_label})")
                                        # 可以选择最佳候选或跳过
                                        download_btn = best_candidate['link']  # 尝试使用最佳候选
                                else:
                                    self.logger.warning(f"行内未找到任何潜在的下载链接 ({account_label})")
                                    
                            except Exception as e:
                                self.logger.error(f"智能分析行内链接时出错: {e} ({account_label})")
                        
                        # 第三步：如果还是没找到，等待页面动态加载
                        if not download_btn:
                            self.logger.info(f"静态分析未找到下载按钮，等待页面动态加载 ({account_label})")
                            max_wait_time = 10  # 最多等待10秒
                            wait_interval = 2   # 每2秒检查一次
                            waited_time = 0
                            
                            while waited_time < max_wait_time and not download_btn:
                                time.sleep(wait_interval)
                                waited_time += wait_interval
                                
                                # 重新尝试主要选择器
                                for selector in download_selectors[:3]:  # 只尝试前3个最可能的选择器
                                    try:
                                        download_btn = row.ele(selector, timeout=1)
                                        if download_btn:
                                            self.logger.info(f"等待{waited_time}秒后找到下载按钮: {selector} ({account_label})")
                                            break
                                    except:
                                        continue
                                
                                if download_btn:
                                    break
                                    
                                self.logger.debug(f"等待下载按钮加载... ({waited_time}/{max_wait_time}秒) ({account_label})")
                            
                            if not download_btn:
                                self.logger.warning(f"等待{max_wait_time}秒后仍未找到下载按钮 ({account_label})")
                    
                    if download_btn:
                        self.logger.info(f"准备点击下载按钮 ({account_label}): {time_str}")
                        try:
                            # 获取点击前下载目录中的文件列表
                            before_files = set()
                            if download_dir.exists():
                                before_files = {f.name for f in download_dir.iterdir() if f.is_file()}
                            
                            self.logger.debug(f"下载前目录中有 {len(before_files)} 个文件 ({account_label})")
                            
                            # 点击下载按钮
                            download_btn.click()
                            self.logger.info(f"成功点击下载按钮 ({account_label}): {time_str}")
                            
                            # 等待下载完成，最多等待60秒（文件可能较大）
                            download_timeout = 60
                            wait_interval = 1
                            waited_time = 0
                            new_file_found = False
                            actual_downloaded_file = None
                            
                            while waited_time < download_timeout and not new_file_found:
                                time.sleep(wait_interval)
                                waited_time += wait_interval
                                
                                # 检查是否有新文件
                                if download_dir.exists():
                                    current_files = {f.name for f in download_dir.iterdir() if f.is_file()}
                                    new_files = current_files - before_files
                                    
                                    if new_files:
                                        # 检查是否有完成下载的文件（非.crdownload文件）
                                        completed_files = [f for f in new_files if not f.endswith('.crdownload')]
                                        downloading_files = [f for f in new_files if f.endswith('.crdownload')]
                                        
                                        if completed_files:
                                            # 找到已完成下载的文件
                                            new_file_name = completed_files[0]
                                            actual_downloaded_file = download_dir / new_file_name
                                            self.logger.info(f"检测到下载完成的文件: {new_file_name} ({account_label})")
                                            new_file_found = True
                                            break
                                        elif downloading_files:
                                            # 文件正在下载中，继续等待
                                            if waited_time % 5 == 0:  # 每5秒记录一次
                                                self.logger.info(f"文件正在下载中: {downloading_files[0]}，继续等待... ({account_label})")
                                
                                if waited_time % 10 == 0:  # 每10秒记录一次等待状态
                                    self.logger.debug(f"等待下载完成... 已等待 {waited_time}秒 ({account_label})")
                            
                            if new_file_found and actual_downloaded_file:
                                # 根据需求，将文件名改为时间戳格式，但保持原文件扩展名
                                original_suffix = actual_downloaded_file.suffix
                                timestamp_name = time_str.replace(':', '-').replace(' ', '_')  # 替换不合法的文件名字符
                                new_file_name = f"{timestamp_name}{original_suffix}"
                                new_file_path = download_dir / new_file_name
                                
                                # 重命名文件 - 处理文件名冲突
                                try:
                                    # 如果目标文件已存在，添加数字后缀
                                    counter = 1
                                    original_new_file_path = new_file_path
                                    while new_file_path.exists():
                                        name_without_ext = timestamp_name
                                        new_file_name = f"{name_without_ext}_{counter}{original_suffix}"
                                        new_file_path = download_dir / new_file_name
                                        counter += 1
                                        if counter > 100:  # 防止无限循环
                                            self.logger.warning(f"重命名尝试次数过多，使用原文件名 ({account_label})")
                                            new_file_path = actual_downloaded_file
                                            break
                                    
                                    if new_file_path != actual_downloaded_file:
                                        actual_downloaded_file.rename(new_file_path)
                                        self.logger.info(f"文件重命名成功: {actual_downloaded_file.name} -> {new_file_name} ({account_label})")
                                    else:
                                        self.logger.info(f"使用原文件名: {actual_downloaded_file.name} ({account_label})")
                                    
                                    # 记录成功下载的文件
                                    downloaded_file_paths.append(str(new_file_path))
                                    self.downloaded_files.append(time_str)
                                    download_count += 1
                                    
                                except Exception as rename_e:
                                    self.logger.error(f"文件重命名失败 ({account_label}): {rename_e}")
                                    # 即使重命名失败，也记录原文件
                                    downloaded_file_paths.append(str(actual_downloaded_file))
                                    self.downloaded_files.append(time_str)
                                    download_count += 1
                            else:
                                self.logger.warning(f"等待 {download_timeout} 秒后未检测到新下载的文件 ({account_label}): {time_str}")
                                
                        except Exception as e:
                            self.logger.error(f"点击下载按钮失败 ({account_label}) {time_str}: {str(e)}")
                    else:
                        self.logger.warning(f"找不到下载按钮 ({account_label}): {time_str}")
                        # 输出更详细的行结构用于调试
                        try:
                            cells = row.eles("tag:td")
                            if len(cells) >= 7:  # 下载按钮应该在第7列
                                download_cell = cells[6]  # 索引6是第7列
                                cell_html = download_cell.html[:500]  # 获取单元格HTML
                                self.logger.debug(f"下载单元格HTML: {cell_html} ({account_label})")
                        except Exception as cell_e:
                            self.logger.debug(f"获取下载单元格信息失败: {cell_e} ({account_label})")
                        
                except Exception as e:
                    self.logger.error(f"下载文件失败 ({account_label}) {time_str}: {str(e)}")
            
            # 更新最后检查时间
            if new_files:
                try:
                    # new_files 是 (time_str, txt_file_path, row) 的列表
                    time_strings = [f[0] for f in new_files]  # 提取时间字符串
                    valid_times = []
                    
                    for time_str in time_strings:
                        # 添加基本验证
                        if not time_str or len(time_str) < 10 or not any(char.isdigit() for char in time_str):
                            self.logger.debug(f"跳过无效时间字符串: '{time_str}' ({account_label})")
                            continue
                        
                        try:
                            parsed_time = datetime.strptime(time_str, '%Y-%m-%d %H:%M:%S')
                            valid_times.append(parsed_time)
                        except ValueError as parse_e:
                            # 尝试其他格式
                            alternative_formats = [
                                '%Y/%m/%d %H:%M:%S',
                                '%m/%d/%Y %H:%M:%S', 
                                '%Y-%m-%d',
                                '%Y/%m/%d'
                            ]
                            parsed_alternative = False
                            for fmt in alternative_formats:
                                try:
                                    parsed_time = datetime.strptime(time_str, fmt)
                                    valid_times.append(parsed_time)
                                    parsed_alternative = True
                                    break
                                except ValueError:
                                    continue
                            
                            if not parsed_alternative:
                                self.logger.warning(f"无法解析时间字符串 '{time_str}': {parse_e} ({account_label})")
                                continue
                    
                    if valid_times:
                        latest_time = max(valid_times)
                        self.zd_flag_time = latest_time
                        self.logger.info(f"更新最后检查时间 ({account_label}): {latest_time}")
                    else:
                        self.logger.warning(f"没有有效的时间字符串可以解析 ({account_label})")
                        
                except Exception as time_e:
                    self.logger.error(f"更新最后检查时间失败 ({account_label}): {time_e}")
            
            self.logger.info(f"下载过程完成 ({account_label}): 成功下载 {download_count}/{len(new_files)} 个文件")
            return downloaded_file_paths
            
        except Exception as e:
            self.logger.error(f"下载文件过程失败 ({account_label}): {str(e)}")
            return []
    
    def handle_jx_website(self, downloaded_files_list):
        """处理警信网站"""
        try:
            # 使用实际下载的文件列表
            if not downloaded_files_list:
                self.logger.info("没有需要上传的文件")
                return True

            self.logger.info(f"准备上传 {len(downloaded_files_list)} 个文件到警信网站")
            
            # 读取已上传文件记录
            uploaded_record_file = Path("uploaded_jx_files.txt")
            if uploaded_record_file.exists():
                with open(uploaded_record_file, 'r', encoding='utf-8') as f:
                    uploaded_files = set(line.strip() for line in f if line.strip())
            else:
                uploaded_files = set()

            # 过滤出未上传过的文件
            files_to_upload_final = []
            for file_path in downloaded_files_list:
                file_name = Path(file_path).name
                if file_name not in uploaded_files:
                    files_to_upload_final.append(file_path)
                else:
                    self.logger.info(f"文件已上传过，跳过: {file_name}")

            if not files_to_upload_final:
                self.logger.info("所有文件都已上传过，无需重复上传")
                return True
            
            self.logger.info(f"实际需要上传的文件数量: {len(files_to_upload_final)}")

            # 2-0 打开警信网址
            self.logger.info("正在访问警信网站...")
            self.tab.get("https://10.2.120.214:10242/#/login")
            time.sleep(5)
            
            
            # 2-1 输入身份证号和密码
            id_card = self.config.get("jx_id_card")
            password = self.config.get("jx_password")
            
            if not id_card or not password:
                self.logger.error("警信网站身份证号或密码未配置")
                return False
            
            self.logger.info("正在输入警信登录信息...")
            
            # 等待页面完全加载
            time.sleep(3)
            self.logger.info(f"当前页面URL: {self.tab.url}")
            
            # 查找登录输入框
            id_input = None
            pwd_input = None
            
            # 等待页面元素完全加载
            self.logger.info("等待页面元素完全加载...")
            time.sleep(8)
            
            # 使用经过验证的成功方法：通过索引直接获取输入框
            self.logger.info("通过索引获取登录输入框...")
            try:
                all_inputs = self.tab.eles("tag:input")
                self.logger.info(f"页面中找到 {len(all_inputs)} 个input元素")
                
                if len(all_inputs) >= 5:  # 确保有足够的input元素
                    id_input = all_inputs[3]  # Input 3是身份证号
                    pwd_input = all_inputs[4]  # Input 4是密码
                    self.logger.info("通过索引3找到身份证号输入框")
                    self.logger.info("通过索引4找到密码输入框")
                else:
                    self.logger.warning(f"页面input元素数量不足: {len(all_inputs)}")
                    
            except Exception as e:
                self.logger.error(f"通过索引获取输入框失败: {e}")
            
            # 如果找不到输入框，循环等待最长2分钟
            if not id_input or not pwd_input:
                self.logger.warning("初次未找到身份证号或密码输入框，开始循环等待...")
                max_wait_time = 120  # 2分钟
                wait_interval = 5    # 每5秒检查一次
                waited_time = 0
                
                while waited_time < max_wait_time and (not id_input or not pwd_input):
                    self.logger.info(f"等待输入框加载... ({waited_time}/{max_wait_time}秒)")
                    time.sleep(wait_interval)
                    waited_time += wait_interval
                    
                    # 重新查找输入框
                    try:
                        if not id_input:
                            id_input = self.tab.ele("t:input@@placeholder=请输入身份证号", timeout=2)
                        if not pwd_input:
                            pwd_input = self.tab.ele("t:input@@placeholder=请输入密码", timeout=2)
                        
                        if id_input and pwd_input:
                            self.logger.info(f"成功找到输入框 (等待了{waited_time}秒)")
                            break
                            
                    except Exception as e:
                        self.logger.debug(f"重新查找输入框失败: {e}")
                        continue
                
                # 最终检查
                if not id_input or not pwd_input:
                    self.logger.error(f"等待{max_wait_time}秒后仍未找到输入框")
                    # 输出页面信息用于调试
                    try:
                        page_html = self.tab.html[:2000]  # 获取页面前2000个字符
                        self.logger.debug(f"页面HTML片段: {page_html}")
                        
                        # 查找所有input元素
                        all_inputs = self.tab.eles("tag:input")
                        self.logger.info(f"页面中总共找到 {len(all_inputs)} 个input元素")
                        for i, inp in enumerate(all_inputs):
                            try:
                                inp_type = inp.attr('type') or '无type'
                                inp_placeholder = inp.attr('placeholder') or '无placeholder'
                                inp_class = inp.attr('class') or '无class'
                                self.logger.info(f"Input {i}: type={inp_type}, placeholder={inp_placeholder}, class={inp_class}")
                            except Exception as e:
                                self.logger.info(f"Input {i}: 获取属性失败 - {e}")
                    except Exception as e:
                        self.logger.error(f"获取调试信息失败: {e}")
                    return False
            
            id_input.clear()
            id_input.input(id_card)
            pwd_input.clear()
            pwd_input.input(password)
            time.sleep(2)
            # 2-2 点击登录
            login_btn = self.tab.ele("t:button@@class=el-button el-button--primary@@tx():登录")
            if not login_btn:
                self.logger.error("找不到登录按钮")
                return False
            
            login_btn.click()
            self.logger.info("已点击登录按钮")
            time.sleep(10)
            
            # 循环等待页面跳转，最长等待5分钟
            max_wait_time = 300  
            check_interval = 10  # 每10秒检查一次
            start_time = time.time()
            
            self.logger.info("开始等待页面跳转到主页...")
            while time.time() - start_time < max_wait_time:
                current_url = self.tab.url
                self.logger.info(f"当前页面URL: {current_url}")
                
                if "home/chat" in current_url:
                    elapsed_time = int(time.time() - start_time)
                    self.logger.info(f"成功跳转到主页，耗时: {elapsed_time}秒")
                    break
                else:
                    elapsed_time = int(time.time() - start_time)
                    remaining_time = max_wait_time - elapsed_time
                    self.logger.info(f"尚未跳转到主页，已等待: {elapsed_time}秒，剩余等待时间: {remaining_time}秒")
                    time.sleep(check_interval)
            else:
                # 循环结束但仍未跳转成功
                total_wait_time = int(time.time() - start_time)
                self.logger.error(f"等待{total_wait_time}秒后仍未跳转到正确页面，当前URL: {self.tab.url}")
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
            upload_success = self.upload_files(files_to_upload_final, uploaded_record_file, uploaded_files)
            return upload_success
            
        except Exception as e:
            self.logger.error(f"处理警信网站失败: {str(e)}")
            return False

    def upload_files(self, files_to_upload, uploaded_record_file=None, uploaded_files=None):
        """上传文件到警信"""
        try:
            upload_count = 0
            uploaded_names = set(uploaded_files) if uploaded_files else set()
            
            for file_path in files_to_upload:
                if not os.path.exists(file_path):
                    self.logger.warning(f"文件不存在: {file_path}")
                    continue
                    
                file_name = Path(file_path).name
                self.logger.info(f"准备上传文件: {file_name}")
                
                try:
                    # 第一步：查找发送文件按钮
                    send_file_btn = self.tab.ele("t:i@@class=icon iconfont icon-wenjian")
                    if not send_file_btn:
                        self.logger.error("找不到发送文件按钮")
                        continue
                    
                    # 第二步：预先设置要上传的文件路径（这会让DrissionPage准备好处理文件对话框）
                    self.logger.info("设置文件上传路径...")
                    self.tab.set.upload_files(file_path)
                    time.sleep(1)
                    
                    # 第三步：点击发送文件按钮，这会弹出系统文件选择对话框
                    self.logger.info("点击发送文件按钮，准备处理系统文件选择对话框...")
                    send_file_btn.click()
                    
                    # 第四步：等待文件路径被自动填入（DrissionPage会自动处理系统对话框）
                    self.logger.info("等待系统文件选择对话框处理完成...")
                    try:
                        # 等待文件路径填入完成，不使用timeout参数
                        self.tab.wait.upload_paths_inputted()
                        self.logger.info("文件路径已成功填入系统对话框")
                    except Exception as wait_e:
                        self.logger.warning(f"等待文件路径填入超时: {wait_e}")
                        # 即使超时也继续尝试，可能已经成功了
                    
                    # 给系统对话框处理一些时间
                    time.sleep(3)
                    
                    # 第五步：查找并点击确认/发送按钮
                    self.logger.info("查找确认发送按钮...")
                    
                    # 使用DrissionPage优化的选择器语法
                    confirm_selectors = [
                        # 第一种：简化路径 - 直接定位到button元素
                        "xpath:/html/body/div[2]/div/div[3]/button[2]",
                        # 第二种：完整路径 - 直接定位到button元素  
                        "xpath:/html/body[@class='el-popup-parent--hidden']/div[@class='el-message-box__wrapper']/div[@class='el-message-box el-message-box--center']/div[@class='el-message-box__btns']/button[@class='el-button el-button--default el-button--small el-button--primary ']",
                        # 备用：使用原始XPath到span，然后获取父元素
                        "/html/body/div[2]/div/div[3]/button[2]/span",
                        "/html/body[@class='el-popup-parent--hidden']/div[@class='el-message-box__wrapper']/div[@class='el-message-box el-message-box--center']/div[@class='el-message-box__btns']/button[@class='el-button el-button--default el-button--small el-button--primary ']/span"
                    ]
                    
                    confirm_btn = None
                    used_selector = None
                    
                    # 尝试找到确认按钮
                    for i, selector in enumerate(confirm_selectors):
                        try:
                            self.logger.debug(f"尝试确认按钮选择器 {i+1}/{len(confirm_selectors)}: {selector}")
                            
                            if i < 2:  # 前两个是直接定位button的选择器
                                btn = self.tab.ele(selector, timeout=3)
                                if btn and btn.tag == 'button':
                                    if btn.states.is_displayed and btn.states.is_enabled:
                                        confirm_btn = btn
                                        used_selector = selector
                                        self.logger.info(f"找到可用的确认按钮 (直接定位): {selector}")
                                        break
                                    else:
                                        self.logger.debug(f"找到按钮但不可用: {selector} (显示:{btn.states.is_displayed}, 启用:{btn.states.is_enabled})")
                                else:
                                    self.logger.debug(f"未找到button元素: {selector}")
                            else:  # 后两个是定位span的选择器，需要获取父元素
                                span_element = self.tab.ele(selector, timeout=3)
                                if span_element:
                                    # 获取span的父元素button
                                    btn = span_element.parent()
                                    if btn and btn.tag == 'button':
                                        if btn.states.is_displayed and btn.states.is_enabled:
                                            confirm_btn = btn
                                            used_selector = selector
                                            self.logger.info(f"找到可用的确认按钮 (通过span): {selector}")
                                            break
                                        else:
                                            self.logger.debug(f"找到按钮但不可用: {selector} (显示:{btn.states.is_displayed}, 启用:{btn.states.is_enabled})")
                                    else:
                                        self.logger.debug(f"span父元素不是button: {selector}")
                                else:
                                    self.logger.debug(f"未找到span元素: {selector}")
                        except Exception as e:
                            self.logger.debug(f"选择器 {selector} 查找失败: {e}")
                            continue
                    
                    # 第六步：点击确认按钮
                    if confirm_btn:
                        try:
                            self.logger.info(f"准备点击确认按钮 (选择器: {used_selector})")
                            
                            # 等待一段时间让弹窗完全显示
                            time.sleep(1.5)
                            
                            # 直接点击按钮
                            confirm_btn.click()
                            click_success = True
                            self.logger.info("确认按钮点击成功")
                            
                            if click_success:
                                # 简化验证：检查el-message-box消失
                                self.logger.info("确认按钮点击成功，验证文件发送状态...")
                                
                                upload_verified = False
                                dialog_disappeared = False
                                
                                # 等待el-message-box消失
                                for wait_count in range(8):
                                    time.sleep(1)
                                    try:
                                        # 检查警信特有的消息框结构
                                        message_boxes = self.tab.eles("//div[@class='el-message-box__wrapper']")
                                        visible_boxes = [box for box in message_boxes if box.states.is_displayed]
                                        
                                        if not visible_boxes:
                                            dialog_disappeared = True
                                            self.logger.info(f"消息框已消失 (等待了{wait_count + 1}秒)")
                                            break
                                        else:
                                            self.logger.debug(f"消息框仍可见，继续等待... ({wait_count + 1}/8秒)")
                                    except Exception as e:
                                        self.logger.debug(f"检查消息框状态失败: {e}")
                                        continue
                                
                                if dialog_disappeared:
                                    # 等待文件处理
                                    self.logger.info("消息框已消失，等待文件处理完成...")
                                    time.sleep(3)
                                    
                                    # 检查聊天消息（根据警信HTML结构）
                                    try:
                                        chat_messages = self.tab.eles("//li[@class='messageBG']")
                                        if chat_messages and len(chat_messages) > 0:
                                            latest_msg = chat_messages[-1]
                                            try:
                                                latest_html = latest_msg.html
                                                if ('docx' in latest_html.lower() or 
                                                    'xls' in latest_html.lower() or 
                                                    'zip' in latest_html.lower() or
                                                    'attachment' in latest_html.lower() or
                                                    'file' in latest_html.lower() or
                                                    '文件' in latest_html or
                                                    '附件' in latest_html):
                                                    upload_verified = True
                                                    self.logger.info(f"在聊天框中发现文件消息: {file_name}")
                                            except Exception as msg_check_e:
                                                self.logger.debug(f"检查最新消息失败: {msg_check_e}")
                                    except Exception as chat_check_e:
                                        self.logger.debug(f"检查聊天消息失败: {chat_check_e}")
                                    
                                    # 记录上传状态
                                    upload_count += 1
                                    uploaded_names.add(file_name)
                                    if upload_verified:
                                        self.logger.info(f"文件上传验证成功: {file_name}")
                                    else:
                                        self.logger.info(f"文件上传成功: {file_name} (确认对话框已消失，文件已成功上传)")
                                else:
                                    self.logger.error(f"消息框未消失，可能确认按钮点击失败: {file_name}")
                            else:
                                self.logger.error(f"所有点击方式都失败，无法确认上传: {file_name}")
                                
                        except Exception as click_e:
                            self.logger.error(f"点击确认按钮时出错: {click_e}")
                    else:
                        self.logger.error("未找到确认按钮，文件上传失败")
                    
                    # 每次上传后稍作等待
                    time.sleep(2)
                    
                except Exception as upload_e:
                    self.logger.error(f"上传文件 {file_name} 时发生错误: {upload_e}")
                    continue
            
            # 上传完成后，记录已上传文件名
            if uploaded_record_file and uploaded_names:
                try:
                    with open(uploaded_record_file, 'w', encoding='utf-8') as f:
                        for name in uploaded_names:
                            f.write(name + '\n')
                    self.logger.info(f"已记录上传文件到: {uploaded_record_file}")
                except Exception as record_e:
                    self.logger.warning(f"记录上传文件失败: {record_e}")
            
            self.logger.info(f"本次上传完成，成功上传文件数量: {upload_count}")
            return upload_count > 0
            
        except Exception as e:
            self.logger.error(f"上传文件过程中发生严重错误: {str(e)}")
            return False 