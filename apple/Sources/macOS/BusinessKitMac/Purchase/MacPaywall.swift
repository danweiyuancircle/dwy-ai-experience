#if os(macOS)
import DesignKitMac
import SwiftUI

public extension View {
    /// 呈现原生付费 sheet。获得权益后，系统关闭 sheet 才回报有效商品，便于接续原操作。
    @MainActor
    func macPaywall(
        isPresented: Binding<Bool>,
        configuration: MacPaywallConfiguration,
        store: MacPaywallStore,
        onUnlocked: @escaping @MainActor (Set<String>) -> Void = { _ in }
    ) -> some View {
        modifier(MacPaywallPresentation(
            isPresented: isPresented, configuration: configuration, store: store, onUnlocked: onUnlocked
        ))
    }
}

/// 供宿主已有设置页或原生模态窗口嵌入的购买内容，共用完整购买和恢复流程。
public struct MacPaywallView<Summary: View, Details: View>: View {
    private let configuration: MacPaywallConfiguration
    private let store: MacPaywallStore
    private let scrollsContent: Bool
    private let onUnlocked: @MainActor (Set<String>) -> Void
    private let summary: Summary
    private let details: Details
    @State private var flow = MacPaywallFlow()

    /// 滚动布局固定购买按钮。嵌入模式直接回报权益，窗口收起及收起后的操作由宿主管理。
    public init(
        configuration: MacPaywallConfiguration,
        store: MacPaywallStore,
        scrollsContent: Bool,
        onUnlocked: @escaping @MainActor (Set<String>) -> Void = { _ in },
        @ViewBuilder summary: () -> Summary,
        @ViewBuilder details: () -> Details
    ) {
        self.configuration = configuration
        self.store = store
        self.scrollsContent = scrollsContent
        self.onUnlocked = onUnlocked
        self.summary = summary()
        self.details = details()
    }

    public var body: some View {
        MacPaywallContent(
            configuration: configuration, store: store, flow: flow, scrollsContent: scrollsContent,
            summary: summary, details: details, close: nil
        ) {
            let products = flow.takeUnlocked()
            if !products.isEmpty { onUnlocked(products) }
        }
    }
}

private struct MacPaywallPresentation: ViewModifier {
    @Binding var isPresented: Bool
    let configuration: MacPaywallConfiguration
    let store: MacPaywallStore
    let onUnlocked: @MainActor (Set<String>) -> Void
    @State private var flow = MacPaywallFlow()

    func body(content: Content) -> some View {
        content.sheet(isPresented: $isPresented, onDismiss: {
            let products = flow.dismissed()
            if !products.isEmpty { onUnlocked(products) }
        }) {
            MacPaywallContent(
                configuration: configuration, store: store, flow: flow, scrollsContent: true,
                summary: EmptyView(), details: EmptyView(), close: { isPresented = false }
            ) {
                isPresented = false
            }
            .frame(minWidth: 320, idealWidth: 520, maxWidth: 620, minHeight: 380, idealHeight: 530, maxHeight: 680)
            .presentationSizing(.fitted)
        }
    }
}

private struct MacPaywallContent<Summary: View, Details: View>: View {
    @Environment(\.eControlTheme) private var theme
    @State private var selectedProductID: String?
    @State private var session: Int?
    let configuration: MacPaywallConfiguration
    let store: MacPaywallStore
    let flow: MacPaywallFlow
    let scrollsContent: Bool
    let summary: Summary
    let details: Details
    let close: (() -> Void)?
    let finishUnlock: () -> Void

    var body: some View {
        let snapshot = store.snapshot()
        let plan = selectedPlan(in: snapshot)
        VStack(spacing: 0) {
            if let close {
                header(close: close)
                Divider()
            }
            if scrollsContent {
                ScrollView { purchaseContent(plan: plan, snapshot: snapshot) }
                Divider()
            } else {
                purchaseContent(plan: plan, snapshot: snapshot)
            }
            footer(plan, snapshot: snapshot)
        }
        .background(theme.colors.background)
        .task {
            session = flow.begin()
            if !configuration.plans.isEmpty { await flow.load(store: store) }
        }
        .onDisappear { flow.deactivate(session) }
        .onChange(of: pendingApproved(in: snapshot)) { _, approved in
            if approved, flow.isCurrent(session), flow.confirmPending(store.snapshot().purchasedProductIDs) {
                finishUnlock()
            }
        }
        .interactiveDismissDisabled(isCompletingTransaction)
    }

    private var isCompletingTransaction: Bool { flow.operation == .buying || flow.operation == .restoring }

    private func pendingApproved(in snapshot: MacPaywallSnapshot) -> Bool {
        guard flow.operation == .idle, let id = flow.pendingProductID else { return false }
        return snapshot.purchasedProductIDs.contains(id)
    }

