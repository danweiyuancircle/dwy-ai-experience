---
name: dwy-ios-development
description: 开发、排查、评审或适配 iOS 18+、iPadOS 18+ 应用时使用，涵盖设计规范、组件复用、界面、系统版本、弹层、Liquid Glass 和目标设备验证。
---

# iOS 开发

同时使用可用的 `dwy-swift-development`；涉及模块边界或公共代码时使用 `dwy-apple-architecture`。缺少其他 Skill 时说明并按现有项目约定继续，不自动安装。按任务使用 Apple 官方 Skill；没有适用项时查官方文档。

默认最低支持 iOS 18+ / iPadOS 18+，不再支持 iOS 17 及以下版本；新项目 deployment target 设为 18.0。具体支持范围按实际项目上下文决定；现有项目先读取实际 deployment target，低于基线时说明差异及迁移范围，不因启用 Skill 自动修改工程配置。新 API 按 SDK 与运行时版本判断，保留 iOS 18 起的可用体验，不为 iOS 17 添加兼容分支。

系统回归默认覆盖 iOS 18 和当前最新支持的大版本；仅在受影响功能存在明确系统差异时增加中间版本，不再安排 iOS 17 的构建、设备或模拟器测试。屏幕尺寸、可访问性及关键业务验证仍按改动影响范围执行。

按需阅读：[布局与安全区](references/layout.md)、[系统外观与 Liquid Glass](references/appearance.md)、[弹窗和锚点](references/presentations.md)、[iOS 踩坑](references/pitfalls.md)。界面变更先确定受影响系统、屏幕尺寸、滚动和交互，再验证布局、可访问性与视觉；编译通过不等于设备验收。

涉及设计规范、全局 token、主题或组件抽取时，先读取项目现有规范，再读 [设计规范与组件复用](references/design-system.md)；不得把某个产品的品牌或几何规格直接变成所有 iOS 项目的要求。

发现可复用新坑先查重：只在 iOS 证实的放本 Skill；双端均有证据时将共通部分放 Swift Skill，保留平台差异。记录现象、范围、根因及证据、处理方法、验证状态和未验证项；未确认标记待验证，项目专属问题留项目内。修改共享 Skill 必须已有来源仓库授权。
