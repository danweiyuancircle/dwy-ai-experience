import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

import '../../app/gallery_settings.dart';
import '../../catalog/catalog.dart';
import '../../catalog/entry.dart';
import 'component_detail.dart';
import 'catalog_navigation.dart';

/// Documentation-style playground: catalog on the left (a sheet on narrow
/// windows), selected component's live preview and reference on the right.
class GalleryPage extends StatefulWidget {
  const GalleryPage({super.key});

  @override
  State<GalleryPage> createState() => _GalleryPageState();
}

class _GalleryPageState extends State<GalleryPage> {
  static const _wideBreakpoint = 900.0;
  CatalogEntry _selected = galleryCatalog.first;

  void _select(CatalogEntry entry) => setState(() => _selected = entry);

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, layout) {
      final wide = layout.maxWidth >= _wideBreakpoint;
      return DwyScaffold(
        title: const Text('DWY Playground'),
        background: _glassBackground(context),
        leading: wide
            ? null
            : DwyBarAction(
                icon: CupertinoIcons.line_horizontal_3,
                label: '组件目录',
                onPressed: () => showDwySheet<void>(
                  context: context,
                  title: '组件目录',
                  builder: (sheetContext) => CatalogNavigation(
                    selected: _selected,
                    onSelect: (entry) {
                      _select(entry);
                      Navigator.of(sheetContext).pop();
                    },
                  ),
                ),
              ),
        trailing: DwyBarAction(
          icon: CupertinoIcons.circle_lefthalf_fill,
          label: '外观模式',
          onPressed: _chooseAppearance,
        ),
        body: SafeArea(
          child: Row(
            children: [
              if (wide) ...[
                SizedBox(
                  width: 280,
                  child: SingleChildScrollView(
                    padding: const EdgeInsets.all(16),
                    child: CatalogNavigation(
                      selected: _selected,
                      onSelect: _select,
                    ),
                  ),
                ),
                SizedBox(
                  width: 1,
                  child: ColoredBox(
                    color: CupertinoColors.separator.resolveFrom(context),
                  ),
                ),
              ],
              Expanded(
                child: ComponentDetail(
                  key: ValueKey(_selected.id),
                  entry: _selected,
                ),
              ),
            ],
          ),
        ),
      );
    },
  );

  // A flat page color hides refraction; the soft gradient gives the glass bar
  // something to bend while keeping panels readable.
  Widget _glassBackground(BuildContext context) {
    final primary = GallerySettingsScope.of(context).primary;
    final base = CupertinoColors.systemGroupedBackground.resolveFrom(context);
    return DecoratedBox(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            Color.alphaBlend(primary.withValues(alpha: 0.18), base),
            base,
            Color.alphaBlend(primary.withValues(alpha: 0.08), base),
          ],
        ),
      ),
      child: const SizedBox.expand(),
    );
  }

  Future<void> _chooseAppearance() async {
    final settings = GallerySettingsScope.of(context);
    final mode = await showCupertinoModalPopup<GalleryThemeMode>(
      context: context,
      builder: (context) => CupertinoActionSheet(
        title: const Text('外观模式'),
        actions: [
          for (final entry in const {
            GalleryThemeMode.system: '跟随系统',
            GalleryThemeMode.light: '浅色',
            GalleryThemeMode.dark: '深色',
          }.entries)
            CupertinoActionSheetAction(
              isDefaultAction: settings.themeMode == entry.key,
              onPressed: () => Navigator.of(context).pop(entry.key),
              child: Text(entry.value),
            ),
        ],
        cancelButton: CupertinoActionSheetAction(
          onPressed: () => Navigator.of(context).pop(),
          child: const Text('取消'),
        ),
      ),
    );
    if (mounted && mode != null) settings.onThemeMode(mode);
  }
}
