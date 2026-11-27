import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

import '../../../app/gallery_settings.dart';

/// State ids: gradient (refraction visible), flat (solid color shows little).
class GlassExample extends StatelessWidget {
  const GlassExample({required this.state, super.key});

  final String state;

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      const Text('导航栏按钮是圆形玻璃按钮；打开示例页，向上滚动内容并观察栏下方的色块。'),
      const SizedBox(height: 16),
      Align(
        alignment: Alignment.centerLeft,
        child: DwyButton(
          label: '打开玻璃导航栏示例',
          icon: CupertinoIcons.sparkles,
          onPressed: () => Navigator.of(context).push<void>(
            CupertinoPageRoute<void>(
              builder: (_) => _GlassDemoPage(flat: state == 'flat'),
            ),
          ),
        ),
      ),
    ],
  );
}

class _GlassDemoPage extends StatelessWidget {
  const _GlassDemoPage({required this.flat});

  final bool flat;

  @override
  Widget build(BuildContext context) {
    final primary = GallerySettingsScope.of(context).primary;
    final base = CupertinoColors.systemGroupedBackground.resolveFrom(context);
    return DwyScaffold(
      title: const Text('玻璃导航栏示例'),
      leading: DwyBarAction(
        icon: CupertinoIcons.chevron_back,
        label: '返回',
        onPressed: () => Navigator.of(context).pop(),
      ),
      trailing: DwyBarAction(
        icon: CupertinoIcons.heart,
        label: '收藏',
        onPressed: () {},
      ),
      background: flat
          ? null
          : DecoratedBox(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  begin: Alignment.topLeft,
                  end: Alignment.bottomRight,
                  colors: [
                    Color.alphaBlend(primary.withValues(alpha: 0.35), base),
                    base,
                    Color.alphaBlend(primary.withValues(alpha: 0.15), base),
                  ],
                ),
              ),
              child: const SizedBox.expand(),
            ),
      // Scaffold only raises MediaQuery.padding.top. An explicit ListView
      // padding replaces the automatic inset, so the top value is added by hand;
      // Builder is needed because the outer context sits above the Scaffold.
      body: Builder(builder: _blocks),
    );
  }

  Widget _blocks(BuildContext context) => ListView.builder(
    padding: EdgeInsets.fromLTRB(
      16,
      MediaQuery.paddingOf(context).top + 16,
      16,
      16,
    ),
    itemCount: 24,
    itemBuilder: (context, index) => Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: DecoratedBox(
        decoration: BoxDecoration(
          color: HSLColor.fromAHSL(
            1,
            (index * 29.0) % 360,
            0.65,
            CupertinoTheme.brightnessOf(context) == Brightness.dark
                ? 0.35
                : 0.6,
          ).toColor(),
          borderRadius: BorderRadius.circular(
            DwyTheme.tokensOf(context).groupRadius,
          ),
        ),
        child: SizedBox(
          height: 88,
          child: Center(
            child: Text(
              '色块 ${index + 1}',
              style: const TextStyle(color: CupertinoColors.white),
            ),
          ),
        ),
      ),
    ),
  );
}
