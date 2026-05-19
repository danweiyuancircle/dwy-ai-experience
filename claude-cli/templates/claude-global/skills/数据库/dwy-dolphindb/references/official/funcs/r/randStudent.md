---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randStudent.html
fetched_at: 2026-05-19T09:35:08Z
category: funcs
title: randStudent
sha1: bb40e17cfc74f86e62e1a4f805464c24e09dc3e1
---

# randStudent

## 语法

`randStudent(df, count)`

## 详情

生成指定个数的 t 分布随机数。

## 参数

**df** 是正数，表示t分布的自由度。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randStudent(2.31, 2);

// output
[-0.543993, 0.375804]
```
