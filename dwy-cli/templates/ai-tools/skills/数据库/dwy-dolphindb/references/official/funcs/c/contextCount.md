---
source_url: https://docs.dolphindb.cn/zh/funcs/c/contextCount.html
fetched_at: 2026-05-19T09:15:46Z
category: funcs
title: contextCount
sha1: e93fd77b358aeb00e6747e48ffa98c5975284450
---

# contextCount

## 语法

`contextCount(X, Y)`

## 详情

计算 *X* 和 *Y* 中相同位置都不为 NULL 的元素个数。

## 参数

**X** 和 **Y** 必须是相同长度的向量。

## 返回值

INT 类型标量。

## 例子

```dolphindb
contextCount(1 2 3, 1 NULL 3)
// output
2

contextCount(1..3,true false true)
// output
3

contextCount(1 2 NULL, 1 NULL 3)
// output
1
```

相关函数：[contextSum](contextSum.html), [contextSum2](contextSum2.html)