    private func purchaseContent(plan: MacPaywallPlan?, snapshot: MacPaywallSnapshot) -> some View {
        VStack(alignment: .leading, spacing: theme.spacing.section) {
            if let subtitle = configuration.subtitle {
                Text(verbatim: subtitle).foregroundStyle(theme.colors.secondaryText)
            }
            summary
            VStack(spacing: theme.spacing.controlGroup) {
                ForEach(configuration.plans) { option in
                    planRow(option, selected: option.id == plan?.id, snapshot: snapshot)
                }
            }
            loadingStatus(snapshot)
            if !configuration.features.isEmpty { featureComparison }
            details
            if configuration.termsURL != nil || configuration.privacyURL != nil {
                HStack(spacing: theme.spacing.group) {
                    if let url = configuration.termsURL {
                        Link(destination: url) {
                            Text("Terms of Use", tableName: "Purchase", bundle: .module)
                        }
                    }
                    if let url = configuration.privacyURL {
                        Link(destination: url) {
                            Text("Privacy Policy", tableName: "Purchase", bundle: .module)
                        }
                    }
                }
                .font(theme.typography.caption)
            }
        }
        .frame(maxWidth: .infinity, alignment: .leading)
        .padding(theme.spacing.pageInset)
    }

    private func header(close: @escaping () -> Void) -> some View {
        HStack(alignment: .center, spacing: theme.spacing.group) {
            Text(verbatim: configuration.title)
                .font(theme.typography.pageTitle)
                .foregroundStyle(theme.colors.text)
                .accessibilityAddTraits(.isHeader)
            Spacer(minLength: 0)
            EButton(emphasis: .plain, action: close) {
                Label {
                    Text("Close", tableName: "Purchase", bundle: .module)
                } icon: {
                    Image(systemName: "xmark")
                }
                .labelStyle(.iconOnly)
            }
            .keyboardShortcut(.cancelAction)
            .disabled(isCompletingTransaction)
        }
        .padding(theme.spacing.pageInset)
    }

    private func selectedPlan(in snapshot: MacPaywallSnapshot) -> MacPaywallPlan? {
        let options = configuration.plans
        let available = options.filter { snapshot.prices[$0.id] != nil && !snapshot.purchasedProductIDs.contains($0.id) }
        if let selected = available.first(where: { $0.id == selectedProductID }) { return selected }
        return available.first(where: \.isRecommended) ?? available.first ??
            options.first(where: { snapshot.purchasedProductIDs.contains($0.id) })
    }

    private func planRow(_ plan: MacPaywallPlan, selected: Bool, snapshot: MacPaywallSnapshot) -> some View {
        let owned = snapshot.purchasedProductIDs.contains(plan.id)
        return Button {
            selectedProductID = plan.id
        } label: {
            ECard {
                HStack(alignment: .top, spacing: theme.spacing.group) {
                    Image(systemName: owned ? "checkmark.circle.fill" : selected ? "largecircle.fill.circle" : "circle")
                        .foregroundStyle(selected || owned ? theme.accent : theme.colors.secondaryText)
                        .accessibilityHidden(true)
                    VStack(alignment: .leading, spacing: theme.spacing.inline) {
                        Text(verbatim: plan.title).font(theme.typography.sectionTitle)
                        if let detail = plan.detail {
                            Text(verbatim: detail)
                                .font(theme.typography.secondary)
                                .foregroundStyle(theme.colors.secondaryText)
                        }
                        if plan.isRecommended {
                            Text("Recommended", tableName: "Purchase", bundle: .module)
                                .font(theme.typography.caption)
                                .foregroundStyle(theme.accent)
                        }
                    }
                    Spacer(minLength: 0)
                    if owned {
                        Text("Purchased", tableName: "Purchase", bundle: .module)
                            .foregroundStyle(theme.colors.success)
                    } else if let price = snapshot.prices[plan.id] {
                        Text(verbatim: price).font(theme.typography.sectionTitle)
                    } else if flow.operation != .loading {
                        Text("Unavailable", tableName: "Purchase", bundle: .module)
                            .foregroundStyle(theme.colors.secondaryText)
                    }
                }
            }
        }
        .buttonStyle(.plain)
        .accessibilityAddTraits(selected ? .isSelected : [])
        .accessibilityIdentifier("paywall.plan.\(plan.id)")
        .disabled(owned || snapshot.prices[plan.id] == nil || isCompletingTransaction)
    }

