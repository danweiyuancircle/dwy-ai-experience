import 'package:dwy_design/dwy_design.dart';
import 'package:material_ui/material_ui.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
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
    const tokens = DwyTokens(controlRadius: 20, controlHeight: 56);
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
