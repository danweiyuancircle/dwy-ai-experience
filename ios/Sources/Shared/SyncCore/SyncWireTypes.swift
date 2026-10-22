import Foundation

/// 有界业务 JSON；整数单独保存，避免 Int64 经 Double 发生精度丢失。
public enum SyncJSON: Codable, Equatable, Sendable {
    case object([String: SyncJSON])
    case array([SyncJSON])
    case string(String)
    case integer(Int64)
    case number(Double)
    case bool(Bool)
    case null

    /// 优先识别布尔与整数，超出 Int64 的整数不允许静默舍入。
    public init(from decoder: any Decoder) throws {
        let container = try decoder.singleValueContainer()
        if container.decodeNil() { self = .null }
        else if let value = try? container.decode(Bool.self) { self = .bool(value) }
        else if let value = try? container.decode(Int64.self) { self = .integer(value) }
        else if let value = try? container.decode(Double.self) {
            guard value.isFinite, value.rounded() != value || abs(value) <= 9_007_199_254_740_991 else {
                throw DecodingError.dataCorruptedError(in: container, debugDescription: "JSON 数值超出精确整数范围")
            }
            self = .number(value)
        } else if let value = try? container.decode(String.self) { self = .string(value) }
        else if let value = try? container.decode([SyncJSON].self) { self = .array(value) }
        else { self = .object(try container.decode([String: SyncJSON].self)) }
    }

    /// 非有限浮点由 JSONEncoder 拒绝，绝不转为不符合 JSON 的字符串。
    public func encode(to encoder: any Encoder) throws {
        var container = encoder.singleValueContainer()
        switch self {
        case let .object(value): try container.encode(value)
        case let .array(value): try container.encode(value)
        case let .string(value): try container.encode(value)
        case let .integer(value): try container.encode(value)
        case let .number(value): try container.encode(value)
        case let .bool(value): try container.encode(value)
        case .null: try container.encodeNil()
        }
    }

    /// JSON 的 1 与 1.0 等价；只在 Double 能精确表示该整数时跨 case 比较。
    public static func == (lhs: Self, rhs: Self) -> Bool {
        switch (lhs, rhs) {
        case let (.object(a), .object(b)): return a == b
        case let (.array(a), .array(b)): return a == b
        case let (.string(a), .string(b)): return a == b
        case let (.integer(a), .integer(b)): return a == b
        case let (.number(a), .number(b)): return a == b
        case let (.integer(a), .number(b)), let (.number(b), .integer(a)): return Int64(exactly: b) == a
        case let (.bool(a), .bool(b)): return a == b
        case (.null, .null): return true
        default: return false
        }
    }
}

/// 服务端文档快照；version 与 cursor 从不通过浮点解析。
public struct SyncRecord: Codable, Equatable, Sendable {
    public let recordID: UUID
    public let version: Int64
    public let cursor: Int64
    public let deleted: Bool
    /// 墓碑必须为 nil；非墓碑必须包含已注册的 kind。
    public let payload: [String: SyncJSON]?

    public init(recordID: UUID, version: Int64, cursor: Int64, deleted: Bool, payload: [String: SyncJSON]?) {
        self.recordID = recordID; self.version = version; self.cursor = cursor
        self.deleted = deleted; self.payload = payload
    }

    enum CodingKeys: String, CodingKey {
        case recordID = "record_id", version, cursor, deleted, payload
    }

    /// 墓碑快照保留显式 null，不让可选字段省略改变服务端 JSON 合同。
    public func encode(to encoder: any Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(recordID, forKey: .recordID)
        try container.encode(version, forKey: .version)
        try container.encode(cursor, forKey: .cursor)
        try container.encode(deleted, forKey: .deleted)
        try container.encode(payload, forKey: .payload)
    }
}

/// 冻结后不可变的上传操作，重试必须保留全部字段。
public struct SyncMutation: Codable, Equatable, Sendable {
    public let operationID: UUID
    public let recordID: UUID
    /// 服务端上界为 Int64.max - 1，为下一版本保留空间。
    public let baseVersion: Int64
    public let deleted: Bool
    public let payload: [String: SyncJSON]?

    public init(operationID: UUID, recordID: UUID, baseVersion: Int64, deleted: Bool, payload: [String: SyncJSON]?) {
        self.operationID = operationID; self.recordID = recordID; self.baseVersion = baseVersion
        self.deleted = deleted; self.payload = payload
    }

    enum CodingKeys: String, CodingKey {
        case operationID = "operation_id", recordID = "record_id", baseVersion = "base_version", deleted, payload
    }

    /// 删除也显式发送 null，与现有服务端合同一致。
    public func encode(to encoder: any Encoder) throws {
        var container = encoder.container(keyedBy: CodingKeys.self)
        try container.encode(operationID, forKey: .operationID)
        try container.encode(recordID, forKey: .recordID)
        try container.encode(baseVersion, forKey: .baseVersion)
        try container.encode(deleted, forKey: .deleted)
        try container.encode(payload, forKey: .payload)
    }
}

/// 单操作回执；replayed 表示服务端返回相同 operationID 的历史结果。
public struct SyncMutationResult: Codable, Equatable, Sendable {
    public let operationID: UUID
    public let record: SyncRecord
    public let replayed: Bool
    public init(operationID: UUID, record: SyncRecord, replayed: Bool) {
        self.operationID = operationID; self.record = record; self.replayed = replayed
    }
    enum CodingKeys: String, CodingKey { case operationID = "operation_id", record, replayed }
}

