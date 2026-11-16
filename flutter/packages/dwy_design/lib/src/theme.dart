import 'package:material_ui/material_ui.dart';

import 'tokens.dart';

/// App-owned branding; fonts must be bundled/configured by the consuming app.
@immutable
class DwyBrand {
  const DwyBrand({this.primary = const Color(0xFF2563EB), this.fontFamily});

  final Color primary;
  final String? fontFamily;
}

/// Builds both brightness variants from one brand. No dynamic wallpaper color.
/// Apps may override semantic colors here and component themes with copyWith.
abstract final class DwyTheme {
  static ThemeData create({
    required Brightness brightness,
    DwyBrand brand = const DwyBrand(),
    DwyTokens tokens = const DwyTokens(),
    ColorScheme? colorScheme,
  }) {
    final dark = brightness == Brightness.dark;
    final generated = ColorScheme.fromSeed(
      seedColor: brand.primary,
      brightness: brightness,
    );
    final primaryContrast = brand.primary.computeLuminance() > 0.179
        ? Colors.black
        : Colors.white;
    final scheme =
        colorScheme ??
        generated.copyWith(
          primary: dark ? generated.primary : brand.primary,
          onPrimary: dark ? generated.onPrimary : primaryContrast,
          surface: dark ? const Color(0xFF18212F) : Colors.white,
          onSurface: dark ? const Color(0xFFF1F5F9) : const Color(0xFF0F172A),
          onSurfaceVariant: dark
              ? const Color(0xFF94A3B8)
              : const Color(0xFF64748B),
          outlineVariant: dark
              ? const Color(0xFF334155)
              : const Color(0xFFE2E8F0),
        );
    final shape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(tokens.controlRadius),
    );
    final base = ThemeData(
      useMaterial3: true,
      brightness: brightness,
      colorScheme: scheme,
      fontFamily: brand.fontFamily,
      scaffoldBackgroundColor: dark
          ? const Color(0xFF0F172A)
          : const Color(0xFFF8FAFC),
      visualDensity: VisualDensity.standard,
      materialTapTargetSize: MaterialTapTargetSize.padded,
      extensions: <ThemeExtension<dynamic>>[tokens],
    );
    return base.copyWith(
      textTheme: base.textTheme.copyWith(
        bodyLarge: base.textTheme.bodyLarge?.copyWith(fontSize: 16),
        bodyMedium: base.textTheme.bodyMedium?.copyWith(fontSize: 16),
      ),
      dividerTheme: DividerThemeData(
        color: scheme.outlineVariant,
        thickness: 1,
        space: 1,
      ),
      appBarTheme: AppBarTheme(
        backgroundColor: base.scaffoldBackgroundColor,
        foregroundColor: scheme.onSurface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        scrolledUnderElevation: 0,
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: Size(48, tokens.controlHeight),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: shape,
          textStyle: base.textTheme.labelLarge,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: Size(48, tokens.controlHeight),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: shape,
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          minimumSize: Size(48, tokens.controlHeight),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: shape,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: scheme.surface,
        contentPadding: const EdgeInsets.all(16),
        border: OutlineInputBorder(
          borderRadius: BorderRadius.circular(tokens.controlRadius),
          borderSide: BorderSide(color: scheme.outlineVariant),
        ),
        enabledBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(tokens.controlRadius),
          borderSide: BorderSide(color: scheme.outlineVariant),
        ),
        focusedBorder: OutlineInputBorder(
          borderRadius: BorderRadius.circular(tokens.controlRadius),
          borderSide: BorderSide(color: scheme.primary, width: 2),
        ),
      ),
    );
  }

  /// Requires a Theme created by DwyTheme; missing root configuration is an error.
  static DwyTokens tokensOf(BuildContext context) {
    final tokens = Theme.of(context).extension<DwyTokens>();
    if (tokens == null) {
      throw StateError('Install DwyTheme.create at the application root.');
    }
    return tokens;
  }
}
