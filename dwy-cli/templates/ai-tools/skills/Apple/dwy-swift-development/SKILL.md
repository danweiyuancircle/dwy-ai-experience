---
name: dwy-swift-development
description: 开发、排查或评审 Swift、SwiftUI 和 Apple 平台共享代码时使用；提供团队 Swift 规范、Apple 官方技能查找和共通问题处理。
---

# Swift 开发基线

先确认任务范围、项目现有约定、调用方和实际 SDK；用户明确要求优先。阅读 [团队写法](references/conventions.md) 中与任务有关的部分；iOS 专属要求不套用到 macOS。架构、公共模块或抽取涉及 `dwy-apple-architecture` 时同时使用它；涉及 iOS / iPadOS 或 macOS 时分别使用 `dwy-ios-development` 或 `dwy-macos-development`。若其他 Skill 未安装，说明缺口并按项目现有约定继续，不自动安装。

SwiftUI、App Intents 等具体技术优先查找当前环境中与任务匹配的 Apple 官方 Skill，阅读相关参考；确认其来源后使用。不存在或不可用时查 Apple 官方文档，不强制安装、不把第三方 Skill 冒充官方。

项目使用 AppleAppKit 时先查可用的 `dwy-apple-appkit`，按项目锁定版本复用同步、基础工具、设计、认证和购买等已有能力；未安装该 Skill 时核实实际依赖与源码，不自动安装依赖。

涉及弹窗、popover 或其锚点时读取 [弹层与锚点](references/presentations.md)，再读取对应平台 Skill 中的差异。

排查共通问题时读 [共通踩坑](references/pitfalls.md)。新增经验先查重，记录现象、适用平台和版本、根因与证据、处理方式、验证及未验证项；未证实的推断明确标记。仅单项目成立的经验留在项目中。共享 Skill 属于其来源仓库：只有已获授权才修改，否则在结果中提出候选；不擅自写全局配置。
