---
name: dwy-macos-development
description: 开发、排查、评审或适配 macOS 应用时使用，涵盖窗口、菜单、键鼠、系统版本、Liquid Glass 和目标系统验证。
---

# macOS 开发

同时使用可用的 `dwy-swift-development`；涉及模块边界或公共代码时使用 `dwy-apple-architecture`。缺少其他 Skill 时说明并按现有项目约定继续，不自动安装。按任务使用 Apple 官方 Skill；没有适用项时查官方文档。

新项目默认最低 macOS 15；现有项目先读取实际 deployment target，发现差异时说明，不擅自升级。新 API 按 SDK 与运行时版本判断，保留低版本可用体验。

macOS 应用与库须支持 Intel `x86_64` 和 Apple Silicon `arm64`；检查源码、二进制依赖和构建设置，发布产物应包含两种架构。分别验证两架构构建，检查产物架构；实际运行和界面验收分别报告，不能以交叉编译代替 Intel 实机验证。

按需阅读 [窗口与系统外观](references/ui-adaptation.md)、[弹窗差异](references/presentations.md) 和 [macOS 踩坑](references/pitfalls.md)。界面变更先确定目标系统、窗口尺寸、键鼠和辅助功能验证；签名或启动通过不等于目标系统交互与视觉验收。

发现可复用新坑先查重：只在 macOS 证实的放本 Skill；双端均有证据时将共通部分放 Swift Skill，保留平台差异。记录现象、范围、根因及证据、处理方法、验证状态和未验证项；未确认标记待验证，项目专属问题留项目内。修改共享 Skill 必须已有来源仓库授权。
