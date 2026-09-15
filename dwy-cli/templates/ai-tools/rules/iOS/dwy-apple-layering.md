---
description: iOS / macOS 四层分包与依赖方向（双壳 Assembly + Features / BizFoundation / Foundation）；根 Package.swift 锁定第三方版本
paths:
  - "**/*.swift"
  - "**/Package.swift"
  - "**/project.yml"
---

# Apple 四层架构与依赖

适用于 iOS 17+ / macOS 14+ 的 SwiftUI 双端或单端应用。风格 / 安全区 / 国际化见 `dwy-swift-core`。本文件只管**层、引用边、版本写在哪**。

单壳（只有 iPhone 或只有 Mac）**不建** PlatformFoundation。双壳且某端领域字节级不同时才加 `DesktopKit`。

系统框架就叫 `Foundation`。SPM **target 禁止叫 `Foundation`**，层目录可以用这个名字。

---

## 一、层名（冻结）

正式层名只有下表四个。目录 / target 可以叫 `AppPhone`、`BizFoundation`，文档可写「本仓 LogKit = Foundation 层的日志」。**禁止**把 `Domain` / `infra` / `core` 当层名。

| 层 | 判定（只用这一条） | 禁止 |
|---|---|---|
| **Foundation** | 换一个完全不同的产品仍原样拿走 | 出现本业务名词 |
| **BizFoundation** | 本产品才有，但跨多个 Feature 都要用 | 页面、导航、某一端壳状态 |
| **Features** | 可整包删/裁剪的业务域 | 被其他 Feature 直接引用 |
| **Assembly** | 生命周期、DI、路由挂载、把实现插进 Protocol | 业务规则、业务计算 |

可选第五盒，**仅多壳**时出现：

| **PlatformFoundation** | 同一业务多个壳，且某端领域字节级不同 | 被其他壳 import；塞回 BizFoundation |

升层：第二个 Feature 或第二个产品**真在用**，才升到 BizFoundation / Foundation。禁止「可能复用」提前抽。禁止为了共用而抽 `AppShared` 把壳状态（Store / Session）塞进 BizFoundation。

业务内聚：一个业务域 = 壳内 `Features/<Name>/`。禁止按 `Views/` `ViewModels/` 横切。目录不等于层：Features 若与壳同一 target，仍遵守互不 import 的源码边界。

---

## 二、依赖边（强制）

```
AppPhone  ──► Features/* ──► BizFoundation ──► Foundation 层目录（LogKit / DesignKit）
AppDesktop ─┬► Features/*
            ├► DesktopKit ──► BizFoundation ──► Foundation 层目录
            └► BizFoundation
```

| 谁 | 允许 | 禁止 |
|---|---|---|
| `AppPhone` | `BizFoundation`、Foundation 层 target、本壳 Features | `DesktopKit`、另一壳源码 |
| `AppDesktop` | `BizFoundation`、`DesktopKit`、Foundation 层 target、本壳 Features | `AppPhone/**/*.swift` |
| 本壳 `Features/Orders` | `BizFoundation`、本壳 App 装配类型 | `Features/Inventory`、另一壳 |
| `BizFoundation` | Foundation 层 target（日志 / 工具，**禁止** DesignKit） | 任一壳、DesktopKit |
| Foundation 层 target | 系统框架、风格无关工具 | 业务类型、壳 |
| `DesktopKit` | `BizFoundation`、Foundation 层 target | `AppPhone`、DesignKit（几何数字用测试锁同值，或升到壳） |

**Feature 互引为零。** 跨域走 BizFoundation Protocol，或壳编排。

`AppPhone` 禁止 `import DesktopKit`。不要抽 `AppShared`。

```swift
// Package.swift：BizFoundation 不依赖壳
.target(
    name: "BizFoundation",
    dependencies: ["LogKit"]  // Foundation 层 target，不是系统 Foundation
)
```

```swift
// 禁止
import DesktopKit    // 写在 AppPhone
import AppPhone      // 写在 BizFoundation
```

---

## 三、分包树

打开工程必须能数出：两个壳（或一个壳）+ `Features` + `BizFoundation` + Foundation 层目录。

```
AppPhone/                         # Assembly 壳
  App/                            # 装配：路由、DI、生命周期
  Features/
    Orders/
    Inventory/
AppDesktop/                       # 另一个 Assembly 壳（单壳则省略）
  App/
  Features/
    Orders/
    Inventory/
Sources/
  BizFoundation/                  # target: BizFoundation
  Foundation/                     # 层目录；target 用 LogKit / DesignKit
  DesktopKit/                     # PlatformFoundation，仅 AppDesktop 依赖
Package.swift                     # from: 只在这
project.yml                       # 壳引用这一份 package，不重复 from:
```

---

## 四、Monorepo 版本（强制）

第三方版本号**只**出现在根 `Package.swift` 的 `.package(..., from:)`。target 只写 product / 本地 target 名。`project.yml` 引用这一份 package，不重复版本。选哪个版本走 `dwy-dependency-freshness`。

```swift
dependencies: [
    .package(url: "https://github.com/apple/swift-log.git", from: "1.5.0"),
]
targets: [
    .target(name: "LogKit", dependencies: [
        .product(name: "Logging", package: "swift-log"),
    ]),
    .target(name: "BizFoundation", dependencies: ["LogKit"]),
]
```

禁止第二个 `Package.swift` 再写同一依赖的 `from:`。禁止 target 注释里另写版本。

---

## 五、检查清单

| 检查项 | 严重 |
|---|---|
| `AppPhone` import `DesktopKit` 或编译另一壳 `.swift` | 高 |
| `BizFoundation` import 壳类型 / DesignKit | 高 |
| 壳内 Features 互相 import | 高 |
| SPM target 名为 `Foundation`（与系统框架撞名） | 高 |
| 第二个 Package.swift / project.yml 重复 `from:` | 高 |
| 抽 `AppShared` 把 Store / Session 塞进 BizFoundation | 高 |
| `Domain` / `infra` / `core` 当层名 | 中 |
