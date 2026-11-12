# DesignKitMacPlayground

可选的 macOS 26+ 组件目录产品，只依赖 `DesignKitMac` 和系统框架。组件产品不反向依赖它。正式应用可通过不链接此产品排除全部展示资源；仅隐藏入口不能证明 Release 已排除。

```swift
import SwiftUI
import DesignKitMacPlayground

struct DeveloperComponents: View {
    var body: some View {
        EPlayground(projectTitle: Text("Project compositions")) {
            Text("Host-owned examples")
        }
    }
}
```

没有项目组合时用 `EPlayground()`。宿主拥有独立窗口、激活与复用策略，项目内容不再嵌整页 `ScrollView`。目录自带详情滚动区域。项目组合仍须自行提供用途、说明和复制内容，基础库不反向依赖项目业务模块。

目录由 `EPlaygroundComponent` 维护稳定 ID 与公开符号映射，`EPlaygroundFixture` 穷举映射到直接编译的公开 API 示例。每项双语说明位于 `Resources/Documentation`；真实示例位于 `Fixtures`，`Resources/Examples` 只存其生成镜像。代码默认使用应用 bundle，目录显式注入自身 bundle；用户原文通过 `Text(verbatim:)` 展示。Markdown 与复制内容读取同一所属 bundle 文件。

修改示例后运行：

```sh
python3 ios/Sources/macOS/DesignKitMacPlayground/Scripts/sync-examples.py
python3 ios/Sources/macOS/DesignKitMacPlayground/Scripts/sync-examples.py --check
```

脚本只使用 Python 标准库，不在消费方构建或应用启动时执行。它同步可复制源码并生成 `Resources/Index.md`。测试还检查所有公开 Mac 可视 E 组件均有目录条目、双语说明与源码完全一致。

默认继承宿主主题、字号、locale 和 placement。窗口顶部「预览设置」弹出层统一调整这些值，切换组件时保留，关闭当前 Playground 后不保存；不再为每个组件显示覆盖开关或环境长表。实际系统与辅助功能信息放在设置内默认折叠区域。

详情先展示真实预览，状态与重置在同一行，随后只有用途摘要和复制按钮。完整说明与 Swift 代码默认折叠，展开、阅读与复制仍使用同源资源。父布局不设置会向后代传播的 AX identifier，保留示例各操作/输入/结果的稳定角色标识。

预览设置只作用子树；独立 `NSHostingView` 的 `appearance` 让原生 AppKit 字段也采用局部明暗。不会调用 `ThemeManager`、`LocalizationManager`、`NSApp.appearance` 或写入用户偏好。大字号同步语义正文和 `nativeBodySize`，不缩小触点。实际辅助功能值来自系统环境，不提供伪造“已通过”开关。

每个条目和示例使用 `playground.<component-id>.<role>` 标识。切条目和重置会重建局部 fixture，原生组件负责取消它拥有的计时任务。复制只写系统剪贴板，失败会明确显示；不运行粘贴的 Swift、不发网络、不创建真实设备或交易。

源码与资源检查不能代替 macOS 26 前台键盘、IME、VoiceOver、窗口边缘、原生材质及动态过程验收。内置说明保留这些未验收边界；宿主项目应单独记录实际证据。
