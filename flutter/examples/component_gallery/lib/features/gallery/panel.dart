import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

/// Grouped surface with a heading, shared by the detail page and examples so
/// both follow the same radius token.
class GalleryPanel extends StatelessWidget {
  const GalleryPanel({required this.title, required this.children, super.key});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => DecoratedBox(
    decoration: BoxDecoration(
      color: CupertinoColors.secondarySystemGroupedBackground.resolveFrom(
        context,
      ),
      borderRadius: BorderRadius.circular(
        DwyTheme.tokensOf(context).groupRadius,
      ),
    ),
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Semantics(
            header: true,
            child: Text(
              title,
              style: CupertinoTheme.of(context).textTheme.navTitleTextStyle,
            ),
          ),
          for (final child in children) ...[const SizedBox(height: 16), child],
        ],
      ),
    ),
  );
}
