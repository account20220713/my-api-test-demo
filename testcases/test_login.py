# ============================================================
# 测试用例：Posts 模块
# ============================================================
# 模块说明：测试 JSONPlaceholder 的帖子 API
# 覆盖场景：GET（列表/单条/404）、POST（创建/参数化/随机）、PUT、DELETE
# ============================================================

import pytest
import allure
from common.utils import random_name, random_email

# allure 装饰器：在报告中建立层级结构
# @allure.epic 最大级别（通常代表整个项目）
# @allure.feature 功能模块（如"帖子管理"）
# @allure.story 具体功能点（如"创建帖子"）
# @allure.title 具体用例标题
# @allure.step 报告中的详细步骤

@allure.epic("接口自动化测试框架")
@allure.feature("JSONPlaceholder 帖子 API")
class TestPosts:

    @allure.title("获取帖子列表")
    @allure.severity(allure.severity_level.CRITICAL)  # 标记为高优先级
    @pytest.mark.smoke  # 标记为冒烟用例（执行 -m smoke 时运行）
    def test_get_posts_list(self, api_client):
        """
        测试用例：获取帖子列表
        验证点：
            1. 状态码为 200
            2. 返回数据是列表
            3. 列表不为空
        使用步骤：
            allure.step 让报告中的步骤更清晰
        """
        with allure.step("发送 GET /posts 请求"):
            resp = api_client.get("/posts")
        with allure.step("验证状态码为 200"):
            assert resp.status_code == 200
        with allure.step("验证返回数据是列表且不为空"):
            data = resp.json()
            assert isinstance(data, list)
            assert len(data) > 0

    @allure.title("创建帖子（数据驱动）")
    @pytest.mark.parametrize("title, body, expected_status", [
        ("正常标题", "正常内容", 201),
        ("", "空标题测试", 201),  # JSONPlaceholder 允许空字符串
        ("正常标题", "", 201),
    ])
    def test_create_post(self, api_client, cleanup_posts, title, body, expected_status):
        """
        数据驱动测试：用 3 组不同数据执行同一条测试逻辑
        使用 cleanup_posts 自动清理创建的数据
        """
        payload = {"title": title, "body": body, "userId": 1}
        with allure.step(f"创建帖子: title='{title[:15]}'"):
            resp = api_client.post("/posts", json=payload)
        assert resp.status_code == expected_status
        data = resp.json()
        assert data["title"] == title
        assert "id" in data