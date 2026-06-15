---
source_url: https://docs.dolphindb.cn/zh/funcs/c/char.html
fetched_at: 2026-05-19T09:14:57Z
category: funcs
title: char
sha1: eae524b630318f75853c87d5d8d5a24ecac38581
---

# char

## 语法

`char(X)`

## 详情

把输入转换为 CHAR 数据类型。

## 参数

**X** 可以是任意数据类型。

## 返回值

CHAR 类型标量。

## 例子

```dolphindb
x=char();
x;
```

返回：null

```dolphindb
typestr x;
```

返回：CHAR

```dolphindb
a=char(99);
a;
```

返回：'c'

```dolphindb
typestr a;
```

返回：CHAR

```dolphindb
char(a+5);
```

返回：'h'

```dolphindb
char("990");
```

返回：`Failed to convert the string to CHAR`

注：

`char` 函数会把输入的字符串识别为 ASCII 码，超出 ASCII
码范围的输入字符无法转换。
