# ============================================================
# Sauce Demo 购物车页面对象
# URL: https://www.saucedemo.com/cart.html
# ============================================================
import allure
from common.ui_base import UIBasePage


class CartPage(UIBasePage):
    """购物车页面"""

    # ---------- 定位器 ----------
    CART_ITEM = ".cart_item"                           # 购物车商品项
    CART_ITEM_NAME = ".inventory_item_name"            # 商品名称
    REMOVE_BUTTON = "button[data-test^='remove']"      # 移除按钮（动态data-test）
    CHECKOUT_BUTTON = "[data-test='checkout']"         # 结算按钮
    CONTINUE_SHOPPING_BUTTON = "[data-test='continue-shopping']"

    @allure.step("验证购物车页面加载成功")
    def assert_loaded(self):
        """验证购物车页面加载完成"""
        self.wait_for_element(self.CART_ITEM, timeout=5)
        return self

    @allure.step("验证购物车中有 {expected_count} 件商品")
    def assert_cart_item_count(self, expected_count: int):
        """验证购物车商品数量"""
        items = self.page.locator(self.CART_ITEM).all()
        actual_count = len(items)
        assert actual_count == expected_count, \
            f"期望购物车有 {expected_count} 件商品，实际有 {actual_count} 件"
        return self

    @allure.step("获取购物车中所有商品名称")
    def get_item_names(self) -> list:
        """获取购物车中所有商品名称"""
        self.wait_for_element(self.CART_ITEM)
        name_elements = self.page.locator(self.CART_ITEM_NAME).all()
        return [el.text_content() for el in name_elements]

    @allure.step("验证购物车包含商品: {expected_name}")
    def assert_contains_item(self, expected_name: str):
        """验证购物车包含指定商品"""
        names = self.get_item_names()
        assert expected_name in names, \
            f"期望购物车包含 '{expected_name}'，实际包含: {names}"
        return self

    @allure.step("点击结算按钮")
    def click_checkout(self):
        """点击 Checkout 按钮进入结算页面"""
        self.click(self.CHECKOUT_BUTTON)
        return self

    @allure.step("点击继续购物按钮")
    def click_continue_shopping(self):
        """点击 Continue Shopping 返回商品列表"""
        self.click(self.CONTINUE_SHOPPING_BUTTON)
        return self