# UI 基础库 Flutter 3.50 验证 · Material 历史记录

本页记录停用前的验证。当前界面基线见 `flutter/docs/design-system.md`。

2026-11-16 回读实际工具链：Flutter 3.50.0 stable，framework ab2912035e，Dart 3.14.0。沿用已安装工具链，没有安装或升级额外工具。

已读取团队 Flutter 开发 Skill 和官方 `flutter-add-widget-test`、`dart-run-static-analysis`，采用 WidgetTester 交互测试及 CLI 分析、测试、构建流程。当前会话没有已连接的 Flutter/Dart 官方 MCP，使用同一 SDK 内置 Flutter/Dart CLI。

`dwy_design`、`dwy_image`、`component_gallery` 的最低声明为 Flutter 3.50 / Dart 3.14，直接依赖 `material_ui 1.11.0`。三个成员的源码与测试均使用独立 Material 公开类型，没有旧 `package:flutter/material.dart` 导入；未引入 Cupertino 风格或无实际需求的兼容桥。

| 本轮实际执行 | 结果 |
| --- | --- |
| `flutter analyze packages/dwy_design packages/dwy_image examples/component_gallery` | 通过，无诊断 |
| dwy_design：`flutter test` | 10 项通过 |
| dwy_image：`flutter test` | 8 项通过 |
| component_gallery：`flutter test` | 5 项通过 |
| component_gallery：`flutter build web` | 通过，产物 `flutter/examples/component_gallery/build/web` |
| 工作区：`flutter analyze` | 仍有数据库测试对 Drift experimental remote API 的 1 项警告；UI 三成员无诊断 |

未执行本轮浏览器视觉验收、官方 Widget Preview、iOS/Android 构建及真机验证。Web 编译和 Widget 测试不能替代原生平台验收。未提交、推送或发布。
