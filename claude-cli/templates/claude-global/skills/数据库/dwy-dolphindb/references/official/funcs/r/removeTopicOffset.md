---
source_url: https://docs.dolphindb.cn/zh/funcs/r/removeTopicOffset.html
fetched_at: 2026-05-19T09:35:48Z
category: funcs
title: removeTopicOffset
sha1: 5c0023bab053b957ae759985d6676b03c0755054
---

# removeTopicOffset

## 语法

`removeTopicOffset(topic)`

## 详情

删除给定订阅主题（topic）的持久化保存的最新一条已经处理订阅数据的偏移量（在 [subscribeTable](../s/subscribeTable.html)
函数中通过指定 *persistOffset* 参数为 true 获得）。

## 参数

**topic** 是 [subscribeTable](../s/subscribeTable.html) 函数返回的订阅主题。
