# 测试、预览与移动端验收

测试前必须读取匹配的官方 Skill，入口见 [工具路由](dwy-flutter-tooling.md)。不要把官方 Skill 中的示例当成必须引入某个 Mock/状态管理包的理由。

| 对象 | 官方工具 | 验证重点 |
| --- | --- | --- |
| 纯 Dart 基础逻辑 | `dart analyze`、`dart test` | 错误、资源清理、文件/网络边界与并发 |
| Flutter 包与 Widget | `flutter analyze`、`flutter test` | 渲染、输入、点击、状态变化和语义 |
| 组件预览 | `flutter widget-preview start`（SDK 支持时） | 多主题、尺寸和可交互组件 |
| 完整 Playground | `flutter run -d <device-id>` | 实际页面入口和组件组合 |
| 移动端插件/真实流程 | `flutter test integration_test -d <device-id>` 或实际交互 | 原生权限、持久化、后台与系统行为 |

## 断言与资源

- `test/` 内文件以 `_test.dart` 结尾，UI 交互用 WidgetTester 的 tap/enterText/scroll 后再验证结果。
- 长驻动画/网络未结束时不要无界依赖 pumpAndSettle；按预期帧或状态推进并设置合理期限。
- 优先简单 fake；已有 Mockito/Mocktail 均按当前项目使用，不因偏好新增或替换依赖。真实资源测试用临时目录/本机服务并明确清理。
- Flutter SDK 的 flutter_test 会约束 test_api 等版本；workspace 解析冲突先核对依赖链，不用无依据 overrides 或删除锁文件绕过。
- 数据库生成代码先运行已选工具；迁移测试保留旧 schema/数据，验证实际磁盘重开，不用清库冒充迁移。
- 共享组件/基础库同步 TEST_CASES.md，描述真实测试目标，不能把未运行字段写成通过。
- 官方集成测试 Skill 的 Driver/MCP 示例若要求启用 `enableFlutterDriverExtension`，只用于明确的独立测试入口和测试构建；不得直接加入生产 main、扩大正式应用的自动化控制入口。先按当前 SDK 的 [integration_test 指南](https://docs.flutter.dev/testing/integration-tests) 选择运行方式，记录采用步骤及与示例的差异。

## 验收边界

- UI 新增或改变需可交互 Playground 示例；纯渲染组件可加官方 Widget Preview。预览可能运行于 Web，原生插件、dart:io/ffi 与平台权限另行验证。
- 至少检查浅深主题、品牌覆盖、禁用/加载/失败、长文案、大字体与窄屏。
- iOS 18+、Android 10+ 是本团队新项目支持基线，至少覆盖最低版本和当前目标版本；无可用设备时逐项记录缺口，不把 emulator/真机混称。
- 分别报告：静态文件检查、依赖解析、代码生成、分析、单测、构建、Web Playground、模拟器、真机、发布。任何一项不能代替其他项。
- 安全存储、相册 limited 权限、系统选择取消、低内存后恢复等平台行为不能只靠 fake 测试宣称成功。
