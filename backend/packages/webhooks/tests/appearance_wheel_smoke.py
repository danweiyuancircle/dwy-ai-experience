"""仓库外从本轮实际 wheel 验证展示 API 与业务模块边界，无真实消息投递。"""

import asyncio
import importlib.util
import sys
from pathlib import Path
from unittest.mock import patch

import dwy_notify
import requests
from dwy_notify import NotificationAppearance, NotificationConfig, Notifier

import dwy_webhooks
from dwy_webhooks.appearance import notification_appearance
from dwy_webhooks.config import NotificationSettings
from dwy_webhooks.notifications import configured_notifier, legacy_discord_config


async def main():
    """检查导入归属、新能力与实际 HTTP JSON，不以旧安装版本号自证新能力。"""
    for module in (dwy_notify, dwy_webhooks):
        assert Path(module.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    for name in ("app_cloud", "apple_iap", "resend", "appstoreserverlibrary", "discord_webhook"):
        assert importlib.util.find_spec(name) is None, name
    seen = []

    def post(url, **kwargs):
        seen.append(kwargs["json"])
        response = requests.Response()
        response.status_code = 200
        response._content = b'{"id": "123456789012345679"}'
        return response

    notifier = Notifier(NotificationConfig(targets={"ops": "discord://123456789/wheel-test-token"}))
    with patch("dwy_notify._transport.post", post):
        try:
            await notifier.send("缺少名称")
        except ValueError as error:
            assert str(error) == "missing_username"
        else:
            raise AssertionError("Unnamed messages must fail before network access")
        assert seen == []
        result = await notifier.send("默认头像", appearance=NotificationAppearance(username="系统通知"))
        assert result.success
        assert "avatar_url" not in seen[-1] and seen[-1]["username"] == "系统通知"
        for source, name in (
            ("apple_notifications", "购买通知"), ("app_store_connect", "应用审核通知"),
            ("app_store_analytics", "经营报表"), ("resend", "邮件通知"), ("other", "系统通知"),
        ):
            assert (await notifier.send("预设", default_appearance=notification_appearance(source))).success
            assert seen[-1]["username"] == name
            assert seen[-1]["avatar_url"].startswith("https://raw.githubusercontent.com/")
        result = await notifier.send(
            "覆盖", default_appearance=notification_appearance("resend"),
            appearance=NotificationAppearance(username="自定义", avatar_url=None),
        )
        assert result.success
        assert seen[-1]["username"] == "自定义" and "avatar_url" not in seen[-1]
        url = "https://discord.com/api/webhooks/123456789/wheel-test-token"
        old = Notifier(legacy_discord_config(url))
        upgraded = configured_notifier(NotificationSettings(discord_webhook_url=url))
        assert old.target_fingerprint("discord") == upgraded.target_fingerprint("discord")
        assert (await upgraded.send("旧配置", default_appearance=notification_appearance("resend"))).success
        assert seen[-1]["username"] == "邮件通知"
    print("actual wheels: isolated imports, platform default, "
          "five module presets and custom overrides passed")


if __name__ == "__main__":
    asyncio.run(main())
