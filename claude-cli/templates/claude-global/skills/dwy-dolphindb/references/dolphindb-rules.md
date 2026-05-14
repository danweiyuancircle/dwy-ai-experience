# DolphinDB 开发规则

所有涉及 DolphinDB 的代码必须遵循以下规则。AI 生成或修改代码时，必须逐条检查。

## 一、社区版硬约束

| 约束 | 值 | 违反后果 |
|---|---|---|
| 最大内存 | 8GB（建议 `maxMemSize=5`，留 3GB 给 OS） | 进程 OOM 崩溃 |
| 最大集群节点数 | 2（允许 1 controller + 1 datanode 的最小集群） | 超出被许可证拒绝;无法扩展到 3 节点以上 |
| 最大并发客户端连接 | 512（`maxConnections=512`） | 新连接直接被拒 |
| TSDB 单次 append | ≤ 204MB（约 800K 行 × 30 列） | 报错 `exceeds max limit` |
| 高可用 / Raft / 异步复制 | 不支持 | 多副本能力需企业版 |

### 本项目部署侧配置（非社区版硬限，是 VM/机器约束）

- VM 规格：**2 核 8 GB**（与社区版 8 GB 内存硬限一致）
- 因 CPU 只有 2 核，`workerNum` 和客户端 `dolphindb_pool_size` 按经验值 `2`，避免大量并行争抢 CPU；**这不是社区版硬限，而是 2 核机器上的合理取值**
- 512 并发连接是协议层上限，实际可持有的连接远少于这个数，不要把它当作"应该开 512 条"的指令

### 违规检测
如果代码中出现以下情况，必须提示：
- 单次 `append!` 数据超过 500K 行（安全上限）
- `maxMemSize` > 8
- 集群配置超过 2 个节点
- 客户端 `dolphindb_pool_size` 显著高于 CPU 核数（在 2 核机器上 > 4 需说明理由）

## 二、连接与会话管理

### 强制规则

| 场景 | 使用方式 | 原因 |
|---|---|---|
| 只读查询 | `run_ddb(script)` — 连接池 | 池自动管理连接复用 |
| 单次 upload + run | `run_ddb_with_data(script, data)` — 独立 Session | 确保 upload 和 run 在同一连接 |
| 批量 upload（多次循环） | `DDBSession` — 复用 Session | 避免每批新建/关闭连接的开销 |

```python
# ❌ 用连接池做 upload + run（变量跨连接不可见）
await run_ddb("upload_var = ...")  # 连接 A
await run_ddb("select * from upload_var")  # 可能路由到连接 B → 变量不存在

# ✅ 独立 Session 保证同一连接
await run_ddb_with_data(script, {"batch_data": df})

# ✅ 批量操作复用 Session
session = DDBSession()
try:
    for batch in batches:
        await session.upload_and_run(script, {"batch_data": batch})
finally:
    session.close()
```

### SDK v3 异步 API
- `DBConnectionPool.run()` 在 SDK v3 中是 **原生 async**，直接 `await pool.run(script)`
- **禁止** `asyncio.to_thread(pool.run, script)`（会产生 "coroutine never awaited" 警告）
- `Session.run()` 仍然是 **同步**，需要 `asyncio.to_thread()` 包装

## 三、分区裁剪（性能关键）

### 强制规则
**WHERE 条件必须直接命中分区列，禁止对分区列使用函数。**

```python
# ❌ 函数包裹分区列 → 全表扫描 → 8GB OOM
WHERE date(datetime) = 2020.01.01
WHERE month(trade_date) = 2020.01M
WHERE string(order_book_id) = "000001.XSHE"

# ✅ 直接范围过滤 → 分区裁剪生效
WHERE trade_date = 2020.01.01
WHERE trade_date >= 2020.01.01, trade_date < 2020.02.01
WHERE order_book_id in [`000001.XSHE`000002.XSHE]
```

### 范围查询禁止链式过滤

