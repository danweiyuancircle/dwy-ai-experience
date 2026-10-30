# SyncCore 测试用例

当前 93 项 XCTest，使用临时 SQLite 文件、受控远端 transport 与 URLProtocol 响应；不依赖真实账号或生产服务。

| 测试文件 | 数量 | 重点 |
|---|---:|---|
| `ios/Tests/SyncCoreTests/SyncStoreTests.swift` | 24 | 事务保存、同步落盘、磁盘重开、冻结请求、页回滚、冲突、导入、设备恢复、非法数据 |
| `ios/Tests/SyncCoreTests/SyncCoordinatorTests.swift` | 17 | 两端增删改、超时重试、连续编辑、暂停、身份刷新、作用域校验、自动退避、逐项停写与持久队列统计 |
| `ios/Tests/SyncCoreTests/SyncTransportTests.swift` | 15 | HTTP 信封、路径、分页、Int64、限长、脱敏、scope 绑定与拒绝回执 |
| `ios/Tests/SyncCoreTests/SyncEvolutionTests.swift` | 15 | raw 隔离、实例约束、字段保留、条件初始化、有界重基、墓碑身份、冻结恢复与双连接竞争 |
| `ios/Tests/SyncCoreTests/SyncUsageTests.swift` | 1 | 无关 payload 模型共用引擎，不串 kind |
| `ios/Tests/SyncCoreTests/SyncRemoteWinsTests.swift` | 13 | 静默远端优先、冻结幂等、新意图版本、墓碑、raw 隔离、旧冲突升级与无快照诊断 |
| `ios/Tests/SyncCoreTests/SyncAutomaticTriggerTests.swift` | 3 | 单次失败不被内部提交再次触发，可等待启动不另起自动轮，新本地编辑或 start 才继续 |
| `ios/Tests/SyncCoreTests/SyncLifecycleDriverTests.swift` | 2 | 前后台动作、首次网络可用、恢复边沿与后台恢复禁止重启 |
| `ios/Tests/SyncCoreTests/SyncPreferencesStoreTests.swift` | 3 | 提交后投影、scope 世代隔离、串行命令保序与失败保留现值 |

## 存储：24 项

- 保存与冻结操作在重开库后保持。
- 同步保存返回前正文与 outbox 已落盘；重开库可读，无效保存不能覆盖已提交正文。
- 无效保存共同回滚；账号、应用、环境数据库隔离。
- 上传中编辑不改变冻结请求；旧确认保留新 revision。
- 未知 kind 原文保留，正常项与游标继续提交。
- pull 内容与冻结请求相同仍保留回执追踪。
- 历史幂等回放不覆盖较高远端版本。
- 冲突保留双方候选；typed 合并重新校验。
- 上传期间删除继续生成后续删除操作。
- 游客导入收据与正文共同提交并幂等。
- 设备恢复隔离旧冻结操作，保留本地内容。
- 损坏磁盘 JSON 显式报错。
- 高远端候选与新本地 revision 同时保留。
- 使用云端解决冲突；干净本地接收远端墓碑。
- 游客 UUID 碰撞及无效批次不覆盖云端内容。
- 业务载荷字节、分页、schema 注册不能绕过限制。
- 观察者只收到已提交的快照。
- 版本耗尽不生成无法发送的操作。
- JSON 可解码但语义损坏的墓碑报错。
- kind 与 HTTP 共享 128 字节 ASCII 边界。
- 设备恢复隔离不被后续 pull 自动解除。
- 已失效执行许可不能提交远端页或游标。
- 已失效执行许可不能确认冻结请求。
- 409 候选改变文档 kind 时暂停原冻结请求，其他项仍可上传。

## 协调器：17 项

- 两设备传播新增、修改、删除并保持版本递增。
- 响应丢失后重开库，用原 operationID 重试，云端版本只增加一次。
- 上传期间再次编辑，旧回执不覆盖新内容。
- 暂停拒绝迟到响应，并保留待确认操作。
- 多次并发触发共用执行器。
- 同文档冲突保留双方内容，其他文档继续同步。
- 配额 409 不创建内容冲突。
- 401 只强制刷新一次，使用同一账号和设备身份。
- 游客只使用本地，不请求会话。
- 身份提供器返回错误账号时不得上传。
- 自动重试丢失响应，不生成多余服务器版本。
- 自动重试遵守次数上限与 Retry-After。
- 传输 scope 与数据库环境或应用错配时不得上传或落盘。
- 逐项永久拒绝不失败整轮，暂停项不会被后续轮次自动重试。
- 手动同步开始发布真实待发统计；请求中再次编辑后失败，状态统计与磁盘队列一致。
- 自动重试等待发布最新待发数量，暂停后迟到重试不能覆盖终态。
- 身份请求失败仍发布已有冲突数和待发数，不以初始零覆盖持久统计。

