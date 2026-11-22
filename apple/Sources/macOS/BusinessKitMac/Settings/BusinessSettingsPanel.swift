#if os(macOS)
import DesignKitMac
import SwiftUI

/// 应用提供稳定且唯一的标识。分类内容仅在选中时构建。
@MainActor
public struct BusinessSettingsSection: Identifiable {
    public nonisolated let id: String
    public let title: Text
    public let systemImage: String
    fileprivate let content: () -> AnyView

    /// `systemImage` 使用 SF Symbols 名称，`content` 可包含任何业务视图。
    public init<Content: View>(
        id: String,
        title: Text,
        systemImage: String,
        @ViewBuilder content: @escaping () -> Content
    ) {
        self.id = id
        self.title = title
        self.systemImage = systemImage
        self.content = { AnyView(content()) }
    }
}

/// 原生侧栏切换与独立滚动的设置面板。作为 Settings 窗口或原生 sheet 的内容使用。
public struct BusinessSettingsPanel: View {
    @Environment(\.eControlTheme) private var theme
    @State private var selection: String?
    private let title: Text
    private let sections: [BusinessSettingsSection]
    private let onClose: (() -> Void)?

    /// `onClose` 用于有显式关闭按钮的 sheet。Settings 窗口使用系统标题栏。
    public init(
        title: Text? = nil,
        sections: [BusinessSettingsSection],
        initialSectionID: String? = nil,
        onClose: (() -> Void)? = nil
    ) {
        self.title = title ?? Text("Settings", tableName: "Settings", bundle: .module)
        self.sections = sections
        self.onClose = onClose
        _selection = State(initialValue: initialSectionID)
    }

    public var body: some View {
        let section = Self.selectedSection(in: sections, id: selection)
        HStack(spacing: 0) {
            sidebar(selected: section?.id)
            VStack(spacing: 0) {
                if let onClose {
                    MacBusinessSheetHeader(onClose: onClose)
                }
                if let section {
                    ESettingsPage {
                        EPageHeader(title: section.title)
                        section.content()
                    }
                    // 每个分类有自己的滚动与焦点范围。
                    .id(section.id)
                } else {
                    Text("No settings available", tableName: "Settings", bundle: .module)
                        .foregroundStyle(theme.colors.secondaryText)
                        .frame(maxWidth: .infinity, maxHeight: .infinity)
                }
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
        }
        .frame(minWidth: 540, idealWidth: 760, minHeight: 360, idealHeight: 520)
        .background(theme.colors.background)
    }

    private func sidebar(selected: String?) -> some View {
        VStack(alignment: .leading, spacing: theme.spacing.inline) {
            title
                .font(theme.typography.sectionTitle)
                .foregroundStyle(theme.colors.text)
                .padding(.horizontal, theme.spacing.group)
                .padding(.top, theme.spacing.group)
                .accessibilityAddTraits(.isHeader)
            List(selection: Binding(get: { selected }, set: { selection = $0 })) {
                ForEach(sections) { section in
                    ESidebarItem {
                        Label { section.title } icon: { Image(systemName: section.systemImage) }
                    }
                    .tag(section.id)
                }
            }
            .listStyle(.sidebar)
            .scrollContentBackground(.hidden)
            .contentMargins(.top, 0, for: .scrollContent)
            .accessibilityLabel(title)
        }
        .background(theme.colors.sidebarSurface)
        .glassEffect(.regular, in: RoundedRectangle(cornerRadius: theme.cardRadius * 2))
        .padding(theme.spacing.controlGroup)
        .frame(width: 200)
    }

    static func selectedSection(in sections: [BusinessSettingsSection], id: String?) -> BusinessSettingsSection? {
        sections.first { $0.id == id } ?? sections.first
    }
}
#endif
