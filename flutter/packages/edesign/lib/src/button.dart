import 'package:cupertino_ui/cupertino_ui.dart';

import 'theme.dart';

/// Action hierarchy, independent of any product-specific command.
enum DwyButtonVariant { primary, secondary, subtle, danger }

/// Keeps its label while loading and prevents duplicate actions. The caller owns
/// the asynchronous operation and must update loading when it finishes.
class DwyButton extends StatelessWidget {
  const DwyButton({
    required this.label,
    required this.onPressed,
    this.variant = DwyButtonVariant.primary,
    this.icon,
    this.loading = false,
    this.padding,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final DwyButtonVariant variant;
  final IconData? icon;
  final bool loading;

  /// Overrides the default content insets for this button.
  final EdgeInsetsGeometry? padding;

  @override
  Widget build(BuildContext context) {
    final theme = CupertinoTheme.of(context);
    final tokens = DwyTheme.tokensOf(context);
    final radius = BorderRadius.circular(tokens.controlRadius);
    final minimumSize = Size(48, tokens.controlHeight);
    final action = loading ? null : onPressed;
    final content = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (loading) ...[
          const CupertinoActivityIndicator(radius: 8),
          const SizedBox(width: 8),
        ] else if (icon != null) ...[
          Icon(icon, size: 20),
          const SizedBox(width: 8),
        ],
        Flexible(child: Text(label, textAlign: TextAlign.center)),
      ],
    );
    if (variant == DwyButtonVariant.secondary) {
      return CupertinoButton.tinted(
        onPressed: action,
        padding: padding,
        minimumSize: minimumSize,
        borderRadius: radius,
        child: content,
      );
    }
    if (variant == DwyButtonVariant.subtle) {
      return CupertinoButton(
        onPressed: action,
        padding: padding,
        minimumSize: minimumSize,
        borderRadius: radius,
        child: content,
      );
    }
    final background = variant == DwyButtonVariant.danger
        ? CupertinoDynamicColor.resolve(CupertinoColors.systemRed, context)
        : theme.primaryColor;
    return CupertinoButton.filled(
      color: background,
      foregroundColor: background.computeLuminance() > 0.179
          ? CupertinoColors.black
          : CupertinoColors.white,
      onPressed: action,
      padding: padding,
      minimumSize: minimumSize,
      borderRadius: radius,
      child: content,
    );
  }
}
