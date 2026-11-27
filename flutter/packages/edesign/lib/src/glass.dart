import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:liquid_glass_widgets/liquid_glass_widgets.dart' as glass;

/// Entry points for the glass material. The backing package stays internal to
/// dwy_design so it can be replaced by an official implementation without
/// touching callers.
abstract final class DwyGlass {
  /// Preloads shaders. Call once in main() before runApp, otherwise the first
  /// glass frames render placeholders.
  static Future<void> initialize() => glass.LiquidGlassWidgets.initialize();

  /// Wrap the child inside CupertinoApp.builder, not outside the app.
  ///
  /// The backing package reads the SDK Cupertino theme while this workspace
  /// uses package:cupertino_ui, so the compatibility bridge is required for
  /// DwyTheme brightness to reach glass widgets. The bridge is deprecated
  /// upstream; remove it together with the backing package.
  static Widget wrap({required Widget child}) =>
      // ignore: deprecated_member_use
      CupertinoUiCompatibilityBridge(
        child: glass.LiquidGlassWidgets.wrap(child: child),
      );
}

/// Icon action shown in a [DwyScaffold] bar as a round glass button.
@immutable
class DwyBarAction {
  const DwyBarAction({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  final IconData icon;

  /// Accessibility label; icon-only buttons have no visible text.
  final String label;
  final VoidCallback onPressed;
}

/// Page scaffold with a glass navigation bar.
///
/// The body extends behind the bar so scrolled content shows through the glass.
/// The scaffold does not pad the body itself: it only raises
/// MediaQuery.padding.top to include the bar, so scroll views must read that
/// value as their top padding (ListView does this automatically, a
/// SingleChildScrollView does not). Requires DwyGlass.wrap above it.
class DwyScaffold extends StatelessWidget {
  const DwyScaffold({
    required this.body,
    this.title,
    this.leading,
    this.trailing,
    this.background,
    super.key,
  });

  final Widget body;
  final Widget? title;
  final DwyBarAction? leading;
  final DwyBarAction? trailing;

  /// Defaults to the theme scaffold color. A flat color shows little glass
  /// effect; pass a gradient or image to see refraction.
  final Widget? background;

  @override
  Widget build(BuildContext context) {
    final media = MediaQuery.of(context);
    final hasBar = title != null || leading != null || trailing != null;
    final bar = hasBar
        ? glass.GlassAppBar(
            title: title,
            leading: leading == null ? null : _button(leading!),
            actions: [if (trailing != null) _button(trailing!)],
          )
        : null;
    final top = media.padding.top + (bar?.preferredSize.height ?? 0);
    return glass.GlassScaffold(
      appBar: bar,
      background: background,
      backgroundColor: background == null
          ? CupertinoDynamicColor.resolve(
              CupertinoTheme.of(context).scaffoldBackgroundColor,
              context,
            )
          : null,
      statusBarStyle: glass.GlassStatusBarStyle.auto,
      body: MediaQuery(
        data: media.copyWith(padding: media.padding.copyWith(top: top)),
        child: body,
      ),
    );
  }

  Widget _button(DwyBarAction action) => glass.GlassIconButton(
    icon: Icon(action.icon),
    semanticLabel: action.label,
    onPressed: action.onPressed,
  );
}
