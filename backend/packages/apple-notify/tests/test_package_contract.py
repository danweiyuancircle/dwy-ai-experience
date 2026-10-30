"""独立 Apple 通知包的领域边界与固定统计延迟。"""

import ast
from pathlib import Path

import pytest
from pydantic import ValidationError


def test_apple_package_has_independent_configuration():
    from dwy_apple_notify.config import AppleNotifyConfig
    from dwy_apple_notify.fastapi import AppleNotifySinks, install_apple_notifications

    assert set(AppleNotifyConfig.model_fields) >= {"app_store_connect", "apple_notifications"}
    assert "resend" not in AppleNotifyConfig.model_fields
    assert "resend" not in AppleNotifySinks.__dataclass_fields__
    assert callable(install_apple_notifications)
    with pytest.raises(ValidationError):
        AppleNotifyConfig(resend={})


def test_analytics_does_not_accept_external_lag_days():
    from dwy_apple_notify.analytics import AppleAnalyticsConfig

    assert "lag_days" not in AppleAnalyticsConfig.model_fields
    with pytest.raises(ValidationError) as error:
        AppleAnalyticsConfig.model_validate({"lag_days": 1})
    assert any(item["loc"] == ("lag_days",) and item["type"] == "extra_forbidden"
               for item in error.value.errors())


def test_domain_source_does_not_import_legacy_webhook_or_email_package():
    import dwy_apple_notify

    root = Path(dwy_apple_notify.__file__).parent
    for source in root.rglob("*.py"):
        tree = ast.parse(source.read_text())
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                modules = [name.name for name in node.names]
            elif isinstance(node, ast.ImportFrom):
                modules = [node.module or ""]
            else:
                continue
            assert all(not module.startswith(("dwy_webhooks", "dwy_email_notify", "resend"))
                       for module in modules), source
