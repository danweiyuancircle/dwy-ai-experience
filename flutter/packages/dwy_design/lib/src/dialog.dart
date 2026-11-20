import 'package:cupertino_ui/cupertino_ui.dart';

import 'theme.dart';
import 'tokens.dart';

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
  final result = await showCupertinoDialog<bool>(
    context: context,
    barrierDismissible: true,
    builder: (dialogContext) => CupertinoAlertDialog(
      title: Text(title),
      content: Text(message),
      actions: [
        CupertinoDialogAction(
          child: Text(cancelLabel),
          onPressed: () => Navigator.of(dialogContext).pop(false),
        ),
        CupertinoDialogAction(
          isDefaultAction: !destructive,
          isDestructiveAction: destructive,
          child: Text(confirmLabel),
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
}) => showCupertinoSheet<T>(
  context: context,
  showDragHandle: true,
  scrollableBuilder: (sheetContext, controller) {
    final theme = CupertinoTheme.of(sheetContext);
    final inset = DwyTheme.tokensOf(sheetContext).pageInset;
    return CupertinoPageScaffold(
      backgroundColor: CupertinoColors.secondarySystemGroupedBackground
          .resolveFrom(sheetContext),
      child: SafeArea(
        child: SingleChildScrollView(
          controller: controller,
          padding: EdgeInsets.fromLTRB(inset, DwyTokens.spaceXL, inset, inset),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Semantics(
                header: true,
                child: Text(title, style: theme.textTheme.navTitleTextStyle),
              ),
              const SizedBox(height: DwyTokens.spaceL),
              Builder(builder: builder),
            ],
          ),
        ),
      ),
    );
  },
);
