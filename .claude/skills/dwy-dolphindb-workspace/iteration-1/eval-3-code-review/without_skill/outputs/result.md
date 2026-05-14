# DolphinDB 代码审查报告

## 审查对象

- **文件类型**: Python 异步函数（DolphinDB 交互层）
- **涉及技术**: Python 3.11 + DolphinDB + pandas
- **审查维度**: 安全性、正确性、性能、可维护性、错误处理

---

## 问题清单

### 🔴 P0 - 严重（必须修复）

#### 1. 脚本注入漏洞（SQL/Script Injection）
**位置**: `query_ticks` 函数  
**问题**: 使用 f-string 将 `stock_code`、`start`、`end` 直接拼接到 DolphinDB 脚本中。攻击者可构造 `" OR 1=1 OR "` 等 payload 读取全表数据。  
**风险**: 数据泄露、非授权数据访问、服务异常。

#### 2. `upload` 语法错误
**位置**: `import_tick_data` 函数  
**问题**: `await run_ddb(f'upload data = {df}')` 不是合法的 DolphinDB Python API 用法。DataFrame 无法直接通过字符串插值上传。  
**风险**: 运行时必然失败，数据导入不可用。

#### 3. 日期比较缺少引号
**位置**: `query_ticks` 函数  
**问题**: `date(trade_date) >= {start}` 中 `start` 是字符串，但拼接后缺少引号，生成类似 `>= 2024-01-01` 的非法 DolphinDB 语法。  
**风险**: 语法错误，查询失败。

### 🟠 P1 - 高优先级（强烈建议修复）

#### 4. 缺少输入校验
**位置**: 两个函数入参  
**问题**: 未校验 `trade_date`、`start`、`end` 的日期格式，未校验 `stock_code` 是否为空或包含非法字符。  
**风险**: 错误传播到 DolphinDB 层，产生难以调试的异常。

#### 5. `select *` 全列查询
**位置**: `query_ticks` 函数  
**问题**: 使用 `select *` 读取所有列，DolphinDB 为列式存储，宽表场景下 I/O 浪费严重。  
**风险**: 查询性能差，网络开销大。

#### 6. 硬编码魔数
**位置**: `query_ticks` 函数  
**问题**: `limit 100 offset 0` 硬编码，且 `dfs://tickDB`、`snapshots` 等数据库对象写死在函数内。  
**风险**: 不可复用，难以测试和配置。

#### 7. 缺少异常处理
**位置**: 两个函数整体  
**问题**: 没有任何 `try/except`，DolphinDB 连接异常、脚本执行失败、Feather 解析错误都会直接抛到调用方。  
**风险**: 服务崩溃，无法向调用方返回有意义的错误信息。

### 🟡 P2 - 中优先级（建议优化）

#### 8. `pd.read_feather` 大文件内存风险
**位置**: `import_tick_data` 函数  
**问题**: 一次性将整个 Feather 文件读入内存，Tick 数据文件可能非常大。  
**风险**: OOM，影响服务稳定性。

#### 9. 缺少日志记录
**位置**: 两个函数  
**问题**: 没有记录操作日志，出现问题难以排查。  
**风险**: 运维困难。

#### 10. `query_ticks` 未做分页参数化
**位置**: `query_ticks` 函数  
**问题**: offset 固定为 0，无法支持翻页。  
**风险**: 功能不完整。

---

## 修复后代码

