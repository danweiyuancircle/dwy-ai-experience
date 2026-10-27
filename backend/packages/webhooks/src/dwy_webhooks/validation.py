"""不依赖平台 SDK 的目标校验，用于配置和可选发送器。"""

import re

DEFAULT_DISCORD_USERNAME = "Apple 应用通知"


def _display_name(value: str, maximum: int, message: str) -> str:
    """两个已使用的展示名称共享空白和控制字符约束，保留各自长度与稳定错误。"""
    if (not isinstance(value, str) or not 1 <= len(value) <= maximum or not value.strip()
            or any(ord(character) < 32 or ord(character) == 127 for character in value)):
        raise ValueError(message)
    return value


def validate_discord_username(value: str) -> str:
    """Discord 发送名称最多 80 字符，错误不回显输入。"""
    return _display_name(value, 80, "Invalid Discord username")


def validate_apple_app_name(value: str) -> str:
    """配置与独立格式化入口使用相同品牌约束，避免回调阶段才失败。"""
    return _display_name(value, 100, "Invalid Apple application name")


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
