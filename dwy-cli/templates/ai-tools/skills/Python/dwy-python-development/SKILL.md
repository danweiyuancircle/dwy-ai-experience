---
name: dwy-python-development
description: 开发、修改或排查 Python 应用、脚本或基础库时使用；覆盖团队写法、测试、异步问题和自有基础库发现。
---

# Python 开发

先检查项目现有版本、依赖和架构，优先复用已安装库。项目未使用自有库时，仅提出可用能力，不自动添加依赖。涉及 FastAPI 使用可用的 dwy-python-api，涉及分层使用 dwy-python-architecture。

- [Python 规范](references/dwy-python-core.md)：语言、依赖与配置。
- [测试](references/dwy-python-testing.md)：编写和运行测试。
- [踩坑](references/dwy-python-pitfalls.md)：排查环境、异步与运行时问题。
- [基础库](references/dwy-python-base-lib.md)：定位 dwyeapi 既有能力；以项目实际依赖与版本为准。

自有库导航：基础设施查 `dwy-eapi`；认证查 `dwy-auth`；支付查 `dwy-payment`；通用通知查 `dwy-notify`；Webhook 查 `dwy-webhooks`；Apple、邮件和微信支付来源分别查 `dwy-apple-notify`、`dwy-email-notify`、`dwy-wechatpay-notify`；设备信息查 `dwy-device-fingerprint`。对应 Skill 未安装时直接核实项目实际依赖和源码，不自动安装。

参考资料中的强制选型只适用于已经采用该技术栈或用户明确选择的新项目；现有项目以其依赖、版本和用户要求为准。
