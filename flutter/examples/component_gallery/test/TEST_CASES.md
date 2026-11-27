# Playground 交互测试

2026-11-27：Flutter3.50.0 / Dart3.14.0，27项测试通过（`catalog_test.dart` 16项、`gallery_test.dart` 8项、`image_examples_test.dart` 3项）。浏览器截图见下方，真实设备与 iOS / macOS 构建未执行。

## catalog_test.dart：目录防漂移

| 测试 | 目标 |
| --- | --- |
| dwy_design / dwy_image / every public export has a catalog entry | 解析包入口 `lib/{package}.dart` 的 `export 'src/*.dart'`，公开的 `Dwy*` 类型、typedef 与 `showDwy*` 函数都必须出现在目录条目的 `symbols` |
| dwy_design / dwy_image / catalog lists no symbol that is no longer exported | 反向检查：目录里不能残留已删除或改名的符号 |
| export scan sees representative symbols | 防止正则失效导致扫描结果为空而空过 |
| ids and names are unique | 条目 id、name 唯一 |
| 每个条目一项：documents purpose, capabilities and a Dart example | 摘要、能力、约束非空；`symbols` 含组件名；示例代码含组件名；状态 id 不重复 |

新增公开 API 时，在 `lib/catalog/catalog.dart` 增加或扩充条目，否则 `every public export has a catalog entry` 失败。

## gallery_test.dart：交互

| 测试 | 目标 |
| --- | --- |
| theme preview shares selection between controls | 主题页分段选择与底部导航共享选择 |
| brand color switch updates the app theme | 切换品牌色后 `CupertinoApp` 主题主色变化 |
| desktop gallery changes theme and exercises button state | 桌面侧栏、深色切换、按钮计数、重置示例、异步演示 |
| state selector switches the displayed status view | 状态切换显示空/错误视图，重试计数与重置 |
| catalog search filters entries and reports no match | 目录搜索过滤与无匹配提示 |
| component detail lists capabilities, constraints and code | 详情页展示能力、约束、Dart 示例和复制按钮 |
| phone directory sheet exposes form validation and a clearable search | 窄屏目录面板、表单错误/恢复、本地搜索及清除 |
| glass navigation entry explains limits and opens the demo | 玻璃导航栏条目说明纯色背景限制；示例页首个色块不被导航栏盖住；返回可用 |

## image_examples_test.dart：图片

| 测试 | 目标 |
| --- | --- |
| image examples default to local sources and repair decode failure | 默认仅asset/memory；错误重试保持失败、修复后显示有效图 |
| network example rejects invalid URI before creating a cache | 非HTTP地址在创建缓存前拒绝，空scope清理不调用原生缓存 |
| image controls wrap in a narrow large-text viewport | 320宽、两倍字体下图片和控件不溢出 |

执行：在 `flutter/examples/component_gallery` 运行 `flutter test`。

## Web 浏览器截图（2026-11-27，Playwright）

`flutter build web --release` 后用 `python3 -m http.server 8090 --directory build/web` 访问 `http://127.0.0.1:8090/`，截图保存在仓库根 `.playwright-mcp/`：1280x800 的首页、按钮状态切换、主题与令牌深色页；430x900 的首页、目录面板、状态错误页、玻璃导航栏示例（深色）。

人工检查：浅深主题、三种品牌色、圆角令牌、组件主题覆盖、弹窗确认/取消、Sheet软键盘、系统大字体、320/390/1440宽度。真实设备检查尚未执行；iOS / macOS 宿主已生成但因本机 Xcode 不完整、未安装 CocoaPods，未构建、未运行。
