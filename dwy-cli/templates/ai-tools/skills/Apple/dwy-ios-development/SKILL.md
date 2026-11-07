---
name: dwy-ios-development
description: 开发、排查、评审或适配 iOS、iPadOS 应用时使用，涵盖界面、系统版本、弹层、Liquid Glass 和目标设备验证。
---

# iOS 开发

同时使用可用的 `dwy-swift-development`；涉及模块边界或公共代码时使用 `dwy-apple-architecture`。缺少其他 Skill 时说明并按现有项目约定继续，不自动安装。按任务使用 Apple 官方 Skill；没有适用项时查官方文档。

新项目默认最低 iOS 17；现有项目先读取实际 deployment target，发现差异时说明，不擅自升级。新 API 按 SDK 与运行时版本判断，保留低版本可用体验。

按需阅读：[布局与安全区](references/layout.md)、[系统外观与 Liquid Glass](references/appearance.md)、[弹窗和锚点](references/presentations.md)、[iOS 踩坑](references/pitfalls.md)。界面变更先确定受影响系统、屏幕尺寸、滚动和交互，再验证布局、可访问性与视觉；编译通过不等于设备验收。

发现可复用新坑先查重：只在 iOS 证实的放本 Skill；双端均有证据时将共通部分放 Swift Skill，保留平台差异。记录现象、范围、根因及证据、处理方法、验证状态和未验证项；未确认标记待验证，项目专属问题留项目内。修改共享 Skill 必须已有来源仓库授权。
