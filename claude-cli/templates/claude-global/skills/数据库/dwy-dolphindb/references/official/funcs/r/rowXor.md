---
source_url: https://docs.dolphindb.cn/zh/funcs/r/rowXor.html
fetched_at: 2026-05-19T09:37:38Z
category: funcs
title: rowXor
sha1: ca5366ed68142f00446076ae5403f3a8bf726ead
---

# rowXor

## 语法

`rowXor(args...)`

row 系列函数通用参数说明和计算规则请参考：[rowFunctions](../themes/rowFunctions.html)

## 详情

逐行进行逻辑异或操作。

## 返回值

返回一个长度与输入参数行数相同的向量。

## 例子

```dolphindb
m=matrix([true false false, true true true, true true true]);
rowXor(m);
// output
[1,0,0]

t=table(true false false true false true as x, false true false true false true as y, false false true true false false as z);
t;
```

| x | y | z |
| --- | --- | --- |
| 1 | 0 | 0 |
| 0 | 1 | 0 |
| 0 | 0 | 1 |
| 1 | 1 | 1 |
| 0 | 0 | 0 |
| 1 | 1 | 0 |

```dolphindb
rowXor(t);
// output
[1,1,1,1,0,0]

t=table(`AAPL`MS`IBM`IBM`C as sym, 49.6 29.46 29.52 30.02 174.97 as price1, 175.23 50.76 50.32 51.29 26.23 as price2);
select * from t where rowXor(price1$ 30, price2$ 50);
```

| sym | price1 | price2 |
| --- | --- | --- |
| MS | 29.46 | 50.76 |
| IBM | 29.52 | 50.32 |
| C | 174.97 | 26.23 |

相关函数：[xor](../x/xor.html)
