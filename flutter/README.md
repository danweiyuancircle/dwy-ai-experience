# DWY Flutter 基础库

iOS 和 Android 共用 Flutter 官方 Cupertino 控件与 DWY 主题。品牌、令牌和共享组件接入见 `flutter/docs/design-system.md`。

## 当前内容

- `flutter/packages/dwy_design`：主题、令牌、基础组件与 widget 测试。
- `flutter/packages/dwy_image`：图片加载、缓存作用域、缩略解码与统一图片组件。
- `flutter/packages/dwy_log`：日志分类、脱敏、轮转、落盘及导出。
- `flutter/packages/dwy_network`：Dio 客户端、解码、取消、真实传输进度和文件提交。
- `flutter/packages/dwy_preferences`：类型化偏好与作用域清理。
- `flutter/packages/dwy_secure_storage`：产品/账户隔离的安全存储。
- `flutter/packages/dwy_database`：Drift/SQLite 连接、生命周期与迁移测试示例。
- `flutter/packages/dwy_media`：无自定义 UI 的相册访问与系统选择器适配。
- `flutter/packages/dwy_permission`：无界面的 iOS / Android 运行时权限，宿主按能力配置用途声明。
- `flutter/packages/dwy_iap`：无界面的商店内购门面（当前适配 `in_app_purchase`），凭据由业务后端验证。
- `flutter/packages/dwy_sign_in`：Apple / Google 第三方登录凭据获取，identityToken 由业务后端验证。
- `flutter/examples/component_gallery`：可交互的组件 Playground，提供 Web 启动入口。
- `flutter/docs/design-system.md`：默认规范、组件接口与定制方式。
- `flutter/docs/architecture.md`：四层边界与后续基础包接入位置。

上述包分别声明依赖，不会因使用一个按钮而引入网络、数据库或相册。工作区开发工具链为 Flutter 3.50.0 stable / Dart 3.14.0，来源与各包兼容范围见 `flutter/docs/development-baseline.md`。

消费项目使用 `dwy-flutter-appkit` Skill，入口位于 `dwy-cli/templates/ai-tools/skills/Flutter/dwy-flutter-appkit/SKILL.md`。按任务读取引用资料，并逐包确认实际解析的来源、版本/提交与公开 API；Skill 和本总览更新不代表消费项目已升级，接入以实际依赖源码为准。

移动端约定支持 iOS 18+、Android 10+（minSdk 29）；实际原生插件、宿主工程及打包产物仍须逐项核对。targetSdk 与最低系统分开管理。

## 启动与检查

使用基线中固定的 Flutter SDK，先核对 `flutter --version --machine` 和 Dart 来源，再执行检查。开发版本和各包声明下限的验证范围分别记录。

```bash
cd flutter
flutter pub get
cd packages/dwy_database
dart run build_runner build
cd ../..
dart format --output=none --set-exit-if-changed packages examples
flutter analyze
```

依赖解析与代码生成成功后，纯 Dart 包（`dwy_database`、`dwy_log`、`dwy_network`）分别在包目录执行 `dart test`；其余 Flutter 包分别执行 `flutter test`。Playground 另行运行：

```bash
cd examples/component_gallery
flutter test
flutter run -d web-server --web-hostname 127.0.0.1 --web-port 5188
```

Playground 地址：`http://127.0.0.1:5188/`。支持桌面侧栏与窄屏目录面板，可切换明暗、品牌色、圆角、按钮内边距，操作表单、搜索、设置、确认弹窗、底部面板和内容状态。

UI 包、测试与 Gallery 使用独立 `cupertino_ui` 1.1.7，公开主题类型来源保持一致。新增 UI 依赖或国际化配置时核对实际版本接口，不直接采用在线最新示例。各包依赖、版本来源和限制见包 README 及迁移记录。

本例先提供 Web 宿主，iOS/Android 宿主工程及签名、设备构建仍待 SDK 环境就绪后生成和验收。不要将 Web 可运行等同于双端验收完成。

## 验收状态

本机 SDK 已升级到 3.50.0 / Dart 3.14.0；各项检查与未完成的设备验收见 `flutter/docs/flutter-3.50-migration.md`。测试清单见各包 TEST_CASES.md，SDK 版本回读不能代替功能验收。

包暂为 `publish_to: none`；未确定分发许可证、发布版本和注册表流程，不执行发布。
