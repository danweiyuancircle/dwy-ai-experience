---
source_url: https://docs.dolphindb.cn/zh/progr/statements/return.html
fetched_at: 2026-05-19T09:02:01Z
category: progr
title: return
sha1: 56ff4605a1a5056bc1063461c754fcd99a08ffcb
---

# return

## 语法

`return [expression]`

## 详情

*return* 语句终止一个函数的执行并返回执行结果。

## 例子

```dolphindb
def f(a, b) {c=a*2+b pow 2; return a+c};
f(1,2);
// output
7
```
