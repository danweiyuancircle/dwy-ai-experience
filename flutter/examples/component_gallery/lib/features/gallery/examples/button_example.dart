import 'dart:async';

import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

/// State ids: default, loading (primary shows its spinner), disabled.
class ButtonExample extends StatefulWidget {
  const ButtonExample({required this.state, super.key});

  final String state;

  @override
  State<ButtonExample> createState() => _ButtonExampleState();
}

class _ButtonExampleState extends State<ButtonExample> {
  int _clicks = 0;
  bool _busy = false;
  String? _result;

  @override
  Widget build(BuildContext context) {
    final disabled = widget.state == 'disabled';
    final VoidCallback? count = disabled
        ? null
        : () => setState(() => _clicks++);
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Wrap(
          spacing: 12,
          runSpacing: 12,
          children: [
            DwyButton(
              label: '主要操作',
              icon: CupertinoIcons.add,
              loading: widget.state == 'loading',
              onPressed: count,
            ),
            DwyButton(
              label: '次要操作',
              variant: DwyButtonVariant.secondary,
              onPressed: count,
            ),
            DwyButton(
              label: '文字操作',
              variant: DwyButtonVariant.subtle,
              onPressed: count,
            ),
            DwyButton(
              label: '危险操作',
              variant: DwyButtonVariant.danger,
              onPressed: count,
            ),
            DwyButton(
              label: '演示异步操作',
              loading: _busy,
              onPressed: disabled ? null : _simulate,
            ),
          ],
        ),
        const SizedBox(height: 16),
        Text('已点击 $_clicks 次'),
        if (_result case final result?)
          Semantics(liveRegion: true, child: Text(result)),
      ],
    );
  }

  Future<void> _simulate() async {
    setState(() {
      _busy = true;
      _result = null;
    });
    await Future<void>.delayed(const Duration(seconds: 1));
    if (!mounted) return;
    setState(() {
      _busy = false;
      _result = '演示操作完成';
    });
  }
}
