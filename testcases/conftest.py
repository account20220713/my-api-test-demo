# ============================================================
# UI 测试的 Pytest 配置（支持自动检测第二屏幕）
# ============================================================
from datetime import datetime

import pytest
import allure
import yaml
import sys
from pathlib import Path
from playwright.sync_api import Playwright, Browser, Page, sync_playwright
from config.settings import (
    BROWSER, HEADLESS, VIEWPORT, UI_BASE_URL, UI_TIMEOUT,
    SLOW_MO, LAUNCH_ARGS, AUTO_DETECT_SCREEN
)
from ui_tests.page_objects.login_page import LoginPage
from common.logger import logger

# ---------- 尝试导入 screeninfo（用于检测多屏幕） ----------
try:
    from screeninfo import get_monitors

    SCREENINFO_AVAILABLE = True
except ImportError:
    SCREENINFO_AVAILABLE = False
    logger.warning("⚠️ screeninfo 未安装，无法自动检测屏幕。运行: pip install screeninfo")


def detect_screen_config():
    """
    自动检测屏幕配置，返回合适的启动参数
    如果检测到第二块屏幕，将浏览器放到第二屏并全屏
    否则在主屏全屏
    """
    if not SCREENINFO_AVAILABLE:
        logger.warning("⚠️ screeninfo 不可用，使用默认配置（主屏最大化）")
        return ["--start-maximized"]

    try:
        monitors = get_monitors()
        logger.info(f"检测到 {len(monitors)} 块屏幕")
        for i, m in enumerate(monitors):
            logger.info(f"  屏幕 {i + 1}: {m.width}x{m.height} 位置: ({m.x}, {m.y})")

        if len(monitors) >= 2:
            # 找到第二块屏幕（主屏通常是 (0, 0) 或离原点最近的）
            # 按 x 坐标排序，找到最右边的屏幕
            sorted_monitors = sorted(monitors, key=lambda m: m.x)

            # 如果第一块屏幕在原点，第二块就是 x > 0
            if sorted_monitors[0].x == 0 and sorted_monitors[0].y == 0:
                second_screen = sorted_monitors[1]
            else:
                # 如果主屏不在原点，用 x 最大的作为第二屏
                second_screen = sorted_monitors[-1]

            logger.info(
                f"✅ 检测到第二块屏幕: {second_screen.width}x{second_screen.height} 位置: ({second_screen.x}, {second_screen.y})")

            # 返回第二屏全屏参数
            return [
                f"--window-position={second_screen.x},{second_screen.y}",
                "--start-maximized"
            ]
        else:
            logger.info("ℹ️ 仅检测到一块屏幕，使用主屏最大化")
            return ["--start-maximized"]

    except Exception as e:
        logger.warning(f"⚠️ 屏幕检测失败: {e}，使用默认配置（主屏最大化）")
        return ["--start-maximized"]


def get_launch_args():
    """
    获取浏览器启动参数
    优先使用用户手动配置的 LAUNCH_ARGS
    如果未配置且 AUTO_DETECT_SCREEN=True，则自动检测
    """
    # 如果用户手动配置了 launch_args，优先使用
    if LAUNCH_ARGS:
        logger.info(f"📌 使用手动配置的启动参数: {LAUNCH_ARGS}")
        return LAUNCH_ARGS

    # 如果启用了自动检测
    if AUTO_DETECT_SCREEN:
        return detect_screen_config()

    # 默认：主屏最大化
    return ["--start-maximized"]


# ---------- 添加自定义命令行参数 ----------
def pytest_addoption(parser):
    parser.addoption(
        "--headed",
        action="store_true",
        default=False,
        help="显示浏览器（非 headless 模式）"
    )
    parser.addoption(
        "--slowmo",
        action="store",
        type=int,
        default=0,
        help="每一步操作延迟（毫秒）"
    )
    parser.addoption(
        "--no-auto-screen",
        action="store_true",
        default=False,
        help="禁用自动屏幕检测（使用主屏）"
    )


# ---------- Session 级别：Playwright 实例 ----------
@pytest.fixture(scope="session")
def playwright_instance():
    with sync_playwright() as p:
        yield p


