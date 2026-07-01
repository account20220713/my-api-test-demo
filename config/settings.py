# ============================================================
# 配置模块：加载和管理环境变量
# ============================================================
# 作用：读取 env.yaml 配置文件，并根据环境变量 TEST_ENV 切换到对应环境
# 使用场景：在测试代码中通过 `from config.settings import BASE_URL` 获取配置
# ============================================================

import os
import yaml
from pathlib import Path

def load_config():
    """
    加载当前环境的配置
    工作流程：
        1. 读取环境变量 TEST_ENV（默认 test），并去除首尾空白字符
        2. 打开 config/env.yaml 文件
        3. 返回对应环境（如 test/staging/prod）的配置字典
    示例：
        env.yaml 中 test 环境配置了 base_url: https://jsonplaceholder.typicode.com
        调用 load_config() 后返回 {'base_url': '...', 'timeout': 10}
    """
    # 1. 优先使用 ENV，其次使用 TEST_ENV，兼容不同命名
    env = os.getenv("ENV") or os.getenv("TEST_ENV", "test")
    env = env.strip()  # 去除可能存在的空格或换行符

    # 2. 调试输出：帮助在 Jenkins 控制台确认实际值
    print(f"[DEBUG] 当前环境变量 ENV/TEST_ENV = '{env}'")

    config_path = Path(__file__).parent / "env.yaml"    # 配置文件的绝对路径
    with open(config_path, "r", encoding="utf-8") as f:
        all_configs = yaml.safe_load(f)                # 解析 YAML 为字典

    # 3. 如果环境不存在，列出所有可用环境
    if env not in all_configs:
        available = ', '.join(all_configs.keys())
        raise ValueError(f"未知环境: {env}，可用的环境: {available}")

    return all_configs[env]

# 全局配置变量（其他模块直接导入使用）
CONF = load_config()                                    # 当前环境全部配置
BASE_URL = CONF["base_url"]                            # 接口基础地址
TIMEOUT = CONF["timeout"]                              # 请求超时时间（秒）