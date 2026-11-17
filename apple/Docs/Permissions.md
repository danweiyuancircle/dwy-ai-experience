# 权限模块接入

适用基线：iOS 18+、macOS 26+ Apple Silicon。源码已纳管；消费方仍使用仓库根 SwiftPM 入口和包含本功能的已发布语义化 tag。权限产品从 0.9.0 起提供，0.8.2 及更早 tag 不包含这些产品。

## 选择产品

- `PermissionCore`：PermissionState、PermissionClient、LocalNetworkAccess、FileAccessScope、PermissionAttributions。
- `PermissionIOS`：iOS 配置检查和应用设置跳转，不隐式链接所有权限框架。
- 按需选择 `PermissionCameraIOS`、`PermissionPhotoLibraryIOS`、`PermissionMicrophoneIOS`、`PermissionContactsIOS`、`PermissionSpeechIOS`、`PermissionMotionIOS`、`PermissionMediaLibraryIOS`、`PermissionBluetoothIOS`、`PermissionTrackingIOS`、`PermissionSiriIOS`。
- 独立范围接口：`PermissionNotificationIOS`、`PermissionCalendarIOS`、`PermissionRemindersIOS`、`PermissionLocationIOS`、`PermissionHealthIOS`、`PermissionFaceIDIOS`。
- `PermissionMac`：MacPermissions 的状态、原生申请与 PermissionFlow 设置引导。
- `PermissionUI`：PermissionExplanation；复用两端 DesignKit，基础请求逻辑不依赖它。

例如相机产品在 Xcode 中只选 PermissionCameraIOS、PermissionIOS、PermissionCore；应用使用的每个 SwiftPM product 都须在宿主 target 明确依赖。不要直接依赖第三方内部 target。

## iOS 请求与恢复

```swift
import PermissionCore
import PermissionIOS
import PermissionCameraIOS

@MainActor
func enableCamera() async throws -> PermissionState {
    try await IOSPermissions.camera.request()
}

@MainActor
func openPermissionSettings() async -> Bool {
    await IOSPermissions.openSettings()
}
```

调用方区分 notDetermined、authorized、denied、restricted、limited、provisional、ephemeral、writeOnly、whenInUse、always、unknown 和 unsupported。不提供混淆有限授权与完整权限的全局 Bool。拒绝或受限后不会反复申请；打开设置返回 true 只代表系统接受跳转，从设置返回后调用 status() 读取实际状态再恢复业务。

同 id、同范围 PermissionClient 请求会合并，重复系统完成回调只消费一次；不同权限不建立隐式请求队列。取消等待不关闭系统弹框；系统请求结束后取消的调用者抛 CancellationError，不执行成功路径。宿主应让自己的 Task 跟随页面生命周期。

| 入口 | 配置与语义 |
|---|---|
| camera | NSCameraUsageDescription |
| photoLibrary | NSPhotoLibraryUsageDescription；limited 保留为 limited，不自动申请全部照片 |
| microphone | NSMicrophoneUsageDescription |
| contacts | NSContactsUsageDescription；有限联系人授权保留 |
| speech | NSSpeechRecognitionUsageDescription；实际录音还需独立麦克风授权 |
| motion | NSMotionUsageDescription |
| mediaLibrary | NSAppleMusicUsageDescription |
| bluetooth | NSBluetoothAlwaysUsageDescription；授权不代表蓝牙已开或设备可用 |
| tracking | NSUserTrackingUsageDescription；限制条件按系统策略执行 |
| siri | NSSiriUsageDescription，并按业务配置 Siri capability |
| notifications(options:) | 使用 UserNotifications 原生 options；provisional/ephemeral 不压成普通允许 |
| calendar(access:) | .full 对应 NSCalendarsFullAccessUsageDescription；.writeOnly 对应 NSCalendarsWriteOnlyAccessUsageDescription；完整请求可从只写授权升级 |
| reminders | NSRemindersFullAccessUsageDescription |
| LocationPermission | 请求时使用 NSLocationWhenInUseUsageDescription；always 同时需要 NSLocationAlwaysAndWhenInUseUsageDescription；snapshot 分别返回范围与 isPrecise |
| requestHealth(read:write:) | 设备支持和 HealthKit capability；按实际类型提供 NSHealthShareUsageDescription、NSHealthUpdateUsageDescription；完成不代表获准读取，healthWriteStatus 只能查询写入 |
| authenticateWithBiometrics(reason:) | 非空用途；Face ID 需 NSFaceIDUsageDescription；返回一次认证结果，不伪造长期权限状态 |

