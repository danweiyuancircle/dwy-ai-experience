# AppleAppKit 平台支持与适配记录

更新日期：2026-11-12。本页记录至 `0.8.0-beta.5`，发布状态与提交以对应 Git tag / GitHub Release 为准。本页记录整个 AppleAppKit 共享版本的平台边界，并按产品和场景限定适配证据；不将某个 UI 示例通过解释为全部模块、系统版本或设备通过。

## 统一版本与最低支持

远程 SwiftPM 入口是仓库根 `Package.swift`，产品源码统一位于 `ios/Sources/`。共享基础模块、DesignKitIOS、DesignKitMac、认证、购买、同步和可选 Playground 使用同一仓库 tag/revision，不分别发布或混用两个版本。同一消费工程的 SwiftPM 与 Xcode 依赖声明及锁文件须一致；运行时支持还取决于实际选择的产品及其系统能力。

| 平台 | 自 0.8.0-beta.1 起的最低支持 | 边界 |
|---|---|---|
| iOS / iPadOS | 18.0 | 使用 26 / 27 新能力时仍保留 18 的调用路径；iPad 不能仅凭 iPhone 模拟器结果视为已验收 |
| macOS | 26.0，Apple Silicon arm64 | Mac App、helper 与内置原生运行库均须符合 arm64；仅 App 可执行文件是 arm64 不足以证明全包通过 |
| 构建语言与工具链 | Swift 6.0；0.8 预发布使用 Xcode 26 或更新工具链 | SDK 版本、编译目标与运行系统分别记录，不用当前 SDK 推断实际测试系统 |

支持或适配系统 27 **不提高最低版本**。已用 `git show 0.7.4:Package.swift` 核实该旧标签的最低 iOS 17 / macOS 14；这是历史版本契约，不代表 0.8 仍支持这些系统，也不主动使旧应用失效。具体升级破坏面见 `ios/CHANGELOG.md`。

## 如何读取验证状态

| 证据类型 | 能说明什么 | 不能据此推断 |
|---|---|---|
| SDK 编译 | 明确产品/target 在指定工具链、SDK 和 deployment target 下通过编译 | 对应系统已运行、UI 正确、所有产品均可用 |
| 自动化测试 | 指定 host / 模拟器内指定测试集通过 | 未纳入测试的产品、状态、真实 IME / VoiceOver 或前台材质通过 |
| 前台交互 | 已记录窗口、控件、动作及结果的实际操作 | 整个平台全量适配，或最低系统同样通过 |
| 实机 / 模拟器 | 明确的运行设备类型与实际 OS runtime | 模拟器等同实机，或 iPhone 等同 iPad |

构建、布局、签名及 inactive 截图都不能替代前台活动窗口的颜色与材质验收。缺少记录写“未验”，不能将空项默认视为通过。

## 各共享库版本的已知证据

以下版本均维持 iOS / iPadOS 18、macOS 26 arm64 最低支持，不表示所有产品都完成了下表涉及系统的全部场景。

