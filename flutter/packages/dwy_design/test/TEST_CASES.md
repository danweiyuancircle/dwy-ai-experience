# dwy_design 测试用例

2026-11-18：Flutter3.50.0 / Dart3.14.0，独立 material_ui1.11.0，15项测试通过；原生设备和视觉验收另行记录。

| 文件 / 测试 | 目标 |
| --- | --- |
| `components_test.dart` / settings subtitle respects theme and disabled colors | 设置说明继承消费方 ListTileTheme 的字号与颜色，禁用时继承系统禁用文字色 |
| `theme_test.dart` / Brightness.dark、Brightness.light shares typography and quiet component surfaces | 两种主题共享文字层级、卡片/导航/弹窗表面，选中文字对比度，导航禁用样式委托原生默认，分段按钮禁用优先于选中状态（2项） |
| `components_test.dart` / Brightness.dark、Brightness.light themed controls fit and retain selection | 320宽、2倍文字下卡片/列表/分段按钮/导航不溢出，分段和导航仍能改变选择（2项） |
| `theme_test.dart` / default theme keeps neutral surfaces and accessible brand text | 公开 ThemeData 与独立 Material 类型一致，默认浅色令牌与主色、次要文字对比度 |
| `theme_test.dart` / brand and geometry are injected without changing component API | 品牌覆盖、按钮与分段控件高度，卡片与弹窗圆角随token变化，品牌文字对比度 |
| `theme_test.dart` / dark theme has distinct surfaces and readable semantic text | 深色表面层级及文字对比度 |
| `components_test.dart` / loading button blocks actions and retains its accessible label | 加载状态防重复且保留操作文字，恢复后可点击 |
| `components_test.dart` / search clear updates controller and parent callback | 清除内容同步调用方，不残留清除按钮 |
| `components_test.dart` / input exposes form validation without owning application rules | Form 校验规则来自调用方 |
| `components_test.dart` / disabled settings row also blocks its trailing control | 禁用设置行也阻止尾部开关响应 |
| `components_test.dart` / confirmation returns explicit choice; dismiss is not acceptance | 确认和取消结果明确 |
| `components_test.dart` / bottom sheet scrolls content and returns the explicit result | 长内容滚动，关闭时返回指定结果 |
| `components_test.dart` / settings and status fit a narrow screen with large text | 320宽、2倍文字下设置与状态组件不溢出 |

执行：在 `flutter/packages/dwy_design` 运行 `flutter test`。需要先在工作区成功解析 SDK 依赖。
