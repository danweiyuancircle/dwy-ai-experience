# Apple 四层脚手架实施验收

日期：2026-11-17。结论：本轮规范、生成器、模板与结构检查交付通过；不代表 ADBox 已迁移或真实设备 / 界面验收通过。

## 范围与快照

- 用户确认统一 iOS、macOS、双平台基础分包，并明确每端内部仍以四层为主。
- ① App 装配，② Features / BusinessUI，③共享 BizFoundation 与产品平台适配，④ AppleAppKit 通用产品；目录、target、package 数量不是层数。
- `apple/scripts/new-app.sh` 保留入口，生成由 `apple/scripts/new_app.py` 使用标准库执行。
- `apple/Templates/common` 维护唯一的产品核心、项目规则、架构文档和检查器；平台模板只保留本端应用代码与工程配置。
- 支持 ios、macos、apple 三种形态；--add-platform 只写新平台，保留旧源码、配置、锁文件和依赖版本。输入校验使用 Swift 原生语法解析拒绝关键字等无效产品类型名；既有工程版本分歧时在写新平台前失败。
- 相关规范同步到 `apple/Docs/ARCHITECTURE.md`、`apple/Docs/LAYERING.md`、`apple/README.md` 以及 Apple 架构 / 平台 / 基础库 Skill 源文件；未修改全局已安装 Skills。
- 基线 HEAD：`339920c65be4bbd7c5e275666a1c34ca3fc69ca4`，分支 develop。进入任务前已有大量 ios→apple 目录迁移、权限模块和其他未提交修改，本轮未将它们作为自己的新增功能或提交。
- 最终执行快照摘要 SHA-256：`feb14beb9520ab968d6ebecfac3ee910f9a72938ae97277085b28f4711d188f7`。计算覆盖工作流、两个生成脚本、两份 Python 测试及模板下 py/sh/swift/yml 共 26 文件，按仓库相对路径排序，依次散列“路径 + NUL + 文件内容”。文档验收记录不计入执行快照。

## 实际验证

| 检查 | 结果与边界 |
| --- | --- |
| `APPLE_TEMPLATE_TOOL_TESTS=1 python3 -B -m unittest discover -s apple/Tests -p 'test_*.py'` | 34 项通过：9 项模板、25 项结构检查；含真实 XcodeGen、SwiftPM dump-package 和临时生成物，非静态文本替代执行。 |
| `swift test --package-path packages/FourLayerQACore` | 最终双端生成物的业务包 5 项通过，0 failures。 |
| `xcodegen generate` | 单端 / 双端模板工具回归通过；独立双端验收工程两端均成功生成。 |
| macOS `xcodebuild ... -destination 'generic/platform=macOS' CODE_SIGNING_ALLOWED=NO build` | 使用公开 AppleAppKit 0.8.0 实际解析并构建，BUILD SUCCEEDED；产物 Bundle ID com.example.fourlayerqa.macos，最低 macOS 26.0，架构 arm64。 |
| iOS `xcodebuild ... -destination 'generic/platform=iOS Simulator' CODE_SIGNING_ALLOWED=NO build` | 同一双端生成物、同一产品业务核心，BUILD SUCCEEDED；产物 Bundle ID com.example.fourlayerqa.ios，最低 iOS 18.0。 |
| 工具链 | 本轮使用 Xcode 27.2（27B52）、Swift 6.4.2、XcodeGen 2.46.0。通过进程内 DEVELOPER_DIR 指定完整 Xcode，未更改系统全局选择。 |
| 工作流 | `private-release.yml` 启用真实模板工具测试，新增固定 XcodeGen 2.46.0 的临时 runner 准备步骤；本地 Ruby YAML 语法解析通过。actionlint 未安装，未执行。 |
| 差异检查 | 本轮相关路径 `git diff --check` 通过。 |

单端与双端模板结构均由生成回归验证；SDK 编译选用双端生成物的两个 App target，不声称另外创建的每个单端样本都重复进行了 SDK 编译。构建产物与完整日志保留于本轮临时验收目录，未作为二进制写入仓库。

Swift 单测存在上游 GoogleSignIn 清单废弃 API 警告；Xcode 存在模板未链接 AppIntents 时跳过其元数据提取的提示。两者均未阻断构建，本轮未升级这些依赖。

## CI 工具来源核实

GitHub 官方 macOS 26 runner 清单未列出 XcodeGen，因此不能依赖其预装：

- 官方 runner 清单：<https://github.com/actions/runner-images/blob/main/images/macos/macos-26-arm64-Readme.md>
- 工具官方发布：<https://github.com/yonaskolb/XcodeGen/releases/tag/2.46.0>，发布日期 2026-07-16，源码随附 MIT 许可证。
- 归档：<https://github.com/yonaskolb/XcodeGen/releases/download/2.46.0/xcodegen.zip>
- 发布元数据 digest 与本轮实际下载的内存归档 SHA-256 一致：`4d9e34b62172d645eed6457cac13fc222569974098ef4ee9c3368bedf0196806`，归档含 xcodegen/bin/xcodegen 和 LICENSE。

本轮没有在本机安装该归档。工作流准备步骤只在未来 runner 临时目录下载、验证、解压，并为当前 job 加入 PATH；未触发 GitHub Actions，不能宣称云端 CI 已通过。未执行长期凭据配置、发布或部署。

## 审查与修复

独立只读审查确认四层、三种生成形态与追加平台保护没有新的阻断；发现 XcodeGen excludes 的相对基准错误，会将实际未编译的业务 UI 误判为通过。

主代理补充真实 XcodeGen 重现，先观察检查器错误通过，再按 source 目录解释 excludes，回归通过。同时补充 includes 过滤造成漏编译的重现与修复。最终两项用例与其余 32 项一起通过，见 `apple/Tests/TEST_CASES.md`。

复用现有 Python 标准库、SwiftPM、XcodeGen；没有新增运行时依赖、通用转发 UI 层或自制 Swift / YAML 解析器。独立审查与主代理测试后的自审均已完成。

## ADBox 与未验证边界

ADBox 只读结构映射见 `docs/superpowers/reports/2026-11-17-adbox-four-layer-audit.md`。本轮未迁移其代码、重命名包、升级基础库、改动数据或执行其应用回归。

- 未执行真实设备或模拟器中的启动、导航、主题切换、视觉和辅助功能验收；SDK 构建通过不等于上述行为通过。
- 未验证 StoreKit 商品、OAuth、真实权限申请或远端服务。模板发布前仍需填写并核对产品配置。
- 未运行整个 AppleAppKit Swift 测试集；本轮没有修改基础库运行时源码，验证范围为脚手架、结构检查与生成物。
- 同功能控件包装、同 target 内跨 Feature 符号引用、宏展开、复杂条件编译与生命周期语义仍需审查和目标编译，检查器不提供完整 Swift 语义证明。
- 未提交、推送、发布，未更新全局 Skills。后续可以直接使用新建入口；ADBox 具体迁移仍按单独授权范围执行。
