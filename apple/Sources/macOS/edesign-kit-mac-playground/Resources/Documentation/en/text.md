# EText

ID: designkit.mac.text
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Show text with a semantic role (body, secondary, caption, title, section title, page title, monospaced) instead of raw system fonts and .secondary colors.

## Capabilities
- Seven roles — body, secondary, caption, title, sectionTitle, pageTitle and monospaced.
- Tone override — tone (EStatusTone) replaces the role color for status text.
- Modifier form — .eText(_:tone:) applies a role to Label or any view.
- Three initializers — Text, LocalizedStringResource and verbatim.

## Parameters, state and constraints
Fonts come from ETypography and colors from ESemanticColors through the injected eControlTheme. tone reuses EStatusTone and overrides the role color; status must still carry readable text. .eText(_:tone:) applies the same role to Label or any other view.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
