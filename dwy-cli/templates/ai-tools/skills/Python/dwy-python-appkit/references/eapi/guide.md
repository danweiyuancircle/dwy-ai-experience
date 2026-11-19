# EAPI 接入

先按 [版本与源码定位](../version-resolution.md) 确认项目解释器、`dwyeapi` 的发行版本和实际导入源码。实际环境代码优先；editable、path、本地修改或模块遮蔽时，不用同版本 tag 覆盖真实代码。

## 选择适用资料

读同目录 `versions.yml` 选择文档线：0.x 对应 `v0/`。尚不存在的版本线不能用已有线冒充；查实际接口与对应版本源码，说明资料缺口。版本线只是导航，0.x 内也可能有破坏性变更。

按需读取以下资料；`shared/` 放常用约定，不代表其中 API 对所有历史版本不变。标明下限的能力在旧版本不能使用；未标明时也要查实际接口。

| 资料 | 何时读 |
| --- | --- |
| [分层](shared/layering.md) | EAPI 与业务服务边界 |
| [时区](shared/timezone.md) | 时间处理 |
| [响应信封](shared/response-envelope.md) | HTTP 响应与错误 |
| [防腐层](shared/anticorruption.md) | 已采用 EAPI 的基础能力约束 |
| [0.x 导航](v0/index.md) | 模块、初始化与使用 |
| [邮件 Provider](v0/providers-email.md) | 邮件投递 |
| [邮箱规范化](v0/email-canonical.md) | 规范化 ≥0.9.6、常见域名及发码校验 ≥0.10.0 |
| [0.x 迁移](v0/breaking.md) | 版本差异与调用方迁移 |
| [任务接入](tasks-integration-guide.md) | 使用 tasks extra |

## 源码与接入

先读实际环境的公开接口、实现、测试和项目已有调用。资料不足时再查同一安装来源的源码：发布包可查 `dwyeapi@<实际版本>` tag 的 `backend/src/dwyeapi/`，Git 依赖查锁定提交。默认分支不能替代；tag 缺失也不影响读取已安装源码。

核对配置环境、数据库/缓存/任务资源的生命周期、异常与响应装配、可选 extra 和失败路径；产品模型与业务状态留在宿主。只读 docstring 不足以证明行为时，继续查实现和相关测试。缺少确切依据时说明未确认项，不猜 API，也不为匹配资料自动升级。
