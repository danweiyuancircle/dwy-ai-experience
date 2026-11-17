#if os(macOS)
import Foundation

@available(macOS 13.0, *)
public struct FullDiskAccessPermissionStatusProvider: PermissionStatusProviding {
    // DWY patch: readable paths cannot prove FDA; avoid probing unrelated users' private data.
    public var capability: PermissionStatusCapability { .unsupported }
    public func authorizationState() -> PermissionAuthorizationState { .unknown }
    public init() {}
}
#endif
