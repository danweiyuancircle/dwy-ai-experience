import 'package:cupertino_ui/cupertino_ui.dart';

/// Sidebar grouping; order here is the display order.
enum GalleryCategory {
  foundation('基础'),
  actions('操作'),
  input('输入'),
  content('内容'),
  feedback('反馈'),
  navigation('导航'),
  media('图片');

  const GalleryCategory(this.label);
  final String label;
}

/// One selectable preview state. [id] is the value passed to the example
/// builder, so it must stay unique inside an entry.
class ExampleState {
  const ExampleState(this.id, this.label);
  final String id;
  final String label;
}

/// Builds the live preview. Examples own their local state; the detail page
/// recreates the widget (new key) to reset it.
typedef ExampleBuilder = Widget Function(BuildContext context, String state);

/// Documentation and preview for one component. [symbols] lists every public
/// export the entry covers; catalog_test.dart compares it with the package
/// barrel so a new export without an entry fails the build.
class CatalogEntry {
  const CatalogEntry({
    required this.id,
    required this.name,
    required this.title,
    required this.category,
    required this.package,
    required this.icon,
    required this.summary,
    required this.symbols,
    required this.capabilities,
    required this.constraints,
    required this.code,
    required this.builder,
    this.states = const [],
  });

  /// Stable identity used for keys and search; never localized.
  final String id;

  /// Primary exported symbol; must be contained in [symbols].
  final String name;
  final String title;
  final GalleryCategory category;
  final String package;
  final IconData icon;
  final String summary;
  final List<String> symbols;
  final List<String> capabilities;
  final List<String> constraints;
  final String code;
  final ExampleBuilder builder;

  /// Empty or single-state entries hide the state selector.
  final List<ExampleState> states;

  bool matches(String query) {
    final text = query.trim().toLowerCase();
    return text.isEmpty ||
        [
          id,
          name,
          title,
          ...symbols,
        ].any((value) => value.toLowerCase().contains(text));
  }
}
