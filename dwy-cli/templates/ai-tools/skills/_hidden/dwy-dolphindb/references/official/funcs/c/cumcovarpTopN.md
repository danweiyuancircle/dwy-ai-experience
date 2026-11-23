---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumcovarpTopN.html
fetched_at: 2026-05-19T09:17:27Z
category: funcs
title: cumcovarpTopN
sha1: 642f23204bf9dafcdec24f59b383d092c880af1e
---

# cumcovarpTopN

首发版本：3.00.5

## 语法

`cumcovarpTopN(X, Y, S, top, [ascending=true],
[tiesMethod='latest'])`

部分通用参数说明和窗口计算规则请参考：[cumTopN
系列](../themes/cumTopN.html)

## 详情

在累计窗口内，根据 *ascending* 指定的排序方式将 *X* 和 *Y* 按照 *S* 进行稳定排序后，取前
*top* 个元素，然后计算 *X* 和 *Y* 的总体协方差。

## 返回值

DOUBLE 类型，其数据形式取决于 *X* (*Y*)。

## 例子

```dolphindb
X=1 2 3 10 13 4 3
Y = 1 7 8 9 0 5 8
S = 0.3 0.5 0.1 0.1 0.5 0.2 0.4
cumcovarpTopN(X, Y, S, 6)
// output: [0,1.5,2.33,7.25,-3.2,-2.67,-2.78]
```

相关函数：[covarp](covarp.html)
