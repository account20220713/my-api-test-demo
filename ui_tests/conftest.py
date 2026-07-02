# ============================================================
# UI 测试的 Pytest 配置（完整版：每步截图 + 高清录屏）
# ============================================================
import pytest
import allure
import yaml
import re
import shutil
from pathlib import Path
from datetime import datetime
from playwright.sync_api import Browser, Page
from config.settings import (
    BROWSER, HEADLESS, VIEWPORT, UI_BASE_URL, UI_TIMEOUT,
    SLOW_MO, LAUNCH_ARGS, AUTO_DETECT_SCREEN
)
from common.logger import logger

# ---------- 辅助函数 ----------
def sanitize_filename(filename: str) -> str:
    illegal_chars = r'[<>:"/\\|?*\[\]\{\}\(\)\s]'
    cleaned = re.sub(illegal_chars, '_', filename)
    cleaned = re.sub(r'_+', '_', cleaned)
    return cleaned.strip('_') or "test_case"

def get_test_case_name(request) -> str:
    node_name = request.node.name
    node_name = re.sub(r'[\[\]]', '_', node_name)
    return sanitize_filename(node_name)

def get_timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def get_date_dir() -> str:
    return datetime.now().strftime("%Y-%m-%d")

# ---------- 截图计数器 ----------
_screenshot_counter = {}

def get_next_screenshot_index(test_name: str) -> int:
    if test_name not in _screenshot_counter:
        _screenshot_counter[test_name] = 1
    idx = _screenshot_counter[test_name]
    _screenshot_counter[test_name] += 1
    return idx

def reset_screenshot_counter(test_name: str):
    _screenshot_counter[test_name] = 1

def save_step_screenshot(page: Page, test_name: str, status: str, step_desc: str) -> Path:
    """
    保存每一步的截图到用例专属文件夹
    命名格式：{序号}_{步骤描述}_{时间戳}.png
    """
    date_dir = get_date_dir()
    case_dir = Path("./reports/screenshots") / date_dir / f"{test_name}_{status}"
    case_dir.mkdir(parents=True, exist_ok=True)

    idx = get_next_screenshot_index(test_name)
    clean_desc = sanitize_filename(step_desc)
    if len(clean_desc) > 30:
        clean_desc = clean_desc[:30]
    filename = f"{idx:02d}_{clean_desc}_{get_timestamp()}.png"
    filepath = case_dir / filename

    try:
        page.screenshot(full_page=True, path=str(filepath))
        logger.debug(f"📸 步骤截图已保存: {filepath}")
    except Exception as e:
        logger.error(f"步骤截图保存失败: {e}")

    return filepath

def save_final_screenshot(page: Page, test_name: str, status: str) -> Path:
    date_dir = get_date_dir()
    case_dir = Path("./reports/screenshots") / date_dir / f"{test_name}_{status}"
    case_dir.mkdir(parents=True, exist_ok=True)
    filename = f"99_最终状态_{get_timestamp()}.png"
    filepath = case_dir / filename
    try:
        page.screenshot(full_page=True, path=str(filepath))
        logger.info(f"📸 最终截图已保存: {filepath}")
    except Exception as e:
        logger.error(f"最终截图保存失败: {e}")
    return filepath

def save_video(page: Page, test_name: str, status: str) -> Path:
    video = page.video
    if not video:
        return None
    try:
        video_path = video.path()
        if not video_path or not Path(video_path).exists():
            return None
        date_dir = get_date_dir()
        videos_dir = Path("./reports/videos") / date_dir
        videos_dir.mkdir(parents=True, exist_ok=True)
        filename = f"{test_name}_{status}_{get_timestamp()}.webm"
        target_path = videos_dir / filename
        shutil.move(str(video_path), str(target_path))
        logger.info(f"🎬 录屏已保存: {target_path}")
        return target_path
    except Exception as e:
        logger.error(f"录屏保存失败: {e}")
        return None

# ---------- 屏幕检测 ----------
try:
    from screeninfo import get_monitors
    SCREENINFO_AVAILABLE = True
except ImportError:
    SCREENINFO_AVAILABLE = False
    logger.warning("⚠️ screeninfo 未安装，无法自动检测屏幕。")

def detect_screen_config():
    if not SCREENINFO_AVAILABLE:
        return ["--start-maximized"]
    try:
        monitors = get_monitors()
        logger.info(f"检测到 {len(monitors)} 块屏幕")
        if len(monitors) >= 2:
            sorted_monitors = sorted(monitors, key=lambda m: m.x)
            if sorted_monitors[0].x == 0 and sorted_monitors[0].y == 0:
                second_screen = sorted_monitors[1]
            else:
                second_screen = sorted_monitors[-1]
            logger.info(f"✅ 第二块屏幕: {second_screen.width}x{second_screen.height} 位置: ({second_screen.x}, {second_screen.y})")
            return [f"--window-position={second_screen.x},{second_screen.y}", "--start-maximized"]
        else:
            logger.info("ℹ️ 仅一块屏幕，使用主屏最大化")
            return ["--start-maximized"]
    except Exception as e:
        logger.warning(f"⚠️ 屏幕检测失败: {e}")
        return ["--start-maximized"]

