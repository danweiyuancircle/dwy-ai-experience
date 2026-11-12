# EIconAction

ID: designkit.mac.icon-action
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.2

## Purpose
Use a named icon action when surrounding context makes its purpose clear.

## Parameters, state and constraints
Provide a meaningful title for VoiceOver and help. SF Symbols and custom image labels remain caller owned.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
