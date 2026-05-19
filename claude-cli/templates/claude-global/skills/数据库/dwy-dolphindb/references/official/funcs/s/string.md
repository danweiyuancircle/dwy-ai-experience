---
source_url: https://docs.dolphindb.cn/zh/funcs/s/string.html
fetched_at: 2026-05-19T09:40:41Z
category: funcs
title: string
sha1: 475191ffb5b7edcc4a2ad2850ec50f24a14ec0a4
---

# string

## 语法

`string(X)`

## 详情

将输入转化为一个字符串。

## 参数

**X** 可以是任何数据类型。

## 返回值

返回值的数据形式与 *X* 一致。

## 例子

```dolphindb
string()=="";  // 创建一个新的字符串，默认值为""。
```

返回：true

```dolphindb
string(10);
```

返回：10

```dolphindb
typestr string(108.5);
```

返回：STRING

```dolphindb
string(now());
```

返回：2024.02.22T15:09:40.931

注：

以 字符串形式返回当前系统时间。
