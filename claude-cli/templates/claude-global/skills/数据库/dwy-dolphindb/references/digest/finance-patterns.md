# DolphinDB 金融场景核心范式

来源：tutorials/new_users_finance.md、backtest/backtest_intro.md、funcs/b/bar.md、funcs/d/dailyAlignedBar.md。

## 1. Tick 行情表结构（L2 逐笔成交）

COMPO 分区（日期 VALUE + 股票代码 HASH），TSDB 引擎，sortColumns 必须含 SecurityID + TradeTime。

```dolphindb
dbDate = database("", VALUE, 2024.01.01..2024.12.31)
dbSym  = database("", HASH, [SYMBOL, 25])
db = database("dfs://tick_l2", COMPO, [dbDate, dbSym], engine="TSDB")

schema = table(
    1:0,
    `SecurityID`TradeTime`TradePrice`TradeQty`TradeAmount`BuyNo`SellNo`TradeBSFlag`ChannelNo,
    [SYMBOL, TIMESTAMP, DECIMAL64(4), LONG, DECIMAL64(4), LONG, LONG, SYMBOL, INT]
)
db.createPartitionedTable(
    schema, `tick,
    partitionColumns=`TradeTime`SecurityID,
    sortColumns=`SecurityID`TradeTime,    // TSDB 必须，最后一列为时间
    keepDuplicates=ALL
)
```

L2 快照 10 档行情用数组向量列：

```dolphindb
`BidPrice`BidQty`OfferPrice`OfferQty 列类型用 DECIMAL64(4)[] 与 LONG[]
```

## 2. K 线（OHLCV）表结构

```dolphindb
kline = table(
    1:0,
    `SecurityID`BarTime`Open`High`Low`Close`Volume`Amount,
    [SYMBOL, TIMESTAMP, DECIMAL64(4), DECIMAL64(4), DECIMAL64(4), DECIMAL64(4), LONG, DECIMAL64(4)]
)
db.createPartitionedTable(kline, `kline_1min,
    partitionColumns=`BarTime`SecurityID,
    sortColumns=`SecurityID`BarTime)
```

## 3. K 线合成

### 3.1 批量 SQL（历史数据）

bar 函数按固定窗口分组，对齐到 0 时刻：

```dolphindb
select
    first(TradePrice) as Open,
    max(TradePrice)   as High,
    min(TradePrice)   as Low,
    last(TradePrice)  as Close,
    sum(TradeQty)     as Volume,
    sum(TradeAmount)  as Amount
from loadTable("dfs://tick_l2", "tick")
where date(TradeTime) = 2024.01.15
group by SecurityID, bar(TradeTime, 60s) as BarTime
```

### 3.2 dailyAlignedBar（对齐交易时段，处理午休/隔夜）

A 股两段：09:30-11:30、13:00-15:00：

```dolphindb
sessionsBegin = 09:30:00 13:00:00
sessionsEnd   = 11:30:00 15:00:00
select first(price) as Open, max(price) as High, min(price) as Low,
       last(price) as Close, sum(volume) as Volume
from tick
group by SecurityID,
    dailyAlignedBar(TradeTime, sessionsBegin, 1m, sessionsEnd, mergeSessionEnd=true) as BarTime
```

支持隔夜期货时段（13:30-16:30 + 22:30 跨日至 02:30）。

### 3.3 流式 createTimeSeriesEngine（实时合成）

```dolphindb
engine = createTimeSeriesEngine(
    name="kline1min",
    windowSize=60000, step=60000,
    metrics=<[first(TradePrice), max(TradePrice), min(TradePrice),
              last(TradePrice), sum(TradeQty)]>,
    dummyTable=tickStream, outputTable=klineStream,
    timeColumn=`TradeTime, keyColumn=`SecurityID,
    useSystemTime=false, useWindowStartTime=true
)
subscribeTable(tableName="tickStream", actionName="kline1min",
               handler=append!{engine}, msgAsTable=true)
```

## 4. 因子计算

DolphinDB 内置千余指标函数 + TA-lib 接口 + Alpha101 / 国君 191 因子库。

### 4.1 截面 z-score

```dolphindb
select SecurityID, BarTime,
       (Close - avg(Close)) \ std(Close) as zscore
