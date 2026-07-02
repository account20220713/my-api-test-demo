import allure
from ui_tests.page_objects.inventory_page import InventoryPage

@allure.epic("Sauce Demo 自动化测试")
@allure.feature("购物车功能")
class TestCart:

    @allure.story("添加商品")
    @allure.title("✅ 添加商品到购物车成功")
    def test_add_item_to_cart(self, logged_in_page):
        """直接使用已登录的页面"""
        inventory = InventoryPage(logged_in_page)
        inventory.assert_loaded()
        inventory.add_backpack_to_cart()
        inventory.assert_cart_count(1)