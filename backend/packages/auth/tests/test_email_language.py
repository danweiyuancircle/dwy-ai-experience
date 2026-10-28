"""邮件语言只认有效且未排除的中文范围，其余回退英文。"""

import pytest


@pytest.mark.parametrize(
    "header,expected",
    [
        (None, "en"),
        ("", "en"),
        ("en-US", "en"),
        ("ja-JP", "en"),
        ("vi-VN", "en"),
        ("*", "en"),
        ("zh", "zh"),
        ("zh-CN", "zh"),
        ("ZH-hAnt-TW", "zh"),
        ("en-US, zh;q=0.2", "zh"),
        ("zh;q=0", "en"),
        ("zh;q=0.000, en;q=1", "en"),
        ("zh;q=0.001", "zh"),
        ("zh;q=invalid", "en"),
        ("zh;q=1.1", "en"),
        ("not-zh", "en"),
        ("zh-", "en"),
    ],
)
def test_resolve_email_language(header, expected):
    """含中文字符的任意字符串不能冒充有效语言标签。"""
    from dwy_auth.email_auth import resolve_email_language

    assert resolve_email_language(header) == expected
