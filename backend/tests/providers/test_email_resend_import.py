"""验证 ResendEmailProvider 在缺 extra 时抛友好 ImportError。

需要 email-resend extra 时才能正常构造,但模块本身可以 import。
"""

import sys
from unittest.mock import patch

import pytest


class TestResendImportError:
    def test_missing_resend_package_raises_friendly_error(self):
        """模拟 `resend` 包未安装,构造 ResendEmailProvider 应抛 ImportError 并带安装提示。"""
        # 移除已缓存的 resend 模块,模拟未安装
        original = sys.modules.pop("resend", None)
        try:
            with patch.dict(sys.modules, {"resend": None}):
                from dwyeapi.providers.email.resend import ResendEmailProvider

                with pytest.raises(ImportError, match=r"dwyeapi\[email-resend\]"):
                    ResendEmailProvider(api_key="x", from_email="a@b.com", subject="t")
        finally:
            if original is not None:
                sys.modules["resend"] = original
