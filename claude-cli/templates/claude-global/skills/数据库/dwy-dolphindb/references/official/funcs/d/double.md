---
source_url: https://docs.dolphindb.cn/zh/funcs/d/double.html
fetched_at: 2026-05-19T09:19:13Z
category: funcs
title: double
sha1: d9a25fe5772fd5a812ae7e4e27e4e1081771881d
---

# double

## 语法

`double(X)`

## 详情

将输入的数据类型转换为 DOUBLE。

## 参数

**X** 可以是任意数据类型。

## 返回值

DOUBLE 类型，数据形式同 *X*。

## 例子

```dolphindb
x=double();  // 创建一个 DOUBLE 类型的变量，默认值为0。
x;
```

返回：null

```dolphindb
typestr x;
```

返回：DOUBLE

```dolphindb
typestr double(`10);
```

返回：DOUBLE

```dolphindb
double(`10.9);
```

返回：10.9

```dolphindb
double(now());
```

返回：1,708,616,927,949

注：

该例子首先使用 `now` 函数获得当前系统时间 2024.02.22
15:50:15.528，`double` 函数将该时间转换为 1,708,616,927,949。
