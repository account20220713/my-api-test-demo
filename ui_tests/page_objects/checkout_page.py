# ============================================================
# Sauce Demo 结算页面对象
# 包含：Checkout Step One（信息填写）和 Step Two（订单确认）
# ============================================================
import allure
from common.ui_base import UIBasePage


class CheckoutPage(UIBasePage):
    """结算页面"""

    # ---------- Step One: 信息填写 ----------
    FIRST_NAME_INPUT = "[data-test='firstName']"
    LAST_NAME_INPUT = "[data-test='lastName']"
    POSTAL_CODE_INPUT = "[data-test='postalCode']"
    CONTINUE_BUTTON = "[data-test='continue']"
    CANCEL_BUTTON = "[data-test='cancel']"

    # ---------- Step Two: 订单确认 ----------
    FINISH_BUTTON = "[data-test='finish']"
    BACK_HOME_BUTTON = "[data-test='back-to-products']"
    TOTAL_LABEL = ".summary_total_label"               # 总价显示
    ITEM_TOTAL_LABEL = ".summary_subtotal_label"       # 商品小计
    TAX_LABEL = ".summary_tax_label"                   # 税费

    # ---------- 完成页面 ----------
    COMPLETE_HEADER = ".complete-header"               # "Thank you for your order!"
    COMPLETE_TEXT = ".complete-text"                   # 完成信息

    @allure.step("验证结算页面加载成功（Step One）")
    def assert_step_one_loaded(self):
        """验证结算信息填写页面加载完成"""
        self.wait_for_element(self.FIRST_NAME_INPUT, timeout=5)
        return self

    @allure.step("验证订单确认页面加载成功（Step Two）")
    def assert_step_two_loaded(self):
        """验证订单确认页面加载完成"""
        self.wait_for_element(self.FINISH_BUTTON, timeout=5)
        return self

    @allure.step("验证下单完成页面加载成功")
    def assert_complete_loaded(self):
        """验证下单完成页面加载完成"""
        self.wait_for_element(self.COMPLETE_HEADER, timeout=5)
        header = self.get_text(self.COMPLETE_HEADER)
        assert "Thank you" in header, f"期望显示 'Thank you'，实际为 '{header}'"
        return self

    @allure.step("填写收货信息: {first_name} {last_name}, 邮编: {postal_code}")
    def fill_checkout_info(self, first_name: str, last_name: str, postal_code: str):
        """填写结算信息（Step One）"""
        self.fill(self.FIRST_NAME_INPUT, first_name)
        self.fill(self.LAST_NAME_INPUT, last_name)
        self.fill(self.POSTAL_CODE_INPUT, postal_code)
        return self

    @allure.step("点击继续按钮")
    def click_continue(self):
        """点击 Continue 进入订单确认页面"""
        self.click(self.CONTINUE_BUTTON)
        return self

    @allure.step("点击完成按钮")
    def click_finish(self):
        """点击 Finish 完成下单"""
        self.click(self.FINISH_BUTTON)
        return self

    @allure.step("验证订单总价: {expected_total}")
    def assert_total(self, expected_total: str):
        """验证订单总价"""
        total_text = self.get_text(self.TOTAL_LABEL)
        assert expected_total in total_text, \
            f"期望总价包含 '{expected_total}'，实际为 '{total_text}'"
        return self

    @allure.step("点击返回首页")
    def click_back_home(self):
        """点击 Back Home 返回商品列表"""
        self.click(self.BACK_HOME_BUTTON)
        return self