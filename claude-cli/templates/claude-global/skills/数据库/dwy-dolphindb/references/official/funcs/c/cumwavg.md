---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumwavg.html
fetched_at: 2026-05-19T09:18:01Z
category: funcs
title: cumwavg
sha1: aa7087e484570e5307aed055e9377e93f0bc1b2a
---

# cumwavg

## 语法

`cumwavg(X, Y)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

以 *Y* 为权重，计算 *X* 的累计加权平均。

## 返回值

DOUBLE 类型，其数据形式同 *X*(*Y*)。

## 例子

```dolphindb
cumwavg(2.2 1.1 3.3, 4 5 6);
// output
[2.2,1.588889,2.273333]

cumwavg(1 NULL 1, 1 1 1);
// output
[1,1,1]
```

相关函数：[wavg](../w/wavg.html)
