# ============================================================
# UI 页面基类（精简版：只对关键操作截图）
# 截图时机：导航、点击、输入、断言（去除纯读取/等待操作）
# ============================================================
import allure
import time
from playwright.sync_api import Page, expect
from common.logger import logger
from config.settings import UI_TIMEOUT


class UIBasePage:
    """所有页面对象的父类，关键步骤自动截图"""

    def __init__(self, page: Page, test_name: str = None, test_status: str = "成功"):
        self.page = page
        self.test_name = test_name or "unknown"
        self.test_status = test_status

    # ---------- 内部方法：关键操作截图 ----------
    def _step_screenshot(self, step_desc: str):
        """保存关键步骤截图到用例专属文件夹，并挂载到 Allure"""
        try:
            from ui_tests.conftest import save_step_screenshot
            screenshot_path = save_step_screenshot(
                self.page,
                self.test_name,
                self.test_status,
                step_desc
            )
            if screenshot_path and screenshot_path.exists():
                with open(screenshot_path, "rb") as f:
                    allure.attach(
                        f.read(),
                        name=f"📸 {step_desc}",
                        attachment_type=allure.attachment_type.PNG
                    )
        except Exception as e:
            logger.debug(f"步骤截图失败: {e}")

    # ---------- 导航（保留截图） ----------
    @allure.step("打开页面: {url}")
    def navigate_to(self, url: str, timeout: int = None):
        if timeout is None:
            timeout = UI_TIMEOUT
        logger.info(f"导航到: {url}")
        self.page.goto(url, timeout=timeout * 1000)
        self.page.wait_for_load_state("networkidle")
        self._step_screenshot(f"导航到 {url[:50]}")
        return self

    # ---------- 等待（去掉截图） ----------
    @allure.step("等待元素可见: {selector}")
    def wait_for_element(self, selector: str, timeout: int = None):
        if timeout is None:
            timeout = UI_TIMEOUT
        logger.debug(f"等待元素: {selector}")
        self.page.wait_for_selector(selector, state="visible", timeout=timeout * 1000)
        # 去掉截图
        return self

    # ---------- 点击（保留截图） ----------
    @allure.step("点击元素: {selector}")
    def click(self, selector: str, timeout: int = None):
        if timeout is None:
            timeout = UI_TIMEOUT
        logger.info(f"点击元素: {selector}")
        self.page.click(selector, timeout=timeout * 1000)
        self._step_screenshot(f"点击 {selector[:30]}")
        return self

    # ---------- 输入（保留截图） ----------
    @allure.step("输入文本: {selector} = {text}")
    def fill(self, selector: str, text: str, timeout: int = None):
        if timeout is None:
            timeout = UI_TIMEOUT
        logger.info(f"输入文本: {selector} -> '{text}'")
        self.page.fill(selector, text, timeout=timeout * 1000)
        self._step_screenshot(f"输入 {text[:20]}...")
        return self

    # ---------- 获取文本（去掉截图） ----------
    @allure.step("获取文本: {selector}")
    def get_text(self, selector: str) -> str:
        text = self.page.text_content(selector)
        logger.debug(f"获取文本: {selector} -> '{text}'")
        # 去掉截图
        return text

    # ---------- 获取属性（去掉截图） ----------
    @allure.step("获取属性: {selector} -> {attribute}")
    def get_attribute(self, selector: str, attribute: str) -> str:
        value = self.page.get_attribute(selector, attribute)
        logger.debug(f"获取属性: {selector}@{attribute} -> '{value}'")
        # 去掉截图
        return value

    # ---------- 断言（保留截图） ----------
    @allure.step("验证页面标题: {expected}")
    def assert_title(self, expected: str):
        logger.info(f"验证页面标题: {expected}")
        expect(self.page).to_have_title(expected)
        self._step_screenshot(f"验证标题")
        return self

    @allure.step("验证 URL 包含: {expected}")
    def assert_url_contains(self, expected: str):
        logger.info(f"验证 URL 包含: {expected}")
        expect(self.page).to_have_url(expected)
        self._step_screenshot(f"验证URL")
        return self

    @allure.step("验证元素可见: {selector}")
    def assert_visible(self, selector: str):
        logger.info(f"验证元素可见: {selector}")
        expect(self.page.locator(selector)).to_be_visible()
        self._step_screenshot(f"验证元素可见")
        return self

    @allure.step("验证元素文本: {selector} = {expected}")
    def assert_text(self, selector: str, expected: str):
        logger.info(f"验证元素文本: {selector} -> '{expected}'")
        expect(self.page.locator(selector)).to_have_text(expected)
        self._step_screenshot(f"验证文本")
        return self

    # ---------- 主动截图 ----------
    @allure.step("主动截图: {name}")
    def screenshot(self, name: str = "screenshot"):
        logger.info(f"主动截图: {name}")
        self._step_screenshot(name)
        return self

    # ---------- 强制等待 ----------
    def wait(self, seconds: int):
        logger.warning(f"强制等待 {seconds} 秒")
        time.sleep(seconds)
        return self