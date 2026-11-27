import 'package:cupertino_ui/cupertino_ui.dart';

import 'theme.dart';

/// A wrapping settings row. For an interactive trailing control such as Switch,
/// leave onTap null to avoid competing tap handlers and duplicated semantics.
class DwySettingsTile extends StatelessWidget {
  const DwySettingsTile({
    required this.title,
    this.subtitle,
    this.leading,
    this.trailing,
    this.onTap,
    this.enabled = true,
    super.key,
  });

  final String title;
  final String? subtitle;
  final Widget? leading;
  final Widget? trailing;
  final VoidCallback? onTap;
  final bool enabled;

  @override
  Widget build(BuildContext context) {
    final text = CupertinoTheme.of(context).textTheme.textStyle;
    final secondary = CupertinoDynamicColor.resolve(
      enabled ? CupertinoColors.secondaryLabel : CupertinoColors.tertiaryLabel,
      context,
    );
    return Semantics(
      enabled: enabled,
      child: CupertinoListTile.notched(
        onTap: enabled ? onTap : null,
        leading: leading,
        title: DefaultTextStyle(
          // The official tile defaults to one line. Settings descriptions may wrap.
          style: text,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(title, style: enabled ? null : TextStyle(color: secondary)),
              if (subtitle != null)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    subtitle!,
                    style: TextStyle(fontSize: 14, color: secondary),
                  ),
                ),
            ],
          ),
        ),
        trailing: trailing == null
            ? (onTap == null ? null : const CupertinoListTileChevron())
            : IgnorePointer(
                ignoring: !enabled,
                child: ExcludeSemantics(excluding: !enabled, child: trailing),
              ),
      ),
    );
  }
}

/// A neutral grouped surface. Titles and footnotes belong to the consuming app.
class DwySettingsGroup extends StatelessWidget {
  const DwySettingsGroup({
    required this.children,
    this.title,
    this.footnote,
    super.key,
  });

  final List<Widget> children;
  final String? title;
  final String? footnote;

  @override
  Widget build(BuildContext context) {
    final tokens = DwyTheme.tokensOf(context);
    return CupertinoListSection.insetGrouped(
      header: title == null ? null : Text(title!),
      footer: footnote == null ? null : Text(footnote!),
      margin: EdgeInsets.zero,
      backgroundColor: CupertinoColors.transparent,
      decoration: BoxDecoration(
        color: CupertinoColors.secondarySystemGroupedBackground.resolveFrom(
          context,
        ),
        borderRadius: BorderRadius.circular(tokens.groupRadius),
      ),
      children: children.isEmpty ? const [SizedBox.shrink()] : children,
    );
  }
}