库在申请前检查必需用途文案，缺失时抛出配置错误。entitlements、签名和系统策略仍由宿主负责；有用途文案不等于 capability 配置完整。

定位对象在主线程创建并由页面持有；同一对象不允许重叠的首次请求。always 升级由用户明确触发，系统保持 whenInUse 时不保证回调，因此升级只发起申请并立即返回当前状态；宿主在适当时机重新读取 snapshot，不等待虚构的完成事件、不循环请求。不同页面应复用同一个定位对象，避免各自触发申请。

## macOS

```swift
import PermissionCore
import PermissionMac

@MainActor
func enableMicrophone() async throws -> PermissionState {
    let permissions = MacPermissions()
    return try await permissions.request(.microphone)
}
```

MacPermissions 由窗口或页面持有，打开引导用 openSettings(for:guidance:)，消失时调用 closeGuide()；localeIdentifier 随应用语言传入。

- camera、microphone、calendars、reminders 使用原生申请并保留受限/只写状态；用途 key 与上表对应。
- accessibility、inputMonitoring、screenRecording、bluetooth、mediaAppleMusic 使用系统或上游状态提供者；系统无法证明的状态保留 unknown。
- fullDiskAccess、localNetwork 无可靠全局授权查询，始终返回 unknown，必须实际执行目标 I/O 或连接验证。
- appManagement、developerTools 等仅支持设置引导，不伪造通用申请结果；request 对非原生申请项抛 requiresSystemSettings。
- guidance 使用 PermissionFlow 原生引导，不额外为悬浮面板申请 Accessibility；无窗口跟踪权限时跟随能力受系统限制。
- FDA 不绕过 App Sandbox，不能代替用户选择文件授权。沙盒网络需 network.client，监听需 network.server；摄像头、麦克风等 capability 按真实业务配置。

## 本地网络

```swift
import PermissionCore

func probeDevice(host: String, port: Int) async -> LocalNetworkAccess.Result {
    await LocalNetworkAccess.probe(host: host, port: port)
}
```

连接实际目标才可能触发系统本地网络弹框；在宿主 Info.plist 声明 NSLocalNetworkUsageDescription，Bonjour 服务另声明 NSBonjourServices。普通互联网请求通常没有同类授权弹框。

probe 返回 open、closed、localNetworkDenied，仅系统明确拒绝才进入权限引导，不能把超时或 No route to host 当权限拒绝。首次系统授权保留连接等待，waitForLocalNetworkAccess 用于失败页恢复监听，离开页面必须取消其 Task；true 仅说明权限不再阻断，目标端口仍可能拒绝。监听开始前使用真实有效的端口，禁止以 0 端口触发授权。

## 所选文件

```swift
import Foundation
import PermissionCore

func readSelectedFile(_ url: URL) throws -> Data {
    try FileAccessScope().withAccess(to: url) { try Data(contentsOf: $0) }
}
```

选择器仍用平台原生 fileImporter 或 DesignKitMac 的 EFileDialog。scope 在同步/异步操作返回或抛错时释放；startAccessing 返回 false 不自动认定拒绝，因为容器 URL 可能无需 scope。真实 I/O 错误必须向用户报告。当前不存 bookmark，跨启动复用由有真实需求的宿主另行处理。

## 说明 UI 与许可

PermissionExplanation 接收宿主已本地化的标题、说明、设置按钮、重试按钮及 async 动作；不会自动请求权限或替宿主控制重连。动作绑定 SwiftUI task 生命周期，页面消失时取消；宿主动作也须遵守取消语义，不能再启动脱离页面的后台业务。openSettings 动作需处理跳转失败，retry 动作需重新检查真实权限。组件依赖现有 DesignKit 根装配规则。

通过 PermissionAttributions.text() 获取随包附带的 MIT 声明，并纳入应用开源许可说明。上游来源、补丁和未采用实现见 apple/Docs/Permissions-Upstream-Audit.md。

## 验证边界

单元测试只证明状态保真、并发、取消、文件生命周期与网络结果分类，不证明系统弹框、签名权益或商店审核通过。新宿主必须逐项验证首次允许、拒绝、受限、设置返回、窗口/页面关闭和真实业务操作；不得为了验收擅自修改系统隐私数据库或重置设备。
