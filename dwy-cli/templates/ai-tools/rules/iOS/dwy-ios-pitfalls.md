---
description: iOS / Swift / SwiftUI 开发避坑清单（XcodeGen / 签名 / 真机部署 / SwiftUI 代码踩坑）
paths:
  - "**/*.swift"
  - "**/project.yml"
  - "**/Package.swift"
---

# iOS 开发坑清单

> 动手前先对照本清单避开已知坑；踩到新坑随手按四栏格式（现象 / 根因 / 正确做法 / 适用）追加到对应分类，没有合适分类就新建一个。

## 分类索引

- 工程与构建（XcodeGen / SPM / Xcode 工程）
- 签名与真机部署
- 证书 / Keychain / mTLS
- 排查方法论
- Swift / SwiftUI 代码
- 其他分类遇到再加：StoreKit / 内购、Info.plist / 权限 / Capability、上架审核

---

## 工程与构建

### XcodeGen 工程要打开 .xcodeproj，不能直接打开项目文件夹

- **现象**：Xcode 里左侧根节点是文件夹名、右边只显示 `Package.swift`，点项目没有 General / Signing & Capabilities 标签页；选不到真机、装不上真机。
- **根因**：用 Xcode 直接打开了**项目文件夹**（或 `Package.swift`），Xcode 把它当 Swift Package（纯库）加载，没有 app target，自然没有签名页、也不能跑真机。
- **正确做法**：先 `xcodegen generate` 生成 `<项目>.xcodeproj`，再用 Xcode 打开这个 `.xcodeproj`（Finder 双击或 File → Open），**不要打开文件夹 / Package.swift**。打开对了，左侧根节点是蓝色 app 图标、底下有 TARGETS。
- **适用**：用 XcodeGen 且 `.xcodeproj` 不入库（被 .gitignore）的工程。SPM-only 的纯库项目本就没 app target，不适用。

### .xcodeproj 是生成物，Xcode 里手改设置会被 xcodegen 覆盖

- **现象**：在 Xcode 里改了签名 / Build Settings / bundle id，下次 `xcodegen generate` 之后改动全没了。
- **根因**：`.xcodeproj` 由 `project.yml` 生成、通常不入库；`xcodegen generate` 整体重建工程，覆盖一切手改。
- **正确做法**：需要持久化的工程设置（签名、bundle id、Build Settings、Info.plist 键）一律改 `project.yml` 再 `xcodegen generate`。Xcode 里手改只用于临时试验。
- **适用**：XcodeGen 工程。

### Package.swift 的 .macOS 平台声明，别为「只支持手机」删掉

- **现象**：想让 app 只支持 iPhone，看到 `Package.swift` 里 `platforms: [.iOS(.v17), .macOS(.v14)]` 就想删掉 `.macOS`。
- **根因**：这是**纯逻辑库**的平台声明，作用是让命令行 `swift test` 能在 mac（host）上跑核心逻辑测试，和 iOS app 支持哪些设备**无关**。app 的设备类型由 app target 的 `TARGETED_DEVICE_FAMILY` 控制。删掉 `.macOS` 会让 `swift test` 在 mac 上跑不起来。
- **正确做法**：保留 `.macOS(.v14)`。要 app 只支持手机，设 app target `TARGETED_DEVICE_FAMILY: "1"`（1=iPhone，2=iPad）。库的 platforms 是「最低支持平台」，不影响 app。
- **适用**：两层结构（SPM 纯逻辑库 + iOS app）、靠命令行 `swift test` 验证核心逻辑的工程。

### XcodeGen 加 String Catalog，要靠 CFBundleLocalizations 才生成多语言 .lproj

