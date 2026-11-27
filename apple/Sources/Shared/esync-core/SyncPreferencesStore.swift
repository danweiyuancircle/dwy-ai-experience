import Observation

/// 显式偏好命令与已提交快照的通用入口；不监听 UserDefaults，也不将运行时投影反向保存。
/// 宿主在同一 MainActor turn 发布作用域和快照，operation 仍须在持久化边界校验捕获的票据。
@MainActor
@Observable
public final class SyncPreferencesStore<Value: Equatable & Sendable> {
    public private(set) var value: Value
    public private(set) var generation: UInt64

    /// 安装时立即投影当前快照；apply 必须同步且不能重新调用保存入口。
    @ObservationIgnored public var onApply: (@MainActor (Value, UInt64) -> Void)? {
        didSet { onApply?(value, generation) }
    }
    @ObservationIgnored private var pendingTask: Task<Void, Never>?

    /// generation 为宿主单调递增的作用域票据；value 必须来自已提交的本地仓储。
    public init(value: Value, generation: UInt64) {
        self.value = value
        self.generation = generation
    }

    /// 同值跨作用域也重新投影；迟到旧作用域的快照不能覆盖当前运行时。
    public func apply(_ value: Value, generation: UInt64) {
        guard generation >= self.generation else { return }
        guard value != self.value || generation != self.generation else { return }
        self.value = value
        self.generation = generation
        onApply?(value, generation)
    }

    /// 在排任务前捕获归属并按用户操作顺序提交；失败不改快照，旧作用域失败不污染新界面。
    @discardableResult
    public func submit(_ operation: @escaping @MainActor (UInt64) async throws -> Void,
                       onFailure: @escaping @MainActor (any Error) -> Void) -> Task<Void, Never> {
        let ticket = generation
        let previous = pendingTask
        let task = Task { [weak self] in
            await previous?.value
            guard let self, ticket == self.generation else { return }
            do { try await operation(ticket) }
            catch {
                if ticket == self.generation { onFailure(error) }
            }
        }
        pendingTask = task
        return task
    }
}
