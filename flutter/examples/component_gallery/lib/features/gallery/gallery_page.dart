import 'package:dwy_design/dwy_design.dart';
import 'package:material_ui/material_ui.dart';

import 'image_examples.dart';

/// Interactive examples consume public DWY UI APIs and Flutter primitives.
class GalleryPage extends StatefulWidget {
  const GalleryPage({
    required this.themeMode,
    required this.primary,
    required this.rounded,
    required this.customButtons,
    required this.onThemeMode,
    required this.onPrimary,
    required this.onRounded,
    required this.onCustomButtons,
    super.key,
  });

  final ThemeMode themeMode;
  final Color primary;
  final bool rounded;
  final bool customButtons;
  final ValueChanged<ThemeMode> onThemeMode;
  final ValueChanged<Color> onPrimary;
  final ValueChanged<bool> onRounded;
  final ValueChanged<bool> onCustomButtons;

  @override
  State<GalleryPage> createState() => _GalleryPageState();
}

class _GalleryPageState extends State<GalleryPage> {
  static const _sections = [
    '主题与令牌',
    '按钮',
    '输入与搜索',
    '列表与设置',
    '弹窗与面板',
    '内容状态',
    '图片',
  ];
  static const _icons = [
    Icons.palette_outlined,
    Icons.touch_app_outlined,
    Icons.search,
    Icons.tune,
    Icons.web_asset_outlined,
    Icons.inbox_outlined,
    Icons.image_outlined,
  ];
  final _name = TextEditingController();
  final _search = TextEditingController();
  final _form = GlobalKey<FormState>();
  int _selected = 0;
  int _clicks = 0;
  bool _loading = false;
  bool _notifications = true;
  bool _sync = false;
  String _query = '';
  String _formResult = '';
  String _dialogResult = '尚未操作';
  DwyStatusKind _status = DwyStatusKind.empty;

