"""不依赖平台 SDK 的目标校验，用于配置和可选发送器。"""

def validate_apple_app_name(value: str) -> str:
    """配置与独立格式化入口使用相同品牌约束，避免回调阶段才失败。"""
    if (not isinstance(value, str) or not 1 <= len(value) <= 100 or not value.strip()
            or any(ord(character) < 32 or ord(character) == 127 for character in value)):
        raise ValueError("Invalid Apple application name")
    return value
