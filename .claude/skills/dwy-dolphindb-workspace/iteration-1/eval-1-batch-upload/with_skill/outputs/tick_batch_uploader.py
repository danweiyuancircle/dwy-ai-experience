"""
DolphinDB tick 数据批量上传模块。

约束：
- 社区版 8GB 内存，TSDB 单次 append ≤ 204MB
- 批量写入上限 500K 行
- 2 核机器，连接池/会话数保持精简
"""

import gc
import os
import re
from pathlib import Path

import pandas as pd
import pyarrow.feather as pf
from dolphindb import DDBSession

# ─────────────────────────────── 常量
BATCH_SIZE = 500_000  # TSDB 安全上限（≈120MB 余量）

# ─────────────────────────────── 输入校验

class BusinessError(ValueError):
    """业务参数非法"""


def _validate_trade_date(trade_date: str) -> str:
    """
    校验并标准化 trade_date 为 DolphinDB DATE 格式 `YYYY.MM.DD`。
    支持输入：`YYYY.MM.DD`、`YYYY-MM-DD`、`YYYY/MM/DD`、`YYYYMMDD`
    """
    if not isinstance(trade_date, str):
        raise BusinessError(f"trade_date 必须是字符串，收到 {type(trade_date).__name__}")

    # 统一归一化到 YYYY.MM.DD
    normalized = trade_date.strip()
    if re.match(r"^\d{4}\.\d{2}\.\d{2}$", normalized):
        return normalized
    if re.match(r"^\d{4}-\d{2}-\d{2}$", normalized):
        return normalized.replace("-", ".")
    if re.match(r"^\d{4}/\d{2}/\d{2}$", normalized):
        return normalized.replace("/", ".")
    if re.match(r"^\d{8}$", normalized):
        return f"{normalized[:4]}.{normalized[4:6]}.{normalized[6:]}"

    raise BusinessError(
        f"trade_date 格式非法: '{trade_date}'，"
        "期望格式：YYYY.MM.DD、YYYY-MM-DD 或 YYYYMMDD"
    )


def _validate_filepath(filepath: str) -> Path:
    """校验 feather 文件路径合法且存在。"""
    if not isinstance(filepath, str) or not filepath.strip():
        raise BusinessError("filepath 不能为空字符串")

    path = Path(filepath).resolve()
    if not path.exists():
        raise BusinessError(f"文件不存在: {path}")
    if not path.is_file():
        raise BusinessError(f"路径不是文件: {path}")
    if path.suffix.lower() not in (".feather", ".ftr"):
        raise BusinessError(f"仅支持 .feather/.ftr 文件，收到: {path.suffix}")

    return path


# ─────────────────────────────── 数据类型映射

_DTYPE_MAP = {
    "uint8": "int64",
    "uint16": "int64",
    "uint32": "int64",
    "uint64": "int64",
    "float32": "float64",
}


def _prepare_batch_for_dolphindb(df: pd.DataFrame) -> pd.DataFrame:
    """
    将 Pandas DataFrame 转换为 DolphinDB 可接受的类型。

    规则来源：references/dolphindb-rules.md 第十章
    """
    df = df.copy()

    for col in df.columns:
        dtype = str(df[col].dtype)

        # 1) 无符号整数 → int64（DolphinDB 不接受 uint）
        if dtype in _DTYPE_MAP:
            # 含 NaN 的浮点列想转整数，先 fillna(0)
            if df[col].isna().any() and "float" in dtype:
                df[col] = df[col].fillna(0)
            df[col] = df[col].astype(_DTYPE_MAP[dtype])
            continue

        # 2) float64 含 NaN → 若目标为整数列，需先 fillna(0)
        if dtype == "float64" and df[col].isna().any():
            # 保留 float64，由调用方决定是否需要进一步转 int
            pass

        # 3) object / string → SYMBOL（低基数字符串，如 order_book_id）
        if dtype == "object":
            df[col] = df[col].astype(str)

    return df


