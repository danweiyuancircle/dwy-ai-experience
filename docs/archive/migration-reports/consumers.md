# Native 消费者迁移验收

执行日期：2026-10-21。right-click、quadrant、adbox 已切换到私有 Git https://github.com/danweiyuancircle/dwy-ai-experience.git ，exact `0.4.1`，SwiftPM identity 为 `dwy-ai-experience`。所有 Swift product 名与最低系统保持，XcodeGen 的 AppleAppKit 映射名沿用。本轮不接入业务 Google 登录 UI。

## 版本与实际解析

最终 tag SHA：`bb5bc480d0c3bace0252c443b48a2b53765edabc`。已从真实私有 URL HTTP/1.1 shallow fetch 并核验；三套 SwiftPM 与三套 Xcode 实际 workspace-state 均为此 SHA。

0.4.0 原标签保持不可变，发布产物目录的 .gitignore 门禁由 0.4.1 修正；两版本 Apple 运行源码一致。消费者使用首个有效 Release 0.4.1。

GoogleSignIn 保持已稳定的 9.1.0，revision `913b4005ea26aebe1c97d54e35ad82a515924c71`。GoogleUtilities 最终固定 8.1.4，revision `cc31f5ed464b111f877ce8554cbef4455d410d91`；8.1.5 当时不足 7 天，未作为最终结果。首次消费者自动解析会裁掉未消费的 shared 依赖约束而选择 8.1.5；本轮已回填真实官方 8.1.4 pin，并以受锁命令重验全部结果。

## 生成工程的锁闭环

三个项目的根 Package.resolved 是 canonical lock；right-click / adbox 已入库，quadrant 当前无 Git、锁文件落盘保留。adbox 使用 ios/Package.resolved，包含原有 Xcode-only KeyboardShortcuts / SwiftTerm / argument-parser pins。project.yml 的 options.postGenCommand 在 xcodegen generate 后把 canonical lock 复制到生成工程的共享 SwiftPM lock。

先删除 ignored 共享 lock 验证旧生成流程：3/3 不会重建；加入钩子后再次删除并生成：3/3 自动重建，最终与 canonical lock 逐字节一致。不依赖本机手工回填，也不跟踪生成工程或缓存。

Swift 验收使用 `--force-resolved-versions`；Xcode 使用 `-disableAutomaticPackageResolution`。不带锁保护的自动解析仍会选传递依赖新版本，依赖升级应单独审查。

## 最终验证结果

环境为 Xcode 27.1 / Apple Swift 6.4；所有命令局部指定 DEVELOPER_DIR，未改变全局 CLT。使用新 scratch / DerivedData；仅复用官方 Git 仓库对象缓存，不复制旧编译产物或用本地 path 冒充私有依赖。

| 检查 | 最终结果 |
|---|---|
| right-click swift test | exit 0；186 tests，4 skipped，0 failures |
| quadrant swift test | exit 0；149 tests，0 failures |
| adbox swift test | exit 0；1713 tests，0 failures |
| ContextKit / macOS | BUILD SUCCEEDED |
| Quadrant / iOS Simulator | BUILD SUCCEEDED |
| QuadrantMac / macOS | BUILD SUCCEEDED |
| TVRemote / iOS Simulator | BUILD SUCCEEDED |
| ADBoxMac / macOS | BUILD SUCCEEDED |

right-click 的 4 个既有 skip 需要外部 RIGHTFLOW_7ZZ_BINARY / RIGHTFLOW_RAR_FIXTURE。ContextKit 原 7zz 打包脚本在完全禁签时缺 EXPANDED_CODE_SIGN_IDENTITY，复验为 App、Finder 扩展和 7zz 统一使用本地 ad hoc 签名；只修改验收命令，未修改原脚本或产品签名配置。

