"""不依赖平台 SDK 的目标校验，用于配置和可选发送器。"""

import re

DEFAULT_DISCORD_USERNAME = "Apple 应用通知"


def validate_discord_username(value: str) -> str:
    """在发送前拒绝空名称、超长名称和控制字符，错误不回显输入。"""
    if (not isinstance(value, str) or not 1 <= len(value) <= 80 or not value.strip()
            or any(ord(character) < 32 or ord(character) == 127 for character in value)):
        raise ValueError("Invalid Discord username")
    return value


def paths_overlap(left: str, right: str) -> bool:
    """已校验路径仅有末尾 app_id 参数，静态与模板同形时必须拒绝。"""
    first, second = left.split("/"), right.split("/")
    return len(first) == len(second) and all(
        a == b or a == "{app_id}" or b == "{app_id}" for a, b in zip(first, second, strict=True)
    )


def validate_discord_webhook_url(value: str) -> str:
    """只接受官方 HTTPS 地址，不回显无效输入中的凭据。"""
    if not isinstance(value, str) or re.fullmatch(
        r"https://discord\.com/api/(?:v10/)?webhooks/[0-9]+/[A-Za-z0-9_-]+", value
    ) is None:
        raise ValueError("discord_webhook_url requires an official Discord HTTPS webhook URL")
    return value
