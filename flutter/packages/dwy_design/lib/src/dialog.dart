import 'package:material_ui/material_ui.dart';

import 'button.dart';
import 'theme.dart';

/// Returns true only for confirmation; cancel, back and barrier dismissal return
/// false. The caller performs the action after awaiting this result.
Future<bool> showDwyConfirmation({
  required BuildContext context,
  required String title,
  required String message,
  required String confirmLabel,
  required String cancelLabel,
  bool destructive = false,
}) async {
  final radius = DwyTheme.tokensOf(context).groupRadius;
  final result = await showDialog<bool>(
    context: context,
    builder: (dialogContext) => AlertDialog(
      backgroundColor: Theme.of(dialogContext).colorScheme.surface,
      surfaceTintColor: Colors.transparent,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(radius),
      ),
      title: Text(title),
      content: Text(message),
      actions: [
        DwyButton(
          label: cancelLabel,
          variant: DwyButtonVariant.subtle,
          onPressed: () => Navigator.of(dialogContext).pop(false),
        ),
        DwyButton(
          label: confirmLabel,
          variant: destructive
              ? DwyButtonVariant.danger
              : DwyButtonVariant.primary,
          onPressed: () => Navigator.of(dialogContext).pop(true),
        ),
      ],
    ),
  );
  return result == true;
}

/// A consistent bottom sheet with safe-area and keyboard padding. Content is
/// scrollable; close with Navigator.pop(sheetContext, result) inside builder.
Future<T?> showDwySheet<T>({
  required BuildContext context,
  required String title,
  required WidgetBuilder builder,
}) => showModalBottomSheet<T>(
  context: context,
  isScrollControlled: true,
  useSafeArea: true,
  showDragHandle: true,
  backgroundColor: Theme.of(context).colorScheme.surface,
  shape: RoundedRectangleBorder(
    borderRadius: BorderRadius.vertical(
      top: Radius.circular(DwyTheme.tokensOf(context).groupRadius),
    ),
  ),
  builder: (sheetContext) => Padding(
    padding: EdgeInsets.only(
      bottom: MediaQuery.viewInsetsOf(sheetContext).bottom,
    ),
    child: ConstrainedBox(
      constraints: BoxConstraints(
        maxHeight: MediaQuery.sizeOf(sheetContext).height * 0.85,
      ),
      child: SingleChildScrollView(
        padding: EdgeInsets.fromLTRB(
          24,
          0,
          24,
          24 + MediaQuery.paddingOf(sheetContext).bottom,
        ),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(title, style: Theme.of(sheetContext).textTheme.titleLarge),
            const SizedBox(height: 20),
            builder(sheetContext),
          ],
        ),
      ),
    ),
  ),
);
