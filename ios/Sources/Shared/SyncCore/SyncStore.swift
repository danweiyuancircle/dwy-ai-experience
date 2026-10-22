import CryptoKit
import Foundation
import GRDB

/// 单作用域离线存储。所有数据库调用同步完成，事务内无 await，避免 actor 重入拆开原子操作。
public actor SyncStore {
    public nonisolated let scope: SyncScope
    private let database: DatabaseQueue
    private let schemas: [String: AnySyncSchema]
    private var observers: [UUID: AsyncStream<SyncStoreSnapshot>.Continuation] = [:]

    /// 文件名由完整作用域散列生成；库内再次校验作用域，防止复制错库后串账号。
    public init(directory: URL, scope: SyncScope, schemas: [AnySyncSchema]) throws {
        try Self.validateScope(scope)
        guard !schemas.isEmpty, schemas.count <= 100 else {
            throw SyncError.invalidConfiguration("schemas count must be 1...100")
        }
        var registry: [String: AnySyncSchema] = [:]
        for schema in schemas {
            guard SyncWireValidation.validKind(schema.kind),
                  schema.maxPayloadBytes > 0, schema.maxPayloadBytes <= SyncWireValidation.maxPayloadBytes,
                  registry[schema.kind] == nil else {
                throw SyncError.invalidConfiguration("invalid or duplicate schema")
            }
            registry[schema.kind] = schema
        }
        self.scope = scope
        self.schemas = registry
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: true)
        let encodedScope = try Self.encode(scope)
        let hash = SHA256.hash(data: encodedScope).map { String(format: "%02x", $0) }.joined()
        database = try DatabaseQueue(path: directory.appendingPathComponent("sync-\(hash).sqlite").path)
        var migrator = DatabaseMigrator()
        migrator.registerMigration("sync_v1") { db in
            // 文档、草稿、冻结请求和冲突共同编码在同一行，避免部分更新导致队列丢失。
            try db.execute(sql: "CREATE TABLE documents (id TEXT PRIMARY KEY, kind TEXT NOT NULL, deleted INTEGER NOT NULL, pending INTEGER NOT NULL, conflicted INTEGER NOT NULL, body BLOB NOT NULL)")
            try db.execute(sql: "CREATE INDEX documents_kind ON documents(kind, id)")
            try db.execute(sql: "CREATE TABLE metadata (id INTEGER PRIMARY KEY CHECK (id = 1), body BLOB NOT NULL)")
            try db.execute(sql: "CREATE TABLE imports (id TEXT PRIMARY KEY)")
            // 设备恢复只隔离原请求，不删除其不可变身份与正文。
            try db.execute(sql: "CREATE TABLE quarantined_operations (id TEXT PRIMARY KEY, body BLOB NOT NULL)")
        }
        try migrator.migrate(database)
        try database.write { db in
            if let data = try Data.fetchOne(db, sql: "SELECT body FROM metadata WHERE id = 1") {
                let metadata = try JSONDecoder().decode(Metadata.self, from: data)
                guard metadata.scope == scope else { throw SyncError.scopeMismatch }
            } else {
                try Self.writeMetadata(Metadata(scope: scope), db: db)
            }
        }
    }

    /// 保存业务文档与待同步标记；冻结中的请求保持原样，后续编辑累积到新 revision。
    public func save<P>(_ document: SyncDocument<P>, using schema: SyncSchema<P>) throws {
        let payload = try validatedPayload(document.payload, schema: schema)
        try transaction { db in
            var stored = try read(document.id, db: db) ?? StoredDocument(id: document.id, kind: schema.kind)
            guard stored.kind == schema.kind || stored.kind.isEmpty else { throw SyncError.invalidPayload("record kind cannot change") }
            stored.kind = schema.kind
            stored.payload = payload
            stored.deleted = false
            stored.localRevision += 1
            stored.dirty = true
            try write(stored, db: db)
        }
    }

    /// 不存在或墓碑返回 nil；损坏正文和 schema 不匹配必须抛错。
    public func document<P>(id: UUID, using schema: SyncSchema<P>) throws -> SyncDocument<P>? {
        try registered(schema)
        return try database.read { db in
            guard let stored = try read(id, db: db), !stored.deleted else { return nil }
            return try typed(stored, schema: schema)
        }
    }

    /// 有界分页按 UUID 稳定排列；业务排序由业务模型自行表达。
    public func documents<P>(using schema: SyncSchema<P>, limit: Int = 100, offset: Int = 0) throws -> [SyncDocument<P>] {
        try registered(schema)
        guard (1...100).contains(limit), (0...1_000_000).contains(offset) else {
            throw SyncError.invalidPayload("invalid pagination")
        }
        return try database.read { db in
            try Data.fetchAll(db, sql: "SELECT body FROM documents WHERE kind = ? AND deleted = 0 ORDER BY id LIMIT ? OFFSET ?", arguments: [schema.kind, limit, offset]).map {
                try typed(decodeStored($0), schema: schema)
            }
        }
    }

    /// 使用墓碑保留删除意图；上传中的新增也必须先确认，再发删除。
    public func delete(id: UUID) throws {
        try transaction { db in
            guard var stored = try read(id, db: db), !stored.deleted else { return }
            stored.payload = nil
            stored.deleted = true
            stored.localRevision += 1
            stored.dirty = true
            try write(stored, db: db)
        }
    }

    /// 订阅提交后的快照，缓冲仅保留最新值，避免慢消费者无限积压。
    public func changes() -> AsyncStream<SyncStoreSnapshot> {
        let id = UUID()
        let (stream, continuation) = AsyncStream<SyncStoreSnapshot>.makeStream(bufferingPolicy: .bufferingNewest(1))
        observers[id] = continuation
        continuation.onTermination = { [weak self] _ in
            Task { await self?.removeObserver(id) }
        }
        return stream
    }

    /// 返回持久化冲突；未知结果的冻结请求不会提前变成可解决冲突。
    public func conflicts() throws -> [SyncConflict] {
        try database.read { db in
            try Data.fetchAll(db, sql: "SELECT body FROM documents WHERE conflicted = 1 ORDER BY id").map {
                let stored = try decodeStored($0)
                return SyncConflict(recordID: stored.id, kind: stored.kind, localPayload: stored.payload,
                                    localDeleted: stored.deleted, localRevision: stored.localRevision,
                                    remote: stored.remote, baseline: stored.baseline, reason: stored.conflictReason!)
            }
        }
    }

    /// 显式选择一方；本地优先会基于最新已知远端版本生成全新操作。
    public func resolveConflict(recordID: UUID, resolution: SyncResolution) throws {
        try transaction { db in
            var stored = try conflicted(recordID, db: db)
            let remote = stored.remote
            stored.baseline = remote
            stored.remote = nil
            stored.conflictReason = nil
            stored.localRevision += 1
            switch resolution {
            case .keepLocal:
                stored.dirty = true
            case .useRemote:
                stored.payload = remote?.payload
                stored.deleted = remote?.deleted ?? true
                stored.dirty = false
            }
            try write(stored, db: db)
        }
    }

    /// 业务合并必须再次通过已注册模型与字节上限校验，不能绕过 typed 写入。
    public func resolveConflict<P>(recordID: UUID, payload: P, using schema: SyncSchema<P>) throws {
        let validated = try validatedPayload(payload, schema: schema)
        try transaction { db in
            var stored = try conflicted(recordID, db: db)
            guard stored.kind == schema.kind else { throw SyncError.invalidPayload("record kind mismatch") }
            stored.baseline = stored.remote
            stored.remote = nil
            stored.conflictReason = nil
            stored.payload = validated
            stored.deleted = false
            stored.localRevision += 1
            stored.dirty = true
            try write(stored, db: db)
        }
    }

    /// 宿主明确选择后导入；收据与目标写入同事务，重复调用不覆盖后续编辑。
    public func importDocuments<P>(_ documents: [SyncDocument<P>], using schema: SyncSchema<P>, importID: UUID) throws {
        guard documents.count <= 100 else { throw SyncError.invalidPayload("import batch exceeds 100") }
        let validated = try documents.map { ($0.id, try validatedPayload($0.payload, schema: schema)) }
        guard Set(documents.map(\.id)).count == documents.count else { throw SyncError.invalidPayload("duplicate import UUID") }
        try transaction { db in
            if try Bool.fetchOne(db, sql: "SELECT EXISTS(SELECT 1 FROM imports WHERE id = ?)", arguments: [importID.uuidString]) == true { return }
            let metadata = try Self.readMetadata(db)
            guard scope.userID == nil || metadata.initialPullCompleted else { throw SyncError.importRequiresInitialPull }
            for (id, payload) in validated {
                if var stored = try read(id, db: db) {
                    guard stored.kind == schema.kind || stored.kind.isEmpty else { throw SyncError.invalidPayload("import kind mismatch") }
                    if stored.payload == payload && !stored.deleted { continue }
                    // 导入必须在初次拉取后显式执行，不能替换正在上传的本地请求。
                    guard stored.frozen == nil, !stored.dirty, stored.conflictReason == nil else {
                        throw SyncError.invalidPayload("import target has local changes")
                    }
                    stored.remote = stored.baseline
                    stored.payload = payload
                    stored.kind = schema.kind
                    stored.deleted = false
                    stored.localRevision += 1
                    stored.dirty = true
                    stored.conflictReason = "import_collision"
                    try write(stored, db: db)
                } else {
                    var stored = StoredDocument(id: id, kind: schema.kind)
                    stored.payload = payload
                    stored.localRevision = 1
                    stored.dirty = true
                    try write(stored, db: db)
                }
            }
            try db.execute(sql: "INSERT INTO imports(id) VALUES (?)", arguments: [importID.uuidString])
        }
    }

    func pullCursor() throws -> Int64 { try database.read { try Self.readMetadata($0).pullCursor } }

    /// 整页校验、合并与游标推进共享事务；任何坏记录均回滚全页。
    func apply(_ page: SyncPullPage, execution: SyncExecutionLease? = nil) throws {
        try withExecution(execution) {
            guard page.items.count <= 100, page.nextCursor >= 0 else { throw SyncError.protocolViolation("invalid pull page") }
            try transaction { db in
                var metadata = try Self.readMetadata(db)
                guard page.nextCursor >= metadata.pullCursor else { throw SyncError.protocolViolation("cursor regressed") }
                var previous = metadata.pullCursor
                var ids = Set<UUID>()
                for record in page.items {
                    try validateRecord(record)
                    guard record.cursor > previous, record.cursor <= page.nextCursor, ids.insert(record.recordID).inserted else {
                        throw SyncError.protocolViolation("unordered or duplicate pull record")
                    }
                    previous = record.cursor
                    var stored = try read(record.recordID, db: db) ?? StoredDocument(id: record.recordID, kind: kind(record.payload) ?? "")
                    try validateKind(record, for: stored)
                    if !record.deleted { stored.kind = kind(record.payload)! }
                    let knownVersion = max(stored.baseline?.version ?? 0, stored.remote?.version ?? 0)
                    if record.version > knownVersion {
                        if stored.frozen != nil || stored.conflictReason == "device_identity_changed" {
                            // 未知结果等幂等回执；设备恢复隔离只能由用户显式解除。
                            stored.remote = record
                        } else if stored.dirty {
                            reconcile(record, with: &stored)
                        } else {
                            adopt(record, into: &stored)
                        }
                        try write(stored, db: db)
                    }
                }
                guard !page.hasMore || page.nextCursor > metadata.pullCursor else { throw SyncError.protocolViolation("non-progressing page") }
                metadata.pullCursor = page.nextCursor
                if !page.hasMore { metadata.initialPullCompleted = true }
                try Self.writeMetadata(metadata, db: db)
            }
        }
    }

    /// 首次绑定可写入；已有绑定不可自动替换，必须走显式恢复。
    func bindDevice(_ deviceID: UUID, execution: SyncExecutionLease? = nil) throws {
        try withExecution(execution) {
            try database.write { db in
                var metadata = try Self.readMetadata(db)
                if let existing = metadata.deviceID, existing != deviceID { throw SyncError.identityChanged }
                metadata.deviceID = deviceID
                try Self.writeMetadata(metadata, db: db)
            }
        }
    }

    /// 冻结完整请求后才返回；同一文档最多一个未知结果请求，重试返回原值。
    func prepareNextMutation(deviceID: UUID, execution: SyncExecutionLease? = nil) throws -> SyncMutation? {
        return try withExecution(execution) {
            try bindDevice(deviceID)
            return try database.write { db in
                let data = try Data.fetchOne(db, sql: "SELECT body FROM documents WHERE pending = 1 AND conflicted = 0 ORDER BY id LIMIT 1")
                guard let data else { return nil }
                var stored = try decodeStored(data)
                if let frozen = stored.frozen {
                    guard frozen.deviceID == deviceID else { throw SyncError.identityChanged }
                    return frozen.mutation
                }
                let baseVersion = stored.baseline?.version ?? 0
                guard baseVersion < Int64.max else { throw SyncError.protocolViolation("record version exhausted") }
                let mutation = SyncMutation(operationID: UUID(), recordID: stored.id, baseVersion: baseVersion,
                                            deleted: stored.deleted, payload: stored.payload)
                stored.frozen = Frozen(mutation: mutation, deviceID: deviceID, localRevision: stored.localRevision)
                try write(stored, db: db)
                return mutation
            }
        }
    }

    /// 回执只清理对应冻结 revision；历史幂等快照不能覆盖更高版本的远端候选。
    func acknowledge(_ result: SyncMutationResult, execution: SyncExecutionLease? = nil) throws {
        try withExecution(execution) {
            try validateRecord(result.record)
            try transaction { db in
                guard var stored = try read(result.record.recordID, db: db), let frozen = stored.frozen,
                      frozen.mutation.operationID == result.operationID else { throw SyncError.protocolViolation("unmatched acknowledgment") }
                try validateKind(result.record, for: stored)
                guard result.record.version > frozen.mutation.baseVersion,
                      result.record.deleted == frozen.mutation.deleted, result.record.payload == frozen.mutation.payload else {
                    throw SyncError.protocolViolation("acknowledgment differs from frozen mutation")
                }
                let remote = stored.remote
                stored.frozen = nil
                stored.remote = nil
                stored.conflictReason = nil
                stored.baseline = result.record
                if stored.localRevision == frozen.localRevision {
                    adopt(remote.flatMap { $0.version > result.record.version ? $0 : nil } ?? result.record, into: &stored)
                } else {
                    stored.dirty = true
                    if let remote, remote.version > result.record.version { reconcile(remote, with: &stored) }
                    else if sameContent(stored, result.record) { stored.dirty = false }
                }
                try write(stored, db: db)
            }
        }
    }

    /// 仅 version_conflict 调用此入口；配额、400 和 operation_reused 保持冻结请求。
    func recordConflict(operationID: UUID, current: SyncRecord?, execution: SyncExecutionLease? = nil) throws {
        try withExecution(execution) {
            if let current { try validateRecord(current) }
            try transaction { db in
                let documents = try Data.fetchAll(db, sql: "SELECT body FROM documents WHERE pending = 1")
                guard var stored = try documents.map({ try decodeStored($0) }).first(where: { $0.frozen?.mutation.operationID == operationID }) else {
                    throw SyncError.protocolViolation("unmatched conflict")
                }
                if let current, current.recordID != stored.id { throw SyncError.protocolViolation("conflict record mismatch") }
                if let current { try validateKind(current, for: stored) }
                let remote = [current, stored.remote].compactMap { $0 }.max { $0.version < $1.version }
                stored.frozen = nil
                if let remote, sameContent(stored, remote) {
                    adopt(remote, into: &stored)
                } else {
                    stored.remote = remote
                    stored.conflictReason = "version_conflict"
                    stored.dirty = true
                }
                try write(stored, db: db)
            }
        }
    }

    /// 新设备先拉取后隔离旧冻结操作，保留请求证据并要求逐文档显式选择。
    func quarantinePendingOperations(newDeviceID: UUID, execution: SyncExecutionLease? = nil) throws {
        try withExecution(execution) {
            try transaction { db in
                var metadata = try Self.readMetadata(db)
                guard metadata.initialPullCompleted else { throw SyncError.importRequiresInitialPull }
                for data in try Data.fetchAll(db, sql: "SELECT body FROM documents WHERE pending = 1") {
                    var stored = try decodeStored(data)
                    guard let frozen = stored.frozen else { continue }
                    try db.execute(sql: "INSERT INTO quarantined_operations(id, body) VALUES (?, ?)", arguments: [frozen.mutation.operationID.uuidString, try Self.encode(frozen)])
                    stored.frozen = nil
                    stored.remote = stored.remote ?? stored.baseline
                    stored.conflictReason = "device_identity_changed"
                    stored.dirty = true
                    try write(stored, db: db)
                }
                metadata.deviceID = newDeviceID
                try Self.writeMetadata(metadata, db: db)
            }
        }
    }

    func snapshot() throws -> SyncStoreSnapshot {
        try database.read { db in
            SyncStoreSnapshot(
                pendingCount: try Int.fetchOne(db, sql: "SELECT COUNT(*) FROM documents WHERE pending = 1 AND conflicted = 0")!,
                conflictCount: try Int.fetchOne(db, sql: "SELECT COUNT(*) FROM documents WHERE conflicted = 1")!,
                changeSequence: try Self.readMetadata(db).changeSequence)
        }
    }

    /// 许可锁覆盖整个同步提交与通知；pause 失效许可后，排队中的旧回调不能落盘。
    private func withExecution<T>(_ execution: SyncExecutionLease?, _ body: () throws -> T) throws -> T {
        if let execution { return try execution.withValidity(body) }
        return try body()
    }

    private func removeObserver(_ id: UUID) { observers.removeValue(forKey: id) }

    private func transaction(_ body: (Database) throws -> Void) throws {
        try database.write { db in
            try body(db)
            var metadata = try Self.readMetadata(db)
            metadata.changeSequence += 1
            try Self.writeMetadata(metadata, db: db)
        }
        let value = try snapshot()
        for observer in observers.values { observer.yield(value) }
    }

    private func registered<P>(_ schema: SyncSchema<P>) throws {
        guard let registered = schemas[schema.kind] else { throw SyncError.unknownKind(schema.kind) }
        guard registered.maxPayloadBytes == schema.maxPayloadBytes else { throw SyncError.invalidConfiguration("schema configuration differs from registration") }
    }

    private func validatedPayload<P>(_ payload: P, schema: SyncSchema<P>) throws -> [String: SyncJSON] {
        try registered(schema)
        try schema.validate(payload)
        let data = try Self.encode(payload)
        guard case .object(var object) = try JSONDecoder().decode(SyncJSON.self, from: data), object["kind"] == nil else {
            throw SyncError.invalidPayload("payload must be an object without reserved kind")
        }
        object["kind"] = .string(schema.kind)
        try validatePayload(object)
        return object
    }

    private func validatePayload(_ payload: [String: SyncJSON]) throws {
        guard SyncWireValidation.validPayload(payload, deleted: false) else {
            throw SyncError.invalidPayload("invalid JSON or kind boundary")
        }
        guard let kind = kind(payload), let schema = schemas[kind] else {
            throw SyncError.unknownKind(kind(payload) ?? "<missing>")
        }
        let data = try Self.encode(payload)
        guard data.count <= schema.maxPayloadBytes else { throw SyncError.invalidPayload("payload byte limit exceeded") }
        var business = payload
        business.removeValue(forKey: "kind")
        try schema.validateData(Self.encode(business))
    }

    private func validateRecord(_ record: SyncRecord) throws {
        guard SyncWireValidation.validRecord(record) else {
            throw SyncError.protocolViolation("invalid record metadata")
        }
        if let payload = record.payload { try validatePayload(payload) }
    }

    /// 墓碑不带 kind；其他候选不得利用另一个已注册模型改变同一 UUID 的类型。
    private func validateKind(_ record: SyncRecord, for stored: StoredDocument) throws {
        guard record.deleted || stored.kind.isEmpty || kind(record.payload) == stored.kind else {
            throw SyncError.invalidPayload("remote kind changed")
        }
    }

    private func typed<P>(_ stored: StoredDocument, schema: SyncSchema<P>) throws -> SyncDocument<P> {
        guard stored.kind == schema.kind, let payload = stored.payload else { throw SyncError.invalidPayload("stored kind or payload mismatch") }
        try validatePayload(payload)
        var business = payload
        business.removeValue(forKey: "kind")
        return SyncDocument(id: stored.id, payload: try JSONDecoder().decode(P.self, from: Self.encode(business)))
    }

    private func kind(_ payload: [String: SyncJSON]?) -> String? {
        guard case .string(let value) = payload?["kind"] else { return nil }
        return value
    }

    private func read(_ id: UUID, db: Database) throws -> StoredDocument? {
        try Data.fetchOne(db, sql: "SELECT body FROM documents WHERE id = ?", arguments: [id.uuidString]).map(decodeStored)
    }

    private func decodeStored(_ data: Data) throws -> StoredDocument {
        let stored = try JSONDecoder().decode(StoredDocument.self, from: data)
        guard stored.deleted == (stored.payload == nil) else {
            throw SyncError.invalidPayload("stored tombstone and payload disagree")
        }
        if let payload = stored.payload { try validatePayload(payload) }
        if let baseline = stored.baseline {
            try validateRecord(baseline)
            try validateKind(baseline, for: stored)
        }
        if let remote = stored.remote {
            try validateRecord(remote)
            try validateKind(remote, for: stored)
        }
        return stored
    }

    private func write(_ stored: StoredDocument, db: Database) throws {
        try db.execute(sql: "INSERT INTO documents(id, kind, deleted, pending, conflicted, body) VALUES (?, ?, ?, ?, ?, ?) ON CONFLICT(id) DO UPDATE SET kind=excluded.kind, deleted=excluded.deleted, pending=excluded.pending, conflicted=excluded.conflicted, body=excluded.body",
                       arguments: [stored.id.uuidString, stored.kind, stored.deleted, stored.dirty || stored.frozen != nil, stored.conflictReason != nil, try Self.encode(stored)])
    }

    private func conflicted(_ id: UUID, db: Database) throws -> StoredDocument {
        guard let stored = try read(id, db: db), stored.conflictReason != nil, stored.frozen == nil else { throw SyncError.conflictNotFound }
        return stored
    }

    private func sameContent(_ stored: StoredDocument, _ record: SyncRecord) -> Bool {
        stored.deleted == record.deleted && stored.payload == record.payload
    }

    private func adopt(_ record: SyncRecord, into stored: inout StoredDocument) {
        stored.payload = record.payload
        stored.deleted = record.deleted
        stored.baseline = record
        stored.remote = nil
        stored.dirty = false
        stored.conflictReason = nil
    }

    private func reconcile(_ remote: SyncRecord, with stored: inout StoredDocument) {
        if sameContent(stored, remote) {
            adopt(remote, into: &stored)
        } else if let baseline = stored.baseline, baseline.deleted == remote.deleted, baseline.payload == remote.payload {
            stored.baseline = remote
            stored.remote = nil
            stored.conflictReason = nil
        } else {
            stored.remote = remote
            stored.conflictReason = "version_conflict"
        }
    }

    private static func encode<T: Encodable>(_ value: T) throws -> Data {
        let encoder = JSONEncoder()
        encoder.outputFormatting = [.sortedKeys]
        return try encoder.encode(value)
    }

    private static func readMetadata(_ db: Database) throws -> Metadata {
        guard let data = try Data.fetchOne(db, sql: "SELECT body FROM metadata WHERE id = 1") else { throw SyncError.protocolViolation("missing store metadata") }
        return try JSONDecoder().decode(Metadata.self, from: data)
    }

    private static func writeMetadata(_ metadata: Metadata, db: Database) throws {
        try db.execute(sql: "INSERT INTO metadata(id, body) VALUES (1, ?) ON CONFLICT(id) DO UPDATE SET body=excluded.body", arguments: [try encode(metadata)])
    }

    private static func validateScope(_ scope: SyncScope) throws {
        guard scope.backendURL.absoluteString.utf8.count <= 2048,
              let parts = URLComponents(url: scope.backendURL, resolvingAgainstBaseURL: false),
              let host = parts.host, !host.isEmpty, parts.user == nil, parts.password == nil,
              parts.query == nil, parts.fragment == nil,
              parts.scheme == "https" || (parts.scheme == "http" && ["localhost", "127.0.0.1", "[::1]", "::1"].contains(host)),
              !scope.appID.isEmpty, scope.appID.utf8.count <= 100 else {
            throw SyncError.invalidConfiguration("invalid backend URL or app ID")
        }
    }
}

/// 本地可见内容、共同基线、远端候选和不可变请求共存，不能用一份 JSON 覆盖全部状态。
private struct StoredDocument: Codable {
    let id: UUID
    var kind: String
    var payload: [String: SyncJSON]?
    var deleted = false
    var localRevision: Int64 = 0
    var dirty = false
    var baseline: SyncRecord?
    var remote: SyncRecord?
    var frozen: Frozen?
    var conflictReason: String?
}

/// 冻结时记录设备与本地 revision，确认后才能为后续编辑创建操作。
private struct Frozen: Codable {
    let mutation: SyncMutation
    let deviceID: UUID
    let localRevision: Int64
}

/// 元数据与正文共用事务；认证 token 永不落盘。
private struct Metadata: Codable {
    let scope: SyncScope
    var pullCursor: Int64 = 0
    var deviceID: UUID?
    var changeSequence: Int64 = 0
    var initialPullCompleted = false
}
