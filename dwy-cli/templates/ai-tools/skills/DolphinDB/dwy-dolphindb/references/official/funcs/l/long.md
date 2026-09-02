---
source_url: https://docs.dolphindb.cn/zh/funcs/l/long.html
fetched_at: 2026-05-19T09:30:28Z
category: funcs
title: long
sha1: 35099862002af32f65832995833b5b905668715d
---

# long

## 语法

`long(X)`

## 详情

将 *X* 的数据类型转换为 LONG。

## 参数

**X** 可以是任意数据类型。

## 返回值

LONG 类型的结果。

## 例子

```dolphindb
x=long();
x;
```

返回：null

```dolphindb
typestr x;
```

返回：LONG

```dolphindb
long(`10.9);
```

返回：10

```dolphindb
long(9223372036854775807l);
```

返回：9,223,372,036,854,775,807

注：

LONG 数据类型的最大值是263-1 =
9,223,372,036,854,775,807。

```dolphindb
long(9223372036854775808l);
```

返回：9,223,372,036,854,775,807