  @override
  void dispose() {
    _name.dispose();
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => LayoutBuilder(
    builder: (context, layout) {
      final wide = layout.maxWidth >= 900;
      return Scaffold(
        appBar: AppBar(
          title: const Text('DWY Playground'),
          actions: [
            PopupMenuButton<ThemeMode>(
              tooltip: '外观模式',
              initialValue: widget.themeMode,
              icon: const Icon(Icons.brightness_6_outlined),
              onSelected: widget.onThemeMode,
              itemBuilder: (_) => const [
                PopupMenuItem(value: ThemeMode.system, child: Text('跟随系统')),
                PopupMenuItem(value: ThemeMode.light, child: Text('浅色')),
                PopupMenuItem(value: ThemeMode.dark, child: Text('深色')),
              ],
            ),
            const SizedBox(width: 12),
          ],
        ),
        drawer: wide ? null : Drawer(child: SafeArea(child: _navigation(true))),
        body: SafeArea(
          top: false,
          child: Row(
            children: [
              if (wide) ...[
                SizedBox(width: 240, child: _navigation(false)),
                const VerticalDivider(width: 1),
              ],
              Expanded(
                child: SingleChildScrollView(
                  key: PageStorageKey<String>(_sections[_selected]),
                  padding: EdgeInsets.all(DwyTheme.tokensOf(context).pageInset),
                  child: Center(
                    child: ConstrainedBox(
                      constraints: const BoxConstraints(maxWidth: 920),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.stretch,
                        children: [
                          Text(
                            _sections[_selected],
                            style: Theme.of(context).textTheme.headlineMedium,
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Material 3 交互底座 · 双端统一视觉 · 无玻璃材质',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                          const SizedBox(height: 28),
                          _content(context),
                          const SizedBox(height: 32),
                          Text(
                            '图片页仅在主动加载 URL 后联网，其他示例均在本地运行。',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ),
                    ),
                  ),
                ),
              ),
            ],
          ),
        ),
      );
    },
  );

  Widget _navigation(bool closeDrawer) => ListView(
    padding: const EdgeInsets.all(16),
    children: [
      Padding(
        padding: const EdgeInsets.fromLTRB(12, 12, 12, 20),
        child: Text('组件目录', style: Theme.of(context).textTheme.titleSmall),
      ),
      for (var index = 0; index < _sections.length; index++)
        Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: ListTile(
            selected: _selected == index,
            selectedTileColor: Theme.of(context).colorScheme.primaryContainer,
            shape: RoundedRectangleBorder(
              borderRadius: BorderRadius.circular(12),
            ),
            leading: Icon(_icons[index]),
            title: Text(_sections[index]),
            onTap: () {
              setState(() => _selected = index);
              if (closeDrawer) Navigator.of(context).pop();
            },
          ),
        ),
    ],
  );

  Widget _content(BuildContext context) => switch (_selected) {
    0 => _themeExamples(context),
    1 => _buttonExamples(),
    2 => _inputExamples(),
    3 => _settingExamples(),
    4 => _dialogExamples(context),
    6 => const ImageExamples(),
    _ => _statusExamples(),
  };

  Widget _themeExamples(BuildContext context) {
    final scheme = Theme.of(context).colorScheme;
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _panel('品牌配置', [
          const Text('切换品牌色后，按钮、聚焦边框、选中状态同时更新。'),
          Wrap(
            spacing: 12,
            runSpacing: 8,
            children: [
              for (final entry in const {
                '清透蓝': Color(0xFF2563EB),
                '松石绿': Color(0xFF0F766E),
                '柔和紫': Color(0xFF7C3AED),
              }.entries)
                ChoiceChip(
                  label: Text(entry.key),
                  selected: widget.primary == entry.value,
                  onSelected: (_) => widget.onPrimary(entry.value),
                ),
            ],
          ),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (final entry in {
                '主要操作': scheme.primary,
                '内容表面': scheme.surface,
                '主要文字': scheme.onSurface,
                '次要文字': scheme.onSurfaceVariant,
                '分隔线': scheme.outlineVariant,
              }.entries)
                SizedBox(
                  width: 140,
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Container(
                        height: 52,
                        decoration: BoxDecoration(
                          color: entry.value,
                          borderRadius: BorderRadius.circular(12),
                          border: Border.all(color: scheme.outlineVariant),
                        ),
                      ),
                      const SizedBox(height: 6),
                      Text(
                        entry.key,
                        style: Theme.of(context).textTheme.bodySmall,
                      ),
                    ],
                  ),
                ),
            ],
          ),
        ]),
        const SizedBox(height: 24),
        DwySettingsGroup(
          title: '令牌与组件级定制',
          children: [
            DwySettingsTile(
              title: '圆角令牌',
              subtitle: '在 12 与 24 之间切换，观察按钮和输入框。',
              trailing: Switch(
                value: widget.rounded,
                onChanged: widget.onRounded,
              ),
            ),
            DwySettingsTile(
              title: '组件主题覆盖',
              subtitle: '应用层通过 ThemeData.copyWith 增大实心按钮内边距。',
              trailing: Switch(
                value: widget.customButtons,
                onChanged: widget.onCustomButtons,
              ),
            ),
          ],
        ),
        const SizedBox(height: 24),
        _panel('预览', [
          DwyButton(
            label: '主要操作',
            icon: Icons.check,
            onPressed: () => _notice('按钮可用'),
          ),
          DwyTextField(controller: _name, label: '示例输入', hintText: '输入内容'),
        ]),
      ],
    );
  }

  Widget _buttonExamples() => _panel('层级与交互状态', [
    Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        DwyButton(label: '主要操作', icon: Icons.add, onPressed: _countClick),
        DwyButton(
          label: '次要操作',
          variant: DwyButtonVariant.secondary,
          onPressed: _countClick,
        ),
        DwyButton(
          label: '文字操作',
          variant: DwyButtonVariant.subtle,
          onPressed: _countClick,
        ),
        DwyButton(
          label: '危险操作',
          variant: DwyButtonVariant.danger,
          onPressed: _countClick,
        ),
        const DwyButton(label: '不可用', onPressed: null),
        DwyButton(
          label: '演示异步操作',
          loading: _loading,
          onPressed: _simulateOperation,
        ),
      ],
    ),
    Text('已点击 $_clicks 次'),
    const Text('加载时保留操作文字，并阻止重复点击。'),
  ]);

  Widget _inputExamples() => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      _panel('表单验证', [
        Form(
          key: _form,
          child: DwyTextField(
            controller: _name,
            label: '名称',
            hintText: '输入一个名称',
            helperText: '校验规则由业务调用方提供。',
            clearLabel: '清除名称',
            validator: (value) => value!.trim().isEmpty ? '名称不能为空' : null,
          ),
        ),
        DwyButton(
          label: '验证输入',
          onPressed: () {
            final valid = _form.currentState!.validate();
            setState(
              () => _formResult = valid ? '输入有效：${_name.text}' : '请检查输入',
            );
          },
        ),
        if (_formResult.isNotEmpty) Text(_formResult),
      ]),
      const SizedBox(height: 24),
      _panel('本地搜索', [
        DwySearchField(
          controller: _search,
          hintText: '搜索示例组件',
          clearLabel: '清除搜索',
          onChanged: (value) => setState(() => _query = value),
        ),
        for (final value in [
          '按钮',
          '输入框',
          '设置行',
          '分组',
          '空状态',
          '弹窗',
        ].where((value) => value.contains(_query)))
          ListTile(
            title: Text(value),
            leading: const Icon(Icons.widgets_outlined),
          ),
      ]),
    ],
  );

  Widget _settingExamples() => DwySettingsGroup(
    title: '设置分组',
    footnote: '整行跳转和独立开关分别处理，不叠加重复点击行为。',
    children: [
      DwySettingsTile(
        title: '通知偏好',
        subtitle: '仅演示本地开关，不申请系统权限。',
        leading: const Icon(Icons.notifications_none),
        trailing: Switch(
          value: _notifications,
          onChanged: (value) => setState(() => _notifications = value),
        ),
      ),
      DwySettingsTile(
        title: '同步偏好',
        leading: const Icon(Icons.sync),
        trailing: Switch(
          value: _sync,
          onChanged: (value) => setState(() => _sync = value),
        ),
      ),
      DwySettingsTile(
        title: '可跳转的设置行',
        subtitle: '支持说明文字自动换行和系统大字体。',
        leading: const Icon(Icons.info_outline),
        onTap: () => _notice('已点击设置行'),
      ),
      const DwySettingsTile(
        title: '暂不可用',
        leading: Icon(Icons.lock_outline),
        enabled: false,
      ),
    ],
  );

  Widget _dialogExamples(BuildContext context) => _panel('确认与底部面板', [
    const Text('双端保持同一套 Material 3 / DWY 外观，不切换 Cupertino。'),
    Wrap(
      spacing: 12,
      runSpacing: 12,
      children: [
        DwyButton(
          label: '打开确认弹窗',
          onPressed: () async {
            final result = await showDwyConfirmation(
              context: context,
              title: '确认演示操作？',
              message: '此示例不会删除文件或修改真实数据。',
              confirmLabel: '确认',
              cancelLabel: '取消',
              destructive: true,
            );
            if (mounted) setState(() => _dialogResult = result ? '已确认' : '已取消');
          },
        ),
        DwyButton(
          label: '打开底部面板',
          variant: DwyButtonVariant.secondary,
          onPressed: () => showDwySheet<void>(
            context: context,
            title: '操作面板',
            builder: (sheetContext) => Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                const Text('内容可滚动，支持安全区域和键盘避让。'),
                const SizedBox(height: 20),
                DwyTextField(controller: _name, label: '试着唤起键盘'),
                const SizedBox(height: 20),
                DwyButton(
                  label: '关闭面板',
                  onPressed: () => Navigator.of(sheetContext).pop(),
                ),
              ],
            ),
          ),
        ),
      ],
    ),
    Text('弹窗结果：$_dialogResult'),
  ]);

  Widget _statusExamples() => _panel('切换实际展示状态', [
    Wrap(
      spacing: 8,
      runSpacing: 8,
      children: [
        for (final entry in const {
          '空结果': DwyStatusKind.empty,
          '加载中': DwyStatusKind.loading,
          '错误': DwyStatusKind.error,
        }.entries)
          ChoiceChip(
            label: Text(entry.key),
            selected: _status == entry.value,
            onSelected: (_) => setState(() => _status = entry.value),
          ),
      ],
    ),
    DwyStatusView(
      kind: _status,
      title: switch (_status) {
        DwyStatusKind.empty => '这里还没有内容',
        DwyStatusKind.loading => '正在加载演示',
        DwyStatusKind.error => '暂时无法获取内容',
      },
      message: _status == DwyStatusKind.loading
          ? '不确定进度使用加载指示，不伪造百分比。'
          : '说明与重试动作由调用方提供。',
      action: _status == DwyStatusKind.error
          ? DwyButton(
              label: '重试演示',
              onPressed: () => setState(() => _status = DwyStatusKind.empty),
            )
          : null,
    ),
  ]);

  Widget _panel(String title, List<Widget> children) => DecoratedBox(
    decoration: BoxDecoration(
      color: Theme.of(context).colorScheme.surface,
      borderRadius: BorderRadius.circular(
        DwyTheme.tokensOf(context).groupRadius,
      ),
    ),
    child: Padding(
      padding: const EdgeInsets.all(24),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text(title, style: Theme.of(context).textTheme.titleMedium),
          for (final child in children) ...[const SizedBox(height: 16), child],
        ],
      ),
    ),
  );

  void _countClick() => setState(() => _clicks++);

  Future<void> _simulateOperation() async {
    setState(() => _loading = true);
    await Future<void>.delayed(const Duration(seconds: 1));
    if (!mounted) return;
    setState(() => _loading = false);
    _notice('演示操作完成');
  }

  void _notice(String message) =>
      ScaffoldMessenger.of(context)
          .showSnackBar(SnackBar(content: Text(message)));
}
