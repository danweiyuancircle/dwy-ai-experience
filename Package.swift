// swift-tools-version: 6.0
import PackageDescription

/// 苹果应用骨架：Shared 横切 + iOS / macOS 平台 UI 基建。
///
/// 部署底线（模板与库一致）：
/// - iOS 18.0+
/// - macOS 26.0+（Apple Silicon）
///
/// SwiftPM 远程依赖要求保留仓库根入口；所有实现、模板和测试统一位于 apple/。
/// App 壳不在此包；用 `apple/scripts/new-app.sh` 从 Templates 生成。
let package = Package(
    name: "AppleAppKit",
    defaultLocalization: "en",
    platforms: [
        .iOS(.v18),
        .macOS("26.0"),
    ],
    products: [
        .library(name: "PermissionCore", targets: ["PermissionCore"]),
        .library(name: "SyncCore", targets: ["SyncCore"]),
        .library(name: "CoreKit", targets: ["CoreKit"]),
        .library(name: "LogKit", targets: ["LogKit"]),
        .library(name: "L10nKit", targets: ["L10nKit"]),
        .library(name: "CacheKit", targets: ["CacheKit"]),
        .library(name: "DesignCore", targets: ["DesignCore"]),
        .library(name: "DesignKitIOS", targets: ["DesignKitIOS"]),
        .library(name: "DesignKitMac", targets: ["DesignKitMac"]),
        .library(name: "DesignKitMacPlayground", targets: ["DesignKitMacPlayground"]),
        .library(name: "BusinessKitMac", targets: ["BusinessKitMac"]),
        .library(name: "PurchaseCore", targets: ["PurchaseCore"]),
        .library(name: "AuthCore", targets: ["AuthCore"]),
        .library(name: "AuthUI", targets: ["AuthUI"]),
        .library(name: "AuthGoogleIOS", targets: ["AuthGoogleIOS"]),
        .library(name: "AuthAppleIOS", targets: ["AuthAppleIOS"]),
        .library(name: "AuthGoogleMac", targets: ["AuthGoogleMac"]),
    ],
    dependencies: [
        .package(url: "https://github.com/groue/GRDB.swift.git", exact: "7.11.1"),
        .package(url: "https://github.com/sushichop/Puppy.git", from: "0.9.0"),
        .package(url: "https://github.com/google/GoogleSignIn-iOS.git", exact: "9.1.0"),
        // 8.1.5 在 2026-10-14 发布，选型时未满 7 天；限制传递依赖使用已稳定版本。
        .package(url: "https://github.com/google/GoogleUtilities.git", exact: "8.1.4"),
    ],
    targets: [
        .target(name: "PermissionCore", path: "apple/Sources/Shared/PermissionCore", resources: [.copy("Resources/ThirdPartyNotices.txt")]),
        .testTarget(name: "PermissionCoreTests", dependencies: ["PermissionCore"], path: "apple/Tests/PermissionCoreTests"),
        .target(
            name: "SyncCore",
            dependencies: [.product(name: "GRDB", package: "GRDB.swift")],
            path: "apple/Sources/Shared/SyncCore"
        ),
        .testTarget(
            name: "SyncCoreTests",
            dependencies: ["SyncCore"],
            path: "apple/Tests/SyncCoreTests",
            exclude: ["TEST_CASES.md"]
        ),
        // MARK: Shared（业务无关、双平台）

        .target(
            name: "CoreKit",
            path: "apple/Sources/Shared/CoreKit"
        ),
        .target(
            name: "L10nKit",
            path: "apple/Sources/Shared/L10nKit"
        ),
        .target(
            name: "LogKit",
            dependencies: [
                .product(name: "Puppy", package: "Puppy"),
            ],
            path: "apple/Sources/Shared/LogKit"
        ),
        .target(
            name: "CacheKit",
            path: "apple/Sources/Shared/CacheKit"
        ),
        .target(
            name: "AuthCore",
            dependencies: ["CoreKit", "L10nKit"],
            path: "apple/Sources/Shared/AuthCore"
        ),
        .target(
            name: "AuthUI",
            dependencies: ["AuthCore", "L10nKit", .product(name: "GoogleSignInSwift", package: "GoogleSignIn-iOS", condition: .when(platforms: [.iOS, .macOS]))],
            path: "apple/Sources/iOS/AuthUI",
            resources: [.process("Resources")]
        ),
        // ThemeMode / Motion 等纯 SwiftUI 共享令牌；不含 UIKit/AppKit。
        .target(
            name: "DesignCore",
            dependencies: ["L10nKit"],
            path: "apple/Sources/Shared/DesignCore"
        ),
        .testTarget(
            name: "DesignCoreTests",
            dependencies: ["DesignCore"],
            path: "apple/Tests/DesignCoreTests",
            exclude: ["TEST_CASES.md"]
        ),

        // MARK: 平台层（两套代码，各自演进）

        .target(
            name: "DesignKitIOS",
            dependencies: ["DesignCore", "L10nKit"],
            path: "apple/Sources/iOS/DesignKit"
        ),
        .testTarget(
            name: "DesignKitIOSTests",
            dependencies: ["DesignKitIOS"],
            path: "apple/Tests/DesignKitIOSTests"
        ),
        .target(
            name: "DesignKitMac",
            dependencies: ["DesignCore", "L10nKit"],
            path: "apple/Sources/macOS/DesignKit"
        ),
        .testTarget(
            name: "DesignKitMacTests",
            dependencies: ["DesignKitMac"],
            path: "apple/Tests/DesignKitMacTests"
        ),
        .target(
            name: "BusinessKitMac",
            dependencies: [
                "DesignKitMac", "DesignCore", "L10nKit", "PurchaseCore", "LogKit",
                "AuthCore", "SyncCore",
            ],
            path: "apple/Sources/macOS/BusinessKitMac",
            resources: [.process("Resources")]
        ),
        .testTarget(
            name: "BusinessKitMacTests",
            dependencies: ["BusinessKitMac", "DesignKitMac", "PurchaseCore", "AuthCore", "SyncCore"],
            path: "apple/Tests/BusinessKitMacTests"
        ),
        .target(
            name: "DesignKitMacPlayground",
            dependencies: ["DesignKitMac"],
            path: "apple/Sources/macOS/DesignKitMacPlayground",
            exclude: ["Scripts", "README.md"],
            resources: [.process("Resources/en.lproj"), .process("Resources/zh-Hans.lproj"), .copy("Resources/Documentation"), .copy("Resources/Examples"), .copy("Resources/Index.md")]
        ),
        .testTarget(
            name: "DesignKitMacPlaygroundTests",
            dependencies: ["DesignKitMacPlayground"],
            path: "apple/Tests/DesignKitMacPlaygroundTests"
        ),
        // iOS 呈现适配只在 iOS 链接 SDK；纯认证核心不依赖 SDK。
        .target(
            name: "AuthGoogleIOS",
            dependencies: [
                "AuthCore",
                .product(name: "GoogleSignIn", package: "GoogleSignIn-iOS", condition: .when(platforms: [.iOS])),
            ],
            path: "apple/Sources/iOS/AuthGoogleIOS"
        ),
        // Apple 系统授权不依赖 Google SDK；AuthCore 保持跨平台。
        .target(
            name: "AuthAppleIOS",
            dependencies: ["AuthCore"],
            path: "apple/Sources/iOS/AuthAppleIOS"
        ),
        .testTarget(
            name: "AuthAppleIOSTests",
            dependencies: ["AuthAppleIOS", "AuthCore"],
            path: "apple/Tests/AuthAppleIOSTests",
            exclude: ["TEST_CASES.md"]
        ),
        // macOS 窗口呈现单独适配，避免 AuthCore 引入 AppKit 或 Google SDK。
        .target(
            name: "AuthGoogleMac",
            dependencies: ["AuthCore", .product(name: "GoogleSignIn", package: "GoogleSignIn-iOS", condition: .when(platforms: [.macOS]))],
            path: "apple/Sources/macOS/AuthGoogleMac"
        ),
        .testTarget(
            name: "AuthGoogleMacTests",
            dependencies: ["AuthGoogleMac", "AuthCore"],
            path: "apple/Tests/AuthGoogleMacTests"
        ),
        // 终身买断 + DEBUG 解锁。试用 / 限额留在 App 的 BizFoundation。
        .target(
            name: "PurchaseCore",
            dependencies: ["L10nKit"],
            path: "apple/Sources/Shared/PurchaseCore"
        ),

        // MARK: Tests

        .testTarget(
            name: "AuthUITests",
            dependencies: ["AuthUI", "AuthCore"],
            path: "apple/Tests/AuthUITests",
            exclude: ["TEST_CASES.md"]
        ),
        .testTarget(
            name: "AuthCoreTests",
            dependencies: ["AuthCore"],
            path: "apple/Tests/AuthCoreTests",
            exclude: ["TEST_CASES.md"]
        ),

        .testTarget(
            name: "CoreKitTests",
            dependencies: ["CoreKit"],
            path: "apple/Tests/CoreKitTests"
        ),
        .testTarget(
            name: "LogKitTests",
            dependencies: ["LogKit"],
            path: "apple/Tests/LogKitTests"
        ),
        .testTarget(
            name: "L10nKitTests",
            dependencies: ["L10nKit"],
            path: "apple/Tests/L10nKitTests"
        ),
        .testTarget(
            name: "CacheKitTests",
            dependencies: ["CacheKit"],
            path: "apple/Tests/CacheKitTests"
        ),
        .testTarget(
            name: "PurchaseCoreTests",
            dependencies: ["PurchaseCore"],
            path: "apple/Tests/PurchaseCoreTests"
        ),
    ]
)

