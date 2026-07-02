import os
import yaml
from pathlib import Path

def load_config():
    env = os.getenv("ENV") or os.getenv("TEST_ENV", "test")
    env = env.strip()
    config_path = Path(__file__).parent / "env.yaml"
    with open(config_path, "r", encoding="utf-8") as f:
        all_configs = yaml.safe_load(f)
    if env not in all_configs:
        available = ', '.join(all_configs.keys())
        raise ValueError(f"未知环境: {env}，可用环境: {available}")
    return all_configs[env]

CONF = load_config()

# ===== API 配置 =====
BASE_URL = CONF["base_url"]
TIMEOUT = CONF["timeout"]

# ===== UI 配置 =====
UI_BASE_URL = CONF.get("ui_base_url", "https://www.saucedemo.com/")
UI_TIMEOUT = CONF.get("ui_timeout", 30)
HEADLESS = CONF.get("headless", True)
BROWSER = CONF.get("browser", "chromium")
SLOW_MO = CONF.get("slow_mo", 0)
VIEWPORT = CONF.get("viewport", {"width": 1920, "height": 1080})

# ⭐ 屏幕配置（新增）
AUTO_DETECT_SCREEN = CONF.get("auto_detect_screen", True)
LAUNCH_ARGS = CONF.get("launch_args", [])
# 在 settings.py 末尾
ENV = os.getenv("ENV") or os.getenv("TEST_ENV", "test")