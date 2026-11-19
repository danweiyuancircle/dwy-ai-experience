import 'package:dwy_design/dwy_design.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  for (final brightness in Brightness.values) {
    test('$brightness shares typography and quiet component surfaces', () {
      final theme = DwyTheme.create(brightness: brightness);
      final scheme = theme.colorScheme;
      expect(theme.textTheme.titleLarge!.fontSize, 22);
      expect(theme.textTheme.titleLarge!.fontWeight, FontWeight.w600);
      expect(theme.textTheme.bodySmall!.fontSize, 13);
      expect(theme.cardTheme.elevation, 0);
      expect(theme.cardTheme.color, scheme.surface);
      expect(theme.navigationBarTheme.backgroundColor, scheme.surface);
      expect(theme.navigationBarTheme.indicatorColor, scheme.primaryContainer);
      expect(
        theme.navigationBarTheme.iconTheme!.resolve({WidgetState.disabled}),
        isNull,
      );
      expect(
        theme.navigationBarTheme.labelTextStyle!.resolve({
          WidgetState.disabled,
        }),
        isNull,
      );
      expect(
        contrast(scheme.primaryContainer, scheme.onPrimaryContainer),
        greaterThanOrEqualTo(4.5),
      );
      expect(
        theme.segmentedButtonTheme.style!.foregroundColor!.resolve({
          WidgetState.selected,
        }),
        scheme.onPrimaryContainer,
      );
      expect(
        theme.segmentedButtonTheme.style!.foregroundColor!.resolve({
          WidgetState.disabled,
          WidgetState.selected,
        }),
        isNot(scheme.onPrimaryContainer),
      );
      expect(theme.dialogTheme.backgroundColor, scheme.surface);
    });
  }

  test('default theme keeps neutral surfaces and accessible brand text', () {
    final ThemeData theme = DwyTheme.create(brightness: Brightness.light);
    expect(theme.useMaterial3, isTrue);
    expect(theme.colorScheme.primary, const Color(0xFF2563EB));
    expect(theme.scaffoldBackgroundColor, const Color(0xFFF8FAFC));
    expect(theme.colorScheme.surface, Colors.white);
    expect(
      theme.extension<DwyTokens>()!.controlHeight,
      greaterThanOrEqualTo(48),
    );
    expect(
      contrast(theme.colorScheme.primary, theme.colorScheme.onPrimary),
      greaterThanOrEqualTo(4.5),
    );
    expect(
      contrast(theme.colorScheme.surface, theme.colorScheme.onSurfaceVariant),
      greaterThanOrEqualTo(4.5),
    );
  });

  test('brand and geometry are injected without changing component API', () {
    const tokens = DwyTokens(
      controlRadius: 20,
      groupRadius: 28,
      controlHeight: 56,
    );
    final theme = DwyTheme.create(
      brightness: Brightness.light,
      brand: const DwyBrand(primary: Color(0xFFFACC15)),
      tokens: tokens,
    );
    expect(theme.colorScheme.primary, const Color(0xFFFACC15));
    expect(
      contrast(theme.colorScheme.primary, theme.colorScheme.onPrimary),
      greaterThanOrEqualTo(4.5),
    );
    expect(theme.extension<DwyTokens>(), same(tokens));
    expect(theme.filledButtonTheme.style!.minimumSize!.resolve({})!.height, 56);
    expect(
      theme.segmentedButtonTheme.style!.minimumSize!.resolve({})!.height,
      56,
    );
    expect(
      (theme.cardTheme.shape! as RoundedRectangleBorder).borderRadius,
      BorderRadius.circular(28),
    );
    expect(
      (theme.dialogTheme.shape! as RoundedRectangleBorder).borderRadius,
      BorderRadius.circular(28),
    );
  });

  test('dark theme has distinct surfaces and readable semantic text', () {
    final theme = DwyTheme.create(brightness: Brightness.dark);
    expect(theme.brightness, Brightness.dark);
    expect(theme.scaffoldBackgroundColor, isNot(theme.colorScheme.surface));
    expect(
      contrast(theme.colorScheme.surface, theme.colorScheme.onSurface),
      greaterThanOrEqualTo(4.5),
    );
    expect(
      contrast(theme.colorScheme.surface, theme.colorScheme.onSurfaceVariant),
      greaterThanOrEqualTo(4.5),
    );
  });
}

double contrast(Color a, Color b) {
  final left = a.computeLuminance();
  final right = b.computeLuminance();
  return left > right
      ? (left + 0.05) / (right + 0.05)
      : (right + 0.05) / (left + 0.05);
}
