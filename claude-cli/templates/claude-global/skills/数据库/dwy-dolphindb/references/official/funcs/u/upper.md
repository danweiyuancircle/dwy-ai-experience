---
source_url: https://docs.dolphindb.cn/zh/funcs/u/upper.html
fetched_at: 2026-05-19T09:43:27Z
category: funcs
title: upper
sha1: aadec061d3bf6acf677143d5c24c80a33521e42d
---

# upper

## 语法

`upper(X)`

## 详情

`upper` 函数把字符串或字符串列表中的所有字符转换为大写。

## 参数

**X** 是一个字符串标量或向量。

## 返回值

字符串标量或向量。

## 例子

```dolphindb
x = `Ibm`C`AapL;
x.upper();
// output: ["IBM","C","AAPL"]

(`Thl).upper();
// output: THL
```

相关函数： [lower](../l/lower.html)