| 已发布版本 / 提交 | SDK 编译与 CI | 自动化测试 | 前台交互与设备边界 |
|---|---|---|---|
| `0.8.0-beta.1` / `5c94a06b10b2d9e982de3842eca02c4175b3021e` | [发布 CI](https://github.com/danweiyuancircle/dwy-ai-experience/actions/runs/43159604082) 成功；macOS 26 runner / Xcode 26.0.1，Mac arm64 编译及 iOS 18 目标平台库编译 | 本机 macOS 27.2.1 全量 216 项，Mac 组件 14 项；iOS 独立组件工程的模拟器结果见下表 | iOS 组件有限实际输入、选择与按钮操作；Mac 27 初步窗口 / AX 核对。macOS 26 实机、完整 IME / VoiceOver / AutoFill 和 iPad 现场未验 |
| `0.8.0-beta.2` / `52421ef0fceb3ef591d14108f9108e8f2e23da8f` | [发布 CI](https://github.com/danweiyuancircle/dwy-ai-experience/actions/runs/43173816837) 成功，同一 Mac / iOS 18 编译基线 | 本机 macOS 27.2.1 全量 227 项，含 Playground 7 项；22 份真实 fixture 同源检查通过 | Mac 27 Playground 窗口核对按钮、复制、Combo 回车单次提交、局部预览设置跨组件保留；下拉后 CUA 超时，完整鼠标、边缘、IME / VoiceOver 矩阵未验；本版未据此宣称 iOS 新增回归全通过 |
| `0.8.0-beta.3` / `08ed1525a57aeb6297f5e1e7e563fcc39f6735d5` | [发布 CI](https://github.com/danweiyuancircle/dwy-ai-experience/actions/runs/43187343657) 全部成功，同一 Mac / iOS 18 编译基线 | 本机 macOS 27.2.1 全量 227 项，Mac 组件 18 项、Playground 7 项 | 修正 floating secondary 的显式 tint，保留 primary / destructive；消费 App 非活动窗口截图不能证明前台颜色通过。macOS 26 前台及 iOS 本版 UI 运行回归未验 |
| `0.8.0-beta.4` / `3922dfa1ece726aff0906bcc1e2b00b224181038` | [发布 CI](https://github.com/danweiyuancircle/dwy-ai-experience/actions/runs/43192292098) 11 jobs 全部成功；Apple job 使用同一 Mac / iOS 18 编译基线 | 本机 macOS 27.2.1 全量 228 项，Mac 组件 19 项；短 Toast 尺寸、长文换行、Playground 同源及双语版本检查通过 | 消费宿主 ADBox 在 macOS 27.2.1 的真实活动 Playground 窗口已确认：EToast 紧凑、无可见关闭按钮并自动消失；floating EButton 主操作蓝色、次操作中性、危险操作红色。这些局部场景通过不覆盖其他状态；macOS 26 实机、完整 VoiceOver / IME 未验，未新增 iOS / iPad 全场景运行结论 |

CI 的 iOS 编译使用真实 iPhone simulator SDK，目标 triple 为 `arm64-apple-ios18.0-simulator`；这是 deployment target 为 18 的编译，不是 iOS 18 模拟器运行测试。Apple job 同时执行根 `swift test`；Mac host 下条件排除的 iOS 测试不计入运行覆盖。配置依据：`.github/workflows/private-release.yml`。

### iOS 组件工程历史模拟器记录

以下只针对 `ios/Examples/IOSControls/` 及相关 DesignKitIOS 测试，不覆盖认证、购买、同步或消费 App 的完整业务。来源：`ios/Docs/UI_FOUNDATION_IMPLEMENTATION.md`。

| 实际模拟器 runtime | 记录与所属阶段 | 限制 |
|---|---|---|
| iOS 18.6 | 首批组件 12 项单元 + 3 项 XCUITest 通过；统一 E 命名后复验同组通过 | 非实机、非完整 iPad 验收；后续 beta.2–4 未逐版重跑该组 |
| iOS 26.5 | 统一 E 命名前，首批组件同组 12 + 3 项通过 | E 命名后未重跑此节点，不泛化为后续标签已测试 |
| iOS 27.0 | 首批同组 12 + 3 项通过；E 命名后复验通过，默认中文页截图核对 | 仅组件工程；不等于 iOS 27 全库、全部控件状态或实机通过 |

Mac 本机记录来自 **macOS 27.2.1 / Apple Silicon 实机**；这不替代 macOS 26 实机。CI 的 macOS 26 runner 构建与自动测试已通过，但没有记录 macOS 26 的前台 GUI / IME / VoiceOver 现场验收。

## 0.8.0-beta.5 菜单适配记录

EMenu / EPicker 的可选图标显示适配以 `0.8.0-beta.4` 为基线，版本为 `0.8.0-beta.5`；发布身份见[对应 Release](https://github.com/danweiyuancircle/dwy-ai-experience/releases/tag/0.8.0-beta.5)的 tag、manifest 和完整 revision。下表是发布前验证证据，后续 CI 结果不回填为本机 GUI 通过。需求不提高 iOS / iPadOS 18、macOS 26 arm64 最低支持。

| 项目 | 当前状态 |
|---|---|
| 改动范围 | EMenu 在原生 Menu 整体默认应用 `.titleAndIcon`，保留 Label 的图文；纯 Text 不制造图标，调用方可在 label 闭包内用 `.iconOnly` 覆盖。EPicker 仅 menu 分支采用该策略，segmented 保持原行为；公开签名未变 |
| SDK 编译 | Xcode 27.2（27B52）、macOS SDK 27.2；MacControlsGallery 构建与签名验证通过。本轮未触发新的 CI，不能借历史 CI 宣称本次源码已通过 macOS 26 runner |
| 自动化测试 | 最终实现于本机 macOS 27.2.1 arm64 通过 DesignKitMac 19 项、Playground 7 项，共 26 项定向测试；不是本次全库测试。22 份 fixture 与 44 份双语文档同源检查通过 |
| macOS 27.2.1 前台交互 | 候选实现曾确认普通 SF 图标菜单显示、纯 Text 菜单的 AX 内容及执行计数从 0 到 1；最终调整为 Menu 整体策略后，分组、子菜单和 Picker 的完整 GUI 复核尚未完成。CUA 打开 nativeMenu 后返回 `timeoutReached`，重开后仍无法获取窗口；不能把候选局部证据或 AX identifier 当作最终图标截图与全部交互通过 |
| macOS 26 兼容 | 本项运行未验；本机 27 构建、测试与候选交互均不能替代最低系统现场验收 |
| iOS / iPadOS | 无本轮源码行为改动，也无本轮新增运行测试；保持平台分离，不把 Mac 结果解释为 iOS 已适配 |

本次最终定向测试日志位于本机临时目录，文件名为 `dwy-menu-icons-final-tests.log`；它不是稳定发布下载地址。测试日志可确认上述 19 + 7 项零失败，不能证明受 CUA 超时影响的最终菜单 GUI 场景通过。

## 新版本记录模板

每个发布版本保留历史结果，新增记录而不覆盖旧版本的未验边界：

```markdown
### <实际 tag> / <完整 commit> / <日期>
- 最低支持：iOS / iPadOS <版本>；macOS <版本>、<架构>；Swift <版本>。
- 本版适配：<产品、组件、OS 差异、公开 API 与行为变化>。
- SDK 编译：<Xcode / SDK / target / deployment target / CI URL / 结果>；缺项：<未验>。
- 自动化测试：<产品、测试集、数量、实际 host 或 runtime / 结果 / 证据>；缺项：<未验>。
- 前台交互：<组件、状态、动作、实际结果及证据>；缺项：<未验>。
- 设备：<实机或模拟器、OS 精确版本、架构；iPhone / iPad 分别说明>。
- 已知限制：<失败、工具超时、未验目标；不得替换为通过>。
- 消费工程：<单独验证结果；不将业务验收计入基础库通用覆盖>。
```

## 发版维护规则

1. 先核对根 `Package.swift` 的统一最低版本、架构要求和实际公开产品；系统 27 的适配不能无意提高最低系统。若确实提高基线，须在 `ios/CHANGELOG.md` 明确破坏面并获得产品授权。
2. 每个发布 tag 更新本页对应记录、完整 revision、CI 链接和实际验证范围；未跑的系统 / 产品仍写未验。测试数量按同一运行计数，不能累加不同阶段制造覆盖率。
3. UI 适配至少分开记录最低系统路径和新系统路径、SDK 编译与 runtime、Mac 前台与 inactive、iPhone 与 iPad。编译或快照不能替代菜单动作、键盘、IME、VoiceOver、长文和字号等受影响交互。
4. 继续使用现有 fixture / 同源检查；发布时同步 Playground catalog、双语 Package 字段和生成 Index。用锁文件、tag、manifest 确认包身份，不用页面版本字符串代替依赖证据。
5. CI 或 GUI 失败、超时和环境缺失原样记录；待补验证完成后追加证据。无 macOS 26 实机时明确保留该缺口，不能用 macOS 27 通过替代。
6. 本页属于基础库记录；消费 App 另查自己的依赖、完整产物架构、签名、资源及真实入口。基础库通过不代表应用已安全替换或业务验收完成。

相关入口：`ios/CHANGELOG.md`、`ios/Docs/UI_FOUNDATION_IMPLEMENTATION.md`、`ios/Docs/IOS_DESIGN_SYSTEM.md`、`ios/Docs/MACOS_DESIGN_SYSTEM.md`。
