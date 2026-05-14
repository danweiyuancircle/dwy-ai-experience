# FastAPI 端点实现：/api/tick/query

## 变更概述

新增一个 FastAPI 端点 `/api/tick/query`，支持按单支股票代码和日期范围从 DolphinDB `dfs://tickDB/snapshots` 表查询 Tick 快照数据。

---

## 文件 1：Schema (`quant_data/schemas/tick.py`)

在现有 schema 文件末尾追加以下请求/响应模型：

```python
class TickQuerySingleRequest(BaseModel):
    """单支股票 Tick 数据查询请求。"""

    stock_code: str = Field(description="股票代码，如 '000001.SZ'")
    start_date: str = Field(description="开始日期 (YYYY-MM-DD)")
    end_date: str = Field(description="结束日期 (YYYY-MM-DD)")


class TickQuerySingleResponse(BaseModel):
    """单支股票 Tick 数据查询响应。"""

    stock_code: str
    start_date: str
    end_date: str
    count: int
    data: list[dict]
```

---

## 文件 2：Service (`quant_data/services/tick_service.py`)

在 `TickService` 类中新增方法：

```python
    async def query_tick_single(
        self,
        stock_code: str,
        start_date: str,
        end_date: str,
    ) -> list[dict]:
        """按单支股票代码和日期范围查询 Tick 快照数据。

        Args:
            stock_code: 股票代码，如 '000001.SZ'。
            start_date: 开始日期 (YYYY-MM-DD)。
            end_date: 结束日期 (YYYY-MM-DD)。

        Returns:
            Tick 快照记录列表，每条记录为字段名到值的字典。

        Raises:
            BusinessError: 股票代码或日期格式非法时抛出。
        """
        validate_ukey(stock_code)
        ddb_start = to_dolphindb_date(start_date)
        ddb_end = to_dolphindb_date(end_date)
        validate_date(ddb_start)
        validate_date(ddb_end)

        script = (
            f'select * from loadTable("dfs://tickDB", "snapshots") '
            f'where trade_date >= {ddb_start}, '
            f'trade_date <= {ddb_end}, '
            f'order_book_id = "{stock_code}" '
            f'order by trade_date, time'
        )
        result_df = await run_ddb(script)

        if result_df is None or (hasattr(result_df, "empty") and result_df.empty):
            return []

        for col in result_df.columns:
            if hasattr(result_df[col], "dt"):
                result_df[col] = result_df[col].astype(str)

        return result_df.to_dict("records")
```

**关键设计点：**
- 使用 `validate_ukey` 校验 `000001.SZ` 格式，防止非法输入进入 DolphinDB 脚本。
- 使用 `to_dolphindb_date` 将 `YYYY-MM-DD` 转为 DolphinDB 原生 `YYYY.MM.DD` 格式。
- 过滤条件使用分区列 `trade_date` 进行范围过滤，触发 DolphinDB 分区裁剪，避免全表扫描。
- 使用 `order_book_id = "{stock_code}"` 精确匹配单支股票。
- 对 DataFrame 的 datetime 列统一转字符串后再序列化，避免 JSON 编码问题。

---

## 文件 3：Router (`quant_data/routers/tick.py`)

在现有 router 文件末尾追加端点：

```python
from quant_data.schemas.tick import (
    # ... 现有导入 ...
    TickQuerySingleRequest,
    TickQuerySingleResponse,
)

# ... 现有路由 ...

@router.post("/query", response_model=TickQuerySingleResponse, summary="查询单支股票 Tick 数据")
async def query_tick_single(
    body: TickQuerySingleRequest,
    _: dict = Depends(require_admin),
) -> TickQuerySingleResponse:
    """根据股票代码和日期范围查询 DolphinDB tickDB snapshots 表。"""
    service = TickService()
    rows = await service.query_tick_single(
        stock_code=body.stock_code,
        start_date=body.start_date,
        end_date=body.end_date,
    )
    return TickQuerySingleResponse(
        stock_code=body.stock_code,
        start_date=body.start_date,
        end_date=body.end_date,
        count=len(rows),
        data=rows,
    )
```

---

## 与现有代码的关系

项目已有 `/api/tick/query` 端点（接收 `symbols` 列表，支持分页和列筛选）。本实现与之路径相同，若需共存，建议将本端点注册为独立路径（如 `/query/single`）或在同一路径下通过请求体字段区分。此处按用户需求复用 `/api/tick/query` 路径提供单股票查询实现。

---

## 依赖注入说明

- `require_admin`：复用现有管理员鉴权依赖。
- `TickService`：无状态服务，每次请求实例化即可；若需连接池复用，可改为依赖注入单例。
- `run_ddb`：通过 `quant_data.dolphindb_pool` 模块的全局连接池执行 DolphinDB 脚本。