from kline_1min
context by BarTime    // 按时间截面分组
```

### 4.2 时序 mavg / rolling

```dolphindb
update kline_1min set ma20 = mavg(Close, 20) context by SecurityID
update kline_1min set rsi  = ta::rsi(Close, 14) context by SecurityID
```

### 4.3 WorldQuant Alpha101 / 国君 Alpha191

模块名：`wq101alpha` / `gtja191alpha`，加载后 `wq101alpha::alpha1(...)` 直接调用，参考教程 [Practical_Factor_Analysis_Modeling](../official/tutorials/Practical_Factor_Analysis_Modeling.md)。

## 5. TopN 选股 SQL

DolphinDB 用 `limit`（小写），不是 SQL 标准的 `LIMIT`：

```dolphindb
// 按当日成交额取前 50
select SecurityID, sum(Amount) as amt
from loadTable("dfs://tick_l2", "tick")
where date(TradeTime) = 2024.01.15
group by SecurityID
order by amt desc
limit 50
```

参考教程 [DolphinDB_TopN](../official/tutorials/DolphinDB_TopN.md)，专门讲千万级数据下的 TopN 优化（topN 排序索引、context by + isort）。

## 6. 回测引擎

`Backtest` 插件 + `Matching Engine Simulator` 模拟撮合插件。

- 资产：股票 / 期货 / 期权 / 银行间债券 / 数字货币 / 多资产组合
- 数据源：DolphinDB 分布式表（dfs://）或本地 csv 回放
- 模式：事件驱动型回测，订单流通过 Matching Engine 撮合，输出成交记录 + 持仓 + 盈亏

下钻：[backtest_intro.md](../official/backtest/backtest_intro.md)。

## 7. 交易日历

模块 `MarketHoliday`，处理节假日/调休：

```dolphindb
use MarketHoliday
MarketHoliday::isBusinessDay(2024.10.01, "CN")        // false（国庆）
MarketHoliday::businessDayOffset(2024.09.30, 1, "CN") // 2024.10.08（下一交易日）
MarketHoliday::businessDaysBetween(2024.01.01, 2024.12.31, "CN")  // 全年交易日数
```

## 8. 金融场景特有陷阱

| 陷阱 | 正确做法 | 错误做法 |
|------|---------|---------|
| 价格精度 | `DECIMAL64(4)` 或 `DECIMAL128(N)` | `DOUBLE`（浮点累加误差，金额对账不上） |
| 股票代码 | `SYMBOL`（≤ 255 字节，自动字典编码，分区/排序友好） | `STRING`（不参与字典，体积大） |
| 时间类型 | `TIMESTAMP`（毫秒精度，年份范围足） | `DATETIME`（2038 年溢出，秒精度不够 tick） |
| L2 高频时间 | `NANOTIMESTAMP`（纳秒） | `TIMESTAMP`（毫秒粒度，逐笔会撞时间戳） |
| TSDB sortColumns | `[SecurityID, TradeTime]`，时间放最后 | 时间放前面 → 同 SecurityID 时序读取退化 |
| L2 10 档行情 | 数组向量 `DECIMAL64(4)[]` 一列存 10 个价 | 拆 10 个列 BidPrice1..BidPrice10（schema 难扩展） |
| 分区粒度 | 日期 VALUE + 股票 HASH 25 桶 | 按分钟分区（元数据爆炸，meta 撑爆控制节点） |
| K 线 bar 截断 | `bar(time, 60s)` / `dailyAlignedBar(...)` 处理跨段 | 自己 `minute(time) \ N` 拼时间戳 |
| TopN SQL | 小写 `limit 50` | 大写 `LIMIT 50`（语法错误） |
| 整数溢出 | `barMinutes*60*long(1000000000)` 显式转 LONG | `barMinutes*60*1000000000`（int 溢出） |

## 9. 下钻原文

- `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/tutorials/new_users_finance.md` — 金融入门完整教程
- `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/tutorials/OHLC.md` + `OHLC_2.md` — K 线合成专题
- `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/tutorials/DolphinDB_TopN.md` — TopN 优化
- `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/tutorials/Practical_Factor_Analysis_Modeling.md` — Alphalens 因子分析
- `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/backtest/backtest_intro.md` — 回测引擎概述
- `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/funcs/b/bar.md` — bar 函数
- `/Users/chances/WebstormProjects/dwy-shared/claude-cli/templates/claude-global/skills/数据库/dwy-dolphindb/references/official/funcs/d/dailyAlignedBar.md` — 对齐交易时段分组
