# macOS 共享页面组合

页面使用 `DesignKitMac` 的通用 UI 入口。基础库内部可使用系统原生控件，系统版本适配、通用字号、间距、圆角与交互外观集中在基础库完成。

| 入口 | 用途与边界 |
| --- | --- |
| `EPageHeader` | 设置和工具页的标题、副标题，读取主题字体并支持长文案 |
| `ESettingsPage` | 页内滚动、留白和可读宽度；不保存导航或业务状态 |
| `EItemRow` | 多操作行的悬停/选中背景与密度；内容槽不合并内部焦点 |
| `ESidebarItem` | 侧栏项字号与密度；选中和键盘导航仍由原生 List 管理 |
| `EManagementListStyle` | 管理列表的紧凑控件密度与原生列表样式 |
| `EReorderableList` | 拖拽和辅助功能等效排序；宿主提供稳定 ID 和持久化回调 |
| `EApplicationIcon` | 从本机 Launch Services 或显式路径读取原色 Logo，缺失时使用指定 SF Symbol |
| `EProgressPanelContent` | 任务进度、说明和动作区布局；取消不会伪装为任务已经结束 |
| `EContentState` | 加载/空态/失败组合；`systemImage` 只指定展示图标，状态与动作由业务提供 |
| `EText`、`.eText(_:tone:)` | 文本语义角色（`body`、`secondary`、`caption`、`title`、`sectionTitle`、`pageTitle`、`monospaced`）。字体读 `ETypography`，颜色读 `ESemanticColors`，`tone` 复用 `EStatusTone` 表达成功/警告/失败色，状态仍须配有文字。修饰符可用于 `Text`、`Label` 等任意视图，业务页面不再裸写 `.font(.caption)`、`.foregroundStyle(.secondary)` |

新页面通过 `@Environment(\.eControlTheme)` 读取根主题。标准页面令牌 `EPalette`、`ETypeScale`、`ESpace`、`ERadius` 为已有静态消费方提供标准主题映射；它们不读取某个 View 子树的自定义环境。需要品牌或密度覆盖的组件应读取环境，不在项目复制静态数值表。

`EControlTheme.standard` 使用 ADBox macOS 的冷静蓝和灰阶层次。`colors.background` 用于内容页，`surface` 用于卡片与输入，`elevatedSurface` 用于 Toast 等浮层。配色跟随明暗外观，在增加对比度时提升强调色、辅助文字、状态文字和分隔线的对比度。原生窗口材质、选中态与键盘焦点继续由系统控件处理。

标准正文为 13 pt，次要文字为 11 pt。应用可从 `.standard` 出发，使用 `ETypography(bodySize:)` 同步调整 SwiftUI 内容字体与 AppKit 编辑器字号，也可修改间距、圆角或个别颜色。改品牌色时应同时设置 `colors.accent` 和 `colors.onAccent`，验证浅色、深色与增加对比度下的组合。悬停底色默认随强调色变化。每个独立窗口、AppKit 宿主或需要覆盖的子树通过 `.eControlTheme(theme)` 注入。

```swift
import SwiftUI
import DesignKitMac

struct SharedSettingsExample: View {
    @State private var enabled = true

    var body: some View {
        ESettingsPage(maxContentWidth: 720) {
            EPageHeader(title: Text("Actions"), subtitle: Text("Choose the actions you use."))
            EItemRow {
                Label("Enabled", systemImage: "checkmark.circle")
                Spacer()
                ESwitch("Enabled", isOn: $enabled)
            }
        }
        .eControlTheme(.standard)
    }
}
```

编辑弹层使用现有 `EForm` 的 content/actions 槽，不自行重复滚动与固定动作区。文案使用 `Text` 或 `LocalizedStringResource` 显式传入，基础库不引用应用本地化 key、资源、单例或业务模型。

组件回归见 `apple/Tests/DesignKitMacTests/MacRecoveredCompositionTests.swift`。本轮改动仍需随共享库版本发布后更新消费方锁文件；本地 workspace 联调不是远程发布证明。

可操作的组合示例为 `apple/Sources/macOS/edesign-kit-mac-playground/ERecoveredCompositionsPreview.swift`，公开入口 `ERecoveredCompositionsPreview()`。演示支持中英文、局部表单状态及排序，不写业务偏好。根目录的 Playground catalog 统一负责展示入口。