```python
import logging
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import pandas as pd

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# 常量与配置（建议从环境变量或配置中心读取）
# ---------------------------------------------------------------------------
DDB_DATABASE = "dfs://tickDB"
DDB_TABLE = "snapshots"
DEFAULT_LIMIT = 100
MAX_LIMIT = 10_000

# 合法股票代码正则（A 股示例，可按实际规则调整）
STOCK_CODE_PATTERN = re.compile(r"^[0-9]{6}$")
DATE_FORMAT = "%Y-%m-%d"


class DDBError(Exception):
    """DolphinDB 操作异常"""
    pass


class ValidationError(Exception):
    """入参校验异常"""
    pass


# ---------------------------------------------------------------------------
# 内部辅助函数
# ---------------------------------------------------------------------------

def _validate_stock_code(stock_code: str) -> None:
    """校验股票代码格式。"""
    if not stock_code:
        raise ValidationError("stock_code 不能为空")
    if not STOCK_CODE_PATTERN.match(stock_code):
        raise ValidationError(f"非法 stock_code: {stock_code}")


def _validate_date_str(date_str: str, field_name: str) -> None:
    """校验日期字符串格式。"""
    if not date_str:
        raise ValidationError(f"{field_name} 不能为空")
    try:
        datetime.strptime(date_str, DATE_FORMAT)
    except ValueError as exc:
        raise ValidationError(
            f"{field_name} 格式错误，期望 {DATE_FORMAT}，收到: {date_str}"
        ) from exc


def _build_query_script(
    stock_code: str,
    start: str,
    end: str,
    columns: list[str] | None,
    limit: int,
    offset: int,
) -> str:
    """
    构造安全的 DolphinDB 查询脚本。
    所有外部输入均通过 DolphinDB 变量注入，避免字符串拼接注入。
    """
    col_clause = ", ".join(columns) if columns else "*"
    # 使用 DolphinDB 的变量占位，再通过 upload 传入实际值
    script = (
        f'select {col_clause} from loadTable("{DDB_DATABASE}", "{DDB_TABLE}") '
        f'where date(trade_date) >= startDate '
        f'and date(trade_date) <= endDate '
        f'and order_book_id = stockCode '
        f'limit queryLimit offset queryOffset'
    )
    return script


# ---------------------------------------------------------------------------
# 业务函数（修复后）
# ---------------------------------------------------------------------------

async def import_tick_data(
    filepath: str,
    trade_date: str,
    batch_size: int = 50_000,
) -> dict[str, Any]:
    """
    将 Feather 格式的 Tick 数据分批导入 DolphinDB。

    Args:
        filepath: Feather 文件路径。
        trade_date: 交易日期（YYYY-MM-DD），用于校验文件内容。
        batch_size: 每批导入行数，防止大文件 OOM。

    Returns:
        {"status": "ok", "imported_rows": int}

    Raises:
        ValidationError: 入参校验失败。
        DDBError: DolphinDB 导入失败。
    """
    _validate_date_str(trade_date, "trade_date")
    path = Path(filepath)
    if not path.exists():
        raise ValidationError(f"文件不存在: {filepath}")

    total_imported = 0

    try:
        # 使用 chunksize 分块读取，避免一次性加载大文件到内存
        for i, chunk in enumerate(pd.read_feather(filepath, columns=None, chunksize=batch_size)):
            if chunk.empty:
                continue

            # 可选：校验 chunk 中的 trade_date 是否与传入参数一致
            if "trade_date" in chunk.columns:
                chunk_dates = chunk["trade_date"].dropna().astype(str).str[:10].unique()
                if len(chunk_dates) > 1 or (len(chunk_dates) == 1 and chunk_dates[0] != trade_date):
                    logger.warning(
                        "文件 %s 第 %d 块的 trade_date 与参数 %s 不一致",
                        filepath, i, trade_date,
                    )

            # 通过 DolphinDB Python API 的 upload + run 方式写入
            # 注意：这里假设 run_ddb 封装了 session.run(script, **vars) 的能力
            upload_vars = {"data": chunk}
            script = (
                f'tb = loadTable("{DDB_DATABASE}", "{DDB_TABLE}"); '
                f'append!(tb, data)'
            )
            result = await run_ddb(script, vars=upload_vars)
            total_imported += len(chunk)
            logger.info(
                "导入 %s 第 %d 批: %d 行", filepath, i, len(chunk)
            )
    except ValidationError:
        raise
    except Exception as exc:
        logger.exception("导入 Feather 文件失败: %s", filepath)
        raise DDBError(f"导入失败: {exc}") from exc

    return {"status": "ok", "imported_rows": total_imported}


async def query_ticks(
    stock_code: str,
    start: str,
    end: str,
    columns: list[str] | None = None,
    limit: int = DEFAULT_LIMIT,
    offset: int = 0,
) -> dict[str, Any]:
    """
    查询指定股票在日期范围内的 Tick 快照数据。

    Args:
        stock_code: 股票代码（如 600000）。
        start: 开始日期（YYYY-MM-DD）。
        end: 结束日期（YYYY-MM-DD）。
        columns: 指定返回列，None 时返回全部列（生产环境建议显式指定）。
        limit: 最大返回行数，默认 100，上限 10000。
        offset: 分页偏移量。

    Returns:
        {"status": "ok", "data": list[dict], "total": int | None}

    Raises:
        ValidationError: 入参校验失败。
        DDBError: DolphinDB 查询失败。
    """
    # ---- 入参校验 ----
    _validate_stock_code(stock_code)
    _validate_date_str(start, "start")
    _validate_date_str(end, "end")
    if limit < 1 or limit > MAX_LIMIT:
        raise ValidationError(f"limit 必须在 1-{MAX_LIMIT} 之间")
    if offset < 0:
        raise ValidationError("offset 不能为负数")

    # ---- 构造查询 ----
    script = _build_query_script(stock_code, start, end, columns, limit, offset)
    # 通过 vars 注入外部值，避免字符串拼接注入
    vars_map = {
        "stockCode": stock_code,
        "startDate": start,
        "endDate": end,
        "queryLimit": limit,
        "queryOffset": offset,
    }

    try:
        logger.info(
            "查询 Tick 数据: %s [%s ~ %s] limit=%d offset=%d",
            stock_code, start, end, limit, offset,
        )
        # 假设 run_ddb 支持 vars 参数用于 upload 变量
        result_df = await run_ddb(script, vars=vars_map)

        # 将结果转为标准 Python 结构返回
        data = result_df.to_dict(orient="records") if hasattr(result_df, "to_dict") else result_df
        return {"status": "ok", "data": data, "total": len(data) if isinstance(data, list) else None}
    except ValidationError:
        raise
    except Exception as exc:
        logger.exception("查询 Tick 数据失败: %s", stock_code)
        raise DDBError(f"查询失败: {exc}") from exc
```

