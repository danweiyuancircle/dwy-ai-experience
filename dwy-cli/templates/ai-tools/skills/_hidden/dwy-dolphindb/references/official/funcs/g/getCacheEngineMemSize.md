---
source_url: https://docs.dolphindb.cn/zh/funcs/g/getCacheEngineMemSize.html
fetched_at: 2026-05-19T09:22:51Z
category: funcs
title: getCacheEngineMemSize
sha1: 4071369df2db6e33c9854dae314c04c3cb190afd
---

# getCacheEngineMemSize

## 语法

`getCacheEngineMemSize()`

## 详情

查看当前节点下 OLAP 引擎的 Cache Engine 的内存情况，单位为字节。

## 参数

无

## 返回值

返回一个 ANY VECTOR：

第1个元素表示 Cache Engine 正在使用的内存量；

第2个元素表示 Cache Engine 保存的列文件占用的内存；

第3个元素表示指向列文件的指针所占用的内存；

第4个元素表示 Cache Engine 允许使用的内存上限。

## 例子

```dolphindb
setCacheEngineMemSize(0.4)
getCacheEngineMemSize()
// output
(0,0,0,429496729)
```

相关函数： [setCacheEngineMemSize](../s/setCacheEngineMemSize.html)
