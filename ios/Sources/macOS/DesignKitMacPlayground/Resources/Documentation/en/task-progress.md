# ETaskProgress

ID: designkit.mac.task-progress
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.2

## Purpose
Display determinate or indeterminate external task progress and explicit actions.

## Parameters, state and constraints
Validate finite fractions in 0...1 with EProgressFraction. Requesting cancellation is not completion; the fixture waits for a separate confirmation and starts no real task.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
