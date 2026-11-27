import Foundation

/// 将同步回调的存储提交与 pause 建立完成屏障；仅在同步数据库事务内持有。
final class SyncExecutionLease: @unchecked Sendable {
    private let lock = NSRecursiveLock()
    private var valid = true

    /// 锁覆盖整个同步事务，invalidate 返回后不会再有旧许可的排队事务提交。
    func withValidity<T>(_ body: () throws -> T) throws -> T {
        lock.lock()
        defer { lock.unlock() }
        guard valid else { throw CancellationError() }
        return try body()
    }

    /// 等待已获许可的事务结束；此后该许可永不恢复，新一代执行器使用新实例。
    func invalidate() {
        lock.lock()
        defer { lock.unlock() }
        valid = false
    }
}
