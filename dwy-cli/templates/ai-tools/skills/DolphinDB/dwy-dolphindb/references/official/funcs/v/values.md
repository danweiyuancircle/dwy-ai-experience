---
source_url: https://docs.dolphindb.cn/zh/funcs/v/values.html
fetched_at: 2026-05-19T09:43:34Z
category: funcs
title: values
sha1: 713c34e785739d8da8be90df9d7fbbabca7c8861
---

# values

## 语法

`values(X)`

## 详情

返回字典 *X* 中的所有值，或者以元组形式返回表 *X* 中的所有列。

## 参数

**X** 是一个字典或表。

## 返回值

向量或元组，数据类型取决于字典的值或表的所有列。

## 例子

```dolphindb
z=dict(INT,DOUBLE)
z[5]=7.9
z[3]=6
z.values();
// output
[6,7.9]

t = table(1 2 3 as id, 4 5 6 as x, `IBM`MSFT`GOOG as name);
values(t);
// output
([1,2,3],[4,5,6],["IBM","MSFT","GOOG"])
```

相关函数：[keys](../k/keys.html)