DolphinDB 不识别链式比较的两端边界，无法做分区剪枝。必须用 `between ... and ...` 或拆成两个独立条件。

```sql
-- ❌ 链式过滤 → 全表扫描（实测扫描 10091 个分区）
select * from loadTable(dbName, tbName)
where 2022.12.01 <= TradeDate <= 2022.12.03

-- ✅ between ... and ... → 分区剪枝（实测扫描 90 个分区）
select * from loadTable(dbName, tbName)
where TradeDate between 2022.12.01 and 2022.12.03

-- ✅ 拆成两个独立条件 → 分区剪枝
select * from loadTable(dbName, tbName)
where TradeDate >= 2022.12.01 and TradeDate <= 2022.12.03
```

可用 `[HINT_EXPLAIN]` 查看实际扫描的分区数验证：`select [HINT_EXPLAIN] * from ...` 输出中的 `partitions.local` 数量应等于范围内的分区数，而不是全库分区数。

### tickDB 分区列
- 第一级：`trade_date`（VALUE 分区，按日）
- 第二级：`order_book_id`（HASH 分区，20 桶）

### factorDB 分区列
- 第一级：`trade_date`（VALUE 分区，按月）
- 第二级：`factor_name`（VALUE 分区）

### 违规检测
如果 DolphinDB 查询脚本中出现以下模式，必须提示：
- `date(...)` / `month(...)` / `year(...)` 包裹分区列
- `WHERE 1=1` 无分区条件（全表扫描）
- `select * from loadTable(...)` 无 WHERE 子句
- 链式比较 `a <= col <= b`（必须改为 `between a and b` 或拆成两个独立条件）

## 四、批量写入

### 强制规则

```python
BATCH_SIZE = 500_000  # TSDB 上限 204MB，500K 行 ≈ 120MB（安全余量）
```

| 规则 | 说明 |
|---|---|
| 每批 ≤ 500K 行 | TSDB 单次 append 内存上限 204MB |
| 每批后 `gc.collect()` | 释放 Python 侧内存 |
| 每批后 `del batch_df` | 显式释放 DataFrame 引用 |
| 大文件用 pyarrow 分片读取 | `pf.read_table()` + `table.slice()` 避免全量加载 |
| 复用 Session | 批量循环中不要每批新建连接 |

```python
# ✅ 标准批量上传模式
table = pf.read_table(filepath)  # memory-mapped，不全量加载
session = DDBSession()
try:
    for i in range(num_batches):
        arrow_slice = table.slice(i * BATCH_SIZE, BATCH_SIZE)
        batch_df = prepare_batch(arrow_slice.to_pandas())
        del arrow_slice
        await session.upload_and_run(script, {"batch_data": batch_df})
        del batch_df
        gc.collect()
finally:
    session.close()
```

### 禁止的写法
```python
# ❌ 一次性读取大文件到 pandas（OOM）
df = pd.read_feather("10M_rows.ftr")  # 2.6GB 内存

# ❌ 单次 append 超过 500K 行
await run_ddb_with_data(script, {"data": df_1million_rows})

# ❌ 不释放内存
for batch in batches:
    await session.upload_and_run(script, {"data": batch})
    # 忘记 del + gc.collect()
```

## 五、DolphinDB 脚本语法

### 列名定义必须单行
```python
# ❌ 多行 backtick 列名 → 语法错误
schema = table(1:0,
    `col1`col2
    `col3`col4,
    [INT, INT, INT, INT])

# ✅ 单行定义
colNames = `col1`col2`col3`col4
colTypes = [INT, INT, INT, INT]
schema = table(1:0, colNames, colTypes)
```

### 多值过滤的 backtick 拼接
```python
# ✅ 正确的 Symbol 列表拼接
symbols = ["000001.XSHE", "000002.XSHE"]
symbols_str = "`" + "`".join(symbols)
script = f"... order_book_id in [{symbols_str}]"
# 生成: order_book_id in [`000001.XSHE`000002.XSHE]
```

