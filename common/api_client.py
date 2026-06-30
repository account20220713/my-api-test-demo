# ============================================================
# HTTP 客户端：封装所有 API 请求逻辑
# ============================================================
# 作用：统一处理请求、响应、日志、重试、Allure 附件
# 设计思路：所有测试用例通过 ApiClient 发送请求，避免代码重复
# 使用示例：
#   client = ApiClient()
#   resp = client.get("/posts")              # GET 请求
#   resp = client.post("/posts", json=payload)  # POST 请求
# ============================================================

import requests
import allure
import json
from tenacity import retry, stop_after_attempt, wait_fixed
from config.settings import BASE_URL, TIMEOUT
from common.logger import setup_logger

# 创建日志记录器（输出到控制台和文件）
logger = setup_logger("api_client")

class ApiClient:
    """API 客户端，负责发送所有 HTTP 请求"""

    def __init__(self):
        """
        初始化客户端
        1. 创建 Session 对象：复用 TCP 连接，提升性能
        2. 设置基础 URL 和默认超时
        """
        self.session = requests.Session()
        self.base_url = BASE_URL
        self.timeout = TIMEOUT

    @retry(stop=stop_after_attempt(3), wait=wait_fixed(1))
    def request(self, method, endpoint, **kwargs):
        """
        发送 HTTP 请求（最核心的方法）
        参数：
            method (str): 请求方法（GET/POST/PUT/DELETE）
            endpoint (str): API 路径，如 '/posts' 或 '/users'
            **kwargs: 其他参数（如 json=payload, params=query_string）
        返回：
            requests.Response: 响应对象
        特性：
            1. 自动重试：网络抖动时自动重试 3 次
            2. 记录日志：请求和响应信息输出到控制台 + 文件
            3. Allure 附件：请求体和响应体自动附加到报告中
        """
        # 拼接完整 URL（避免重复斜杠）
        url = f"{self.base_url}/{endpoint.lstrip('/')}"
        kwargs.setdefault("timeout", self.timeout)      # 设置超时

        # 将请求体附加到 Allure 报告（方便定位问题）
        allure.attach(
            json.dumps(kwargs.get("json", {}), indent=2, ensure_ascii=False),
            name=f"📤 请求体 ({method} {endpoint})",
            attachment_type=allure.attachment_type.JSON
        )

        logger.info(f"Request: {method} {url}")        # 打印请求日志
        resp = self.session.request(method, url, **kwargs)  # 发送请求

        # 将响应体附加到 Allure 报告
        try:
            allure.attach(
                resp.text[:1000],                      # 截断过长内容
                name=f"📥 响应体 (状态码: {resp.status_code})",
                attachment_type=allure.attachment_type.TEXT
            )
        except:
            pass

        logger.info(f"Response: {resp.status_code} in {resp.elapsed.total_seconds():.2f}s")
        return resp

    # ---------- 快捷方法 ----------
    # 以下方法本质都是调用 request()，只是提供了更直观的函数名
    def get(self, endpoint, **kwargs):
        """发送 GET 请求"""
        return self.request("GET", endpoint, **kwargs)

    def post(self, endpoint, **kwargs):
        """发送 POST 请求"""
        return self.request("POST", endpoint, **kwargs)

    def put(self, endpoint, **kwargs):
        """发送 PUT 请求"""
        return self.request("PUT", endpoint, **kwargs)

    def delete(self, endpoint, **kwargs):
        """发送 DELETE 请求"""
        return self.request("DELETE", endpoint, **kwargs)