---
source_url: https://docs.dolphindb.cn/zh/progr/operators/pair.html
fetched_at: 2026-05-19T09:01:27Z
category: progr
title: pair(:)
sha1: 84ad55645df8ff21ea80fdb6b435964b9c020291
---

# pair(:)

## 语法

`a:b`

## 参数

**a** 和 **b** 必须是标量。

## 详情

返回一个数据对。

## 例子

```dolphindb
1:3+1;
// output
2:4

1:3<0:6;
// output
0 : 1
```