/// 上传结果中的 cursor 仅供参考，禁止直接替换本地 pullCursor。
public struct SyncPushResult: Codable, Equatable, Sendable {
    public let items: [SyncMutationResult]
    public let cursor: Int64
    public init(items: [SyncMutationResult], cursor: Int64) { self.items = items; self.cursor = cursor }
}

/// 增量拉取页；只有整页事务提交后才能推进 nextCursor。
public struct SyncPullPage: Codable, Equatable, Sendable {
    public let items: [SyncRecord]
    public let nextCursor: Int64
    public let hasMore: Bool
    public init(items: [SyncRecord], nextCursor: Int64, hasMore: Bool) {
        self.items = items; self.nextCursor = nextCursor; self.hasMore = hasMore
    }
    enum CodingKeys: String, CodingKey { case items, nextCursor = "next_cursor", hasMore = "has_more" }
}

/// 一次同步会话身份；令牌仅存在内存，由宿主认证系统提供。
public struct SyncIdentity: Equatable, Sendable, CustomStringConvertible, CustomDebugStringConvertible {
    public let userID: UUID
    public let deviceID: UUID
    public let accessToken: String
    public init(userID: UUID, deviceID: UUID, accessToken: String) {
        self.userID = userID; self.deviceID = deviceID; self.accessToken = accessToken
    }
    /// 默认打印和调试打印均脱敏，避免宿主记录身份时泄露 Bearer。
    public var description: String { "SyncIdentity(userID: \(userID), deviceID: \(deviceID), accessToken: [redacted])" }
    public var debugDescription: String { description }
}

/// 无存储依赖的传输接口；每次 push 固定为一个冻结操作。
public protocol SyncTransport: Sendable {
    /// 固定后端、应用与账号；协调器必须与存储作用域逐字段匹配。
    var scope: SyncScope { get }
    func push(_ mutation: SyncMutation, identity: SyncIdentity) async throws -> SyncPushResult
    func pull(cursor: Int64, identity: SyncIdentity) async throws -> SyncPullPage
}

/// 本地协议边界错误；固定 case 不携带 URL、正文或认证令牌。
public enum SyncTransportError: Error, Equatable, Sendable {
    case invalidBaseURL
    case invalidIdentity
    case invalidRequest
    case invalidResponse
    case responseTooLarge
}

/// 服务错误保留 HTTP 状态和业务 code；同为 409 也不等同版本冲突。
public struct SyncServerError: Error, Equatable, Sendable {
    public let statusCode: Int
    public let code: String
    /// 有界诊断文案；宿主不应直接当作面向用户的说明。
    public let message: String
    public let operationID: UUID?
    public let current: SyncRecord?
    /// 只接受有限非负秒数，协调器结合自身上限决定退避。
    public let retryAfter: TimeInterval?
    public init(statusCode: Int, code: String, message: String, operationID: UUID? = nil, current: SyncRecord? = nil, retryAfter: TimeInterval? = nil) {
        self.statusCode = statusCode; self.code = code; self.message = message
        self.operationID = operationID; self.current = current; self.retryAfter = retryAfter
    }
}

/// 存储与 HTTP 共用边界，防止本地保存成功后才被传输层拒绝。
enum SyncWireValidation {
    /// 通用硬上限不替代应用更小的 schema 业务限制。
    static let maxPayloadBytes = 1_048_576

    /// kind 用于注册表路由；仅允许稳定 ASCII 标识符，最多128字节。
    static func validKind(_ kind: String) -> Bool {
        !kind.isEmpty && kind.utf8.count <= 128 && kind.utf8.allSatisfy {
            (48...57).contains($0) || (65...90).contains($0) || (97...122).contains($0) || [45, 46, 95].contains($0)
        }
    }

    /// 版本/游标范围、墓碑与 payload 必须同时合法。
    static func validRecord(_ record: SyncRecord) -> Bool {
        record.version > 0 && record.cursor > 0 && validPayload(record.payload, deleted: record.deleted)
    }

    /// 通用层仅验证 JSON 与 kind 边界，业务字段交给宿主注册 schema。
    static func validPayload(_ payload: [String: SyncJSON]?, deleted: Bool) -> Bool {
        guard deleted == (payload == nil) else { return false }
        guard let payload else { return true }
        guard case let .string(kind) = payload["kind"], validKind(kind),
              validJSON(.object(payload), depth: 0),
              let data = try? JSONEncoder().encode(payload), data.count <= maxPayloadBytes
        else { return false }
        return true
    }

    /// 编码之前限制深度与容器规模，避免递归或巨大单字段占用无界内存。
    private static func validJSON(_ value: SyncJSON, depth: Int) -> Bool {
        guard depth <= 64 else { return false }
        switch value {
        case let .object(values):
            return values.count <= 10_000 && values.allSatisfy { $0.key.utf8.count <= 1_024 && validJSON($0.value, depth: depth + 1) }
        case let .array(values): return values.count <= 10_000 && values.allSatisfy { validJSON($0, depth: depth + 1) }
        case let .string(value): return value.utf8.count <= maxPayloadBytes
        case let .number(value): return value.isFinite
        case .integer, .bool, .null: return true
        }
    }
}
