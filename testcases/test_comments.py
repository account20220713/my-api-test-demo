# ============================================================
# testcases/conftest.py
# 接口测试的 fixture 配置
# ============================================================
import pytest
import requests
from config.settings import BASE_URL, TIMEOUT


@pytest.fixture(scope="session")
def api_client():
    """
    提供 API 客户端实例
    所有接口测试用例通过此 fixture 发送请求
    """
    class ApiClient:
        def __init__(self):
            self.base_url = BASE_URL
            self.timeout = TIMEOUT
            self.session = requests.Session()
            self.session.headers.update({
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "Accept": "application/json"
            })

        def get(self, endpoint, **kwargs):
            url = f"{self.base_url}{endpoint}"
            return self.session.get(url, timeout=self.timeout, **kwargs)

        def post(self, endpoint, **kwargs):
            url = f"{self.base_url}{endpoint}"
            return self.session.post(url, timeout=self.timeout, **kwargs)

        def put(self, endpoint, **kwargs):
            url = f"{self.base_url}{endpoint}"
            return self.session.put(url, timeout=self.timeout, **kwargs)

        def delete(self, endpoint, **kwargs):
            url = f"{self.base_url}{endpoint}"
            return self.session.delete(url, timeout=self.timeout, **kwargs)

    return ApiClient()


@pytest.fixture(scope="function")
def cleanup_posts(api_client):
    """清理测试创建的帖子（测试后清理）"""
    created_ids = []
    yield created_ids
    for post_id in created_ids:
        try:
            api_client.delete(f"/posts/{post_id}")
        except:
            pass


@pytest.fixture(scope="function")
def cleanup_comments(api_client):
    """清理测试创建的评论"""
    created_ids = []
    yield created_ids
    for comment_id in created_ids:
        try:
            api_client.delete(f"/comments/{comment_id}")
        except:
            pass


@pytest.fixture(scope="function")
def cleanup_photos(api_client):
    """清理测试创建的照片"""
    created_ids = []
    yield created_ids
    for photo_id in created_ids:
        try:
            api_client.delete(f"/photos/{photo_id}")
        except:
            pass


@pytest.fixture(scope="function")
def cleanup_todos(api_client):
    """清理测试创建的待办"""
    created_ids = []
    yield created_ids
    for todo_id in created_ids:
        try:
            api_client.delete(f"/todos/{todo_id}")
        except:
            pass