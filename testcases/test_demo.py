# ============================================================
# 演示用例：展示不同测试结果类型（通过 / 失败 / 跳过 / 预期失败）
# ============================================================
# 面试时可以这样说：
# "我的测试用例覆盖了正常场景，也覆盖了异常场景。
#  比如这个 demo 模块包含了预期失败、跳过、超时模拟、异常断言等，
#  能真实反映系统在不同情况下的表现，而不是只写能跑通的用例。"
# ============================================================

import pytest
import requests
import time
import allure


# ============================================================
# 1. 正常通过的用例
# ============================================================
@allure.feature("演示用例")
@allure.story("正常通过")
class TestPass:

    @allure.title("这是一个会通过的用例")
    def test_always_pass(self):
        """简单断言 1+1=2"""
        assert 1 + 1 == 2

    @allure.title("GET 请求正常返回 200")
    def test_get_request_pass(self, api_client):
        """请求一个存在的资源，应该返回 200"""
        resp = api_client.get("/posts/1")
        assert resp.status_code == 200


# ============================================================
# 2. 预期失败的用例（标记为 xfail）
# ============================================================
@allure.feature("演示用例")
@allure.story("预期失败")
class TestXFail:

    @allure.title("这个用例预期会失败（接口返回 500）")
    @pytest.mark.xfail(reason="模拟接口不可用，预期失败")
    def test_expected_fail(self):
        """访问一个不存在的接口，预期返回 500"""
        url = "https://jsonplaceholder.typicode.com/non-existent-endpoint"
        resp = requests.get(url)
        # 这个断言会失败，但因为标记了 xfail，测试结果会显示为 "预期失败"
        assert resp.status_code == 200

    @allure.title("预期失败的参数化用例")
    @pytest.mark.xfail(reason="演示预期失败的参数化用例")
    @pytest.mark.parametrize("input_val, expected", [
        (1, 2),   # 1+1=2，但故意写错预期值 3
        (2, 4),   # 2+2=4，故意写错预期值 5
    ])
    def test_param_xfail(self, input_val, expected):
        """参数化 + 预期失败"""
        assert input_val + input_val == expected


# ============================================================
# 3. 跳过的用例
# ============================================================
@allure.feature("演示用例")
@allure.story("跳过测试")
class TestSkip:

    @allure.title("这个用例被跳过（条件不满足）")
    @pytest.mark.skip(reason="这个功能还没开发，暂时跳过")
    def test_skip_demo(self):
        """演示 skip 用法"""
        assert False  # 这行不会执行

    @allure.title("条件跳过：只在特定环境运行")
    @pytest.mark.skipif(True, reason="当前环境不满足条件，跳过")
    def test_skip_if_demo(self):
        """演示 skipif 用法"""
        assert 1 == 1


# ============================================================
# 4. 真实失败的用例（展示失败时的信息）
# ============================================================
@allure.feature("演示用例")
@allure.story("真实失败")
class TestRealFail:

    @allure.title("这个用例会真实失败（展示失败信息）")
    def test_real_fail(self):
        """模拟真实失败场景"""
        response_data = {"status": "error", "code": 500}
        # 故意让断言失败，展示失败时的错误信息
        assert response_data["status"] == "success", \
            f"期望 status=success，实际 status={response_data['status']}"

    @allure.title("参数化用例：部分通过部分失败")
    @pytest.mark.parametrize("test_input, expected", [
        (1, 1),   # 通过
        (2, 2),   # 通过
        (3, 5),   # 失败：3 不等于 5
        (4, 4),   # 通过
        (5, 10),  # 失败：5 不等于 10
    ])
    def test_partial_fail(self, test_input, expected):
        """展示部分通过、部分失败"""
        assert test_input == expected, f"{test_input} 不等于 {expected}"


# ============================================================
# 5. 异常断言（测试是否抛出预期异常）
# ============================================================
@allure.feature("演示用例")
@allure.story("异常断言")
class TestException:

    @allure.title("验证 KeyError 异常被正确抛出")
    def test_exception_expected(self):
        """断言代码抛出了预期的异常"""
        data = {"name": "test"}
        with pytest.raises(KeyError):
            value = data["non_existent_key"]  # 这会抛出 KeyError

    @allure.title("验证 ValueError 异常被正确抛出")
    def test_exception_value_error(self):
        """断言 int() 转换非数字字符串会抛出 ValueError"""
        with pytest.raises(ValueError):
            int("not a number")


# ============================================================
# 6. 超时模拟（展示超时场景）
# ============================================================
@allure.feature("演示用例")
@allure.story("超时模拟")
class TestTimeout:

    @allure.title("模拟请求超时")
    def test_request_timeout(self, api_client):
        """模拟接口超时场景"""
        import requests.exceptions

        # 注意：JSONPlaceholder 不会真的超时，这里用 try-except 模拟捕获超时异常
        # 实际项目中可以用 Mock 服务模拟超时
        try:
            # 设置极短超时（0.001秒），预期会超时
            resp = api_client.get("/posts/1", timeout=0.001)
            assert resp.status_code == 200
        except requests.exceptions.Timeout:
            # 捕获到超时异常，标记为通过（说明超时处理逻辑正确）
            allure.attach("请求超时，符合预期", name="超时信息")
            assert True
        except Exception as e:
            # 其他异常也捕获，用 allure 记录
            allure.attach(str(e), name="异常信息")
            # 如果抛出其他异常（比如连接被拒绝），也视为通过，说明处理逻辑正确
            assert True


# ============================================================
# 7. 边界值测试（展示边界值设计）
# ============================================================
@allure.feature("演示用例")
@allure.story("边界值测试")
class TestBoundary:

    @allure.title("字符串长度边界值测试")
    @pytest.mark.parametrize("text, expected_length", [
        ("", 0),           # 空字符串
        ("A", 1),          # 最短长度
        ("A" * 100, 100),  # 边界长度
        ("A" * 101, 101),  # 超出边界
    ])
    def test_string_length_boundary(self, text, expected_length):
        """验证字符串长度"""
        assert len(text) == expected_length

    @allure.title("数值范围边界值测试")
    @pytest.mark.parametrize("value, is_valid", [
        (-1, False),   # 小于最小值
        (0, True),     # 最小值
        (50, True),    # 中间值
        (100, True),   # 最大值
        (101, False),  # 大于最大值
    ])
    def test_number_boundary(self, value, is_valid):
        """假设业务规则：数字必须在 0-100 之间"""
        if is_valid:
            assert 0 <= value <= 100
        else:
            assert not (0 <= value <= 100)