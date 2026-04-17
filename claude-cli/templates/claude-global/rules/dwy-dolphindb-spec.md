---
description: DolphinDB 连接池与查询规范(量化金融项目专用)
paths:
  - "**/dolphindb*.py"
  - "**/ddb_*.py"
  - "**/quant/**/*.py"
  - "**/factors/**/*.py"
---

# DolphinDB 规范(量化金融项目专用)

> 仅适用于需要时序数据库的量化金融项目,普通业务项目跳过此文件。

---

## 一、连接池管理

```python
# dolphindb_pool.py — 全局单例
import dolphindb as ddb

_pool: ddb.DBConnectionPool | None = None

def get_pool() -> ddb.DBConnectionPool:
    global _pool
    if _pool is None:
        _pool = ddb.DBConnectionPool(
            host=settings.ddb_host,
            port=settings.ddb_port,
            userid=settings.ddb_user,
            password=settings.ddb_password,
            poolSize=2,  # 社区版限制:最多 2 个连接
        )
    return _pool
```

## 二、查询规则

```python
# 正确:WHERE 条件直接命中分区列
script = 'select * from loadTable("dfs://factors", "factor_data") where date = 2024.01.01, code = "000001"'

# 错误:函数包裹分区列(导致全表扫描)
script = 'select * from ... where month(date) = 2024.01M'  # 禁止!
```

## 三、强制规则

| 规则 | 说明 |
|------|------|
| 连接池 ≤ 2 | DolphinDB 社区版限制 |
| 批量写入 ≤ 500K 行/批 | 内存安全,超过需分片 |
| WHERE 必须直接命中分区列 | 禁止函数包裹,防止全表扫描 |
| 外部输入必须校验 | 防止 DolphinDB 脚本注入(用 validators.py) |
| 大数据处理后调 `gc.collect()` | 及时释放 DataFrame 内存 |
| 禁止在业务代码中直接拼 DDB 脚本 | 封装到 services 层 |
