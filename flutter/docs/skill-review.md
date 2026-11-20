# Flutter Skill 核对与更新

核对日期：2026-11-16。范围：共享仓库 Flutter Skill 模板、根目录与 Flutter 工作区入口；用户后续要求同时加强 Apple/iOS 开发前核对，追加 Swift/iOS/macOS 入口及共享工具说明。未改全局工具配置。

## 结论

原入口已说明先核对版本、依赖和现有方案，但四份引用资料仍包含旧结构和过度固定的选型，不能直接作为本次共享基础库的规范。已保留同名 Skill 与引用路径，更新其内容并补充架构、官方工具路由。

| 原有要求 | 更新后的边界 |
| --- | --- |
| core/shared + data/domain/presentation 作为默认结构 | 四层归属 Foundation/BizFoundation/Features/Assembly；对象职责与官方架构映射 |
| 必须 Riverpod 生成式 Provider，禁止 ChangeNotifier | 尊重项目方案；官方架构 Skill 实际包含 ChangeNotifier/Listenable，不误报为 Flutter 废弃 |
| 必须 Freezed/json_serializable，禁止手写 JSON | 依据模型复杂度、已有工具和用户选型；简单模型允许安全的手写转换 |
| 全部导航强制 GoRouter | SDK 路由与已选声明式方案按需求使用，深链等外部参数必须验证 |
| 网络固定 eapi 包裹格式、全局 Token/刷新 | 基础包与产品协议解耦；服务/认证作用域隔离，不默认重放写请求 |
| 统一 Mocktail、测试用例只覆盖既定 Provider 模式 | 匹配纯 Dart/Widget/平台测试，按实际依赖选 fake/mock，明确验证范围 |
| 无官方 Skill 实际使用凭据 | 每项开发必须读取并使用匹配官方 Skill，记录来源、工作流与实际验证结果 |

## 2026-11-16 评审时的强约束

当前界面基线见 `flutter/docs/design-system.md`。

- 新移动端支持基线 iOS 18+、Android 10+/minSdk29；targetSdk、compileSdk 和 Dart/Flutter SDK 版本分别管理。
- Material 3 + DWY 主题统一双端视觉，不默认混用 Cupertino/adaptive 外观，不加入玻璃材质。
- 共享库与产品业务分开；无 UI 插件不等于纯 Dart。当前底座选择按用户已确认方案，仍核实精确版本、许可证及原生边界。
- 官方 CLI 创建宿主与生成产物，执行分析、格式化、测试、运行和构建；缺环境不得声称通过。
- 官方 Skill 来源可直接读取，不把访问源码当作已安装插件/MCP。SDK 或新工具安装仍需具体方案授权，不顺带修改用户全局配置。

## 官方来源与本轮使用

- Flutter 官方说明：https://docs.flutter.dev/ai/tools
- Flutter Skills：https://github.com/flutter/agent-plugins
- Dart Skills：https://github.com/dart-lang/skills
- Flutter CLI：https://docs.flutter.dev/reference/flutter-cli
- 本轮实际读取 `flutter-apply-architecture-best-practices`，用于检查对象职责与四层归属；读取 `flutter-build-responsive-layout`、`flutter-add-widget-test`、`flutter-add-widget-preview` 和 `dart-add-unit-test`，用于更新布局、测试及预览约束。来源为官方仓库在线 SKILL.md，未安装外部副本。
- 具体来源链接、后续任务路由在团队 Skill 的 `references/dwy-flutter-tooling.md`，避免在本报告复制官方手册或固定其动态 API。

## 验证

- Skill Creator `quick_validate.py`：通过。
- CLI `node --test tests/stack-skills.test.js`：通过；覆盖模板扫描、Skill 及其直接引用资料发现与既有同步行为。
- 本地相对引用：全部有效；根入口 Flutter/项目经验标题各保留一处；跟踪文件空白检查通过。独立场景复核另记录于 `.dwy/tasks/flutter-foundation/skill-review.md`。
- 本轮仅改变开发规范与入口，未安装 Flutter/Dart SDK、官方插件或 MCP，未执行 Flutter 分析、组件测试、宿主构建或 Playground 运行。

独立场景复核发现官方集成测试 Skill 中 Driver 启用步骤需要隔离生产入口；已在测试规范明确限定为独立测试入口/构建，并要求按当前 SDK 的 integration_test 文档核对，不机械把自动化扩展加入生产 main。

## 官方 Skill / MCP / CLI / SDK 四项核对

用户进一步明确 Flutter 和 iOS 都必须核对四类能力。已将四项核对设为 Flutter、Swift、iOS 和 macOS 的开发前必做检查，包含来源、实际连接状态、CLI 路径/版本、选中 SDK、宿主与目标 runtime。适用且已连接的官方能力直接使用；本轮条件未变可复用证据。核对不自动授予安装、升级、授权外部代理或接受许可的权限。

实际环境核对：默认 `xcodebuild -version` 报当前 developer directory 是 Command Line Tools，默认 `xcrun --sdk iphoneos --show-sdk-version` 失败；仅在单条命令设置已有 Xcode 的 `DEVELOPER_DIR` 后，读回 Xcode 27.2（27B52）和 iOS SDK 27.2。未执行全局 xcode-select 切换。当前会话未暴露 Dart/Flutter 或 Xcode 官方 MCP 工具，不能标成已连接。

Apple 官方 MCP 来源已核实为 Apple 文档 `Giving external agents access to Xcode` 与 Tech Talk `Meet agentic coding in Xcode`；Flutter MCP 来源为官方 AI 接入指南。规范只引用实际可核实能力，不凭第三方包名判断官方身份。

追加验证：四份 Skill 的 quick_validate 均通过；Apple + stack 模板发现/同步测试共 8 项通过；四类 Skill 下的 21 个本地相对链接全部有效；跟踪文件空白检查通过。未执行安装或全局配置变更。

## 复用与后续

沿用现有 `dwy-flutter-development` 和 CLI 自动扫描分发，不增加第二份竞争 Skill、不复制整套官方插件到模板、不改 Skills 启用选择。未来通过现有 dwy 同步流程接入；本次未提交、推送或发布。
