import SwiftUI
import StoreKit
import DesignCore
import DesignKitMac
import L10nKit
import LogKit

// MARK: - ① App 层 · 根路由

struct RootView: View {
    @Environment(LocalizationManager.self) private var localization
    @Environment(\.requestReview) private var requestReview
    @Environment(\.eControlTheme) private var controlTheme

    var body: some View {
        // loc() 0.2.0 不登记 Observation；读 language 才能让切语言当场重绘。
        let _ = localization.language
        NavigationStack {
            VStack(spacing: controlTheme.spacing.group) {
                Text(loc("home_title"))
                    .font(controlTheme.typography.pageTitle)
                    .foregroundStyle(controlTheme.colors.text)
                Text(loc("home_subtitle"))
                    .font(controlTheme.typography.secondary)
                    .foregroundStyle(controlTheme.colors.secondaryText)
                    .multilineTextAlignment(.center)
                NavigationLink(loc("settings_title")) {
                    SettingsView()
                }
                .buttonStyle(.borderedProminent)
                .scalePress()
            }
            .padding(controlTheme.spacing.pageInset)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .background(controlTheme.colors.background)
            .navigationTitle(loc("home_title"))
        }
        .onAppear {
            AppLog.logger(category: "ui").info("RootView appear")
            ReviewPrompt.recordLaunch(requestReview: requestReview)
        }
    }
}
