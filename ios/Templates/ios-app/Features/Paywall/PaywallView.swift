import SwiftUI
import L10nKit
import PurchaseCore

// MARK: - ② 买断墙
// 标题 + 说明 + 价格。文案按产品改 xcstrings。Mac 上跑 iPhone App 须显式注入 LifetimeStore。

struct PaywallView: View {
    @Environment(LifetimeStore.self) private var store
    @Environment(LocalizationManager.self) private var localization
    @Environment(\.dismiss) private var dismiss
    @State private var errorMessage: String?
    @State private var isRestoring = false

    var body: some View {
        let _ = localization.language
        NavigationStack {
            VStack(spacing: 16) {
                Spacer()
                Text(loc("paywall_title"))
                    .font(.title2.weight(.semibold))
                    .multilineTextAlignment(.center)
                Text(loc("paywall_body"))
                    .font(.body)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                    .padding(.horizontal, 28)
                if store.isPurchased {
                    Text(loc("paywall_owned"))
                        .font(.callout)
                } else if let price = store.priceText {
                    Text(price)
                        .font(.largeTitle.weight(.bold))
                    Text(loc("paywall_once"))
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                } else if store.isLoadingProduct {
                    ProgressView()
                } else if let err = store.productLoadError {
                    Text(err)
                        .font(.footnote)
                        .foregroundStyle(.secondary)
                        .multilineTextAlignment(.center)
                    Button(loc("store_retry_load")) {
                        Task { await store.reloadProduct() }
                    }
                }
                Spacer()
            }
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .toolbar {
                ToolbarItem(placement: .cancellationAction) {
                    Button(loc("common_close")) { dismiss() }
                }
                ToolbarItemGroup(placement: .bottomBar) {
                    Button(loc("store_restore")) {
                        Task { await restore() }
                    }
                    .disabled(isRestoring || store.isPurchased)
                    Spacer(minLength: 12)
                    Button(buyLabel) {
                        Task { await buy() }
                    }
                    .buttonStyle(.borderedProminent)
                    .disabled(!store.canPurchase)
                }
            }
            .alert(loc("store_err_title"), isPresented: Binding(
                get: { errorMessage != nil },
                set: { if !$0 { errorMessage = nil } }
            )) {
                Button(loc("common_ok"), role: .cancel) {}
            } message: {
                Text(errorMessage ?? "")
            }
            .onAppear { store.startIfNeeded() }
        }
    }

    private var buyLabel: String {
        if store.isPurchasing { return loc("paywall_buying") }
        if let price = store.priceText {
            return String(format: loc("paywall_buy_fmt"), price)
        }
        return loc("paywall_buy")
    }

    private func buy() async {
        do {
            if try await store.purchase() { dismiss() }
        } catch {
            errorMessage = error.localizedDescription
        }
    }

    private func restore() async {
        isRestoring = true
        defer { isRestoring = false }
        do {
            try await store.restore()
            if store.isPurchased { dismiss() }
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}