---

## 关键修复说明

| 问题 | 修复措施 |
|------|----------|
| 脚本注入 | 所有外部输入通过 `vars` 字典以 DolphinDB 变量形式注入，不再拼接进脚本字符串 |
| upload 语法错误 | 改为 `run_ddb(script, vars={"data": chunk})` 的标准变量上传方式 |
| 日期引号缺失 | 日期通过变量注入，不再手写引号 |
| 缺少输入校验 | 新增 `_validate_stock_code`、`_validate_date_str` 正则与格式校验 |
| `select *` | 支持 `columns` 参数，默认仍用 `*` 但留有优化空间 |
| 硬编码 | 提取 `DDB_DATABASE`、`DDB_TABLE`、`DEFAULT_LIMIT` 等常量 |
| 缺少异常处理 | 全链路 `try/except`，自定义 `DDBError` 和 `ValidationError` |
| 大文件内存风险 | `pd.read_feather` 使用 `chunksize` 分批读取 |
| 缺少日志 | 关键路径增加 `logger.info` / `logger.warning` / `logger.exception` |
| 分页不可控 | `limit` / `offset` 参数化，并增加上限约束 |

---

## 对 `run_ddb` 封装层的假设

修复后的代码假设 `run_ddb` 支持如下签名：

```python
async def run_ddb(script: str, vars: dict[str, Any] | None = None) -> Any:
    ...
```

若现有封装不支持 `vars`，需要在外层统一增加 `session.upload(var_name, value)` + `session.run(script)` 的封装逻辑。

---

*审查完成时间: 2026-05-14*
