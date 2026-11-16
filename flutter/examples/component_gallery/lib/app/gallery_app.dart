import 'package:dwy_design/dwy_design.dart';
import 'package:material_ui/material_ui.dart';

import '../features/gallery/gallery_page.dart';

/// Playground assembly owns theme configuration; component state stays local.
class GalleryApp extends StatefulWidget {
  const GalleryApp({super.key});

  @override
  State<GalleryApp> createState() => _GalleryAppState();
}

class _GalleryAppState extends State<GalleryApp> {
  ThemeMode _mode = ThemeMode.system;
  Color _primary = const Color(0xFF2563EB);
  bool _rounded = false;
  bool _customButtons = false;

  ThemeData _theme(Brightness brightness) {
    final theme = DwyTheme.create(
      brightness: brightness,
      brand: DwyBrand(primary: _primary),
      tokens: DwyTokens(controlRadius: _rounded ? 24 : 12),
    );
    if (!_customButtons) return theme;
    return theme.copyWith(
      filledButtonTheme: FilledButtonThemeData(
        style: theme.filledButtonTheme.style!.copyWith(
          padding: const WidgetStatePropertyAll(
            EdgeInsets.symmetric(horizontal: 32, vertical: 20),
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) => MaterialApp(
    title: 'DWY 组件 Playground',
    debugShowCheckedModeBanner: false,
    theme: _theme(Brightness.light),
    darkTheme: _theme(Brightness.dark),
    themeMode: _mode,
    home: GalleryPage(
      themeMode: _mode,
      primary: _primary,
      rounded: _rounded,
      customButtons: _customButtons,
      onThemeMode: (value) => setState(() => _mode = value),
      onPrimary: (value) => setState(() => _primary = value),
      onRounded: (value) => setState(() => _rounded = value),
      onCustomButtons: (value) => setState(() => _customButtons = value),
    ),
  );
}
