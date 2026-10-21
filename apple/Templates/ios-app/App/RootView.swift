import SwiftUI
import StoreKit
import DesignCore
import DesignKitIOS
import L10nKit
import LogKit

// MARK: - ① App 层 · 根路由

struct RootView: View {
    @Environment(LocalizationManager.self) private var localization
    @Environment(\.requestReview) private var requestReview

    var body: some View {
        // loc() 0.2.0 不登记 Observation；读 language 才能让切语言当场重绘。
        let _ = localization.language
        NavigationStack {
            VStack(spacing: 16) {
                Text(loc("home_title"))
                    .font(.title2.weight(.semibold))
                Text(loc("home_subtitle"))
                    .font(.subheadline)
                    .foregroundStyle(.secondary)
                    .multilineTextAlignment(.center)
                NavigationLink(loc("settings_title")) {
                    SettingsView()
                }
                .buttonStyle(.borderedProminent)
                .scalePress()
            }
            .padding(24)
            .frame(maxWidth: .infinity, maxHeight: .infinity)
            .navigationTitle(loc("home_title"))
        }
        .onAppear {
            AppLog.logger(category: "ui").info("RootView appear")
            ReviewPrompt.recordLaunch(requestReview: requestReview)
        }
    }
}
