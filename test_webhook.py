# test_webhook.py
import os
import requests

webhook = os.getenv("FEISHU_WEBHOOK_URL")

if not webhook:
    print("❌ 请先设置环境变量: $env:FEISHU_WEBHOOK_URL = '你的地址'")
    exit(1)

# 1. 测试纯文本消息
payload_text = {
    "msg_type": "text",
    "content": {"text": "🧪 测试消息：Webhook 连接成功！\n当前时间: 2026-07-02 11:30"}
}

# 2. 测试卡片消息（模拟“全部正常”的样式）
payload_card = {
    "msg_type": "interactive",
    "card": {
        "config": {"wide_screen_mode": True},
        "header": {
            "title": {"tag": "plain_text", "content": "✅ 网站健康检查通过"},
            "template": "green"
        },
        "elements": [
            {
                "tag": "div",
                "text": {
                    "tag": "lark_md",
                    "content": "**所有移民局网站均正常访问**\n\n- INZ 在线服务门户: ✅ 200\n- INZ 打工度假签证: ✅ 200\n- INZ 付款页面: ✅ 302\n\n🕐 检查时间: 2026-07-02 11:30"
                }
            }
        ]
    }
}

try:
    # 发送卡片消息（你想要测试的内容）
    resp = requests.post(webhook, json=payload_card, timeout=10)
    if resp.status_code == 200:
        print("✅ 测试卡片消息发送成功！请检查飞书群。")
    else:
        print(f"❌ 发送失败: {resp.status_code} - {resp.text}")
except Exception as e:
    print(f"❌ 异常: {e}")