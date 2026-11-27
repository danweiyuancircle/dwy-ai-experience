# EToast

ID: designkit.mac.toast
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Show brief non-critical success feedback from an external message Binding.

## Capabilities
- Transient message — bound to an EToastMessage? and cleared automatically.
- Auto dismiss — dismissAfter defaults to two seconds; replacing the message restarts the timer.
- Verbatim or localized — EToastMessage(verbatim:) for runtime text.
- Announcement — the message is announced to assistive technology; dismissTitle names the dismiss action.

## Parameters, state and constraints
Two-second dismissal pauses for hover, focus and VoiceOver; replacements and teardown cancel old work. Important failures belong in ENotice. Each repeated message has a new identity.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
