"""Tests for dwyeapi.email(Gmail plus/点号/googlemail 折成同一收件箱)."""

import pytest

from dwyeapi.email import canonicalize_email, is_common_email_domain, is_folded_alias, require_common_email_domain
from dwyeapi.exceptions import BusinessError


class TestCanonicalizeEmail:
    def test_strips_gmail_plus_and_dots(self):
        """gmail.com / googlemail.com 去掉 +tag 与点,域名统一 gmail.com."""
        assert canonicalize_email("BaiWen4243+5623@gmail.com") == "baiwen4243@gmail.com"
        assert canonicalize_email("bai.wen.4243+x@googlemail.com") == "baiwen4243@gmail.com"
        assert canonicalize_email("  User.Name+tag@Gmail.COM ") == "username@gmail.com"

    def test_other_domains_only_lower(self):
        """非 Gmail 只做大小写与首尾空白规范化,保留 + 与点."""
        assert canonicalize_email("Alfred.Yuan+ops@icloud.com") == "alfred.yuan+ops@icloud.com"
        assert canonicalize_email("a.b@example.com") == "a.b@example.com"

    def test_missing_at_returns_stripped_lower(self):
        """无 @ 的非法输入不抛,只做 strip + lower,交给上游校验."""
        assert canonicalize_email("  NotAnEmail ") == "notanemail"


class TestIsFoldedAlias:
    def test_detects_gmail_variants(self):
        """Gmail plus / 点 / googlemail 视为折叠别名;仅大小写不算."""
        assert is_folded_alias("a+x@gmail.com") is True
        assert is_folded_alias("a.b@gmail.com") is True
        assert is_folded_alias("a@googlemail.com") is True
        assert is_folded_alias("a@gmail.com") is False
        assert is_folded_alias("A@gmail.com") is False
        assert is_folded_alias("a+x@icloud.com") is False


class TestIsCommonEmailDomain:
    def test_allows_common_consumer_domains(self):
        """常见个人域 qq / 163 / gmail / outlook / icloud / proton 放行."""
        assert is_common_email_domain("user@qq.com") is True
        assert is_common_email_domain("user@163.com") is True
        assert is_common_email_domain("user@126.com") is True
        assert is_common_email_domain("user@foxmail.com") is True
        assert is_common_email_domain("user@outlook.com") is True
        assert is_common_email_domain("user@icloud.com") is True
        assert is_common_email_domain("user@proton.me") is True
        assert is_common_email_domain("Bai.Wen+1@Gmail.COM") is True
        assert is_common_email_domain("user@googlemail.com") is True

    def test_rejects_disposable_and_unknown_domains(self):
        """一次性域名与随便注册的域名拒绝;不因大小写放行."""
        assert is_common_email_domain("qz2d062021@uberip.com") is False
        assert is_common_email_domain("cactus666_1@2925.com") is False
        assert is_common_email_domain("a@mail.tm") is False
        assert is_common_email_domain("a@example.com") is False
        assert is_common_email_domain("a@mail.qq.com") is False

    def test_allows_edu_cn_by_default(self):
        """默认放行 *.edu.cn;关闭开关后拒绝;不放行任意 .edu."""
        assert is_common_email_domain("a@mails.tsinghua.edu.cn") is True
        assert is_common_email_domain("a@mail2.sysu.edu.cn") is True
        assert is_common_email_domain("a@columbia.edu") is False
        assert is_common_email_domain("a@mails.tsinghua.edu.cn", allow_edu_cn=False) is False

    def test_extra_allow_is_case_insensitive(self):
        """机构域靠 extra_allow;大小写不敏感,可传完整邮箱."""
        assert is_common_email_domain("ops@yanbofund.com") is False
        assert is_common_email_domain("ops@YanboFund.com", extra_allow={"yanbofund.com"}) is True
        assert is_common_email_domain("ops@contek.io", extra_allow={"ops@Contek.io"}) is True

    def test_missing_at_is_not_common(self):
        """无 @ 视为不在白名单,不抛."""
        assert is_common_email_domain("not-an-email") is False


class TestRequireCommonEmailDomain:
    def test_returns_canonical_email(self):
        """放行时返回规范化邮箱,供写入与查重."""
        assert require_common_email_domain("Bai.Wen+1@Gmail.com") == "baiwen@gmail.com"

    def test_raises_business_error_without_echoing_domain(self):
        """拒绝时抛 BusinessError,固定错误码,消息不回显用户域名."""
        with pytest.raises(BusinessError) as exc_info:
            require_common_email_domain("qz2d062021@uberip.com")
        err = exc_info.value
        assert err.code == "EMAIL_DOMAIN_NOT_ALLOWED"
        assert "uberip" not in err.message.lower()
        assert "qz2d062021" not in err.message.lower()