- **现象**：加了 `Localizable.xcstrings` 并翻译了多国语言，运行时却只显示开发语言（如中文），系统切语言 / app 内切语言都不生效；`xcodegen generate` 出来的 `.xcodeproj` 里 `knownRegions` 只有 `Base, en`。
- **根因**：XcodeGen 不会扫 `.xcstrings` 内容来推断本地化区域。pbxproj 的 `knownRegions` 决定 Xcode 编译哪些 `.lproj`；某语言不在其中，String Catalog 里该语言就不会编进 app bundle，自建的 `loc()` / 系统本地化都只能回退开发语言。纯 `.xcodeproj` 工程不暴露此坑，因为 `knownRegions` 是手维护的（参考项目 niannian 即如此）。
- **正确做法**：在 `project.yml` 的 app target `info.properties` 下显式声明 `CFBundleLocalizations` 数组，列出全部目标区域（如 `zh-Hans, zh-Hant, en, ja, ko, de, fr, es`）。XcodeGen 会据此把这些区域写进 pbxproj 的 `knownRegions`，Xcode 才会把 `.xcstrings` 编成各语言 `.lproj`。生成后用 `grep -A12 knownRegions TVRemote.xcodeproj/project.pbxproj` 核对区域齐全。
- **适用**：XcodeGen + String Catalog（`.xcstrings`）且 `.xcodeproj` 不入库的工程。

### Info.plist 文案本地化要用固定文件名 InfoPlist.xcstrings

- **现象**：`CFBundleDisplayName`（app 显示名）、各 `NS*UsageDescription`（权限弹窗文案）硬编码成一种语言，想随界面语言本地化，但放进 `Localizable.xcstrings` 不生效。
- **根因**：Info.plist 的面向用户字段不归 `Localizable.xcstrings` 管，Xcode 用一个专门的 String Catalog —— 文件名必须是 `InfoPlist.xcstrings`（大小写敏感），Xcode 自动识别它来本地化 Info.plist 各键。
- **正确做法**：在资源目录建 `InfoPlist.xcstrings`，key 用 Info.plist 的键名（`CFBundleDisplayName` / `NSLocalNetworkUsageDescription` / `NSPhotoLibraryAddUsageDescription`…），各 key 补齐目标语言。XcodeGen 工程把它放进 target 的 sources 目录即自动纳入 resources（`lastKnownFileType = text.json.xcstrings`）；仍需配 `CFBundleLocalizations` 注册区域（见上一条）。`project.yml` 里 `info.properties` 的原值作为开发语言默认保留即可，xcstrings 提供各语言覆盖。
- **适用**：iOS app 本地化 Info.plist 文案，Xcode 15+ String Catalog。

---

## 签名与真机部署

### 命令行/CI 用的 CODE_SIGNING_ALLOWED=NO + 空 DEVELOPMENT_TEAM，装真机前要改

- **现象**：工程命令行编译、模拟器运行都正常，但装不上真机 / 没有可用签名。
- **根因**：`project.yml` 为命令行、CI、模拟器验证配了 `CODE_SIGNING_ALLOWED: "NO"` 和 `DEVELOPMENT_TEAM: ""`；真机安装必须代码签名，这套配置把签名直接关了。
- **正确做法**：真机部署在 `project.yml` 的 app target settings 配 `DEVELOPMENT_TEAM: "<teamID>"` + `CODE_SIGN_STYLE: Automatic`，删掉 `CODE_SIGNING_ALLOWED: "NO"`，再 `xcodegen generate`。命令行 / CI 仍可在调用时用 `xcodebuild ... CODE_SIGNING_ALLOWED=NO` 覆盖，不必把它写死进工程。teamID 在 Xcode → Settings → Accounts 看。
- **适用**：为命令行 / 模拟器验证而关签名的工程，首次要装真机时。

### personal team（免费账号）签名，bundle id 不能用 com.example 等保留前缀

- **现象**：用免费 personal team 自动签名失败 / 注册 App ID 被拒。
- **根因**：`com.example.*`（及 `com.apple.*` 等）是保留 / 示例域名，注册 App ID 会被拒。
- **正确做法**：换成自有反向域名，如 `com.<你的标识>.<app>`；同时改 `project.yml` 的 `bundleIdPrefix` 和 `PRODUCT_BUNDLE_IDENTIFIER`，再 `xcodegen generate`。
- **适用**：免费 personal team 真机调试。付费账号用已注册的 App ID。

### personal team 签的 app 7 天过期、首次需在设备「信任开发者」

- **现象**：免费账号装的 app 几天后打不开；或刚装上点击提示「不受信任的开发者」。
- **根因**：personal team 签名证书有效期仅 7 天；且首次安装的开发者证书需手动信任。
- **正确做法**：过期重新 `Cmd+R` 安装即可；首次安装后到 iPhone → 设置 → 通用 → VPN与设备管理 → 信任你的开发者证书。
- **适用**：免费 personal team。付费账号无 7 天限制。