    @ViewBuilder
    private func loadingStatus(_ snapshot: MacPaywallSnapshot) -> some View {
        if flow.operation == .loading {
            ProgressView {
                Text("Loading products…", tableName: "Purchase", bundle: .module)
            }
            .controlSize(.small)
        } else if let message = snapshot.loadError {
            VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
                Text(verbatim: message).foregroundStyle(theme.colors.secondaryText)
                retryButton
            }
        } else if configuration.plans.contains(where: { snapshot.prices[$0.id] == nil && !snapshot.purchasedProductIDs.contains($0.id) }) {
            retryButton
        }
    }

    private var retryButton: some View {
        EButton(emphasis: .plain) {
            Task { await flow.load(store: store) }
        } label: {
            Text("Retry loading products", tableName: "Purchase", bundle: .module)
        }
        .disabled(flow.operation != .idle)
    }

    private var featureComparison: some View {
        let showColumns = configuration.features.contains { $0.free != nil || $0.paid != nil }
        return VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
            Text("Features", tableName: "Purchase", bundle: .module)
                .font(theme.typography.sectionTitle)
                .accessibilityAddTraits(.isHeader)
            ECard {
                Grid(alignment: .leading, horizontalSpacing: theme.spacing.group, verticalSpacing: theme.spacing.group) {
                    if showColumns {
                        GridRow {
                            Color.clear.frame(height: 0).accessibilityHidden(true)
                            Text("Free", tableName: "Purchase", bundle: .module).font(theme.typography.sectionTitle)
                            Text("Paid", tableName: "Purchase", bundle: .module).font(theme.typography.sectionTitle)
                        }
                    }
                    ForEach(Array(configuration.features.enumerated()), id: \.offset) { _, feature in
                        GridRow {
                            Text(verbatim: feature.title).frame(maxWidth: .infinity, alignment: .leading)
                            if showColumns {
                                featureValue(feature.free)
                                featureValue(feature.paid)
                            }
                        }
                    }
                }
            }
        }
    }

    private func featureValue(_ value: String?) -> some View {
        Group {
            if let value {
                Text(verbatim: value)
            } else {
                Image(systemName: "minus")
                    .accessibilityLabel(Text("Not included", tableName: "Purchase", bundle: .module))
            }
        }
        .font(theme.typography.secondary)
        .foregroundStyle(theme.colors.secondaryText)
    }

    private func footer(_ plan: MacPaywallPlan?, snapshot: MacPaywallSnapshot) -> some View {
        VStack(alignment: .leading, spacing: theme.spacing.controlGroup) {
            notice
            HStack(spacing: theme.spacing.group) {
                EButton(emphasis: .plain) {
                    let requestSession = session
                    Task {
                        guard flow.isCurrent(requestSession) else { return }
                        if await flow.restore(configured: configuration.restoreProductIDs, store: store),
                           flow.isCurrent(requestSession) { finishUnlock() }
                    }
                } label: {
                    if flow.operation == .restoring {
                        Text("Restoring…", tableName: "Purchase", bundle: .module)
                    } else {
                        Text("Restore Purchases", tableName: "Purchase", bundle: .module)
                    }
                }
                .disabled(flow.operation != .idle || configuration.restoreProductIDs.isEmpty)
                Spacer(minLength: 0)
                if !configuration.plans.isEmpty {
                    EButton(emphasis: .primary) {
                        guard let plan else { return }
                        let requestSession = session
                        Task {
                            guard flow.isCurrent(requestSession) else { return }
                            if await flow.buy(plan.id, store: store), flow.isCurrent(requestSession) { finishUnlock() }
                        }
                    } label: {
                        if flow.operation == .buying {
                            Text("Purchasing…", tableName: "Purchase", bundle: .module)
                        } else if let plan, snapshot.purchasedProductIDs.contains(plan.id) {
                            Text("Purchased", tableName: "Purchase", bundle: .module)
                        } else if let title = plan?.purchaseTitle {
                            Text(verbatim: title)
                        } else {
                            Text("Purchase", tableName: "Purchase", bundle: .module)
                        }
                    }
                    .accessibilityIdentifier("paywall.purchase")
                    .disabled(
                        flow.operation != .idle || flow.pendingProductID != nil ||
                        plan.map { snapshot.prices[$0.id] == nil || snapshot.purchasedProductIDs.contains($0.id) } != false
                    )
                }
            }
            if let plan, let price = snapshot.prices[plan.id], !snapshot.purchasedProductIDs.contains(plan.id) {
                Text(verbatim: plan.priceSuffix.map { price + $0 } ?? price)
                    .font(theme.typography.caption)
                    .foregroundStyle(theme.colors.secondaryText)
                    .frame(maxWidth: .infinity, alignment: .trailing)
            }
        }
        .padding(theme.spacing.pageInset)
    }

    @ViewBuilder
    private var notice: some View {
        if let notice = flow.notice {
            Group {
                switch notice {
                case .pending:
                    Text("This purchase is waiting for approval.", tableName: "Purchase", bundle: .module)
                case .noPurchases:
                    Text("There are no eligible purchases to restore.", tableName: "Purchase", bundle: .module)
                case .unconfirmed:
                    Text("Access has not been confirmed for this purchase.", tableName: "Purchase", bundle: .module)
                case let .failed(message):
                    Text(verbatim: message)
                }
            }
            .font(theme.typography.secondary)
            .foregroundStyle(theme.colors.secondaryText)
        }
    }
}
#endif
