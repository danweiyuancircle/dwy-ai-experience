import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

import '../../../app/gallery_settings.dart';

/// Reads and changes the app-level theme through [GallerySettingsScope], so the
/// whole playground (not just this page) reflects the choice.
class ThemeExample extends StatefulWidget {
  const ThemeExample({super.key});

  @override
  State<ThemeExample> createState() => _ThemeExampleState();
}

class _ThemeExampleState extends State<ThemeExample> {
  final _name = TextEditingController();
  int _scope = 0;

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final settings = GallerySettingsScope.of(context);
    final theme = CupertinoTheme.of(context);
    final tokens = DwyTheme.tokensOf(context);
    final separator = CupertinoColors.separator.resolveFrom(context);
    final dark = CupertinoTheme.brightnessOf(context) == Brightness.dark;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _Section(
          title: '品牌配置',
          children: [
            const Text('切换品牌色后，按钮和 Tab 选中状态同时更新。'),
            Wrap(
              spacing: 12,
              runSpacing: 8,
              children: [
                for (final entry in const {
                  '清透蓝': Color(0xFF2563EB),
                  '松石绿': Color(0xFF0F766E),
                  '柔和紫': Color(0xFF7C3AED),
                }.entries)
                  DwyButton(
                    label: entry.key,
                    variant: settings.primary == entry.value
                        ? DwyButtonVariant.primary
                        : DwyButtonVariant.secondary,
                    onPressed: () => settings.onPrimary(entry.value),
                  ),
              ],
            ),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final entry in {
                  '主要操作色': theme.primaryColor,
                  '内容表面': CupertinoColors.secondarySystemGroupedBackground
                      .resolveFrom(context),
                  '主要文字': CupertinoColors.label.resolveFrom(context),
                  '次要文字': CupertinoColors.secondaryLabel.resolveFrom(context),
                  '分隔线': separator,
                }.entries)
                  SizedBox(
                    width: 120,
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          height: 52,
                          decoration: BoxDecoration(
                            color: entry.value,
                            borderRadius: BorderRadius.circular(12),
                            border: Border.all(color: separator),
                          ),
                        ),
                        const SizedBox(height: 6),
                        Text(
                          entry.key,
                          style: theme.textTheme.textStyle.copyWith(
                            fontSize: 13,
                          ),
                        ),
                      ],
                    ),
                  ),
              ],
            ),
            Text('当前外观：${dark ? '深色' : '浅色'}。可通过导航栏右侧按钮切换跟随系统、浅色或深色。'),
          ],
        ),
        const SizedBox(height: 24),
        _Section(
          title: '圆角与间距令牌',
          children: [
            Wrap(
              spacing: 12,
              runSpacing: 12,
              children: [
                for (final entry in {
                  'controlRadius': tokens.controlRadius,
                  'groupRadius': tokens.groupRadius,
                }.entries)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: 96,
                        height: 64,
                        decoration: BoxDecoration(
                          color: theme.primaryColor.withValues(alpha: 0.16),
                          borderRadius: BorderRadius.circular(entry.value),
                          border: Border.all(color: theme.primaryColor),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${entry.key} ${entry.value.round()}',
                        style: theme.textTheme.textStyle.copyWith(fontSize: 13),
                      ),
                    ],
                  ),
              ],
            ),
            Wrap(
              spacing: 12,
              runSpacing: 8,
              crossAxisAlignment: WrapCrossAlignment.end,
              children: [
                for (final entry in const {
                  'spaceXS': DwyTokens.spaceXS,
                  'spaceS': DwyTokens.spaceS,
                  'spaceM': DwyTokens.spaceM,
                  'spaceL': DwyTokens.spaceL,
                  'spaceXL': DwyTokens.spaceXL,
                }.entries)
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        width: entry.value * 3,
                        height: 12,
                        color: theme.primaryColor,
                      ),
                      const SizedBox(height: 6),
                      Text(
                        '${entry.key} ${entry.value.round()}',
                        style: theme.textTheme.textStyle.copyWith(fontSize: 13),
                      ),
                    ],
                  ),
              ],
            ),
            DwySettingsGroup(
              children: [
                DwySettingsTile(
                  title: '圆角令牌',
                  subtitle: '在 12 与 24 之间切换，观察按钮和输入框。',
                  trailing: CupertinoSwitch(
                    value: settings.rounded,
                    onChanged: settings.onRounded,
                  ),
                ),
                DwySettingsTile(
                  title: '组件主题覆盖',
                  subtitle: '应用层为单个按钮覆盖内容内边距。',
                  trailing: CupertinoSwitch(
                    value: settings.customButtons,
                    onChanged: settings.onCustomButtons,
                  ),
                ),
              ],
            ),
          ],
        ),
        const SizedBox(height: 24),
        _Section(
          title: '预览',
          children: [
            DwyButton(
              label: '主要操作',
              icon: CupertinoIcons.check_mark,
              padding: settings.customButtons
                  ? const EdgeInsets.symmetric(horizontal: 32, vertical: 20)
                  : null,
              onPressed: () {},
            ),
            DwyTextField(controller: _name, label: '示例输入', hintText: '输入内容'),
            CupertinoSlidingSegmentedControl<int>(
              children: const {0: Text('概览'), 1: Text('记录')},
              groupValue: _scope,
              onValueChanged: (value) {
                if (value != null) setState(() => _scope = value);
              },
            ),
            CupertinoTabBar(
              currentIndex: _scope,
              onTap: (value) => setState(() => _scope = value),
              items: const [
                BottomNavigationBarItem(
                  icon: Icon(CupertinoIcons.house),
                  label: '概览',
                ),
                BottomNavigationBarItem(
                  icon: Icon(CupertinoIcons.list_bullet),
                  label: '记录',
                ),
              ],
            ),
          ],
        ),
      ],
    );
  }
}

/// Sub-heading plus content. The detail page already supplies the surface, so
/// this stays flat instead of nesting another card.
class _Section extends StatelessWidget {
  const _Section({required this.title, required this.children});

  final String title;
  final List<Widget> children;

  @override
  Widget build(BuildContext context) => Column(
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
  );
}
