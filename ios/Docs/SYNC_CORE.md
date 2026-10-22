# SyncCore：iOS/macOS 本地优先同步

支持 iOS 17+、macOS 14+。通过根 SwiftPM 包的 `SyncCore` 产品使用，内部使用 GRDB 7.11.1。公开 API 不暴露 GRDB，不依赖 UI 框架或特定认证 SDK。

## 应用接入合同

1. 定义具体 `Codable & Sendable` payload，使用 `SyncSchema` 注册 kind、UTF-8 JSON 字节上限及业务校验。
2. 在 Application Support 中提供存储根目录。`SyncScope` 包含完整后端 URL、appID 与可信 userID；游客使用 nil。框架对作用域生成独立数据库文件名，禁止多个 scope 共用同一数据库文件。
3. 通过 `SyncStore` 保存、删除、分页读取与观察；本地写入不需要认证。保存成功才代表数据与 outbox 同时提交。
4. 登录后以同一个 `SyncScope` 创建 `AppCloudSyncTransport` 与 `SyncCoordinator`。协调器校验传输的完整 scope 与数据库一致；正式 HTTP 地址只取 scope.backendURL，避免生产/测试环境与应用误配。身份提供器返回当前后端认证的 userID、会话绑定的 deviceID、access token；`forceRefresh=true` 时复用宿主认证的刷新入口。
5. 在登录完成、进入前台、网络恢复时调用 `start()`；它也观察后续本地待上传修改。手动刷新可 `try await synchronize()`。需要获取结果的调用会直接收到错误，自动触发才执行有限退避重试。
6. 在退出、切号或释放账号界面前调用 `pause()`，再卸载对应 Store。暂停后用 `start()` 恢复；不要复用旧账号协调器访问新账号库。

在线服务器必须注册对应 kind 的封闭 payload schema。客户端注册新类型不会自动扩展服务端业务能力。现有 ADBox 只接受 `kind=shortcut`、标题和命令；第二个应用在自己的服务端包配置自己的模型。

## 数据与同步语义

- UUID 创建后跨编辑稳定；每个作用域内 UUID 跨 kind 唯一。
- 框架编码 payload 时注入 kind；业务模型无需包含 UUID 或 kind。输入大小上限包含注入后的完整 JSON。
- 文档、修改 revision、待发状态、冻结操作和元数据在同一 GRDB 事务内保存。发生磁盘或解码错误会抛出异常，不折为空数据。
- 待发草稿可合并；开始发送前冻结完整 operationID、baseVersion、正文、删除状态、deviceID。未知结果必须原样重试。
- 上传回执仅确认对应冻结操作；上传期间的新修改继续排队，旧回执不会覆盖新内容或更高远端版本。
- 拉取逐页提交；页面非法或保存失败，整页与 nextCursor 共同回滚。push 返回的 cursor 不用于推进 pullCursor。
- 删除先从界面隐藏，本地保留删除操作，远端保留墓碑。长期离线设备收到墓碑后移除本地可见数据；离线编辑遇到删除进入冲突。
- 当前协议是最新状态增量，不是操作历史；首版单条上传，避免服务器整批回滚扩大冲突影响。

## 冲突与错误

`conflicts()` 返回本地内容、远端内容、共同基线和原因。业务展示差异后调用 `resolveConflict(recordID:resolution:)` 选择 `.keepLocal` 或 `.useRemote`；业务合并使用 `resolveConflict(recordID:payload:using:)`，重新执行业务校验并生成新操作。

内容冲突隔离单条记录，其他待上传文档继续同步。HTTP 409 必须按 code 处理：`version_conflict` 才是内容对账；`operation_reused` 表示冻结合同或身份恢复错误；配额错误保留队列并停止当前同步，不生成伪冲突。

仅临时网络错误、429、5xx 自动退避重试；401 通过宿主强制刷新一次，仍失败则等待登录。校验、配额、未知 kind、非法响应与本地存储故障不自动无限重试。`SyncState.errorCode` 不包含令牌或业务正文。

框架不保证应用挂起后仍在后台同步，也不提供服务器实时推送；宿主在前台/网络恢复时触发即可继续。

## 游客、迁移与恢复

- 游客数据库与账号数据库独立。登录后先完成初次云端拉取；由宿主明确选择导入，再调用目标库 `importDocuments(_:using:importID:)`。同一次导入必须复用稳定 importID；导入收据与数据共同提交，重复调用不重复写入。
- 相同 UUID 内容不同进入冲突；不同 UUID 即使同名也不自动去重。源游客数据不由目标库导入操作删除。
- 旧 UserDefaults 导入由各应用适配：先保留原始 Data，区分不存在与损坏，完整解码、校验后导入并记收据，不能长期双写。
- Token 过期时已挂载账号库仍能编辑；显式退出后卸载账号库，展示独立游客空间。重新认证同账号后再挂载旧库。
- deviceID 变化时普通同步暂停。调用 `recoverDeviceIdentity()` 先拉取，再隔离旧冻结操作为需要显式处理的恢复冲突；不使用新设备身份重放旧 operationID。调用前后宿主必须保证当前认证身份稳定。
- SQLite 不保存 access/refresh token，也不实现端到端加密。认证密钥继续交给现有 Keychain/AuthCore。宿主负责应用沙盒、Data Protection 与备份政策。

## 范围与验收边界

此产品是有界 JSON 文档同步，未提供附件传输、复杂关系查询、自动字段合并、CRDT、排序语义或历史回放。应用的排序字段、关系约束和同步白名单由业务 schema 定义。

服务端墓碑和回执当前长期保留并受配额限制。客户端不能自行清理服务器历史；未来回收需同时设计同步 epoch、离线窗口和全量重建。

示例见 `ios/Examples/OfflineSync/README.md`。自动化测试覆盖本地存储、HTTP 合同与可控多端交错；真实 OAuth、生产 PostgreSQL、ADBox 数据迁移与真机双端验收属于后续应用接入阶段。
