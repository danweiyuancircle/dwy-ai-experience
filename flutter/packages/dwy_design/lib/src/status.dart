import 'package:cupertino_ui/cupertino_ui.dart';

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
    final theme = CupertinoTheme.of(context);
    final secondary = CupertinoColors.secondaryLabel.resolveFrom(context);
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 24, vertical: 32),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          if (kind == DwyStatusKind.loading)
            const CupertinoActivityIndicator()
          else
            Icon(
              icon ??
                  (kind == DwyStatusKind.error
                      ? CupertinoIcons.exclamationmark_circle
                      : CupertinoIcons.tray),
              size: 40,
              color: secondary,
            ),
          const SizedBox(height: 16),
          Text(
            title,
            style: theme.textTheme.navTitleTextStyle,
            textAlign: TextAlign.center,
          ),
          if (message != null) ...[
            const SizedBox(height: 8),
            Text(
              message!,
              textAlign: TextAlign.center,
              style: theme.textTheme.textStyle.copyWith(color: secondary),
            ),
          ],
          if (action != null) ...[const SizedBox(height: 20), action!],
        ],
      ),
    );
  }
}