### devicectl 的设备 UUID 和 xcodebuild 的 -destination id 不是同一套

- **现象**：`xcrun devicectl list devices` 拿到设备 Identifier（如 `5C5E6FAB-D288-559D-9425-3C2754AA401C`），直接拿去 `xcodebuild -destination 'id=...'`，报 `Unable to find a device matching the provided destination specifier` / `no available devices matched`。
- **根因**：两套工具用两套设备标识。`devicectl` 列的是它自己的 CoreDevice UUID；`xcodebuild` 的 `-destination id=` 要的是硬件 ECID 形式的 id（如 `00008101-001645E21406001E`）。同一台真机两个 id 完全不同，不能混用。
- **正确做法**：编译阶段从 `xcodebuild` 报错末尾的「Available destinations for the scheme」里抄那台机器的 `id=`（ECID 形式）传给 `-destination`；安装阶段 `xcrun devicectl device install app --device <UUID>` 用 `devicectl list devices` 的 UUID。即：build 用 xcodebuild 的 id，install 用 devicectl 的 UUID，按名字对上同一台机器。
- **适用**：命令行 `xcodebuild` 编译 + `xcrun devicectl device install` 安装真机的流程（Xcode 15+ / iOS 17+ CoreDevice）。

---

## 排查方法论

### 别把 deploymentTarget 下限误读成「不支持高版本」

- **现象**：看到工程部署目标 iOS 17.0，以为「不支持 iOS 26」，甚至想抬高部署目标来「支持新系统」。
- **根因**：deploymentTarget 是**最低**支持版本（下限），不是上限。iOS 17.0 表示 17 及以上（含 26）全部支持。真机装不上几乎从不是因为这个。
- **正确做法**：真机装不上，按「打开方式 → 签名配置 → Xcode 是否支持该 iOS 大版本」排查，别先动部署目标。另：iOS 新大版本真机需要配套新 Xcode（如 iOS 26 真机需 Xcode 26），但那报的是设备支持 / 架构类错误，也不是改部署目标能解决的。
- **适用**：通用。

### 真机装不上时，拿「同机能跑的另一个项目」做对照

- **现象**：一个项目装不上真机、报错含糊（如 unsupported architecture），方向难定。
- **根因**：同一台 Mac、同一个 Xcode 下，若另一个项目能装真机，说明 Xcode 版本、设备、账号都没问题，差异一定在**这个项目的工程配置**（打开方式 / 签名 / bundle id）。
- **正确做法**：找一个同机能装真机的项目当 working example，逐项对比 `project.yml`、打开方式、签名设置，差异处就是根因——比凭空猜快得多。
- **适用**：手头有可对照项目时的真机部署排查。

---

## 证书 / Keychain / mTLS

### SecIdentityCreateWithCertificate 在 iOS 不存在，组装 SecIdentity 要走 keychain 查询

- **现象**：用 swift-certificates 生成自签证书后想组装 `SecIdentity`，命令行 `swift test`（host 是 macOS）能过，但一编译 iOS（模拟器/真机）就报 `cannot find 'SecIdentityCreateWithCertificate' in scope`，阻断整个 app build。
- **根因**：`SecIdentityCreateWithCertificate` 是 **macOS-only** API，iOS SDK 里没有。只在 macOS 跑 `swift test` 不会暴露——因为测试 host 就是 macOS，能解析到该符号。
- **正确做法**：iOS 上把私钥(`SecItemAdd` + `kSecClassKey`)和证书(`SecItemAdd` + `kSecClassCertificate`)分别入 keychain，再用 `kSecClassIdentity` + `SecItemCopyMatching` 查询——系统会自动把同一公钥的 key+cert 组装成 `SecIdentity` 返回。此写法 iOS / macOS 通用。
- **适用**：iOS 客户端 mTLS / 自签证书 / SecIdentity 组装。两层工程（SPM 纯逻辑库 + iOS app）只靠 `swift test` 验证逻辑时，**务必再补一次 iOS 编译**，否则 macOS-only 的 Security API 会从 `swift test` 漏过去。

