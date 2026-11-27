---
name: dwy-macos-development
description: 开发、排查、评审或适配 macOS 应用时使用，涵盖设计规范、组件复用、窗口、菜单、键鼠、系统版本、Liquid Glass 和目标系统验证。
---

# macOS 开发

同时使用可用的 `dwy-swift-development`；涉及模块边界或公共代码时使用 `dwy-apple-architecture`。缺少其他 Skill 时说明并按现有项目约定继续，不自动安装。按任务使用 Apple 官方 Skill；没有适用项时查官方文档。

开发前必须同时核对官方 Skill、可用 MCP、Xcode/CLI 与实际 macOS SDK；遵循 `dwy-swift-development` 的 `references/official-tooling.md`，即使该 Skill 未安装也不能省略四项核对。确认选中工具链、SDK、部署版本和目标架构，不能只读 Skill 或只看到构建成功就跳过核对。

新应用默认最低 macOS 26+，默认不为 macOS 15 及以下版本编写兼容实现或安排测试。先读取项目约定与实际 deployment target，现有项目不因启用 Skill 自动升级系统下限。新 API 按 SDK 与实际支持的运行时版本判断。

最低系统基线为 macOS 26.0：新应用及已明确迁移的项目须统一 App、扩展、测试目标的 `MACOSX_DEPLOYMENT_TARGET`、XcodeGen 的 `deploymentTarget` 与本项目 Swift Package 的 macOS 平台声明；同时更新当前支持说明。构建后回读 App 和扩展的 `LSMinimumSystemVersion` 及 Mach-O 的 `minos`，确认均不低于 26.0。macOS 26 已提供的 API 可直接使用，不为已停止支持的系统新增兼容分支；高于项目最低版本的 API 仍须判断可用性。

先核对项目约定、实际构建与发布配置，以及共享库调用方的架构要求。项目上下文没有明确架构要求时，默认仅支持 Apple Silicon `arm64`。只有上下文明确要求 Intel `x86_64` 时，才将 Intel 纳入实现、构建、发布和验证范围。现有项目已明确支持的架构继续按项目约定执行。

检查源码、二进制依赖、构建设置和发布产物与项目支持架构一致。实际运行和界面验收分别报告，未完成的验证明确标注，不能以交叉编译代替目标设备验证。

按需阅读 [窗口与系统外观](references/ui-adaptation.md)、[弹窗差异](references/presentations.md) 和 [macOS 踩坑](references/pitfalls.md)。界面变更先确定目标系统、窗口尺寸、键鼠和辅助功能验证；签名或启动通过不等于目标系统交互与视觉验收。

问号或信息按钮触发的简短只读说明必须使用锚定到按钮的 `.popover`。需要独占输入的弹框必须使用系统模态（`.sheet`、`.alert`、`.confirmationDialog`、AppKit sheet / modal），禁止用 overlay、ZStack 或透明拦截层在页面内叠加模拟模态；不给底页自绘蒙层或模糊。实现与评审弹框时按 [弹窗差异](references/presentations.md) 核对呈现方式、键盘和验收要求。

**菜单标题按点击后的实际行为判断是否加省略号。**

- 自定义状态栏菜单、上下文菜单和应用内菜单中，仅用于打开页面或窗口、启动工具的入口，以及立即完成的命令，标题末尾不得加省略号，例如「设置」「取色器」「退出」。
- 命令必须等待用户输入、选择或确认才能完成时，标题末尾用单个 `…`，例如「另存为…」「打开文件…」。评审时按实际点击行为核对各语言的菜单标题。
- macOS 标准应用菜单沿用平台标准标题，例如「设置…」。[Apple 菜单设计规范](https://developer.apple.com/design/human-interface-guidelines/menus) · [Apple 菜单栏设计规范](https://developer.apple.com/design/human-interface-guidelines/the-menu-bar)

界面开发与评审同时遵循 `dwy-swift-development` 的图标视觉一致性、按钮语义与样式一致性、重复能力封装与复用要求；跨页面检查同类入口，不仅检查当前窗口。

涉及设计规范、全局 token、主题或组件抽取时，先读取项目现有规范，再读 [设计规范与组件复用](references/design-system.md)；不得把某个产品的品牌或几何规格直接变成所有 Mac 项目的要求。

macOS 单端与双端项目内部均按 App①、Features②、BizFoundation③、Foundation④四层；BusinessUI 属于②，产品平台业务适配属于③，不增加第五层。新项目使用统一生成器的 macos 或 apple 形态，按 `dwy-apple-architecture` 的目录与依赖规则执行；只生成所选平台，追加另一端不搬已有壳或升级依赖。

发现可复用新坑先查重：只在 macOS 证实的放本 Skill；双端均有证据时将共通部分放 Swift Skill，保留平台差异。记录现象、范围、根因及证据、处理方法、验证状态和未验证项；未确认标记待验证，项目专属问题留项目内。修改共享 Skill 必须已有来源仓库授权。