### 脚本拼接用分号 + 换行
```python
# ✅ 多语句用 ;\n 分隔
script = (
    f'tickData = select * from loadTable("dfs://tickDB","snapshots") '
    f'where {ts_filter};\n'
    f'{user_script};\n'
    f'exec count(*) from result'
)
```

## 六、输入校验（安全关键）

### 强制规则
**所有外部输入在拼接到 DolphinDB 脚本前，必须经过 `validators.py` 校验。**

| 类型 | 正则 | 示例 |
|---|---|---|
| 因子名 | `^[a-zA-Z0-9_]{1,50}$` | `alpha_vwap_001` |
| 股票代码 (ukey) | `^\d{6}\.[A-Z]{2}$` | `000001.SZ` |
| 日期 | `^\d{4}\.\d{2}\.\d{2}$` | `2024.01.02` |

```python
# ✅ 先校验再拼接
validate_factor_name(factor_name)  # 不通过则抛 BusinessError
script = f'... factor_name = "{factor_name}"'

# ❌ 未校验直接拼接 → 脚本注入风险
script = f'... factor_name = "{user_input}"'
```

### 违规检测
如果代码中出现以下情况，必须提示：
- f-string 拼接 DolphinDB 脚本时使用了未经 `validate_*` 校验的变量
- 用户输入直接出现在 `run_ddb()` 的 script 参数中

## 七、分区操作

### 删除分区用 `dropPartition`，不用 `DELETE`
```python
# ✅ dropPartition — 原子操作，无 tombstone
dropPartition(db, partitionPath, tableName)

# ❌ DELETE — 标记删除，产生 tombstone，需后续 GC
delete from loadTable("dfs://tickDB", "snapshots") where trade_date = 2020.01.01
```

### 新增分区值
配置 `newValuePartitionPolicy=add`，VALUE 分区自动扩展，无需预创建。

## 八、查询优化

### 聚合查询合并
```python
# ❌ 3 次查询
min_date = await run_ddb("select min(trade_date) ...")
max_date = await run_ddb("select max(trade_date) ...")
count = await run_ddb("select count(*) ...")

# ✅ 1 次查询
result = await run_ddb(
    'select min(trade_date) as earliest, max(trade_date) as latest, count(*) as total '
    'from loadTable("dfs://tickDB","snapshots")'
)
```

### 多因子查询用 PIVOT BY
```python
# ✅ DolphinDB 服务端完成列转换，无需 Python 端 merge
script = (
    'select value from loadTable("dfs://factorDB","factors") '
    f'where {where_clause} '
    'pivot by trade_date, ukey, factor_name'
)
```

### 分页查询用 `limit offset, count`
```python
# ❌ SQL 标准语法 — DolphinDB 不支持 OFFSET 关键字
f"select * from loadTable(...) limit {page_size} offset {offset}"

# ✅ DolphinDB 分页语法：limit 跳过行数, 返回行数
offset = (page - 1) * page_size
f"select * from loadTable(...) limit {offset}, {page_size}"
```

### 只查需要的列
```python
# ❌ select *（传输全部 30 列）
"select * from loadTable(...)"

# ✅ 只取需要的列
"select trade_date, time, order_book_id, last, volume from loadTable(...)"
```

## 九、Docker 环境注意事项

### DolphinDB v3 Alpine 镜像
| 问题 | 解决方案 |
|---|---|
| 无 `curl` | 用 `wget` 替代 |
| `localhost` 解析到 IPv6 | healthcheck 用 `127.0.0.1` |
| macOS 无 `/etc/hostname` `/etc/machine-id` | 不要挂载这两个文件 |
| 自定义 cfg 中 `logFile`/`volumes` 路径与 Docker volume 冲突 | 只覆盖必要参数，其余用默认值 |
| `dataSync + CacheEngine` 必须同时启用 | 开发环境建议都不配置，用默认值 |

