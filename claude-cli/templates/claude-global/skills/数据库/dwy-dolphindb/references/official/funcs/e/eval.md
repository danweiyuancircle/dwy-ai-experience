---
source_url: https://docs.dolphindb.cn/zh/funcs/e/eval.html
fetched_at: 2026-05-19T09:21:10Z
category: funcs
title: eval
sha1: d674cf1adb00e7afb43c2bf86ef65e0214593fb2
---

# eval

## 语法

`eval(expr)`

## 详情

解析给定的元代码。

注：

- DolphinDB `eval` 用于执行 DolphinDB 元代码。
- Python 内置的 [eval](https://docs.python.org/3/library/functions.html#eval) 用于执行 Python 表达式字符串。
- [pandas.eval](https://pandas.pydata.org/docs/reference/api/pandas.eval.html) 用于对 pandas
  对象执行表达式字符串。

## 参数

**expr** 是元代码。

## 例子

```dolphindb
eval(<1+2>);
// output
3

eval(<1+2+3=10>);
// output
0

eval(expr(6,<,8));
// output
1

eval(expr(sum, 1 2 3));
// output
6

a=6; b=9;
eval(expr(<a>,+,<b>));
// output
15
```

相关函数：[expr](expr.html), [parseExpr](../p/parseExpr.html)