def get_launch_args():
    if LAUNCH_ARGS:
        logger.info(f"📌 使用手动配置: {LAUNCH_ARGS}")
        return LAUNCH_ARGS
    if AUTO_DETECT_SCREEN:
        return detect_screen_config()
    return ["--start-maximized"]

# ---------- 自定义命令行参数 ----------
def pytest_addoption(parser):
    parser.addoption("--no-auto-screen", action="store_true", default=False, help="禁用自动屏幕检测")

# ---------- 覆盖浏览器启动参数 ----------
@pytest.fixture(scope="session")
def browser_type_launch_args(pytestconfig):
    no_auto = pytestconfig.getoption("--no-auto-screen")
    launch_args = ["--start-maximized"] if no_auto else get_launch_args()
    launch_options = {
        "headless": HEADLESS if not pytestconfig.getoption("--headed") else False,
        "slow_mo": SLOW_MO,
        "args": launch_args,
    }
    return launch_options

# ---------- 登录 Cookies（session 级别） ----------
@pytest.fixture(scope="session")
def login_cookies(browser: Browser):
    context = browser.new_context()
    page = context.new_page()
    logger.info("🔐 执行登录（仅一次）...")
    page.goto(UI_BASE_URL)
    page.fill("#user-name", "standard_user")
    page.fill("#password", "secret_sauce")
    page.click("#login-button")
    page.wait_for_url("**/inventory.html", timeout=10000)
    cookies = context.cookies()
    page.close()
    context.close()
    logger.info(f"✅ Cookies 已保存，共 {len(cookies)} 条")
    return cookies

# ---------- 已登录的页面（function 级别，隔离） ----------
@pytest.fixture(scope="function")
def logged_in_page(browser: Browser, login_cookies, request):
    """
    每个用例独立上下文，通过 Cookies 保持登录态
    每一步操作都会自动截图到用例专属文件夹
    """
    context = browser.new_context(
        viewport=VIEWPORT,
        record_video_dir="./reports/videos",
        record_video_size={"width": 1280, "height": 720}
    )
    context.add_cookies(login_cookies)
    page = context.new_page()
    page.goto(UI_BASE_URL + "inventory.html")
    test_name = get_test_case_name(request)

    # 重置截图计数器
    reset_screenshot_counter(test_name)

    # 将 test_name 附加到 page 对象，供 UIBasePage 使用
    page._test_name = test_name

    logger.info(f"📄 创建独立页面（已登录）: {test_name}")

    yield page

    # 判断测试状态
    failed = False
    if hasattr(request.node, 'rep_call'):
        failed = request.node.rep_call.failed if hasattr(request.node.rep_call, 'failed') else False
    status = "失败" if failed else "成功"

    # ----- 1. 保存最终状态截图 -----
    try:
        final_path = save_final_screenshot(page, test_name, status)
        if final_path and final_path.exists():
            with open(final_path, "rb") as f:
                allure.attach(f.read(), name=f"{test_name}_{status}_最终状态", attachment_type=allure.attachment_type.PNG)
    except Exception as e:
        logger.error(f"最终截图处理失败: {e}")

    # ----- 2. 关闭上下文（视频落盘） -----
    context.close()

    # ----- 3. 录屏处理 -----
    try:
        v_path = save_video(page, test_name, status)
        if v_path and v_path.exists():
            with open(v_path, "rb") as f:
                allure.attach(f.read(), name=f"{test_name}_{status}录屏", attachment_type=allure.attachment_type.WEBM)
    except Exception as e:
        logger.error(f"录屏处理失败: {e}")

    logger.info(f"✅ 测试完成: {test_name}, 状态: {status}")

# ---------- 登录页面 fixture（用于测试登录功能本身） ----------
@pytest.fixture(scope="function")
def login_page(page: Page):
    from ui_tests.page_objects.login_page import LoginPage
    return LoginPage(page)

# ---------- 其他 fixtures ----------
@pytest.fixture(scope="function")
def ui_base_url():
    return UI_BASE_URL

@pytest.fixture(scope="session")
def ui_test_data():
    data_file = Path(__file__).parent.parent / "data" / "ui_test_data.yaml"
    with open(data_file, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)

# ---------- Allure 环境信息 ----------
def pytest_sessionfinish(session, exitstatus):
    allure_env_path = Path("./reports/allure_results") / "environment.properties"
    allure_env_path.parent.mkdir(parents=True, exist_ok=True)
    import platform, sys
    from config.settings import ENV

    env_info = {
        "测试环境": ENV,
        "浏览器": BROWSER,
        "Headless": str(HEADLESS),
        "测试网站": UI_BASE_URL,
        "超时时间(秒)": str(UI_TIMEOUT),
        "操作延迟(ms)": str(SLOW_MO),
        "Python版本": sys.version.split()[0],
        "操作系统": platform.system() + " " + platform.release(),
        "执行时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "测试框架": "pytest + playwright",
        "报告生成时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    # ⭐ 关键修复：指定 encoding='utf-8'，并确保文件以 UTF-8 写入
    with open(allure_env_path, "w", encoding="utf-8") as f:
        for k, v in env_info.items():
            f.write(f"{k}={v}\n")

    logger.info(f"📊 Allure 环境信息已保存: {allure_env_path}")

# ---------- Pytest 钩子 ----------
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    setattr(item, "rep_" + rep.when, rep)