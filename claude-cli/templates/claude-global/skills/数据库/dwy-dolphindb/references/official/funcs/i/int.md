---
source_url: https://docs.dolphindb.cn/zh/funcs/i/int.html
fetched_at: 2026-05-19T09:27:50Z
category: funcs
title: int
sha1: a92c96596cc58f5aebc6a9bf7ab60ae19e1421ab
---

# int

## 语法

`int(X)`

## 详情

将输入的数据转换为 INT 类型数据。

## 参数

**X** 可以是任意数据类型。

## 返回值

整型，数据形式同 *X*。

## 例子

```dolphindb
x=int();
x;
```

返回：null

```dolphindb
typestr x;
```

返回：INT

```dolphindb
int(`10.9);
```

返回：10

```dolphindb
int(2147483647);
```

返回：2,147,483,647

注：

INT 数据类型的最大值为 231 -1 = 2,147,483,647。

```dolphindb
int(2147483648);
```

由于2,147,483,648 超出了 INT 数据类型的最大值，因此返回：null
