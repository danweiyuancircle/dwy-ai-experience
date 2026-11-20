import 'package:cupertino_ui/cupertino_ui.dart';

import 'tokens.dart';

/// Brand settings shared by the theme and the official Cupertino controls.
@immutable
class DwyBrand {
  const DwyBrand({this.primary = CupertinoColors.systemBlue, this.fontFamily});

  final Color primary;
  final String? fontFamily;
}

/// Installs the Cupertino defaults and exposes geometry shared by DWY widgets.
abstract final class DwyTheme {
  /// Pass to CupertinoApp.theme. Omit brightness to follow the system.
  static CupertinoThemeData create({
    Brightness? brightness,
    DwyBrand brand = const DwyBrand(),
  }) {
    final theme = CupertinoThemeData(
      brightness: brightness,
      primaryColor: brand.primary,
      scaffoldBackgroundColor: CupertinoColors.systemGroupedBackground,
    );
    final font = brand.fontFamily;
    if (font == null) return theme;
    final text = theme.textTheme;
    return theme.copyWith(
      textTheme: text.copyWith(
        textStyle: text.textStyle.copyWith(fontFamily: font),
        actionTextStyle: text.actionTextStyle.copyWith(fontFamily: font),
        actionSmallTextStyle: text.actionSmallTextStyle.copyWith(
          fontFamily: font,
        ),
        tabLabelTextStyle: text.tabLabelTextStyle.copyWith(fontFamily: font),
        navTitleTextStyle: text.navTitleTextStyle.copyWith(fontFamily: font),
        navLargeTitleTextStyle: text.navLargeTitleTextStyle.copyWith(
          fontFamily: font,
        ),
        navActionTextStyle: text.navActionTextStyle.copyWith(fontFamily: font),
        pickerTextStyle: text.pickerTextStyle.copyWith(fontFamily: font),
        dateTimePickerTextStyle: text.dateTimePickerTextStyle.copyWith(
          fontFamily: font,
        ),
      ),
    );
  }

  /// Place in CupertinoApp.builder to share geometry with pages and overlays.
  static Widget withTokens({
    required DwyTokens tokens,
    required Widget child,
  }) => _DwyTokenScope(tokens: tokens, child: child);

  /// Reads the nearest geometry overrides or the standard DWY dimensions.
  static DwyTokens tokensOf(BuildContext context) =>
      context.dependOnInheritedWidgetOfExactType<_DwyTokenScope>()?.tokens ??
      const DwyTokens();
}

class _DwyTokenScope extends InheritedWidget {
  const _DwyTokenScope({required this.tokens, required super.child});

  final DwyTokens tokens;

  @override
  bool updateShouldNotify(_DwyTokenScope oldWidget) =>
      tokens != oldWidget.tokens;
}
