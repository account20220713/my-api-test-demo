# ============================================================
# Pytest 公共配置（所有测试用例共享）
# ============================================================
# 作用：存放 fixture（测试准备和数据清理）
# 运行顺序：
#   1. health_check（自动执行）→ 2. 测试用例执行 → 3. 数据清理（如果有）
# ============================================================
import pytest
import requests
import sys
import platform
import os
from datetime import datetime
from pathlib import Path
from common.api_client import ApiClient
from config.settings import BASE_URL


@pytest.fixture(scope="session", autouse=True)
def health_check():
    try:
        resp = requests.get(f"{BASE_URL}/posts/1", timeout=3)
        if resp.status_code == 200:
            print("✅ 服务健康检查通过")
        else:
            pytest.skip(f"❌ 服务返回 {resp.status_code}，跳过所有测试")
    except Exception as e:
        pytest.skip(f"❌ 服务不可用: {e}")


@pytest.fixture(scope="session")
def api_client():
    return ApiClient()


@pytest.fixture
def cleanup_posts(api_client):
    created_ids = []
    def _create_and_track(payload):
        resp = api_client.post("/posts", json=payload)
        if resp.status_code in (200, 201):
            pid = resp.json().get("id")
            if pid:
                created_ids.append(pid)
        return resp
    yield _create_and_track
    for pid in created_ids:
        try:
            api_client.delete(f"/posts/{pid}")
            print(f"🧹 清理帖子 ID: {pid}")
        except:
            pass


@pytest.fixture
def cleanup_comments(api_client):
    created_ids = []
    def _create_and_track(payload):
        resp = api_client.post("/comments", json=payload)
        if resp.status_code in (200, 201):
            cid = resp.json().get("id")
            if cid:
                created_ids.append(cid)
        return resp
    yield _create_and_track
    for cid in created_ids:
        try:
            api_client.delete(f"/comments/{cid}")
            print(f"🧹 清理评论 ID: {cid}")
        except:
            pass


@pytest.fixture
def cleanup_todos(api_client):
    created_ids = []
    def _create_and_track(payload):
        resp = api_client.post("/todos", json=payload)
        if resp.status_code in (200, 201):
            tid = resp.json().get("id")
            if tid:
                created_ids.append(tid)
        return resp
    yield _create_and_track
    for tid in created_ids:
        try:
            api_client.delete(f"/todos/{tid}")
            print(f"🧹 清理待办 ID: {tid}")
        except:
            pass


@pytest.fixture
def cleanup_photos(api_client):
    created_ids = []
    def _create_and_track(payload):
        resp = api_client.post("/photos", json=payload)
        if resp.status_code in (200, 201):
            pid = resp.json().get("id")
            if pid:
                created_ids.append(pid)
        return resp
    yield _create_and_track
    for pid in created_ids:
        try:
            api_client.delete(f"/photos/{pid}")
            print(f"🧹 清理照片 ID: {pid}")
        except:
            pass


@pytest.fixture(scope="session", autouse=True)
def allure_environment_info():
    allure_dir = Path("reports/allure_results")
    allure_dir.mkdir(parents=True, exist_ok=True)
    env_file = allure_dir / "environment.properties"
    with open(env_file, "w", encoding="utf-8") as f:
        f.write(f"Python Version: {sys.version.split()[0]}\n")
        f.write(f"Platform: {platform.system()} {platform.release()}\n")
        f.write(f"Architecture: {platform.machine()}\n")
        f.write(f"Test Environment: {os.getenv('TEST_ENV', 'test')}\n")
        f.write(f"Base URL: {BASE_URL}\n")
        f.write(f"Test Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"Executor: {os.getenv('COMPUTERNAME', 'Local')}\n")
    print("✅ Allure 环境信息已生成")