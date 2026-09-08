"""Tests for dwyeapi.email(Gmail plus/点号/googlemail 折成同一收件箱)."""

from dwyeapi.email import canonicalize_email, is_folded_alias


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
