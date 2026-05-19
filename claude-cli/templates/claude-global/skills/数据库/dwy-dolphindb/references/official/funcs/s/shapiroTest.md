---
source_url: https://docs.dolphindb.cn/zh/funcs/s/shapiroTest.html
fetched_at: 2026-05-19T09:39:14Z
category: funcs
title: shapiroTest
sha1: 8c16484c6bbb1d652fe07761ad51d523141b6fe6
---

# shapiroTest

## 语法

`shapiroTest(X)`

## 详情

对样本数据进行 Shapiro-Wilk 检验。

## 参数

**X** 是一个数值向量，表示样本。

## 返回值

一个字典，包含以下 key：

- method ：字符串 "Shapiro-Wilk normality test"
- pValue ：p 值
- W ：W 统计量

## 例子

```dolphindb
x = norm(0.0, 1.0, 50)
shapiroTest(x);

// output
method->Shapiro-Wilk normality test
pValue->0.621668
W->0.981612
```
