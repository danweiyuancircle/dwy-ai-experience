---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getSystemLoadAvg.html
fetched_at: 2026-05-19T09:26:19Z
category: funcs
title: getSystemLoadAvg
sha1: 08a358cceae16a033c65c92f7ee958a3d0498713
---

# getSystemLoadAvg

## 语法

`getSystemLoadAvg()`

## 详情

返回实时系统平均负载。使用该函数前，需要启动性能监控，即在配置文件中把 *perfMonitoring* 设为1。

## 返回值

DOUBLE 类型标量。

## 例子

```dolphindb
getSystemLoadAvg();

// output: 5.664062
```
