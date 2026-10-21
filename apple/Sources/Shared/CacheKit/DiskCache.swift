import Foundation

/// 统一文件缓存层（业务无关、可复用）。
///
/// 通用 key-value 磁盘缓存：业务层注入 `namespace` + `key` + `cacheKey`，
/// 本层不认识任何业务类型。目录布局：`<root>/<cacheKey>/<namespace>/<base64url(key)>`。
/// 纯 `FileManager`，注入 `root` 即可命令行测试。
public struct DiskCache: Sendable {
    /// 缓存层错误。读不存在不算错误（返回 nil）；编解码/IO 失败透传。
    public enum CacheError: LocalizedError {
        case encode(String)
        case decode(String)
        case io(String)

        public var errorDescription: String? {
            switch self {
            case let .encode(m): "缓存编码失败：\(m)"
            case let .decode(m): "缓存解码失败：\(m)"
            case let .io(m): "缓存读写失败：\(m)"
            }
        }
    }

    private let root: URL

    /// 缓存根目录，供同根其它存储复用。
    public var rootURL: URL { root }

    private var fm: FileManager { .default }

    /// - Parameter root: 缓存根目录。默认应用 Documents 下的 `Cache`。
    public init(root: URL? = nil) {
        if let root {
            self.root = root
        } else {
            let docs = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
            self.root = docs.appendingPathComponent("Cache", isDirectory: true)
        }
    }

    // MARK: - Codable JSON

    /// 存 Codable 值为 JSON。
    public func save<T: Encodable>(_ value: T, namespace: String, key: String, cacheKey: String) throws {
        let data: Data
        do {
            data = try JSONEncoder().encode(value)
        } catch {
            throw CacheError.encode(error.localizedDescription)
        }
        try writeData(data, namespace: namespace, key: key, cacheKey: cacheKey)
    }

    /// 读 JSON 解码为 T。文件不存在返回 nil；存在但解码失败抛 `.decode`。
    public func load<T: Decodable>(_ type: T.Type, namespace: String, key: String, cacheKey: String) throws -> T? {
        guard let data = loadData(namespace: namespace, key: key, cacheKey: cacheKey) else { return nil }
        do {
            return try JSONDecoder().decode(T.self, from: data)
        } catch {
            throw CacheError.decode(error.localizedDescription)
        }
    }

    // MARK: - 二进制

    public func saveData(_ data: Data, namespace: String, key: String, cacheKey: String) throws {
        try writeData(data, namespace: namespace, key: key, cacheKey: cacheKey)
    }

    public func loadData(namespace: String, key: String, cacheKey: String) -> Data? {
        let url = fileURL(namespace: namespace, key: key, cacheKey: cacheKey)
        return try? Data(contentsOf: url)
    }

    // MARK: - 查询与清理

    public func hasCache(cacheKey: String) -> Bool {
        let dir = root.appendingPathComponent(cacheKey, isDirectory: true)
        var isDir: ObjCBool = false
        guard fm.fileExists(atPath: dir.path, isDirectory: &isDir), isDir.boolValue else { return false }
        let contents = (try? fm.contentsOfDirectory(atPath: dir.path)) ?? []
        return !contents.isEmpty
    }

    public func clear(cacheKey: String) throws {
        let dir = root.appendingPathComponent(cacheKey, isDirectory: true)
        guard fm.fileExists(atPath: dir.path) else { return }
        do {
            try fm.removeItem(at: dir)
        } catch {
            throw CacheError.io(error.localizedDescription)
        }
    }

    // MARK: - 私有

    private func writeData(_ data: Data, namespace: String, key: String, cacheKey: String) throws {
        let url = fileURL(namespace: namespace, key: key, cacheKey: cacheKey)
        do {
            try fm.createDirectory(at: url.deletingLastPathComponent(), withIntermediateDirectories: true)
            try data.write(to: url, options: .atomic)
        } catch {
            throw CacheError.io(error.localizedDescription)
        }
    }

    private func fileURL(namespace: String, key: String, cacheKey: String) -> URL {
        root
            .appendingPathComponent(cacheKey, isDirectory: true)
            .appendingPathComponent(namespace, isDirectory: true)
            .appendingPathComponent(base64url(key))
    }

    private func base64url(_ s: String) -> String {
        Data(s.utf8).base64EncodedString()
            .replacingOccurrences(of: "+", with: "-")
            .replacingOccurrences(of: "/", with: "_")
            .replacingOccurrences(of: "=", with: "")
    }
}
