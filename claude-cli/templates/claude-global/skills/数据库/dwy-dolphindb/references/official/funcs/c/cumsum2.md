---
source_url: https://docs.dolphindb.cn/zh/funcs/c/cumsum2.html
fetched_at: 2026-05-19T09:17:51Z
category: funcs
title: cumsum2
sha1: 87a9bc8377375f3ffd902bfa2520a42bab2cc051
---

# cumsum2

## 语法

`cumsum2(X)`

参数说明和窗口计算规则请参考：[累计窗口系列（cum 系列）](../themes/cumFunctions.html)

## 详情

计算 *X* 元素的累计平方和。

## 返回值

DOUBLE 类型，其数据形式同 *X*。

## 例子

```dolphindb
x=[2,3,4];
cumsum2 x;
// output
[4,13,29]

m=matrix(1 2 3, 4 5 6);
m;
```

| #0 | #1 |
| --- | --- |
| 1 | 16 |
| 5 | 41 |
| 14 | 77 |

相关函数：[sum2](../s/sum2.html)
