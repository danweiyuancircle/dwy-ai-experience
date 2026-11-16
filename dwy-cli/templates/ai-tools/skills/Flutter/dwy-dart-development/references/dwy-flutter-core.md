# Dart 编码、配置与输入边界

- 遵循 [Effective Dart](https://dart.dev/effective-dart) 和项目 analyzer 配置。文件用 snake_case，类型用 UpperCamelCase，成员用 lowerCamelCase。
- 核对目标包 `environment.sdk` 后选择语法与 API；开发 SDK 高于下限不代表可以直接使用新特性。不得用 language version override 掩盖不兼容声明。
- 导出 API 写清用途、返回语义，以及取消、资源或线程约束；公开边界有类型，JSON/平台/文件等外部输入要验证。
- 简单模型允许手写类型安全转换；已选生成器的项目按其锁定版本生成。不要为几个字段强制引入 Freezed、json_serializable 或 build_runner。
- 使用官方 `dart format`；不靠手工排版或忽略 analyzer 错误代替检查。生成文件使用对应工具产生，不手写冒充。
- 导入风格与现有 lint 保持一致；不要为了本 Skill 全仓重排 import、提常量或拆类。
- 编译时配置、应用配置均不等于保密机制；不要把私钥、服务端密钥或密码打进 APK/IPA。环境示例使用占位符。
- Dart 单测放 `test/`，文件以 `_test.dart` 结尾；用外部可观察的结果验证正常与失败路径，不只断言 mock 被调用。
