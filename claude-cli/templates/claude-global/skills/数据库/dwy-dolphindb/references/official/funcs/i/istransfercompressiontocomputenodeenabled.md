---
source_url: https://docs.dolphindb.cn/zh/funcs/i/istransfercompressiontocomputenodeenabled.html
fetched_at: 2026-05-19T09:28:56Z
category: funcs
title: isTransferCompressionToComputeNodeEnabled
sha1: 7f5da46868d69cf033cef3a392bc54cf90378bcb
---

# isTransferCompressionToComputeNodeEnabled

## 语法

`isTransferCompressionToComputeNodeEnabled()`

## 详情

查询数据节点到计算节点的数据传输是否启用压缩。

## 参数

无

## 返回值

布尔值。true 表示开启了压缩，false 表示未开启压缩。

## 例子

```dolphindb
isTransferCompressionToComputeNodeEnabled()

//输出：true
```

**相关函数：**[enableTransferCompressionToComputeNode](../e/enabletransfercompressiontocomputenode.html)