### swift-crypto 的 Crypto 产物在 Xcode 测试目标链接报「framework 缺二进制」

- **现象**：给 SPM Core 加了 swift-crypto / swift-certificates 后，app target 能 build，但单元测试目标 `build-for-testing` 报 `clang: error: no such file or directory: .../Crypto_<hash>_PackageProduct.framework/Crypto_<hash>_PackageProduct`。
- **根因**：swift-crypto 的 `Crypto` 产物在 Apple 平台会桥接系统 CryptoKit，其 `PackageProduct.framework` 没有可链接的二进制。测试目标若**同时**依赖 app target 和 `package: <Core>`，就会去直接链这个空 framework 而报缺文件；app target 自身的链接逻辑会跳过它，所以 app build 不受影响、只有测试目标炸。
- **正确做法**：单元测试目标**只依赖 app 宿主 target**（`- target: <App>`），删掉冗余的 `- package: <Core>`。Core 及其传递框架由 app 链接并嵌入，测试经宿主仍可 `import <Core>`（含 `@testable import <App>`）。改 `project.yml` 后 `xcodegen generate` 重生工程。
- **适用**：XcodeGen + SPM，且 unit-test 目标依赖了含 swift-crypto / swift-certificates 这类「Apple 平台会桥接系统库」的包时。

---

## Swift / SwiftUI 代码

### @AppStorage 驱动 .preferredColorScheme 切换后不即时生效（须重启）

- **现象**：设置页切「浅色/深色/跟随系统」，`.preferredColorScheme` 由 `@AppStorage("themeMode")` 驱动，改后界面不变，杀进程重启才生效。换 sheet→push、枚举存值改存 `String` rawValue、调整视图层级都**无效**——全是猜，方向错。
- **根因**：SwiftUI 框架级已知问题——`.preferredColorScheme` 由 `@AppStorage` 驱动时不即时刷新，尤其 `.system` 档对应的 `nil` 不触发更新（iOS 17/18 多人复现）。与「枚举 vs String 的 KVO」无关，换存储类型治不了本。
- **正确做法**：别用 `@AppStorage` 驱动 `.preferredColorScheme`。改用单一 `@MainActor @Observable` 单例（如 `ThemeManager.shared`，持久化自己写 UserDefaults），`@State private var theme = ThemeManager.shared` 在根视图持有，`.preferredColorScheme(theme.mode.colorScheme)` 读它；`@Observable` 属性变化可靠驱动重算，绕开框架 bug。这正是同项目语言切换 `LocalizationManager.shared` 已验证的免重启 pattern——设置类全局开关一律照此办，别走 `@AppStorage` + `App` struct。范例：`Sources/Foundation/DesignKit/ThemeManager.swift` + `TVRemote/App/RootView.swift`。仍命中 nil 不刷新时，system 档读 `@Environment(\.colorScheme)` 当前值兜底代替 nil。
- **适用**：iOS 17+ SwiftUI，运行时切换 `.preferredColorScheme` 需即时生效。推广：任何「设置改后须即时全局生效」的状态，优先 `@Observable` 单例 + `@State` 持有，而非 `@AppStorage` 跨视图/跨 App-struct 同步。

### 隐藏系统导航栏后边缘滑动返回手势失灵

- **现象**：用 NavigationStack 做主路由，页面自绘深色 UI 故 `.toolbar(.hidden, for: .navigationBar)` 隐藏系统导航栏。隐藏后 iOS 左缘右滑返回手势（interactivePopGestureRecognizer）不响应，只能点自绘返回按钮。
- **根因**：`interactivePopGestureRecognizer` 的 `delegate` 默认指向系统导航栏。导航栏被隐藏后，delegate 据「栏不可见」拒绝识别手势，于是边缘返回整体失效。这是 SwiftUI/UIKit 十年老坑，不是 NavigationStack 的 bug。
- **正确做法**：用 `UIViewControllerRepresentable` 在 `didMove(toParent:)` 拿 `navigationController?.interactivePopGestureRecognizer`，置 `isEnabled = true` 并把 delegate 换成**自定义带守卫的 delegate**（`gestureRecognizerShouldBegin` 仅在 `viewControllers.count > 1` 时返回 true）。封装成 `.swipeBackEnabled()` View 扩展。范例见 `TVRemote/App/SwipeBackEnabler.swift`。**切忌把 delegate 置 nil**——见下条。
- **适用**：iOS 16+ NavigationStack（或 UIKit push 栈）+ 隐藏系统导航栏自绘顶栏的场景。手感须真机验证。

