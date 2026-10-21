// swift-tools-version: 6.0
import PackageDescription

/// 苹果应用骨架：Shared 横切 + iOS / macOS 平台 UI 基建。
///
/// 部署底线（模板与库一致）：
/// - iOS 17.0+
/// - macOS 14.0+
///
/// SwiftPM 远程依赖要求保留仓库根入口；所有实现、模板和测试统一位于 ios/。
/// App 壳不在此包；用 `ios/scripts/new-app.sh` 从 Templates 生成。
let package = Package(
    name: "AppleAppKit",
    defaultLocalization: "en",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
    ],
    products: [
        .library(name: "CoreKit", targets: ["CoreKit"]),
        .library(name: "LogKit", targets: ["LogKit"]),
        .library(name: "L10nKit", targets: ["L10nKit"]),
        .library(name: "CacheKit", targets: ["CacheKit"]),
        .library(name: "DesignCore", targets: ["DesignCore"]),
        .library(name: "DesignKitIOS", targets: ["DesignKitIOS"]),
        .library(name: "DesignKitMac", targets: ["DesignKitMac"]),
        .library(name: "PurchaseCore", targets: ["PurchaseCore"]),
        .library(name: "AuthCore", targets: ["AuthCore"]),
        .library(name: "AuthUI", targets: ["AuthUI"]),
        .library(name: "AuthGoogleIOS", targets: ["AuthGoogleIOS"]),
    ],
    dependencies: [
        .package(url: "https://github.com/sushichop/Puppy.git", from: "0.9.0"),
        .package(url: "https://github.com/google/GoogleSignIn-iOS.git", exact: "9.1.0"),
        // 8.1.5 在 2026-10-14 发布，选型时未满 7 天；限制传递依赖使用已稳定版本。
        .package(url: "https://github.com/google/GoogleUtilities.git", exact: "8.1.4"),
    ],
    targets: [
        // MARK: Shared（业务无关、双平台）

        .target(
            name: "CoreKit",
            path: "ios/Sources/Shared/CoreKit"
        ),
        .target(
            name: "L10nKit",
            path: "ios/Sources/Shared/L10nKit"
        ),
        .target(
            name: "LogKit",
            dependencies: [
                .product(name: "Puppy", package: "Puppy"),
            ],
            path: "ios/Sources/Shared/LogKit"
        ),
        .target(
            name: "CacheKit",
            path: "ios/Sources/Shared/CacheKit"
        ),
        .target(
            name: "AuthCore",
            dependencies: ["CoreKit", "L10nKit"],
            path: "ios/Sources/Shared/AuthCore"
        ),
        .target(
            name: "AuthUI",
            dependencies: ["AuthCore", "L10nKit"],
            path: "ios/Sources/iOS/AuthUI",
            resources: [.process("Resources")]
        ),
        // ThemeMode / Motion 等纯 SwiftUI 共享令牌；不含 UIKit/AppKit。
        .target(
            name: "DesignCore",
            dependencies: ["L10nKit"],
            path: "ios/Sources/Shared/DesignCore"
        ),

        // MARK: 平台层（两套代码，各自演进）

        .target(
            name: "DesignKitIOS",
            dependencies: ["DesignCore", "L10nKit"],
            path: "ios/Sources/iOS/DesignKit"
        ),
        .target(
            name: "DesignKitMac",
            dependencies: ["DesignCore", "L10nKit"],
            path: "ios/Sources/macOS/DesignKit"
        ),
        // Google 的呈现与回调局限于 iOS；纯认证核心不依赖 SDK。
        .target(
            name: "AuthGoogleIOS",
            dependencies: [
                "AuthCore",
                .product(name: "GoogleSignIn", package: "GoogleSignIn-iOS", condition: .when(platforms: [.iOS])),
            ],
            path: "ios/Sources/iOS/AuthGoogleIOS"
        ),
        // 终身买断 + DEBUG 解锁。试用 / 限额留在 App 的 BizFoundation。
        .target(
            name: "PurchaseCore",
            dependencies: ["L10nKit"],
            path: "ios/Sources/Shared/PurchaseCore"
        ),

        // MARK: Tests

        .testTarget(
            name: "AuthUITests",
            dependencies: ["AuthUI", "AuthCore"],
            path: "ios/Tests/AuthUITests",
            exclude: ["TEST_CASES.md"]
        ),
        .testTarget(
            name: "AuthCoreTests",
            dependencies: ["AuthCore"],
            path: "ios/Tests/AuthCoreTests",
            exclude: ["TEST_CASES.md"]
        ),

        .testTarget(
            name: "CoreKitTests",
            dependencies: ["CoreKit"],
            path: "ios/Tests/CoreKitTests"
        ),
        .testTarget(
            name: "LogKitTests",
            dependencies: ["LogKit"],
            path: "ios/Tests/LogKitTests"
        ),
        .testTarget(
            name: "L10nKitTests",
            dependencies: ["L10nKit"],
            path: "ios/Tests/L10nKitTests"
        ),
        .testTarget(
            name: "CacheKitTests",
            dependencies: ["CacheKit"],
            path: "ios/Tests/CacheKitTests"
        ),
        .testTarget(
            name: "PurchaseCoreTests",
            dependencies: ["PurchaseCore"],
            path: "ios/Tests/PurchaseCoreTests"
        ),
    ]
)
