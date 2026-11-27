# EForm

ID: designkit.mac.form
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Keep form content scrollable while its action area remains reachable.

## Capabilities
- Content plus actions — two slots: fields on top, action buttons below.
- Group spacing — spacing comes from the theme group role.
- State owned by caller — validation and submit state are passed in by the host.

## Parameters, state and constraints
The host owns validation, Enter/Escape behavior, save and cancel. Avoid nesting an unbounded full-page form in another fixed-height form.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
