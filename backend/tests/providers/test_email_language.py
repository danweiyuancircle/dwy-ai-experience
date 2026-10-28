"""邮件语言逐次传入;主题、HTML 与纯文本必须保持同一种语言。"""

import asyncio
import re
from unittest.mock import AsyncMock

import pytest

from dwyeapi.providers.email import EmailSettings, ResendConfig, make_email_provider
from dwyeapi.providers.email.resend import ResendEmailProvider


@pytest.mark.parametrize("language", [None, "en", "zh"])
async def test_language_selects_complete_message(language, monkeypatch, fake_redis):
    """漏传语言默认英文;显式中文保留中文主题与两种正文。"""
    provider = ResendEmailProvider(
        api_key="re_test",
        from_email="from@example.com",
        brand_name="Example",
        support_email="support@example.com",
        redis=fake_redis,
    )
    sender = AsyncMock(return_value={"id": "message"})
    monkeypatch.setattr(provider._resend.Emails, "send_async", sender)
    kwargs = {} if language is None else {"language": language}
    assert await provider.send_code("person@gmail.com", **kwargs)
    params = sender.await_args.args[0]
    code = await fake_redis.get("dwyeapi:email:code:person@gmail.com")
    if isinstance(code, bytes):
        code = code.decode()
    assert code in params["html"] and code in params["text"]
    if language == "zh":
        assert params["subject"] == "验证码"
        assert '<html lang="zh-CN">' in params["html"]
        assert "您正在进行身份验证" in params["html"]
        assert "5 分钟内有效" in params["text"]
        assert "如有疑问,请联系客服:" in params["html"]
    else:
        assert params["subject"] == "Verification code"
        assert '<html lang="en">' in params["html"]
        assert "Verify your identity" in params["html"]
        assert "5 minutes" in params["html"] and "5 minutes" in params["text"]
        assert "Do not share" in params["html"] and "Do not share" in params["text"]
        assert "support@example.com" in params["html"] and "support@example.com" in params["text"]
        assert not re.search(r"[\u4e00-\u9fff]", params["html"] + params["text"])


async def test_concurrent_languages_do_not_change_shared_provider(monkeypatch):
    """同一实例交错发信,各请求自己的语言和验证码保持一致。"""
    provider = ResendEmailProvider(api_key="re_test", from_email="from@example.com")
    sent = []

    async def deliver(params):
        await asyncio.sleep(0)
        sent.append(params)
        return {"id": "message"}

    monkeypatch.setattr(provider._resend.Emails, "send_async", deliver)
    assert all(
        await asyncio.gather(
            provider.send_verification_code("zh@gmail.com", "123456", language="zh"),
            provider.send_verification_code("en@gmail.com", "654321", language="en"),
        )
    )
    messages = {message["to"][0]: message for message in sent}
    chinese, english = messages["zh@gmail.com"], messages["en@gmail.com"]
    assert chinese["subject"] == "验证码" and "123456" in chinese["html"]
    assert "您正在进行身份验证" in chinese["text"]
    assert english["subject"] == "Verification code" and "654321" in english["html"]
    assert "Verify your identity" in english["text"]


async def test_factory_forwards_localized_subject_and_brand_copy(monkeypatch):
    """英文配置独立透传;缺省不回退到中文品牌宣传文案。"""
    settings = EmailSettings(
        brand_name="Example",
        brand_tagline="中文副标语",
        brand_slogan="中文页脚",
        brand_tagline_en="English tagline",
        brand_slogan_en="English footer",
        resend=ResendConfig(
            api_key="re_test",
            from_email="from@example.com",
            subject="自定义验证码",
            subject_en="Your Example code",
        ),
    )
    provider = make_email_provider(settings)
    sender = AsyncMock(return_value={"id": "message"})
    monkeypatch.setattr(provider._resend.Emails, "send_async", sender)
    assert await provider.send_verification_code("person@gmail.com", "123456", language="en")
    params = sender.await_args.args[0]
    assert params["subject"] == "Your Example code"
    assert "English tagline" in params["html"] and "English footer" in params["html"]
    assert "中文副标语" not in params["html"] and "中文页脚" not in params["html"]
    assert await provider.send_verification_code("person@gmail.com", "123456", language="zh")
    params = sender.await_args.args[0]
    assert params["subject"] == "自定义验证码"
    assert "中文副标语" in params["html"] and "中文页脚" in params["html"]


def test_english_omits_untranslated_tagline_and_slogan():
    """未提供英文品牌宣传文案时直接省略,保留品牌名。"""
    provider = ResendEmailProvider(
        api_key="re_test",
        from_email="from@example.com",
        brand_name="Example",
        brand_tagline="中文副标语",
        brand_slogan="中文页脚",
    )
    html = provider._render_code_html("123456")
    assert "Example" in html
    assert "中文副标语" not in html and "中文页脚" not in html


@pytest.mark.parametrize("language", ["zh", "en"])
def test_localized_html_escapes_brand_and_code(language):
    """翻译不得改变模板的动态文案转义约束。"""
    provider = ResendEmailProvider(
        api_key="re_test",
        from_email="from@example.com",
        brand_name='<script>"Example"</script>',
        brand_tagline="<tag>",
        brand_tagline_en="<tag>",
        brand_slogan="<footer>",
        brand_slogan_en="<footer>",
    )
    html = provider._render_code_html("<code>", language=language)
    for expected in ["&lt;script&gt;", "&quot;Example&quot;", "&lt;tag&gt;", "&lt;footer&gt;", "&lt;code&gt;"]:
        assert expected in html
    assert "<script>" not in html
