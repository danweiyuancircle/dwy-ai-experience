# dwy-email-notify

邮件平台官方 Webhook 事件接入与通知转发。当前提供 Resend，未来平台各自添加 provider 和 extra；本包不提供业务发信、验证码或邮件正文读取功能。

```bash
pip install 'dwy-email-notify[resend]==0.1.0'
```

```python
from fastapi import FastAPI
from dwy_notify import NotificationConfig
from dwy_email_notify import EmailNotifyConfig, ResendWebhookConfig, install_email_notifications

def configure(app: FastAPI, signing_secret: str, notification_url: str) -> None:
    install_email_notifications(app, EmailNotifyConfig(
        notifications=NotificationConfig(targets={"operations": notification_url}),
        resend=ResendWebhookConfig(secret=signing_secret),
    ))
```

配置由宿主从安全配置中显式注入，本包不读取环境或 dotenv。Resend 只需要独立的 Webhook signing secret，无需发信 API key。默认接收路径为 `/webhooks/resend`，可由配置覆盖；只有配置来源后才加载对应 SDK。

事件经过原始载荷大小限制、官方 SDK 验签及事件筛选后才交付。仅转发事件类型、邮件编号和通知编号，不读取或转发主题、正文、收件人。默认转发使用“邮件通知”名称及固定 GitHub PNG 头像，应用可以通过 `NotificationConfig.appearance` 覆盖名称或显式清除头像。最终发送者名称必填；本包提供默认名称。

默认内存去重只覆盖当前进程，只有成功发送才登记。需要重启后仍可靠接收的宿主，应通过 `sink` 注入自己的持久化接收函数；返回 `True` 表示新事件被接受，`False` 表示已接受的重复事件，失败必须抛出异常，不能提前向 Resend 确认成功。

安装器返回 `EmailNotifyRuntime`，只持有去重状态，不接管宿主数据库、异常处理器或 lifespan。同一 FastAPI 应用只安装一次。`providers.resend.webhooks.create_resend_router` 可用于自行组合路由。

通知头像保持已有固定公开资产引用，不打包图片或拉取浮动分支：`https://raw.githubusercontent.com/danweiyuancircle/dwy-ai-experience/091ad4fea18ed3840fec83dc833f18b759256ca7/backend/packages/webhooks/assets/email.png`。
