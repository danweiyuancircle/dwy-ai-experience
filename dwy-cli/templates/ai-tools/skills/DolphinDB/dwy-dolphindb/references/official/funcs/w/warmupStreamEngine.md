---
source_url: https://docs.dolphindb.cn/zh/funcs/w/warmupStreamEngine.html
fetched_at: 2026-05-19T09:43:48Z
category: funcs
title: warmupStreamEngine
sha1: 418d8f55c5a378357b47ccb4be7f9cf9790df79f
---

# warmupStreamEngine

## 语法

`warmupStreamEngine(engine, msgs)`

## 详情

将预热数据写入流数据引擎，但不输出计算结果，仅将结果保留为中间状态。当下一批数据写入引擎时，可以基于该中间状态进行计算。

目前仅支持响应式状态引擎，时间序列聚合引擎和日级时间序列引擎。

## 参数

**engine** 是创建流数据引擎时返回的表对象。

**msgs** 是一个数据表，表示预热数据。。

## 返回值

无。

## 例子

下例比较了使用 `warmupStreamEngine` 预热对计算结果的影响。创建两个相同的响应式状态引擎，对 engineA
注入预热数据；engineB 未注入预热数据。

```dolphindb
// 模拟数据
trade=table(1000:0, `date`sym`price`volume, [DATE, SYMBOL, DOUBLE, INT])
n=3000*100
date=take(2021.03.08, n)
sym=take("A"+string(1..3000), n)
price=round(rand(100.0, n), 2)
volume=rand(100, n)
table1 = table(date, sym, price, volume)
outputTableA = table(n:0, `sym`factor1, [STRING,DOUBLE])
outputTableB = table(n:0, `sym`factor1, [STRING,DOUBLE])

// 创建流数据引擎并注入数据
dropStreamEngine("test1")
dropStreamEngine("test2")
engineA = createReactiveStateEngine("test1", <ema(volume, 40)>, table1, outputTableA, "sym")
engineB = createReactiveStateEngine("test2", <ema(volume, 40)>, table1, outputTableB, "sym")
warmupStreamEngine(engineA, table1) // 使用 warmupStreamEngine 预热

// 向引擎分别写入数据：
date=take(2021.03.09, n)
sym=take("A"+string(1..3000), n)
price=round(rand(100.0, n), 2)
volume=rand(100, n)
table2 = table(date, sym, price, volume)
engineA.append!(table2)
engineB.append!(table2)
```

outputTableA：

![](../images/warmupStreamEngine1.png)

outputTableB：

![](../images/warmupStreamEngine2.png)

使用 `warmupStreamEngine` 将预热数据写入流数据引擎 engineA，基于中间状态计算，输出表 outputTableA
自第 1 行开始返回非空数据。由于窗口长度为 40，输出表 outputTableB 前39个分组返回值为空，自 117001 行开始返回非空数据。
