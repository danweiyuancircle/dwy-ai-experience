---
name: dwy-email-notify
description: 使用或排查 dwy-email-notify 邮件事件通知能力时使用；先核实项目安装版本及公开 API。
---

# dwy-email-notify

邮件平台事件和通知，核实供应商配置、Webhook 验证与宿主处理。

## 查找与使用

项目使用 0.1.0 时可阅读 [0.1.0 接入和示例](references/v0/0.1.0.md)；其他版本先查该版本的资料和代码，不把此快照当作其他版本的合同。

1. 检查项目锁文件和当前 Python 环境；用 `importlib.metadata.version("dwy-email-notify")` 查询实际发行版本，依赖范围不等于实际安装版本。未安装时不得假设可用或自动安装。
2. 在实际环境中检查 `dwy_email_notify` 的公开接口、类型及项目已有调用；editable 安装以实际源码为准。说明、实现或安装版本不一致时以运行代码为准。
3. 本索引基于仓库 0.1.0，能力与签名可能随小版本变化。精确版本源码位于仓库 `backend/packages/email-notify`，文档为该目录的 `README.md`；只在确认其版本与消费项目一致时使用。缺少安装源码时查对应 `dwy-email-notify@版本` 标签，不能用默认分支冒充。
4. 在已有调用和该版本文档中核对配置、必需依赖、输入校验、失败处理及生命周期后接入。没有足够证据时说明缺口，不猜 API。

不要因为发现此库就改动项目依赖；新增依赖遵循项目选型规则。关联 FastAPI 或其他自有包时同时参考可用的对应 Skill。