### healthcheck 配置
```yaml
healthcheck:
  test: ["CMD-SHELL", "wget -qO- --timeout=3 http://127.0.0.1:8848/ || exit 1"]
  start_period: 30s  # DolphinDB 启动较慢，给足初始化时间
  interval: 5s
  timeout: 5s
  retries: 10
```

### 后端连接配置
```
DOLPHINDB_HOST=dolphindb    # Docker 服务名（不是 localhost）
DOLPHINDB_PORT=8848
DOLPHINDB_POOL_SIZE=2       # 2 核机器的经验值;社区版协议上限是 512 并发,不是 2
```

## 十、数据类型映射

### Feather/Pandas → DolphinDB

| Python/Pandas 类型 | DolphinDB 类型 | 转换方式 |
|---|---|---|
| `uint32` (日期如 20191205) | `DATE` | `pd.to_datetime(str, format='%Y%m%d')` |
| `uint32` (时间如 91509000) | `INT` | `.astype('int64')` |
| `float64` | `DOUBLE` | 无需转换 |
| `uint64` | `LONG` | `.astype('int64')` |
| `uint32` | `INT` | `.astype('int64')` |
| `float64` 含 NaN → 整数 | `INT` | `.fillna(0).astype('int64')` |
| `object` (字符串) | `SYMBOL` | `.astype(str)` |

### 注意事项
- DolphinDB 不接受 `uint` 类型，必须先转 `int64`
- NaN 不能直接转整数，必须先 `fillna(0)`
- `SYMBOL` 类型是 DolphinDB 的字典编码字符串，适用于低基数列（如股票代码）

## 十一、测试 Mock 规范

### DolphinDB 测试不连真实服务
```python
# conftest.py 中使用 autouse fixture mock 所有 DolphinDB 调用
@pytest.fixture(autouse=True)
def mock_dolphindb():
    async def mock_run_ddb(script):
        if "snapshots" in script and "count" in script.lower():
            return pd.DataFrame({"count": [1000]})
        # ... 基于脚本内容的模式匹配
        return pd.DataFrame()

    with patch("app.services.tick_service.run_ddb", side_effect=mock_run_ddb):
        yield
```

### Mock 必须覆盖所有 import 路径
```python
# 每个 service 文件都有独立的 import，必须分别 patch
patch("app.services.tick_service.run_ddb", ...)
patch("app.services.tick_archive.run_ddb", ...)
patch("app.services.tick_compute.run_ddb", ...)
```

## 十二、分区设计原则（建表时）

### 单分区合理大小（压缩前）

| 引擎 | 推荐范围 | 说明 |
|---|---|---|
| OLAP | 100MB ~ 300MB | 列存按分区粒度加载，过大易 OOM |
| TSDB / PKEY | 400MB ~ 1GB | 内部还有 LevelFile 二级组织，单分区可大一些 |

分区过小：元数据膨胀、查询时分区数爆炸、命中 `maxPartitionNumPerQuery` 限制（默认 65536）。
分区过大：单分区加载内存压力大、并行度下降、删除/重写代价高。

### 分区层级与类型

| 维度 | 规则 |
|---|---|
| 层级 | 最少 1 级，最多 3 级；分区方案一经确定无法调整，库下所有表共用 |
| 范围分区 (RANGE) | **只能向后扩展且无法自动扩展**，需手动 `addRangePartitions` |
| 范围分区越界数据 | `allowMissingPartitions=true`（默认）会**静默丢弃**范围外数据；需要报错改为 `false` |
| 值分区 (VALUE) | 可自动扩展（需 `newValuePartitionPolicy=add`）；**不宜初始化过多空分区** |
| 哈希分区 (HASH) | 桶数固定，建库后不可改 |

### 分区方案设计反例

> 股票行情数据（每天 5000 万条记录），先按 `TradeDate` 值分区，再按 `SecurityID` 二级值分区。
> 假设全是国内股票（约 5000 只），一天分区数就达 5000+。每天数据 3GB，**每个分区只有约 0.6MB**。

