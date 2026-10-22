# SyncCore 测试用例

当前 51 项 XCTest，使用临时 SQLite 文件、受控远端 transport 与 URLProtocol 响应；不依赖真实账号或生产服务。

| 测试文件 | 数量 | 重点 |
|---|---:|---|
| `ios/Tests/SyncCoreTests/SyncStoreTests.swift` | 23 | 事务保存、磁盘重开、冻结请求、页回滚、冲突、导入、设备恢复、非法数据 |
| `ios/Tests/SyncCoreTests/SyncCoordinatorTests.swift` | 13 | 两端增删改、超时重试、连续编辑、暂停、身份刷新、作用域校验与自动退避 |
| `ios/Tests/SyncCoreTests/SyncTransportTests.swift` | 14 | HTTP 信封、路径、分页、Int64、限长、脱敏与 scope 绑定 |
| `ios/Tests/SyncCoreTests/SyncUsageTests.swift` | 1 | 无关 payload 模型共用引擎，不串 kind |

## 存储：23 项

- 保存与冻结操作在重开库后保持。
- 无效保存共同回滚；账号、应用、环境数据库隔离。
- 上传中编辑不改变冻结请求；旧确认保留新 revision。
- 未知 kind 导致整页及游标回滚。
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
- 409 候选不能改变文档 kind 或清除原冻结请求。

## 协调器：13 项

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

## HTTP：14 项

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

## 执行与边界

在仓库根目录执行：

```sh
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test --filter SyncCoreTests
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer swift test
```

另编译 iOS 17 模拟器目标。上述验证不等于真实 OAuth、真实 app-cloud PostgreSQL 并发、ADBox 旧数据迁移或真机双端同步验收。
