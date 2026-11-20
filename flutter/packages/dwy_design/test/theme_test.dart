import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('brand and brightness configure the standalone Cupertino theme', () {
    const brand = DwyBrand(primary: Color(0xFF0F766E), fontFamily: 'Example');
    final CupertinoThemeData light = DwyTheme.create(
      brightness: Brightness.light,
      brand: brand,
    );
    final dark = DwyTheme.create(brightness: Brightness.dark, brand: brand);
    expect(light.brightness, Brightness.light);
    expect(dark.brightness, Brightness.dark);
    expect(light.primaryColor, brand.primary);
    expect(dark.primaryColor, brand.primary);
    expect(light.textTheme.textStyle.fontFamily, 'Example');
    expect(dark.textTheme.navLargeTitleTextStyle.fontFamily, 'Example');
  });

  testWidgets('dynamic background follows the active theme', (tester) async {
    for (final brightness in Brightness.values) {
      await tester.pumpWidget(
        CupertinoApp(
          theme: DwyTheme.create(brightness: brightness),
          home: const CupertinoPageScaffold(child: Text('Preview')),
        ),
      );
      final context = tester.element(find.text('Preview'));
      expect(
        CupertinoTheme.of(context).scaffoldBackgroundColor,
        CupertinoDynamicColor.resolve(
          CupertinoColors.systemGroupedBackground,
          context,
        ),
      );
    }
  });
}
