# 权限源码纳管审查

日期：2026-11-17。范围：PermissionsKit 12.0.0、PermissionFlow v2.11.4 的源码、请求/状态接口、资源、许可证及本次团队适配。完整 SHA 与修改文件记录在 apple/ThirdParty 下各库的 DWY-UPSTREAM.md。两个版本均为发布满七天的 MIT 正式版本，已通过 GitHub release 元数据核对。

## 结论

采用经修改的部分，不以“无问题”概括上游全部实现。团队产品不公开第三方类型；不执行上游安装脚本、自动更新、权限数据库修改或外部提权。所用源码基于 Apple Framework；源码检索未发现 URLSession 外传、shell 子进程或动态下载执行路径。窗口跟踪使用公开 AX/窗口 API，受系统授权限制。

| 已确认问题 | 处理 |
|---|---|
| PermissionsKit 将 restricted 映射 denied，将 limited 映射 authorized | 对纳入编译的对应模块增加并保留 restricted、limited、unknown；核心/平台测试覆盖状态保真 |
| 通知同步查询使用 semaphore，且 provisional/ephemeral 丢失 | 不编译上游通知模块；自有通知适配使用 async settings/request，保留状态与 Error |
| 日历只写、定位 whenInUse/always 被按请求范围压缩 | 日历、提醒、定位使用独立原生适配，保留真实范围和定位精度 |
| 定位 always 升级若用户保持原状态，系统不保证回调 | 升级只发起并返回当前快照，不无限等待；注入不改变授权的 manager 验证 |
| 通知从 provisional 到完整权限需要显式升级申请 | 完整 options 可从 provisional 发起，provisional 自身不重复申请；iOS 策略测试覆盖 |
| Health 的通用 status/request 是不可用 fatalError 接口，读取权限不能查询 | Health 采用按原生类型申请和单独写权限查询，不提供虚假读取授权 |
| Face ID 用空白 reason 执行认证，无法表达一次认证结果 | 改为一次生物识别操作，校验用途文案，透传认证结果/错误 |
| PermissionFlow 按目录可读性猜测 FDA，包括其他用户目录 | 移除探测并返回 unknown/unsupported，不接触无关用户数据 |
| PermissionFlow 打开系统设置不处理返回值 | authorize 返回 Bool；失败关闭面板，不把打开失败当作引导成功 |
| 同一控制器从拖拽权限切换到仅设置权限会保留旧面板 | 新授权前关闭自身旧引导；设置跳转注入测试不访问真实系统设置 |

## 采用范围与维护

PermissionsKit 的相机、照片、麦克风、联系人、语音、运动、媒体库、蓝牙、跟踪、Siri 作为按需内部 target；团队对应适配在 apple/Sources/iOS 下。其余六类由团队原生接口承接，上游完整源码仍保留以供对照。联系人请求改用原生 async throws 以保留上游丢弃的 Error，状态仍由修正后的上游实现读取。

PermissionFlow 的设置导航、引导控制器和扩展状态模块纳入编译；Mac 原生申请状态使用自有精确映射，避免受限/未知被压缩。上游遗留弃用警告不视为验收通过的功能证明；后续升级按最小补丁维护，不扩展成系统权限管理器。

本地网络复用 ADBox 已有连接路径判定和恢复等待，实现迁入 PermissionCore，未引入 ADBox 设备实体或重连状态机。所选文件采用原生 scope，拒绝通过真实 I/O 错误报告。ADBox 的业务迁移需等包含权限产品的新 tag 可消费后进行，本轮不把旧版 0.8.0 当作新库，也不自动发布或改变 ADBox 的锁定依赖。

## 验证记录与限制

使用 Xcode 27.2 / Swift 6.4.2。根 SwiftPM 测试与隔离权限依赖图的 Xcode 构建/模拟器测试分别执行；本机既有 GRDB 镜像影响根 Xcode 依赖解析，因此不能把隔离构建当作根 Xcode 依赖图验证通过。没有修改本机镜像配置。

最终代码经一次独立只读审查，通知升级、定位升级等待、旧引导残留、UI 动作脱离页面和历史 Changelog 误改均已修复；前两项先建立编译失败的回归，再实现并通过。UI 使用 SwiftUI 结构化 task 跟随页面取消，配合核心取消等待测试；真实视图消失/重入仍保留交互验收。

测试明细由 apple/Tests/TEST_CASES.md 与测试源文件记录。真实首次隐私弹框、签名沙盒下读写、引导视觉/键盘/VoiceOver、设置跳转失败的系统场景、CI 远端执行和 ADBox 业务迁移仍需分别验收，不通过修改系统隐私状态伪造证据。
