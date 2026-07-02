# ============================================================
# 网站健康检查脚本（新西兰移民局）
# ============================================================
import requests
import json
import logging
import os
import sys
import time
from datetime import datetime
from pathlib import Path

# ---------- 配置 ----------
URLS = [
    {
        "name": "INZ 在线服务门户",
        "url": "https://onlineservices.immigration.govt.nz/"
    },
    {
        "name": "INZ 打工度假签证",
        "url": "https://onlineservices.immigration.govt.nz/WorkingHoliday/"
    },
    {
        "name": "INZ 付款页面",
        "url": "https://onlineservices.immigration.govt.nz/PaymentGateway/OnLinePayment.aspx?SourceUrl=//onlineservices.immigration.govt.nz/WorkingHoliday/Application/SubmitConfirmation.aspx?ApplicationId=3950366&ProductId=2&Token=LctQ9Y5g+5WanrJmA6S2WZ1Wh+x0uJrShXkeXYFpMHIInIjP2w8fOC6w+Dx3Yt0q9a9wXceWv0I="
    }
]

TIMEOUT = 30
CONNECT_TIMEOUT = 10
MAX_RETRIES = 2
RETRY_DELAY = 2
REPORT_DIR = Path("./reports/health_check")

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(levelname)s | %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)


def shorten_url(url: str) -> str:
    short = url.replace("https://", "").replace("http://", "")
    if "/" in short:
        short = short.split("/")[0]
    return short


def build_progress_bar(rate: float, length: int = 10) -> str:
    filled = int(round(rate / 100 * length))
    filled = max(0, min(filled, length))
    return "▓" * filled + "░" * (length - filled)


def pad_text(text: str, width: int) -> str:
    visible_width = 0
    for ch in text:
        if ord(ch) > 127:
            visible_width += 2
        else:
            visible_width += 1
    padding = max(0, width - visible_width)
    return text + " " * padding


def send_feishu_card_smart(results: list):
    webhook = os.getenv("FEISHU_WEBHOOK_URL")
    if not webhook:
        logger.warning("⚠️ 未配置 FEISHU_WEBHOOK_URL，跳过飞书通知")
        return

    total = len(results)
    failures = [r for r in results if not r["healthy"]]
    healthy = total - len(failures)
    pass_rate = round(healthy / total * 100) if total > 0 else 0

    is_all_healthy = len(failures) == 0
    status_color = "green" if is_all_healthy else "red"
    status_icon = "✅" if is_all_healthy else "⚠️"
    status_text = "网站健康检查通过" if is_all_healthy else "网站健康检查失败"

    name_width = max(8, max(len(r["name"]) for r in results))
    url_width = max(6, max(len(shorten_url(r["url"])) for r in results))

    header = f"{pad_text('网站名称', name_width)}  {pad_text('地址', url_width)}  状态    响应时间"
    separator = "─" * (name_width + url_width + 20)

    rows = []
    for r in results:
        name = pad_text(r["name"], name_width)
        url = pad_text(shorten_url(r["url"]), url_width)
        if r["healthy"]:
            status = f"✅ {r['status_code']}"
            time_str = f"{r['response_time']}s"
        else:
            status = f"❌ {r.get('status_code', 'N/A')}"
            time_str = f"{r.get('response_time', '-')}s"
        rows.append(f"{name}  {url}  {status}    {time_str}")

    table_content = f"```\n{header}\n{separator}\n" + "\n".join(rows) + "\n```"

    bar = build_progress_bar(pass_rate, 10)
    bar_display = f"📈 **通过率**: {pass_rate}%  {bar}"

    error_details = ""
    if failures:
        error_lines = []
        for f in failures:
            short_url = shorten_url(f["url"])
            error_msg = f.get("error", f"HTTP {f.get('status_code', 'N/A')}")
            error_lines.append(f"  · {f['name']} ({short_url}): {error_msg}")
        error_details = "🔴 **异常详情**\n" + "\n".join(error_lines)

    if is_all_healthy:
        suggestion = "🎉 所有服务运行正常"
    elif pass_rate >= 50:
        suggestion = "⚠️ 部分服务异常，建议检查相关服务状态"
    else:
        suggestion = "🚨 大部分服务不可用，请立即排查"

    content = f"""{table_content}

{bar_display}

{error_details}

💡 **建议**: {suggestion}

🕐 **检查时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""

    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": f"{status_icon} {status_text}"},
                "template": status_color
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                },
                {
                    "tag": "note",
                    "elements": [
                        {
                            "tag": "plain_text",
                            "content": f"🤖 GitHub Actions · {total}个网站 · 异常{failures and f' {len(failures)}个' or ' 0个'}"
                        }
                    ]
                }
            ]
        }
    }

    try:
        resp = requests.post(webhook, json=payload, timeout=10)
        if resp.status_code == 200:
            logger.info("✅ 飞书卡片发送成功")
        else:
            logger.error(f"❌ 飞书卡片发送失败: {resp.status_code}")
    except Exception as e:
        logger.error(f"❌ 飞书卡片异常: {e}")


def check_url(name: str, url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
        "Connection": "keep-alive",
    }

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            start = datetime.now()
            resp = requests.get(url, headers=headers, timeout=(CONNECT_TIMEOUT, TIMEOUT), allow_redirects=True)
            elapsed = round((datetime.now() - start).total_seconds(), 2)

            if resp.status_code in [200, 302, 303, 307, 308]:
                logger.info(f"✅ {name} - {resp.status_code} ({elapsed}s)")
                return {
                    "name": name,
                    "url": url,
                    "healthy": True,
                    "status_code": resp.status_code,
                    "response_time": elapsed,
                    "error": None,
                }
            else:
                logger.warning(f"⚠️ {name} - {resp.status_code} (尝试 {attempt}/{MAX_RETRIES})")
                if attempt < MAX_RETRIES:
                    time.sleep(RETRY_DELAY)

        except requests.exceptions.Timeout:
            logger.warning(f"⏱️ {name} - 超时 (尝试 {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)
        except Exception as e:
            logger.warning(f"❌ {name} - {str(e)[:50]} (尝试 {attempt}/{MAX_RETRIES})")
            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY)

    return {
        "name": name,
        "url": url,
        "healthy": False,
        "status_code": None,
        "response_time": None,
        "error": "所有重试均失败",
    }


def main():
    logger.info("=" * 60)
    logger.info("检查新西兰移民局网站")
    logger.info(f"超时: 连接{CONNECT_TIMEOUT}s, 读取{TIMEOUT}s, 最大重试: {MAX_RETRIES} 次")
    logger.info("=" * 60)

    results = [check_url(item["name"], item["url"]) for item in URLS]

    failures = [r for r in results if not r["healthy"]]

    logger.info("=" * 60)
    logger.info(f"📊 总数: {len(results)}, 正常: {len(results)-len(failures)}, 异常: {len(failures)}")
    logger.info("=" * 60)

    send_feishu_card_smart(results)

    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    with open(REPORT_DIR / f"health_check_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", "w") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()