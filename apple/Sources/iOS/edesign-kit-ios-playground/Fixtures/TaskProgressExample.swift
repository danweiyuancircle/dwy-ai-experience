#if os(iOS)
import SwiftUI
import DesignKitIOS

/// 取消请求与真实取消结果分别由业务回写；示例只改本地状态。
struct TaskProgressExample: View {
    @State private var phase = ETaskPhase.running
    @State private var fraction = 0.25

    var body: some View {
        VStack(alignment: .leading, spacing: 12) {
            determinate
            Slider(value: $fraction, in: 0...1)
            EButton("Confirm cancellation") { phase = .cancelled }
            EButton("Restart task") { phase = .running }
            ETaskProgress(title: Text("Indeterminate task"), phase: .running)
        }
    }

    @ViewBuilder private var determinate: some View {
        switch Result(catching: { try EProgressValue(fraction: fraction) }) {
        case .success(let value):
            ETaskProgress(title: title, phase: phase, progress: value, cancel: { phase = .cancelling }) {
                Text("Cancel task")
            }
        case .failure:
            EStateView(state: .failure, title: Text("Invalid progress"))
        }
    }

    private var title: Text {
        switch phase {
        case .running: Text("Task is running")
        case .cancelling: Text("Cancellation requested")
        case .cancelled: Text("Task was cancelled")
        case .succeeded: Text("Task succeeded")
        case .failed: Text("Task failed")
        }
    }
}
#endif
