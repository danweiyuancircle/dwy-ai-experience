# ECard

ID: designkit.mac.card
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Group content on a semantic opaque surface.

## Capabilities
- Surface container — theme surface fill with the card radius and card inset.
- Full width — stretches to the available width, content aligned leading.
- No navigation or glass — the card does not own navigation or glass effects.

## Parameters, state and constraints
A content card is not a glass control or a navigation action. Supply any actions explicitly.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
