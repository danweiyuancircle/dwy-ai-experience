# DWY Flutter UI 首版实现与自审

## 结论

开发交付状态：**未完成验收**。首版源码、12 项测试源码和 Web Playground 入口已完成。当前机器未找到 Flutter/Dart SDK，无法执行 Dart 格式化、分析、测试、构建及真实界面验收；静态文件检查通过不能代替这些检查。

## 范围与快照

- 基准：共享仓库 `develop`，HEAD `e5cc65e5`，开始时工作树干净。
- 新增路径仅 `flutter/`；未修改 Apple、CLI、后端或其他产品。
- 快照：添加本报告前 25 文件，14 Dart 文件；SHA-256 `73d14e1c222785021d0abb8302b6d492da160a048e6a678401e686095d4dab65`，按文件路径排序依次合并根相对路径、零字节及文件内容计算。
- 审查方式：开发者自审，无独立审查或真实设备验收。
- 不提交、推送、发布，不安装 SDK、插件或第三方依赖。

## 已实现

- `flutter/packages/dwy_design`：品牌、主题、几何令牌；主/次/文字/危险按钮；加载与禁用状态；受控输入、搜索、清除、业务校验；设置行和分组；空/加载/错误；确认弹窗和可滚动底部面板。
- 浅深主题采用中性背景和蓝色强调，保留系统文字缩放；支持品牌、令牌和组件主题三级覆盖，不使用 Android 壁纸动态色。
- `flutter/examples/component_gallery`：主题/品牌/圆角/组件覆盖、按钮计数、异步本地演示、表单验证、本地搜索、设置开关、确认结果和内容状态切换。
- 展示应用在宽屏使用侧栏，窄屏使用抽屉；Web 宿主入口已提供。
- 使用 SDK Material 兼容导入，未引入独立 `material_ui` 或其他运行时库。

## 验证

已执行：

1. 对全部 25 个新增文件运行 `git diff --no-index --check /dev/null <file>`，无 whitespace 问题。
2. 使用机器已有 PyYAML 解析全部 4 个 YAML 文件，通过。
3. 使用 Python 标准 HTMLParser 读取 Web 入口，通过。
4. 检查无本机绝对路径、无未批准第三方依赖，无越界修改。

未执行：`dart format`、`flutter pub get`、`flutter analyze`、`flutter test`、`flutter build web`、浏览器与 iOS/Android 验收。12 项测试源码的精确清单见两个 `test/TEST_CASES.md`，不得标为 PASS。

## 自审发现与处理

- 已修复禁用设置行仍可能触发独立尾部开关的问题：禁用时阻止尾部指针事件，并新增测试。
- 已在确认弹窗显示前读取主题圆角，避免弹窗 builder 保留并读取可能已经失效的调用方 context。
- 表单与搜索控制器由宿主持有和释放；组件不创建产品全局单例，也不持有网络任务。
- 确认操作仅 true 表示接受，遮罩、系统返回及取消均 false；不在组件内部执行破坏操作。
- 基础 UI 不依赖产品、业务仓或其他 Feature。演示状态只在 Playground。
- 默认主色/文字对比度、任意品牌明暗文字选择、大字体布局等已有针对性测试源码，但仍待执行。

## 剩余验证与接入

1. 主任务确认并准备合格的稳定 Flutter SDK，核对已抽离 Material 的 SDK 兼容导入与 API，必要时经依赖选型后改用独立包。
2. 首次解析并保留工作区锁文件；执行格式化、分析和 12 项测试，修复所有实际发现。
3. 启动 Web Playground：`http://127.0.0.1:5188/`，检查交互和布局。
4. 生成 iOS/Android 宿主后检查系统返回、键盘、大字体、安全区域和真实设备；目前只有 Web 宿主，不宣称双端可交付。
5. 分发许可证、最终 SDK 版本和 CI 尚未确定，包保持 `publish_to: none`，不执行发布。

## 复用决定

采用 Flutter 官方 Material 交互实现，通过 `dwy_design` 统一视觉和受控组件约束。未重写文本编辑、焦点、滚动、表单或原生权限流程。网络、日志、相册、存储、图片加载和产品模板归后续独立任务，本次没有空壳包或推测性插件接口。

## Playground 图片接入（增量）

### 四项核对与官方 Skill

- 已再次读取 `flutter/AGENTS.md`、团队 `dwy-flutter-development` 及 tooling 路由；在理解图片能力前用 CodeGraph 读取 `DwyImage`、`DwyImageSource`、`DwyImageCache` 的当前源码。
- 已实际读取本机官方副本，并在线核对 `flutter/agent-plugins` 的 [responsive-layout](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-build-responsive-layout/SKILL.md)、[widget-test](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-add-widget-test/SKILL.md)、[widget-preview](https://github.com/flutter/agent-plugins/blob/main/skills/flutter-add-widget-preview/SKILL.md)。三份 metadata last_modified 均为 2026-04-21。
- 采用可用宽度 `LayoutBuilder` + Wrap/受限宽度，保留系统文字缩放；按 test → pumpWidget → input/tap → pump → expect 编写三项增量 widget 测试；Preview 使用无必填参数顶层入口、明确尺寸、memory 图片，不调用原生插件。
- MCP：本轮实际工具目录未暴露 Dart/Flutter MCP；不把可发现官方服务等同于已连接。
- CLI：子任务开始时 `command -v flutter; command -v dart` 无输出；随后主代理核实 SDK 已存在且 PATH 未覆盖。主代理已核验 Flutter 3.47.9 stable / Dart 3.13.7 / revision c197ca5，本子任务按调度要求不并行运行共享 CLI，以免争用解析锁。
- SDK/目标：Gallery 提升最低 Flutter 3.47 / Dart 3.13 以匹配官方 Widget Preview；图片包自身最低 Flutter 3.44 / Dart 3.12，可由目标 SDK 满足。移动基线 iOS18 / Android10 minSdk29 不变；本子任务不生成或宣称验收原生宿主。

### 实现范围

- Gallery 直接依赖已批准的 `dwy_image`，增加“图片”目录页。
- 本地 Asset 与 Memory 共用自制 `assets/sample.png`；默认无外部请求。
- 物理解码尺寸、圆角控制；明确无效内存图片的错误/重试与修复示例。
- 网络地址由用户输入并点击加载；无凭据/片段的 HTTP(S) 校验在创建缓存前执行，不默认配置远程域名或认证头。
- Scope A/B 使用独立缓存，清理先卸载当前消费者并等帧，再 await 当前 scope clear；关闭页面保留当前维护链后逐个 clear/dispose，每项失败报告且继续释放其余缓存。
- 只绑定127.0.0.1的可选 `tool/image_fixture.dart`：正常、延迟1秒、首次503后恢复、404四类端点；只读取仓库PNG。
- `lib/previews/image_previews.dart` 增加浅深主题两个官方 `@Preview` 入口，不安装第三方预览库。

### 增量验证状态

增加 `test/image_examples_test.dart` 三项测试源码：默认本地来源与失败修复、非法URI与空scope清理、320宽/2倍字体布局。源码和测试由本子任务完成，但共享 CLI 的格式化、分析、widget 测试、Web/Preview、HTTP fixture 及真实设备验证交主代理串行执行，当前不能标为 PASS。

PNG fixture使用Python标准库生成并核对PNG chunk CRC、96×64尺寸、内存base64与asset字节一致；这不是Flutter解码/视觉验收。Web磁盘缓存能力与移动端不同，不能凭Playground展示声称移动端磁盘隔离通过。
