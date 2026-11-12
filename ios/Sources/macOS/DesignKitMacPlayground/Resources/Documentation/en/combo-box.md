# EComboBox

ID: designkit.mac.combo-box
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.5

## Purpose
Edit raw text with native NSComboBox suggestions and explicit submission.

## Parameters, state and constraints
Suggestions are raw strings, deduplicated by text. Use a typed Picker for distinct objects with equal names. Editing-ended differs from commit; IME, keyboard and pop-up edges need foreground acceptance.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.

The native ComboBox uses EControlTheme.typography.nativeBodySize. The local larger-text preview updates both this native size and SwiftUI body typography. Actual glyph metrics, IME composition and focus still require foreground verification.
