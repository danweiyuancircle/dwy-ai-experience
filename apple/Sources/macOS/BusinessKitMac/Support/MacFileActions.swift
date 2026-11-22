#if os(macOS)
import AppKit
import DesignKitMac
import LogKit
import SwiftUI

/// 供系统分享或保存的文件。应用保有现有文件及沙盒访问的生命周期。
public enum MacFileExportSource: Sendable {
    case file(URL)
    /// 内存生成的图片、归档或文档应提供对应的文件扩展名。
    case data(Data)
}

/// 在原生分享菜单和系统保存框中导出同一份文件内容。
public struct MacFileActions: View {
    @Environment(\.eControlTheme) private var theme
    @Environment(\.locale) private var locale
    @State private var presenter = MacFileActionPresenter()
    private let prepare: @MainActor () async throws -> PreparedSupportFile

    /// 每次操作时才读取文件或生成数据。现有文件须保持可读，直到原生操作结束。
    public init(fileName: String, load: @escaping @MainActor () async throws -> MacFileExportSource) {
        prepare = {
            let source = try await load()
            return try await Task.detached(priority: .userInitiated) {
                try PreparedSupportFile.prepare(source, fileName: fileName)
            }.value
        }
    }

    private init(prepare: @escaping @MainActor () async throws -> PreparedSupportFile) {
        self.prepare = prepare
    }

    /// 用户发起操作后打包当前 AppLog 日志。应用须先初始化独立的日志目录。
    public static func logs(fileNamePrefix: String) -> Self {
        Self(prepare: {
            try await Task.detached(priority: .userInitiated) {
                try PreparedSupportFile.exportLogs(fileNamePrefix: fileNamePrefix)
            }.value
        })
    }

    public var body: some View {
        @Bindable var presenter = presenter
        HStack(spacing: theme.spacing.controlGroup) {
            EButton(action: { run(.share) }) {
                Label { supportText("Share") } icon: { Image(systemName: "square.and.arrow.up") }
            }
            .background(MacFileActionAnchor(presenter: presenter))
            EButton(action: { run(.save) }) {
                Label { supportText("Save As") } icon: { Image(systemName: "arrow.down.document") }
            }
            if presenter.busy {
                ProgressView().controlSize(.small).accessibilityLabel(supportText("Preparing file"))
            }
        }
        .disabled(presenter.busy)
        .eErrorAlert(title: localized("Export failed"), message: $presenter.errorMessage, dismissTitle: localized("OK"))
    }

    private func run(_ action: MacFileActionPresenter.Action) {
        Task { await presenter.perform(action, locale: locale, prepare: prepare) }
    }

    private func localized(_ key: String.LocalizationValue) -> String {
        String(localized: key, table: "Support", bundle: .module, locale: locale)
    }
}

enum SupportFileError: LocalizedError {
    case invalidName
    case notAFile
    case noWindow
    case noLogs
    case logExportFailed

    var errorDescription: String? { message(locale: .current) }

    func message(locale: Locale) -> String {
        let key: String.LocalizationValue = switch self {
        case .invalidName: "Enter a valid file name."
        case .notAFile: "This item is not a readable file."
        case .noWindow: "Open the export from a visible window."
        case .noLogs: "There are no logs to export."
        case .logExportFailed: "Unable to archive the logs."
        }
        return String(localized: key, table: "Support", bundle: .module, locale: locale)
    }
}

struct PreparedSupportFile: Sendable {
    let url: URL
    let suggestedName: String
    private let ownedDirectory: URL?

    static func prepare(_ source: MacFileExportSource, fileName: String) throws -> Self {
        try validate(fileName: fileName)
        switch source {
        case .file(let url):
            guard url.isFileURL, try url.resourceValues(forKeys: [.isRegularFileKey]).isRegularFile == true,
                  FileManager.default.isReadableFile(atPath: url.path) else {
                throw SupportFileError.notAFile
            }
            return Self(url: url, suggestedName: fileName, ownedDirectory: nil)
        case .data(let data):
            return try temporaryFile(named: fileName) { try data.write(to: $0, options: .atomic) }
        }
    }

    static func exportLogs(fileNamePrefix: String) throws -> Self {
        guard AppLog.directoryURL != nil else { throw SupportFileError.noLogs }
        let name = LogExport.makeFileName(prefix: fileNamePrefix) + ".zip"
        try validate(fileName: name)
        let archive: URL
        do {
            archive = try LogExport.exportZip(fileName: UUID().uuidString)
        } catch LogExport.ExportError.noLogs {
            throw SupportFileError.noLogs
        } catch LogExport.ExportError.zipFailed {
            throw SupportFileError.logExportFailed
        }
        defer { try? FileManager.default.removeItem(at: archive) }
        return try temporaryFile(named: name) { try FileManager.default.moveItem(at: archive, to: $0) }
    }

