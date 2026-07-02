# ============================================================
# 日志模块
# 使用方式：from common.logger import logger
# ============================================================
import logging
import sys
from pathlib import Path

def setup_logger(name=__name__, log_file="logs/api_test.log"):
    """
    配置日志记录器（同时输出到控制台和文件）
    """
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formatter = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(name)s | %(message)s"
        )

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        # 确保日志目录存在
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, encoding="utf-8")
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger

# ===== ⭐ 关键：创建全局 logger 实例，供其他模块导入 =====
logger = setup_logger("ui_test")