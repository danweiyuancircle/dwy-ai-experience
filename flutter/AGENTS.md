# Flutter 工作区开发约束

本目录遵循仓库根规则，团队规范真源位于 `dwy-cli/templates/ai-tools/skills/Flutter/`。Dart 代码使用 `dwy-dart-development`，分层与抽取使用 `dwy-flutter-architecture`，Widget 与平台使用 `dwy-flutter-development`，消费自有包使用 `dwy-flutter-appkit`；按任务组合，不要求每次全读。修改规范应同步核对本入口，不复制完整 Skill。

## 必须使用官方 Skills 与 CLI

- 开发前必须核对四项：匹配官方 Skill、当前已连接 MCP、实际 CLI 路径/版本及 SDK/目标平台。Flutter iOS/Android 宿主须同时核对原生工具链；本轮证据未变可复用，不能只读 Skill 就跳过环境适配。

- 每项 Flutter 开发先读取并使用匹配的 `flutter/agent-plugins` 官方 Skill；纯 Dart 子任务同时使用 `dart-lang/skills` 的匹配 Skill。先读团队 Skill 的 `references/dwy-flutter-tooling.md` 选择入口，不能只读本地规范就宣称已使用官方 Skill。
- 可以读取已安装官方副本或官方仓库的 `SKILL.md` 及必要引用，不擅自安装整套插件、MCP 或全局工具。来源不可用时报告缺口。
- 任务记录注明官方 Skill 来源、采用的工作流、实际命令及未完成项。匹配的官方示例不覆盖用户已选底座和安装授权。
- 创建宿主、分析、格式化、测试、运行、构建使用官方 Flutter/Dart CLI 或已核实的官方 MCP；不手拼原生工程冒充 CLI 生成，不手写代码生成产物。

## 产品与包边界

- 工作区开发工具链固定 Flutter 3.50.0 stable / 内置 Dart 3.14.0，具体来源、UI 包与验证范围见 `flutter/docs/development-baseline.md`。首次封装的全部包从此基线开始：Dart 下限统一为 3.14，依赖 Flutter 的包下限统一为 3.50；不保留旧版兼容入口、适配层或旧下限。不自动升级到下一补丁或浮动 latest/stable。
- UI 使用独立 `material_ui`；公开主题与组件类型不能混用 SDK 内置 Material 类型。兼容桥只解决旧 Widget 上下文，不解决公开类型冲突。
- 统一移动端基线：iOS 18+，Android 10+（minSdk 29）。targetSdk/compileSdk 分别核实；插件升级不得静默提高最低支持版本。
- 四层：Assembly、Features、BizFoundation、Foundation；业务包不得依赖 Widget、设计主题和应用路由；Feature 互不引用。
- UI 以 Material 3 + DWY 主题统一双端风格；不默认切 Cupertino/adaptive 外观，不加玻璃材质。必要平台行为单独适配。
- 默认清爽中性灰白 + 蓝强调色，浅深跟随系统；产品可覆盖品牌、令牌、组件主题。新组件提供 Playground 示例及必要测试。
- 网络 Dio、日志 logger、偏好 shared_preferences、安全存储 flutter_secure_storage、数据库 Drift/SQLite、相册 photo_manager/image_picker、图片 cached_network_image 是当前用户选定底座；精确版本、传递依赖和原生约束仍须核实。
- 共享包按需依赖，无 UI 插件不等于纯 Dart。基础包不包含产品 DTO、数据库表、全局认证或导航。
- 每个成员声明直接依赖，workspace 统一解析；测试依赖与 SDK 的 flutter_test 约束一起检查，不随意 overrides 或删除锁文件。

## 验证与交付

- 修改公共能力同步 README、TEST_CASES.md、导出与消费者；执行对应的分析、测试和必要构建。
- 代码生成先运行已选官方/生态工具，再分析测试；SDK 或设备缺失时明确阻断，不把文件语法检查写成运行通过。
- 分开记录依赖解析、分析、单测、构建、Web Playground、模拟器及真机结果；Web 预览不能证明相册、安全存储或移动端系统交互通过。
- SDK、工具及全局插件安装沿用工具发现规则；确认安装方案前不执行下载后的代码，不自动升级环境。
