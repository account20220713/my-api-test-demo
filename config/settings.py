import os
import yaml

def load_config():
    # 获取环境变量，并去除首尾空白字符（防止换行符或空格）
    env = os.getenv('ENV', 'test').strip()
    # 打印调试信息，方便在 Jenkins 控制台查看
    print(f"[DEBUG] 当前环境变量 ENV = '{env}'")

    # 读取配置文件
    config_file = os.path.join(os.path.dirname(__file__), '..', 'env.yaml')
    with open(config_file, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    # 如果环境不存在，列出所有可用环境
    if env not in config:
        available = ', '.join(config.keys())
        raise ValueError(f"未知环境: {env}，可用的环境: {available}")

    return config[env]

# 全局配置对象
CONF = load_config()

# 导出常用变量
BASE_URL = CONF['BASE_URL']
TIMEOUT = CONF['TIMEOUT']