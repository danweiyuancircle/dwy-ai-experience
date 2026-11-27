import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

import '../../catalog/catalog.dart';
import '../../catalog/entry.dart';

/// Searchable catalog list grouped by category. Used inline on wide windows
/// and inside a sheet on narrow ones; the owner decides what selecting does.
class CatalogNavigation extends StatefulWidget {
  const CatalogNavigation({
    required this.selected,
    required this.onSelect,
    super.key,
  });

  final CatalogEntry selected;
  final ValueChanged<CatalogEntry> onSelect;

  @override
  State<CatalogNavigation> createState() => _CatalogNavigationState();
}

class _CatalogNavigationState extends State<CatalogNavigation> {
  final _search = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final matches = galleryCatalog.where((entry) => entry.matches(_query));
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        DwySearchField(
          controller: _search,
          hintText: '搜索组件',
          clearLabel: '清除目录搜索',
          onChanged: (value) => setState(() => _query = value),
        ),
        const SizedBox(height: 16),
        if (matches.isEmpty)
          const Padding(
            padding: EdgeInsets.symmetric(vertical: 24),
            child: Text('没有匹配的组件', textAlign: TextAlign.center),
          ),
        for (final category in GalleryCategory.values)
          if (matches.where((entry) => entry.category == category)
              case final items when items.isNotEmpty)
            Padding(
              padding: const EdgeInsets.only(bottom: 16),
              child: DwySettingsGroup(
                title: category.label,
                children: [for (final entry in items) _tile(context, entry)],
              ),
            ),
      ],
    );
  }

  Widget _tile(BuildContext context, CatalogEntry entry) {
    final selected = entry.id == widget.selected.id;
    return Semantics(
      selected: selected,
      child: CupertinoListTile.notched(
        key: Key('catalog-${entry.id}'),
        backgroundColor: selected
            ? CupertinoColors.tertiarySystemFill.resolveFrom(context)
            : CupertinoColors.transparent,
        leading: Icon(entry.icon),
        title: Text(entry.title),
        onTap: () => widget.onSelect(entry),
      ),
    );
  }
}
