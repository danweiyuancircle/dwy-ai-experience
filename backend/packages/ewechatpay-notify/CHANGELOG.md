# Changelog

## 0.1.1

- 新增 PaymentNotificationContext.extra_fields，可用于付款和退款通知；默认空值保持旧正文。
- 复用 dwy-notify 0.3.1 通用展示能力，保护固定支付事实、字节预算与元数据白名单；自定义标签不能冒充固定字段。

## 0.1.0

- 新增公开 SDK callback 注入、付款/退款身份与金额核验。
- 新增已验证结果、宿主确认结果、安全上下文与统一业务去重键。
- 新增显式持久 sink 的可选 FastAPI 接收路由与独立 wheel 验收。
- 采用 MIT License，发行包含许可证；工作流校验许可声明与版本标签。
