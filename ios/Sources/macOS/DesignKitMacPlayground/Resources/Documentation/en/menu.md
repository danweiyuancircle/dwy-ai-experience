# EMenu

ID: designkit.mac.menu
Module: DesignKitMac
Platform: macOS 26.0+
Package: 0.8.0-beta.5

## Purpose
Present actions, grouped items and native toggle semantics.

## Parameters, state and constraints
Opening or cancelling a menu must not execute actions. Do not nest a Button inside the trigger label or use this as a replacement for Picker.

Icons are optional and owned by the caller: use a native Button with a Label and SF Symbol for an icon, or Text for a text-only item. EMenu applies titleAndIcon to the native Menu as its default label strategy so supplied Label icons, including grouped and submenu items, remain visible on macOS 27; it does not invent icons for Text. Trigger labels follow the caller's Label or Text and can use a more local labelStyle override, such as iconOnly. Trigger and item labels remain independent: a text trigger can open icon items, and an icon-and-text trigger can open text items. Native selection marks, Toggle state, submenu arrows, disabled items and destructive roles stay with the system.

The fixture offers three triggers: text-only, icon items with a text trigger, and mixed grouped content with an icon-and-text trigger. The mixed menu also includes Toggle, a submenu, disabled and destructive actions. Stable trigger IDs end in menu.text-only, menu.with-icons and menu.trigger; actions update only the visible local count or Boolean Binding.

The fixture owns only local @State and resets on component changes or reset. Its bundle parameter defaults to .main; the catalog explicitly injects its own resource bundle. Copy into an app or resource-bearing SwiftPM consumer. Preview settings live in one window-level popover and persist while switching components, affecting only the preview subtree. System information and full documentation/code start collapsed.

## Validation status and known limits
Available: compiled fixtures use public APIs. Requires host capabilities: windows, keyboard and accessibility. Resource/source consistency is checked automatically. macOS 26 foreground interaction, IME, VoiceOver, dynamic materials and cross-window edges require separate acceptance; displayed state is not business success.
