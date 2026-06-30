# testcases/test_todos.py
import pytest
import allure
from common.utils import random_string, random_int


@allure.epic("接口自动化测试框架")
@allure.feature("JSONPlaceholder 待办 API")
class TestTodos:

    @allure.title("获取所有待办列表")
    @pytest.mark.smoke
    def test_get_todos_list(self, api_client):
        """GET /todos 验证返回待办列表"""
        with allure.step("请求 /todos"):
            resp = api_client.get("/todos")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        first = data[0]
        assert "id" in first
        assert "title" in first
        assert "completed" in first
        assert "userId" in first

    @allure.title("获取单条待办")
    def test_get_single_todo(self, api_client):
        """GET /todos/1 验证返回单条待办"""
        with allure.step("请求 /todos/1"):
            resp = api_client.get("/todos/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert "title" in data

    @allure.title("创建待办（数据驱动）")
    @pytest.mark.parametrize("title, completed, userId, expected_status", [
        ("完成测试框架", False, 1, 201),
        ("", False, 1, 201),                # 空标题允许
        ("测试", True, 1, 201),
        ("测试", False, 0, 201),            # userId 为 0 也允许
    ])
    def test_create_todo(self, api_client, cleanup_todos, title, completed, userId, expected_status):
        """POST /todos 创建待办（参数化）"""
        payload = {
            "title": title,
            "completed": completed,
            "userId": userId
        }
        with allure.step(f"创建待办: title='{title[:10]}'"):
            resp = api_client.post("/todos", json=payload)
        assert resp.status_code == expected_status
        data = resp.json()
        assert data["title"] == title
        assert data["completed"] == completed
        assert "id" in data

    @allure.title("使用动态数据创建待办")
    def test_create_todo_with_random_data(self, api_client, cleanup_todos):
        """验证使用随机数据创建待办"""
        payload = {
            "title": random_string(15),
            "completed": random_int(0, 1) == 1,
            "userId": random_int(1, 10)
        }
        with allure.step(f"创建待办: {payload['title']}"):
            resp = api_client.post("/todos", json=payload)
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["title"] == payload["title"]
        assert "id" in data

    @allure.title("更新待办（PUT）")
    def test_update_todo(self, api_client):
        """PUT /todos/1 更新待办"""
        payload = {
            "id": 1,
            "title": "更新后的待办标题",
            "completed": True,
            "userId": 1
        }
        with allure.step("发送 PUT /todos/1"):
            resp = api_client.put("/todos/1", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "更新后的待办标题"
        assert data["completed"] is True

    @allure.title("删除待办")
    def test_delete_todo(self, api_client):
        """DELETE /todos/1 验证删除"""
        with allure.step("发送 DELETE /todos/1"):
            resp = api_client.delete("/todos/1")
        assert resp.status_code in (200, 204)

    @allure.title("过滤已完成的待办")
    def test_get_completed_todos(self, api_client):
        """GET /todos?completed=true 验证过滤"""
        with allure.step("请求 /todos?completed=true"):
            resp = api_client.get("/todos", params={"completed": True})
        assert resp.status_code == 200
        data = resp.json()
        with allure.step("验证所有返回的待办都是已完成状态"):
            assert all(item["completed"] is True for item in data)