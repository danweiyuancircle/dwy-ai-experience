# PermissionsKit 纳管来源

- 上游：https://github.com/sparrowcode/PermissionsKit
- 版本：12.0.0；正式发布于 2026-09-12。
- commit：`1ccec73d2417b9c46aade552d6b2752e40e15a93`
- 导入日期：2026-11-17；使用 git archive 导入完整 tag，不包含嵌套 .git。
- 许可：MIT，保留本目录 LICENSE 和原始版权；随 PermissionCore 分发声明资源。

本地补丁：`Sources/PermissionsKit/Permission.swift` 增加 restricted、limited、unknown；Camera、PhotoLibrary、Contacts、Bluetooth、Tracking、MediaLibrary、Siri、SpeechRecognizer、Motion 的状态映射保留这些差异。其他源码保持上游快照。

SwiftPM 只编译根 Package.swift 声明的按需模块。通知的同步 semaphore、Health 通用状态的 fatalError、生物识别的空用途认证，以及日历/定位的范围压缩不纳入团队公开实现；对应团队适配直接使用原生 API，见 apple/Docs/Permissions-Upstream-Audit.md。禁止向消费者重新导出第三方 Permission 类型。

升级时对比固定 tag，逐项重放补丁、更新能力矩阵并运行两端测试；不自动跟踪上游主干。
