# ============================================================
# 飞书通知模块
# 复用已有的 FEISHU_WEBHOOK_URL 环境变量
# ============================================================
import requests
import os
import sys
import json


def send_feishu_text(content: str, webhook_url: str = None) -> bool:
    """发送纯文本消息到飞书"""
    if not webhook_url:
        webhook_url = os.getenv("FEISHU_WEBHOOK_URL") or os.getenv("FEISHU_WEBHOOK")
    if not webhook_url:
        print("❌ 未配置 FEISHU_WEBHOOK_URL", file=sys.stderr)
        return False

    payload = {"msg_type": "text", "content": {"text": content}}
    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code == 200:
            print("✅ 飞书通知发送成功")
            return True
        else:
            print(f"❌ 飞书通知失败: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ 飞书通知异常: {e}")
        return False


def send_feishu_card(title: str, content: str, color: str = "green", webhook_url: str = None) -> bool:
    """发送卡片消息到飞书"""
    if not webhook_url:
        webhook_url = os.getenv("FEISHU_WEBHOOK_URL") or os.getenv("FEISHU_WEBHOOK")
    if not webhook_url:
        print("❌ 未配置 FEISHU_WEBHOOK_URL", file=sys.stderr)
        return False

    payload = {
        "msg_type": "interactive",
        "card": {
            "config": {"wide_screen_mode": True},
            "header": {
                "title": {"tag": "plain_text", "content": title},
                "template": color
            },
            "elements": [
                {
                    "tag": "div",
                    "text": {
                        "tag": "lark_md",
                        "content": content
                    }
                }
            ]
        }
    }

    try:
        resp = requests.post(webhook_url, json=payload, timeout=10)
        if resp.status_code == 200:
            print("✅ 飞书卡片发送成功")
            return True
        else:
            print(f"❌ 飞书卡片失败: {resp.status_code}")
            return False
    except Exception as e:
        print(f"❌ 飞书卡片异常: {e}")
        return False


if __name__ == "__main__":
    if len(sys.argv) > 1:
        send_feishu_text(sys.argv[1])
    else:
        print("用法: python notify.py <消息内容>")