import SwiftUI
import DesignKitIOS

/// 独立公开产品消费示例，不依赖 ADBox、MacUI 或业务服务。
@main
struct IOSControlsApp: App {
    var body: some Scene { WindowGroup { IOSControlsShowcase() } }
}

private struct IOSControlsShowcase: View {
    @State private var theme = ThemeManager.shared
    @State private var useAlternateBrand = false
    @State private var noticeCenter = ENoticeCenter()
    @State private var name = ""
    @State private var password = ""
    @State private var search = ""
    @State private var enabled = true
    @State private var busy = false
    @State private var actionCount = 0
    @State private var selected: Int? = nil
    @State private var segment = 0
    @State private var showThirdOption = true
    @State private var failure = false
    @State private var phase = ETaskPhase.running
    @State private var progress = 0.25
    @State private var contentState = EContentState.empty
    @FocusState private var nameFocused: Bool

    var body: some View {
        NavigationStack {
            EForm {
                appearance
                controls
                selection
                fields
                feedback
                combinations
            }
            .navigationTitle("iOS Controls")
            .toolbar {
                ToolbarItemGroup(placement: .keyboard) {
                    Spacer()
                    Button("Done") { nameFocused = false }
                }
            }
            .safeAreaInset(edge: .bottom) {
                ENoticeHost(center: noticeCenter, dismissLabel: Text("Dismiss notice"))
                    .padding(.horizontal)
            }
        }
        .eControlTheme(useAlternateBrand ? alternateTheme : .standard)
        .preferredColorScheme(theme.preferredColorScheme)
        .onAppear { theme.applyOnLaunch() }
    }

    private var appearance: some View {
        ECard {
            VStack(alignment: .leading) {
                Text("Appearance").font(.headline)
                ESwitch(isOn: $useAlternateBrand) { Text("Alternate brand") }
                EActionGroup {
                    EButton("System") { theme.mode = .system }
                    EButton("Light") { theme.mode = .light }
                    EButton("Dark") { theme.mode = .dark }
                }
            }
        }
    }

    private var controls: some View {
        ECard {
            VStack(alignment: .leading) {
                Text("Actions").font(.headline)
                ESwitch(isOn: $busy) { Text("Busy state") }
                Text("Action count: \(actionCount)")
                    .accessibilityIdentifier("showcase.actionCount")
                    .accessibilityValue(Text(verbatim: String(actionCount)))
                EActionGroup {
                    EButton("Primary action", emphasis: .primary, isBusy: busy) {
                        actionCount += 1
                        noticeCenter.show(.transientSuccess("Action completed"))
                    }
                    .accessibilityIdentifier("showcase.primary")
                    EButton("Secondary action", isBusy: busy) {}
                    EButton("Tertiary action", emphasis: .tertiary) {}
                    EButton("Dangerous action", role: .destructive) {
                        noticeCenter.show(ENotice("No data was deleted", tone: .warning))
                    }
                    EButton("Disabled action") {}.disabled(true)
                }
                HStack {
                    EIconAction(accessibilityLabel: Text("Add item"), action: {}) { Image(systemName: "plus") }
                    EMenu {
                        Button("First action") { noticeCenter.show(.transientSuccess("First action completed")) }
                        Button("Disabled action") {}.disabled(true)
                        Divider()
                        Button("Dangerous action", role: .destructive) {}
                    } label: {
                        Label("More actions", systemImage: "ellipsis.circle")
                    }
                }
                EButton("Floating action", emphasis: .primary) {}
                    .eControlPlacement(.floating)
            }
        }
    }

    private var selection: some View {
        ECard {
            VStack(alignment: .leading) {
                Text("Selection").font(.headline)
                EPicker(selection: $selected) {
                    Text("No selection").tag(nil as Int?)
                    Text("First option").tag(1 as Int?)
                    Text("Disabled option").tag(2 as Int?).disabled(true)
                    if showThirdOption { Text("Third option").tag(3 as Int?) }
                } label: { Text("Choose an option") }
                ESwitch(isOn: $showThirdOption) { Text("Include third option") }
                if selected == 3 && !showThirdOption {
                    EInlineNotice(tone: .warning) { Text("The current option was removed. Choose another option.") } actions: { EmptyView() }
                }
                EPicker(selection: $segment, presentation: .segmented) {
                    Text("First").tag(0)
                    Text("Second").tag(1)
                } label: { Text("Segment") }
                .accessibilityIdentifier("showcase.segment")
                Text("Selected segment: \(segment)")
                    .accessibilityIdentifier("showcase.segmentValue")
                    .accessibilityValue(Text(verbatim: String(segment)))
            }
        }
    }

