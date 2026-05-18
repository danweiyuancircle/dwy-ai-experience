# SQL 批计算

## 核心范式

DDB 三种批计算范式，按数据量选：

| 数据量 | 范式 | 说明 |
|---|---|---|
| 单分区 / 单股 / 单天 | 直接 SQL | 一句话搞定 |
| 跨多分区 | `sqlDS` + `mr` 分布式 | 自动分片并行 |
| 复杂多步骤管道 | 中间内存表 + 多步 SQL | 拆步骤调试 |

## 范式 1：单步 SQL

```dolphindb
// 单天单股 SOIR
select TradeDate, TradeTime, SecurityID,
       (BidOrderQty - OfferOrderQty) \ (BidOrderQty + OfferOrderQty) as imbalance
from loadTable("dfs://stock_lv2_snapshot", "snapshot")
where TradeDate = 2024.01.03 and SecurityID = `600000`
```

## 范式 2：sqlDS + mr（**跨分区必用**）

```dolphindb
def calcSomething(snapshot){
    return select SecurityID, TradeDate,
        avg(LastPrice) as avgPx,
        sum(TotalVolumeTrade) as vol
    from snapshot
    group by SecurityID, TradeDate
}

dbName = "dfs://stock_lv2_snapshot"
tbName = "snapshot"
beginDate = 2024.01.01
endDate = 2024.01.31

// sqlDS = 把一个 SQL 切成多个数据源（按分区）
ds = sqlDS(<select * from loadTable(dbName, tbName)
            where TradeDate between beginDate and endDate>)

// mr = map-reduce
// 参数：数据源, map 函数, reduce 函数（可省）, final 合并, parallel
re = mr(ds, calcSomething, , unionAll, false)
```

**parallel=false 的意义**：写同一目标分区时必须 false。读分布式查询 + 写内存结果 → 可以 true。

## 完整案例：K 线合成（snapshot → 1 分钟 K）

```dolphindb
defg highPx(deltasHigh, highPrice, lastPrice){
    // 函数式聚合：如果有 deltas 就用 high，否则用 last
    if(sum(deltasHigh) > 0.000001){
        return max(highPrice)
    } else {
        return max(lastPrice)
    }
}

def calcKLine(snapshot){
    // 第一步：处理时间 + 计算 delta（按股票分组）
    tempTB = select TradeDate,
        iif(TradeTime <= 09:30:00.000, 09:30:00.000, TradeTime) as TradeTime,
        SecurityID,
        OpenPrice, HighPrice, LowPrice, LastPrice,
        iif(deltas(HighPrice) > 0.000001, 1, 0) as deltasHigh,
        iif(deltas(TotalVolumeTrade) == NULL,
            TotalVolumeTrade,
            deltas(TotalVolumeTrade)) as deltasVolume
    from snapshot
    where TradeTime >= 09:25:00.000
    context by SecurityID                  // 注意：deltas 要分组

    // 第二步：按 1 分钟桶聚合
    return select firstNot(LastPrice, 0) as open,
        highPx(deltasHigh, HighPrice, LastPrice) as high,
        last(LastPrice) as close,
        sum(deltasVolume) as volume
    from tempTB
    group by SecurityID, TradeDate,
        interval(X=TradeTime, duration=60s, label='left', fill=0) as bar1min
}

// 跑全月
dbName = "dfs://stock_lv2_snapshot"
ds = sqlDS(<select * from loadTable(dbName, "snapshot")
            where TradeDate between 2024.01.01 and 2024.01.31>)
result = mr(ds, calcKLine, , unionAll, false)
```

## 完整案例：SOIR（订单失衡率）

```dolphindb
def wavgSOIR(bidQty, askQty, lag=20){
    // rowWavg：按 10 档权重加权 (10,9,8,...,1)
    imbalance = rowWavg(
        (bidQty - askQty) \ (bidQty + askQty),
        10 9 8 7 6 5 4 3 2 1
    ).ffill().nullFill(0)

    // 滚动均值 + 标准差，做 z-score
    mean = mavg(prev(imbalance), (lag - 1), 2)
    std = mstdp(prev(imbalance) * 1000000, (lag - 1), 2) \ 1000000

    return iif(std >= 0.0000001,
               (imbalance - mean) \ std,
               NULL).ffill().nullFill(0)
}

re = select SecurityID, TradeDate, TradeTime,
            wavgSOIR(BidOrderQty, OfferOrderQty, lag=20) as soir
     from loadTable("dfs://stock_lv2_snapshot", "snapshot")
     where TradeDate between 2024.01.01 and 2024.01.31
     context by SecurityID csort TradeTime
```

