# ENotice

ID: designkit.mac.notice
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Keep important information or failure readable until replaced by the caller.

## Capabilities
- Tones — neutral, success, warning and failure.
- Adaptive layout — actions sit beside the text when wide and wrap below when narrow.
- Actions slot — optional ViewBuilder actions such as dismiss or retry.

## Parameters, state and constraints
Persistent and non-modal. Actions remain explicit and do not disable unrelated controls.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
