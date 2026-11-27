#if os(macOS)
import Foundation
import Observation
import PurchaseCore
import StoreKit

@MainActor
@Observable
final class MacPaywallFlow {
    enum Operation { case idle, loading, buying, restoring }
    enum Notice { case pending, noPurchases, unconfirmed, failed(String) }

    private(set) var operation = Operation.idle
    private(set) var notice: Notice?
    private(set) var pendingProductID: String?
    @ObservationIgnored private var session = 0
    @ObservationIgnored private var isPresented = false
    @ObservationIgnored private var unlocked = Set<String>()

    @discardableResult
    func begin() -> Int {
        session &+= 1
        isPresented = true
        operation = .idle
        notice = nil
        pendingProductID = nil
        unlocked = []
        return session
    }

    func dismissed() -> Set<String> {
        deactivate(session)
        return takeUnlocked()
    }

    func takeUnlocked() -> Set<String> {
        defer { unlocked = [] }
        return unlocked
    }

    func isCurrent(_ session: Int?) -> Bool {
        isPresented && self.session == session
    }

    func deactivate(_ presentation: Int?) {
        guard isCurrent(presentation) else { return }
        session &+= 1
        isPresented = false
    }

    func load(store: MacPaywallStore) async {
        guard isPresented, operation == .idle else { return }
        let session = self.session
        operation = .loading
        defer { if self.session == session { operation = .idle } }
        if pendingProductID == nil { notice = nil }
        do { try await store.load() }
        catch {
            guard self.session == session, !Task.isCancelled else { return }
            notice = .failed(error.localizedDescription)
        }
    }

    func buy(_ id: String, store: MacPaywallStore) async -> Bool {
        guard isPresented, operation == .idle, pendingProductID == nil, unlocked.isEmpty else { return false }
        let snapshot = store.snapshot()
        guard snapshot.prices[id] != nil, !snapshot.purchasedProductIDs.contains(id) else { return false }
        let session = self.session
        operation = .buying
        notice = nil
        defer { if self.session == session { operation = .idle } }
        do {
            let result = try await store.purchase(id)
            guard self.session == session else { return false }
            switch result {
            case .purchased:
                if store.snapshot().purchasedProductIDs.contains(id) { return unlock([id]) }
                notice = .unconfirmed
            case .pending:
                if store.snapshot().purchasedProductIDs.contains(id) { return unlock([id]) }
                pendingProductID = id
                notice = .pending
            case .cancelled:
                break
            }
        } catch {
            guard self.session == session, !Task.isCancelled else { return false }
            notice = .failed(error.localizedDescription)
        }
        return false
    }

    func restore(configured: Set<String>, store: MacPaywallStore) async -> Bool {
        guard isPresented, operation == .idle, unlocked.isEmpty else { return false }
        let session = self.session
        operation = .restoring
        defer { if self.session == session { operation = .idle } }
        do {
            try await store.restore()
            guard self.session == session else { return false }
            let restored = store.snapshot().purchasedProductIDs.intersection(configured)
            if !restored.isEmpty { return unlock(restored) }
            notice = pendingProductID == nil ? .noPurchases : .pending
        } catch StoreKitError.userCancelled {
            return false
        } catch {
            guard self.session == session, !Task.isCancelled else { return false }
            notice = .failed(error.localizedDescription)
        }
        return false
    }

    func confirmPending(_ purchased: Set<String>) -> Bool {
        guard isPresented, operation == .idle, let pendingProductID, purchased.contains(pendingProductID) else { return false }
        return unlock([pendingProductID])
    }

    private func unlock(_ ids: Set<String>) -> Bool {
        guard unlocked.isEmpty else { return false }
        pendingProductID = nil
        unlocked = ids
        return true
    }
}
#endif
