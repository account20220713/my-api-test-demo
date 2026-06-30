import os
import sys
import subprocess
import time
import shutil
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent
REPORT_DIR = PROJECT_ROOT / "reports" / "allure_results"
HTML_REPORT_DIR = PROJECT_ROOT / "reports" / "allure_html"
CUSTOM_LOGO = PROJECT_ROOT / "custom_logo.png"
CATEGORIES_FILE = PROJECT_ROOT / "categories.json"
EXECUTOR_FILE = PROJECT_ROOT / "executor.json"


def print_header(title):
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60 + "\n")


def run_tests(smoke=False, module=None):
    print_header("🚀 开始执行接口自动化测试")
    cmd = ["pytest", "-v", "--alluredir", str(REPORT_DIR)]
    if smoke:
        cmd += ["-m", "smoke"]
        print("📌 执行模式: 冒烟测试")
    else:
        print("📌 执行模式: 全量回归测试")
    if module:
        cmd.append(f"testcases/{module}.py")
        print(f"📌 指定模块: {module}")
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    start_time = time.time()
    result = subprocess.run(cmd, cwd=PROJECT_ROOT)
    elapsed = time.time() - start_time
    print(f"\n⏱️  测试执行耗时: {elapsed:.2f} 秒")
    print("✅ 测试执行完成")
    return result.returncode


def check_allure_installed():
    try:
        subprocess.run("allure --version", shell=True, capture_output=True, check=True)
        return True
    except:
        return False


def generate_allure_report():
    print_header("📊 正在生成 Allure 报告")
    if not check_allure_installed():
        print("❌ 未安装 allure 命令行工具")
        return False

    # 复制 categories.json
    if CATEGORIES_FILE.exists():
        shutil.copy(CATEGORIES_FILE, REPORT_DIR / "categories.json")
        print("✅ 已加载 categories.json")

    # 复制 executor.json
    if EXECUTOR_FILE.exists():
        shutil.copy(EXECUTOR_FILE, REPORT_DIR / "executor.json")
        print("✅ 已加载 executor.json")

    # 生成报告
    cmd = f"allure generate {str(REPORT_DIR)} -o {str(HTML_REPORT_DIR)} --clean"
    if CUSTOM_LOGO.exists():
        cmd += f" --logo {str(CUSTOM_LOGO)}"
        print("✅ 已加载自定义 Logo")

    subprocess.run(cmd, cwd=PROJECT_ROOT, shell=True)
    print(f"✅ 报告已生成: {HTML_REPORT_DIR}")
    return True


def open_allure_report():
    print_header("🌐 正在打开 Allure 报告")
    if not check_allure_installed():
        return False
    env = os.environ.copy()
    env["ALLURE_LANGUAGE"] = "zh"
    try:
        subprocess.Popen(
            f"allure open {str(HTML_REPORT_DIR)}",
            cwd=PROJECT_ROOT,
            env=env,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            shell=True
        )
        print("✅ 报告已在浏览器中打开（中文界面）")
        return True
    except Exception as e:
        print(f"❌ 打开报告失败: {e}")
        return False


def generate_html_report():
    print_header("📄 生成 HTML 报告（备用方案）")
    try:
        import pytest_html
    except ImportError:
        subprocess.run("pip install pytest-html", shell=True, cwd=PROJECT_ROOT)
    subprocess.run(
        "pytest testcases/ -v --html=./reports/test_report.html --self-contained-html",
        cwd=PROJECT_ROOT,
        shell=True
    )
    print("\n📄 HTML 报告已生成: ./reports/test_report.html")


def main():
    print("""
╔══════════════════════════════════════════════════════════════╗
║                                                              ║
║   接口自动化测试框架 - 一键执行脚本                         ║
║                                                              ║
║   用法:                                                      ║
║     python run.py              # 全量测试                   ║
║     python run.py --smoke      # 冒烟测试                   ║
║     python run.py -m test_login # 指定模块                  ║
║                                                              ║
╚══════════════════════════════════════════════════════════════╝
    """)
    smoke = "--smoke" in sys.argv or "-s" in sys.argv
    module = None
    for i, arg in enumerate(sys.argv):
        if arg in ("-m", "--module") and i + 1 < len(sys.argv):
            module = sys.argv[i + 1]

    exit_code = run_tests(smoke=smoke, module=module)
    if exit_code == 5:
        print("\n⚠️  没有找到测试用例")
        sys.exit(1)

    if generate_allure_report() and HTML_REPORT_DIR.exists():
        open_allure_report()
    else:
        generate_html_report()

    print("\n" + "=" * 60)
    print("  🎉 全部完成！")
    print("=" * 60)


if __name__ == "__main__":
    main()