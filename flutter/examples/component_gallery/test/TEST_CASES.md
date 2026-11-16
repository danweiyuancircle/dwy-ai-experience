# Playground 交互测试

2026-11-16：Flutter3.50.0 / Dart3.14.0，5项测试通过；浏览器视觉与真实设备检查另行记录。

| 测试 | 目标 |
| --- | --- |
| desktop gallery changes theme and exercises button state | 桌面目录、深色切换、按钮计数和异步加载演示 |
| phone drawer exposes form validation and a clearable search | 窄屏抽屉、表单错误/恢复、本地搜索及清除 |
| image_examples_test.dart / image examples default to local sources and repair decode failure | 默认仅asset/memory；错误重试保持失败、修复后显示有效图 |
| image_examples_test.dart / network example rejects invalid URI before creating a cache | 非HTTP地址在创建缓存前拒绝，空scope清理不调用原生缓存 |
| image_examples_test.dart / image controls wrap in a narrow large-text viewport | 320宽、两倍字体下图片和控件不溢出 |

执行：在 `flutter/examples/component_gallery` 运行 `flutter test`。

人工检查：浅深主题、三种品牌色、圆角令牌、组件主题覆盖、弹窗确认/取消、Sheet软键盘、系统大字体、320/390/1440宽度。真实设备检查尚未执行。
