---
source_url: https://docs.dolphindb.cn/zh/funcs/e/eye.html
fetched_at: 2026-05-19T09:21:34Z
category: funcs
title: eye
sha1: 72dfe1356a61bfd064529a0b63eb6ee66262de52
---

# eye

## 语法

`eye(n)`

## 详情

生成一个维度为 *n* 的单位矩阵。

## 参数

**n** 是一个正整数，表示维度。

## 返回值

一个 DOUBLE 类型矩阵。

## 例子

```dolphindb
eye(3);
```

| #0 | #1 | #2 |
| --- | --- | --- |
| 1 | 0 | 0 |
| 0 | 1 | 0 |
| 0 | 0 | 1 |