#if os(macOS)
package.products.append(.executable(name: "MotionGallery", targets: ["MotionGallery"]))
package.targets.append(.executableTarget(
    name: "MotionGallery",
    dependencies: ["DesignCore"],
    path: "apple/Examples/Motion",
    exclude: ["project.yml", "README.md", "MotionGallery.xcodeproj"]
))
// 示例只作为开发工具构建，应用仍只链接 DesignKitMac library product。
package.products.append(.executable(name: "MacControlsGallery", targets: ["MacControlsGallery"]))
package.targets.append(.executableTarget(
    name: "MacControlsGallery",
    dependencies: ["DesignKitMacPlayground"],
    path: "apple/Examples/MacControls/Sources/MacControlsGallery"
))
package.products.append(.executable(name: "MacBusinessGallery", targets: ["MacBusinessGallery"]))
package.targets.append(.executableTarget(
    name: "MacBusinessGallery",
    dependencies: ["BusinessKitMac", "DesignKitMac", "LogKit", "AuthCore", "SyncCore"],
    path: "apple/Examples/MacBusiness/Sources/MacBusinessGallery"
))
#endif

 // MARK: 可按权限单独链接；上游源码纳管在 ThirdParty，不要求消费方额外检出仓库。
package.products += [
    .library(name: "PermissionIOS", targets: ["PermissionIOS"]),
    .library(name: "PermissionMac", targets: ["PermissionMac"]),
]
package.targets += [
    .target(name: "PermissionsKit", path: "apple/ThirdParty/PermissionsKit/Sources/PermissionsKit",
            resources: [.process("Resources")]),
    .target(name: "PermissionIOS", dependencies: ["PermissionCore"], path: "apple/Sources/iOS/PermissionIOS"),
]

