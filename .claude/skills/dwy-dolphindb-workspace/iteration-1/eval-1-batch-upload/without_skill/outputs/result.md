# DolphinDB Tick Data Batch Upload

## 代码实现

```python
import pandas as pd
from dolphindb import session
from pathlib import Path
import logging
from typing import Optional

logger = logging.getLogger(__name__)


def upload_tick_to_dolphindb(
    filepath: str,
    trade_date: str,
    db_path: str = "dfs://tickDB",
    table_name: str = "snapshots",
    host: str = "localhost",
    port: int = 8848,
    username: str = "admin",
    password: str = "123456",
    batch_size: int = 100_000,
) -> dict:
    """
    将 feather 格式的 tick 数据批量写入 DolphinDB 分区表。

    参数
    ----------
    filepath : str
        feather 文件路径，包含约 200 万行 tick 数据。
    trade_date : str
        交易日期，格式建议为 'YYYY-MM-DD'，会写入 DataFrame 作为分区列。
    db_path : str
        DolphinDB 数据库路径，默认 "dfs://tickDB"。
    table_name : str
        目标表名，默认 "snapshots"。
    host, port, username, password : str/int
        DolphinDB 连接信息。
    batch_size : int
        每批写入行数，默认 10 万行。可根据内存和网速调整。

    返回
    -------
    dict
        {"total_rows": int, "batches": int, "status": str}
    """

    # 1. 读取 feather
    fp = Path(filepath)
    if not fp.exists():
        raise FileNotFoundError(f"feather 文件不存在: {filepath}")

    df = pd.read_feather(filepath)
    total_rows = len(df)
    logger.info(f"读取 feather 完成: {total_rows:,} 行, {len(df.columns)} 列")

    # 2. 补齐分区列 trade_date
    if "trade_date" not in df.columns:
        df["trade_date"] = pd.to_datetime(trade_date)
    else:
        # 如果文件中已有该列，确保类型一致
        df["trade_date"] = pd.to_datetime(df["trade_date"])

    # 确保 order_book_id 为字符串（DolphinDB SYMBOL 或 STRING 分区常见要求）
    if "order_book_id" in df.columns:
        df["order_book_id"] = df["order_book_id"].astype(str)

    # 3. 连接 DolphinDB
    s = session()
    s.connect(host, port, username, password)
    logger.info(f"已连接 DolphinDB {host}:{port}")

    # 4. 获取 tableAppender（自动按分区列路由）
    appender = s.tableAppender(dbPath=db_path, tableName=table_name)

    # 5. 分批写入
    batches = (total_rows + batch_size - 1) // batch_size
    inserted = 0

    for i in range(batches):
        start = i * batch_size
        end = min((i + 1) * batch_size, total_rows)
        chunk = df.iloc[start:end]

        try:
            appender.append(chunk)
            inserted += len(chunk)
            logger.info(f"第 {i + 1}/{batches} 批写入成功: {len(chunk):,} 行")
        except Exception as e:
            logger.error(f"第 {i + 1}/{batches} 批写入失败: {e}")
            # 根据业务需求决定：中断还是继续
            raise RuntimeError(f"写入失败 at batch {i + 1}: {e}") from e

    s.close()

    logger.info(f"全部写入完成: {inserted:,} 行 -> {db_path}/{table_name}")
    return {
        "total_rows": total_rows,
        "batches": batches,
        "inserted_rows": inserted,
        "status": "success",
    }


# ── 使用示例 ──────────────────────────────
if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    result = upload_tick_to_dolphindb(
        filepath="/data/ticks/2024-01-15.feather",
        trade_date="2024-01-15",
        host="192.168.1.100",
        port=8848,
        username="admin",
        password="123456",
        batch_size=100_000,
    )
    print(result)
```

## 关键设计说明

1. **分区列补齐**：函数参数中的 `trade_date` 会被显式写入 DataFrame，作为 DolphinDB 的 RANGE/HASH 分区键之一，确保 `tableAppender` 能正确路由到对应分区。

2. **分批写入**：默认每批 10 万行。对于 200 万行数据，约 20 批。此粒度在网络不稳定或单节点内存有限时能有效降低单次事务压力，同时不会过度增加 RTT 开销。

3. **`tableAppender` 自动路由**：`tableAppender` 是写入分区表的首选 API，内部会根据 `trade_date` + `order_book_id` 把行映射到正确分区，无需手动构造 `append!` 脚本。

4. **类型安全**：显式将 `order_book_id` 转 `str`，避免 pandas 的 `mixed` 类型或 `int64` 与 DolphinDB `SYMBOL` 分区不兼容的问题。

5. **异常处理**：单批失败即中断并抛出异常，防止脏数据残留。若需容错（如跳过坏批），可把 `raise` 改为日志记录并继续。

## 依赖

```bash
pip install pandas pyarrow dolphindb
```

- `pyarrow` 是 `pandas.read_feather` 的后端必需库。
- `dolphindb` 为 DolphinDB 官方 Python API。
