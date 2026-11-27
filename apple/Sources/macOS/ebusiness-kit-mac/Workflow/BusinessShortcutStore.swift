#if os(macOS)
import Foundation
import Observation
import SwiftUI

/// 可保存的 macOS 键盘组合，保存字符而非当前键盘布局下的物理键位。
public struct BusinessShortcut: Codable, Hashable, Sendable {
    public struct Modifiers: OptionSet, Codable, Hashable, Sendable {
        public let rawValue: UInt8
        public init(rawValue: UInt8) { self.rawValue = rawValue }
        public static let control = Self(rawValue: 1 << 0)
        public static let option = Self(rawValue: 1 << 1)
        public static let shift = Self(rawValue: 1 << 2)
        public static let command = Self(rawValue: 1 << 3)
    }

    public let key: String
    public let modifiers: Modifiers

    /// 录入要求 Command、Option 或 Control，避免将普通输入分配给业务命令。
    public init?(key: Character, modifiers: Modifiers) {
        let normalized = String(key).lowercased()
        let supported: Modifiers = [.control, .option, .shift, .command]
        guard normalized.count == 1, supported.isSuperset(of: modifiers),
              !modifiers.intersection([.control, .option, .command]).isEmpty
        else { return nil }
        self.key = normalized
        self.modifiers = modifiers
    }

    private enum CodingKeys: CodingKey { case key, modifiers }

    public init(from decoder: any Decoder) throws {
        let values = try decoder.container(keyedBy: CodingKeys.self)
        let key = try values.decode(String.self, forKey: .key)
        let modifiers = try values.decode(Modifiers.self, forKey: .modifiers)
        guard key.count == 1, let character = key.first, let shortcut = Self(key: character, modifiers: modifiers) else {
            throw DecodingError.dataCorruptedError(forKey: .key, in: values, debugDescription: "Invalid shortcut")
        }
        self = shortcut
    }

    /// 供宿主注册在 SwiftUI 命令或按钮上。全局注册由平台适配器完成。
    public var keyboardShortcut: KeyboardShortcut {
        var flags: EventModifiers = []
        if modifiers.contains(.control) { flags.insert(.control) }
        if modifiers.contains(.option) { flags.insert(.option) }
        if modifiers.contains(.shift) { flags.insert(.shift) }
        if modifiers.contains(.command) { flags.insert(.command) }
        return KeyboardShortcut(KeyEquivalent(Character(key)), modifiers: flags, localization: .withoutMirroring)
    }

    var keyCap: String {
        let title: String
        switch Character(key) {
        case KeyEquivalent.escape.character: title = "⎋"
        case KeyEquivalent.delete.character: title = "⌫"
        case KeyEquivalent.return.character: title = "↩"
        case KeyEquivalent.tab.character: title = "⇥"
        case KeyEquivalent.space.character: title = "␣"
        case KeyEquivalent.upArrow.character: title = "↑"
        case KeyEquivalent.downArrow.character: title = "↓"
        case KeyEquivalent.leftArrow.character: title = "←"
        case KeyEquivalent.rightArrow.character: title = "→"
        default: title = key.uppercased()
        }
        var prefix = ""
        if modifiers.contains(.control) { prefix += "⌃" }
        if modifiers.contains(.option) { prefix += "⌥" }
        if modifiers.contains(.shift) { prefix += "⇧" }
        if modifiers.contains(.command) { prefix += "⌘" }
        return prefix + title
    }

    var isSystemReserved: Bool {
        switch modifiers {
        case .command:
            ["q", "h", "m", "w", ",", " ", "\t", "`"].contains(key)
        case [.command, .shift]:
            key == "q" || ["3", "4", "5", "6"].contains(key)
        case [.command, .option]:
            key == String(KeyEquivalent.escape.character)
        case .control:
            key == " " || [
                KeyEquivalent.upArrow, .downArrow, .leftArrow, .rightArrow
            ].contains { key == String($0.character) }
        default: false
        }
    }
}

/// 用稳定 ID 定义一项可配置的应用命令，标题使用调用方解析的本地化文案。
public struct BusinessShortcutAction: Identifiable, Sendable {
    public enum Scope: Sendable { case application, global }
    public let id: String
    public let title: String
    public let scope: Scope
    public let defaultShortcut: BusinessShortcut?

    public init(id: String, title: String, scope: Scope = .application, defaultShortcut: BusinessShortcut? = nil) {
        self.id = id
        self.title = title
        self.scope = scope
        self.defaultShortcut = defaultShortcut
    }
}

/// 配置、录入与注册失败由设置页转为本地化提示。
public enum BusinessShortcutError: Error, Equatable, Sendable {
    case invalidConfiguration, unreadableSettings, unknownAction, reservedShortcut, conflict(String), globalRegistrationUnavailable
}

