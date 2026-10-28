# 公共 Webhook 测试场景

## Apple 购买详情与可复用文案

- `test_apple_content.py`：金额/币种、零/缺失/未知值、家庭共享、退款申请与结果、续订设置、名称注入、旧八字段与安全元数据合同、实际 Discord JSON 和 UTF-16 长度。
- `test_portable_apple.py`：通用 verifier 与 router 的详情链路、SDK raw 未知枚举、畸形字段拒绝及敏感数据白名单；保留嵌套签名、并发取消与生命周期测试。
- `apple_wheel_smoke.py`：全新非 editable 环境中仅装 `[discord,apple]`，业务模块及 Resend 缺席，其他项目品牌/发送者覆写与真实离线 HTTP 链路成功。

| 编号 | 场景 | 预期 |
|---|---|---|
| WH-001 | 来源向 Discord 发送事件 | 单次请求、wait 确认、无 mentions、按需禁止预览、10 秒超时 |
| WH-009 | 发送者名称默认值与覆写 | 默认「Apple 应用通知」；低层 username、全局与来源 discord_username、评分配置覆写均进入实际 HTTP JSON；拒绝空值、超长和控制字符 |
| WH-002 | Discord 返回跳转或 HTTP 错误 | 不跟随、不自动重发，报告安全错误及永久/暂时分类 |
| WH-003 | 429 返回数字、畸形或 header 延迟 | 只接受有限非负秒数，支持 header 回退，不在请求内休眠 |
| WH-004 | 2xx 没有合法消息编号 | 拒绝空值、非 ASCII 数字、非字符串和超过 128 字符的编号 |
| WH-005 | 网络异常包含 token | 不在错误消息/异常链/HTTPX 日志中公开秘密 |
| WH-006 | 独立调用传入非官方目标 | 在发送前拒绝 HTTP、其他主机、query 和隐藏字符 |
| WH-007 | 服务关闭时取消发送 | 取消继续传播，HTTP 客户端关闭，无后台重试 |
| WH-008 | 单产品非 editable wheel 安装 | dwy_webhooks 来自当前独立环境，发送离线契约成功，另两个产品缺席 |

来源签名、去重及持久投递仍由 integration 与 iap 测试负责；公共测试不会访问真实平台或发送通知。

## App Store 评论采集

| 文件 | 场景与预期 |
|---|---|
| `test_review_client.py` | 配置及密钥校验；独立验证 ES256 JWT；有界分页、可选总数、合法末页；恶意 next/重定向/畸形响应拒绝；错误脱敏及客户端资源所有权 |
| `test_review_storage.py` | 首次历史基线、新增/修改/重复、A→B→A、30/60/90 天清理、扩大保留期静默补历史；持久调度、周期变更、多消费者租约、过期租约接管、原子回滚 |
| `test_review_service.py` | 未到期不请求 Apple；失败隔离、取消释放租约；保留期限传递、启用/新增/更新标题、可视星级、消息长度限制及过期投递跳过 |
| `test_review_runtime.py` | 自有任务在宿主数据库释放前停止；外部注入客户端不被关闭；重复安装拒绝 |

## 评论 extra 的独立安装验收

| 编号 | 场景 | 预期 |
|---|---|---|
| REV-PKG-001 | 全新环境只安装源码 `[discord]`，使用 EAPI 允许且不强制依赖 PyJWT 的 Redis 版本 | 源码导入路径属于当前 checkout；`install_review_monitor` 在缺少 `jwt` 时失败。旧 Redis 可能传递安装 PyJWT，不能据此把 `[discord]` 当作完整评论依赖 |
| REV-PKG-002 | 在同一合法依赖组合中安装源码 `[discord,reviews]` | 可从当前 checkout 导入评论客户端与运行时；直接声明 HTTPX、PyJWT、cryptography；`appstoreserverlibrary`、`resend` 和宿主产品包缺席 |
| REV-PKG-003 | 全新环境显式安装当前清单版本实际 wheel 的 `[discord,reviews]` | 版本和模块路径属于新环境的 site-packages；评论客户端与注册入口正常，平台 SDK 缺席 |
| REV-PKG-004 | 从当前源码执行全部包测试 | 明确断言源码路径，230 项来源、传输、Apple 详情、评论、名称注入和持久队列测试通过；不把旧 registry wheel 当成新源码 |
| REV-PKG-005 | 更新 CI 内部版本和 reviews extra | 第三方锁记录保持不变；包元数据与 Discord User-Agent 与清单版本一致；Apple 独立烟测的预期版本由 workflow 传入 |