后果：
- 默认 `maxPartitionNumPerQuery=65536`，每天 5000 个分区，**查 14 天就报错**：`The number of partitions relevant to the query is too large`
- 单分区 0.6MB 远低于 OLAP 100MB / TSDB 400MB 推荐下限，元数据开销远大于数据本身
- 修复方向：二级分区改用 `HASH(SecurityID, 20)`（按经验固定 20 桶），或合并到日粒度单级分区

### 设计检查项

- [ ] 单分区估算大小是否落在引擎推荐区间？
- [ ] 总分区数是否远低于单次查询 65536 上限？
- [ ] 二级是否用了高基数列做 VALUE 分区？（高基数列优先 HASH）
- [ ] RANGE 分区是否预留了 `addRangePartitions` 的扩展机制？是否需要 `allowMissingPartitions=false`？

## 十三、字符串/BLOB/SYMBOL 长度限制

自 **1.30.23 / 2.00.11** 版本起，分布式表写入对字符串类数据增加了硬性大小限制：

| 类型 | 上限 | 超限行为 |
|---|---|---|
| `STRING` | < 64 KB | 静默截断到 65,535 字节（64 KB - 1） |
| `BLOB` | < 64 MB | 静默截断到 67,108,863 字节（64 MB - 1） |
| `SYMBOL` | ≤ 255 字节 | **直接抛异常**，写入失败 |

### 强制规则

写入前必须做长度校验，**特别是 SYMBOL 列会让整批写入失败**：

```python
# ✅ 写入前校验 SYMBOL 列长度
MAX_SYMBOL_BYTES = 255
oversize_mask = batch_df["order_book_id"].str.encode("utf-8").str.len() > MAX_SYMBOL_BYTES
if oversize_mask.any():
    raise BusinessError(
        f"SYMBOL 列 order_book_id 有 {oversize_mask.sum()} 行超过 255 字节"
    )
```

### 类型选择建议

- 短编码字段（股票代码、因子名）→ `SYMBOL`，但必须保证 ≤ 255 字节
- 用户可输入的中等长度文本（备注、描述）→ `STRING`，注意 64 KB 截断风险，超长字段做应用层校验
- 大文本/二进制（JSON、文件）→ `BLOB`，超长会被截断而不是报错，**截断不可逆**，必须在应用层校验长度
- 中文按 UTF-8 编码，1 字符 ≈ 3 字节，预估时按字节而非字符

### 违规检测

- 写入路径上对 `SYMBOL` 列没有长度校验 → 整批写入可能失败
- 写入 `STRING`/`BLOB` 时没有长度上限断言 → 数据被静默截断，事后无法恢复

## 十四、检查清单

每次涉及 DolphinDB 的代码变更，必须逐条检查：

- [ ] WHERE 条件是否命中分区列？是否有函数包裹分区列？
- [ ] 范围条件是否使用 `between ... and ...` 或两个独立条件？是否存在链式比较 `a <= col <= b`？
- [ ] 批量写入是否 ≤ 500K 行？是否有 `gc.collect()`？
- [ ] 外部输入是否经过 `validators.py` 校验？
- [ ] 使用 `run_ddb` 还是 `run_ddb_with_data`？场景是否匹配？
- [ ] 连接池大小是否与 CPU 核数匹配（2 核机器建议 `pool_size=2`）？
- [ ] 查询是否只 select 了需要的列？
- [ ] 多次聚合查询能否合并为一次？
- [ ] 脚本中 backtick 列名是否在单行内？
- [ ] 新增 service 文件的 `run_ddb` 导入是否在 conftest.py 中 mock？
- [ ] 分页查询是否使用 `limit offset, count` 语法？（禁止 `LIMIT x OFFSET y`）
- [ ] 新建库表时单分区估算大小是否在引擎推荐区间内？总分区数是否远低于 65536？
- [ ] 写入路径对 `SYMBOL` 列是否有 ≤ 255 字节长度校验？`STRING` / `BLOB` 是否有上限断言以避免静默截断？
