// swift-tools-version: 6.0
import PackageDescription

/// =============================================================================
/// 四层中的 ③ 本产品业务基础包；两端共享，不包含 UI 和应用生命周期。
/// 平台 App/Features/BusinessUI 在各自 App target；④ 通过 AppleAppKit 版本依赖消费。
///
/// 部署：iOS 18.0+（含 macOS 26 以便 host 上 swift test）
/// 规约：Docs/ARCHITECTURE.md
/// =============================================================================
let package = Package(
    name: "__APP_NAME__Core",
    platforms: [
        .iOS(.v18),
        .macOS("26.0"),
    ],
    products: [
        /// ③ 业务基础层
        .library(name: "BizFoundation", targets: ["BizFoundation"]),
    ],
    dependencies: [
        .package(url: "__PACKAGE_URL__", exact: "__PACKAGE_VERSION__"),
    ],
    targets: [
        .target(
            name: "BizFoundation",
            dependencies: [
                .product(name: "CoreKit", package: "__PACKAGE_ID__"),
                .product(name: "L10nKit", package: "__PACKAGE_ID__"),
                .product(name: "LogKit", package: "__PACKAGE_ID__"),
                .product(name: "CacheKit", package: "__PACKAGE_ID__"),
            ],
            path: "Sources/BizFoundation",
            exclude: ["README.md"]
        ),
        .testTarget(
            name: "BizFoundationTests",
            dependencies: ["BizFoundation"],
            path: "Tests/BizFoundationTests"
        ),
    ]
)
