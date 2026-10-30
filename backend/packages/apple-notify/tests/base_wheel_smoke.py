"""仅安装基础 wheel 时验证公开入口，不加载平台 SDK 或旧集成包。"""

import importlib.metadata
import importlib.util
import sys
from pathlib import Path

import dwy_apple_notify
from dwy_apple_notify import AppleNotifyConfig, AppleNotifySinks, install_apple_notifications


def main(expected_version: str) -> None:
    """要求实际 wheel 位于当前隔离环境中，依赖元数据不得指回旧包。"""
    distribution = importlib.metadata.distribution("dwy-apple-notify")
    assert distribution.version == expected_version
    assert Path(dwy_apple_notify.__file__).resolve().is_relative_to(Path(sys.prefix).resolve())
    assert not any("dwy-webhooks" in requirement.lower().replace("_", "-")
                   for requirement in distribution.requires or ())
    for name in ("dwy_webhooks", "dwy_email_notify", "resend", "appstoreserverlibrary", "app_cloud"):
        assert importlib.util.find_spec(name) is None, name
        assert name not in sys.modules, name
    assert "resend" not in AppleNotifyConfig.model_fields
    assert "resend" not in AppleNotifySinks.__dataclass_fields__
    assert callable(install_apple_notifications)


if __name__ == "__main__":
    main(sys.argv[1])
    print("Apple notification base wheel isolation passed.")
