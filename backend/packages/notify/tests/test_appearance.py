"""核对实际 Discord JSON 的展示覆盖与平台默认，不访问真实平台。"""

import asyncio
import json
from unittest.mock import Mock

import pytest
import requests
from pydantic import ValidationError

from dwy_notify import NotificationAppearance, NotificationConfig, Notifier

DISCORD = "discord://123456789012345678/offline-appearance-token"
ICON = "https://example.com/purchase.png"


@pytest.fixture
def post(monkeypatch):
    response = requests.Response()
    response.status_code = 200
    response._content = json.dumps({"id": "123456789012345679"}).encode()
    mocked = Mock(return_value=response)
    monkeypatch.setattr("dwy_notify._transport.post", mocked)
    return mocked


@pytest.mark.parametrize("targets", [
    {"ops": DISCORD}, {"ops": "wecombot://offline-key"},
    {"named": DISCORD.replace("discord://", "discord://URLName@"), "missing": DISCORD},
])
async def test_missing_username_is_rejected_before_any_target_request(post, targets):
    notifier = Notifier(NotificationConfig(targets=targets))
    with pytest.raises(ValueError, match="missing_username"):
        await notifier.send("消息", title="正文标题不能代替发送者名称")
    post.assert_not_called()


async def test_required_username_with_optional_avatar_uses_platform_default_avatar(post):
    notifier = Notifier(NotificationConfig(
        targets={"ops": DISCORD}, appearance=NotificationAppearance(username="系统通知"),
    ))
    result = await notifier.send("消息")
    assert result.success
    assert "avatar_url" not in post.call_args.kwargs["json"]
    assert post.call_args.kwargs["json"]["username"] == "系统通知"


async def test_per_field_override_and_explicit_null_avatar_preserve_required_name(post):
    notifier = Notifier(NotificationConfig(
        targets={"ops": DISCORD}, appearance=NotificationAppearance(username="业务通知"),
    ))
    preset = NotificationAppearance(username="购买通知", avatar_url=ICON)
    await notifier.send("消息", default_appearance=preset)
    assert post.call_args.kwargs["json"]["username"] == "业务通知"
    assert post.call_args.kwargs["json"]["avatar_url"] == ICON
    await notifier.send("消息", default_appearance=preset,
                        appearance=NotificationAppearance(avatar_url=None))
    assert post.call_args.kwargs["json"]["username"] == "业务通知"
    assert "avatar_url" not in post.call_args.kwargs["json"]


async def test_explicit_target_url_is_preserved_below_application_override(post):
    notifier = Notifier(NotificationConfig(targets={
        "ops": DISCORD.replace("discord://", "discord://URLName@") + "?avatar=no",
    }))
    preset = NotificationAppearance(username="购买通知", avatar_url=ICON)
    await notifier.send("消息", default_appearance=preset)
    assert post.call_args.kwargs["json"]["username"] == "URLName"
    assert "avatar_url" not in post.call_args.kwargs["json"]
    await notifier.send("消息", appearance=NotificationAppearance(username="单次", avatar_url=ICON))
    assert post.call_args.kwargs["json"]["username"] == "单次"
    assert post.call_args.kwargs["json"]["avatar_url"] == ICON


async def test_explicit_apprise_avatar_is_preserved_below_application_override(post):
    notifier = Notifier(NotificationConfig(
        targets={"ops": DISCORD + "?avatar=yes"}, appearance=NotificationAppearance(username="系统通知"),
    ))
    await notifier.send("消息", default_appearance=NotificationAppearance(avatar_url=ICON))
    assert "caronc/apprise" in post.call_args.kwargs["json"]["avatar_url"]
    await notifier.send("消息", appearance=NotificationAppearance(avatar_url=None))
    assert "avatar_url" not in post.call_args.kwargs["json"]


async def test_concurrent_messages_do_not_share_appearance_or_change_target_fingerprint(post):
    notifier = Notifier(NotificationConfig(targets={"ops": DISCORD}))
    before = notifier.target_fingerprint("ops")
    await asyncio.gather(*(
        notifier.send(f"消息{i}", appearance=NotificationAppearance(
            username=f"名称{i}", avatar_url=f"https://example.com/{i}.png",
        )) for i in range(12)
    ))
    for call in post.call_args_list:
        payload = call.kwargs["json"]
        index = payload["content"].removeprefix("消息")
        assert payload["username"] == f"名称{index}"
        assert payload["avatar_url"] == f"https://example.com/{index}.png"
    assert notifier.target_fingerprint("ops") == before
    with pytest.raises(ValueError, match="missing_username"):
        await notifier.send("无预设")
    await notifier.send("无头像", appearance=NotificationAppearance(username="系统通知"))
    assert "avatar_url" not in post.call_args.kwargs["json"]


@pytest.mark.parametrize("values", [
    {"username": None}, {"username": ""}, {"username": "a" * 81}, {"username": "bad\nname"},
    {"avatar_url": "http://example.com/icon.png"},
    {"avatar_url": "file:///tmp/icon.png"},
    {"avatar_url": "https://user:password@example.com/icon.png"},
])
def test_appearance_rejects_invalid_external_values(values):
    with pytest.raises(ValidationError):
        NotificationAppearance(**values)


async def test_other_channels_accept_appearance_without_discord_fields(post):
    post.return_value._content = b'{"errcode": 0}'
    notifier = Notifier(NotificationConfig(targets={"ops": "wecombot://offline-key"}))
    assert (await notifier.send("消息", appearance=NotificationAppearance(
        username="名称", avatar_url=ICON,
    ))).success
    assert post.call_args.kwargs["json"] == {"msgtype": "text", "text": {"content": "消息"}}
