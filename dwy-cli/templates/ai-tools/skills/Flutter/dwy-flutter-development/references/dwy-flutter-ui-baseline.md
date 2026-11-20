# 开发基线、UI 迁移与 SDK 升级

## 基线的四个维度

团队新项目和首次封装基础库统一采用 Flutter 3.50.0 stable / 内置 Dart 3.14.0。全部新基础包声明 Dart 3.14 下限，依赖 Flutter 的包同时声明 Flutter 3.50 下限；不保留旧版本兼容入口或适配层。实际版本仍从 SDK 回读，不单独升级 Flutter 工作区的 Dart。其他已有项目使用项目锁定版本；SDK 安装与升级遵循用户授权，不因 Skill 刷新而改动。

| 维度 | 权威来源 | 约束 |
| --- | --- | --- |
| 精确开发工具链 | 项目已有 SDK 配置与 CI；缺少时在项目文档集中记录 | 开发机与 CI 固定精确 Flutter 版本，不使用浮动 stable/latest；pubspec.lock 不负责锁定 SDK |
| 包兼容下限 | 每个包的 pubspec.yaml environment | 按目标包下限选语法/API；没有验证不能声称支持下限 |
| 平台基线 | 宿主工程、插件与 CI | 新移动项目 iOS 18+、Android 10+（minSdk29）；分别核对 target/compile SDK、Xcode、JDK/Gradle |
| 实测范围 | 当前源码的 CI/运行记录 | 分别列分析、测试、构建、浏览器和目标设备结果 |

纯 Dart 基础包保持纯 Dart 依赖，只声明 Dart 3.14 下限，不为约束版本引入 Flutter。Flutter SDK 约束目前只执行下限，不能用 `environment.flutter` 的范围代替工具链固定或版本兼容测试。

## Flutter 3.50 UI 基线

Flutter 3.50 的 DWY UI 使用独立 `cupertino_ui`，统一采用 Apple 风格。UI 包与 Flutter SDK 独立选版本，按工作区解析结果核对。

1. 查 [官方迁移说明](https://docs.flutter.dev/release/breaking-changes/material-ui-and-cupertino-ui)，跟踪源码、测试、示例和第三方依赖使用的公开 UI 类型。直接导入的成员自行声明依赖。
2. 应用用 `CupertinoApp` 和 `DwyTheme.create` 装配主题。项目令牌通过 `DwyTheme.withTokens` 装配。国际化用独立包的 `GlobalCupertinoLocalizations.delegates`，验证产品实际支持的语言。
3. Flutter 核心布局使用核心 Widget。已有 Cupertino 控件直接使用，共用样式和交互使用 `dwy_design`。只有实际消费旧 SDK Cupertino Widget 时才核对 `CupertinoUiCompatibilityBridge` 的上下文适用范围。
4. 用共用 Widget 用例验证主题、输入、弹层和导航，再用同一条流程验证 iOS 和 Android 安全区、键盘与返回。公开主题类型变化需同步消费方接入。

## 升级闭环

升级前核对官方正式标签/发行记录、迁移说明、SDK 路径及已有改动；保留可恢复的旧 SDK。共享 PATH 中 SDK 的升级影响其他使用它的项目，要明确报告。

升级后回读 `flutter --version --machine`、Dart 路径及 `flutter doctor -v`；按已选流程解析依赖、运行生成器、format、analyze、测试及目标平台构建。仅更新锁文件中解析确需变化的内容，不顺带升级全部依赖，不用 overrides 掩盖冲突。

同步项目 SDK 配置、CI、宿主、文档和验证记录。依赖解析失败或设备缺失时标明未完成，不伪造兼容通过。官方 Skill 示例和在线最新 API 都须核对当前项目版本；不因示例较新而提高包下限。

来源：[Flutter SDK 归档](https://docs.flutter.dev/install/archive)、[SDK 升级](https://docs.flutter.dev/install/upgrade)、[pubspec SDK 约束](https://dart.dev/tools/pub/pubspec#sdk-constraints)。
