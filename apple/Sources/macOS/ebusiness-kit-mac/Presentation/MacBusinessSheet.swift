#if os(macOS)
import DesignKitMac
import SwiftUI

/// 业务弹框的统一标题和关闭入口。原生宿主负责呈现与窗口归属。
public struct MacBusinessSheetHeader: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text?
    private let onClose: () -> Void

    /// 设置右栏可以省略标题，页面标题随分类内容显示。
    public init(title: Text? = nil, onClose: @escaping () -> Void) {
        self.title = title
        self.onClose = onClose
    }

    public var body: some View {
        HStack(spacing: theme.spacing.group) {
            if let title {
                title
                    .font(theme.typography.sectionTitle)
                    .foregroundStyle(theme.colors.text)
                    .accessibilityAddTraits(.isHeader)
            }
            Spacer(minLength: theme.spacing.group)
            ESheetCloseButton(Text("Close", tableName: "Settings", bundle: .module), action: onClose)
        }
        .padding(.horizontal, theme.spacing.pageInset)
        .padding(.vertical, theme.spacing.controlGroup)
    }
}

/// 供原生 `.sheet` 内容使用的业务弹框布局。标题和底部操作在滚动区之外。
public struct MacBusinessSheet<Content: View, Footer: View>: View {
    @Environment(\.eControlTheme) private var theme
    private let title: Text
    private let onClose: () -> Void
    private let content: Content
    private let footer: Footer

    /// 业务表单提供内容和底部操作，宿主处理提交结果与关闭路由。
    public init(
        title: Text,
        onClose: @escaping () -> Void,
        @ViewBuilder content: () -> Content,
        @ViewBuilder footer: () -> Footer
    ) {
        self.title = title
        self.onClose = onClose
        self.content = content()
        self.footer = footer()
    }

    public var body: some View {
        VStack(spacing: 0) {
            MacBusinessSheetHeader(title: title, onClose: onClose)
            ESettingsPage { content }
            footer
                .frame(maxWidth: .infinity)
                .padding(.horizontal, theme.spacing.pageInset)
                .padding(.vertical, theme.spacing.group)
        }
        .background(theme.colors.background)
    }
}
#endif