    func save(to destination: URL) throws {
        if url.standardizedFileURL == destination.standardizedFileURL { return }
        try Data(contentsOf: url, options: .mappedIfSafe).write(to: destination, options: .atomic)
    }

    func cleanUp() {
        if let ownedDirectory { try? FileManager.default.removeItem(at: ownedDirectory) }
    }

    private static func validate(fileName: String) throws {
        guard !fileName.trimmingCharacters(in: .whitespacesAndNewlines).isEmpty,
              fileName != ".", fileName != "..",
              fileName.rangeOfCharacter(from: CharacterSet(charactersIn: "/\\:\0")) == nil else {
            throw SupportFileError.invalidName
        }
    }

    private static func temporaryFile(named fileName: String, write: (URL) throws -> Void) throws -> Self {
        let directory = FileManager.default.temporaryDirectory.appendingPathComponent(UUID().uuidString, isDirectory: true)
        try FileManager.default.createDirectory(at: directory, withIntermediateDirectories: false)
        let url = directory.appendingPathComponent(fileName, isDirectory: false)
        let file = Self(url: url, suggestedName: fileName, ownedDirectory: directory)
        do {
            try write(url)
            return file
        } catch {
            file.cleanUp()
            throw error
        }
    }
}

@MainActor
@Observable
private final class MacFileActionPresenter {
    enum Action { case share, save }
    @ObservationIgnored weak var anchor: NSView?
    private(set) var busy = false
    var errorMessage: String?

    func perform(_ action: Action, locale: Locale, prepare: @MainActor () async throws -> PreparedSupportFile) async {
        guard !busy else { return }
        guard let anchor, let window = anchor.window, window.isVisible else {
            errorMessage = SupportFileError.noWindow.message(locale: locale)
            return
        }

        busy = true
        defer { busy = false }
        do {
            let file = try await prepare()
            defer { file.cleanUp() }
            guard anchor.window === window, window.isVisible else { throw SupportFileError.noWindow }
            switch action {
            case .share:
                try await withCheckedThrowingContinuation { continuation in
                    MacFileSharingSession(onFinish: { continuation.resume(with: $0) })
                        .present(file.url, relativeTo: anchor)
                }
            case .save:
                let panel = NSSavePanel()
                panel.nameFieldStringValue = file.suggestedName
                guard await panel.beginSheetModal(for: window) == .OK, let destination = panel.url else { return }
                try await Task.detached(priority: .userInitiated) { try file.save(to: destination) }.value
            }
        } catch let error as SupportFileError {
            errorMessage = error.message(locale: locale)
        } catch is CancellationError {
            return
        } catch let error as NSError where error.domain == NSCocoaErrorDomain && error.code == NSUserCancelledError {
            return
        } catch {
            errorMessage = error.localizedDescription
        }
    }
}

private struct MacFileActionAnchor: NSViewRepresentable {
    let presenter: MacFileActionPresenter

    func makeNSView(context: Context) -> NSView {
        let view = NSView()
        presenter.anchor = view
        return view
    }

    func updateNSView(_ nsView: NSView, context: Context) {
        presenter.anchor = nsView
    }
}

@MainActor
private final class MacFileSharingSession: NSObject, @MainActor NSSharingServicePickerDelegate, @MainActor NSSharingServiceDelegate {
    private var picker: NSSharingServicePicker?
    private var service: NSSharingService?
    private var onFinish: ((Result<Void, Error>) -> Void)?
    // AppKit 的两个 delegate 都是弱引用。即使视图消失，文件也须保留到服务结束。
    private var retainedSession: MacFileSharingSession?

    init(onFinish: @escaping (Result<Void, Error>) -> Void) { self.onFinish = onFinish }

    func present(_ url: URL, relativeTo anchor: NSView) {
        let picker = NSSharingServicePicker(items: [url])
        picker.delegate = self
        self.picker = picker
        retainedSession = self
        picker.show(relativeTo: anchor.bounds, of: anchor, preferredEdge: .minY)
    }

    func sharingServicePicker(_ sharingServicePicker: NSSharingServicePicker, delegateFor service: NSSharingService) -> (any NSSharingServiceDelegate)? {
        self.service = service
        return self
    }

    func sharingServicePicker(_ sharingServicePicker: NSSharingServicePicker, didChoose service: NSSharingService?) {
        if let service {
            self.service = service
            service.delegate = self
        } else {
            finish(.success(()))
        }
    }

    func sharingService(_ sharingService: NSSharingService, didShareItems items: [Any]) {
        if sharingService === service { finish(.success(())) }
    }

    func sharingService(_ sharingService: NSSharingService, didFailToShareItems items: [Any], error: Error) {
        if sharingService === service { finish(.failure(error)) }
    }

    private func finish(_ result: Result<Void, Error>) {
        let callback = onFinish
        onFinish = nil
        picker = nil
        service = nil
        retainedSession = nil
        callback?(result)
    }
}
#endif
