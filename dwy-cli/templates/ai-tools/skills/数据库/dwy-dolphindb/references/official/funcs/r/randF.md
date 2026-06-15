---
source_url: https://docs.dolphindb.cn/zh/funcs/r/randF.html
fetched_at: 2026-05-19T09:34:59Z
category: funcs
title: randF
sha1: 56db7e4d10f84dc4c5a8487600785ba0019ff6d6
---

# randF

## 语法

`randF(numeratorDF, denominatorDF, count)`

## 详情

生成指定个数的 F 分布随机数。

## 参数

**numeratorDF** 和 **denominatorDF** 都是正数，表示 F 分布的自由度。

**count** 是正整数，表示生成的随机数个数。

## 返回值

长度为 *count* 的 DOUBLE 类型向量。

## 例子

```dolphindb
randF(2.31, 0.671, 2);
// output
[0.41508, 0.642609]
```
