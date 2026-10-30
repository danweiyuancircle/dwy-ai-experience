# SyncCore：iOS/macOS 本地优先同步

支持 iOS 17+、macOS 14+。通过根 SwiftPM 包的 `SyncCore` 产品使用，内部使用 GRDB 7.11.1。公开 API 不暴露 GRDB，不依赖 UI 框架或特定认证 SDK。

## 应用接入合同

1. 定义具体 `Codable & Sendable` payload，使用 `SyncSchema` 注册 kind、UTF-8 JSON 字节上限及业务校验。固定实例及平台适用性在 `validateRecord` 中按完整 UUID 和 payload 验证；`managedFields` 声明可更新字段，`identityFields` 声明不可变字段。
2. 在 Application Support 中提供存储根目录。`SyncScope` 包含完整后端 URL、appID 与可信 userID；游客使用 nil。框架对作用域生成独立数据库文件名，禁止多个 scope 共用同一数据库文件。
3. 通过 `SyncStore` 保存、删除、分页读取与观察；本地写入不需要认证。保存成功才代表数据与 outbox 同时提交。
4. 登录后以同一个 `SyncScope` 创建 `AppCloudSyncTransport` 与 `SyncCoordinator`。协调器校验传输的完整 scope 与数据库一致；正式 HTTP 地址只取 scope.backendURL，避免生产/测试环境与应用误配。身份提供器返回当前后端认证的 userID、会话绑定的 deviceID、access token；`forceRefresh=true` 时复用宿主认证的刷新入口。
5. 在登录完成、进入前台、网络恢复时调用 `start()`；它也观察后续本地待上传修改。需要开启观察并等待本轮结果时，使用 `try await startAndSynchronize()`，不要串联 `start()` 与 `synchronize()`，否则快速失败时可能另起自动轮次。`changes()` 仍发布所有存储提交，协调器只消费其中递增的 `localChangeSequence`，pull、回执和冲突对账不会自行开启下一轮。仅手动刷新已运行的协调器可 `try await synchronize()`。需要获取结果的调用直接收到错误，自动触发按 `SyncRetryPolicy` 执行有限退避重试。
6. 在退出、切号或释放账号界面前调用 `pause()`，再卸载对应 Store。暂停后用 `start()` 恢复；不要复用旧账号协调器访问新账号库。

在线服务器必须注册对应 kind 的封闭 payload schema。客户端注册新类型不会自动扩展服务端业务能力。各应用在自己的服务端包定义模型、固定 ID 和类型生命周期；SyncCore 不含平台名或产品配置。

## 数据与同步语义

- UUID 创建后跨编辑稳定；每个作用域内 UUID 跨 kind 唯一。
- 框架编码 payload 时注入 kind；业务模型无需包含 UUID 或 kind。输入大小上限包含注入后的完整 JSON。
- 文档、修改 revision、待发状态、冻结操作和元数据在同一 GRDB 事务内保存。发生磁盘或解码错误会抛出异常，不折为空数据。
- 待发草稿可合并；开始发送前冻结完整 operationID、baseVersion、正文、删除状态、deviceID。未知结果必须原样重试。
- 上传回执仅确认对应冻结操作；上传期间的新修改继续排队，旧回执不会覆盖新内容或更高远端版本。
- 拉取逐页提交；外层元数据、分页或大小非法及保存失败时，整页与 nextCursor 共同回滚。未知 kind、实例或业务值保存原文并隔离投影，不阻塞其余记录与游标。push 返回的 cursor 不用于推进 pullCursor。
- 已知类型的未知字段保留；保存与冲突重基只替换 schema 托管字段。结构化字段按整体值替换，不提供任意嵌套 JSON Patch。改变类型或身份语义应使用新 kind 和固定 ID。
- 停用 schema 或实例后，已有 dirty/frozen 项保留并暂停，其他待发项继续；重启仍保留冻结请求。`recordStateLocally(id:)` 区分 missing、deleted、available 和 unsupported，不能将 typed 读取失败当作缺失。
- 删除先从界面隐藏，本地保留删除操作，远端保留墓碑。长期离线设备收到墓碑后移除本地可见数据；离线编辑遇到删除进入冲突。
- 当前协议是最新状态增量，不是操作历史；首版单条上传，避免服务器整批回滚扩大冲突影响。

## 冲突与错误

`conflicts()` 返回本地内容、远端内容、共同基线和原因。业务展示差异后调用 `resolveConflict(recordID:resolution:)` 选择 `.keepLocal` 或 `.useRemote`；业务合并使用 `resolveConflict(recordID:payload:using:)`，重新执行业务校验并生成新操作。

内容冲突隔离单条记录，其他待上传文档继续同步。HTTP 409 必须按 code 处理：`version_conflict` 才是内容对账；`operation_reused` 表示冻结合同或身份恢复错误；配额错误保留队列并停止当前同步，不生成伪冲突。

设置类 schema 可明确指定 `.localIntent`，在最新远端原文上重叠托管字段并生成新操作，最多连续重基三次；新用户编辑可重新开始。默认 `.manual` 继续保留双方候选。服务端逐项 `status:rejected,reason_code:write_retired,record:null` 持久暂停该操作，不影响其他文档；`diagnostics(limit:)` 返回有界原因与标识，不暴露原始正文。

需要无冲突弹窗的模型可指定 `.remoteWins`：dirty 草稿遇到实际远端内容变化、确定的 `version_conflict` 或导入 UUID 碰撞时，采用最新已确认远端原文或墓碑；远端仅推进版本而基线内容未变时，本地修改继续排队。旧 `.manual`/`.localIntent` 的默认与处理方式不变。改用 `.remoteWins` 后重开库会收口已有版本冲突及导入碰撞。

