# health — 健康检查路由工厂

> 何时读这份：当用户需要添加健康检查端点、配置 k8s livenessProbe、或讨论 readiness vs liveness 设计时读取。

```python
from dwyeapi.health import create_health_router

router = create_health_router(
    service_name="my-api",
    version="1.0.0",
    path="/health",
    include_in_schema=True,
)
app.include_router(router)
```

## 设计取舍

端点**只**报告进程是否存活（liveness），**不连接 PostgreSQL / Redis** 等依赖。

原因：健康端点通常对公网开放，若内置 readiness / dependency check，攻击者可用低频高并发请求放大到数据库/缓存层，变成 DoS 放大器。

需要 readiness 语义的业务（如 k8s readinessProbe）应在业务项目里自行实现，并把该端点限制在内网或挂鉴权。

## create_health_router 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| service_name | str | **必填** | 服务名，通常取自 `Settings.service_name` |
| version | str | **必填** | 版本号，通常取自 `__version__` |
| path | str | `"/health"` | 端点路径 |
| include_in_schema | bool | True | 是否在 OpenAPI 文档暴露 |

## 响应示例

```json
{
  "code": 200,
  "message": "success",
  "data": {
    "service": "my-api",
    "version": "1.0.0",
    "status": "alive"
  },
  "timestamp": 1775625000
}
```