### interactivePopGestureRecognizer.delegate 置 nil 致根页崩溃/卡死

- **现象**：为恢复边缘手势把 `interactivePopGestureRecognizer.delegate = nil`。结果：在首页（栈根）边缘右滑后首页卡死、点击崩溃；甚至点返回按钮程序化 pop 也崩溃，app 退到桌面。
- **根因**：UIKit 默认的手势 delegate 含「栈深 ≤ 1 不识别」的守卫，防止 pop 根控制器。置 nil 移除这道守卫，根页边缘滑动会试图 pop 根控制器，UINavigationController 内部状态损坏 → 卡死/崩溃；损坏后任何后续 pop（含程序化 `path = []`）都可能崩。
- **正确做法**：不要 `delegate = nil`。装自定义 `UIGestureRecognizerDelegate`，`gestureRecognizerShouldBegin` 返回 `navigationController.viewControllers.count > 1`，根页（count==1）不放行。`shouldRecognizeSimultaneouslyWith` 返回 false 避免与滚动冲突。delegate 弱引用 navigationController 防循环。
- **适用**：iOS 16+ 自管 interactivePopGestureRecognizer 的场景。本坑由上一条「隐藏 navbar 恢复手势」的错误修法引出，二者要一起记。

### TabView 切页保活视图态，别用 switch 渲染 tab 内容

- **现象**：底部 tab 用 `@ViewBuilder { switch tab { case .a: AViewView() ... } }` 渲染，切 tab 再切回，页面的滚动位置、已加载数据、嵌套导航栈全丢——「重复刷新」。
- **根因**：`switch` 在视图树里每次只保留当前 case 的子树，切 tab 时 SwiftUI **销毁**旧 tab 视图、**重建**新 tab 视图，`@State` 随之重置。它不是缓存容器。
- **正确做法**：用系统 `TabView(selection:)` + 每页 `.tag(...)`。TabView 保活所有 tab 页，切换只是显隐，状态天然保留。隐藏系统 tab bar（`.toolbar(.hidden, for: .tabBar)`）后用自绘底栏，`selection` 与自绘栏共用同一 `@State`。注意别用 `.tabViewStyle(.page)`（会引入左右滑动切页，与边缘返回手势冲突）。
- **适用**：iOS 16+ SwiftUI 多 tab 且需保留各 tab 页内状态时。

### Mac（Designed for iPhone/iPad）上 sheet 不继承 Observable environment，弹层即崩

- **现象**：iPhone 真机正常；把 iOS app 装到 macOS（「在 Mac 上使用 iPhone/iPad App」）后，一点「解锁」/付费墙/编辑设备/键盘 sheet 就崩。崩溃报告 `EXC_BREAKPOINT` / `SIGTRAP`，栈顶 `libswiftCore _assertionFailure` → `SwiftUICore EnvironmentValues.subscript.getter` → `SheetBridge.present` / `PresentationHostingController`。应用日志只到 `app 启动`。
- **根因**：`@Environment(Store.self)` / `@Environment(AppRouter.self)` 在未注入时会 fatal。iPhone 上 sheet 内容通常继承父树的 `.environment(...)`；Mac 上 UIKitMacHelper 走 `PresentationHostingController`，**不把父视图的 Observable environment 传进 sheet**，于是 `PaywallView` 等一 present 就 assertionFailure。
- **正确做法**：凡 sheet / fullScreenCover 内容里读了 `@Environment(SomeObservable.self)`，在 content 上**显式** `.environment(store)` / `.environment(router)` 重注入，不要依赖继承。嵌套 sheet 同样要再注一次。例：`PaywallView().environment(store)`、`DeviceEditSheet(...).environment(router)`、`KeyboardSheet().environment(router)`。
- **适用**：iOS 17+ `@Observable` + `.environment(instance)`，且 app 会在 Mac 上以 Designed for iPhone/iPad 运行时。iPhone 上不重注入多数也能跑，但为跨平台一致应一律重注入。
