# DolphinDB 流计算引擎摘要

定位：DolphinDB 自研的高性能流处理引擎（C++），与时序数据库无缝融合，覆盖实时 ETL、低延时复杂计算、多源关联、流批一体。内置 10+ 流计算引擎，支持金融实时行情、量化因子、IoT 监控等场景。

## 流 vs 批查询对比

| 维度 | 批查询（SQL on DFS） | 流计算（Stream Engine） |
|------|---------------------|------------------------|
| 数据源 | 分布式分区表，静态历史数据 | 流数据表（share streamTable），持续追加 |
| 触发方式 | 用户主动 `select` | 数据写入流表 → 订阅 handler 推送 → 引擎触发 |
| 计算模式 | 一次性全量 / 批 | 增量、有状态、行/窗口触发 |
| 结果 | 结果集（返回客户端 / 落表） | 持续写入 outputTable（可级联订阅） |
| 延迟 | 秒～分钟 | 毫秒～亚毫秒 |
| 代码 | DolphinDB SQL | 同一套 metrics 表达式（流批一体） |

## 流引擎家族选型

| 引擎 | 场景 | 输入 | 输出 |
|------|------|------|------|
| `createTimeSeriesEngine` | 滑动/翻滚时间窗口聚合（K 线、分钟均值） | 带 timeColumn 的流表 | 每个窗口结束触发一行（含 metrics） |
| `createDailyTimeSeriesEngine` | 股票/期货固定交易时段的时序聚合 | 同上 + sessionStart/End | 每窗口一行，含跨段补齐 |
| `createSessionWindowEngine` | 按事件活跃度动态划分会话窗口（用户点击、设备脉冲） | 时间列 + sessionGap | 会话结束（gap 超时）触发一行 |
| `createCrossSectionalEngine` | 截面计算（指数内含值、批设备最值） | 含 keyColumn 的流表（每键最新值） | 按 perRow/perBatch/interval 触发 |
| `createReactiveStateEngine` | 高频有状态因子（ema 嵌套、累积/topN）；每输入一行输出一行 | 含 keyColumn 的 tick 流 | 与输入同频，含 factor 值 |
| `createAnomalyDetectionEngine` | 实时异常检测（温度持续上升、阈值越界） | 时间序列流 + 检测条件 | 命中条件触发告警行 |
| `createAsofJoinEngine` / `createSnapshotJoinEngine` / `createEquiJoinEngine` / `createLookupJoinEngine` / `createLeftSemiJoinEngine` / `createNearestJoinEngine` | 双流/流-维表实时关联（订单匹配快照、报价对齐成交） | 两个流表/键值表 | 关联结果流 |
| `createCEPEngine` | 复杂事件处理（订单异常模式、设备故障序列） | 事件流 + Monitor DSL | 命中模式发送事件/写表 |
| `streamEngineParser` | SQL → 自动拆解多引擎链路 | 含窗口/聚合/状态的 SQL | 自动 outputTable 串接 |

## 引擎链路（级联）

两种串法：

1. **显式串接**：A 引擎的 `outputTable` 是一个 `share streamTable`，B 引擎 `subscribeTable` 该流表 → handler 调 `append!{B}`。
2. **streamEngineParser 自动拆解**：用 SQL 描述复杂计算，parser 自动识别窗口/状态算子并组装多级引擎，省去手工链路。

示例（时序引擎 → 横截面引擎）：流表 `electricity` → `createTimeSeriesEngine` 滑动均值 → 写入 `outputTable1`（share streamTable） → 再用 `createReactiveStateEngine` 订阅 `outputTable1` 计算移动峰值。

## 流订阅核心 API

DolphinDB 服务端：

```dolphindb
// 1. 流表必须 share，否则订阅看不到
share streamTable(1000:0, `time`sym`price`qty, [TIMESTAMP,SYMBOL,DOUBLE,INT]) as trades

// 2. 创建引擎（以时序聚合为例）
outputTable = table(10000:0, `time`sym`open`high`low`close`vol,
                    [TIMESTAMP,SYMBOL,DOUBLE,DOUBLE,DOUBLE,DOUBLE,LONG])
eng = createTimeSeriesEngine(name="kline1min", windowSize=60000, step=60000,
        metrics=<[first(price), max(price), min(price), last(price), sum(qty)]>,
        dummyTable=trades, outputTable=outputTable,
        timeColumn=`time, keyColumn=`sym)

// 3. 订阅流表 → handler 喂引擎
subscribeTable(tableName="trades", actionName="kline1min_sub",
               offset=-1, handler=append!{eng}, msgAsTable=true)
```

Python API：

```python
import dolphindb as ddb
s = ddb.session()
s.connect("127.0.0.1", 8848, "admin", "123456")
s.enableStreaming(9999)  # 本机监听端口

