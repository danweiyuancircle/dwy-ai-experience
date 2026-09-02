---
source_url: https://docs.dolphindb.cn/zh/funcs/s/sinppet.html
fetched_at: 2026-05-19T09:39:33Z
category: funcs
title: snippet
sha1: daf67c5a8517778b200e0ab62b99c8fbad792f85
---

# snippet

## 语法

`snippet(X)`

## 详情

获取打印结果。

## 参数

**X** 任意数据。

## 返回值

返回一个字符串标量。

## 例子

```dolphindb
a = [["a","b"],"c"]
snippet(a)
//output
"(["a","b"],"c")"

snippet(date(2023.01.01))
//output
"2023.01.01"
```
