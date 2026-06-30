# testcases/test_comments.py
import pytest
import allure
from common.utils import random_string, random_int


@allure.epic("接口自动化测试框架")
@allure.feature("JSONPlaceholder 评论 API")
class TestComments:

    @allure.title("获取某篇文章的所有评论")
    @pytest.mark.smoke
    def test_get_comments_by_post(self, api_client):
        """GET /posts/1/comments 验证返回评论列表"""
        with allure.step("请求 /posts/1/comments"):
            resp = api_client.get("/posts/1/comments")
        assert resp.status_code == 200
        data = resp.json()
        with allure.step("验证返回数据是列表且不为空"):
            assert isinstance(data, list)
            assert len(data) > 0
        with allure.step("验证评论字段完整性"):
            first = data[0]
            assert "id" in first
            assert "postId" in first
            assert "name" in first
            assert "email" in first
            assert "body" in first

    @allure.title("获取单条评论")
    def test_get_single_comment(self, api_client):
        """GET /comments/1 验证返回单条评论"""
        with allure.step("请求 /comments/1"):
            resp = api_client.get("/comments/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert "postId" in data

    @allure.title("创建评论（数据驱动）")
    @pytest.mark.parametrize("name, email, body, expected_status", [
        ("测试用户", "test@example.com", "这是一条测试评论", 201),
        ("", "test@example.com", "空名称评论", 201),          # JSONPlaceholder 允许空名称
        ("测试用户", "", "空邮箱评论", 201),                  # 允许空邮箱
        ("测试用户", "invalid-email", "无效邮箱格式", 201),    # 不校验邮箱格式
    ])
    def test_create_comment(self, api_client, cleanup_comments, name, email, body, expected_status):
        """POST /comments 创建评论（参数化）"""
        payload = {
            "postId": 1,
            "name": name,
            "email": email,
            "body": body
        }
        with allure.step(f"创建评论: name='{name[:10]}'"):
            resp = api_client.post("/comments", json=payload)
        assert resp.status_code == expected_status
        data = resp.json()
        assert data["name"] == name
        assert data["body"] == body
        assert "id" in data

    @allure.title("使用动态数据创建评论")
    def test_create_comment_with_random_data(self, api_client, cleanup_comments):
        """验证使用随机数据创建评论"""
        payload = {
            "postId": random_int(1, 10),
            "name": random_string(8),
            "email": f"{random_string(6)}@example.com",
            "body": random_string(20)
        }
        with allure.step(f"创建评论: {payload['name']}"):
            resp = api_client.post("/comments", json=payload)
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["name"] == payload["name"]
        assert "id" in data

    @allure.title("按 postId 过滤评论")
    def test_get_comments_filter_by_post(self, api_client):
        """GET /comments?postId=1 验证过滤结果"""
        with allure.step("请求 /comments?postId=1"):
            resp = api_client.get("/comments", params={"postId": 1})
        assert resp.status_code == 200
        data = resp.json()
        with allure.step("验证所有返回的评论都属于 postId=1"):
            assert all(item["postId"] == 1 for item in data)

    @allure.title("获取不存在的评论（404）")
    def test_get_comment_not_found(self, api_client):
        """GET /comments/99999 验证返回 404"""
        with allure.step("请求不存在的评论 ID 99999"):
            resp = api_client.get("/comments/99999")
        assert resp.status_code == 404