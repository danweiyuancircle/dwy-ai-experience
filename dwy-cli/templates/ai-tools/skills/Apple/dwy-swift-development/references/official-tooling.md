# Apple 官方能力与工具链核对

每项 Apple 开发在设计和实现前必须核对以下四项；同一任务中来源、版本、权限、项目和运行目标未变时可以复用本轮证据。核对所有类别，不代表每类都必须找到、安装或实际调用。

| 类别 | 必须核对 | 采用方式 |
| --- | --- | --- |
| 官方 Skill | 匹配技术、实际正文与必要引用、发布来源、适用 SDK | 来源可核实且适用时实际读取使用；无匹配项则记录范围并查 Apple 官方文档 |
| MCP | 当前会话真正暴露的工具、来源、连接状态、权限、项目/设备上下文 | 匹配且已连接时优先复用；只有配置或已安装不代表连接成功；不可用时用官方 CLI/文档继续并报告限制 |
| CLI | 项目脚本、Xcode/Swift/xcrun 工具路径和版本、实际支持的命令 | 先复用已核实的项目脚本与官方工具，不手写替代构建/签名/测试链路 |
| SDK | 实际选中 Xcode 与 SDK、deployment target、平台/架构、模拟器或设备 runtime、包/扩展要求 | 编译 SDK 与最低系统是不同概念；新 API 按运行时可用性处理 |

先核对已安装/已连接能力；缺少或已变化时查官方文档、官方工具目录及发行说明。不能只凭历史用过、本机存在或第三方自称“官方”跳过来源与适配检查，也不无限检索不存在的工具。

## Xcode / Swift / SDK

按当前任务检查所需命令，不机械执行整张表：

```bash
xcode-select -p
xcodebuild -version
xcrun swift --version
xcodebuild -showsdks
xcrun --sdk iphoneos --show-sdk-version
xcrun --sdk macosx --show-sdk-version
xcrun simctl list devices available
```

- 系统当前 developer directory 可能是 Command Line Tools，不能据此判断未安装 Xcode。先核对项目指定的 `DEVELOPER_DIR`、已安装 Xcode 路径，再决定实际命令环境；不自动执行全局 `xcode-select --switch`。
- API 版本以实际构建 SDK 和目标系统为准，不能照搬最新文档到较旧 SDK，也不能为绕过错误擅自提高 deployment target。
- 读取 App、扩展、测试及本地 package 的支持范围；验证目标明确区分真机/模拟器、系统版本与架构。版本锁定和发布约束继续遵循项目规则。

## 官方 MCP 与文档

- [Apple：Giving external agents access to Xcode](https://developer.apple.com/documentation/xcode/giving-external-agents-access-to-xcode) 说明 Xcode Tools 与 `xcrun mcpbridge`。先核对本机 Xcode 是否支持、实际连接及授权；不要直接启动桥接或启用外部代理访问来代替确认。
- [Apple：Meet agentic coding in Xcode](https://developer.apple.com/videos/play/tech-talks/111428/) 介绍官方 MCP 的构建、测试和文档能力。
- 匹配任务的官方 Skill 缺失时，使用 [Apple Developer Documentation](https://developer.apple.com/documentation/)；不能把非官方 Xcode MCP 或社区 Skill 自动标记为 Apple 官方。
- 官方 MCP 未连接不阻止使用已经可用的官方 CLI；需要 MCP 才能完成的检查明确标未完成，不伪造交互结果。

## 记录与安装边界

任务记录写明四项的来源、实际版本/状态、选用工具及检查结果。对未找到、未安装、未连接、不适用和已验证使用分别表述；无变化的本轮核对可引用已有记录。

SDK/CLI/Skill/MCP 的安装、升级、连接或权限扩展仍走工具发现与现有授权；不因本规则自动安装新工具、接受许可、修改全局配置或上传代码。找到能力不等于已授权启用它。
