# Apple 项目四层分包实施计划

> 执行方式：主代理负责生成器与集成；独立任务更新文档和架构检查，最后独立审查。用户已确认执行，不重复请求批准。

**目标：** 新项目按四层架构生成 iOS、macOS 或双平台形态，已有项目可安全追加另一平台。

**架构：** App（①）、Features/BusinessUI（②）、本产品 BizFoundation 与按需的平台业务实现（③）、AppleAppKit（④）。平台目录和 SPM 包是部署、隔离单位，不增加逻辑层级。

**技术：** 现有 Bash/Python 标准库、SwiftPM、XcodeGen，无新运行时依赖。

**依据：** `docs/superpowers/specs/2026-11-17-apple-project-architecture-design.md`，以及用户追加的“双端内部仍为四层”。

## 约束与审查重点

- 不覆盖已有工程，不改变全局 Xcode 选择，不修改全局 Skills，不提交或发布。
- iOS 18+；macOS 26+、arm64；外部 AppleAppKit 精确版本，内部包相对 path。
- BusinessUI 满足业务定制才创建实现，不为共享控件套壳；③禁止依赖 UI 和 App。
- 双端包引用同一业务核心，App sources 不编译另一端、业务核心或已由包编译的实现。
- 追加平台保留已有源码、manifest 与版本；无效参数、重复目标、版本分歧、遗漏/重复源码必须明确失败。

## 任务

- [x] 1. 重写 `apple/Tests/test_templates.py`：三种真实生成物、重复目标和无效输入拒绝、追加平台保留原文件、UI 检查。先运行并确认新布局断言失败。
- [x] 2. 更新 `apple/scripts/new-app.sh` 与 `apple/Templates`：common 中只维护一份产品核心；平台模板链接 `../packages/<Product>Core`；新增 apple 和安全追加平台入口。
- [x] 3. 新增 `apple/Templates/common/scripts/check-architecture.py` 与回归：调用原生 XcodeGen/SwiftPM 读取结构，验证四层依赖、跨平台源码、版本声明和已有锁文件；语义边界明确留审查。
- [x] 4. 同步规范、Skill、模板说明，记录 ADBox 当前结构映射与审计限制；更新 `apple/Tests/TEST_CASES.md`。
- [x] 5. 运行模板完整回归，真实生成三种形态，XcodeGen/SwiftPM 验证与目标构建；运行生成包单测。记录外部解析、编译和 UI 验收的实际边界。
- [x] 6. 独立审查并修复本轮阻断，回归受影响检查，更新方案与验收记录。

结果：34 项 Python 回归和生成物的 5 项 Swift 单测通过，生成的两平台 App 构建通过。CI 补齐固定 XcodeGen 与归档 SHA-256 验证，工作流只做本地 YAML 语法检查，未触发远端执行。详情见 `docs/superpowers/reports/2026-11-17-apple-project-architecture-validation.md`。
