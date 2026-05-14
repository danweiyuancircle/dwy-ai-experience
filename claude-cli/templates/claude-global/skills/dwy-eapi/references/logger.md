# logger — 基于 loguru 的全局日志

> 何时读这份：当用户需要配置日志输出、轮转策略、拦截 uvicorn/SQLAlchemy 日志、或使用 JSON Lines 格式对接日志聚合系统时读取。

```python
from dwyeapi import logger

# 启动时调用一次（通常在 lifespan 中）
logger.configure(
    level="INFO",
    log_dir="./logs",
    filename="app",
    max_bytes=100 * 1024 * 1024,   # 100 MB
    retention="30 days",
    console=True,
    serialize=False,
    enqueue=True,
    intercept_stdlib=True,
    intercept_loggers=["uvicorn", "sqlalchemy"],
)

# 获取命名 logger
log = logger.get_logger("users")
log.info("用户 %s 登录", user_id)
log.error("操作失败", exc_info=True)
log.exception("未捕获异常")  # 自动 exc_info=True

# 关闭（lifespan 结束时）
logger.close()
```

## configure 参数

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| level | str | `"INFO"` | 最低级别：DEBUG/INFO/WARNING/ERROR/CRITICAL |
| log_dir | str/Path/None | None | 日志文件目录，None 表示关闭文件输出 |
| filename | str | `"app"` | 文件基础名，最终为 `{filename}_YYYY-MM-DD.log` |
| max_bytes | int | `100*1024*1024` | 单文件大小上限（字节） |
| retention | str/int | `"30 days"` | 保留策略（如 `"1 week"`、整数个数） |
| console | bool | True | 是否输出彩色日志到 stderr |
| console_format | str/None | None | 自定义控制台格式 |
| file_format | str/None | None | 自定义文件格式 |
| serialize | bool | False | 文件 sink 是否按 JSON Lines 序列化 |
| enqueue | bool | True | 是否异步写入（非阻塞、多进程安全） |
| intercept_stdlib | bool | True | 是否拦截 stdlib `logging` |
| intercept_loggers | list[str]/None | None | 限定拦截的 logger 名前缀，None 表示拦截 root |

## Logger 门面 API

`get_logger()` 返回的 `Logger` 兼容 stdlib 语义：

- `debug(msg, *args, exc_info=False)`
- `info(msg, *args, exc_info=False)`
- `warning(msg, *args, exc_info=False)`
- `error(msg, *args, exc_info=False)`
- `exception(msg, *args)` — 等价于 `error(msg, *args, exc_info=True)`
- `critical(msg, *args, exc_info=False)`

所有方法支持 `%s` / `%d` 等 stdlib 占位符，空 args 时保留 msg 原样。
