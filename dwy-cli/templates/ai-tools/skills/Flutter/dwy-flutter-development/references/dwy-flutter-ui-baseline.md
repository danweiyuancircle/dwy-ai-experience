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

Material/Cupertino 已拆成独立包，SDK 内置设计库在 3.50 正式废弃。新 Material UI 从 `package:material_ui/material_ui.dart` 导入；不为未使用的 Cupertino 引入独立包。UI 包与 Flutter SDK 独立选版本并记录锁定结果，不能认为升级 Flutter 就升级了 Material。

迁移顺序：

1. 查 [官方迁移说明](https://docs.flutter.dev/release/breaking-changes/material-ui-and-cupertino-ui)，追踪当前源码、测试、示例及直接/传递依赖的 import 和公开 UI 类型。
2. 使用本次 SDK 的 `dart fix --dry-run --code=migrate_design_widgets` 预览，只应用与任务相关的迁移。新增直接依赖遵循已有选型规则；每个直接 import 的成员包自己声明依赖。
3. 统一公开 ThemeData、ColorScheme、TextTheme、组件主题及回调签名的类型来源。新旧库同名类型不同，必须迁移相应依赖契约；禁止 dynamic/cast 绕过。
4. 核对本版本独立库的国际化入口，例如 `GlobalMaterialLocalizations.delegates`，验证产品实际支持语言。不要机械保留旧 flutter_localizations 配置。
5. 只有第三方旧 Widget 实际需要旧 Theme/Localizations 时，在根装配使用 `MaterialUiCompatibilityBridge`，记录需要它的具体依赖和移除条件。桥只能向下提供上下文，不能转换公开 API 的新旧类型。
6. 运行分析和受影响测试，验证浅深主题、输入、弹层、导航与本地化，再做目标平台构建/交互验收。基础库公开类型迁移属于破坏性变更，发布时按实际消费影响处理。

## 升级闭环

升级前核对官方正式标签/发行记录、迁移说明、SDK 路径及已有改动；保留可恢复的旧 SDK。共享 PATH 中 SDK 的升级影响其他使用它的项目，要明确报告。

升级后回读 `flutter --version --machine`、Dart 路径及 `flutter doctor -v`；按已选流程解析依赖、运行生成器、format、analyze、测试及目标平台构建。仅更新锁文件中解析确需变化的内容，不顺带升级全部依赖，不用 overrides 掩盖冲突。

同步项目 SDK 配置、CI、宿主、文档和验证记录。依赖解析失败或设备缺失时标明未完成，不伪造兼容通过。官方 Skill 示例和在线最新 API 都须核对当前项目版本；不因示例较新而提高包下限。

来源：[Flutter SDK 归档](https://docs.flutter.dev/install/archive)、[SDK 升级](https://docs.flutter.dev/install/upgrade)、[pubspec SDK 约束](https://dart.dev/tools/pub/pubspec#sdk-constraints)。