**关键点**：
- `context by SecurityID csort TradeTime`：按股票分组、组内按时间排序
- `prev()`：取上一行，避免使用当前行未来信息
- `ffill().nullFill(0)`：先用前值补，前值也没有时填 0

## 完整案例：截面排名（行业内 z-score）

```dolphindb
// 输入：因子表 t(date, sid, industry, factor)
// 输出：每天每个行业内 z-score 排名

// 方式 1：context by 多键
select date, sid, industry, factor,
       (factor - avg(factor)) \ stdp(factor) as zscore
from t
context by date, industry

// 方式 2：pivot 后矩阵化
m = exec factor from t pivot by date, sid
// 转置：行=date, 列=sid -> 每行内 rank
rankM = rowRank(m, true) \ count(m[0])    // 转 percentile
```

## 时序窗口函数（DDB 强项）

| 函数 | 说明 |
|---|---|
| `prev(x, n=1)` | 取前 n 行 |
| `next(x, n=1)` | 取后 n 行 |
| `deltas(x)` | 一阶差分 |
| `ratios(x)` | 比率 |
| `cumsum/cumavg/cummax/cummin(x)` | 累计 |
| `mavg/msum/mmax/mmin(x, window)` | 滚动 |
| `mvar/mstdp(x, window)` | 滚动方差/标准差 |
| `ema(x, alpha)` | 指数移动平均 |
| `rolling(func, x, window, step)` | 通用滚动 |

## 截面函数

| 函数 | 说明 |
|---|---|
| `rowSum/rowAvg/rowMin/rowMax(m)` | 矩阵每行聚合 |
| `rowRank(m, asc=true)` | 行内排名 |
| `rowWavg(m, weights)` | 行加权平均 |
| `corrMatrix(m)` | 相关性矩阵 |
| `pivot by` | 长表 → 矩阵 |
| `unpivot` | 矩阵 → 长表 |

## Python 触发批计算

```python
# 方式 1：把 DDB 函数注册到服务端，Python 调用
ddb_func = """
def calcKLine(snapshot){ ... }
"""
s.run(ddb_func)

# 然后跑 mr
result = s.run("""
    ds = sqlDS(<select * from loadTable('dfs://k','snapshot')
                where TradeDate between 2024.01.01 and 2024.01.31>);
    mr(ds, calcKLine, , unionAll, false)
""")  # 返回 DataFrame

# 方式 2：用 submitJob 异步跑，避免 keepAlive 超时
jobId = s.run("""
    submitJob('calcK', 'calc kline for jan',
              {def(){
                ds = sqlDS(<select * from loadTable('dfs://k','snapshot')
                            where TradeDate between 2024.01.01 and 2024.01.31>);
                re = mr(ds, calcKLine, , unionAll, false);
                loadTable('dfs://k','k_minute').tableInsert(re)
              }})
""")
# 查进度
s.run(f"getJobStatus(`{jobId})")
```

## 性能技巧

1. **能 group by 就别 context by**：context by 保留所有行，内存翻倍。
2. **数组向量比拆列快**：10 档行情用 `DOUBLE[]` 一列，而不是 20 列。
3. **mr 的 final 函数选择**：返回小表用 `unionAll`，返回标量用 `+` 或 `add`。
4. **defg vs def**：`defg`（aggregate function）用于聚合上下文，性能比普通 `def` 在 group by 中快 10x+。
5. **避免 join 大表**：DDB 的 `equal join` 在大分布式表上很慢，能 pivot 解决就 pivot。
6. **chunkSize 调优**：mr 太多小任务调度开销大，太少不并行。社区版 4 worker → 控制在 8-16 个 chunk。

跨引用：建表 → [[create-database-table]]，调优 → [[performance-tuning]]。