package.targets += [
    .target(name: "CameraPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/CameraPermission"),
    .target(name: "PermissionCameraIOS", dependencies: ["PermissionIOS", "PermissionCore", "CameraPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionCameraIOS"),
]
package.products.append(.library(name: "PermissionCameraIOS", targets: ["PermissionCameraIOS"]))

package.targets += [
    .target(name: "PhotoLibraryPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/PhotoLibraryPermission"),
    .target(name: "PermissionPhotoLibraryIOS", dependencies: ["PermissionIOS", "PermissionCore", "PhotoLibraryPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionPhotoLibraryIOS"),
]
package.products.append(.library(name: "PermissionPhotoLibraryIOS", targets: ["PermissionPhotoLibraryIOS"]))

package.targets += [
    .target(name: "MicrophonePermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/MicrophonePermission"),
    .target(name: "PermissionMicrophoneIOS", dependencies: ["PermissionIOS", "PermissionCore", "MicrophonePermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionMicrophoneIOS"),
]
package.products.append(.library(name: "PermissionMicrophoneIOS", targets: ["PermissionMicrophoneIOS"]))

package.targets += [
    .target(name: "ContactsPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/ContactsPermission"),
    .target(name: "PermissionContactsIOS", dependencies: ["PermissionIOS", "PermissionCore", "ContactsPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionContactsIOS"),
]
package.products.append(.library(name: "PermissionContactsIOS", targets: ["PermissionContactsIOS"]))

package.targets += [
    .target(name: "SpeechRecognizerPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/SpeechRecognizerPermission"),
    .target(name: "PermissionSpeechIOS", dependencies: ["PermissionIOS", "PermissionCore", "SpeechRecognizerPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionSpeechIOS"),
]
package.products.append(.library(name: "PermissionSpeechIOS", targets: ["PermissionSpeechIOS"]))

package.targets += [
    .target(name: "MotionPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/MotionPermission"),
    .target(name: "PermissionMotionIOS", dependencies: ["PermissionIOS", "PermissionCore", "MotionPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionMotionIOS"),
]
package.products.append(.library(name: "PermissionMotionIOS", targets: ["PermissionMotionIOS"]))

package.targets += [
    .target(name: "MediaLibraryPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/MediaLibraryPermission"),
    .target(name: "PermissionMediaLibraryIOS", dependencies: ["PermissionIOS", "PermissionCore", "MediaLibraryPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionMediaLibraryIOS"),
]
package.products.append(.library(name: "PermissionMediaLibraryIOS", targets: ["PermissionMediaLibraryIOS"]))

package.targets += [
    .target(name: "BluetoothPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/BluetoothPermission"),
    .target(name: "PermissionBluetoothIOS", dependencies: ["PermissionIOS", "PermissionCore", "BluetoothPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionBluetoothIOS"),
]
package.products.append(.library(name: "PermissionBluetoothIOS", targets: ["PermissionBluetoothIOS"]))

package.targets += [
    .target(name: "TrackingPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/TrackingPermission"),
    .target(name: "PermissionTrackingIOS", dependencies: ["PermissionIOS", "PermissionCore", "TrackingPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionTrackingIOS"),
]
package.products.append(.library(name: "PermissionTrackingIOS", targets: ["PermissionTrackingIOS"]))

package.targets += [
    .target(name: "SiriPermission", dependencies: ["PermissionsKit"],
            path: "apple/ThirdParty/PermissionsKit/Sources/SiriPermission"),
    .target(name: "PermissionSiriIOS", dependencies: ["PermissionIOS", "PermissionCore", "SiriPermission", "PermissionsKit"],
            path: "apple/Sources/iOS/PermissionSiriIOS"),
]
package.products.append(.library(name: "PermissionSiriIOS", targets: ["PermissionSiriIOS"]))

package.targets.append(.target(name: "PermissionNotificationIOS", dependencies: ["PermissionIOS", "PermissionCore"],
                              path: "apple/Sources/iOS/PermissionNotificationIOS"))
package.products.append(.library(name: "PermissionNotificationIOS", targets: ["PermissionNotificationIOS"]))

package.targets.append(.target(name: "PermissionCalendarIOS", dependencies: ["PermissionIOS", "PermissionCore"],
                              path: "apple/Sources/iOS/PermissionCalendarIOS"))
package.products.append(.library(name: "PermissionCalendarIOS", targets: ["PermissionCalendarIOS"]))

package.targets.append(.target(name: "PermissionRemindersIOS", dependencies: ["PermissionIOS", "PermissionCore"],
                              path: "apple/Sources/iOS/PermissionRemindersIOS"))
package.products.append(.library(name: "PermissionRemindersIOS", targets: ["PermissionRemindersIOS"]))

package.targets.append(.target(name: "PermissionHealthIOS", dependencies: ["PermissionIOS", "PermissionCore"],
                              path: "apple/Sources/iOS/PermissionHealthIOS"))
package.products.append(.library(name: "PermissionHealthIOS", targets: ["PermissionHealthIOS"]))

package.targets.append(.target(name: "PermissionFaceIDIOS", dependencies: ["PermissionIOS", "PermissionCore"],
                              path: "apple/Sources/iOS/PermissionFaceIDIOS"))
package.products.append(.library(name: "PermissionFaceIDIOS", targets: ["PermissionFaceIDIOS"]))

package.targets.append(.target(name: "PermissionLocationIOS", dependencies: ["PermissionIOS", "PermissionCore"],
                              path: "apple/Sources/iOS/PermissionLocationIOS"))
package.products.append(.library(name: "PermissionLocationIOS", targets: ["PermissionLocationIOS"]))

package.targets += [
    .target(name: "SystemSettingsKit", path: "apple/ThirdParty/PermissionFlow/Sources/SystemSettingsKit"),
    .target(name: "PermissionFlow", dependencies: ["SystemSettingsKit"],
            path: "apple/ThirdParty/PermissionFlow/Sources/PermissionFlow", resources: [.process("Resources")]),
]

package.targets.append(.target(name: "PermissionFlowBluetoothStatus", dependencies: ["PermissionFlow"],
                              path: "apple/ThirdParty/PermissionFlow/Sources/PermissionFlowBluetoothStatus"))

package.targets.append(.target(name: "PermissionFlowCameraStatus", dependencies: ["PermissionFlow"],
                              path: "apple/ThirdParty/PermissionFlow/Sources/PermissionFlowCameraStatus"))

package.targets.append(.target(name: "PermissionFlowInputMonitoringStatus", dependencies: ["PermissionFlow"],
                              path: "apple/ThirdParty/PermissionFlow/Sources/PermissionFlowInputMonitoringStatus"))

package.targets.append(.target(name: "PermissionFlowMediaStatus", dependencies: ["PermissionFlow"],
                              path: "apple/ThirdParty/PermissionFlow/Sources/PermissionFlowMediaStatus"))

package.targets.append(.target(name: "PermissionFlowScreenRecordingStatus", dependencies: ["PermissionFlow"],
                              path: "apple/ThirdParty/PermissionFlow/Sources/PermissionFlowScreenRecordingStatus"))

package.targets += [
    .target(name: "PermissionFlowExtendedStatus",
            dependencies: ["PermissionFlowBluetoothStatus", "PermissionFlowCameraStatus", "PermissionFlowInputMonitoringStatus",
                           "PermissionFlowMediaStatus", "PermissionFlowScreenRecordingStatus"],
            path: "apple/ThirdParty/PermissionFlow/Sources/PermissionFlowExtendedStatus"),
    .target(name: "PermissionMac", dependencies: ["PermissionCore", "PermissionFlow", "PermissionFlowExtendedStatus", "SystemSettingsKit"],
            path: "apple/Sources/macOS/PermissionMac"),
    .testTarget(name: "PermissionMacTests", dependencies: ["PermissionMac", "PermissionFlow"], path: "apple/Tests/PermissionMacTests"),
]

// 权限 UI 单独选择，纯状态/请求模块不依赖设计系统。
package.products.append(.library(name: "PermissionUI", targets: ["PermissionUI"]))
package.targets += [
    .target(name: "PermissionUI", dependencies: [
        .target(name: "DesignKitIOS", condition: .when(platforms: [.iOS])),
        .target(name: "DesignKitMac", condition: .when(platforms: [.macOS])),
    ], path: "apple/Sources/Shared/PermissionUI"),
    .testTarget(name: "PermissionIOSTests", dependencies: ["PermissionCore", "PermissionIOS",
        "PermissionCameraIOS",
        "PermissionPhotoLibraryIOS",
        "PermissionMicrophoneIOS",
        "PermissionContactsIOS",
        "PermissionSpeechIOS",
        "PermissionMotionIOS",
        "PermissionMediaLibraryIOS",
        "PermissionBluetoothIOS",
        "PermissionTrackingIOS",
        "PermissionSiriIOS",
        "PermissionNotificationIOS",
        "PermissionCalendarIOS",
        "PermissionRemindersIOS",
        "PermissionHealthIOS",
        "PermissionFaceIDIOS",
        "PermissionLocationIOS"
    ], path: "apple/Tests/PermissionIOSTests"),
]
