---
source_url: https://docs.dolphindb.cn/zh/funcs/b/bool.html
fetched_at: 2026-05-19T09:14:06Z
category: funcs
title: bool
sha1: 4b387b077d4ae18f52ddf4d1d02429598032abdb
---

# bool

## 语法

`bool(X)`

## 详情

把输入转换为布尔值。

## 参数

**X** 可以是任意的数据类型。

## 返回值

布尔类型，其数据形式同 *X*。

## 例子

```dolphindb
x=bool();
x;
```

返回：null

```dolphindb
typestr x;
```

返回：BOOL

```dolphindb
bool(`true);
```

返回：true

```dolphindb
bool(`false);
```

返回：false

```dolphindb
bool(`true`false)
```

返回：[true, false]

```dolphindb
bool(100.2);
```

返回：true

```dolphindb
bool(0);
```

返回：false
