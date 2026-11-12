# DesignKitMac 原型接入与状态

本轮已转为 iOS / macOS 分别设计、抽取的方案。总览见 `ios/Docs/DESIGN_SYSTEMS.md`，Mac 规范见 `ios/Docs/MACOS_DESIGN_SYSTEM.md`。0.8.0-beta.3 包含下述中性玻璃着色修正；锁定旧标签的应用须显式升级后才会生效。

## 按钮着色

浮动区域的次要 EButton / EIconAction 使用原生中性玻璃，清除显式品牌 tint；帮助、关闭不与主要操作争夺视觉强调。主要操作仍使用品牌色的 glassProminent，危险角色仍保留 danger 语义色。自定义图标前景由调用方负责，在实际主题与材质下核对对比度；不能将灰色图标配饱和品牌色背景。

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

## 简短提示与持久通知

`EToast` 使用图标加文字的紧凑圆角提示，短文案按内容自然收窄，长文案在宿主可用宽度内换行；不显示关闭按钮，不复用 `ENotice` 的全宽通知卡。普通情况下两秒后自动清除消息；消息替换、取消与宿主销毁不清除后续消息，悬停、键盘/辅助焦点和 VoiceOver 阅读时保留既有暂停策略。

既有 `dismissTitle` 仍为辅助功能清除动作命名，不增加配置参数。提示获得键盘焦点后可用 Esc、Return 或空格清除；无需点击可见按钮。重要错误及需要用户操作的信息继续使用持久 `ENotice`，不改为短暂提示。

`MacControlHostTests.testToastIsCompactForShortFeedbackAndWrapsLongMessages` 检查短提示宽度、相对旧通知卡的高度及长文换行；布局测试不能代替前台键盘、VoiceOver 和真实显示效果验收。
