---
source_url: https://docs.dolphindb.cn/zh/funcs/s/strip.html
fetched_at: 2026-05-19T09:40:43Z
category: funcs
title: strip
sha1: c4d08bbd47a5d070188c0311bee58e9650aafa85
---

# strip

## 语法

`strip(X)`

## 详情

去掉首尾所有空格，制表符，换行和回车符号。

## 参数

**X** 是字符串标量或向量。

## 返回值

STRING 类型，数据形式与输入参数相同。

## 例子

```dolphindb
x="\nhello world\t\n";
x;

// output
hello world

strip x;
// output
hello world
```

相关函数：[trim](../t/trim.html)
