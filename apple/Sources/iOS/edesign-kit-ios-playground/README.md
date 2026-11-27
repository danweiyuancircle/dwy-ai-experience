# DesignKitIOSPlayground

`DesignKitIOS` 的可选组件目录，仅用于开发和验收，不要在正式 App 链接。最低 iOS 18。

结构与 `DesignKitMacPlayground` 相近：目录（搜索 + 分类）、组件详情（符号、模块、最低系统、实时预览、示例状态切换与重置、支持的能力、用法与约束、可复制 Swift 示例）、主题与设计令牌页。`NavigationSplitView` 在 iPhone 折叠为单栏，iPad 横屏为双栏。

## 使用

```swift
import DesignKitIOSPlayground

WindowGroup { IOSPlayground() }
```

`IOSPlayground` 自带 `NavigationSplitView`，不要嵌入另一个 `NavigationStack`。预览设置（外观、大字号、备用品牌色、浮动材质）只作用于预览子树，不写 `ThemeManager` 或用户偏好。可运行入口见 `apple/Examples/IOSControls/README.md` 的 `IOSPlayground` scheme。

## 与 macOS 版的关系

macOS 版全部位于 `#if os(macOS)` 并绑定 AppKit，无法复用；本目录独立实现。目录、文档、搜索、预览选项为平台无关代码（`IOSPlaygroundComponent.swift`、`IOSPlaygroundDocumentation.swift`、`IOSPlaygroundCatalog.swift`），macOS 上 `swift test --filter DesignKitIOSPlaygroundTests` 可执行；视图与 fixture 位于 `#if os(iOS)`。

## 新增组件

1. 在 `IOSPlaygroundComponent` 增加 case、分类与场景，在 `IOSPlaygroundDocumentation.swift` 补中英文说明。
2. 在 `Fixtures/` 新增 `<Name>Example.swift`，并在 `IOSPlaygroundFixture.swift` 的 switch 映射（漏写会编译失败）。
3. 运行 `python3 -I apple/Sources/iOS/edesign-kit-ios-playground/Scripts/sync-examples.py` 生成 `Resources/Examples/*.swift.txt`；`--check` 只检查不写入。
4. 目录覆盖测试会对比公开 iOS E* 视图与目录符号，缺项直接失败。
