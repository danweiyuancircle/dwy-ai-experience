import 'package:material_ui/material_ui.dart';

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
    this.style,
    super.key,
  });

  final String label;
  final VoidCallback? onPressed;
  final DwyButtonVariant variant;
  final IconData? icon;
  final bool loading;
  final ButtonStyle? style;

  @override
  Widget build(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    final action = loading ? null : onPressed;
    final content = Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        if (loading) ...[
          const SizedBox.square(
            dimension: 18,
            child: CircularProgressIndicator(strokeWidth: 2),
          ),
          const SizedBox(width: 8),
        ] else if (icon != null) ...[
          Icon(icon, size: 20),
          const SizedBox(width: 8),
        ],
        Flexible(child: Text(label, textAlign: TextAlign.center)),
      ],
    );
    return switch (variant) {
      DwyButtonVariant.primary => FilledButton(
        onPressed: action,
        style: style,
        child: content,
      ),
      DwyButtonVariant.secondary => OutlinedButton(
        onPressed: action,
        style: style,
        child: content,
      ),
      DwyButtonVariant.subtle => TextButton(
        onPressed: action,
        style: style,
        child: content,
      ),
      DwyButtonVariant.danger => FilledButton(
        onPressed: action,
        style: FilledButton.styleFrom(
          backgroundColor: scheme.error,
          foregroundColor: scheme.onError,
        ).merge(style),
        child: content,
      ),
    };
  }
}
