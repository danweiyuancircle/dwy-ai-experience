# AppleAppKit 0.9.0 与 create-dwy 0.37.1 发布前验收

日期：2026-11-17。基线为 develop 的 db423faa，包含用户授权提交的全部工作区改动；本记录区分源码验证、平台编译和目标系统交互，不把本机通过扩大为云端或生产验收。

## 范围与版本

- AppleAppKit：恢复被目录迁移覆盖的 0.8.1/0.8.2 历史记录，新建 0.9.0 正式版本，包含权限产品、iOS 原生弹框、apple/ 目录和四层单端/双端模板。原有产品与 API 保留，不修改消费应用依赖。
- create-dwy：0.37.1，覆盖尚未发布的 Flutter 旧规则迁移映射修正及最新随包 Skills；ai-tools 内部版本为 0.40.0。
- 其他 npm/PyPI 包没有运行时改动，不创建空版本；原有主干、分支和历史标签保留，不强推或重打已交付标签。
- 用户已授权纳入四个本地旧 AI 配置文件的删除；VirtualBuddy 安装及停止的 macOS 26 镜像下载不属于仓库提交。

## 实际检查

| 检查 | 结果与边界 |
|---|---|
| SwiftPM 全量测试 | 本机 macOS 27.2.1 / Xcode 27.2，269 项 XCTest，0 失败；iOS 条件测试在 Mac 上不计覆盖 |
| Apple 模板与架构 | APPLE_TEMPLATE_TOOL_TESTS=1，34 项通过，包含真实 XcodeGen / SwiftPM 清单工具，不以文本检查替代生成结果 |
| CLI | 201 项 Node 测试通过，包版本为 0.37.1 |
| 发布工具 | 使用 ci/.venv Python 执行 scripts/tests，20 项通过；系统 Python 的模拟隔离路径用例失败，改用项目已有虚拟环境后通过，未放宽测试 |
| iOS 编译 | DesignKitIOS 使用真实 iPhoneSimulator SDK 和 arm64-apple-ios18.0-simulator 编译通过 |
| Playground | 30 份 fixture 复制资源及双语说明的同源校验通过，目录与文档版本均为 0.9.0 |
| 清单 | 37 个公开产品，其中 20 个权限产品；全部 target 目录存在 |
| Skills | 四份变更 SKILL.md 通过 quick_validate；相关平台和架构引用资料已同步，iOS 新弹框调用与权限产品版本边界已补齐 |
| 工作流 | 全部 YAML 本地解析通过；Apple 双环境均保留必需检查，联合打包等待 Apple 和设备指纹成功 |
| 仓库访问 | scripts/private_release.py check 通过；发布继续使用现有 GitHub Actions / OIDC |

## 自审与安全

已自审公开产品、版本来源、生成器调用、测试、资源、文档和 CI 依赖。原有 SwiftPM 产品名保持，权限按需链接，不替宿主配置权限声明，不伪造授权或任务成功；确认与取消仍由原生弹框处理。

暂存文件名无凭据、数据库或日志产物。内容扫描的五个 token 赋值均为历史已跟踪的认证测试固定样例，本轮只是随目录迁移保留，未发现实际凭据。SwiftPM 本机镜像导致的锁文件 identity 变化已还原，实际依赖版本未变。

纳管第三方上游源码含既有尾空白，使用 .gitattributes 仅排除 apple/ThirdParty 的行尾/文件尾空白提示，保留上游可比对性；自有代码继续执行默认差异检查，不改第三方行为或许可。

## 未覆盖项

macOS 26 本机虚拟机尚未安装；权限真实允许/拒绝、设置返回、完整窗口交互、VoiceOver、外设和支付行为不在本次本地回归结论内。云端 macOS 26/27 结果、GitHub Release、SwiftPM tag 可访问性及 npm 精确版本安装须在发布流程中另行核实。
