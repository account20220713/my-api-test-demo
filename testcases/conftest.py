# ============================================================
# Pytest 公共配置（所有测试用例共享）
# ============================================================
# 作用：存放 fixture（测试准备和数据清理）
# 运行顺序：
#   1. health_check（自动执行）→ 2. 测试用例执行 → 3. 数据清理（如果有）
# ============================================================

import pytest
import requests
from common.api_client import ApiClient
from config.settings import BASE_URL

# ---------- 1. 健康检查 ----------
# 目的：在测试开始前检查服务是否可用，避免无意义报错
# 场景：如果被测服务挂了，所有测试都会直接跳过，而不是报一堆 500
@pytest.fixture(scope="session", autouse=True)
def health_check():
    """自动执行：检查被测服务是否可用"""
    try:
        resp = requests.get(f"{BASE_URL}/posts/1", timeout=3)
        if resp.status_code == 200:
            print("✅ 服务健康检查通过")
        else:
            pytest.skip(f"❌ 服务返回 {resp.status_code}，跳过所有测试")
    except Exception as e:
        pytest.skip(f"❌ 服务不可用: {e}")

# ---------- 2. API 客户端 ----------
# 目的：提供共享的 ApiClient 实例，避免每个用例重复创建
@pytest.fixture(scope="session")
def api_client():
    """返回共享的 API 客户端（所有用例共用，提升性能）"""
    return ApiClient()

# ---------- 3. 数据清理 ----------
# 原理：
#   1. 测试开始前，创建空列表 created_ids
#   2. 测试用例调用 _create_and_track() 创建数据，记录 ID
#   3. 测试结束后（yield 之后），逐个删除 created_ids 中的数据
# 目的：确保每次测试独立，不依赖上一次的残留数据

@pytest.fixture
def cleanup_posts(api_client):
    """自动清理 POST 测试中创建的数据"""
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


@pytest.fixture(scope="session", autouse=True)
def allure_environment_info():
    """自动生成 environment.properties 文件"""
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

# ========== 清理照片 ==========
@pytest.fixture
def cleanup_photos(api_client):
    """测试结束后自动删除创建的照片"""
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