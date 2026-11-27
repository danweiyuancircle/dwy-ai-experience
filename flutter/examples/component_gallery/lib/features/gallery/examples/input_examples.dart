import 'package:cupertino_ui/cupertino_ui.dart';
import 'package:dwy_design/dwy_design.dart';

/// State ids: default, error (external errorText), disabled.
class TextFieldExample extends StatefulWidget {
  const TextFieldExample({required this.state, super.key});

  final String state;

  @override
  State<TextFieldExample> createState() => _TextFieldExampleState();
}

class _TextFieldExampleState extends State<TextFieldExample> {
  final _name = TextEditingController();
  final _form = GlobalKey<FormState>();
  String _result = '';

  @override
  void dispose() {
    _name.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final disabled = widget.state == 'disabled';
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        Form(
          key: _form,
          child: DwyTextField(
            controller: _name,
            label: '名称',
            hintText: '输入一个名称',
            helperText: '校验规则由业务调用方提供。',
            clearLabel: '清除名称',
            enabled: !disabled,
            errorText: widget.state == 'error' ? '名称已被占用' : null,
            validator: (value) => value!.trim().isEmpty ? '名称不能为空' : null,
          ),
        ),
        const SizedBox(height: 16),
        Align(
          alignment: Alignment.centerLeft,
          child: DwyButton(
            label: '验证输入',
            onPressed: disabled
                ? null
                : () {
                    final valid = _form.currentState!.validate();
                    setState(
                      () => _result = valid ? '输入有效：${_name.text}' : '请检查输入',
                    );
                  },
          ),
        ),
        if (_result.isNotEmpty)
          Padding(
            padding: const EdgeInsets.only(top: 12),
            child: Text(_result),
          ),
      ],
    );
  }
}

/// State ids: default, disabled.
class SearchFieldExample extends StatefulWidget {
  const SearchFieldExample({required this.state, super.key});

  final String state;

  @override
  State<SearchFieldExample> createState() => _SearchFieldExampleState();
}

class _SearchFieldExampleState extends State<SearchFieldExample> {
  static const _items = ['按钮', '输入框', '设置行', '分组', '空状态', '弹窗'];
  final _search = TextEditingController();
  String _query = '';

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) => Column(
    crossAxisAlignment: CrossAxisAlignment.stretch,
    children: [
      DwySearchField(
        controller: _search,
        hintText: '搜索示例组件',
        clearLabel: '清除搜索',
        enabled: widget.state != 'disabled',
        onChanged: (value) => setState(() => _query = value),
      ),
      const SizedBox(height: 8),
      for (final value in _items.where((value) => value.contains(_query)))
        CupertinoListTile(
          title: Text(value),
          leading: const Icon(CupertinoIcons.square_grid_2x2),
        ),
    ],
  );
}