def handler(msg):
    print(msg)  # msg 为 list 或 DataFrame，取决于 msgAsTable

s.subscribe(host="127.0.0.1", port=8848, handler=handler,
            tableName="outputTable", actionName="py_sub",
            offset=0, msgAsTable=True)
```

清理：`unsubscribeTable(,tableName, actionName)` → `dropStreamEngine(name)` → `undef(\`tableName, SHARED)`。

## 流批一体（replay）

`replay` 把历史数据按 timeColumn 还原成流速注入流表，复用同一套 metrics/引擎代码做回测：

- 历史回测：`replay(inputTables, outputTables, dateColumn, timeColumn, replayRate, parallelLevel)` → 引擎接到的数据顺序与实盘一致。
- 同一份因子表达式在批 SQL（`select metrics ... context by sym`）和流引擎中产出完全相同的值，校验便捷。

## 典型范式：tick → 1 分钟 K 线

```dolphindb
share streamTable(1000000:0, `time`sym`price`qty,
                  [TIMESTAMP, SYMBOL, DOUBLE, INT]) as trades

outputTable = table(100000:0,
    `time`sym`open`high`low`close`volume,
    [TIMESTAMP, SYMBOL, DOUBLE, DOUBLE, DOUBLE, DOUBLE, LONG])

klineEng = createTimeSeriesEngine(
    name        = "kline_1min",
    windowSize  = 60000,      // 60s
    step        = 60000,      // 翻滚（非滑动）
    metrics     = <[first(price), max(price), min(price), last(price), sum(qty)]>,
    dummyTable  = trades,
    outputTable = outputTable,
    timeColumn  = `time,
    keyColumn   = `sym        // 按股票分组
)

subscribeTable(
    tableName  = "trades",
    actionName = "kline_1min_sub",
    offset     = -1,
    handler    = append!{klineEng},
    msgAsTable = true
)
```

要切成滑动 K 线，把 `step` 改小于 `windowSize`（如 `step=10000, windowSize=60000` → 每 10s 输出近 1 分钟 K 线）。

## 常见陷阱

- **流表必须 `share`**：未 share 的 streamTable 订阅不到，且重启 session 即丢失；命名 `share ... as name`。
- **忘记清理订阅**：重复执行同一脚本前必须 `unsubscribeTable + dropStreamEngine + undef`，否则报 `engine already exists` / `subscription already exists`。
- **流计算函数限制**：响应式状态引擎只支持「状态函数」（内置滑窗/累积/topN 或 `@state` 修饰的自定义函数）；普通自定义函数若有状态依赖必须显式声明 `@state`。
- **不支持聚合嵌套**：时序引擎 `metrics` 中禁止 `sum(spread(ask,bid))` 这种聚合套聚合。
- **窗口边界规整**：第一个窗口起点按数据时间向 step 取整（不是数据到达时间）；窗口结束需要后续数据触发，最后一个不完整窗口不会被计算（除非用 `forceTriggerTime` / `closed=\`left` 等参数）。
- **Python 订阅端口**：`enableStreaming(port)` 监听的是**客户端**端口，需保证防火墙放行 server → client 方向；否则订阅创建成功但 handler 收不到数据。
- **offset 含义**：`-1` = 从订阅当下最新位置开始；`0` = 从流表第一条开始；正整数 = 从该位置开始。回测/补数据用 `0`，实盘用 `-1`。
- **outputTable 类型**：普通 table → 终点；share streamTable → 可被下游引擎再订阅串接。

## 下钻原文

- `references/official/stream/str_intro.md` — 流数据总览与核心特性
- `references/official/stream/time_series_engine.md` — 时序聚合引擎完整用法
- `references/official/stream/cross_sectional_engine.md` — 横截面引擎与触发模式
- `references/official/stream/reactive_state_engine.md` — 响应式状态引擎与高频因子
- `references/official/stream/session_window_engine.md` — 会话窗口引擎
- `references/official/stream/anomaly_detection_engine.md` — 异常检测引擎
- `references/official/stream/cep.md` / `cep_engine.md` / `cep_basic_concept.md` — CEP 复杂事件处理
- `references/official/stream/str_join_engine.md` / `asof_join_engine.md` / `snapshot_join_engine.md` — 流连接系列
- `references/official/stream/str_replay.md` / `str_replay_n21.md` / `str_replay_n2n.md` — 历史 replay
- `references/official/stream/str_eng_parser.md` — streamEngineParser 自动拆解
- `references/official/stream/str_api_python.md` / `py_sub.md` — Python 订阅 API
- `references/official/stream/str_table.md` / `share` / `subscribeTable` 文档 — 流表与订阅基础
