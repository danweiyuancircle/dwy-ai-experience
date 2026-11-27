# 支付能力测试范围

所有测试均不调用真实商户。默认SQLite隔离验收；PostgreSQL测试需要显式本机连接环境变量，缺省跳过。

| 文件 | 验证行为 |
| --- | --- |
| `tests/test_payment_commands.py` | 支付意图触网前可见，同键复用，取消/未知结果原号及原截止恢复，会话提交后过期兼容，稳定键必填 |
| `tests/test_payments.py` | 严格金额、同键参数冲突、晚到成功回调、回调渠道/交易号核对、事件回放与确认事务、关单竞争、配置凭据脱敏 |
| `tests/test_refund_commands.py` | 持久意图及租约、并发占用、同号参数冲突、未知提交恢复、查询身份核对、回调抢先、历史金额不明阻挡、显式结果钩子 |
| `tests/test_wechat_sdk_boundaries.py` | SDK下单/查单/关单超时和通用验签异常归一与脱敏，取消正常传播 |
| `tests/test_migrations.py` | 新库资金表、旧记录保留、缺列/类型/唯一性/索引拒绝、两新增字段及事件表升降级、旧截止不猜测 |
| `tests/test_postgres.py` | 真实PostgreSQL独立会话同键竞争、不同退款号预算竞争、受理与SUCCESS回调竞争 |
| `tests/wheel_smoke.py` | 真实已安装core wheel版本/导入、无宿主与认证依赖、支付宝非强依赖、未配置网关不可用 |

源码、模拟渠道和数据库验收不能替代真实支付、真实退款及消费项目部署验收。
