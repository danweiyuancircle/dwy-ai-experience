import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

/// State ids: default, disabled (every row disabled, including trailing switches).
class SettingsExample extends StatefulWidget {
  const SettingsExample({required this.state, super.key});

  final String state;

  @override
  State<SettingsExample> createState() => _SettingsExampleState();
}

class _SettingsExampleState extends State<SettingsExample> {
  bool _notifications = true;
  bool _sync = false;
  String? _feedback;

  @override
  Widget build(BuildContext context) {
    final enabled = widget.state != 'disabled';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        DwySettingsGroup(
          title: '设置分组',
          footnote: '整行跳转和独立开关分别处理，不叠加重复点击行为。',
          children: [
            DwySettingsTile(
              title: '通知偏好',
              subtitle: '仅演示本地开关，不申请系统权限。',
              leading: const Icon(CupertinoIcons.bell),
              enabled: enabled,
              trailing: CupertinoSwitch(
                value: _notifications,
                onChanged: (value) => setState(() => _notifications = value),
              ),
            ),
            DwySettingsTile(
              title: '同步偏好',
              leading: const Icon(CupertinoIcons.arrow_2_circlepath),
              enabled: enabled,
              trailing: CupertinoSwitch(
                value: _sync,
                onChanged: (value) => setState(() => _sync = value),
              ),
            ),
            DwySettingsTile(
              title: '可跳转的设置行',
              subtitle: '支持说明文字自动换行和系统大字体。',
              leading: const Icon(CupertinoIcons.info_circle),
              enabled: enabled,
              onTap: () => setState(() => _feedback = '已点击设置行'),
            ),
            const DwySettingsTile(
              title: '暂不可用',
              leading: Icon(CupertinoIcons.lock),
              enabled: false,
            ),
          ],
        ),
        if (_feedback case final feedback?)
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Semantics(liveRegion: true, child: Text(feedback)),
          ),
      ],
    );
  }
}

/// State ids: empty, loading, error.
class StatusExample extends StatefulWidget {
  const StatusExample({required this.state, super.key});

  final String state;

  @override
  State<StatusExample> createState() => _StatusExampleState();
}

class _StatusExampleState extends State<StatusExample> {
  int _retries = 0;

  @override
  Widget build(BuildContext context) {
    final kind = DwyStatusKind.values.byName(widget.state);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        DwyStatusView(
          kind: kind,
          title: switch (kind) {
            DwyStatusKind.empty => '这里还没有内容',
            DwyStatusKind.loading => '正在加载演示',
            DwyStatusKind.error => '暂时无法获取内容',
          },
          message: kind == DwyStatusKind.loading
              ? '不确定进度使用加载指示，不伪造百分比。'
              : '说明与重试动作由调用方提供。',
          action: kind == DwyStatusKind.error
              ? DwyButton(
                  label: '重试演示',
                  onPressed: () => setState(() => _retries++),
                )
              : null,
        ),
        if (_retries > 0)
          Semantics(
            liveRegion: true,
            child: Text('已触发重试 $_retries 次', textAlign: TextAlign.center),
          ),
      ],
    );
  }
}
