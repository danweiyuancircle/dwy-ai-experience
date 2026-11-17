# PermissionFlow 纳管来源

- 上游：https://github.com/jaywcjlove/PermissionFlow
- 版本：v2.11.4；正式发布于 2026-10-23。
- commit：`65434c9ae04dba97cf52c1dffbe3e4e62b547c82`
- 导入日期：2026-11-17；使用 git archive 导入完整 tag，不包含嵌套 .git。
- 许可：MIT，保留本目录 LICENSE 和原始版权；随 PermissionCore 分发声明资源。

本地补丁：

- `Sources/PermissionFlow/PermissionStatusProviders/FullDiskAccessPermissionStatusProvider.swift` 不再扫描用户目录或按可读性猜测 FDA，返回 unsupported capability 和 unknown 状态。
- `Sources/PermissionFlow/PermissionFlowController.swift` 的 authorize 返回设置跳转是否被接受；失败关闭引导，切换权限时关闭同一控制器旧面板。设置打开函数可注入以测试失败路径，不访问真实系统设置。

根 Package.swift 纳管所需 targets，不使用上游包清单，也不提高本仓部署下限。升级时对比固定 tag，重放以上补丁并验证窗口监听生命周期；第三方类型不出现在 PermissionMac 公开接口。
