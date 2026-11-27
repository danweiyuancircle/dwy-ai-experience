import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

/// State ids: normal, destructive.
class ConfirmationExample extends StatefulWidget {
  const ConfirmationExample({required this.state, super.key});

  final String state;

  @override
  State<ConfirmationExample> createState() => _ConfirmationExampleState();
}

class _ConfirmationExampleState extends State<ConfirmationExample> {
  String _result = '尚未操作';

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Align(
        alignment: Alignment.centerLeft,
        child: DwyButton(
          label: '打开确认弹窗',
          onPressed: () async {
            final result = await showDwyConfirmation(
              context: context,
              title: '确认演示操作？',
              message: '此示例不会删除文件或修改真实数据。',
              confirmLabel: '确认',
              cancelLabel: '取消',
              destructive: widget.state == 'destructive',
            );
            if (mounted) {
              setState(() => _result = result ? '已确认' : '已取消');
            }
          },
        ),
      ),
      const SizedBox(height: 12),
      Text('弹窗结果：$_result'),
    ],
  );
}

/// Single state; the sheet owns a text field to exercise keyboard avoidance.
class SheetExample extends StatefulWidget {
  const SheetExample({super.key});

  @override
  State<SheetExample> createState() => _SheetExampleState();
}

class _SheetExampleState extends State<SheetExample> {
  final _name = TextEditingController();
  String _result = '尚未操作';

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      Align(
        alignment: Alignment.centerLeft,
        child: DwyButton(
          label: '打开底部面板',
          variant: DwyButtonVariant.secondary,
          onPressed: () async {
            final result = await showDwySheet<String>(
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
                    onPressed: () => Navigator.of(sheetContext).pop('已关闭'),
                  ),
                ],
              ),
            );
            if (mounted) setState(() => _result = result ?? '已下滑关闭');
          },
        ),
      ),
      const SizedBox(height: 12),
      Text('面板结果：$_result'),
    ],
  );
}