/// 应用拥有此实例。修改先验证和注册，成功后才发布并持久化新映射。
@MainActor
@Observable
public final class BusinessShortcutStore {
    public let actions: [BusinessShortcutAction]
    public private(set) var loadError: BusinessShortcutError?
    private var overrides: [String: Override] = [:]
    private let defaults: UserDefaults
    private let storageKey: String
    private let reserved: Set<BusinessShortcut>
    private let applyGlobal: (([String: BusinessShortcut]) throws -> Void)?

    private enum Override: Codable {
        case assigned(BusinessShortcut)
        case disabled
    }

    /// 全局适配器一次接收全部有效全局组合，失败须保留先前注册。调用方可补充系统及产品保留组合。
    public init(
        actions: [BusinessShortcutAction],
        defaults: UserDefaults = .standard,
        storageKey: String,
        reserved: Set<BusinessShortcut> = [],
        applyGlobal: (([String: BusinessShortcut]) throws -> Void)? = nil
    ) throws {
        guard !storageKey.isEmpty, Set(actions.map(\.id)).count == actions.count,
              actions.allSatisfy({ !$0.id.isEmpty })
        else { throw BusinessShortcutError.invalidConfiguration }
        self.actions = actions
        self.defaults = defaults
        self.storageKey = storageKey
        self.reserved = reserved
        self.applyGlobal = applyGlobal
        try validate(overrides)
        if defaults.object(forKey: storageKey) != nil {
            do {
                guard let data = defaults.data(forKey: storageKey) else { throw BusinessShortcutError.unreadableSettings }
                let saved = try JSONDecoder().decode([String: Override].self, from: data)
                try validate(saved)
                overrides = saved
            } catch {
                loadError = .unreadableSettings
            }
        }
    }

    public var canRegisterGlobalShortcuts: Bool { applyGlobal != nil }

    /// 应用启动并准备好全局动作回调后注册已保存组合。
    public func activateGlobalShortcuts() throws {
        if let loadError { throw loadError }
        try applyGlobal?(globalMapping(overrides))
    }

    /// 返回当前启用的组合。未知或显式停用的命令返回 nil。
    public func shortcut(for id: String) -> BusinessShortcut? {
        guard let action = actions.first(where: { $0.id == id }) else { return nil }
        return shortcut(for: action, overrides: overrides)
    }

    /// nil 显式停用命令，即使该命令有默认快捷键。
    public func assign(_ shortcut: BusinessShortcut?, to id: String) throws {
        if let loadError { throw loadError }
        guard let action = actions.first(where: { $0.id == id }) else { throw BusinessShortcutError.unknownAction }
        if action.scope == .global && applyGlobal == nil { throw BusinessShortcutError.globalRegistrationUnavailable }
        var edited = overrides
        edited[id] = shortcut.map(Override.assigned) ?? .disabled
        try commit(edited)
    }

    /// 恢复命令原始定义，其他命令仍保留用户配置。
    public func reset(_ id: String) throws {
        if let loadError { throw loadError }
        guard actions.contains(where: { $0.id == id }) else { throw BusinessShortcutError.unknownAction }
        var edited = overrides
        edited[id] = nil
        try commit(edited)
    }

    /// 显式恢复全部默认定义，也用于修复无法读取的保存数据。
    public func resetAll() throws {
        try commit([:])
        loadError = nil
    }

    private func shortcut(for action: BusinessShortcutAction, overrides: [String: Override]) -> BusinessShortcut? {
        switch overrides[action.id] {
        case .assigned(let shortcut): shortcut
        case .disabled: nil
        case nil: action.defaultShortcut
        }
    }

    private func validate(_ edited: [String: Override]) throws {
        var assigned: [BusinessShortcut: String] = [:]
        for action in actions {
            guard let shortcut = shortcut(for: action, overrides: edited) else { continue }
            if shortcut.isSystemReserved || reserved.contains(shortcut) {
                throw BusinessShortcutError.reservedShortcut
            }
            if let other = assigned.updateValue(action.title, forKey: shortcut) {
                throw BusinessShortcutError.conflict(other)
            }
        }
    }

    private func globalMapping(_ edited: [String: Override]) -> [String: BusinessShortcut] {
        actions.reduce(into: [:]) { mapping, action in
            if action.scope == .global { mapping[action.id] = shortcut(for: action, overrides: edited) }
        }
    }

    private func commit(_ edited: [String: Override]) throws {
        try validate(edited)
        let bytes = try JSONEncoder().encode(edited)
        let global = globalMapping(edited)
        if global != globalMapping(overrides) || loadError != nil { try applyGlobal?(global) }
        defaults.set(bytes, forKey: storageKey)
        overrides = edited
    }
}
#endif
