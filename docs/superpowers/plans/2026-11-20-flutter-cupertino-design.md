# DWY Flutter Cupertino 薄封装实施计划

> 实施时按本计划的复选框逐项推进。本文是待评审方案。

## 目标与范围

以官方 `cupertino_ui` 为界面底座，将现有 `dwy_design` 迁移为 Android 和 iOS 共用的 Apple 风格基础库。项目通过共享主题和基础组件获得统一风格，产品间可以覆盖品牌色和字体。组件有共用外观或交互变更时，在共享包调整一次，消费方升级依赖即可获得更新。

沿用 Flutter 3.50.0、Dart 3.14.0、iOS 18+ 和 Android 10+。`cupertino_ui` 有独立版本号，本次评估候选为 Flutter 官方发布的 `1.1.6`，许可证 BSD-3-Clause，声明 Flutter ≥3.47、Dart ^3.13。实施前复核版本并运行工作区依赖解析。[官方迁移说明](https://docs.flutter.dev/release/breaking-changes/material-ui-and-cupertino-ui) · [包版本](https://pub.dev/packages/cupertino_ui/versions/1.1.6) · [版本源码](https://github.com/flutter/packages/blob/cupertino_ui-v1.1.6/packages/cupertino_ui/pubspec.yaml)

首期交付共用主题、现有组件迁移、Gallery 示例及移动端验证。项目业务组件在实际消费场景中逐步抽取。Liquid Glass、双端切换两种设计体系、整套 Cupertino API 镜像和公开发包均在首期范围之外。

## 封装边界

| 层级 | 做法 | 实例 |
|---|---|---|
| 官方控件 | 由应用按需直接使用，继承根 `CupertinoTheme`。 | `CupertinoApp.router`、导航栏和 Tab、日期滚轮、滑块、分段控件 |
| DWY 主题 | 复用 `DwyBrand`、`DwyTokens` 和 `DwyTheme` 入口。主题负责动态色、文字、表面和分隔线，令牌负责共用间距和圆角。 | 项目在应用入口设置品牌色和浅深主题，页面通过共用主题获取默认值。 |
| DWY 基础组件 | 用官方控件实现，公开接口围绕共用视觉和行为。优先延用现有名称和调用语义。 | 按钮、输入、搜索、设置分组、状态页、确认和 Sheet |
| 应用业务组件 | 放在所属项目的 Feature 或应用级共享 UI。跨项目出现相同工作流后，再核对输入和行为，抽到单独的共享模块。 | 含产品文案、校验和权限的编辑表单，或涉及数据和路由的选择流程 |

平台差异集中在实际需要它的入口。例如直接沿用 Flutter 的系统键盘、`SafeArea` 和返回事件，由共享 Sheet 处理底部内容布局。根路由与 Tab 页面栈由应用装配。保留 Flutter 标准的 `Widget`、`Color`、`FocusNode` 等类型，组件 API 避免重新定义官方已有的通用能力。

## 任务一 · 锁定主题和消费边界

- [ ] 核对 `flutter/packages/dwy_design/pubspec.yaml`、`flutter/pubspec.lock`、Gallery 与仓库外已知消费者。记录哪些调用方依赖 `DwyTheme.create` 返回的 Material `ThemeData`，哪些使用 `ColorScheme`、`ButtonStyle` 或 `ThemeData.copyWith`。这些属于明确的接口迁移点。
- [ ] 先在 `flutter/packages/dwy_design/test/theme_test.dart` 写预期，再迁移 `flutter/packages/dwy_design/lib/src/theme.dart` 和 `flutter/packages/dwy_design/lib/src/tokens.dart`。建议 `DwyTheme.create` 返回独立包的 `CupertinoThemeData`，应用通过 `CupertinoApp.theme` 安装。现有令牌采用可跟随 Widget 树更新的作用域，保留 `DwyTheme.tokensOf(context)` 调用方式。
- [ ] 验证同一套组件可接受两个项目的品牌配置，系统浅深色切换后主题与组件一致，中文和大字号下可读。平台字体走系统回退，应用可以按需提供有双端分发许可的字体。保留产品级覆盖，避免把某个应用的品牌写到共享默认值中。

## 任务二 · 迁移现有组件并保持调用语义

改动集中在 `flutter/packages/dwy_design/lib/src/`，每组先补 `flutter/packages/dwy_design/test/components_test.dart` 的行为断言。沿用 `flutter/packages/dwy_design/lib/dwy_design.dart` 作为公共入口。

| 组件 | 官方底层 | 迁移验收 |
|---|---|---|
| `DwyButton` | `CupertinoButton` | 主次、弱化和危险样式层级清晰。加载时保留文字并阻止重复触发，禁用态保持禁用。 |
| `DwyTextField`、`DwySearchField` | `CupertinoTextField`、`CupertinoTextFormFieldRow`、`CupertinoSearchTextField` | 保留标签、帮助及错误、表单校验、提交和清除回调。控制器和焦点的生命周期继续由调用者管理。 |
| `DwySettingsGroup`、`DwySettingsTile` | `CupertinoListSection.insetGrouped`、`CupertinoListTile` | 分组标题和脚注可换行，说明可读。整行与尾部独立动作保持各自的点击和语义。 |
| `DwyStatusView` | `CupertinoActivityIndicator` 和 Flutter 布局 | 保留空态、加载、错误和调用方提供的重试操作。 |
| `showDwyConfirmation` | `showCupertinoDialog` 和 `CupertinoAlertDialog` | 只有确认返回 `true`。取消、系统返回等退出统一返回 `false`。调用方仍在取得结果后执行实际操作。 |
| `showDwySheet<T>` | `showCupertinoSheet` | 保留 `Navigator.pop` 的类型化结果、安全区、键盘避让和长内容滚动。拖拽关闭与内容滚动联动，取消时不产生提交结果。 |

- [ ] 只为这些有共享默认值或行为的组件提供 DWY 入口。一处直接使用的官方控件留在页面内。出现跨项目复用需求时再评估扩展公共 API。
- [ ] 处理 `flutter/packages/dwy_image/lib/src/image.dart` 的 Material 占位色与加载、错误控件。保持图片源、缓存、重试、占位 builder 和公开接口的原有行为，验证可在 Cupertino 根组件中挂载。图片包继续可被单独消费。

## 任务三 · 接入 Gallery 与项目复用入口

- [ ] 将 `flutter/examples/component_gallery/lib/app/gallery_app.dart`、组件页、图片示例和 Widget Preview 迁到 Cupertino 根。保留 Gallery 的常用导航与组件入口。在现有示例中覆盖分组设置、搜索列表、带键盘和底部保存按钮的编辑 Sheet，以及浅深和品牌配置。
- [ ] 在 `flutter/docs/design-system.md` 写清根主题安装、直接使用官方控件的边界，以及应用如何组合业务组件。同步 `flutter/AGENTS.md`、`flutter/docs/development-baseline.md` 和 Flutter 团队 Skill 中仍面向当前开发的 UI 基线。历史验证记录保留原时间和结果。
- [ ] 验证一个已知消费者能用锁定的仓库版本接入 `dwy_design`。有现有消费者时优先选它做一次代表性页面迁移。需要用独立样例验证跨仓依赖时复用 Gallery 所示的入口，避免把本机绝对路径写入项目依赖。记录调用方 Material 特有 API 的替换方式和升级注意事项。

## 任务四 · 用一套用例验证双端

- [ ] 从 `flutter/` 运行 `flutter pub get`、`flutter analyze packages/dwy_design packages/dwy_image examples/component_gallery`。分别在两个包和 Gallery 目录执行 `flutter test`。将实际通过的组件行为同步到对应的 `test/TEST_CASES.md`。
- [ ] 在 Android 和 iOS 执行同一条设备流程「搜索列表 → 打开详情 → 编辑 → 打开 Sheet → 聚焦最后一个输入框 → 保存或取消 → 返回」。检查键盘避让、安全区、Tab 返回栈、浅深色、中文和大字号。Android 同时检查系统返回和较新系统的预测性返回，iOS 检查页面侧滑。分别记录构建、运行和交互结果。
- [ ] 确认至少一个消费入口能用同一套 UI 在双端运行。验收标准包括切换共享主题后共用组件更新、确认与取消语义一致、底部保存可达。未覆盖的系统版本在记录里列明。
