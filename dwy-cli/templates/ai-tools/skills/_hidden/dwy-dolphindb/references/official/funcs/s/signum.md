---
source_url: https://docs.dolphindb.cn/zh/funcs/s/signum.html
fetched_at: 2026-05-19T09:39:22Z
category: funcs
title: signum
sha1: caea7bca2699f6129966fb3cbabfb01b116c7982
---

# signum

## 语法

`signum(X)`

别名：sign

## 详情

返回 *X* 的符号标志。

## 参数

**X** 是布尔值或数值类型的标量、向量或矩阵。

## 返回值

如果 *X* 为正数，返回1； 如果 *X* 为0，返回0；如果 *X* 为负数，返回-1；如果 *X* 中元素为 NULL，则返回 NULL。

## 例子

```dolphindb
signum(8.2 0 -6 NULL);
// output
[1,0,-1, ]
```
