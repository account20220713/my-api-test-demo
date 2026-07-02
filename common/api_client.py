# testcases/conftest.py
import pytest
import requests
from config.settings import BASE_URL, TIMEOUT


@pytest.fixture(scope="session")
def api_client():
    class ApiClient:
        def __init__(self):
            self.base_url = BASE_URL
            self.timeout = TIMEOUT
            self.session = requests.Session()

        def get(self, endpoint, **kwargs):
            return self.session.get(f"{self.base_url}{endpoint}", timeout=self.timeout, **kwargs)

        def post(self, endpoint, **kwargs):
            return self.session.post(f"{self.base_url}{endpoint}", timeout=self.timeout, **kwargs)

        def put(self, endpoint, **kwargs):
            return self.session.put(f"{self.base_url}{endpoint}", timeout=self.timeout, **kwargs)

        def delete(self, endpoint, **kwargs):
            return self.session.delete(f"{self.base_url}{endpoint}", timeout=self.timeout, **kwargs)

    return ApiClient()


# 其他 cleanup fixtures 省略（可选）