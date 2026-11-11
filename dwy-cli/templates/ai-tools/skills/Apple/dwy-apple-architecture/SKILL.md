---
name: dwy-apple-architecture
description: 设计、开发、排查或评审 iOS、macOS 的模块架构、依赖方向、共享基础库及代码抽取时使用。
---

# Apple 架构与复用

同时使用可用的 `dwy-swift-development` 和受影响的平台 Skill；缺少时按现有项目约定继续，不自动安装。先检查项目结构、已有基础库、调用方和依赖边界；不因启用 Skill 重建现有工程。

需要分层与依赖判断时读 [分层与依赖](references/layering.md)，需要共用或抽取时读 [共享与抽取](references/extraction.md)，遇到架构问题读 [架构踩坑](references/pitfalls.md)。新项目遵循团队分层；既有项目先尊重实际架构，若与团队规范冲突，说明影响并在授权范围内处理。

团队最低支持 iOS 18+、macOS 15+，不再为 iOS 17 及以下版本设计兼容实现或测试。现有项目先核对实际 deployment target，低于基线时说明差异及迁移范围，不因启用 Skill 自动修改工程配置。针对当前任务查找适用的 Apple 官方 Skill；缺失时使用官方文档。目标平台和 SDK 版本决定 API 可用性。
