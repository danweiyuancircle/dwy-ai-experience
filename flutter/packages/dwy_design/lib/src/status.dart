import 'package:material_ui/material_ui.dart';

/// States describe presentation only; data ownership stays in the feature.
enum DwyStatusKind { empty, loading, error }

/// Shared empty/loading/error layout. Async callers supply the actual state;
/// loading is indeterminate and never simulates completed work.
class DwyStatusView extends StatelessWidget {
  const DwyStatusView({
    required this.title,
    this.message,
    this.kind = DwyStatusKind.empty,
    this.icon,
    this.action,
    super.key,
  });

  final String title;
  final String? message;
  final DwyStatusKind kind;
  final IconData? icon;
  final Widget? action;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (kind == DwyStatusKind.loading)
            const CircularProgressIndicator()
          else
            Icon(
              icon ??
                  (kind == DwyStatusKind.error
                      ? Icons.error_outline
                      : Icons.inbox_outlined),
              size: 40,
              color: theme.colorScheme.onSurfaceVariant,
            ),
          const SizedBox(height: 16),
          Text(
            title,
            style: theme.textTheme.titleMedium,
            textAlign: TextAlign.center,
          ),
          if (message != null) ...[
            const SizedBox(height: 8),
            Text(
              message!,
              textAlign: TextAlign.center,
              style: theme.textTheme.bodyMedium?.copyWith(
                color: theme.colorScheme.onSurfaceVariant,
              ),
            ),
          ],
          if (action != null) ...[const SizedBox(height: 20), action!],
        ],
      ),
    );
  }
}
