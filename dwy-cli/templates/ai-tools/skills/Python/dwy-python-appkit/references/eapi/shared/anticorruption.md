# 防腐层

业务代码禁止直调底层 API：

| 禁止 | 改用 |
|------|------|
| `datetime.now()` / `datetime.utcnow()` | `dt.now()` / `dt.utc_now()` |
| `import logging; logging.getLogger()` | `from dwyeapi import logger; logger.get_logger()` |
| 手写 `from redis.asyncio import Redis` 全局变量 | `cache.configure()` + `cache.get_redis()` |
| 手写 JWT encode/decode（含 `import jwt`） | `security.create_token()` / `security.decode_token()` |
| 直接 `raise HTTPException(404, ...)` | `raise NotFoundError("资源名")` |
| 自己写 `{"code": ..., "data": ...}` dict | `ApiResponse.ok(data)` / `ApiResponse.page(...)` |
| 自己写 `?page=&page_size=` Query | `params: PaginationParams = Depends()` |
