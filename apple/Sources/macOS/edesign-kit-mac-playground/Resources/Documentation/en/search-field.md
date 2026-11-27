# ESearchField

ID: designkit.mac.search-field
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.11.0

## Purpose
Edit and clear the current search Binding.

## Capabilities
- Search chrome — uses the taller searchHeight from the theme.
- Clear action — requires a localized clearTitle for the clear button's accessibility name.
- Rich title — accepts LocalizedStringResource or Text.

## Parameters, state and constraints
Clear removes only the current text. The component never deletes history, starts a network request or implicitly submits.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
