// swift-tools-version: 6.0
import PackageDescription

/// =============================================================================
/// 四层目录架构（与 TVRemote 一致）
///
///   App/              ① APP 层（源码在 App target，不在本 Package）
///   Features/         ② Features 层（编入 App target）
///   BizFoundation/    ③ 业务基础层 ← 本 Package 定义
///   Foundation/       ④ 业务无关基础层（层锚点；实现由统一私有包版本 提供）
///
/// 部署：iOS 17.0+（含 macOS 14 以便 host 上 swift test）
/// 规约：Docs/ARCHITECTURE.md
/// =============================================================================
let package = Package(
    name: "BizFoundation",
    platforms: [
        .iOS(.v17),
        .macOS(.v14),
    ],
    products: [
        /// ③ 业务基础层
        .library(name: "BizFoundation", targets: ["BizFoundation"]),
    ],
    dependencies: [
        .package(url: "__PACKAGE_URL__", from: "__PACKAGE_VERSION__"),
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
            path: "BizFoundation"
        ),
        .testTarget(
            name: "BizFoundationTests",
            dependencies: ["BizFoundation"],
            path: "Tests/BizFoundationTests"
        ),
    ]
)
