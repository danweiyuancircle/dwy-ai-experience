# DesignKitMac 原型接入与状态

本轮已转为 iOS / macOS 分别设计、抽取的方案。总览见 `ios/Docs/DESIGN_SYSTEMS.md`，Mac 规范见 `ios/Docs/MACOS_DESIGN_SYSTEM.md`。当前原型没有发布，不能通过旧标签消费。

## 当前接口示例

以下代码可放在已链接当前源码 DesignKitMac 的 Mac target 中；部署最低 macOS 26。独立完整应用位于 `ios/Examples/MacControls/Sources/MacControlsGallery/MacControlsGallery.swift`。

```swift
import SwiftUI
import DesignKitMac

struct ControlsExample: View {
    @State private var name = ""
    @State private var mode = "standard"
    @State private var enabled = true

    var body: some View {
        VStack(alignment: .leading, spacing: 16) {
            EField("名称", hint: "输入由应用保存") {
                ETextField("名称", text: $name)
            }
            EPicker("模式", selection: $mode) {
                Text("标准").tag("standard")
                Text("紧凑").tag("compact")
            }
            ESwitch("启用", isOn: $enabled)
            EActionGroup {
                EButton("保存", emphasis: .primary) { print(name) }
                EIconAction("刷新", systemImage: "arrow.clockwise") {}
                EMenu("更多") {
                    Button("重置") { name = "" }
                }
            }
            .eControlPlacement(.floating)
        }
        .padding()
        .eControlTheme(EControlTheme(accent: .blue))
    }
}
```

根仓库执行：

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcrun swift test --filter DesignKitMacTests
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer xcrun swift run MacControlsGallery
python3 -m unittest ios/Tests/test_templates.py
```

## 接入边界

- 正式消费通过已发布的固定版本/提交；不把本机 checkout 路径写入业务工程或提交锁文件。
- 应用继续负责业务动作、验证、持久化、Pro 门控、资源和本地化。
- 基础材质变更集中修改组件；消费项目更新版本后仍验证实际宿主布局和业务路径。
- 当前展示只验证部分交互；完整键盘、VoiceOver、窗口边缘下拉和 macOS 26 实机验收未完成，参见 Mac 规范的发布门槛。
