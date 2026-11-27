#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 内容状态必须由业务显式提供，组件不会从数据推断成功。
struct StateViewExample: View {
    @State private var state = EContentState.empty

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            EPicker(selection: $state) {
                Text("Idle").tag(EContentState.idle)
                Text("Loading").tag(EContentState.loading)
                Text("Success").tag(EContentState.success)
                Text("Empty").tag(EContentState.empty)
                Text("Failure").tag(EContentState.failure)
            } label: {
                Text("Content state")
            }
            EStateView(state: state, title: Text("Explicit content state"), detail: Text("The component never infers success from the data")) {
                EButton("Retry") { state = .loading }
            }
        }
    }
}
#endif
