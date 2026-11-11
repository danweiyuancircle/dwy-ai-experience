---
name: dwy-macos-development
description: 开发、排查、评审或适配 macOS 应用时使用，涵盖窗口、菜单、键鼠、系统版本、Liquid Glass 和目标系统验证。
---

# macOS 开发

同时使用可用的 `dwy-swift-development`；涉及模块边界或公共代码时使用 `dwy-apple-architecture`。缺少其他 Skill 时说明并按现有项目约定继续，不自动安装。按任务使用 Apple 官方 Skill；没有适用项时查官方文档。

新应用默认最低 macOS 26；默认不为 macOS 15 及以下版本编写兼容实现、安排测试。架构以 Apple Silicon `arm64` 为主要目标；代码和依赖不涉及芯片兼容差异、无需额外适配时，可以同时支持 Intel `x86_64`。若支持 Intel 需要专用代码、依赖替换或额外兼容工作，先说明差异、成本和验证范围，与用户确认后再实施。具体支持范围按实际项目上下文决定：先读取项目约定、实际 deployment target、架构与调用方要求，现有项目不因启用 Skill 自动升级系统下限或移除架构。新 API 按 SDK 与实际支持的运行时版本判断。

最低系统基线为 macOS 26.0：新应用及已明确迁移的项目须统一 App、扩展、测试目标的 `MACOSX_DEPLOYMENT_TARGET`、XcodeGen 的 `deploymentTarget` 与本项目 Swift Package 的 macOS 平台声明；同时更新当前支持说明。构建后回读 App 和扩展的 `LSMinimumSystemVersion` 及 Mach-O 的 `minos`，确认均不低于 26.0。macOS 26 已提供的 API 可直接使用，不为已停止支持的系统新增兼容分支；高于项目最低版本的 API 仍须判断可用性。

检查源码、二进制依赖、构建设置和发布产物与项目支持架构一致；支持 Intel 时也须验证 `x86_64` 构建，实际运行和界面验收分别报告，未完成的验证明确标注，不能以交叉编译代替目标设备验证。共享库的支持范围按调用方要求决定，不直接套用新应用默认值。

按需阅读 [窗口与系统外观](references/ui-adaptation.md)、[弹窗差异](references/presentations.md) 和 [macOS 踩坑](references/pitfalls.md)。界面变更先确定目标系统、窗口尺寸、键鼠和辅助功能验证；签名或启动通过不等于目标系统交互与视觉验收。

发现可复用新坑先查重：只在 macOS 证实的放本 Skill；双端均有证据时将共通部分放 Swift Skill，保留平台差异。记录现象、范围、根因及证据、处理方法、验证状态和未验证项；未确认标记待验证，项目专属问题留项目内。修改共享 Skill 必须已有来源仓库授权。
