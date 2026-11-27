---
name: dwy-vue-appkit
description: 使用或排查 DWY 自有 Vue 基础包，包括 EUI、EKIT、后台框架和网页认证时使用。
---

# Vue 自有基础包

## 先确认实际依赖

先读 [版本与源码定位](references/version-resolution.md)，从消费项目定位每个包的真实解析目录、锁定来源、版本和公开导出。依赖范围不等于安装版本，workspace/link/patch 也不等于同名版本的发布产物；多个包分别核对。

本 Skill 与引用资料是能力导航，不保证旧项目包含当前 API。实际声明与运行代码优先，版本快照和迁移说明按适用范围读取。Skill 刷新不代表项目已升级；缺少能力先评估现有 API，确需升级再说明目标版本、配套依赖、配置迁移和受影响调用，不擅自修改依赖。

**项目接入自有基础包或 UI 库后，新增和修改的代码必须直接复用实际版本中满足需求的公开能力。** 禁止手写、复制、另接入第三方等价实现或再套同功能包装。只有核实能力缺失或接口确实无法满足需求时，才补具体缺口，优先组合已有能力。开发和评审时检查本次涉及的页面、业务组件及模块。

## 按需求读取资料

| 需求 | 包 | 接入资料 |
| --- | --- | --- |
| 组件、主题、表单、弹层与设计规范 | `@dwydev/eui` | [EUI](references/eui/guide.md) |
| 请求、存储、日期、校验与通用 hooks | `@dwydev/ekit` | [EKIT](references/ekit/guide.md) |
| 管理后台装配、布局与分页列表 | `@dwydev/admin-kit` | [Admin Kit](references/admin-kit/guide.md) |
| 管理员 Cookie 登录和会话界面 | `@dwydev/auth-web` | [Auth Web](references/auth-web/guide.md) |

新建或扩展管理后台时，必须读取 Admin Kit 和 EUI 的接入资料，并遵循 `dwy-vue-development` 的强制复用规则。其他场景按任务读取资料和选择依赖。组合使用时核对实际包的 peerDependencies、公开子入口、样式和根 Provider；不能只检查各包自身版本。产品路由、账户策略、权限与业务状态仍归宿主。Vue 开发规范使用 `dwy-vue-development`，分层使用 `dwy-vue-architecture`。

## 维护基础包时

公开导出、props/emits/slots、主题/Provider、插件契约、peer 依赖、生命周期或错误语义变化时，同步检查相关接入资料、manifest 和版本迁移记录。发布前对照该包上一发布版本/提交，按真实差异标注能力边界；新源码不能自动当作已发布能力，也不要求所有包一起升版。检查不授权升级消费者、发布或修改全局 Skills。
