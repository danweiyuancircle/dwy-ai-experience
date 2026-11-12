import AppKit
import SwiftUI
import DesignKitMac

/// 独立消费公开组件，不能引用 ADBox 或使用 @testable 接口。
@main
struct MacControlsGallery: App {
    var body: some Scene {
        WindowGroup("Mac Controls") {
            GalleryView()
                .eControlTheme(EControlTheme())
                .frame(minWidth: 360, minHeight: 540)
                .onAppear {
                    NSApp.setActivationPolicy(.regular)
                    NSApp.activate()
                }
        }
        .defaultSize(width: 820, height: 850)
    }
}

private struct GalleryView: View {
    @State private var text = ""
    @State private var password = ""
    @State private var search = ""
    @State private var suggestion = ""
    @State private var selection = "standard"
    @State private var suggestions = ["Android", "ADBox", "输入法", "应用管理", "文件管理", "Android"]
    @State private var optionalChoice: String? = nil
    @State private var enabled = true
    @State private var dark = false
    @State private var large = false
    @State private var toast: EToastMessage?
    @State private var useBrand = false
    @State private var result = "尚未操作"

    private var brandTheme: EControlTheme {
        var theme = EControlTheme()
        if useBrand {
            theme.colors.accent = .purple
            theme.colors.onAccent = .white
        }
        return theme
    }

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 24) {
                Text("DesignKitMac · macOS 26").font(.title2)
                Text("相同公开组件用于内容区、浮动操作和系统工具栏。")
                    .foregroundStyle(.secondary)

                GroupBox("内容区按钮") {
                    EActionGroup {
                        EButton("主要操作", emphasis: .primary) { result = "主要操作" }
                        EButton("次要操作") { result = "次要操作" }
                        EButton("危险操作", role: .destructive) { result = "危险操作（示例不删除数据）" }
                        EIconAction("截图", systemImage: "camera") { result = "截图" }
                        EButton("禁用", action: {}).disabled(true)
                    }
                    .padding(8)
                }

                GroupBox("浮动操作 · Liquid Glass") {
                    EActionGroup {
                        EButton("保存", emphasis: .primary) { result = "保存" }
                        EButton("取消") { result = "取消" }
                        EIconAction("自定义标签", action: { result = "自定义标签" }) {
                            Image(systemName: "square.stack.3d.up.fill").foregroundStyle(.purple)
                        }
                        EMenu("更多") {
                            Button("复制") { result = "复制菜单动作" }
                            Divider()
                            Toggle("启用", isOn: $enabled)
                            Button("删除", role: .destructive) { result = "删除菜单动作（无副作用）" }
                        }
                        EButton("处理中", isBusy: true) {}
                    }
                    .eControlPlacement(.floating)
                    .padding(12)
                }

                HStack(alignment: .top, spacing: 20) {
                    EField("语言选择", hint: "选择后立即更新下方状态") {
                        EPicker("语言", selection: $selection) {
                            Text("标准 / Standard").tag("standard")
                            Text("较长的选项 / A longer option").tag("long")
                        }
                    }
                    EPicker("模式", selection: $selection, presentation: .segmented) {
                        Text("标准").tag("standard")
                        Text("较长").tag("long")
                    }
                }

                EField("名称", hint: "支持中文输入法、复制、粘贴及原生焦点") {
                    ETextField("名称", text: $text)
                        .onSubmit { result = "提交：\(text)" }
                }
                EField("密码", error: password.isEmpty ? "示例校验：密码不能为空" : nil) {
                    ESecureField("密码", text: $password)
                }
                ESearchField("搜索", text: $search, clearTitle: "清空搜索")
                EField("输入或选择建议", hint: "上下键选择，Enter 提交，Esc 收起；下面的开关可用于验证失焦") {
                    EComboBox("建议", text: $suggestion, suggestions: suggestions + (1...15).map { "历史建议 \($0)" }, onEditingEnded: {
                        result = "编辑结束（没有提交）：\($0)"
                    }) { result = "已提交建议：\($0)" }
                }
                EActionGroup {
                    EButton("反转候选") { suggestions.reverse() }
                    EButton("清空候选") { suggestions = [] }
                }
                EPicker("可选选择", selection: $optionalChoice) {
                    Text("未选择").tag(nil as String?)
                    Text("第一项").tag("first" as String?)
                    Text("禁用项").tag("disabled" as String?).disabled(true)
                }
                EForm {
                    EField("表单名称", hint: "正文滚动，底部操作保持可达") {
                        ETextField("表单名称", text: $text)
                    }
                    ETextField("不可编辑", text: .constant("可读原文")).disabled(true)
                } actions: {
                    EActionGroup {
                        EButton("取消") { result = "表单取消" }
                        EButton("保存", emphasis: .primary) { result = "表单保存：\(text)" }
                    }
                }
                .frame(height: 160)
                ECard {
                    VStack(spacing: 12) {
                        ESettingsRow("后台任务", detail: "设置行会在窄窗口改为纵向布局") {
                            ESwitch("启用后台任务", isOn: $enabled).labelsHidden()
                        }
                        Divider()
                        ELabelValue("设备原文", value: Text(verbatim: text))
                        ECheckbox("保存本次选择（仅示例绑定）", isOn: $enabled)
                        EStatusBadge("连接正常", tone: .success)
                        EStatusBadge("需要检查", tone: .warning)
                        EStatusBadge("连接失败", tone: .failure)
                    }
                }
                EContentState(.empty, title: "还没有内容", detail: "此处演示业务明确提供的空态") {
                    EButton("添加内容") { result = "空态添加动作" }
                }
                EContentState(.failure, title: "未能加载", detail: "错误保留到业务主动更新") {
                    EButton("重试") { result = "用户请求重试" }
                }
                EContentState(.loading, title: "正在加载")
                ETaskProgress("正在传输", fraction: EProgressFraction(0.4)) {
                    EButton("取消") { result = "已请求取消，仍等待业务回写" }
                }
                ETaskProgress("正在准备")
                ENotice("需要检查输入后重试", tone: .failure) {
                    EButton("查看详情") { result = "通知动作" }
                }
                EButton("显示成功提示") { toast = EToastMessage("操作完成") }
                EToast(message: $toast, dismissTitle: "关闭提示")
                ESwitch("品牌覆盖", isOn: $useBrand)
                ESwitch("启用功能", isOn: $enabled)
                ESwitch("深色模式", isOn: $dark)
                ESwitch("大字号", isOn: $large)
                Text("选择：\(selection)；开关：\(enabled ? "开" : "关")；搜索：\(search)")
                    .accessibilityIdentifier("gallery.bindings")
                Text("操作结果：\(result)")
                    .accessibilityIdentifier("gallery.result")
            }
            .font(.system(size: large ? 20 : 14))
            .padding(24)
        }
        .eControlTheme(brandTheme)
        .preferredColorScheme(dark ? .dark : .light)
        .toolbar {
            ToolbarItem {
                EIconAction("工具栏刷新", systemImage: "arrow.clockwise") { result = "工具栏刷新" }
                    .eControlPlacement(.toolbar)
            }
        }
    }
}
