import 'package:material_ui/material_ui.dart';

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
    final theme = Theme.of(context);
    return ListTile(
      enabled: enabled,
      onTap: onTap,
      contentPadding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      minVerticalPadding: 12,
      leading: leading,
      title: Text(title),
      subtitle: subtitle == null
          ? null
          : Padding(
              padding: const EdgeInsets.only(top: 4),
              child: Text(subtitle!, style: theme.textTheme.bodySmall),
            ),
      trailing: trailing == null
          ? (onTap == null ? null : const Icon(Icons.chevron_right))
          : IgnorePointer(ignoring: !enabled, child: trailing),
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
    final theme = Theme.of(context);
    final tokens = DwyTheme.tokensOf(context);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        if (title != null)
          Padding(
            padding: const EdgeInsets.only(left: 4, bottom: 12),
            child: Text(title!, style: theme.textTheme.titleSmall),
          ),
        ClipRRect(
          borderRadius: BorderRadius.circular(tokens.groupRadius),
          child: Material(
            color: theme.colorScheme.surface,
            child: Column(
              children: [
                for (var index = 0; index < children.length; index++) ...[
                  if (index > 0) const Divider(indent: 16, endIndent: 16),
                  children[index],
                ],
              ],
            ),
          ),
        ),
        if (footnote != null)
          Padding(
            padding: const EdgeInsets.only(left: 4, top: 8),
            child: Text(footnote!, style: theme.textTheme.bodySmall),
          ),
      ],
    );
  }
}