    private var fields: some View {
        VStack(alignment: .leading) {
            Text("Fields").font(.headline)
            EField(hint: Text("Whitespace is preserved"), error: failure ? Text("Enter a value before saving") : nil) {
                Text("Name")
            } content: {
                ETextField(Text("Name"), text: $name, isInvalid: failure)
                    .focused($nameFocused)
                    .submitLabel(.done)
                    .onSubmit { nameFocused = false }
                    .accessibilityIdentifier("showcase.name")
            }
            Text(verbatim: name)
                .accessibilityIdentifier("showcase.nameValue")
            ESecureField(Text("Password"), text: $password).textContentType(.newPassword)
            ESearchField(Text("Search"), text: $search, clearLabel: Text("Clear search"))
            ETextField(Text("Read only"), text: .constant("Original value")).disabled(true)
            EActionGroup {
                EButton("Save", emphasis: .primary) {
                    nameFocused = false
                    failure = name.isEmpty
                    if !failure { noticeCenter.show(.transientSuccess("Saved")) }
                }
                EButton("Cancel") { nameFocused = false }
            }
        }
    }

    private var feedback: some View {
        ECard {
            VStack(alignment: .leading) {
                Text("Feedback").font(.headline)
                ForEach(EStatusTone.allCases, id: \.self) { tone in
                    EStatusBadge(Text(verbatim: tone.rawValue), tone: tone)
                }
                EButton("Show persistent error") { noticeCenter.show(ENotice("An error remains readable until dismissed", tone: .error)) }
                EButton("Replace with success") { noticeCenter.show(.transientSuccess("Saved")) }
                taskProgress
                Slider(value: $progress, in: 0...1)
                EButton("Confirm cancellation") { phase = .cancelled }
                EButton("Restart task") { phase = .running }
                ETaskProgress(title: Text("Indeterminate task"), phase: .running)
            }
        }
    }

    private var combinations: some View {
        ECard {
            VStack(alignment: .leading) {
                Text("Compositions").font(.headline)
                ESettingsRow(detail: Text("Changes remain local to this demonstration")) { Text("Preference") } content: {
                    ESwitch(isOn: $enabled) { Text("Enabled") }
                }
                ELabelValue { Text("Original text") } value: { Text(verbatim: name) }
                EPicker(selection: $contentState) {
                    Text("Idle").tag(EContentState.idle)
                    Text("Loading").tag(EContentState.loading)
                    Text("Success").tag(EContentState.success)
                    Text("Empty").tag(EContentState.empty)
                    Text("Failure").tag(EContentState.failure)
                } label: { Text("Content state") }
                EStateView(state: contentState, title: Text("Explicit content state"), detail: Text("The component never infers success from the data")) {
                    EButton("Retry") { contentState = .loading }
                }
            }
        }
    }

    private var taskTitle: Text {
        switch phase {
        case .running: Text("Task is running")
        case .cancelling: Text("Cancellation requested")
        case .cancelled: Text("Task was cancelled")
        case .succeeded: Text("Task succeeded")
        case .failed: Text("Task failed")
        }
    }

    @ViewBuilder private var taskProgress: some View {
        switch Result(catching: { try EProgressValue(fraction: progress) }) {
        case .success(let value):
            ETaskProgress(title: taskTitle, phase: phase, progress: value, cancel: {
                phase = .cancelling
            }) { Text("Cancel task") }
        case .failure:
            EStateView(state: .failure, title: Text("Invalid progress"))
        }
    }

    private var alternateTheme: EControlTheme {
        EControlTheme(accent: EAccentColors(
            light: .indigo, onLight: .white, dark: .cyan, onDark: .black,
            highContrastLight: .black, onHighContrastLight: .white,
            highContrastDark: .white, onHighContrastDark: .black
        ))
    }
}
