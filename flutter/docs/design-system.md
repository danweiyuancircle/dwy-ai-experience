# DWY Flutter 设计系统

iOS 和 Android 共用官方 Cupertino 控件和 DWY 主题。应用声明品牌色和字体，通过根应用配置系统浅深色。常用间距和圆角集中在 `DwyTokens`，有共用样式或交互约定的组件通过 `dwy_design` 使用。

## 应用接入

应用在 pubspec 中声明 `dwy_design`，从其公开入口导入 DWY 组件和常用 Cupertino 控件。共享库统一管理 `cupertino_ui` 与图标字体的版本，Flutter 基础布局通过 `flutter/widgets.dart` 使用。

```dart
import 'package:dwy_design/dwy_design.dart';
import 'package:flutter/widgets.dart';

void main() => runApp(const ExampleApp());

class ExampleApp extends StatelessWidget {
  const ExampleApp({super.key});

  @override
  Widget build(BuildContext context) => CupertinoApp(
    theme: DwyTheme.create(
      brand: const DwyBrand(primary: CupertinoColors.systemTeal),
    ),
    localizationsDelegates: GlobalCupertinoLocalizations.delegates,
    supportedLocales: const [Locale('zh'), Locale('en')],
    builder: (context, child) => DwyTheme.withTokens(
      tokens: const DwyTokens(pageInset: 24),
      child: child!,
    ),
    home: CupertinoPageScaffold(
      navigationBar: const CupertinoNavigationBar(middle: Text('设置')),
      child: SafeArea(
        child: Center(
          child: DwyButton(label: '继续', onPressed: () {}),
        ),
      ),
    ),
  );
}
```

`DwyTheme.create` 返回独立包的 `CupertinoThemeData`。省略亮度时跟随系统。需要自定义令牌时，在根应用的 `builder` 使用 `DwyTheme.withTokens`，页面和弹层通过 `DwyTheme.tokensOf(context)` 读到同一组令牌。单个按钮可通过 `DwyButton.padding` 覆盖内容内边距。

## 共享组件

| 入口 | 共用约定 |
|---|---|
| `DwyButton` | 主、次、文字、危险四种层级，加载时保留标签并禁止重复触发 |
| `DwyTextField`、`DwySearchField` | Cupertino 风格输入，调用方持有控制器和焦点，提供校验、文案、输入长度上限与自动填充语义 |
| `DwySettingsGroup`、`DwySettingsTile` | 圆角分组、可换行标题和说明，独立尾部动作与整行点击由调用方配置 |
| `DwyStatusView` | 空态、加载、错误及调用方提供的重试 |
| `showDwyConfirmation` | 仅确认返回 `true`，其余退出返回 `false` |
| `showDwySheet<T>` | 底部安全区、键盘避让、滚动与拖拽联动，使用 `Navigator.pop(context, result)` 返回结果 |

导航栏、Tab、日期选择器等从 `dwy_design` 导入，使用官方控件原有 API。编辑表单、筛选面板等业务组件放在对应 Feature 或应用共享 UI，由业务层提供数据、校验与动作。跨项目出现相同交互后再评估抽取范围。

Gallery 在 `flutter/examples/component_gallery/`，包含浅深、品牌色、令牌、输入搜索、分组、弹层和图片示例。

## 旧实现归档 · 停用

旧 Material UI 全部源码可从本地 Git 归档标签 `archive/flutter-material-ui-2026-11-20` 恢复。归档指向 `241f504f`，包括旧设计包、图片 UI、Gallery、依赖锁和配套 Skill。仅用于查阅或恢复，新项目采用当前 Cupertino 接入方式。