## HTTP：15 项

- 请求保留应用基路径、snake_case 与 Int64 精度。
- pull 正确解包信封，固定 limit=100。
- 最终页允许 nextCursor 超过最后一条记录 cursor。
- 保留业务 code、冲突快照与 Retry-After。
- 拒绝不安全 base URL。
- 请求前拒绝非法身份、游标和 mutation。
- 响应无 Content-Length 仍受流式字节上限限制。
- 拒绝非法 pull 页与不前进游标。
- JSON 保留 Int64，拒绝非有限数值。
- 服务错误与身份调试描述不泄露 access token。
- 删除 payload 编码为 null；不匹配回执被拒绝。
- transport 对外声明 scope，HTTP 目标仅由该 scope 派生。
- 错误账号与游客 scope 在网络发送前被拒绝。
- appID 存在明确字节上限。
- `status=rejected`、`record=null`、`reason_code=write_retired` 可正常解包。

## 演进：15 项

- 未知值、kind、固定实例原文保留并持久诊断，重开后游标仍正确。
- 受管字段编辑保留未知字段；CAS 重基保留最新远端新增字段与冻结身份。
- 首拉前不得初始化；条件创建遇墓碑采用远端，初始化中新增用户编辑保留。
- 移除 schema 后暂停脏记录与冻结请求，重新注册后原 operationID 可继续。
- 永久拒绝跨重启保留，其他记录仍可发送。
- 明确用户编辑可以基于远端墓碑重基；最多三次后留下冲突。
- typed 分页跳过未识别项，升级支持后能重新投影原始数据。
- 中间页游标不等于最后一项时整页回滚，不推进首拉标记。
- 双连接短事务竞争有界等待，不能把正常账号恢复当作 SQLite 错误。
- 条件初始化不能绕过注册校验；新用户编辑可重新开始有界重基。
- 删除未确认、已确认墓碑与重开磁盘后，复活同 UUID 仍不能改变身份字段。
- 无 baseline 的 dirty/frozen 本机删除保留原文证据，移除实例后暂停，恢复支持后原冻结操作不变。
- 未知实例的远端墓碑无需合成业务 payload，仍可接收并推进游标。
- 已确认删除后导入同身份配置，重开、保留本地与后续上传仍保留未知字段。
- 未识别枚举或已移除实例被远端确认删除后，按墓碑重置投影，历史原文不再阻断。

## 静默冲突、触发与生命周期：21 项

- pull 实际冲突采用远端，新编辑使用新远端版本上传；仅版本变化保留本地意图。
- 409 与已拉候选取最高版本，不生成内容冲突。
- frozen 请求经 pull、重开库仍保留原 operationID、baseVersion、正文；旧回执到达后才采用远端。
- 新远端之后再次编辑，重开及旧回执后仍能上传，保留最新远端未知字段。
- 新意图不受旧操作 409 覆盖；再次遭遇更新远端时按远端优先。
- 墓碑覆盖离线编辑；之后明确编辑可按墓碑版本重建。
- 冻结请求遇到新远端后，本地删除以该远端版本继续上传。
- 未支持远端原文保留，无冲突弹窗或自动回传；恢复 schema 后可投影。
- 改用远端优先后重开，已有手动冲突自动收口。
- 导入碰撞采用远端，不新增弹窗冲突。
- 409 无远端快照时本地内容保留为诊断，后续确认远端才恢复对账。
- 身份或 kind 变化继续隔离，不用远端优先绕过校验。
- 单次失败后内部 pull 提交不重发；新本地提交、外部 start 均可重放原 frozen 请求。
- 可等待启动遇到立即 pull 失败只执行一次；随后真实本地编辑再触发一次。
- 可等待启动已有 pending 快照时，push 立即失败仍只执行一次，不因内部快照另起自动轮；随后真实本地编辑继续触发。
- 前台、后台与首次网络可用/恢复边沿按根层动作驱动；后台网络恢复不会重启。
- 偏好命令提交后才投影，同值跨 scope 重新投影，拒绝旧 snapshot。
- 串行命令保持顺序，本地失败不改值；排队旧 scope 命令及迟到错误不影响新 scope。

## 执行与边界

在仓库根目录执行：

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test --filter SyncCoreTests
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test
```

另编译 iOS 17 模拟器目标。上述验证不等于真实 OAuth、真实 app-cloud PostgreSQL 并发、ADBox 旧数据迁移或真机双端同步验收。
