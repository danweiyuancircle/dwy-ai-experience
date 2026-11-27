# EContentState

ID: designkit.mac.content-state
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Present an explicit idle, loading, empty, failure or success result.

## Capabilities
- Five phases — idle, loading, empty, failure and success.
- Title, detail and symbol — optional detail text and SF Symbol.
- Actions slot — a ViewBuilder for retry or follow-up actions.

## Parameters, state and constraints
The caller supplies phase and retry actions. Empty data is not proof of success or loading; no automatic retry occurs.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
