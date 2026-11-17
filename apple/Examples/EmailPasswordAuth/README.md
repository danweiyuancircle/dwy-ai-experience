# 邮箱密码登录示例

用 XcodeGen 在本目录执行 `xcodegen generate`，再打开生成工程。

示例通过本地 SwiftPM 包引用 `AuthCore`、`AuthUI`，使用真实 HTTP 客户端，没有模拟登录。把 `EmailPasswordAuthApp.swift` 中 AppConfig.authBaseURL 替换为完整应用后端 URL，并配置后端邮件与数据库迁移后，才可完成真实注册。

宿主示例展示 Keychain 保存、安装级设备 UUID、注册登录完成回调、退出、冷启动恢复与进入前台续期。默认域名 `https://api.example.com/adbox` 只作配置示意，不是可用服务。

此示例不是 ADBox 客户端接入验收；真实邮件送达与后端部署需独立验证。

`Tests/AuthFlowUITests.swift` 覆盖首次自动呈现、注册/找回密码切换和空邮箱错误提示；生成工程后可直接运行 scheme 的测试。
