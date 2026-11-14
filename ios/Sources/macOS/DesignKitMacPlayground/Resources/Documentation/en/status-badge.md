# EStatusBadge

ID: designkit.mac.status-badge
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.6

## Purpose
Present neutral, success, warning and failure with text plus an icon.

## Parameters, state and constraints
The badge does not infer business success and is not an action. Never rely on color alone or replace danger with brand accent.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
