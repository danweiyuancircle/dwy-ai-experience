---
source_url: https://docs.dolphindb.cn/zh/backtest/backtest_intro.html
fetched_at: 2026-05-19T09:47:00Z
category: backtest
title: 回测与模拟撮合
sha1: be3c597836cc7798a48c62898d774f7d7ce953c1
---

# 回测与模拟撮合

DolphinDB 提供了强大的回测解决方案，包括回测引擎插件（Backtest）和模拟撮合引擎插件（Matching Engine Simulator），帮助用户精准测试和验证策略在实盘交易中的效果。

## 主要组件

- **模拟撮合引擎插件（Matching Engine Simulator）**：用于模拟用户在某个时间点发出或取消订单的操作，并获取相应的交易结果。
- **回测引擎插件（Backtest）**：基于分布式存储和计算、多范式的编程语言和模拟撮合引擎插件，提供事件型回测引擎服务。

## 支持的资产类型

回测引擎支持多资产策略回测，涵盖：

- 股票
- 期货
- 期权
- 债券（银行间债券）
- 数字货币
- 多资产组合
