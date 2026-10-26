# dwy-webhooks

## 0.1.1

- 首个公开 PyPI 版本，通过 GitHub Actions OIDC 发布。
- 显式声明 Ruff 的本包模块分类，使仓库根目录与包目录运行的导入排序检查一致。
- Discord 请求的 User-Agent 版本同步为 `0.1.1`；验签、注入与发送行为保持不变。

## 0.1.0（未公开）

- 首次通过 GitHub Actions OIDC 发布到公开 PyPI，导入命名空间为 `dwy_webhooks`，基础依赖为 `dwyeapi==0.12.0`。
- 提供公开配置、FastAPI 注册入口、中立事件与可替换接收器；密钥、路由、目标地址和存储资源由调用项目注入。
- 将 Discord 发送、Resend 事件、App Store Connect HMAC 和 Apple Server Notifications V2 适配为可复用模块，包含验签、去重、失败语义和发送边界。
- `discord`、`resend`、`apple` SDK 分别通过 extras 安装；基础安装及公开入口导入不要求这些平台 SDK。
