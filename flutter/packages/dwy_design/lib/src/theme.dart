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
          primaryContainer: Color.alphaBlend(
            (dark ? generated.primary : brand.primary).withValues(alpha: 0.10),
            dark ? const Color(0xFF18212F) : Colors.white,
          ),
          onPrimaryContainer: generated.onPrimaryContainer,
          surface: dark ? const Color(0xFF18212F) : Colors.white,
          surfaceContainerLow: dark
              ? const Color(0xFF1E293B)
              : const Color(0xFFF1F5F9),
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
    final text = base.textTheme.copyWith(
      headlineLarge: base.textTheme.headlineLarge?.copyWith(
        fontSize: 28,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      headlineMedium: base.textTheme.headlineMedium?.copyWith(
        fontSize: 26,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      headlineSmall: base.textTheme.headlineSmall?.copyWith(
        fontSize: 24,
        fontWeight: FontWeight.w600,
        height: 1.3,
      ),
      titleLarge: base.textTheme.titleLarge?.copyWith(
        fontSize: 22,
        fontWeight: FontWeight.w600,
        height: 1.35,
      ),
      titleMedium: base.textTheme.titleMedium?.copyWith(
        fontSize: 17,
        fontWeight: FontWeight.w600,
        height: 1.4,
      ),
      titleSmall: base.textTheme.titleSmall?.copyWith(
        fontSize: 15,
        fontWeight: FontWeight.w600,
        height: 1.4,
      ),
      bodyLarge: base.textTheme.bodyLarge?.copyWith(fontSize: 16, height: 1.5),
      bodyMedium: base.textTheme.bodyMedium?.copyWith(
        fontSize: 16,
        height: 1.5,
      ),
      bodySmall: base.textTheme.bodySmall?.copyWith(fontSize: 13, height: 1.45),
      labelLarge: base.textTheme.labelLarge?.copyWith(
        fontSize: 15,
        fontWeight: FontWeight.w600,
        height: 1.4,
      ),
      labelMedium: base.textTheme.labelMedium?.copyWith(
        fontSize: 13,
        fontWeight: FontWeight.w500,
        height: 1.4,
      ),
      labelSmall: base.textTheme.labelSmall?.copyWith(
        fontSize: 12,
        fontWeight: FontWeight.w500,
        height: 1.4,
      ),
    );
    final groupShape = RoundedRectangleBorder(
      borderRadius: BorderRadius.circular(tokens.groupRadius),
    );
    return base.copyWith(
      textTheme: text,
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
        titleTextStyle: text.titleLarge?.copyWith(color: scheme.onSurface),
      ),
      cardTheme: CardThemeData(
        color: scheme.surface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        margin: EdgeInsets.zero,
        shape: groupShape,
      ),
      listTileTheme: ListTileThemeData(
        contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 4),
        minTileHeight: tokens.controlHeight,
        horizontalTitleGap: 12,
        iconColor: scheme.onSurfaceVariant,
        titleTextStyle: text.bodyLarge?.copyWith(color: scheme.onSurface),
        subtitleTextStyle: text.bodySmall?.copyWith(
          color: scheme.onSurfaceVariant,
        ),
        selectedColor: scheme.onPrimaryContainer,
        selectedTileColor: scheme.primaryContainer,
        shape: shape,
      ),
      navigationBarTheme: NavigationBarThemeData(
        backgroundColor: scheme.surface,
        surfaceTintColor: Colors.transparent,
        elevation: 0,
        height: 72,
        indicatorColor: scheme.primaryContainer,
        indicatorShape: shape,
        iconTheme: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.disabled)
              ? null
              : IconThemeData(
                  size: 24,
                  color: states.contains(WidgetState.selected)
                      ? scheme.onPrimaryContainer
                      : scheme.onSurfaceVariant,
                ),
        ),
        labelTextStyle: WidgetStateProperty.resolveWith(
          (states) => states.contains(WidgetState.disabled)
              ? null
              : text.labelSmall!.copyWith(
                  color: states.contains(WidgetState.selected)
                      ? scheme.onPrimaryContainer
                      : scheme.onSurfaceVariant,
                ),
        ),
      ),
      segmentedButtonTheme: SegmentedButtonThemeData(
        style: ButtonStyle(
          minimumSize: WidgetStatePropertyAll(Size(48, tokens.controlHeight)),
          shape: WidgetStatePropertyAll(shape),
          side: WidgetStateProperty.resolveWith(
            (states) => BorderSide(
              color: states.contains(WidgetState.focused)
                  ? scheme.primary
                  : scheme.outlineVariant,
            ),
          ),
          textStyle: WidgetStatePropertyAll(text.labelMedium),
          backgroundColor: WidgetStateProperty.resolveWith(
            (states) => states.contains(WidgetState.selected)
                ? scheme.primaryContainer
                : scheme.surface,
          ),
          foregroundColor: WidgetStateProperty.resolveWith((states) {
            if (states.contains(WidgetState.disabled)) {
              return scheme.onSurface.withValues(alpha: 0.38);
            }
            return states.contains(WidgetState.selected)
                ? scheme.onPrimaryContainer
                : scheme.onSurfaceVariant;
          }),
        ),
      ),
      chipTheme: ChipThemeData(
        backgroundColor: scheme.surfaceContainerLow,
        selectedColor: scheme.primaryContainer,
        secondarySelectedColor: scheme.primaryContainer,
        checkmarkColor: scheme.onPrimaryContainer,
        side: BorderSide.none,
        shape: shape,
        labelStyle: text.labelMedium,
        secondaryLabelStyle: text.labelMedium?.copyWith(
          color: scheme.onPrimaryContainer,
        ),
        padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 8),
      ),
      dialogTheme: DialogThemeData(
        backgroundColor: scheme.surface,
        surfaceTintColor: Colors.transparent,
        shape: groupShape,
        titleTextStyle: text.titleLarge?.copyWith(color: scheme.onSurface),
        contentTextStyle: text.bodyMedium?.copyWith(
          color: scheme.onSurfaceVariant,
        ),
      ),
      filledButtonTheme: FilledButtonThemeData(
        style: FilledButton.styleFrom(
          minimumSize: Size(48, tokens.controlHeight),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: shape,
          textStyle: text.labelLarge,
        ),
      ),
      outlinedButtonTheme: OutlinedButtonThemeData(
        style: OutlinedButton.styleFrom(
          minimumSize: Size(48, tokens.controlHeight),
          padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
          shape: shape,
          textStyle: text.labelLarge,
          side: BorderSide(color: scheme.outlineVariant),
        ),
      ),
      textButtonTheme: TextButtonThemeData(
        style: TextButton.styleFrom(
          minimumSize: Size(48, tokens.controlHeight),
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
          shape: shape,
          textStyle: text.labelLarge,
        ),
      ),
      inputDecorationTheme: InputDecorationTheme(
        filled: true,
        fillColor: scheme.surface,
        constraints: BoxConstraints(minHeight: tokens.controlHeight),
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
          borderSide: BorderSide(color: scheme.primary, width: 1.5),
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
