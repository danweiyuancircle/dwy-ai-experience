"""在仓库外检查实际 wheel 的公开合同与可选供应商导入边界。"""

import importlib.metadata
import sys

from dwy_email_notify import EmailNotifyConfig, EmailNotifyRuntime, ResendWebhookConfig
from dwy_email_notify.providers.resend.appearance import DEFAULT_APPEARANCE

assert importlib.metadata.version("dwy-email-notify") == "0.1.0"
assert importlib.metadata.version("dwy-notify") == "0.2.1"
assert EmailNotifyConfig().resend is None
assert EmailNotifyRuntime.__name__ == "EmailNotifyRuntime"
assert ResendWebhookConfig.model_fields["path"].default == "/webhooks/resend"
assert DEFAULT_APPEARANCE.username == "邮件通知"
assert not any(name == "resend" or name.startswith(("appstoreserverlibrary", "dwy_webhooks"))
               for name in sys.modules)
print("Email notify wheel base imports and optional provider boundary passed.")
