# ============================================================
# Sauce Demo 登录测试用例（Allure 报告优化版）
# ============================================================
import sys
import pytest
import allure
from ui_tests.page_objects.inventory_page import InventoryPage
from common.logger import logger


def print_test_info(test_name: str, expected: str, account: str):
    """控制台打印测试用例信息（保留）"""
    msg = (
            "\n" + "═" * 70 + "\n"
                              f"🧪 {test_name}\n"
                              f"📝 预期: {expected}\n"
                              f"🔑 账号: {account}\n"
                              "═" * 70 + "\n"
    )
    print(msg, flush=True)


@allure.epic("Sauce Demo 电商平台")
@allure.feature("用户登录")
class TestLogin:

    @allure.story("正常登录")
    @allure.title("✅ 标准用户登录成功")
    @allure.description("""
    **测试目标**：验证标准用户 (standard_user) 能够正常登录

    **前置条件**：Sauce Demo 网站可访问

    **测试步骤**：
    1. 打开登录页面
    2. 输入用户名 standard_user
    3. 输入密码 secret_sauce
    4. 点击登录按钮

    **预期结果**：登录成功，跳转到商品列表页，页面标题显示 "Products"
    """)
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "login", "positive")
    def test_login_success(self, login_page):
        print_test_info(
            "标准用户登录",
            "登录成功 → 跳转到商品列表页 → 显示 Products",
            "standard_user / secret_sauce"
        )

        login_page.open()
        login_page.login("standard_user", "secret_sauce")
        login_page.assert_login_success()

        inventory = InventoryPage(login_page.page)
        inventory.assert_loaded()

        print("✅ 测试通过：标准用户登录成功\n", flush=True)
        logger.info("✅ 测试通过：标准用户登录成功")

    @allure.story("登录异常")
    @allure.title("❌ 错误密码登录失败")
    @allure.description("""
    **测试目标**：验证错误密码登录失败

    **测试步骤**：
    1. 打开登录页面
    2. 输入用户名 standard_user
    3. 输入错误密码 wrong_password
    4. 点击登录按钮

    **预期结果**：登录失败，显示错误提示 "Username and password do not match"
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("login", "negative")
    def test_login_wrong_password(self, login_page):
        print_test_info(
            "错误密码登录",
            "登录失败 → 显示错误提示",
            "standard_user / wrong_password"
        )

        login_page.open()
        login_page.login("standard_user", "wrong_password")
        login_page.assert_login_failed("Username and password do not match")
        print("✅ 测试通过：错误密码被正确拦截\n", flush=True)

    @allure.story("登录异常")
    @allure.title("❌ 空用户名登录失败")
    @allure.description("""
    **测试目标**：验证空用户名登录失败

    **测试步骤**：
    1. 打开登录页面
    2. 不输入用户名
    3. 输入密码 secret_sauce
    4. 点击登录按钮

    **预期结果**：登录失败，显示错误提示 "Username is required"
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("login", "negative")
    def test_login_empty_username(self, login_page):
        print_test_info(
            "空用户名登录",
            "登录失败 → 显示 'Username is required'",
            "(空) / secret_sauce"
        )

        login_page.open()
        login_page.login("", "secret_sauce")
        login_page.assert_login_failed("Username is required")
        print("✅ 测试通过：空用户名被正确拦截\n", flush=True)

    @allure.story("登录异常")
    @allure.title("❌ 锁定用户登录失败")
    @allure.description("""
    **测试目标**：验证被锁定的用户登录失败

    **测试步骤**：
    1. 打开登录页面
    2. 输入用户名 locked_out_user
    3. 输入密码 secret_sauce
    4. 点击登录按钮

    **预期结果**：登录失败，显示错误提示 "Sorry, this user has been locked out"
    """)
    @allure.severity(allure.severity_level.NORMAL)
    @allure.tag("login", "negative")
    def test_login_locked_user(self, login_page):
        print_test_info(
            "锁定用户登录",
            "登录失败 → 显示 'Sorry, this user has been locked out'",
            "locked_out_user / secret_sauce"
        )

        login_page.open()
        login_page.login("locked_out_user", "secret_sauce")
        login_page.assert_login_failed("locked out")
        print("✅ 测试通过：锁定用户被正确拦截\n", flush=True)

    # ========== 🚨 失败用例（演示截图和录屏） ==========

    @allure.story("失败演示")
    @allure.title("❌ 错误断言演示（预期失败）")
    @allure.description("""
    **测试目的**：演示测试失败时的截图和录屏能力

    **测试步骤**：
    1. 正常登录
    2. 断言 1 == 2（故意失败）

    **预期结果**：测试失败，自动生成截图和录屏
    """)
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.tag("demo", "fail")
    # 把 def test_fail_wrong_assertion(self, login_page): 改为：
    def test_fail_wrong_assertion(self, logged_in_page):
        # 内部直接使用 logged_in_page，不再需要登录
        # 示例：
        inventory = InventoryPage(logged_in_page)
        inventory.assert_loaded()
        assert 1 == 2, "故意失败"

    # 同样修改 test_fail_element_not_found、test_fail_wrong_login、test_fail_parametrized
    # 将它们的参数从 login_page 改为 logged_in_page

    @allure.story("失败演示")
    @allure.title("❌ 元素未找到演示（预期失败）")
    @allure.description("""
    **测试目的**：演示页面元素找不到时的截图和录屏能力

    **测试步骤**：
    1. 正常登录
    2. 尝试查找不存在的元素 .non-existent-element

    **预期结果**：超时失败，自动生成截图和录屏
    """)
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.tag("demo", "fail")
    def test_fail_element_not_found(self, login_page):
        print_test_info(
            "❌ 元素未找到演示",
            "预期失败 → 验证截图和录屏是否生成",
            "standard_user / secret_sauce"
        )

        login_page.open()
        login_page.login("standard_user", "secret_sauce")
        login_page.assert_login_success()

        print("🚨 故意查找不存在的元素：.non-existent-element", flush=True)
        login_page.page.locator(".non-existent-element").wait_for(timeout=3000)

    @allure.story("失败演示")
    @allure.title("❌ 错误账号登录（预期失败）")
    @allure.description("""
    **测试目的**：使用无效账号登录，但断言成功，导致失败

    **测试步骤**：
    1. 打开登录页面
    2. 输入无效用户名 invalid_user / wrong_password
    3. 断言登录成功（实际会失败）

    **预期结果**：断言失败，生成截图和录屏
    """)
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.tag("demo", "fail")
    def test_fail_wrong_login(self, login_page):
        print_test_info(
            "❌ 错误账号登录",
            "预期失败 → 登录失败但断言成功",
            "invalid_user / wrong_password"
        )

        login_page.open()
        login_page.login("invalid_user", "wrong_password")
        print("🚨 故意断言：期望登录成功，但实际会失败", flush=True)
        login_page.assert_login_success()  # 会失败

    @allure.story("失败演示")
    @allure.title("❌ 参数化失败用例（多个场景）")
    @allure.description("""
    **测试目的**：多组参数化测试，演示每个失败场景的截图和录屏

    **参数**：
    - standard_user / wrong → 密码错误
    - locked_out_user / secret_sauce → 账户锁定
    - 空账号密码 → 空登录
    """)
    @allure.severity(allure.severity_level.TRIVIAL)
    @allure.tag("demo", "fail", "parametrized")
    @pytest.mark.parametrize("username, password, expected", [
        ("standard_user", "wrong", "登录成功"),
        ("locked_out_user", "secret_sauce", "登录成功"),
        ("", "", "登录成功"),
    ])
    def test_fail_parametrized(self, login_page, username, password, expected):
        print_test_info(
            f"❌ 参数化失败: {username}/{password}",
            f"预期: {expected} → 实际会失败",
            f"{username} / {password}"
        )

        login_page.open()
        login_page.login(username, password)
        assert login_page.page.url == "https://www.saucedemo.com/inventory.html", \
            f"期望登录成功，但实际停留在登录页"