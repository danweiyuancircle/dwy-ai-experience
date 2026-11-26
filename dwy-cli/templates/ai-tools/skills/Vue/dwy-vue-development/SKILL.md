---
name: dwy-vue-development
description: 开发、修改、测试或排查 Vue 应用、组件及组合式函数时使用；覆盖团队写法、常见踩坑和自有基础库发现。
---

# Vue 开发

先确认 Vue、TypeScript、构建工具及项目已有依赖。优先复用项目现有组件和工具。涉及模块边界时使用可用的 dwy-vue-architecture。

- [Vue 规范](references/dwy-vue-core.md)：组件、路由、样式及配置。
- [Pinia](references/dwy-vue-pinia.md)：项目使用 Pinia 时参考。
- [测试](references/dwy-vue-testing.md)：组件和业务测试。
- [踩坑](references/dwy-vue-pitfalls.md)：响应式、路由和构建排查。
- [自有基础库](references/dwy-vue-base-lib.md)：涉及 EUI、EKIT、Admin Kit 或 Auth Web 时查 `dwy-vue-appkit` 的对应资料。

新建或扩展管理后台时，必须使用 `@dwydev/admin-kit` 装配后台，并使用 `@dwydev/eui` 实现其已提供的基础控件。开发前读取 [强制规则](references/dwy-vue-base-lib.md#二强制规则)。

其他强制选型仅适用于已采用该栈或用户明确选择的新项目。其他场景遵循现有依赖和用户要求，不自动新增自有依赖。
