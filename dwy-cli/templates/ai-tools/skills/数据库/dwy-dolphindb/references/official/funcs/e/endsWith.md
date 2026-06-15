---
source_url: https://docs.dolphindb.cn/zh/funcs/e/endsWith.html
fetched_at: 2026-05-19T09:20:54Z
category: funcs
title: endsWith
sha1: 20f2217413971e77ebc7aa6a1b682648d7514855
---

# endsWith

## 语法

`endsWith(X, str)`

## 详情

检查 *X* 是否以 *str* 结尾。如果是，返回 true； 否则返回 false。

## 参数

**X** 是搜索的目标字符串。它可以是标量或向量。

**str** 是被搜索的目标字符串。它可以是标量或向量。

## 返回值

布尔类型标量或向量。

## 例子

```dolphindb
endsWith('ABCDEF!', "F!");
// output
true

endsWith('ABCDEF!', "E!");
// output
false
```
