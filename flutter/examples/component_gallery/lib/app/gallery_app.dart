import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

import '../features/gallery/gallery_page.dart';
import 'gallery_settings.dart';

/// Playground assembly owns theme configuration; component state stays local.
class GalleryApp extends StatefulWidget {
  const GalleryApp({super.key});

  @override
  State<GalleryApp> createState() => _GalleryAppState();
}

class _GalleryAppState extends State<GalleryApp> {
  GalleryThemeMode _mode = GalleryThemeMode.system;
  Color _primary = const Color(0xFF2563EB);
  bool _rounded = false;
  bool _customButtons = false;

  @override
  Widget build(BuildContext context) => CupertinoApp(
    title: 'DWY 组件 Playground',
    debugShowCheckedModeBanner: false,
    theme: DwyTheme.create(
      brightness: switch (_mode) {
        GalleryThemeMode.system => null,
        GalleryThemeMode.light => Brightness.light,
        GalleryThemeMode.dark => Brightness.dark,
      },
      brand: DwyBrand(primary: _primary),
    ),
    localizationsDelegates: GlobalCupertinoLocalizations.delegates,
    supportedLocales: const [Locale('zh'), Locale('en')],
    builder: (context, child) => DwyGlass.wrap(
      child: DwyTheme.withTokens(
        tokens: DwyTokens(controlRadius: _rounded ? 24 : 12),
        child: GallerySettingsScope(
          settings: GallerySettings(
            themeMode: _mode,
            primary: _primary,
            rounded: _rounded,
            customButtons: _customButtons,
            onThemeMode: (value) => setState(() => _mode = value),
            onPrimary: (value) => setState(() => _primary = value),
            onRounded: (value) => setState(() => _rounded = value),
            onCustomButtons: (value) => setState(() => _customButtons = value),
          ),
          child: child!,
        ),
      ),
    ),
    home: const GalleryPage(),
  );
}
