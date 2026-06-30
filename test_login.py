# test_login.py
# 覆盖接口测试常见场景：GET / POST / PUT / DELETE / 参数化 / 异常 / 数据结构验证

import pytest
import requests
import json


# ============================================================
# 场景1：使用 JSONPlaceholder 测试 CRUD 接口
# ============================================================

class TestJSONPlaceholder:

    BASE_URL = "https://jsonplaceholder.typicode.com"

    # ----- 1. GET 请求：获取资源列表 -----
    def test_get_posts_list(self):
        """验证 GET /posts 返回文章列表，状态码200，且列表不为空"""
        resp = requests.get(f"{self.BASE_URL}/posts")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0

    # ----- 2. GET 请求：获取单个资源 -----
    def test_get_single_post(self):
        """验证 GET /posts/1 返回单条数据，且字段完整"""
        resp = requests.get(f"{self.BASE_URL}/posts/1")
        assert resp.status_code == 200
        data = resp.json()
        # 关键字段存在性断言
        assert "id" in data
        assert "title" in data
        assert "body" in data
        assert "userId" in data
        assert data["id"] == 1

    # ----- 3. POST 请求：创建资源 -----
    def test_create_post(self):
        """验证 POST /posts 创建新文章，返回201，且数据正确"""
        payload = {
            "title": "接口自动化测试",
            "body": "这是通过自动化测试创建的文章",
            "userId": 1
        }
        resp = requests.post(f"{self.BASE_URL}/posts", json=payload)
        assert resp.status_code == 201  # JSONPlaceholder 对 POST 返回 201
        data = resp.json()
        assert data["title"] == payload["title"]
        assert data["body"] == payload["body"]
        assert "id" in data  # 新生成的 ID

    # ----- 4. PUT 请求：更新资源 -----
    def test_update_post(self):
        """验证 PUT /posts/1 更新文章，返回200，数据变更"""
        payload = {
            "id": 1,
            "title": "更新后的标题",
            "body": "更新后的内容",
            "userId": 1
        }
        resp = requests.put(f"{self.BASE_URL}/posts/1", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "更新后的标题"

    # ----- 5. DELETE 请求：删除资源 -----
    def test_delete_post(self):
        """验证 DELETE /posts/1 返回200（或204）"""
        resp = requests.delete(f"{self.BASE_URL}/posts/1")
        # JSONPlaceholder 对 DELETE 返回 200
        assert resp.status_code in (200, 204)

    # ----- 6. 异常场景：访问不存在的资源 -----
    def test_get_not_found(self):
        """验证 GET /posts/99999 返回404"""
        resp = requests.get(f"{self.BASE_URL}/posts/99999")
        assert resp.status_code == 404

    # ----- 7. 边界值：空参数 POST -----
    def test_create_post_empty_body(self):
        """验证 POST 空 JSON 体是否返回 400 或 201（取决于服务实现）"""
        resp = requests.post(f"{self.BASE_URL}/posts", json={})
        # JSONPlaceholder 对空体也会返回 201，但这里我们只断言不是 5xx 即可
        assert resp.status_code < 500


# ============================================================
# 场景2：使用 ReqRes 测试登录和用户管理（常见业务场景）
# ============================================================

class TestReqRes:

    BASE_URL = "https://reqres.in/api"

    # ----- 8. 成功登录（带 token） -----
    def test_login_success(self):
        """验证登录成功返回 token"""
        payload = {
            "email": "eve.holt@reqres.in",
            "password": "cityslicka"
        }
        resp = requests.post(f"{self.BASE_URL}/login", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert "token" in data
        assert isinstance(data["token"], str)

    # ----- 9. 登录失败（错误密码） -----
    def test_login_fail_wrong_password(self):
        """验证错误密码返回 400 和错误信息"""
        payload = {
            "email": "eve.holt@reqres.in",
            "password": "wrong_password"
        }
        resp = requests.post(f"{self.BASE_URL}/login", json=payload)
        assert resp.status_code == 400
        data = resp.json()
        assert "error" in data

    # ----- 10. 登录失败（缺失必填字段） -----
    def test_login_missing_field(self):
        """验证缺少 email 字段返回 400"""
        payload = {"password": "cityslicka"}
        resp = requests.post(f"{self.BASE_URL}/login", json=payload)
        assert resp.status_code == 400

    # ----- 11. 获取用户列表 + 数据结构校验 -----
    def test_get_users_list(self):
        """验证 GET /users 返回列表，且包含分页信息"""
        resp = requests.get(f"{self.BASE_URL}/users?page=2")
        assert resp.status_code == 200
        data = resp.json()
        assert "data" in data
        assert isinstance(data["data"], list)
        assert len(data["data"]) > 0
        # 检查第一个用户是否包含必要字段
        first_user = data["data"][0]
        assert "id" in first_user
        assert "email" in first_user
        assert "first_name" in first_user


# ============================================================
# 场景3：Pytest 参数化示例（数据驱动）
# ============================================================

class TestParameterized:

    # ----- 12. 参数化测试：验证不同用户 ID 返回不同数据 -----
    @pytest.mark.parametrize("user_id, expected_email", [
        (1, "george.bluth@reqres.in"),
        (2, "janet.weaver@reqres.in"),
        (3, "emma.wong@reqres.in"),
    ])
    def test_get_user_by_id(self, user_id, expected_email):
        """验证根据 user_id 查询返回的用户邮箱正确"""
        url = f"https://reqres.in/api/users/{user_id}"
        resp = requests.get(url)
        assert resp.status_code == 200
        data = resp.json()
        assert data["data"]["email"] == expected_email

    # ----- 13. 参数化测试：登录失败场景 -----
    @pytest.mark.parametrize("email, password, expected_status", [
        ("eve.holt@reqres.in", "cityslicka", 200),          # 成功
        ("eve.holt@reqres.in", "wrong", 400),               # 密码错
        ("", "cityslicka", 400),                            # 空邮箱
        ("not_an_email", "cityslicka", 400),                # 非邮箱格式
    ])
    def test_login_scenarios(self, email, password, expected_status):
        """参数化测试多种登录场景"""
        payload = {"email": email, "password": password}
        resp = requests.post("https://reqres.in/api/login", json=payload)
        assert resp.status_code == expected_status


# ============================================================
# 场景4：使用 Pytest Fixture（前置准备）
# ============================================================

@pytest.fixture(scope="session")
def base_url():
    """提供一个基础 URL，供测试用例使用"""
    return "https://jsonplaceholder.typicode.com"

def test_using_fixture(base_url):
    """验证 fixture 提供的 URL 可用"""
    resp = requests.get(f"{base_url}/posts/1")
    assert resp.status_code == 200

