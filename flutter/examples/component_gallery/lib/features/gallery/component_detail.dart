import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';
import 'package:flutter/services.dart';

import '../../catalog/entry.dart';
import 'panel.dart';

/// Reference page for one catalog entry. Create it with a key derived from the
/// entry id so state selection, reset count and copy feedback start over when
/// another component is chosen.
class ComponentDetail extends StatefulWidget {
  const ComponentDetail({required this.entry, super.key});

  final CatalogEntry entry;

  @override
  State<ComponentDetail> createState() => _ComponentDetailState();
}

class _ComponentDetailState extends State<ComponentDetail> {
  late String _state = widget.entry.states.firstOrNull?.id ?? '';
  int _resets = 0;
  bool _copied = false;

  @override
  Widget build(BuildContext context) {
    final entry = widget.entry;
    final theme = CupertinoTheme.of(context);
    final secondary = CupertinoColors.secondaryLabel.resolveFrom(context);
    return SingleChildScrollView(
      padding: EdgeInsets.all(DwyTheme.tokensOf(context).pageInset),
      child: Center(
        child: ConstrainedBox(
          constraints: const BoxConstraints(maxWidth: 920),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Semantics(
                header: true,
                child: Text(
                  entry.title,
                  style: theme.textTheme.navLargeTitleTextStyle,
                ),
              ),
              const SizedBox(height: 4),
              Text(
                '${entry.name} · ${entry.package} · ${entry.category.label}',
                style: theme.textTheme.textStyle.copyWith(
                  fontSize: 13,
                  color: secondary,
                ),
              ),
              const SizedBox(height: 12),
              Text(entry.summary),
              const SizedBox(height: 24),
              GalleryPanel(
                title: '实时预览',
                children: [
                  if (entry.states.length > 1) _stateBar(entry),
                  KeyedSubtree(
                    key: ValueKey('${entry.id}-$_resets'),
                    child: entry.builder(context, _state),
                  ),
                ],
              ),
              const SizedBox(height: 24),
              GalleryPanel(
                title: '支持的能力',
                children: [
                  for (final item in entry.capabilities)
                    _bullet(CupertinoIcons.checkmark_circle, item, context),
                ],
              ),
              const SizedBox(height: 24),
              GalleryPanel(
                title: '用法与约束',
                children: [
                  for (final item in entry.constraints)
                    _bullet(CupertinoIcons.info_circle, item, context),
                ],
              ),
              const SizedBox(height: 24),
              GalleryPanel(
                title: 'Dart 示例',
                children: [
                  _code(context, entry.code),
                  Row(
                    children: [
                      DwyButton(
                        label: '复制示例',
                        variant: DwyButtonVariant.secondary,
                        icon: CupertinoIcons.doc_on_doc,
                        onPressed: _copy,
                      ),
                      if (_copied)
                        Padding(
                          padding: const EdgeInsets.only(left: 12),
                          child: Semantics(
                            liveRegion: true,
                            child: const Text('已复制'),
                          ),
                        ),
                    ],
                  ),
                ],
              ),
              const SizedBox(height: 24),
            ],
          ),
        ),
      ),
    );
  }

  Widget _stateBar(CatalogEntry entry) => Wrap(
    spacing: 12,
    runSpacing: 12,
    crossAxisAlignment: WrapCrossAlignment.center,
    children: [
      CupertinoSlidingSegmentedControl<String>(
        groupValue: _state,
        children: {
          for (final state in entry.states) state.id: Text(state.label),
        },
        onValueChanged: (value) {
          if (value != null) setState(() => _state = value);
        },
      ),
      DwyButton(
        label: '重置示例',
        variant: DwyButtonVariant.subtle,
        onPressed: () => setState(() => _resets++),
      ),
    ],
  );

  Widget _bullet(IconData icon, String text, BuildContext context) => Row(
    crossAxisAlignment: CrossAxisAlignment.start,
    children: [
      Padding(
        padding: const EdgeInsets.only(top: 2),
        child: Icon(
          icon,
          size: 18,
          color: CupertinoTheme.of(context).primaryColor,
        ),
      ),
      const SizedBox(width: 10),
      Expanded(child: Text(text)),
    ],
  );

  Widget _code(BuildContext context, String code) => DecoratedBox(
    decoration: BoxDecoration(
      color: CupertinoColors.tertiarySystemFill.resolveFrom(context),
      borderRadius: BorderRadius.circular(
        DwyTheme.tokensOf(context).controlRadius,
      ),
    ),
    child: SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      padding: const EdgeInsets.all(16),
      child: Text(
        code.trim(),
        style: CupertinoTheme.of(context).textTheme.textStyle.copyWith(
          fontFamily: 'Menlo',
          fontFamilyFallback: const ['Courier', 'monospace'],
          fontSize: 13,
        ),
      ),
    ),
  );

  Future<void> _copy() async {
    await Clipboard.setData(ClipboardData(text: widget.entry.code.trim()));
    if (mounted) setState(() => _copied = true);
  }
}
