---
source_url: https://docs.dolphindb.cn/zh/pydoc/AdvancedOperations/EventSendSub/eventsendsub.html
fetched_at: 2026-05-19T09:52:38Z
category: pydoc
title: 事件发送及订阅
sha1: 6cdf577a72add4ee3ac03b1ad633174c8e295276
---

# 事件发送及订阅

DolphinDB 3.00.0 版本引入了重大功能——复杂事件处理引擎（Complex Event Processing Engine，简称 CEP
引擎）。为配合使用该功能，Python API 从 3.0.0.0 版本开始提供了 cep 模块，该模块包含 Event
等类，用于自定义、发送和订阅事件。本节将介绍事件相关的操作，包含以下内容：

- 定义事件。
- 将事件写入异构流表，作为服务端 CEP 引擎接收的数据源。
- 订阅服务端 CEP 引擎输出的异构流表中的事件。

更多详细将在下文中分章节进行阐述。关于 CEP 引擎的介绍和使用请参考 [CEP 引擎](https://docs.dolphindb.cn/zh/stream/cep_engine.html) 。
