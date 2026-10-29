import Foundation

/// 数据隔离键；用户 UUID 必须来自可信认证结果，游客使用 nil。
public struct SyncScope: Codable, Hashable, Sendable {
    public let backendURL: URL
    public let appID: String
    public let userID: UUID?

    public init(backendURL: URL, appID: String, userID: UUID?) {
        self.backendURL = backendURL
        self.appID = appID
        self.userID = userID
    }
}

/// 框架边界错误；消息仅说明约束，不包含业务正文或认证信息。
public enum SyncError: Error, Sendable, Equatable {
    case invalidConfiguration(String)
    case invalidPayload(String)
    case unknownKind(String)
    case unsupportedRecord
    case scopeMismatch
    case identityChanged
    case protocolViolation(String)
    case conflictNotFound
    case importRequiresInitialPull
}

/// 具体业务文档；id 与协议 kind 由框架管理，payload 不需重复声明。
public struct SyncDocument<Payload: Codable & Sendable>: Sendable {
    public let id: UUID
    public var payload: Payload

    public init(id: UUID, payload: Payload) {
        self.id = id
        self.payload = payload
    }
}

extension SyncDocument: Equatable where Payload: Equatable {}

/// 业务模型注册；maxPayloadBytes 限制编码后含 kind 的整份 JSON。
public struct SyncSchema<Payload: Codable & Sendable>: Sendable {
    public let kind: String
    public let maxPayloadBytes: Int
    let validate: @Sendable (Payload) throws -> Void
    let managedFields: Set<String>?
    let identityFields: Set<String>
    let conflictPolicy: SyncConflictPolicy
    let validateRecord: @Sendable (UUID, Payload) throws -> Void

    /// managedFields 指定可覆盖字段，未托管字段原样保留；identityFields 一经创建不可改变。
    /// validateRecord 校验固定实例与宿主适用范围，不能访问 UI 或执行网络请求。
    public init(kind: String, maxPayloadBytes: Int, managedFields: Set<String>? = nil,
                identityFields: Set<String> = [], conflictPolicy: SyncConflictPolicy = .manual,
                validateRecord: @escaping @Sendable (UUID, Payload) throws -> Void = { _, _ in },
                validate: @escaping @Sendable (Payload) throws -> Void) {
        self.kind = kind
        self.maxPayloadBytes = maxPayloadBytes
        self.validate = validate
        self.managedFields = managedFields
        self.identityFields = identityFields
        self.conflictPolicy = conflictPolicy
        self.validateRecord = validateRecord
    }

    /// 擦除仅用于注册与远端解码，公开写入仍要求具体业务类型。
    public var erased: AnySyncSchema {
        AnySyncSchema(kind: kind, maxPayloadBytes: maxPayloadBytes, managedFields: managedFields,
                      identityFields: identityFields, conflictPolicy: conflictPolicy) { id, data in
            let payload = try JSONDecoder().decode(Payload.self, from: data)
            try validate(payload)
            try validateRecord(id, payload)
        }
    }
}

/// 保存注册模型的解码校验器，不提供任意字典写入入口。
public struct AnySyncSchema: Sendable {
    public let kind: String
    public let maxPayloadBytes: Int
    let managedFields: Set<String>?
    let identityFields: Set<String>
    let conflictPolicy: SyncConflictPolicy
    let validateData: @Sendable (UUID, Data) throws -> Void

    init(kind: String, maxPayloadBytes: Int, managedFields: Set<String>?, identityFields: Set<String>,
         conflictPolicy: SyncConflictPolicy, validateData: @escaping @Sendable (UUID, Data) throws -> Void) {
        self.kind = kind
        self.maxPayloadBytes = maxPayloadBytes
        self.validateData = validateData
        self.managedFields = managedFields
        self.identityFields = identityFields
        self.conflictPolicy = conflictPolicy
    }
}

/// 普通文档保留冲突候选；设置类可基于最新原文重叠明确的本地字段，最多重基三次。
public enum SyncConflictPolicy: Sendable { case manual, localIntent }

/// 缺失、墓碑和暂不可解释必须区分，初始化只能使用 missing。
public enum SyncRecordState: Sendable, Equatable { case missing, deleted, available, unsupported }

/// 有界诊断只含记录标识和稳定原因，不暴露业务正文。
public struct SyncDiagnostic: Sendable, Equatable {
    public let recordID: UUID
    public let kind: String
    public let reason: String
}

/// 默认冲突选择；合并结果通过具体 payload 重载提交。
public enum SyncResolution: Sendable { case keepLocal, useRemote }

/// 提交后的存储快照；pendingCount 只含可自动发送项，隔离与永久暂停项通过 diagnostics 查询。
public struct SyncStoreSnapshot: Sendable, Equatable {
    public let pendingCount: Int
    public let conflictCount: Int
    public let changeSequence: Int64

    public init(pendingCount: Int, conflictCount: Int, changeSequence: Int64) {
        self.pendingCount = pendingCount
        self.conflictCount = conflictCount
        self.changeSequence = changeSequence
    }
}

/// 冲突保留双方和共同基线，删除候选用 localDeleted 或 remote.deleted 表达。
public struct SyncConflict: Codable, Sendable, Equatable {
    public let recordID: UUID
    public let kind: String
    public let localPayload: [String: SyncJSON]?
    public let localDeleted: Bool
    public let localRevision: Int64
    public let remote: SyncRecord?
    public let baseline: SyncRecord?
    public let reason: String
}
