---
name: dwy-python-appkit
description: 使用或排查 DWY 自有 Python 基础包，包括 EAPI、认证、支付、通知和设备指纹时使用。
---

# Python 自有基础包

## 先确认实际依赖

先读 [版本与源码定位](references/version-resolution.md)，逐包核对当前解释器、锁定来源、实际导入路径及代码。版本范围不是安装版本，发行元数据也不能证明 editable 源码未修改；多个基础包分别核对，不按一套版本接入。

本 Skill 是能力导航，不保证项目版本包含列出的所有 API。引用资料只按其标明的版本使用；源码、公开接口与资料有差异时，以项目实际运行代码为准。缺少能力先评估现有 API，确需升级再说明目标版本、配置/数据迁移、调用方与验证范围；不因更新 Skill 自动改项目依赖。

## 按需求读取资料

| 需求 | 包 | 接入资料 |
| --- | --- | --- |
| FastAPI 基础设施、响应、数据库、任务 | `dwyeapi` | [EAPI](references/eapi/guide.md) |
| 用户认证、会话、管理端认证 | `dwy-auth` | [认证](references/auth/guide.md) |
| 支付网关、订单和回调 | `dwy-payment` | [支付](references/payment/guide.md) |
| 多目标通知与投递 | `dwy-notify` | [通知](references/notify/guide.md) |
| Webhook 接收、发送和事件 | `dwy-webhooks` | [Webhook](references/webhooks/guide.md) |
| Apple 服务端事件 | `dwy-apple-notify` | [Apple 通知](references/apple-notify/guide.md) |
| 邮件事件 | `dwy-email-notify` | [邮件通知](references/email-notify/guide.md) |
| 微信支付事件 | `dwy-wechatpay-notify` | [微信支付通知](references/wechatpay-notify/guide.md) |
| 设备指纹 | `dwy-device-fingerprint` | [设备指纹](references/device-fingerprint/guide.md) |

只读本次任务涉及的资料，不加载全部包或自动引入依赖。框架适配、可选 extra、配置、存储和生命周期按实际版本核对；产品模型、会话策略、HTTP 装配与权益由宿主按相应契约承担。语言与异步规范使用 `dwy-python-development`，分层使用 `dwy-python-architecture`，FastAPI 接口开发使用 `dwy-python-fastapi`。

## 维护基础包时

公开 API、依赖/extra、初始化与资源释放、错误语义、安全配置或数据库迁移变化时，同步检查该包接入资料和版本记录。发布前对照该包上一发布版本/提交；新增或删除能力标明可证明的版本边界，不把不同包一起升版，也不把未发布代码标为已发布。检查不授权更新消费者、发布或修改全局 Skills。
