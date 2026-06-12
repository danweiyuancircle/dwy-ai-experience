---
source_url: https://docs.dolphindb.cn/zh/funcs/i/ilike.html
fetched_at: 2026-05-19T09:27:31Z
category: funcs
title: ilike
sha1: 7c44bb9e4f91760933781f2c14a7664dede5bf1e
---

# ilike

## 语法

`ilike(X, pattern)`

## 详情

判断字符串 *X* 中是否包含字符串 *pattern*。和函数 [like](../l/like.html) 不同，比较是不区分大小写的。

## 参数

**X** 可以是标量、向量或矩阵。

**pattern** 是一个字符串，通常包含类似 "%" 的通配符。

## 返回值

布尔标量、向量、矩阵。

## 例子

```dolphindb
ilike(`ABCDEFG, `de);
// output
0

ilike(`ABCDEFG, "%de%");
// output
1

a=`IBM`ibm`MSFT`Goog`YHOO`ORCL;
a ilike  "%OO%";
// output
[0,0,0,1,1,0]

a[a ilike  "%OO%"];
// output
["Goog","YHOO"]
```

相关函数：[like](../l/like.html)