# ---------- Session 级别：浏览器 ----------
@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright, pytestconfig):
    """创建浏览器实例，支持多屏幕自动检测"""
    browser_type = getattr(playwright_instance, BROWSER)

    # 读取命令行参数
    headed = pytestconfig.getoption("--headed")
    headless = False if headed else HEADLESS

    slowmo = pytestconfig.getoption("--slowmo")
    if slowmo == 0:
        slowmo = SLOW_MO

    # 判断是否禁用自动屏幕检测
    no_auto_screen = pytestconfig.getoption("--no-auto-screen")

    # 获取启动参数
    if no_auto_screen:
        logger.info("📌 命令行指定 --no-auto-screen，使用主屏最大化")
        launch_args = ["--start-maximized"]
    else:
        launch_args = get_launch_args()

    # 构建启动选项
    launch_options = {
        "headless": headless,
        "slow_mo": slowmo,
        "args": launch_args
    }

    # 如果使用了全屏参数，viewport 交给浏览器控制
    if not any(arg in launch_args for arg in ["--kiosk", "--start-maximized"]):
        launch_options["viewport"] = VIEWPORT

    logger.info(f"🚀 启动浏览器: {BROWSER}, headless={headless}, slow_mo={slowmo}ms")
    logger.info(f"📐 启动参数: {launch_args}")

    browser = browser_type.launch(**launch_options)
    yield browser
    browser.close()
    logger.info("🔚 关闭浏览器")


# ---------- Function 级别：页面 ----------
@pytest.fixture(scope="function")
def page(browser: Browser, request):
    """创建新页面，失败时自动截图 + 录屏"""
    # 获取启动参数
    launch_args = get_launch_args()

    # 如果浏览器已经全屏，context 不需要再设置 viewport
    if any(arg in launch_args for arg in ["--kiosk", "--start-maximized"]):
        context = browser.new_context(
            record_video_dir="./reports/videos"
        )
    else:
        context = browser.new_context(
            viewport=VIEWPORT,
            record_video_dir="./reports/videos"
        )

    page = context.new_page()
    logger.info(f"📄 创建新页面: {request.node.name}")

    yield page

    # 检查测试是否失败
    failed = False
    if hasattr(request.node, 'rep_call'):
        failed = request.node.rep_call.failed if hasattr(request.node.rep_call, 'failed') else False

    if failed:
        logger.warning(f"❌ 测试失败: {request.node.name}，正在收集截图和录屏")
        try:
            screenshot_bytes = page.screenshot(full_page=True)
            allure.attach(
                screenshot_bytes,
                name=f"{request.node.name}_失败截图",
                attachment_type=allure.attachment_type.PNG
            )
            logger.info("📸 截图已附加到 Allure 报告")
        except Exception as e:
            logger.error(f"截图失败: {e}")

        context.close()
        video_path = page.video.path() if page.video else None
        if video_path and Path(video_path).exists():
            logger.info(f"🎬 录屏文件: {video_path}")
            with open(video_path, "rb") as f:
                video_bytes = f.read()
            allure.attach(
                video_bytes,
                name=f"{request.node.name}_失败录屏",
                attachment_type=allure.attachment_type.WEBM
            )
            logger.info("🎬 录屏已附加到 Allure 报告")
        else:
            logger.warning("未找到录屏文件")
    else:
        context.close()


# ---------- 基础 URL fixture ----------
@pytest.fixture(scope="function")
def ui_base_url():
    return UI_BASE_URL


# ---------- 登录页面 fixture ----------
@pytest.fixture(scope="function")
def login_page(page: Page, ui_base_url: str):
    return LoginPage(page, ui_base_url)


# ---------- 加载测试数据 ----------
@pytest.fixture(scope="session")
def ui_test_data():
    data_file = Path(__file__).parent.parent / "data" / "ui_test_data.yaml"
    with open(data_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


# ---------- Pytest 钩子 ----------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)


# ---------- 添加 Allure 环境信息 ----------
def pytest_sessionfinish(session, exitstatus):
    """在测试结束后生成 Allure 环境信息文件"""
    allure_env_path = Path("./reports/allure_results") / "environment.properties"
    allure_env_path.parent.mkdir(parents=True, exist_ok=True)

    import platform
    import sys
    from config.settings import BROWSER, HEADLESS, UI_BASE_URL, ENV

    env_info = {
        "测试环境": ENV if hasattr(ENV, 'value') else "test",
        "浏览器": BROWSER,
        "Headless": str(HEADLESS),
        "测试网站": UI_BASE_URL,
        "Python版本": sys.version.split()[0],
        "操作系统": platform.system(),
        "执行时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "Playwright版本": "1.49.0",  # 可以从 playwright.__version__ 获取
    }

    with open(allure_env_path, "w", encoding="utf-8") as f:
        for key, value in env_info.items():
            f.write(f"{key}={value}\n")

    logger.info(f"📊 Allure 环境信息已保存: {allure_env_path}")