import 'package:cupertino_ui/cupertino_ui.dart';

/// Appearance selection for the Gallery app root.
enum GalleryThemeMode { system, light, dark }

/// App-level theme knobs that examples may read and change. Owned by
/// GalleryApp so the theme page can reconfigure the whole playground.
@immutable
class GallerySettings {
  const GallerySettings({
    required this.themeMode,
    required this.primary,
    required this.rounded,
    required this.customButtons,
    required this.onThemeMode,
    required this.onPrimary,
    required this.onRounded,
    required this.onCustomButtons,
  });

  final GalleryThemeMode themeMode;
  final Color primary;
  final bool rounded;
  final bool customButtons;
  final ValueChanged<GalleryThemeMode> onThemeMode;
  final ValueChanged<Color> onPrimary;
  final ValueChanged<bool> onRounded;
  final ValueChanged<bool> onCustomButtons;
}

/// Provides [GallerySettings] below CupertinoApp.builder so pushed routes and
/// sheets read the same values as the pages.
class GallerySettingsScope extends InheritedWidget {
  const GallerySettingsScope({
    required this.settings,
    required super.child,
    super.key,
  });

  final GallerySettings settings;

  static GallerySettings of(BuildContext context) => context
      .dependOnInheritedWidgetOfExactType<GallerySettingsScope>()!
      .settings;

  // Callbacks are recreated on every GalleryApp build, so compare values only.
  @override
  bool updateShouldNotify(GallerySettingsScope oldWidget) =>
      settings.themeMode != oldWidget.settings.themeMode ||
      settings.primary != oldWidget.settings.primary ||
      settings.rounded != oldWidget.settings.rounded ||
      settings.customButtons != oldWidget.settings.customButtons;
}
