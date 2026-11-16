# Flutter 3.50 升级与 Skills 拆分

## 结论

本地 SDK 已升级并回读 Flutter 3.50.0 channel stable / Dart 3.14.0，框架提交与官方正式标签一致。依赖解析、独立 Material 迁移与四个团队 Skills 已落地；运行检查结果在本记录验证表中分别报告，不能由 SDK 版本或 Web 构建推断原生验收通过。

## 范围与快照

- 日期：2026-11-16。仓库 develop，基准提交 `e5cc65e54ce02706c083329321e692c570409736`。
- 开始时已有 Apple Skills、Flutter Skill、根 AGENTS 修改和未跟踪 flutter 工作区；保留既有内容。没有提交、推送或发布。
- 本次范围：四个 Flutter/Dart Skills、CLI 旧规则映射与发现/同步测试、Flutter 基线/入口文档、UI 包与 Gallery 导入、必要的测试和生成工具链适配。
- SDK：原 PATH 工具链原位升级；保留完整 3.47.9 备份及旧 stable 分支恢复点。未修改 AndroPane 业务源码。其他使用同一 SDK 的项目未回归。
- 审查方式：开发者自审；Skills 另做独立行为情景测试。未做原生设备或浏览器视觉验收。

## 官方能力与采用步骤

- 实际读取 Flutter 官方 `flutter-apply-architecture-best-practices`、`flutter-add-widget-test` 和 Dart 官方 `dart-run-static-analysis` 的 SKILL.md。按四层映射对象职责，先建立类型兼容失败测试，按 dry-run → 定向迁移 → 分析/测试执行。
- 官方来源：`https://github.com/flutter/agent-plugins`、`https://github.com/dart-lang/skills`、`https://docs.flutter.dev/release/breaking-changes/material-ui-and-cupertino-ui`。
- 本会话未暴露已连接 Dart/Flutter MCP，使用现有官方 CLI，没有安装额外插件或版本管理器。SDK 下载原站较慢，采用 Flutter 官方文档列出的 CFUG 镜像作为本次命令的下载源，未改全局镜像配置。
- 升级后最初 detached HEAD 生成了 user-branch 渠道缓存；切回 stable 并重建生成缓存后回读为 stable，版本和 revision 不变。

## 发现与处理

1. 新旧 Material 的 ThemeData 不兼容。主题测试先使用独立库公开类型，旧实现编译失败；官方 `migrate_design_widgets` 定向迁移16处导入，统一设计包、图片包、示例和测试，不添加没有实际需要的兼容桥。
2. UI 三个成员显式依赖升级前锁文件已有的 material_ui 1.11.0，并同步声明 Flutter3.50 / Dart3.14。未使用 Cupertino，不引入额外设计库；纯 Dart 包保留原兼容下限。
3. SDK flutter_test 固定 test_api0.7.14，与数据库原 test1.31.1 冲突；改用 test1.32.0，不添加 overrides。
4. 原 analyzer13.3 只支持 Dart3.13。定向更新 analyzer14.7 后，原 build_runner2.16.1 使用已移除内部 setter，生成失败；同步到 build_runner2.17.1，保留 Drift 运行时版本。
5. 新工具链分析报告5处机械诊断和测试 fake 的 immutable 警告。官方定向 fix 处理导入/tearoff；只在可变测试替身上说明并局部抑制 immutable 误报，没有隐藏产品诊断。
6. 按 Dart、架构、Flutter UI/平台、自有基础包拆成四个 Skills；本地引用可独立安装，其他职责按名称路由，不要求每次全读。旧 core/network 托管规则指向新的 Dart 资料位置，不自动增加用户启用项。
7. 数据库失败迁移测试原来预期裸 StateError，实际 Drift isolate 保留为 DriftRemoteException；断言改为检查远端包装及原始错误文本，继续验证旧文件可重开与数据保留，不改变生产异常语义。
8. 图片测试暴露 flutter_cache_manager3.5.0 创建后立即关闭的竞态：CacheManager.dispose 不等待仓库 open，而 store.dispose 会等待。已有适配层改用 store.dispose；原来失败的三个测试全部通过，保留命名空间隔离、关闭与重新接管断言，没有预热 fixture 掩盖问题。

## 验证

所有命令通过实际 Flutter3.50.0 内置工具链执行。表中检查结果只覆盖对应范围。

| 检查 | 结果 |
| --- | --- |
| SDK version/revision/channel 回读 | 3.50.0 stable / Dart3.14.0；与 development-baseline 一致 |
| flutter pub get | 通过，保留并更新工作区锁文件 |
| Skills 初始发现测试 | 失败，缺三个入口；拆分后通过 |
| Skills 独立行为情景 | 原规则缺少语言版本、公开类型与迁移闸门；新规则正确处理三个情景 |
| CLI 发现、同步与迁移回归 | pnpm test：201/201 通过，包含四个 Skills 独立安装及引用检查 |
| 数据库代码生成 | dart run build_runner build：通过，17秒，8个输出，无旧 analyzer 语言警告 |
| format / analyze | 待最终汇总 |
| 各包及 Gallery 测试 | 73/73 通过：database5、log13、network14、design10、image8、media9、preferences5、secure_storage4、Gallery5 |
| Web 构建 | 待最终汇总 |
| 浏览器视觉、官方 Widget Preview | 未执行 |
| iOS / Android 构建、签名和设备验收 | 未执行；本机 doctor 提示 Android licenses、Xcode/CocoaPods 问题，未扩大安装或接受许可范围 |

## 复用与后续边界

复用官方迁移器、现有 Material 包、组件和测试，没有新增自研 UI 框架或通用抽象。四个 Skills 是仓库模板，未执行全局 refresh，也未擅自给其他项目增加启用项。当前没有 Flutter CI，后续持续验证应固定同一精确工具链；不将一次本地验证描述为已有 CI 保证。

历史首版状态与证据保留在 `flutter/docs/implementation-review.md` 和旧安装提案中；当前开发基线以 `flutter/docs/development-baseline.md` 及本轮验证为准。