官方 SwiftTerm 全历史下载较慢：实时核对官方 v1.10.1 SHA `5c83a9d214e7354697624c11deb4e488bdcfabad` 后，复用同一对象的现有 bare cache，并对官方 URL 实际 depth-1 fetch。最终 ADBox 构建使用 -skipPackageUpdates / -scmProvider system，同时保留锁保护；所有编译产物由本轮生成。

复现时令 IOS_WORKSPACE 指向业务工作区，XCODE_APP 指向当前 Xcode.app；每个消费者目录执行：

```sh
export DEVELOPER_DIR="$XCODE_APP/Contents/Developer"
swift test --force-resolved-versions
xcodegen generate
xcodebuild -project "$PROJECT" -scheme "$SCHEME" -destination "$DESTINATION" \
  -disableAutomaticPackageResolution CODE_SIGNING_ALLOWED=NO DEVELOPMENT_TEAM= build
```

| 消费者目录 | PROJECT | SCHEME / DESTINATION |
|---|---|---|
| $IOS_WORKSPACE/right-click | ContextKit.xcodeproj | ContextKit / generic/platform=macOS |
| $IOS_WORKSPACE/quadrant | Quadrant.xcodeproj | Quadrant / generic/platform=iOS Simulator；QuadrantMac / generic/platform=macOS |
| $IOS_WORKSPACE/adbox/ios | TVRemote.xcodeproj | TVRemote / generic/platform=iOS Simulator；ADBoxMac / generic/platform=macOS |

ContextKit 将禁签参数替换为 `CODE_SIGNING_ALLOWED=YES CODE_SIGN_IDENTITY=- CODE_SIGN_STYLE=Manual CODE_SIGNING_REQUIRED=NO EXPANDED_CODE_SIGN_IDENTITY=- DEVELOPMENT_TEAM=`。精确实际 argv、起止时间、原始日志和最终 hash 清单保存在本地 $CONSUMER_BACKUP，未进入仓库。

## 源码保留与 Git 交付

开始时 right-click/main、adbox/preview 均 clean；quadrant 无 Git；ios-arc/feat/google-auth-core 保留原有认证 dirty source。全部将编辑的配置、locks 和生成工程先备份至 $CONSUMER_BACKUP。本 agent 只修改依赖配置/locks、生成锁钩子和 ios-arc 文档指引。

right-click 的 328 个与 ios-arc 的 62 个源码/资源文件最终 SHA256 均与初始相同；ios-arc 原 Package.swift / Package.resolved 逐字节相同，原认证未提交/未跟踪内容保留，只新增 README pointer 与 Docs/MIGRATION.md。quadrant 和 adbox 后续出现其他任务并发业务编辑，全部保留：最终清单分别有 13 / 5 个初始文件发生变化或删除，本执行者未编辑这些文件。构建通过证明对应记录时间的工作树快照，不替后续并发业务编辑作验收。

| 仓库 | 本轮提交与远端 | 最终状态 |
|---|---|---|
| right-click main | `8ac35cf681fe515b5f8e2ce46c739e3ad3c8ef46` | push 成功，实际远端 SHA 相同，upstream 0/0，clean |
| adbox preview | `78e481c3cc5d0cfa168be2fd1427bc76c2f3ca52` | push 成功，实际远端 SHA 相同，upstream 0/0；并发业务 dirty 保留 |
| quadrant | 无 Git | 配置与锁已落盘，不创建仓库 |
| ios-arc | 不提交 | 原认证 dirty 保留，迁移文档落盘 |

两个 native commit 各仅三个 tracked 配置文件，提交前同步远端、cached diff --check 与敏感扫描均通过；未纳入 .github 或业务源码。历史 ADBox 私有只读 CI 运行 39536771900 成功；workflow 后续范围由主执行者按用户最新指令处理，本报告不新增 workflow，也不宣称 TestFlight 上传。主执行者另已核验旧 apple-app-kit 远端为 PRIVATE、匿名访问 404，历史标签与本地来源保留作回退。

真实 OAuth、StoreKit、设备安装与业务 UI 端到端验收不在本次依赖迁移结论中。