# ─────────────────────────────── 核心上传函数

async def upload_tick_snapshots(
    filepath: str,
    trade_date: str,
    ddb_host: str = "127.0.0.1",
    ddb_port: int = 8848,
    ddb_user: str = "admin",
    ddb_password: str = "123456",
) -> dict:
    """
    将 feather 文件中的 tick snapshots 数据批量写入 DolphinDB。

    Parameters
    ----------
    filepath : str
        feather 文件路径（.feather 或 .ftr）
    trade_date : str
        交易日，支持 `YYYY.MM.DD`、`YYYY-MM-DD`、`YYYYMMDD`
    ddb_host, ddb_port, ddb_user, ddb_password :
        DolphinDB 连接参数（默认连本地单节点）

    Returns
    -------
    dict
        {"total_rows": int, "batches": int, "status": "ok"}

    Raises
    ------
    BusinessError
        参数校验失败
    RuntimeError
        DolphinDB 写入异常
    """
    # 1. 输入校验
    path = _validate_filepath(filepath)
    td = _validate_trade_date(trade_date)

    # 2. 用 pyarrow memory-mapped 读取，避免一次性加载 200 万行到内存
    #    规则来源：第四章「大文件用 pyarrow 分片读取」
    arrow_table = pf.read_table(str(path), memory_map=True)
    total_rows = arrow_table.num_rows

    if total_rows == 0:
        return {"total_rows": 0, "batches": 0, "status": "ok"}

    # 3. 复用 DDBSession（批量循环不新建连接）
    #    规则来源：第二章「批量 upload（多次循环）→ DDBSession — 复用 Session」
    session = DDBSession(ddb_host, ddb_port, ddb_user, ddb_password)
    num_batches = (total_rows + BATCH_SIZE - 1) // BATCH_SIZE
    uploaded = 0

    try:
        for i in range(num_batches):
            offset = i * BATCH_SIZE
            limit = min(BATCH_SIZE, total_rows - offset)

            # 3.1 分片读取（零拷贝 slice）
            arrow_slice = arrow_table.slice(offset, limit)
            batch_df = arrow_slice.to_pandas()
            del arrow_slice  # 尽早释放 pyarrow buffer

            # 3.2 确保分区列存在且类型正确
            if "trade_date" not in batch_df.columns:
                # 若文件内无 trade_date，则以外部参数注入
                batch_df["trade_date"] = pd.to_datetime(td.replace(".", "-")).date()

            # 3.3 类型转换（uint→int64、NaN 处理等）
            batch_df = _prepare_batch_for_dolphindb(batch_df)

            # 3.4 构建 DolphinDB 脚本
            #     使用 upload + run 同一 Session，保证变量可见
            #     规则来源：第二章「单次 upload + run → 独立 Session」
            script = (
                f't = loadTable("dfs://tickDB", "snapshots");\n'
                f'append!(t, batch_data);\n'
                f'exec count(*) from t where trade_date = {td}'
            )

            # 同步 Session 需包装到线程（规则来源：第二章「Session.run() 仍然是同步，
            # 需要 asyncio.to_thread() 包装」）
            import asyncio
            await asyncio.to_thread(
                session.run,
                script,
                {"batch_data": batch_df},
            )

            uploaded += len(batch_df)

            # 3.5 显式释放内存 + gc
            #     规则来源：第四章「每批后 gc.collect() / del batch_df」
            del batch_df
            gc.collect()

    except Exception as exc:
        raise RuntimeError(f"DolphinDB 写入失败（batch {i}/{num_batches}, offset {offset}）: {exc}") from exc
    finally:
        session.close()

    return {"total_rows": uploaded, "batches": num_batches, "status": "ok"}


# ─────────────────────────────── 便捷同步入口（可选）

def upload_tick_snapshots_sync(*args, **kwargs) -> dict:
    """同步包装器。"""
    import asyncio
    return asyncio.run(upload_tick_snapshots(*args, **kwargs))
