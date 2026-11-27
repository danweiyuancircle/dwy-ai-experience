# ETextField

ID: designkit.mac.text-field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Edit a single line while preserving native input, submit and focus behavior.

## Capabilities
- Single-line text — plain text field inside the shared field chrome.
- Title as placeholder — the title is both placeholder and accessibility name.
- Rich title — accepts LocalizedStringResource or Text.

## Parameters, state and constraints
No trim, case conversion, history or business validation occurs. The fixture displays verbatim Binding text and a submit count; marked text must remain intact.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
