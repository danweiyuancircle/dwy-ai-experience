# DWY Flutter 默认设计系统

## 默认主题

| 语义 | 浅色 | 深色 |
| --- | --- | --- |
| 品牌主色 | `#2563EB` | 从品牌种子生成适合深色背景的主色 |
| 页面背景 | `#F8FAFC` | `#0F172A` |
| 内容表面 | `#FFFFFF` | `#18212F` |
| 主要文字 | `#0F172A` | `#F1F5F9` |
| 次要文字 | `#64748B` | `#94A3B8` |
| 分隔线 | `#E2E8F0` | `#334155` |

正文基准 16 逻辑像素，保留 Flutter 系统文字缩放。按钮与输入框圆角 12、分组圆角 16，间距基准 4、8、12、16、24，交互控件最小高度 48。浅色大面积表面保持中性，不使用壁纸动态取色。

### 文字与组件层级

采用清爽、克制的工具界面：页面标题 `titleLarge` 22/600，分区或内容标题 `titleMedium` 17/600，小标题 `titleSmall` 15/600，正文 16，辅助信息 `bodySmall` 13。按钮文字 15/600，底部导航标签 12/500。字号为逻辑像素，不禁用系统文字缩放。

`DwyTheme.create` 同时配置 AppBar、按钮、输入框、Card、ListTile、NavigationBar、SegmentedButton、Chip 和 Dialog。Card 无阴影和默认描边，内容用留白与分隔线分组；选中状态使用低饱和品牌底色，文字采用从品牌种子生成的对比色；输入聚焦边框保留品牌色，错误和禁用反馈由 Material 组件继续处理。

产品优先使用 `Theme.of(context).textTheme`、`colorScheme` 与 `DwyTheme.tokensOf(context)`，避免在页面重复写字号、固定颜色和圆角。原生 Card 等组件直接消费根主题，无需再包装一层同名组件。产品的拍照入口、记录布局和提醒规则仍归应用，不放入基础库。

`DwySettingsTile` 继承根 ListTileTheme 的间距与标题样式；`showDwyConfirmation` 继承 DialogTheme。原有品牌、令牌和 ThemeData.copyWith 定制入口保持可用。公共主题更改会影响所有升级该源码版本的消费者，升级时应检查局部主题覆盖与实际页面。

## 应用层接入与三级定制

```dart
import 'package:dwy_design/dwy_design.dart';
import 'package:material_ui/material_ui.dart';

void main() => runApp(const ExampleApp());

class ExampleApp extends StatelessWidget {
  const ExampleApp({super.key});

  @override
  Widget build(BuildContext context) => MaterialApp(
        theme: DwyTheme.create(brightness: Brightness.light),
        darkTheme: DwyTheme.create(brightness: Brightness.dark),
        themeMode: ThemeMode.system,
        home: Scaffold(
          body: Center(
            child: DwyButton(label: '继续', onPressed: () {}),
          ),
        ),
      );
}
```

1. 品牌：向 `DwyTheme.create` 传入 `DwyBrand(primary: ..., fontFamily: ...)`；字体由应用声明和打包。
2. 令牌：传入 `DwyTokens` 调整几何；传入 `ColorScheme` 覆盖完整语义颜色。提供完整 ColorScheme 时，其 brightness 应与主题一致，且由应用验收对比度。
3. 组件：在返回的 ThemeData 上 `copyWith` 覆盖 `filledButtonTheme` 等，或给具体 `DwyButton` 传 `ButtonStyle`。覆盖主题扩展列表时须保留 `DwyTokens`。

组件读取实际 `ThemeData`；没有另建全局主题缓存。需要 `DwyTokens` 的组件要求根主题由 `DwyTheme.create` 生成，缺失会明确报配置错误。

## 公共组件

| 组件 | 状态与调用约束 |
| --- | --- |
| `DwyButton` | primary / secondary / subtle / danger；loading 保留文字并阻止点击；异步任务归调用方 |
| `DwyTextField` | controller 和 FocusNode 由调用方持有、释放；校验与文案由业务提供 |
| `DwySearchField` | 搜索与清除回调，不发请求；清除按钮文案由调用方本地化 |
| `DwySettingsTile` | 标题、说明可换行；有独立交互 trailing 时不再给整行叠加 onTap |
| `DwySettingsGroup` | 中性分组表面、分隔线、标题和脚注，不带产品路由 |
| `DwyStatusView` | empty / loading / error；重试动作和错误描述由调用方决定，不伪造进度 |
| `showDwyConfirmation` | 仅确认返回 true，返回/遮罩/取消均为 false；操作在结果之后由调用方执行 |
| `showDwySheet` | 安全区域、键盘避让和可滚动内容；builder 内通过 Navigator.pop 返回结果 |

这套 UI 不按系统切换 Cupertino。系统返回、输入、滚动与安全区域继续使用 Flutter 的平台能力。系统权限、相册与分享界面不在 UI 包内重画。

## 验证要求

主题对比度、品牌定制和组件交互使用 widget 测试；展示应用需在窄屏/桌面、大字体、浅/深色及 iOS/Android 上核验布局。底部面板还需在真实软键盘和手势导航下检查，模拟窗口不能替代这些结果。
