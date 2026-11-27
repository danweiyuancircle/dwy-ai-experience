#if os(macOS)
import SwiftUI
import DesignKitMac

struct ApplicationIconExample: View {
    var body: some View {
        EApplicationIcon(bundleIdentifier: "com.apple.Terminal", fallbackSymbol: "terminal")
    }
}
#endif
