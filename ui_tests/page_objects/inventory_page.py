# ============================================================
# Sauce Demo 商品列表页面对象
# ============================================================
import allure
from common.ui_base import UIBasePage

class InventoryPage(UIBasePage):
    """商品列表页面"""

    # ---------- 定位器 ----------
    TITLE = ".title"
    ADD_TO_CART_BACKPACK = "[data-test='add-to-cart-sauce-labs-backpack']"
    SHOPPING_CART_BADGE = ".shopping_cart_badge"
    SHOPPING_CART_LINK = ".shopping_cart_link"

    def __init__(self, page, test_name: str = None, test_status: str = "成功"):
        super().__init__(page, test_name, test_status)

    @allure.step("验证商品页面加载成功")
    def assert_loaded(self):
        self.wait_for_element(self.TITLE)
        title = self.get_text(self.TITLE)
        assert "Products" in title, f"期望标题包含 'Products'，实际为 '{title}'"
        return self

    @allure.step("添加商品到购物车")
    def add_backpack_to_cart(self):
        self.click(self.ADD_TO_CART_BACKPACK)
        return self

    @allure.step("验证购物车数量: {expected_count}")
    def assert_cart_count(self, expected_count: int):
        count_text = self.get_text(self.SHOPPING_CART_BADGE)
        actual_count = int(count_text)
        assert actual_count == expected_count, \
            f"期望购物车数量为 {expected_count}，实际为 {actual_count}"
        return self

    @allure.step("点击购物车图标")
    def go_to_cart(self):
        self.click(self.SHOPPING_CART_LINK)
        return self