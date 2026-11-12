# ELabelValue

ID: designkit.mac.label-value
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.5

## Purpose
Display a readable, selectable static value next to its meaning.

## Parameters, state and constraints
Use Text(verbatim:) for user or protocol content. Formatting and confidentiality belong to the caller.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
