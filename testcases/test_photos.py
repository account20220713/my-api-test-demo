# testcases/test_photos.py
import pytest
import allure
from common.utils import random_string, random_int


@allure.epic("接口自动化测试框架")
@allure.feature("JSONPlaceholder 照片 API")
class TestPhotos:

    @allure.title("获取照片列表")
    @pytest.mark.smoke
    def test_get_photos_list(self, api_client):
        """GET /photos 验证返回照片列表"""
        with allure.step("发送 GET /photos 请求"):
            resp = api_client.get("/photos")
        assert resp.status_code == 200
        data = resp.json()
        assert isinstance(data, list)
        assert len(data) > 0
        first = data[0]
        assert "id" in first
        assert "title" in first
        assert "url" in first
        assert "thumbnailUrl" in first
        assert "albumId" in first

    @allure.title("获取单张照片")
    def test_get_single_photo(self, api_client):
        """GET /photos/1 验证返回单张照片"""
        with allure.step("请求 /photos/1"):
            resp = api_client.get("/photos/1")
        assert resp.status_code == 200
        data = resp.json()
        assert data["id"] == 1
        assert data["title"] is not None

    @allure.title("按 albumId 过滤照片")
    def test_get_photos_by_album(self, api_client):
        """GET /photos?albumId=1 验证过滤"""
        with allure.step("请求 /photos?albumId=1"):
            resp = api_client.get("/photos", params={"albumId": 1})
        assert resp.status_code == 200
        data = resp.json()
        assert all(item["albumId"] == 1 for item in data)

    @allure.title("创建照片（数据驱动）")
    @pytest.mark.parametrize("title, url, thumbnailUrl, albumId, expected_status", [
        ("测试照片1", "https://example.com/photo1.jpg", "https://example.com/thumb1.jpg", 1, 201),
        ("", "https://example.com/empty.jpg", "https://example.com/empty_thumb.jpg", 1, 201),
        ("测试照片2", "", "", 1, 201),
    ])
    def test_create_photo(self, api_client, cleanup_photos, title, url, thumbnailUrl, albumId, expected_status):
        """POST /photos 创建照片（参数化）"""
        payload = {
            "title": title,
            "url": url,
            "thumbnailUrl": thumbnailUrl,
            "albumId": albumId
        }
        with allure.step(f"创建照片: title='{title[:15]}'"):
            resp = api_client.post("/photos", json=payload)
        assert resp.status_code == expected_status
        data = resp.json()
        assert data["title"] == title
        assert "id" in data

    @allure.title("使用动态数据创建照片")
    def test_create_photo_with_random_data(self, api_client, cleanup_photos):
        """验证使用随机数据创建照片"""
        payload = {
            "title": random_string(12),
            "url": f"https://example.com/{random_string(8)}.jpg",
            "thumbnailUrl": f"https://example.com/{random_string(8)}_thumb.jpg",
            "albumId": random_int(1, 10)
        }
        with allure.step(f"创建照片: {payload['title']}"):
            resp = api_client.post("/photos", json=payload)
        assert resp.status_code in (200, 201)
        data = resp.json()
        assert data["title"] == payload["title"]
        assert "id" in data

    @allure.title("更新照片标题（PUT）")
    def test_update_photo(self, api_client):
        """PUT /photos/1 更新照片标题"""
        payload = {
            "id": 1,
            "title": "更新后的照片标题",
            "url": "https://example.com/updated.jpg",
            "thumbnailUrl": "https://example.com/updated_thumb.jpg",
            "albumId": 1
        }
        with allure.step("发送 PUT /photos/1"):
            resp = api_client.put("/photos/1", json=payload)
        assert resp.status_code == 200
        data = resp.json()
        assert data["title"] == "更新后的照片标题"

    @allure.title("删除照片")
    def test_delete_photo(self, api_client):
        """DELETE /photos/1 验证删除"""
        with allure.step("发送 DELETE /photos/1"):
            resp = api_client.delete("/photos/1")
        assert resp.status_code in (200, 204)

    @allure.title("获取不存在的照片（404）")
    def test_get_photo_not_found(self, api_client):
        """GET /photos/99999 验证返回 404"""
        with allure.step("请求不存在的照片 ID 99999"):
            resp = api_client.get("/photos/99999")
        assert resp.status_code == 404