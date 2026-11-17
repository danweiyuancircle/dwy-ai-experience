# AuthAppleIOS 回归清单

- AppleSignInProviderTests：nonce 原样进入原生请求，姓名/邮箱 scopes，宿主窗口锚点，委托保活，Task/系统取消、并发拒绝、取消后重试、迟到回调隔离，无锚点及无效 nonce 拒绝；UTF-8 凭据解析、首次/空/再次授权姓名，缺失/空/非 UTF-8 凭据拒绝，非取消系统错误原样抛出。

在 iOS simulator 中执行该测试 target；macOS 的 SwiftPM 测试不执行 iOS 原生适配用例。真实 Apple ID 授权另需宿主签名与真机验收。