未知结果的 frozen 请求不能因新 pull 被丢弃或改变正文。必须先用原 operationID 对账；之后才采用更高远端版本。用户在已知新远端后再次编辑，保存时记录该版本的意图基线，旧回执或针对旧操作的 409 不会丢掉这次编辑；下一操作使用新远端 baseVersion。新意图再次遭遇更高远端版本时仍采用远端。未知业务值保留 raw 并隔离投影，跨 kind/身份变化继续隔离，不以静默策略绕过校验。409 没有任何可信远端快照时保留本地数据并暂停为 `remote_state_missing` 诊断；后续确认远端后恢复对账，不能伪造墓碑。

仅临时网络错误、429、5xx 自动退避重试；401 通过宿主强制刷新一次，仍失败则等待登录。校验、配额、非法响应与本地存储故障不自动无限重试。`SyncState.errorCode` 不包含令牌或业务正文。

需要失败后等待下一次本地编辑或外部触发时，使用 `SyncRetryPolicy(maximumAttempts: 1, initialDelay: 0, maximumDelay: 0)`。请求失败仍保留冻结操作与新草稿；不会连续重试。`SyncState.lastSuccessfulSync` 仅表示已完成一轮同步的展示时间，不参与记录冲突裁决。

## 通用偏好仓库

`@MainActor SyncPreferencesStore<Value>` 适用于 iOS/macOS 的统一设置门面，`Value` 需为 `Equatable & Sendable`。它不读取 UserDefaults，也不决定业务 kind、校验或账号授权。

- 用已提交的本地快照和作用域 `generation` 初始化；业务页面只绑定宿主设置门面的属性与命令，不调用同步接口。
- 命令通过 `submit(_:onFailure:)` 排队：在创建任务前捕获作用域票据，按操作顺序执行；持久化入口仍须校验票据。旧作用域任务及迟到失败不能污染当前账号。
- 仓储提交或拉取完成后调用 `apply(_:generation:)`，拒绝旧作用域快照；同值、同作用域不重复应用。
- `onApply` 安装时立即投影当前快照，随后仅将已提交内容单向应用到语言、主题等运行时。投影回调不得再次调用保存入口。
- 存储不可用时由业务门面明确拒绝保存，不可把默认值投影到真实用户偏好后伪装成功。网络失败属于同步执行器，不作为本地设置保存失败反馈。

宿主仍拥有配置字段定义和平台呈现；共享层集中提供串行提交、作用域保护与投影去重。新增业务配置只接统一门面，不在根视图或各页面追加同步观察者。

## 通用生命周期

应用根层持有 `@MainActor SyncLifecycleDriver`，通过 `onForeground`/`onBackground` 注入当前账号的启动与有界收尾动作；场景入口调用 `await driver.foreground()` 和 `await driver.background()`，业务页面无需接触同步。driver 在现有 SyncCore 内使用系统 Network 监听网络，首次可用或不可用到可用仅在前台调用 `onForeground`，后台网络恢复不会重启同步。释放 driver 时取消监听。`monitorNetwork: false` 与 `connectivityChanged(isAvailable:)` 可用于宿主自管网络或确定性测试，无须新 package 或依赖。

框架不保证应用挂起后仍在后台同步，也不提供服务器实时推送；宿主在前台/网络恢复时触发即可继续。

## 游客、迁移与恢复

- 游客数据库与账号数据库独立。登录后先完成初次云端拉取；由宿主明确选择导入，再调用目标库 `importDocuments(_:using:importID:)`。同一次导入必须复用稳定 importID；导入收据与数据共同提交，重复调用不重复写入。
- 配置初始化使用 `initializeLocally(_:using:)`：首拉完成且真正 missing 才条件创建。初始化冲突采用远端，墓碑不复活；用户编辑有独立意图。宿主维护游客基线，不能把账号 A 已投影到 UI 的值当作账号 B 的初值。
- 相同 UUID 内容不同进入冲突；不同 UUID 即使同名也不自动去重。源游客数据不由目标库导入操作删除。
- 旧 UserDefaults 导入由各应用适配：先保留原始 Data，区分不存在与损坏，完整解码、校验后导入并记收据，不能长期双写。
- Token 过期时已挂载账号库仍能编辑；显式退出后卸载账号库，展示独立游客空间。重新认证同账号后再挂载旧库。
- deviceID 变化时普通同步暂停。调用 `recoverDeviceIdentity()` 先拉取，再隔离旧冻结操作为需要显式处理的恢复冲突；不使用新设备身份重放旧 operationID。调用前后宿主必须保证当前认证身份稳定。
- SQLite 不保存 access/refresh token，也不实现端到端加密。认证密钥继续交给现有 Keychain/AuthCore。宿主负责应用沙盒、Data Protection 与备份政策。

## 范围与验收边界

此产品是有界 JSON 文档同步，未提供附件传输、复杂关系查询、任意字段合并、CRDT、排序语义或历史回放。应用的排序字段、关系约束和同步白名单由业务 schema 定义。

服务端墓碑和回执当前长期保留并受配额限制。客户端不能自行清理服务器历史；未来回收需同时设计同步 epoch、离线窗口和全量重建。

示例见 `ios/Examples/OfflineSync/README.md`。自动化测试覆盖本地存储、HTTP 合同与可控多端交错；真实 OAuth、生产 PostgreSQL、ADBox 数据迁移与真机双端验收属于后续应用接入阶段。
