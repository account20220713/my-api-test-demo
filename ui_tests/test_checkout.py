# ============================================================
# Sauce Demo 完整购物流程测试
# ============================================================
import allure
from ui_tests.page_objects.inventory_page import InventoryPage
from ui_tests.page_objects.cart_page import CartPage
from ui_tests.page_objects.checkout_page import CheckoutPage


@allure.epic("Sauce Demo 自动化测试")
@allure.feature("端到端购物流程")
class TestCheckout:

    @allure.story("完整购物流程")
    @allure.title("✅ 标准用户完成完整购物流程：登录 → 加购 → 下单")
    @allure.severity(allure.severity_level.CRITICAL)
    @allure.tag("smoke", "e2e", "checkout")
    def test_full_checkout_flow(self, logged_in_page):
        """完整购物流程测试：添加商品 → 购物车 → 结算 → 下单"""
        # 获取测试名称
        test_name = getattr(logged_in_page, '_test_name', 'unknown')

        # 创建页面对象时传入 test_name
        inventory = InventoryPage(logged_in_page, test_name=test_name)
        inventory.assert_loaded()

        # 添加商品
        inventory.add_backpack_to_cart()
        inventory.assert_cart_count(1)

        # 进入购物车
        inventory.go_to_cart()
        cart = CartPage(logged_in_page, test_name=test_name)
        cart.assert_loaded()
        cart.assert_cart_item_count(1)

        # 结算
        cart.click_checkout()
        checkout = CheckoutPage(logged_in_page, test_name=test_name)
        checkout.assert_step_one_loaded()
        checkout.fill_checkout_info("Test", "User", "12345")
        checkout.click_continue()
        checkout.assert_step_two_loaded()
        checkout.click_finish()
        checkout.assert_complete_loaded()