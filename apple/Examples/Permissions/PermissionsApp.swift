import SwiftUI
import UniformTypeIdentifiers
import PermissionCore
import PermissionUI
#if os(iOS)
import PermissionIOS
import PermissionCameraIOS
import DesignKitIOS
#else
import PermissionMac
import DesignKitMac
#endif

/// 仓库开发示例；所有请求只在按钮点击后开始，不修改或重置既有系统授权。
@main
struct PermissionsApp: App {
    var body: some Scene {
        WindowGroup { PermissionsDemo() }
    }
}

@MainActor
private struct PermissionsDemo: View {
    @State private var message = "尚未请求权限 / No request yet"
    @State private var pickingFile = false
    #if os(macOS)
    @State private var permissions = MacPermissions()
    #endif

    var body: some View {
        ScrollView {
            VStack(alignment: .leading, spacing: 16) {
                Text("权限示例 / Permissions").font(.title)
                Text(verbatim: message).textSelection(.enabled)
                EButton {
                    Task {
                        do {
                            #if os(iOS)
                            let state = try await IOSPermissions.camera.request()
                            #else
                            let state = try await permissions.request(.camera)
                            #endif
                            message = state.rawValue
                        } catch { message = error.localizedDescription }
                    }
                } label: { Text("申请相机 / Request camera") }
                EButton { pickingFile = true } label: { Text("选择文件 / Choose file") }
                PermissionExplanation(
                    title: "权限不可用 / Permission unavailable",
                    message: "拒绝后可打开设置，返回后重新检查。打开设置本身不代表允许。",
                    settingsTitle: "打开设置 / Open Settings", retryTitle: "重新检查 / Refresh",
                    openSettings: {
                        #if os(iOS)
                        let opened = await IOSPermissions.openSettings()
                        #else
                        let opened = permissions.openSettings(for: .camera)
                        #endif
                        if !opened { message = "无法打开设置 / Settings unavailable" }
                    }, retry: {
                        #if os(iOS)
                        do { message = try await IOSPermissions.camera.status().rawValue }
                        catch { message = error.localizedDescription }
                        #else
                        message = permissions.status(for: .camera).rawValue
                        #endif
                    }
                )
            }.padding()
        }
        .fileImporter(isPresented: $pickingFile, allowedContentTypes: [.data]) { result in
            do {
                let url = try result.get()
                let count = try FileAccessScope().withAccess(to: url) { selected in
                    let handle = try FileHandle(forReadingFrom: selected)
                    do {
                        let count = try handle.read(upToCount: 1)?.count ?? 0
                        try handle.close()
                        return count
                    } catch {
                        try? handle.close()
                        throw error
                    }
                }
                message = "读取文件首字节数 / First bytes read: \(count)"
            } catch { message = error.localizedDescription }
        }
        #if os(macOS)
        .onDisappear { permissions.closeGuide() }
        #endif
    }
}
