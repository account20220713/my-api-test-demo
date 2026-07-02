# ============================================================
# Sauce Demo 登录页面对象
# URL: https://www.saucedemo.com/
# ============================================================
import allure
from common.ui_base import UIBasePage
from config.settings import UI_BASE_URL

class LoginPage(UIBasePage):
    """Sauce Demo 登录页面"""

    # ---------- 定位器 ----------
    USERNAME_INPUT = "#user-name"                 # 用户名输入框
    PASSWORD_INPUT = "#password"                  # 密码输入框
    LOGIN_BUTTON = "#login-button"                # 登录按钮
    ERROR_MESSAGE = "[data-test='error']"         # 错误提示
    BOT_IMAGE = ".bot_column"                     # 页面装饰图（用于判断页面加载）

    def __init__(self, page, base_url: str = UI_BASE_URL):
        super().__init__(page)
        self.base_url = base_url

    @allure.step("打开 Sauce Demo 登录页面")
    def open(self):
        """打开登录页面"""
        self.navigate_to(self.base_url)
        self.wait_for_element(self.USERNAME_INPUT)  # 等待输入框可见
        return self

    @allure.step("登录: {username}")
    def login(self, username: str, password: str):
        """执行登录操作"""
        self.fill(self.USERNAME_INPUT, username)
        self.fill(self.PASSWORD_INPUT, password)
        self.click(self.LOGIN_BUTTON)
        return self

    @allure.step("验证登录成功（跳转到商品页）")
    def assert_login_success(self):
        """验证登录成功：URL 包含 /inventory.html"""
        self.page.wait_for_url("**/inventory.html", timeout=10000)
        return self

    @allure.step("验证登录失败，显示错误信息")
    def assert_login_failed(self, expected_error: str = None):
        """验证登录失败：检查错误提示"""
        self.wait_for_element(self.ERROR_MESSAGE)
        error_text = self.get_text(self.ERROR_MESSAGE)
        if expected_error:
            assert expected_error in error_text, \
                f"期望错误包含 '{expected_error}'，实际为 '{error_text}'"
        return self