---
source_url: https://docs.dolphindb.cn/zh/funcs/e/enabletransfercompressiontocomputenode.html
fetched_at: 2026-05-19T09:20:49Z
category: funcs
title: enableTransferCompressionToComputeNode
sha1: 37c4e585540ef2f65b8e7eac774935fde2d780f2
---

# enableTransferCompressionToComputeNode

首发版本：3.00.5

## 语法

`enableTransferCompressionToComputeNode(enable)`

## 详情

用于控制数据节点在向计算节点传输数据前是否进行压缩。

## 参数

**enable** 布尔值，指定是否压缩将被传输的数据。true 表示压缩，false 表示不压缩。

## 返回值

无

## 例子

```dolphindb
enableTransferCompressionToComputeNode(true)
```

**相关函数：**[isTransferCompressionToComputeNodeEnabled](../i/istransfercompressiontocomputenodeenabled.html)
