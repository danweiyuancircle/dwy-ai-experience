# EButton

ID: designkit.mac.button
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Trigger an explicit action with native primary, secondary, plain, destructive, busy and disabled semantics.

## Capabilities
- Emphasis — primary, secondary or plain; the style follows the control placement (content, toolbar, floating glass).
- Role — ButtonRole.destructive switches the tint to the danger color.
- Busy — isBusy shows a small spinner and disables only this button.
- Custom label — a ViewBuilder label accepts SF Symbols or images; icon-only labels need an accessibility name.

## Parameters, state and constraints
The caller owns execution, errors and completion. Busy blocks only this button; the fixture increments a local count.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
